#!/usr/bin/env python3
"""
Test script for Google Text-to-Speech functionality.

This script tests the TTS service independently to verify:
1. Google Cloud credentials are configured
2. Text-to-speech synthesis works
3. Audio output can be generated and saved
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

    if settings.google_tts_voice:
        print(f"✅ TTS Voice: {settings.google_tts_voice}")
    else:
        issues.append("❌ GOOGLE_TTS_VOICE not set")

    if not has_auth:
        issues.append("❌ Missing authentication (need API key or credentials file)")

    if issues:
        print("\n" + "="*70)
        print("⚠️  CONFIGURATION ISSUES FOUND:")
        print("="*70)
        for issue in issues:
            print(f"  {issue}")

        print("\n📝 TO FIX - Option 1 (API Key - Easiest):")
        print("="*70)
        print("1. Go to: https://console.cloud.google.com/apis/credentials")
        print("2. Create or select a project")
        print("3. Click 'Create Credentials' → 'API Key'")
        print("4. Add to .env file:")
        print("   GOOGLE_CLOUD_API_KEY=your-api-key-here")
        print("   GOOGLE_CLOUD_PROJECT_ID=your-project-id")
        print("   GOOGLE_TTS_VOICE=en-US-Neural2-D")

        print("\n📝 TO FIX - Option 2 (Service Account):")
        print("="*70)
        print("1. Create service account and download JSON key")
        print("2. Add to .env file:")
        print("   GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json")
        print("="*70)
        return False

    print("\n✅ All configuration looks good!")
    return True


async def test_tts_basic():
    """Test basic TTS functionality."""
    from src.services import GoogleTTSService

    print("\n" + "="*70)
    print("🎙️  TESTING BASIC TEXT-TO-SPEECH")
    print("="*70)

    try:
        # Initialize TTS service
        tts = GoogleTTSService()
        print("✅ GoogleTTSService initialized")

        # Test text
        test_text = "Hello! This is a test of the CoffeeBeans voice agent text to speech system."
        print(f"\n📝 Input text: '{test_text}'")

        # Generate speech
        print("🔄 Generating speech...")
        audio_data = await tts.synthesize_speech(test_text)

        if not audio_data:
            print("❌ No audio data generated")
            return False

        print(f"✅ Generated {len(audio_data)} bytes of audio (μ-law, 8kHz)")

        # Save to file
        output_file = Path("test_tts_output.mulaw")
        output_file.write_bytes(audio_data)
        print(f"💾 Saved to: {output_file.absolute()}")

        print("\n" + "="*70)
        print("✅ BASIC TTS TEST PASSED")
        print("="*70)
        print("\n📝 NOTE: The output is in μ-law format (8kHz, mono)")
        print("To play it, you can convert with ffmpeg:")
        print(f"  ffmpeg -f mulaw -ar 8000 -ac 1 -i {output_file} output.wav")

        return True

    except Exception as e:
        print(f"\n❌ TTS TEST FAILED: {e}")
        logger.exception("TTS test error")
        return False


async def test_tts_with_conversion():
    """Test TTS and convert output to WAV for easy playback."""
    from src.services import GoogleTTSService
    import subprocess

    print("\n" + "="*70)
    print("🎵 TESTING TTS WITH WAV CONVERSION")
    print("="*70)

    try:
        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            has_ffmpeg = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_ffmpeg = False
            print("⚠️  ffmpeg not found - will skip WAV conversion")
            print("\n📦 To install ffmpeg on Mac:")
            print("   brew install ffmpeg")
            print("\nContinuing with .mulaw generation only...\n")

        # Initialize TTS
        tts = GoogleTTSService()

        # Test with different text
        test_texts = [
            "Hi, this is Alex from CoffeeBeans Consulting. Do you have a few minutes?",
            "We specialize in AI, blockchain, and big data analytics.",
            "I understand your concern about cost. Let me explain our flexible pricing."
        ]

        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 Test {i}: '{text[:50]}...'")

            # Generate audio
            audio_data = await tts.synthesize_speech(text)

            if not audio_data:
                print(f"❌ Failed to generate audio for test {i}")
                continue

            # Save μ-law file
            mulaw_file = Path(f"test_tts_{i}.mulaw")
            mulaw_file.write_bytes(audio_data)
            print(f"   💾 μ-law: {mulaw_file}")

            # Convert to WAV if ffmpeg available
            if has_ffmpeg:
                wav_file = Path(f"test_tts_{i}.wav")
                result = subprocess.run([
                    "ffmpeg", "-y",
                    "-f", "mulaw",
                    "-ar", "8000",
                    "-ac", "1",
                    "-i", str(mulaw_file),
                    str(wav_file)
                ], capture_output=True)

                if result.returncode == 0:
                    print(f"   🎵 WAV: {wav_file}")
                    print(f"   ▶️  Play: open {wav_file}")
                else:
                    print(f"   ⚠️  WAV conversion failed")

        print("\n" + "="*70)
        print("✅ TTS CONVERSION TEST COMPLETE")
        print("="*70)

        if has_ffmpeg:
            print("\n🎧 To listen to the generated audio:")
            print("   macOS: open test_tts_1.wav")
            print("   Linux: aplay test_tts_1.wav")
            print("   Windows: start test_tts_1.wav")

        return True

    except Exception as e:
        print(f"\n❌ TTS CONVERSION TEST FAILED: {e}")
        logger.exception("TTS conversion error")
        return False


async def test_voice_pipeline():
    """Test the full voice AI pipeline (STT → LLM → TTS)."""
    print("\n" + "="*70)
    print("🔄 TESTING FULL VOICE PIPELINE")
    print("="*70)
    print("\n⚠️  This test requires:")
    print("   - Google Cloud credentials (for STT/TTS)")
    print("   - Groq API key (for LLM)")
    print("   - Audio input file or microphone")
    print("\nSkipping full pipeline test (use real phone call for end-to-end)")
    print("="*70)


async def main():
    """Main test function."""
    print("\n" + "🎙️ "*20)
    print("\n   COFFEEBEANS VOICE AGENT - TTS TESTING")
    print("\n" + "🎙️ "*20 + "\n")

    # Check credentials first
    if not check_credentials():
        print("\n⚠️  Please configure Google Cloud credentials before testing TTS")
        return

    print("\n📋 Available Tests:")
    print("="*70)
    print("1. Basic TTS Test (generate audio)")
    print("2. TTS with WAV conversion (requires ffmpeg)")
    print("3. Exit")
    print("="*70)

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == "1":
        success = await test_tts_basic()
        sys.exit(0 if success else 1)

    elif choice == "2":
        success = await test_tts_with_conversion()
        sys.exit(0 if success else 1)

    elif choice == "3":
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
