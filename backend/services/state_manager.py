import time
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class AgentMetadata(BaseModel):
    agent: str
    schema_version: str = "1.0.0"
    generated_at: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    uncertainty_factors: List[str] = Field(default_factory=list)

class OCRStateEnvelope(BaseModel):
    metadata: AgentMetadata
    data: Any

class ESGStateEnvelope(BaseModel):
    metadata: AgentMetadata
    data: Any

class PortfolioStateEnvelope(BaseModel):
    metadata: AgentMetadata
    data: Any

class ComplianceStateEnvelope(BaseModel):
    metadata: AgentMetadata
    data: Any

class AUQStateEnvelope(BaseModel):
    metadata: AgentMetadata
    data: Any

class UnifiedWorkflowState(BaseModel):
    session_id: str
    ocr: Optional[OCRStateEnvelope] = None
    esg: Dict[str, ESGStateEnvelope] = Field(default_factory=dict)  # ticker -> report
    portfolio: Optional[PortfolioStateEnvelope] = None
    compliance: Optional[ComplianceStateEnvelope] = None
    auq: Optional[AUQStateEnvelope] = None
    overall_confidence: float = 1.0
    uncertainty_score: float = 0.0
    requires_human_review: bool = False

class ESGStateManager:
    def __init__(self):
        self._states: Dict[str, UnifiedWorkflowState] = {}

    def get_or_create_state(self, session_id: str) -> UnifiedWorkflowState:
        if session_id not in self._states:
            self._states[session_id] = UnifiedWorkflowState(session_id=session_id)
            logger.info(f"Created new UnifiedWorkflowState for session: {session_id}")
        return self._states[session_id]

    def update_ocr(self, session_id: str, ocr_result: Any, confidence: float, uncertainty_factors: List[str] = None):
        state = self.get_or_create_state(session_id)
        metadata = AgentMetadata(
            agent="OCR_Tax_Agent",
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            confidence=confidence,
            uncertainty_factors=uncertainty_factors or []
        )
        state.ocr = OCRStateEnvelope(metadata=metadata, data=ocr_result)
        logger.info(f"Updated OCR state in session {session_id}")
        self._recalculate_uncertainty(state)

    def update_esg(self, session_id: str, ticker: str, esg_report: Any, confidence: float, uncertainty_factors: List[str] = None):
        state = self.get_or_create_state(session_id)
        metadata = AgentMetadata(
            agent="ESG_Analyst_Agent",
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            confidence=confidence,
            uncertainty_factors=uncertainty_factors or []
        )
        state.esg[ticker.upper()] = ESGStateEnvelope(metadata=metadata, data=esg_report)
        logger.info(f"Updated ESG state for {ticker.upper()} in session {session_id}")
        self._recalculate_uncertainty(state)

    def update_portfolio(self, session_id: str, portfolio: Any, confidence: float, uncertainty_factors: List[str] = None):
        state = self.get_or_create_state(session_id)
        metadata = AgentMetadata(
            agent="Portfolio_Allocator_Agent",
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            confidence=confidence,
            uncertainty_factors=uncertainty_factors or []
        )
        state.portfolio = PortfolioStateEnvelope(metadata=metadata, data=portfolio)
        logger.info(f"Updated Portfolio state in session {session_id}")
        self._recalculate_uncertainty(state)

    def update_compliance(self, session_id: str, compliance: Any, confidence: float, uncertainty_factors: List[str] = None):
        state = self.get_or_create_state(session_id)
        metadata = AgentMetadata(
            agent="Compliance_Guard_Agent",
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            confidence=confidence,
            uncertainty_factors=uncertainty_factors or []
        )
        state.compliance = ComplianceStateEnvelope(metadata=metadata, data=compliance)
        logger.info(f"Updated Compliance state in session {session_id}")
        self._recalculate_uncertainty(state)

    def update_auq(self, session_id: str, auq_report: Any, confidence: float, uncertainty_factors: List[str] = None):
        state = self.get_or_create_state(session_id)
        metadata = AgentMetadata(
            agent="AUQ_Manager_Agent",
            generated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            confidence=confidence,
            uncertainty_factors=uncertainty_factors or []
        )
        state.auq = AUQStateEnvelope(metadata=metadata, data=auq_report)
        logger.info(f"Updated AUQ state in session {session_id}")

    def _recalculate_uncertainty(self, state: UnifiedWorkflowState):
        """
        Recalculates overall confidence score and uncertainty level for the session.
        Formula: Confidence_overall = Conf_ocr * Conf_esg_avg * Conf_alloc * Conf_comp
        """
        ocr_conf = state.ocr.metadata.confidence if state.ocr else 1.0
        
        esg_conf_list = [env.metadata.confidence for env in state.esg.values()]
        esg_conf = sum(esg_conf_list) / len(esg_conf_list) if esg_conf_list else 1.0
        
        alloc_conf = state.portfolio.metadata.confidence if state.portfolio else 1.0
        comp_conf = state.compliance.metadata.confidence if state.compliance else 1.0
        
        overall_confidence = ocr_conf * esg_conf * alloc_conf * comp_conf
        state.overall_confidence = round(overall_confidence, 4)
        state.uncertainty_score = round(1.0 - overall_confidence, 4)
        
        # Trigger human review if overall_confidence < 0.75 or uncertainty_score > 0.30
        state.requires_human_review = (state.overall_confidence < 0.75) or (state.uncertainty_score > 0.30)
        logger.info(f"Recalculated state for session {state.session_id}: overall_conf={state.overall_confidence}, requires_human_review={state.requires_human_review}")

    def clear(self):
        self._states.clear()

state_manager = ESGStateManager()
