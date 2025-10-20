"""Service layer for integrating with external APIs."""

import asyncio
import json
import base64
import logging
import io
from typing import Optional, AsyncGenerator
from groq import AsyncGroq
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech_v1 as texttospeech
from twilio.rest import Client
from .config import settings

logger = logging.getLogger(__name__)


class GroqService:
    """Service for managing Groq LLM API with function calling support."""

    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.conversation_history = []

    async def get_response(
        self,
        user_message: str,
        system_instruction: str = None,
        tools: list = None,
        tool_choice: str = "auto"
    ) -> tuple[str, list]:
        """
        Get LLM response from Groq with optional function calling.

        Args:
            user_message: User's text input
            system_instruction: Current phase system instruction
            tools: List of tool schemas for function calling
            tool_choice: How to use tools ("auto", "none", or specific function)

        Returns:
            Tuple of (agent_response, tool_calls)
        """
        try:
            # Build messages
            messages = []

            # Add system instruction if provided
            if system_instruction:
                messages.append({
                    "role": "system",
                    "content": system_instruction
                })

            if len(self.conversation_history) != 0:
                # Add conversation history
                messages.extend(self.conversation_history)

            if not user_message:
                return "Please enter a message before sending.", []

            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Prepare request parameters
            request_params = {
                "model": settings.groq_model,
                "messages": messages,
                "temperature": settings.temperature,
                "max_tokens": settings.max_response_tokens,
                "stream": False
            }

            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = tool_choice

            # Get response from Groq
            response = await self.client.chat.completions.create(**request_params)

            message = response.choices[0].message
            agent_response = message.content or ""
            tool_calls = message.tool_calls or []

            # Update conversation history with user message
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })

            # Add assistant message to history
            assistant_msg = {"role": "assistant"}
            if agent_response:
                assistant_msg["content"] = agent_response
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]

            self.conversation_history.append(assistant_msg)

            # Keep history manageable (last 10 messages)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            logger.info(f"Groq response: {len(agent_response)} chars, {len(tool_calls)} tool calls")
            return agent_response, tool_calls

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "I apologize, I'm having trouble processing that. Could you repeat?", []

    def add_tool_result_to_history(self, tool_call_id: str, function_name: str, result: str):
        """Add tool execution result to conversation history."""
        self.conversation_history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": function_name,
            "content": result
        })

    def reset_history(self):
        """Reset conversation history."""
        self.conversation_history = []


class GoogleSTTService:
    """Service for Google Speech-to-Text."""

    def __init__(self):
        # Use API key if available, otherwise use credentials file
        if settings.google_api_key:
            from google.cloud import speech_v1

            # Create client with API key
            client_options = {"api_key": settings.google_api_key}
            self.client = speech_v1.SpeechClient(client_options=client_options)
        else:
            self.client = speech.SpeechClient()

        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MULAW,
            sample_rate_hertz=8000,
            language_code=settings.google_stt_language,
            enable_automatic_punctuation=True,
            model="phone_call"
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=self.config,
            interim_results=False
        )
        
    async def transcribe_audio(self, audio_content: bytes) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_content: Audio data in μ-law format
            
        Returns:
            Transcribed text
        """
        try:
            audio = speech.RecognitionAudio(content=audio_content)
            
            # Perform synchronous recognition
            response = self.client.recognize(config=self.config, audio=audio)
            
            # Extract transcription
            for result in response.results:
                transcript = result.alternatives[0].transcript
                logger.info(f"STT: '{transcript}'")
                return transcript
            
            return ""
            
        except Exception as e:
            logger.error(f"Google STT error: {e}")
            return ""
    
    def create_streaming_requests(self, audio_generator):
        """
        Create streaming requests for real-time transcription.
        
        Args:
            audio_generator: Generator yielding audio chunks
            
        Yields:
            StreamingRecognizeRequest objects
        """
        yield speech.StreamingRecognizeRequest(streaming_config=self.streaming_config)
        
        for audio_chunk in audio_generator:
            yield speech.StreamingRecognizeRequest(audio_content=audio_chunk)


class GoogleTTSService:
    """Service for Google Text-to-Speech."""

    def __init__(self):
        # Use API key if available, otherwise use credentials file
        if settings.google_api_key:
            import google.auth.transport.requests
            from google.cloud import texttospeech_v1

            # Create client with API key
            client_options = {"api_key": settings.google_api_key}
            self.client = texttospeech_v1.TextToSpeechClient(client_options=client_options)
        else:
            self.client = texttospeech.TextToSpeechClient()

        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=settings.google_tts_voice
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MULAW,
            sample_rate_hertz=8000
        )
        
    async def synthesize_speech(self, text: str) -> bytes:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data in μ-law format
        """
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Perform synthesis
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )
            
            logger.info(f"TTS: Generated {len(response.audio_content)} bytes")
            return response.audio_content
            
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            return b""


class VoiceAIService:
    """
    Combined service managing the full voice AI pipeline:
    Audio → STT → LLM → TTS → Audio
    """
    
    def __init__(self):
        self.stt = GoogleSTTService()
        self.llm = GroqService()
        self.tts = GoogleTTSService()
        self.current_system_instruction = None
        
    async def process_voice(
        self,
        audio_content: bytes,
        system_instruction: str = None
    ) -> bytes:
        """
        Process voice input through full pipeline.
        
        Args:
            audio_content: Input audio (μ-law format)
            system_instruction: Current phase instructions
            
        Returns:
            Response audio (μ-law format)
        """
        try:
            # Update system instruction if provided
            if system_instruction:
                self.current_system_instruction = system_instruction
            
            # Step 1: Speech to Text
            logger.info("Step 1: Converting speech to text...")
            text = await self.stt.transcribe_audio(audio_content)
            
            if not text:
                logger.warning("No text transcribed from audio")
                return b""
            
            # Step 2: Get LLM Response
            logger.info("Step 2: Getting LLM response...")
            response_text = await self.llm.get_response(
                text,
                self.current_system_instruction
            )
            
            # Step 3: Text to Speech
            logger.info("Step 3: Converting text to speech...")
            response_audio = await self.tts.synthesize_speech(response_text)
            
            logger.info("Voice processing complete")
            return response_audio
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            return b""
    
    def update_system_instruction(self, instruction: str):
        """Update the system instruction for the LLM."""
        self.current_system_instruction = instruction
        logger.info("System instruction updated")
    
    def reset(self):
        """Reset conversation state."""
        self.llm.reset_history()
        self.current_system_instruction = None
        logger.info("Voice AI service reset")


class TwilioService:
    """Service for managing Twilio phone calls."""
    
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        
    def initiate_call(self, to_number: str, callback_url: str) -> str:
        """Initiate an outbound call via Twilio."""
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=settings.twilio_phone_number,
                url=callback_url,
                record=True
            )
            logger.info(f"Initiated call to {to_number}, SID: {call.sid}")
            return call.sid
        except Exception as e:
            logger.error(f"Failed to initiate call: {e}")
            raise
    
    def get_call_status(self, call_sid: str) -> str:
        """Get the status of a call."""
        try:
            call = self.client.calls(call_sid).fetch()
            return call.status
        except Exception as e:
            logger.error(f"Failed to get call status: {e}")
            raise