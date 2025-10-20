"""WebSocket handlers for managing call connections with Groq + Google."""

import asyncio
import json
import base64
import logging
from typing import Dict, Any
from fastapi import WebSocket
from .services import VoiceAIService, TwilioService
from .state import create_initial_state, ConversationState
from .graph import supervisor_agent, update_state_from_transcript

logger = logging.getLogger(__name__)


class CallHandler:
    """Manages the bridge between Twilio and Voice AI (STT → LLM → TTS)."""
    
    def __init__(self):
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        logger.info("CallHandler initialized with Groq + Google")
        
    async def handle_call(self, websocket: WebSocket, call_sid: str) -> None:
        """Handle an incoming call connection from Twilio."""
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for call {call_sid}")
        
        # Initialize Voice AI service
        voice_ai = VoiceAIService()
        
        # Create initial state
        state = create_initial_state(call_sid, f"SESSION-{call_sid}")
        
        # Execute first graph step (greeting) and get initial prompt
        state = await self._execute_graph_step(state, voice_ai)
        
        # Store active call
        self.active_calls[call_sid] = {
            "websocket": websocket,
            "voice_ai": voice_ai,
            "state": state,
            "audio_buffer": bytearray(),
            "stream_sid": None
        }
        
        try:
            # Handle bidirectional streaming
            await self._handle_streaming(websocket, voice_ai, call_sid)
            
        except Exception as e:
            logger.error(f"Error handling call {call_sid}: {e}")
        finally:
            # Cleanup
            await self._cleanup_call(call_sid)
    
    async def _handle_streaming(
        self,
        websocket: WebSocket,
        voice_ai: VoiceAIService,
        call_sid: str
    ) -> None:
        """Handle bidirectional streaming between Twilio and Voice AI."""

        greeting_sent = False

        try:
            while True:
                # Receive message from Twilio
                message = await websocket.receive_text()
                data = json.loads(message)

                event_type = data.get("event")

                if event_type == "start":
                    logger.info(f"Call {call_sid} started")
                    stream_sid = data.get("start", {}).get("streamSid")
                    self.active_calls[call_sid]["stream_sid"] = stream_sid
                    logger.info(f"Stream SID: {stream_sid}")

                    # Send initial greeting AFTER stream starts
                    if not greeting_sent:
                        await self._send_initial_greeting(websocket, voice_ai, call_sid)
                        greeting_sent = True
                    
                elif event_type == "media":
                    # Accumulate audio in buffer
                    media = data.get("media", {})
                    payload = media.get("payload")
                    
                    if payload and call_sid in self.active_calls:
                        # Decode and add to buffer
                        audio_chunk = base64.b64decode(payload)
                        self.active_calls[call_sid]["audio_buffer"].extend(audio_chunk)
                        
                        # Process when we have enough audio (125ms worth ~= 1000 bytes for μ-law 8kHz)
                        if len(self.active_calls[call_sid]["audio_buffer"]) >= 1000:
                            await self._process_audio_buffer(websocket, voice_ai, call_sid)
                    
                elif event_type == "stop":
                    logger.info(f"Call {call_sid} stopped")
                    # Process any remaining audio
                    if call_sid in self.active_calls and len(self.active_calls[call_sid]["audio_buffer"]) > 0:
                        await self._process_audio_buffer(websocket, voice_ai, call_sid)
                    break
                    
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
    
    async def _send_initial_greeting(
        self,
        websocket: WebSocket,
        voice_ai: VoiceAIService,
        call_sid: str
    ) -> None:
        """Send initial greeting to caller."""
        try:
            # Get greeting text from prompts
            from .prompts import prompt_manager
            
            greeting_text = (
                "Hi! This is an AI assistant calling from CoffeeBeans Consulting. "
                "We specialize in helping companies with AI, data engineering, and "
                "digital transformation. Do you have a couple of minutes to chat "
                "about your technology initiatives?"
            )
            
            # Generate greeting audio
            greeting_audio = await voice_ai.tts.synthesize_speech(greeting_text)
            
            if greeting_audio:
                # Send to Twilio
                await self._send_audio_to_twilio(websocket, greeting_audio, call_sid)
                logger.info("Initial greeting sent")
            
        except Exception as e:
            logger.error(f"Error sending initial greeting: {e}")
    
    async def _process_audio_buffer(
        self,
        websocket: WebSocket,
        voice_ai: VoiceAIService,
        call_sid: str
    ) -> None:
        """Process accumulated audio buffer."""
        if call_sid not in self.active_calls:
            return
        
        try:
            # Get audio buffer
            audio_buffer = bytes(self.active_calls[call_sid]["audio_buffer"])
            self.active_calls[call_sid]["audio_buffer"].clear()
            
            if len(audio_buffer) < 1000:  # Too short, probably noise
                return
            
            logger.info(f"Processing {len(audio_buffer)} bytes of audio")
            
            # Get current state and system instruction
            state = self.active_calls[call_sid]["state"]
            
            # Process through Voice AI pipeline
            response_audio = await voice_ai.process_voice(audio_content=audio_buffer)
            
            if response_audio:
                # Send response back to Twilio
                await self._send_audio_to_twilio(websocket, response_audio, call_sid)
                
                # Update state based on the conversation
                # Note: The transcription happens inside voice_ai.process_voice
                # We need to get the transcript for state update
                transcript = await voice_ai.stt.transcribe_audio(audio_buffer)
                
                if transcript:
                    # Update state and potentially transition phases
                    state = await self._execute_graph_step(
                        state,
                        voice_ai,
                        user_transcript=transcript
                    )
                    self.active_calls[call_sid]["state"] = state
            
        except Exception as e:
            logger.error(f"Error processing audio buffer: {e}")
    
    async def _send_audio_to_twilio(
        self,
        websocket: WebSocket,
        audio_content: bytes,
        call_sid: str
    ) -> None:
        """Send audio back to Twilio."""
        try:
            if call_sid not in self.active_calls:
                return
            
            stream_sid = self.active_calls[call_sid].get("stream_sid")
            if not stream_sid:
                logger.warning("No stream SID available")
                return
            
            # Encode audio to base64
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            # Send as media message to Twilio
            media_message = {
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": audio_base64
                }
            }
            
            await websocket.send_text(json.dumps(media_message))
            logger.info(f"Sent {len(audio_content)} bytes to Twilio")
            
        except Exception as e:
            logger.error(f"Error sending audio to Twilio: {e}")
    
    async def _execute_graph_step(
        self,
        state: ConversationState,
        voice_ai: VoiceAIService,
        user_transcript: str = None
    ) -> ConversationState:
        """Execute one step of the conversation graph and update Voice AI context."""
        try:
            # Update state based on user transcript if provided
            if user_transcript:
                state = update_state_from_transcript(state, user_transcript, "user")

            # Get current phase
            current_phase = state.get("phase")
            logger.info(f"Executing graph step for phase: {current_phase}")

            # Execute supervisor agent to get system instruction
            # Supervisor handles all phases dynamically
            state = supervisor_agent(state)

            # Update Voice AI with new system instructions
            messages = state.get("messages", [])
            if messages and messages[-1]["role"] == "system":
                voice_ai.update_system_instruction(messages[-1]["content"])

            return state

        except Exception as e:
            logger.error(f"Error executing graph step: {e}")
            return state
    
    async def _cleanup_call(self, call_sid: str) -> None:
        """Clean up resources for a completed call."""
        if call_sid in self.active_calls:
            call_info = self.active_calls[call_sid]
            
            # Reset Voice AI service
            voice_ai = call_info.get("voice_ai")
            if voice_ai:
                voice_ai.reset()
            
            # Remove from active calls
            del self.active_calls[call_sid]
            logger.info(f"Cleaned up call {call_sid}")


# Global handler instance
call_handler = CallHandler()