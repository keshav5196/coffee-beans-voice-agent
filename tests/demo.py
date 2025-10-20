"""Demo script to test the voice agent with a simple call."""

import asyncio
import logging
from src.services import TwilioService
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_call(phone_number: str, ngrok_url: str):
    """
    Initiate a demo call to test the voice agent.
    
    Args:
        phone_number: Phone number to call (E.164 format, e.g., +1234567890)
        ngrok_url: Your ngrok HTTPS URL (e.g., https://abc123.ngrok.io)
    """
    logger.info("=== CoffeeBeans Voice Agent Demo ===")
    logger.info(f"Initiating call to: {phone_number}")
    
    try:
        # Initialize Twilio service
        twilio_service = TwilioService()
        
        # Construct callback URL using ngrok URL
        callback_url = f"{ngrok_url}/voice"
        
        logger.info(f"Callback URL: {callback_url}")
        
        # Initiate call
        call_sid = twilio_service.initiate_call(phone_number, callback_url)
        
        logger.info(f"✅ Call initiated successfully!")
        logger.info(f"Call SID: {call_sid}")
        
        # Monitor call status
        logger.info("\nMonitoring call status...")
        for i in range(10):
            await asyncio.sleep(2)
            status = twilio_service.get_call_status(call_sid)
            logger.info(f"Call status: {status}")
            
            if status in ["completed", "busy", "failed", "no-answer"]:
                break
        
        logger.info("\n=== Demo Complete ===")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


async def test_openai_connection():
    """Test connection to OpenAI Realtime API."""
    from src.services import OpenAIRealtimeService
    
    logger.info("=== Testing OpenAI Realtime API Connection ===")
    
    try:
        service = OpenAIRealtimeService()
        await service.connect()
        logger.info("✅ Successfully connected to OpenAI Realtime API")
        await service.disconnect()
        logger.info("✅ Successfully disconnected")
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        raise


async def main():
    """Main demo function."""
    print("\n" + "="*50)
    print("CoffeeBeans Voice Agent - Phase 1 Demo")
    print("="*50 + "\n")
    
    print("⚠️  IMPORTANT: Before making a call, ensure:")
    print("   1. Your FastAPI server is running (python -m src.main)")
    print("   2. ngrok is exposing your server (ngrok http 8000)")
    print("   3. You have your ngrok HTTPS URL ready\n")
    
    print("Choose a demo option:")
    print("1. Test OpenAI Realtime API connection")
    print("2. Make a test call")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        await test_openai_connection()
    elif choice == "2":
        print("\n" + "-"*50)
        print("STEP 1: Start your server")
        print("-"*50)
        print("In another terminal, run:")
        print("  python -m src.main")
        print()
        
        print("-"*50)
        print("STEP 2: Expose with ngrok")
        print("-"*50)
        print("In another terminal, run:")
        print("  ngrok http 8000")
        print()
        print("Copy the HTTPS URL (looks like: https://abc123.ngrok.io)")
        print()
        
        ngrok_url = input("Enter your ngrok HTTPS URL: ").strip()
        
        if not ngrok_url.startswith("https://"):
            logger.error("❌ ngrok URL must start with https://")
            return
        
        # Remove trailing slash if present
        ngrok_url = ngrok_url.rstrip("/")
        
        phone_number = input("Enter phone number (E.164 format, e.g., +1234567890): ").strip()
        if not phone_number.startswith("+"):
            logger.error("❌ Phone number must be in E.164 format (starting with +)")
            return
        
        await demo_call(phone_number, ngrok_url)
    elif choice == "3":
        logger.info("Exiting...")
    else:
        logger.error("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())