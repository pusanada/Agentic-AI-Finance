import sys
from pathlib import Path

# Add backend to path for testing
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.audio_service import AudioService

def test_analyze_audio_fallback():
    # Test fallback analysis for PTT
    ptt_audio = AudioService.analyze_audio("PTT")
    assert ptt_audio["ticker"] == "PTT"
    assert " JUMP+ " in ptt_audio["transcription"]
    assert ptt_audio["analysis"]["confidence_score"] > 80
    assert ptt_audio["analysis"]["sincerity_score"] > 80
    
    # Test fallback for a non-existent ticker
    unknown_audio = AudioService.analyze_audio("UNKNOWN")
    assert unknown_audio["ticker"] == "UNKNOWN"
    assert "confidence_score" in unknown_audio["analysis"]
