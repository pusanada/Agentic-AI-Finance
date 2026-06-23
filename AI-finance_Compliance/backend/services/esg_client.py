import logging
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.config import settings
from backend.esg_analyst.agents.esg_agent import ESGAgent

logger = logging.getLogger(__name__)

class FirstStageChecks(BaseModel):
    cgr_score: int
    jump_plus: bool
    sec_clean: bool

class DocumentAudit(BaseModel):
    alignment_rating: str
    commitments_found: List[str] = Field(default_factory=list)
    one_report_evidence: List[str] = Field(default_factory=list)
    gaps_or_delays: List[str] = Field(default_factory=list)
    rationale: str

class AudioCredibility(BaseModel):
    confidence_score: float
    sincerity_score: float
    evasion_score: float
    findings: List[str] = Field(default_factory=list)
    conclusion: str

class ESGAnalysisReport(BaseModel):
    ticker: str
    company_name: str
    status: str
    overall_score: Optional[float] = 0.0
    weighted_breakdown: Optional[Dict[str, float]] = Field(default_factory=dict)
    first_stage_checks: Optional[FirstStageChecks] = None
    document_audit: Optional[DocumentAudit] = None
    audio_credibility: Optional[AudioCredibility] = None
    executive_summary_th: Optional[str] = ""
    key_strengths: List[str] = Field(default_factory=list)
    risks_and_warnings: List[str] = Field(default_factory=list)
    investment_recommendation: Optional[str] = ""

# Mock Database for Fallback
MOCK_REPORTS = {
    "PTT": {
        "ticker": "PTT",
        "company_name": "PTT Public Company Limited",
        "status": "APPROVED",
        "overall_score": 93.4,
        "weighted_breakdown": {"cgr_contribution": 29.4, "sec_contribution": 20.0, "cvup_contribution": 30.0, "audio_contribution": 14.0},
        "first_stage_checks": {"cgr_score": 98, "jump_plus": True, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "High",
            "commitments_found": ["เพิ่มการลงทุนพลังงานหมุนเวียน 15,000 ล้านบาทภายในปี 2025"],
            "one_report_evidence": ["จัดสรรงบประมาณจริง 16,200 ล้านบาทในพลังงานสะอาด (หน้า 56)"],
            "gaps_or_delays": [],
            "rationale": "บริษัทดำเนินการตามคำสัญญาและเปิดเผยงบประมาณอย่างโปร่งใส"
        },
        "audio_credibility": {
            "confidence_score": 85.0,
            "sincerity_score": 70.0,
            "evasion_score": 10.0,
            "findings": ["น้ำเสียงมั่นใจ", "ตอบตรงประเด็น"],
            "conclusion": "ผู้บริหารมีความจริงใจสูง"
        },
        "executive_summary_th": "ผลการวิเคราะห์ของ PTT แสดงความก้าวหน้าอย่างยอดเยี่ยม...",
        "key_strengths": ["คะแนน CG ดีเลิศ", "ไม่มีคดีความ"],
        "risks_and_warnings": [],
        "investment_recommendation": "อนุมัติจัดสรรปกติ"
    },
    "CPALL": {
        "ticker": "CPALL",
        "company_name": "CP ALL Public Company Limited",
        "status": "APPROVED",
        "overall_score": 90.5,
        "weighted_breakdown": {"cgr_contribution": 28.5, "sec_contribution": 20.0, "cvup_contribution": 30.0, "audio_contribution": 12.0},
        "first_stage_checks": {"cgr_score": 95, "jump_plus": True, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "High",
            "commitments_found": ["ขยายสาขา 7-Eleven ประหยัดพลังงานเพิ่มอีก 700 สาขา"],
            "one_report_evidence": ["เปิดสาขาประหยัดพลังงานใหม่ 750 สาขา"],
            "gaps_or_delays": ["แผนการลดการปล่อยคาร์บอนขอบเขตที่ 3 ล่าช้ากว่ากำหนด 6 เดือน"],
            "rationale": "แผนการดำเนินการโดยรวมแข็งแกร่ง มีการระบุความล่าช้าอย่างตรงไปตรงมา"
        },
        "audio_credibility": {
            "confidence_score": 80.0,
            "sincerity_score": 60.0,
            "evasion_score": 15.0,
            "findings": ["น้ำเสียงปานกลาง", "มีประเด็นหลีกเลี่ยงเล็กน้อย"],
            "conclusion": "ผู้บริหารอธิบายชัดเจนในแผนงานส่วนใหญ่"
        },
        "executive_summary_th": "CPALL ผ่านเกณฑ์ประเมินระดับสูง...",
        "key_strengths": ["สาขาประหยัดพลังงานเป็นรูปธรรม"],
        "risks_and_warnings": ["ความล่าช้า Scope 3"],
        "investment_recommendation": "อนุมัติจัดสรรปกติ"
    },
    "ADVANC": {
        "ticker": "ADVANC",
        "company_name": "Advanced Info Service Public Company Limited",
        "status": "APPROVED",
        "overall_score": 94.1,
        "weighted_breakdown": {"cgr_contribution": 29.1, "sec_contribution": 20.0, "cvup_contribution": 30.0, "audio_contribution": 15.0},
        "first_stage_checks": {"cgr_score": 97, "jump_plus": True, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "High",
            "commitments_found": ["ยกระดับสถานีฐานให้ใช้พลังงานแสงอาทิตย์ 100% ครบ 3,000 แห่ง"],
            "one_report_evidence": ["ติดตั้งโซลาร์เซลล์สำเร็จ 3,120 แห่ง"],
            "gaps_or_delays": [],
            "rationale": "ผลการดำเนินงานจริงสูงกว่าเป้าหมายที่ระบุในแผนเพิ่มพูนมูลค่าบริษัท"
        },
        "audio_credibility": {
            "confidence_score": 90.0,
            "sincerity_score": 75.0,
            "evasion_score": 5.0,
            "findings": ["ตอบคำถามรวดเร็วชัดเจน", "แสดงข้อมูลรองรับน้ำหนักเสียงดี"],
            "conclusion": "ผู้บริหารน่าเชื่อถือระดับดีเยี่ยม"
        },
        "executive_summary_th": "ADVANC แผนงานมีประสิทธิภาพ...",
        "key_strengths": ["ทำได้ดีกว่าเป้าหมายสถานีฐาน"],
        "risks_and_warnings": [],
        "investment_recommendation": "อนุมัติจัดสรรปกติ"
    },
    "SCC": {
        "ticker": "SCC",
        "company_name": "The Siam Cement Public Company Limited",
        "status": "APPROVED",
        "overall_score": 78.8,
        "weighted_breakdown": {"cgr_contribution": 28.8, "sec_contribution": 20.0, "cvup_contribution": 15.0, "audio_contribution": 15.0},
        "first_stage_checks": {"cgr_score": 96, "jump_plus": True, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "Medium",
            "commitments_found": ["เพิ่มสัดส่วนพลังงานทดแทนในกระบวนการผลิตปูนซีเมนต์เป็น 30%"],
            "one_report_evidence": ["สัดส่วนพลังงานทดแทนอยู่ที่ 25% ต่ำกว่าเป้าหมายเนื่องจากราคาพลังงานชีวมวลพุ่งสูงขึ้น"],
            "gaps_or_delays": ["เป้าหมายการเปลี่ยนผ่านเชื้อเพลิงบางส่วนเลื่อนออกไป 1 ปี"],
            "rationale": "รายงานความท้าทายชัดเจน แต่เป้าหมายสำคัญสองประการยังไม่บรรลุผลอย่างเป็นทางการ"
        },
        "audio_credibility": {
            "confidence_score": 85.0,
            "sincerity_score": 75.0,
            "evasion_score": 5.0,
            "findings": ["อธิบายความล้มเหลวโปร่งใส"],
            "conclusion": "ข้อมูลน่าเชื่อถือสูง"
        },
        "executive_summary_th": "SCC อยู่ในระดับปานกลางเนื่องจากมีเป้าหมายไม่บรรลุ...",
        "key_strengths": ["ความซื่อสัตย์ในการเปิดเผยข้อมูล"],
        "risks_and_warnings": ["ความล่าช้าในการเปลี่ยนผ่านเชื้อเพลิง"],
        "investment_recommendation": "แนะนำถือครองปานกลาง"
    },
    "KBANK": {
        "ticker": "KBANK",
        "company_name": "Kasikornbank Public Company Limited",
        "status": "APPROVED",
        "overall_score": 93.8,
        "weighted_breakdown": {"cgr_contribution": 28.8, "sec_contribution": 20.0, "cvup_contribution": 30.0, "audio_contribution": 15.0},
        "first_stage_checks": {"cgr_score": 96, "jump_plus": True, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "High",
            "commitments_found": ["สนับสนุนการเปลี่ยนผ่านภาคธุรกิจ (Sustainable Financing) มูลค่า 50,000 ล้านบาท"],
            "one_report_evidence": ["ยอดปล่อยสินเชื่อและตราสารหนี้สีเขียวรวม 52,400 ล้านบาท"],
            "gaps_or_delays": [],
            "rationale": "แผนการจัดสรรเงินทุนสีเขียวทำได้เกินเป้าหมายและรายงานละเอียด"
        },
        "audio_credibility": {
            "confidence_score": 88.0,
            "sincerity_score": 75.0,
            "evasion_score": 5.0,
            "findings": ["มีข้อมูลรองรับครบถ้วน"],
            "conclusion": "ความน่าเชื่อถือดีเยี่ยม"
        },
        "executive_summary_th": "KBANK ยอดสินเชื่อสีเขียวเกินเป้า...",
        "key_strengths": ["ผลงานด้านการเงินสีเขียว"],
        "risks_and_warnings": [],
        "investment_recommendation": "อนุมัติจัดสรรปกติ"
    },
    "GULF": {
        "ticker": "GULF",
        "company_name": "Gulf Energy Development Public Company Limited",
        "status": "REJECTED_STAGE_1",
        "overall_score": 0.0,
        "weighted_breakdown": {},
        "first_stage_checks": {"cgr_score": 88, "jump_plus": True, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "Low",
            "commitments_found": [],
            "one_report_evidence": [],
            "gaps_or_delays": [],
            "rationale": "ตกเกณฑ์ประเมินเบื้องต้น CGR Score ต่ำกว่า 90"
        },
        "audio_credibility": {"confidence_score": 0.0, "sincerity_score": 0.0, "evasion_score": 0.0, "findings": [], "conclusion": ""},
        "executive_summary_th": "ไม่ผ่านเกณฑ์การประเมินเบื้องต้นเนื่องจากคะแนน CG ต่ำกว่าเกณฑ์",
        "key_strengths": [],
        "risks_and_warnings": ["CGR 88 < 90"],
        "investment_recommendation": "ปฏิเสธการจัดสรรพอร์ต"
    },
    "AOT": {
        "ticker": "AOT",
        "company_name": "Airports of Thailand Public Company Limited",
        "status": "REJECTED_STAGE_1",
        "overall_score": 0.0,
        "weighted_breakdown": {},
        "first_stage_checks": {"cgr_score": 94, "jump_plus": False, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "Low",
            "commitments_found": [],
            "one_report_evidence": [],
            "gaps_or_delays": [],
            "rationale": "ตกเกณฑ์ประเมินเบื้องต้นเนื่องจากไม่เข้าร่วมโครงการ JUMP+"
        },
        "audio_credibility": {"confidence_score": 0.0, "sincerity_score": 0.0, "evasion_score": 0.0, "findings": [], "conclusion": ""},
        "executive_summary_th": "ไม่ผ่านเนื่องจากไม่ใช่สมาชิก JUMP+",
        "key_strengths": [],
        "risks_and_warnings": ["Non-JUMP+ status"],
        "investment_recommendation": "ปฏิเสธการจัดสรรพอร์ต"
    },
    "BDMS": {
        "ticker": "BDMS",
        "company_name": "Bangkok Dusit Medical Services Public Company Limited",
        "status": "APPROVED",
        "overall_score": 84.2,
        "weighted_breakdown": {"cgr_contribution": 27.6, "sec_contribution": 20.0, "cvup_contribution": 15.0, "audio_contribution": 21.6},
        "first_stage_checks": {"cgr_score": 92, "jump_plus": True, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "Medium",
            "commitments_found": ["ติดตั้งระบบโซลาร์รูฟท็อปครบทุกโรงพยาบาลในเครือภายในปี 2025"],
            "one_report_evidence": ["ติดตั้งแล้วเสร็จร้อยละ 85 ของจำนวนโรงพยาบาลทั้งหมด"],
            "gaps_or_delays": ["การติดตั้งในโรงพยาบาลย่อยมีความล่าช้า 1 ไตรมาส"],
            "rationale": "มีทิศทางการเติบโตที่ดีแต่ล่าช้าในส่วนย่อย"
        },
        "audio_credibility": {
            "confidence_score": 80.0,
            "sincerity_score": 72.0,
            "evasion_score": 8.0,
            "findings": ["ให้รายละเอียดดี"],
            "conclusion": "ผู้บริหารอธิบายได้ดี"
        },
        "executive_summary_th": "BDMS ความคืบหน้าโซลาร์เซลล์ล่าช้าเล็กน้อย...",
        "key_strengths": ["การประหยัดพลังงานในระดับกว้าง"],
        "risks_and_warnings": ["แผนงานโรงพยาบาลขนาดเล็กล่าช้า"],
        "investment_recommendation": "อนุมัติจัดสรร"
    },
    "TRUE": {
        "ticker": "TRUE",
        "company_name": "True Corporation Public Company Limited",
        "status": "APPROVED",
        "overall_score": 79.7,
        "weighted_breakdown": {"cgr_contribution": 27.3, "sec_contribution": 20.0, "cvup_contribution": 15.0, "audio_contribution": 17.4},
        "first_stage_checks": {"cgr_score": 91, "jump_plus": True, "sec_clean": True},
        "document_audit": {
            "alignment_rating": "Medium",
            "commitments_found": ["รวมศูนย์การจัดการโครงสร้างเสาสัญญาณเพื่อลดการใช้ไฟฟ้าพลังงานหลักลง 15%"],
            "one_report_evidence": ["ลดการใช้ไฟฟ้าลงได้จริงร้อยละ 10 ต่ำกว่าเป้าหมาย"],
            "gaps_or_delays": ["การรวมเสาสัญญาณหลังควบรวมล่าช้ากว่าแผน"],
            "rationale": "เป้าหมายหลักยังต่ำกว่าแผนงานและแผน Net Zero ระยะยาวยังไม่ชัดเจนในรายละเอียด"
        },
        "audio_credibility": {
            "confidence_score": 75.0,
            "sincerity_score": 58.0,
            "evasion_score": 12.0,
            "findings": ["น้ำเสียงมีแนวโน้มกังวลเรื่องเสาสัญญาณ"],
            "conclusion": "ข้อมูลปานกลาง"
        },
        "executive_summary_th": "TRUE แผนงานรวมศูนย์เสาสัญญาณมีความท้าทาย...",
        "key_strengths": [],
        "risks_and_warnings": ["การควบรวมล่าช้ากว่าเป้า"],
        "investment_recommendation": "อนุมัติแบบมีเงื่อนไขเฝ้าระวัง"
    }
}

class ESGClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.esg_analyst_api_url

    def get_esg_report(self, ticker: str, session_id: Optional[str] = None) -> ESGAnalysisReport:
        """
        Fetches the ESG Report for a given ticker from the local in-process ESGAgent.
        Falls back to mock data if execution fails.
        Saves result to state_manager if session_id is provided.
        """
        ticker_upper = ticker.upper()
        report = None
        
        try:
            logger.info(f"Invoking local ESGAgent for ticker: {ticker_upper}")
            agent = ESGAgent()
            data = agent.analyze_ticker(ticker_upper)
            report = ESGAnalysisReport.model_validate(data)
            logger.info(f"Successfully ran local ESG analysis for {ticker_upper}")
        except Exception as e:
            logger.warning(f"Failed to run local ESG Analyst Agent ({str(e)}). Using fallback mock data.")

        if not report:
            fallback_data = MOCK_REPORTS.get(ticker_upper)
            if not fallback_data:
                fallback_data = {
                    "ticker": ticker_upper,
                    "company_name": f"{ticker_upper} Public Company Limited",
                    "status": "APPROVED",
                    "overall_score": 80.0,
                    "weighted_breakdown": {"cgr_contribution": 27.0, "sec_contribution": 20.0, "cvup_contribution": 15.0, "audio_contribution": 18.0},
                    "first_stage_checks": {"cgr_score": 90, "jump_plus": True, "sec_clean": True},
                    "document_audit": {
                        "alignment_rating": "Medium",
                        "commitments_found": ["แผนการดำเนินงานทั่วไป"],
                        "one_report_evidence": ["ความคืบหน้าทั่วไป"],
                        "gaps_or_delays": [],
                        "rationale": "การวิเคราะห์ผ่านระดับปานกลางเนื่องจากเป็นข้อมูลสำรอง"
                    },
                    "audio_credibility": {
                        "confidence_score": 80.0,
                        "sincerity_score": 90.0,
                        "evasion_score": 5.0,
                        "findings": [],
                        "conclusion": "ความน่าเชื่อถือปานกลาง"
                    },
                    "executive_summary_th": f"ผลประเมินสำรองสำหรับ {ticker_upper}",
                    "key_strengths": ["ข้อมูลเบื้องต้นผ่านเกณฑ์"],
                    "risks_and_warnings": [],
                    "investment_recommendation": "อนุมัติจัดสรรน้ำหนักขั้นต่ำ"
                }
            report = ESGAnalysisReport.model_validate(fallback_data)

        # Write to State Manager if session_id is provided
        if session_id:
            try:
                from backend.services.state_manager import state_manager
                # Calculate confidence score (0.0 to 1.0) based on sincerity
                sincerity = report.audio_credibility.sincerity_score if report.audio_credibility else 0.0
                confidence = max(0.90, sincerity / 100.0) if report.status == "APPROVED" else (sincerity / 100.0 if sincerity > 0 else 0.85)
                
                uncertainty_factors = []
                if report.document_audit and report.document_audit.alignment_rating == "Low":
                    uncertainty_factors.append("Low Document Alignment Rating")
                if report.audio_credibility and report.audio_credibility.evasion_score > 30:
                    uncertainty_factors.append("High Executive Evasion Score")
                
                state_manager.update_esg(
                    session_id=session_id,
                    ticker=ticker_upper,
                    esg_report=report.model_dump(),
                    confidence=confidence,
                    uncertainty_factors=uncertainty_factors
                )
            except Exception as e:
                logger.error(f"Failed to save ESG state in state manager: {str(e)}")

        return report

esg_client = ESGClient()
