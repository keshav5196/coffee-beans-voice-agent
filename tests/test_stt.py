#!/usr/bin/env python3
"""
Test script for Google Speech-to-Text functionality.

This script tests the STT service independently to verify:
1. Google Cloud credentials are configured
2. Speech-to-text transcription works
3. Audio input can be processed
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path so we can import src module
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_credentials():
    """Check if Google Cloud credentials are configured."""
    from src.config import settings

    print("\n" + "="*70)
    print("🔍 CHECKING GOOGLE CLOUD CONFIGURATION")
    print("="*70)

    issues = []
    has_auth = False

    # Check for API key (preferred method)
    if settings.google_api_key:
        print(f"✅ API Key: {settings.google_api_key[:10]}...{settings.google_api_key[-4:]}")
        has_auth = True
    # Check for credentials file (alternative)
    elif settings.google_credentials_path:
        if Path(settings.google_credentials_path).exists():
            print(f"✅ Credentials file: {settings.google_credentials_path}")
            has_auth = True
        else:
            issues.append(f"❌ Credentials file not found: {settings.google_credentials_path}")
    else:
        issues.append("❌ No Google Cloud authentication configured")

    # Check other settings
    if settings.google_project_id:
        print(f"✅ Project ID: {settings.google_project_id}")
    else:
        print("⚠️  GOOGLE_CLOUD_PROJECT_ID not set (optional)")

    if settings.google_stt_language:
        print(f"✅ STT Language: {settings.google_stt_language}")
    else:
        issues.append("❌ GOOGLE_STT_LANGUAGE not set")

    if not has_auth:
        issues.append("❌ Missing authentication (need API key or credentials file)")

    if issues:
        print("\n" + "="*70)
        print("⚠️  CONFIGURATION ISSUES FOUND:")
        print("="*70)
        for issue in issues:
            print(f"  {issue}")

        print("\n📝 TO FIX:")
        print("="*70)
        print("Your Google Cloud API key should work for both STT and TTS.")
        print("Make sure these are in your .env file:")
        print("   GOOGLE_CLOUD_API_KEY=your-api-key")
        print("   GOOGLE_CLOUD_PROJECT_ID=your-project-id")
        print("   GOOGLE_STT_LANGUAGE=en-US")
        print("="*70)
        return False

    print("\n✅ All configuration looks good!")
    return True


async def test_stt_with_sample_audio():
    """Test STT with generated sample audio."""
    from src.services import GoogleSTTService, GoogleTTSService

    print("\n" + "="*70)
    print("🎤 TESTING SPEECH-TO-TEXT")
    print("="*70)

    try:
        # First, generate sample audio using TTS
        print("\n📝 Step 1: Generating sample audio with TTS...")
        tts = GoogleTTSService()
        sample_text = "Hello, this is a test of the speech to text system."
        print(f"   Text: '{sample_text}'")

        audio_data = await tts.synthesize_speech(sample_text)

        if not audio_data:
            print("❌ Failed to generate sample audio")
            return False

        print(f"   ✅ Generated {len(audio_data)} bytes of audio")

        # Save the audio for reference
        sample_file = Path("test_stt_sample.mulaw")
        sample_file.write_bytes(audio_data)
        print(f"   💾 Saved to: {sample_file}")

        # Now test STT
        print("\n🔄 Step 2: Transcribing audio with STT...")
        stt = GoogleSTTService()
        print("   ✅ GoogleSTTService initialized")

        transcript = await stt.transcribe_audio(audio_data)

        if not transcript:
            print("❌ No transcript generated")
            return False

        print(f"\n📝 Transcription Result:")
        print("="*70)
        print(f"Original text: {sample_text}")
        print(f"Transcribed:   {transcript}")
        print("="*70)

        # Check accuracy
        if sample_text.lower() in transcript.lower() or transcript.lower() in sample_text.lower():
            print("\n✅ STT TEST PASSED - Transcription matches!")
        else:
            print("\n⚠️  Transcription differs from original (this is normal for TTS→STT)")

        return True

    except Exception as e:
        print(f"\n❌ STT TEST FAILED: {e}")
        logger.exception("STT test error")
        return False


async def test_stt_with_test_phrases():
    """Test STT with multiple test phrases."""
    from src.services import GoogleSTTService, GoogleTTSService

    print("\n" + "="*70)
    print("🎙️  TESTING MULTIPLE PHRASES")
    print("="*70)

    test_phrases = [
        "Hello, how are you today?",
        "We are struggling with AI deployment issues.",
        "I'm interested in your big data analytics services.",
        "What is the cost of your blockchain solutions?",
        "Can you schedule a discovery call for next week?"
    ]

    try:
        tts = GoogleTTSService()
        stt = GoogleSTTService()

        results = []

        for i, phrase in enumerate(test_phrases, 1):
            print(f"\n📝 Test {i}/{len(test_phrases)}: '{phrase}'")

            # Generate audio
            audio = await tts.synthesize_speech(phrase)
            if not audio:
                print(f"   ❌ TTS failed")
                continue

            # Transcribe
            transcript = await stt.transcribe_audio(audio)
            if not transcript:
                print(f"   ❌ STT failed")
                continue

            print(f"   → Transcribed: '{transcript}'")

            # Calculate simple accuracy
            original_words = set(phrase.lower().replace('?', '').replace('.', '').split())
            transcribed_words = set(transcript.lower().replace('?', '').replace('.', '').split())

            if original_words and transcribed_words:
                common_words = original_words & transcribed_words
                accuracy = len(common_words) / len(original_words) * 100
                print(f"   ✓ Word accuracy: {accuracy:.0f}%")
                results.append(accuracy)
            else:
                results.append(0)

        if results:
            avg_accuracy = sum(results) / len(results)
            print("\n" + "="*70)
            print(f"📊 AVERAGE ACCURACY: {avg_accuracy:.1f}%")
            print("="*70)

            if avg_accuracy >= 70:
                print("✅ STT is working well!")
            elif avg_accuracy >= 50:
                print("⚠️  STT is working but with some errors")
            else:
                print("⚠️  STT accuracy is low - check audio quality/settings")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        logger.exception("Multi-phrase test error")
        return False


async def test_stt_with_user_audio():
    """Test STT with user-provided audio file."""
    print("\n" + "="*70)
    print("📁 TESTING WITH CUSTOM AUDIO FILE")
    print("="*70)

    print("\n⚠️  To test with your own audio:")
    print("   1. Provide a .mulaw file (8kHz, mono, μ-law encoding)")
    print("   2. Or use one of the generated test files from TTS testing")

    audio_file = input("\n📂 Enter path to .mulaw file (or press Enter to skip): ").strip()

    if not audio_file:
        print("⏭️  Skipping custom audio test")
        return True

    audio_path = Path(audio_file)

    if not audio_path.exists():
        print(f"❌ File not found: {audio_path}")
        return False

    try:
        from src.services import GoogleSTTService

        # Read audio file
        audio_data = audio_path.read_bytes()
        print(f"✅ Loaded {len(audio_data)} bytes from {audio_path.name}")

        # Transcribe
        print("🔄 Transcribing...")
        stt = GoogleSTTService()
        transcript = await stt.transcribe_audio(audio_data)

        if transcript:
            print("\n📝 Transcription:")
            print("="*70)
            print(transcript)
            print("="*70)
            print("\n✅ Transcription successful!")
        else:
            print("❌ No transcription generated")
            return False

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        logger.exception("Custom audio test error")
        return False


async def main():
    """Main test function."""
    print("\n" + "🎤 "*20)
    print("\n   COFFEEBEANS VOICE AGENT - STT TESTING")
    print("\n" + "🎤 "*20 + "\n")

    # Check credentials first
    if not check_credentials():
        print("\n⚠️  Please configure Google Cloud credentials before testing STT")
        return

    print("\n📋 Available Tests:")
    print("="*70)
    print("1. Basic STT Test (TTS → STT round-trip)")
    print("2. Multiple Phrases Test (accuracy check)")
    print("3. Custom Audio File Test")
    print("4. Exit")
    print("="*70)

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == "1":
        success = await test_stt_with_sample_audio()
        sys.exit(0 if success else 1)

    elif choice == "2":
        success = await test_stt_with_test_phrases()
        sys.exit(0 if success else 1)

    elif choice == "3":
        success = await test_stt_with_user_audio()
        sys.exit(0 if success else 1)

    elif choice == "4":
        print("\n👋 Goodbye!")

    else:
        print("\n❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        logger.exception("Test failed")
        sys.exit(1)
