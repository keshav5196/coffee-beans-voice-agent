"""Interactive test script for Phase 2 - Real LLM conversation testing.

This script allows testing the conversation flow with actual Groq responses.
You can interact with the agent in real-time via terminal.
"""

import asyncio
import logging
import sys
from typing import Optional
from groq import AsyncGroq
from src.state import create_initial_state, ConversationState
from src.graph import (
    supervisor_agent,
    update_state_from_transcript,
    analyze_sentiment,
    extract_interests,
    detect_objections,
    TOOL_SCHEMAS,
    execute_tool_call
)
from src.config import settings
from src.knowledge import knowledge_base

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class InteractiveLLMAgent:
    """Interactive agent with real LLM responses."""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.state: Optional[ConversationState] = None
        # self.conversation_history = [].client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.state: Optional[ConversationState] = None
        self.conversation_history = []
        
    async def start_conversation(self):
        """Start a new conversation with the agent."""
        print("\n" + "="*70)
        print("🎙️  COFFEEBEANS VOICE AGENT - INTERACTIVE TEST")
        print("="*70)
        print("\n💡 You can now have a real conversation with the AI agent!")
        print("   The agent will use actual OpenAI responses.\n")
        print("   Type 'quit' to end the conversation")
        print("   Type 'status' to see current conversation state")
        print("="*70 + "\n")
        
        # Create initial state
        self.state = create_initial_state("INTERACTIVE-TEST", "INT-SESSION-001")
        
        # Start with greeting phase
        await self._execute_phase_transition("greeting")
        
        # Get initial greeting from agent
        await self._get_agent_response()
        
    async def _execute_phase_transition(self, new_phase: str = "supervisor"):
        """Execute transition - now just calls supervisor."""
        # With supervisor pattern, we don't have explicit phases
        # Supervisor handles everything dynamically
        self.state["phase"] = "supervisor"

        # Import here to avoid circular dependency
        from src.graph import supervisor_agent

        # Execute supervisor to get system prompt (not async)
        self.state = supervisor_agent(self.state)
    
    async def _get_agent_response(self, user_input: Optional[str] = None) -> str:
        """Get response from Groq with function calling support."""
        try:
            import json

            # Build messages
            messages = []

            # Add system instruction from current phase
            phase_messages = self.state.get("messages", [])
            if phase_messages and phase_messages[-1]["role"] == "system":
                messages.append({
                    "role": "system",
                    "content": phase_messages[-1]["content"]
                })

            # Add conversation history
            messages.extend(self.conversation_history)

            # Add user input if provided
            if user_input:
                messages.append({
                    "role": "user",
                    "content": user_input
                })

            # Get response from Groq with tools
            response = await self.client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=settings.max_response_tokens,
                tools=TOOL_SCHEMAS,
                tool_choice="auto"
            )

            message = response.choices[0].message
            agent_message = message.content or ""
            tool_calls = message.tool_calls or []

            # Update conversation history with user message
            if user_input:
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input
                })

            # Add assistant message to history
            assistant_msg = {"role": "assistant"}
            if agent_message:
                assistant_msg["content"] = agent_message
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

            # Execute any tool calls
            if tool_calls:
                print(f"🔧 Tool calls: {len(tool_calls)}")
                for tool_call in tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    print(f"   → Calling {func_name}({func_args})")

                    # Execute the tool
                    result = execute_tool_call(func_name, func_args)

                    # Add tool result to conversation history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": result
                    })

                    print(f"   ✓ Result: {result[:100]}...")

                # Get final response after tool execution
                final_response = await self.client.chat.completions.create(
                    model=settings.groq_model,
                    messages=messages + self.conversation_history[len(messages):],
                    temperature=settings.temperature,
                    max_tokens=settings.max_response_tokens
                )

                agent_message = final_response.choices[0].message.content
                self.conversation_history.append({
                    "role": "assistant",
                    "content": agent_message
                })

            # Display agent response
            print(f"🤖 AGENT: {agent_message}\n")

            return agent_message

        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            print(f"❌ Error: {e}\n")
            return "I apologize, I'm having technical difficulties. Could you repeat that?"
    
    async def process_user_input(self, user_input: str):
        """Process user input and manage conversation flow."""
        # Analyze user input and update state (not async)
        self.state = update_state_from_transcript(
            self.state,
            user_input,
            "user"
        )
        
        # Show analysis (optional debug info)
        if user_input.lower() == "status":
            self._show_status()
            return
        
        # Get agent response (supervisor handles everything)
        await self._get_agent_response(user_input)
        
        # No explicit phase transitions - supervisor decides dynamically
    
    def _show_status(self):
        """Display current conversation state."""
        print("\n" + "="*70)
        print("📊 CONVERSATION STATUS")
        print("="*70)
        print(f"Phase: {self.state.get('phase', 'unknown').upper()}")
        print(f"Sentiment: {self.state.get('sentiment', 'neutral')}")
        print(f"Engagement Level: {self.state.get('engagement_level', 'medium')}")
        print(f"Interests: {', '.join(self.state.get('interests', [])) or 'None detected'}")
        print(f"Services Discussed: {', '.join(self.state.get('services_discussed', [])) or 'None'}")
        print(f"Objections: {', '.join(self.state.get('objections_raised', [])) or 'None'}")
        print(f"Messages Exchanged: {len(self.conversation_history)}")
        print("="*70 + "\n")
    
    async def run_interactive_loop(self):
        """Run the interactive conversation loop."""
        while True:
            try:
                # Get user input
                user_input = input("👤 YOU: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit command
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Ending conversation. Goodbye!\n")
                    self._show_status()
                    break
                
                # Check for status command
                if user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                # Process the input
                print()  # Add spacing
                await self.process_user_input(user_input)
                
                # Check if conversation ended
                if self.state.get("phase") == "close":
                    print("\n✅ Conversation completed!")
                    
                    # Ask if user wants to continue or end
                    continue_choice = input("\nContinue chatting? (y/n): ").strip().lower()
                    if continue_choice != 'y':
                        print("\n👋 Thank you for testing the CoffeeBeans Voice Agent!\n")
                        self._show_status()
                        break
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Conversation interrupted by user")
                self._show_status()
                break
            except Exception as e:
                logger.error(f"Error in conversation loop: {e}")
                print(f"\n❌ Error: {e}\n")


async def quick_test_scenarios():
    """Run quick automated test scenarios (non-interactive)."""
    print("\n" + "="*70)
    print("🧪 QUICK TEST SCENARIOS")
    print("="*70)
    
    from src.graph import analyze_sentiment, extract_interests, detect_objections
    
    test_inputs = [
        "Yes, I'm interested in learning more about your AI solutions.",
        "We're struggling with getting our ML models into production.",
        "This sounds expensive. What's the cost?",
        "I'm too busy right now. Can you call back later?",
        "We already have an internal team handling this.",
    ]
    
    print("\n📊 Testing Sentiment Analysis & Interest Detection:\n")
    
    for i, text in enumerate(test_inputs, 1):
        sentiment = analyze_sentiment(text)
        interests = extract_interests(text)
        objections = detect_objections(text)
        
        print(f"{i}. Input: '{text}'")
        print(f"   → Sentiment: {sentiment}")
        print(f"   → Interests: {interests if interests else 'None'}")
        print(f"   → Objections: {objections if objections else 'None'}")
        print()


async def test_knowledge_base():
    """Test knowledge base functionality."""
    print("\n" + "="*70)
    print("📚 KNOWLEDGE BASE TEST")
    print("="*70)
    
    print("\n🏢 Company Information:")
    print(f"   Name: {knowledge_base.company_info['name']}")
    print(f"   Founded: {knowledge_base.company_info['founded']}")
    print(f"   Team Size: {knowledge_base.company_info['team_size']}")
    print(f"   Philosophy: {knowledge_base.company_info['core_philosophy']}")
    
    print("\n🔧 Available Services:")
    for key, service in knowledge_base.services.items():
        print(f"   • {service['name']}")
        print(f"     {service['description'][:80]}...")
    
    print("\n💼 Case Studies:")
    for case in knowledge_base.case_studies[:3]:
        print(f"   • {case['client']} ({case['industry']})")
        print(f"     Challenge: {case['challenge'][:60]}...")
    
    print("\n🎯 Pain Point Matching Test:")
    test_points = [
        "Our AI models won't scale to production",
        "We have serious data quality issues",
        "Need better security in our supply chain",
        "Legacy systems holding us back"
    ]
    
    for pain_point in test_points:
        matched = knowledge_base.match_service_to_pain_point(pain_point)
        service_name = knowledge_base.services[matched]['name']
        print(f"   '{pain_point}'")
        print(f"   → {service_name}")


async def main():
    """Main interactive test menu."""
    print("\n" + "="*70)
    print("🎙️  COFFEEBEANS VOICE AGENT - PHASE 2 INTERACTIVE TESTING")
    print("="*70)
    
    print("\n📋 Available Options:")
    print("1. 🗣️  Interactive Conversation (Talk with real LLM)")
    print("2. 🧪 Quick Test Scenarios (Automated)")
    print("3. 📚 Test Knowledge Base")
    print("4. 🚀 Run All Tests")
    print("5. ❌ Exit")
    
    choice = input("\n➡️  Enter your choice (1-5): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting interactive conversation with LLM agent...")
        print("   This will use real OpenAI API calls.\n")
        
        agent = InteractiveLLMAgent()
        await agent.start_conversation()
        await agent.run_interactive_loop()
        
    elif choice == "2":
        await quick_test_scenarios()
        
    elif choice == "3":
        await test_knowledge_base()
        
    elif choice == "4":
        print("\n🚀 Running all tests...\n")
        await test_knowledge_base()
        await quick_test_scenarios()
        print("\n" + "="*70)
        print("✅ Non-interactive tests complete!")
        print("="*70)
        
        run_interactive = input("\nRun interactive conversation test? (y/n): ").strip().lower()
        if run_interactive == 'y':
            agent = InteractiveLLMAgent()
            await agent.start_conversation()
            await agent.run_interactive_loop()
        
    elif choice == "5":
        print("\n👋 Goodbye!\n")
        
    else:
        print("\n❌ Invalid choice\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!\n")