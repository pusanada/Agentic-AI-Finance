import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient
from backend.main import app
from backend.services.state_manager import state_manager

def run_audit():
    client = TestClient(app)
    session_id = "SUPERVISOR-TEST-001"
    
    # Clean previous state
    state_manager.clear()
    
    payload = {
        "assessable_income": 1200000.0,
        "already_purchased": 0.0,
        "financial_goal": "Balanced",
        "risk_profile": "moderate",
        "user_instructions": "",
        "ocr_confidence": 0.95,
        "session_id": session_id
    }
    
    trace_steps = []
    trace_steps.append("Step 1: Initializing SUPERVISOR-TEST-001 audit session...")
    
    # 1. Execute OCR and allocate portfolio
    trace_steps.append("Step 2: Triggering API Portfolio Allocation and Compliance Guard Loop...")
    response = client.post("/api/v1/portfolio/allocate", json=payload)
    
    assert response.status_code == 200, f"API call failed with status: {response.status_code}"
    res_data = response.json()
    
    trace_steps.append("Step 3: API execution completed successfully.")
    
    # Retrieve Unified Workflow State
    state = state_manager.get_or_create_state(session_id)
    
    # Auditing requirements
    pass_status = "PASS"
    violations = []
    
    # R1: Direct check in code for ESG -> Compliance direct calls
    guard_code_path = Path(__file__).resolve().parent.parent / "services" / "compliance_guard.py"
    with open(guard_code_path, "r", encoding="utf-8") as f:
        code_content = f.read()
        
    if "from backend.services.esg_client import esg_client" in code_content or "import esg_client" in code_content:
        violations.append("Architecture Violation: Direct imports of esg_client found in compliance_guard.py!")
        pass_status = "FAIL"
    else:
        trace_steps.append("Audit Verification: Compliance Guard contains ZERO direct esg_client calls (PASSED).")
        
    # R2: Envelope metadata check
    for key in ["ocr", "portfolio", "compliance", "auq"]:
        envelope = getattr(state, key)
        if not envelope:
            violations.append(f"Missing State Envelope: {key} was not populated in state!")
            pass_status = "FAIL"
            continue
            
        metadata = envelope.metadata
        if not all(hasattr(metadata, attr) for attr in ["agent", "schema_version", "generated_at", "confidence", "uncertainty_factors"]):
            violations.append(f"Invalid Envelope Metadata structure for agent: {key}")
            pass_status = "FAIL"
            
    # R3: ESG state population
    if not state.esg:
        violations.append("Missing ESG State Envelopes for underlying stocks!")
        pass_status = "FAIL"
        
    # R4: AUQ Calculations
    overall_conf = state.overall_confidence
    uncertainty_score = state.uncertainty_score
    requires_human_review = state.requires_human_review
    
    trace_steps.append(f"AUQ Calculations: overall_confidence={overall_conf}, uncertainty_score={uncertainty_score}, requires_human_review={requires_human_review}")
    
    # Trigger checks
    expected_trigger = (overall_conf < 0.75) or (uncertainty_score > 0.30)
    if requires_human_review != expected_trigger:
        violations.append(f"AUQ Logic Failure: requires_human_review is {requires_human_review} but expected {expected_trigger}")
        pass_status = "FAIL"
        
    # Generate MD report
    report_lines = []
    report_lines.append("# Supervisor End-to-End Validation & Audit Report")
    report_lines.append(f"**Audit Target Session**: `{session_id}`")
    report_lines.append(f"**Overall Status**: `{pass_status}`\n")
    
    report_lines.append("## Workflow Execution Trace")
    for step in trace_steps:
        report_lines.append(f"- {step}")
    report_lines.append("")
    
    report_lines.append("## State Snapshots by Step")
    report_lines.append("### 1. OCR State Envelope")
    report_lines.append(f"```json\n{json.dumps(state.ocr.model_dump() if state.ocr else {}, indent=2, ensure_ascii=False)}\n```")
    report_lines.append("### 2. Portfolio Allocator State Envelope")
    report_lines.append(f"```json\n{json.dumps(state.portfolio.model_dump() if state.portfolio else {}, indent=2, ensure_ascii=False)}\n```")
    report_lines.append("### 3. ESG Stocks Envelopes")
    report_lines.append("```json")
    for ticker, env in state.esg.items():
        report_lines.append(f'"{ticker}": {json.dumps(env.model_dump(), indent=2, ensure_ascii=False)}')
    report_lines.append("```")
    report_lines.append("### 4. Compliance Guard State Envelope")
    report_lines.append(f"```json\n{json.dumps(state.compliance.model_dump() if state.compliance else {}, indent=2, ensure_ascii=False)}\n```")
    report_lines.append("### 5. AUQ Supervisor State Envelope")
    report_lines.append(f"```json\n{json.dumps(state.auq.model_dump() if state.auq else {}, indent=2, ensure_ascii=False)}\n```")
    report_lines.append("")
    
    report_lines.append("## AUQ Calculation & Human Review Decision")
    report_lines.append(f"- **Overall Confidence**: `{overall_conf}` (Threshold for Human Review: `< 0.75`)")
    report_lines.append(f"- **Uncertainty Score**: `{uncertainty_score}` (Threshold for Human Review: `> 0.30`)")
    report_lines.append(f"- **Human Review Triggered**: `{requires_human_review}`")
    report_lines.append("")
    
    report_lines.append("## Architecture Violations Detected")
    if violations:
        for v in violations:
            report_lines.append(f"- 🛑 {v}")
    else:
        report_lines.append("- ✅ Zero violations detected! Clean implementation.")
    report_lines.append("")
    
    report_lines.append("## Recommendations")
    report_lines.append("1. **State Memory Management**: The current in-memory cache for state is session-based. Consider backing it with Redis or ChromaDB for multi-instance production scalability.")
    report_lines.append("2. **Strong Typing on Data Envelope**: Use Pydantic's generic models `Envelope[T]` instead of `Any` to guarantee strict deserialization schemas of agent data fields in production.")
    
    report_path = Path("C:/Users/LOQ/.gemini/antigravity-ide/brain/dff42c39-5c2e-42af-ba7f-077a39976978/supervisor_e2e_audit_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Audit completed. Report generated at: {report_path}")
    print(f"Status: {pass_status}")

if __name__ == "__main__":
    run_audit()
