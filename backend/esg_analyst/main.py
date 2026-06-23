import os
import sys
import shutil
from pathlib import Path

# Add backend directory to sys.path programmatically
sys.path.append(str(Path(__file__).resolve().parent.parent))

from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.set_service import SETService
from app.agents.esg_agent import ESGAgent

app = FastAPI(
    title="JUMP+ & ESG Analyst Agent API",
    description="Backend service for screening Thai stocks and analyzing corporate transparency & credibility.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ESGAgent()

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "typhoon_configured": bool(settings.TYPHOON_API_KEY), "claude_configured": bool(settings.ANTHROPIC_API_KEY)}

@app.get("/api/v1/screen")
def screen_stocks():
    """
    Runs the first stage screening for all listed stocks.
    Returns the passed and failed stocks.
    """
    all_stocks = SETService.get_all_stocks()
    passed_stocks = []
    failed_stocks = []
    
    for stock in all_stocks:
        result = agent.analyze_ticker(stock["ticker"])
        if result.get("status") == "APPROVED":
            passed_stocks.append(result)
        else:
            failed_stocks.append(result)
            
    return {
        "passed_count": len(passed_stocks),
        "failed_count": len(failed_stocks),
        "passed": passed_stocks,
        "failed": failed_stocks
    }

@app.post("/api/v1/analyze/{ticker}")
async def analyze_ticker(
    ticker: str,
    cvup_file: Optional[UploadFile] = File(None),
    onereport_file: Optional[UploadFile] = File(None),
    audio_file: Optional[UploadFile] = File(None)
):
    """
    Upload files and run the full in-depth ESG and credibility analysis for a ticker.
    """
    ticker_upper = ticker.upper()
    stock_data = SETService.get_stock_by_ticker(ticker_upper)
    if not stock_data:
        raise HTTPException(status_code=404, detail=f"Ticker {ticker_upper} not found in SET database.")

    # Paths to save uploaded files locally
    cvup_path = None
    onereport_path = None
    audio_path = None

    try:
        # Save CVUP PDF
        if cvup_file:
            cvup_path = settings.PDF_DIR / f"{ticker_upper}_CVUP.pdf"
            with open(cvup_path, "wb") as buffer:
                shutil.copyfileobj(cvup_file.file, buffer)

        # Save One Report PDF
        if onereport_file:
            onereport_path = settings.PDF_DIR / f"{ticker_upper}_OneReport.pdf"
            with open(onereport_path, "wb") as buffer:
                shutil.copyfileobj(onereport_file.file, buffer)

        # Save Audio File
        if audio_file:
            # Detect extension
            ext = os.path.splitext(audio_file.filename)[1] or ".mp3"
            audio_path = settings.AUDIO_DIR / f"{ticker_upper}_OppDay{ext}"
            with open(audio_path, "wb") as buffer:
                shutil.copyfileobj(audio_file.file, buffer)

        # Run ESG Analysis
        report = agent.analyze_ticker(
            ticker=ticker_upper,
            cvup_pdf=cvup_path,
            onereport_pdf=onereport_path,
            opp_day_audio=audio_path
        )
        return report

    except Exception as e:
        # Cleanup uploaded files in case of error
        for p in [cvup_path, onereport_path, audio_path]:
            if p and p.exists():
                try:
                    os.remove(p)
                except Exception:
                    pass
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/v1/report/{ticker}")
def get_report(ticker: str):
    """
    Retrieves the report or runs analysis with whatever data is already available.
    """
    ticker_upper = ticker.upper()
    
    # Check if there are local files already uploaded
    cvup_path = settings.PDF_DIR / f"{ticker_upper}_CVUP.pdf"
    onereport_path = settings.PDF_DIR / f"{ticker_upper}_OneReport.pdf"
    audio_path = settings.AUDIO_DIR / f"{ticker_upper}_OppDay.mp3"
    if not audio_path.exists():
        audio_path = settings.AUDIO_DIR / f"{ticker_upper}_OppDay.wav"

    cvup_p = cvup_path if cvup_path.exists() else None
    onereport_p = onereport_path if onereport_path.exists() else None
    audio_p = audio_path if audio_path.exists() else None

    report = agent.analyze_ticker(
        ticker=ticker_upper,
        cvup_pdf=cvup_p,
        onereport_pdf=onereport_p,
        opp_day_audio=audio_p
    )
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
