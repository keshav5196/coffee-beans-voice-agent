#!/usr/bin/env python3
"""
Quick script to chat with the CoffeeBeans agent.

Usage:
    python chat_with_agent.py

This provides a simple, clean interface to test the agent without menus.
"""

import asyncio
import sys
from test_phase2 import InteractiveLLMAgent


async def main():
    """Run interactive conversation."""
    print("\n" + "🎙️ "*20)
    print("\n   COFFEEBEANS VOICE AGENT - INTERACTIVE TEST")
    print("   Have a natural conversation with our AI agent")
    print("\n" + "🎙️ "*20 + "\n")
    
    print("💡 Tips:")
    print("   • Chat naturally - the agent will respond conversationally")
    print("   • Type 'status' to see conversation analysis")
    print("   • Type 'quit' to end the conversation")
    print("   • Press Ctrl+C to exit anytime\n")
    print("="*60 + "\n")
    
    agent = InteractiveLLMAgent()
    
    try:
        await agent.start_conversation()
        await agent.run_interactive_loop()
    except KeyboardInterrupt:
        print("\n\n👋 Conversation ended. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())