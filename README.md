# 🌱 JUMP+ & ESG Analyst Agent

> **Agentic AI system for screening and auditing sustainable Thai stocks on the Stock Exchange of Thailand (SET)**

An end-to-end AI-powered platform that screens Thai-listed equities against ESG (Environmental, Social, Governance) criteria and performs deep-dive transparency audits using LLM document analysis and executive voice sentiment analysis.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Screening Pipeline](#screening-pipeline)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)

---

## Overview

The JUMP+ & ESG Analyst Agent automates the **supply-side ESG auditing** process for Thai stocks. It combines structured data screening with AI-powered document cross-referencing and executive voice credibility analysis to produce a holistic transparency score for each company.

### What It Does

1. **First-Stage Screening** — Filters stocks based on three hard criteria: JUMP+ membership, CGR score ≥ 90, and no SEC prosecution history in the past 5 years.
2. **Document Alignment Audit** — Cross-references the company's Corporate Value-Up Plan (CVUP) against its Form 56-1 One Report to detect gaps, delays, or greenwashing.
3. **Voice Sentiment Analysis** — Analyzes Opportunity Day audio recordings using Typhoon2-Audio to evaluate executive confidence, sincerity, and evasion patterns.
4. **Synthesis & Scoring** — Produces a weighted overall ESG & Credibility Score with a Thai-language executive summary and investment recommendation.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                     │
│  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │  Tab 1: Screening │  │  Tab 2: Deep-Dive ESG Audit  │  │
│  │  - Stock table     │  │  - File upload (CVUP/OneRpt) │  │
│  │  - Pass/Fail list  │  │  - Plotly gauge & bar charts │  │
│  │                    │  │  - Executive summary          │  │
│  └──────────────────┘  └──────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────┘
                            │ REST API (HTTP)
┌───────────────────────────▼──────────────────────────────┐
│                     FastAPI Backend                       │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐  │
│  │  ESG Agent   │ │  SET Service  │ │  SEC Service      │  │
│  │  (Claude 3.5)│ │  (Stock data) │ │  (Prosecution DB) │  │
│  └──────┬──────┘ └──────────────┘ └───────────────────┘  │
│         │        ┌──────────────┐ ┌───────────────────┐  │
│         │        │ Audio Service │ │  SimpleVectorDB   │  │
│         │        │ (Typhoon2)    │ │  (TF-IDF search)  │  │
│         │        └──────────────┘ └───────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Key Features

| Feature | Description |
|---|---|
| 🏦 **SET Stock Screening** | Filters Thai equities by JUMP+ membership, CGR score, and SEC prosecution history |
| 📄 **CVUP vs One Report Audit** | AI-powered cross-referencing of corporate value-up plans against annual reports |
| 🎙️ **Voice Credibility Analysis** | Analyzes executive tone, confidence, sincerity, and evasion from Opportunity Day recordings |
| 📊 **Weighted ESG Scoring** | Configurable multi-factor scoring: CGR (30%), SEC (20%), Document Alignment (30%), Audio Credibility (20%) |
| 🤖 **Multi-LLM Integration** | Claude 3.5 Sonnet for document analysis + Typhoon2-Audio for Thai speech processing |
| 🇹🇭 **Thai Language Native** | Full Thai-language UI, summaries, and analysis outputs |
| 🔌 **Agent Hand-off** | Export results to a downstream Portfolio Allocator Agent |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit, Plotly, Pandas |
| **Backend API** | FastAPI, Uvicorn, Pydantic |
| **LLM (Documents)** | Anthropic Claude 3.5 Sonnet |
| **LLM (Audio)** | Typhoon2-Audio (OpenTyphoon API) |
| **Document Processing** | PyPDF for PDF parsing |
| **Search / Retrieval** | Custom TF-IDF Vector DB (supports Thai tokenization via character n-grams) |
| **Language** | Python 3.12+ |

---

## Project Structure

```
AI-fianance_ESG_analyst/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application & endpoints
│   │   ├── config.py                # Settings, paths, scoring weights
│   │   ├── agents/
│   │   │   ├── esg_agent.py         # Core ESG analysis orchestrator
│   │   │   └── prompts.py           # LLM prompt templates
│   │   └── services/
│   │       ├── set_service.py       # SET stock data service
│   │       ├── sec_service.py       # SEC prosecution history service
│   │       ├── audio_service.py     # Typhoon2-Audio integration
│   │       └── vector_db.py         # TF-IDF document search engine
│   └── requirements.txt
├── frontend/
│   └── app.py                       # Streamlit dashboard
├── data/
│   ├── pdfs/                        # Uploaded CVUP & One Report PDFs
│   ├── audio/                       # Uploaded Opp Day audio files
│   └── vector_db/                   # Indexed document store
├── tests/
│   ├── test_set_service.py
│   ├── test_sec_service.py
│   ├── test_audio_service.py
│   └── test_vector_db.py
├── .env                             # API keys (not committed)
├── .gitignore
├── requirements.txt                 # Root-level dependencies
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12 or higher
- (Optional) Anthropic API key for Claude 3.5 Sonnet
- (Optional) Typhoon API key for audio transcription

### 1. Clone the Repository

```bash
git clone https://github.com/pusanada/Agentic-AI-Finance.git
cd Agentic-AI-Finance
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TYPHOON_API_KEY=your_typhoon_api_key_here
```

> **Note:** The system works in **Mock Mode** without API keys — all services have built-in realistic fallback data for demonstration purposes.

### 4. Start the Backend Server

```bash
python backend/app/main.py
```

The FastAPI server will start at `http://127.0.0.1:8000`. Interactive API docs are available at `http://127.0.0.1:8000/docs`.

### 5. Start the Frontend Dashboard

```bash
streamlit run frontend/app.py
```

The Streamlit dashboard will open at `http://localhost:8501`.

---

## API Reference

### Health Check

```
GET /api/v1/health
```

Returns backend status and API key configuration.

### First-Stage Screening

```
GET /api/v1/screen
```

Runs all stocks through the three-gate screening criteria. Returns passed and failed lists with detailed reasons.

### Deep-Dive Analysis (with file upload)

```
POST /api/v1/analyze/{ticker}
```

| Parameter | Type | Description |
|---|---|---|
| `ticker` | path | Stock ticker symbol (e.g., `PTT`) |
| `cvup_file` | file (optional) | Corporate Value-Up Plan PDF |
| `onereport_file` | file (optional) | Form 56-1 One Report PDF |
| `audio_file` | file (optional) | Opportunity Day audio (MP3/WAV) |

### Get Report (no upload)

```
GET /api/v1/report/{ticker}
```

Retrieves or generates a report using previously uploaded files or mock data.

---

## Screening Pipeline

The analysis pipeline processes each stock through two stages:

### Stage 1: Hard Screening (Gate)

All three criteria must pass:

| # | Criterion | Threshold | Source |
|---|---|---|---|
| 1 | JUMP+ Membership | Must be enrolled | SET / ตลท. |
| 2 | CGR Score | ≥ 90 (Excellent / 5 stars) | IOD Thailand |
| 3 | SEC Prosecution History | No cases in past 5 years | Thai SEC / ก.ล.ต. |

### Stage 2: Deep-Dive Analysis

For stocks that pass Stage 1:

| Component | Weight | Method |
|---|---|---|
| CGR Score | 30% | Normalized from CGR score (0–100) |
| SEC Clean Record | 20% | Binary: 20 pts if clean, 0 if not |
| CVUP ↔ One Report Alignment | 30% | Claude AI cross-reference analysis |
| Audio Voice Credibility | 20% | Typhoon2-Audio sincerity scoring |

**Final Score** = Sum of all weighted components (0–100)

---

## Configuration

Scoring weights are configurable in `backend/app/config.py`:

```python
WEIGHT_CGR: float = 0.30          # Corporate Governance Rating
WEIGHT_SEC: float = 0.20          # SEC clean record
WEIGHT_CVUP_ALIGN: float = 0.30   # Document alignment
WEIGHT_AUDIO_CRED: float = 0.20   # Audio credibility
```

---

## Testing

Run the test suite with pytest:

```bash
pytest tests/ -v
```

Available test modules:

| Test File | Coverage |
|---|---|
| `test_set_service.py` | SET stock data retrieval & screening logic |
| `test_sec_service.py` | SEC prosecution history lookup & clean check |
| `test_audio_service.py` | Audio analysis mock fallback behavior |
| `test_vector_db.py` | PDF ingestion, TF-IDF indexing, and search |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is part of an academic/research initiative. Please contact the maintainers for licensing inquiries.

---

<p align="center">
  Built with 🌱 by the ESG Analyst Agent Team
</p>