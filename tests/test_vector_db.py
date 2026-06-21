import sys
import shutil
from pathlib import Path

# Add backend to path for testing
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.services.vector_db import SimpleVectorDB

def test_tokenization_and_search(tmp_path):
    # Initialize DB in temporary path
    db = SimpleVectorDB(tmp_path)
    
    # Manually populate document index for testing search
    db.documents["TEST_TICKER"] = [
        {
            "source": "cvup.pdf",
            "text": "Our company CPALL commits to reducing carbon emissions by 15 percent and increasing green energy products in stores.",
            "start_char": 0,
            "end_char": 100
        },
        {
            "source": "onereport.pdf",
            "text": "During this financial year, the board focused on corporate governance CGR score targets and community investments.",
            "start_char": 0,
            "end_char": 100
        }
    ]
    db.save()
    
    # Test load
    db2 = SimpleVectorDB(tmp_path)
    assert "TEST_TICKER" in db2.documents
    assert len(db2.documents["TEST_TICKER"]) == 2
    
    # Test search
    results_carbon = db2.search("TEST_TICKER", "carbon emissions")
    assert len(results_carbon) > 0
    # The first document contains "carbon emissions", so it should have a high score
    assert "carbon emissions" in results_carbon[0]["text"]
    assert results_carbon[0]["score"] > 0
    
    results_gov = db2.search("TEST_TICKER", "corporate governance")
    assert len(results_gov) > 0
    assert "corporate governance" in results_gov[0]["text"]
    assert results_gov[0]["score"] > 0
