import sys
from pathlib import Path

# Add backend to path for testing
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.sec_service import SECService

def test_get_prosecution_history():
    history = SECService.get_prosecution_history("STARK")
    assert len(history) > 0
    assert history[0]["case_type"] == "Criminal Prosecution"

def test_is_clean():
    # STARK has a prosecution in 2023, which is within 5 years of 2026
    stark_status = SECService.is_clean("STARK", years=5)
    assert stark_status["is_clean"] is False
    assert "Fails SEC check" in stark_status["message"]
    
    # PTT has no prosecutions
    ptt_status = SECService.is_clean("PTT", years=5)
    assert ptt_status["is_clean"] is True
    assert len(ptt_status["cases"]) == 0
