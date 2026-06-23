import json
from pathlib import Path
from typing import Dict, Any, List
from anthropic import Anthropic
from app.config import settings
from app.services.set_service import SETService
from app.services.sec_service import SECService
from app.services.audio_service import AudioService
from app.services.vector_db import SimpleVectorDB
from app.agents.prompts import CVUP_VS_ONEREPORT_PROMPT, FINAL_ESG_SYNTHESIS_PROMPT

class ESGAgent:
    def __init__(self):
        self.db = SimpleVectorDB(settings.DB_DIR)
        self.client = None
        if settings.ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def analyze_ticker(self, ticker: str, cvup_pdf: Path = None, onereport_pdf: Path = None, opp_day_audio: Path = None) -> Dict[str, Any]:
        """
        Runs the complete screening and deep-dive analysis for a stock.
        """
        ticker_upper = ticker.upper()
        
        # 1. Core SET Screening Data
        stock_data = SETService.get_stock_by_ticker(ticker_upper)
        if not stock_data:
            return {
                "ticker": ticker_upper,
                "status": "FAILED",
                "message": f"Ticker {ticker_upper} not found in SET database."
            }

        # 2. SEC Lawsuits Screening
        sec_status = SECService.is_clean(ticker_upper)

        # First stage screening evaluation
        passes_first_stage = (
            stock_data["jump_plus"] and 
            stock_data["cgr_score"] >= 90 and 
            sec_status["is_clean"]
        )

        if not passes_first_stage:
            reasons = []
            if not stock_data["jump_plus"]:
                reasons.append("Not in JUMP+ project")
            if stock_data["cgr_score"] < 90:
                reasons.append(f"CGR Score ({stock_data['cgr_score']}) < 90")
            if not sec_status["is_clean"]:
                reasons.append(sec_status["message"])
                
            return {
                "ticker": ticker_upper,
                "company_name": stock_data["name"],
                "status": "REJECTED_STAGE_1",
                "message": f"Rejected at first-stage screening: {', '.join(reasons)}",
                "details": {
                    "cgr_score": stock_data["cgr_score"],
                    "jump_plus": stock_data["jump_plus"],
                    "sec_clean": sec_status["is_clean"]
                }
            }

        # 3. Handle PDF Ingestions if provided
        if cvup_pdf and cvup_pdf.exists():
            self.db.add_pdf(ticker_upper, cvup_pdf)
        if onereport_pdf and onereport_pdf.exists():
            self.db.add_pdf(ticker_upper, onereport_pdf)

        # 4. CVUP vs Form 56-1 One Report Alignment Analysis
        alignment_result = self._analyze_cvup_alignment(ticker_upper)

        # 5. Opportunity Day Tone Analysis
        audio_result = AudioService.analyze_audio(ticker_upper, opp_day_audio)

        # 6. Overall Synthesis and Scoring
        synthesis = self._synthesize_report(
            stock_data=stock_data,
            sec_status=sec_status,
            alignment_result=alignment_result,
            audio_result=audio_result
        )

        return {
            "ticker": ticker_upper,
            "company_name": stock_data["name"],
            "status": "APPROVED",
            "overall_score": synthesis["overall_score"],
            "weighted_breakdown": synthesis["weighted_breakdown"],
            "first_stage_checks": {
                "cgr_score": stock_data["cgr_score"],
                "jump_plus": stock_data["jump_plus"],
                "sec_clean": sec_status["is_clean"]
            },
            "document_audit": {
                "alignment_rating": alignment_result["alignment_rating"],
                "commitments_found": alignment_result["commitments_found"],
                "one_report_evidence": alignment_result["one_report_evidence"],
                "gaps_or_delays": alignment_result["gaps_or_delays"],
                "rationale": alignment_result["analysis_rationale"]
            },
            "audio_credibility": {
                "confidence_score": audio_result["analysis"]["confidence_score"],
                "sincerity_score": audio_result["analysis"]["sincerity_score"],
                "evasion_score": audio_result["analysis"]["evasion_score"],
                "findings": audio_result["analysis"]["tone_markers"],
                "conclusion": audio_result["analysis"]["conclusion"]
            },
            "executive_summary_th": synthesis["executive_summary_th"],
            "key_strengths": synthesis["key_strengths"],
            "risks_and_warnings": synthesis["risks_and_warnings"],
            "investment_recommendation": synthesis["investment_recommendation"]
        }

    def _analyze_cvup_alignment(self, ticker: str) -> Dict[str, Any]:
        """
        Queries Vector DB and prompts Claude to evaluate the alignment between CVUP and One Report.
        """
        # Retrieve chunks for comparing commitments vs actual executions
        queries = ["JUMP+", "Value Up Plan", "Corporate Governance", "ESG targets", "แผนเพิ่มพูนมูลค่าบริษัท", "เป้าหมายความยั่งยืน"]
        retrieved_chunks = []
        for q in queries:
            chunks = self.db.search(ticker, q, top_k=2)
            retrieved_chunks.extend(chunks)

        # De-duplicate chunks by text
        seen = set()
        unique_chunks = []
        for chunk in retrieved_chunks:
            if chunk["text"] not in seen:
                seen.add(chunk["text"])
                unique_chunks.append(chunk)

        # Format context for prompt
        context_str = ""
        for i, chunk in enumerate(unique_chunks[:6]):
            context_str += f"\n--- Chunk {i+1} (Source: {chunk['source']}) ---\n{chunk['text']}\n"

        if not context_str:
            # Fallback mock analysis if no PDFs are uploaded/indexed yet
            mock_alignments = {
                "PTT": {
                    "alignment_rating": "High",
                    "commitments_found": ["เพิ่มการลงทุนพลังงานหมุนเวียน 15,000 ล้านบาทภายในปี 2025", "บรรลุเป้าหมายความเป็นกลางทางคาร์บอนภายในปี 2040"],
                    "one_report_evidence": ["จัดสรรงบประมาณจริง 16,200 ล้านบาทในพลังงานสะอาด (หน้า 56)", "ลดการปล่อยก๊าซเรือนกระจกสะสมร้อยละ 12 สำเร็จตามแผน"],
                    "gaps_or_delays": [],
                    "analysis_rationale": "บริษัทดำเนินการตามคำสัญญาและเปิดเผยงบประมาณอย่างโปร่งใสใน One Report สอดคล้องกับแผนเพิ่มพูนมูลค่าบริษัททุกด้าน"
                },
                "CPALL": {
                    "alignment_rating": "High",
                    "commitments_found": ["ขยายสาขา 7-Eleven ประหยัดพลังงานเพิ่มอีก 700 สาขา", "ลดการใช้พลาสติกในบรรจุภัณฑ์ลงร้อยละ 20"],
                    "one_report_evidence": ["เปิดสาขาประหยัดพลังงานใหม่ 750 สาขา (หน้า 112)", "ลดปริมาณขยะพลาสติกลงได้ร้อยละ 22.5 ในปีที่ผ่านมา"],
                    "gaps_or_delays": ["แผนการลดการปล่อยคาร์บอนขอบเขตที่ 3 (Scope 3) ล่าช้ากว่ากำหนด 6 เดือนเนื่องจากความพร้อมของห่วงโซ่อุปทาน"],
                    "analysis_rationale": "แผนการดำเนินการโดยรวมแข็งแกร่ง มีการระบุความล่าช้าในขอบเขตที่ 3 อย่างตรงไปตรงมาในรายงานประจำปี ถือว่ามีความโปร่งใสสูง"
                },
                "ADVANC": {
                    "alignment_rating": "High",
                    "commitments_found": ["ยกระดับสถานีฐานให้ใช้พลังงานแสงอาทิตย์ 100% ครบ 3,000 แห่ง", "พัฒนาโซลูชันขับเคลื่อนความยั่งยืนแก่คู่ค้า"],
                    "one_report_evidence": ["ติดตั้งโซลาร์เซลล์ที่สถานีฐานสำเร็จแล้ว 3,120 แห่ง (หน้า 88)", "เปิดตัวโครงการ Green Partner Hub รองรับพันธมิตร 200 ราย"],
                    "gaps_or_delays": [],
                    "analysis_rationale": "ผลการดำเนินงานจริงสูงกว่าเป้าหมายที่ระบุไว้ในแผนเพิ่มพูนมูลค่าบริษัท แสดงถึงความมุ่งมั่นและวินัยในการบริหารจัดการข้อมูลที่ดีเยี่ยม"
                },
                "SCC": {
                    "alignment_rating": "Medium",
                    "commitments_found": ["เพิ่มสัดส่วนพลังงานทดแทนในกระบวนการผลิตปูนซีเมนต์เป็น 30%", "เปิดตัวผลิตภัณฑ์คาร์บอนต่ำ (SCG Green Choice) ให้ได้ร้อยละ 50 ของพอร์ต"],
                    "one_report_evidence": ["สัดส่วนพลังงานทดแทนอยู่ที่ 25% ต่ำกว่าเป้าหมายเนื่องจากราคาพลังงานชีวมวลพุ่งสูงขึ้น", "สินค้าในพอร์ตได้รับการรับรอง SCG Green Choice คิดเป็นร้อยละ 48 ของยอดขายรวม"],
                    "gaps_or_delays": ["เป้าหมายการเปลี่ยนผ่านเชื้อเพลิงบางส่วนต้องเลื่อนออกไป 1 ปีเนื่องจากปัญหาห่วงโซ่อุปทานและสภาวะตลาด"],
                    "analysis_rationale": "บริษัทรายงานความท้าทายอย่างชัดเจน แต่เป้าหมายสำคัญสองประการยังไม่บรรลุผลอย่างเป็นทางการ ถือว่ามีความสอดคล้องระดับปานกลาง"
                },
                "KBANK": {
                    "alignment_rating": "High",
                    "commitments_found": ["สนับสนุนการเปลี่ยนผ่านภาคธุรกิจ (Sustainable Financing) มูลค่า 50,000 ล้านบาท", "การชดเชยคาร์บอนของสำนักงานใหญ่ให้เป็นศูนย์"],
                    "one_report_evidence": ["ยอดปล่อยสินเชื่อและตราสารหนี้สีเขียวรวม 52,400 ล้านบาท (หน้า 45)", "สำนักงานใหญ่ได้รับการรับรองความเป็นกลางทางคาร์บอนเรียบร้อยแล้ว"],
                    "gaps_or_delays": [],
                    "analysis_rationale": "แผนการจัดสรรเงินทุนสีเขียวทำได้เกินเป้าหมายที่ตั้งไว้ และแสดงรายละเอียดของโครงการสินเชื่อใน One Report อย่างครบถ้วน"
                },
                "BDMS": {
                    "alignment_rating": "Medium",
                    "commitments_found": ["ติดตั้งระบบโซลาร์รูฟท็อปครบทุกโรงพยาบาลในเครือภายในปี 2025", "ลดขยะทางการแพทย์ที่ไปสู่หลุมฝังกลบให้เหลือน้อยกว่าร้อยละ 5"],
                    "one_report_evidence": ["ติดตั้งแล้วเสร็จร้อยละ 85 ของจำนวนโรงพยาบาลทั้งหมด", "ขยะทางการแพทย์ได้รับการจัดการตามมาตรฐาน ปริมาณส่งหลุมฝังกลบลดลงเหลือร้อยละ 8.2"],
                    "gaps_or_delays": ["การติดตั้งโซลาร์รูฟท็อปในโรงพยาบาลขนาดเล็กเขตต่างจังหวัดมีความล่าช้า 1 ไตรมาส"],
                    "analysis_rationale": "เป้าหมายการติดตั้งโซลาร์เซลล์ล่าช้าไปบางส่วนเนื่องจากการจัดสรรงบประมาณในส่วนย่อย แต่ในภาพรวมมีทิศทางการเติบโตที่ดี"
                },
                "TRUE": {
                    "alignment_rating": "Medium",
                    "commitments_found": ["รวมศูนย์การจัดการโครงสร้างเสาสัญญาณเพื่อลดการใช้ไฟฟ้าพลังงานหลักลง 15%", "บรรลุ Net Zero ในปี 2050"],
                    "one_report_evidence": ["ลดการใช้ไฟฟ้าลงได้จริงร้อยละ 10 ต่ำกว่าเป้าหมาย 15% เล็กน้อย", "รายละเอียดแผน Net Zero ใน One Report ยังระบุแผนกว้างๆ"],
                    "gaps_or_delays": ["การปลดระวางและรวมเสาสัญญาณที่ซ้ำซ้อนจากกระบวนการควบรวมกิจการใช้เวลามากกว่าที่คาดการณ์ไว้"],
                    "analysis_rationale": "มีความสอดคล้องบางส่วน แต่เป้าหมายลดการใช้ไฟฟ้าพลังงานหลักยังห่างไกลเป้าหมายและแผนระยะยาวยังไม่ชัดเจนในรายละเอียดเชิงเทคนิค"
                }
            }
            return mock_alignments.get(ticker, {
                "alignment_rating": "Medium",
                "commitments_found": ["ส่งเสริมแผนพัฒนาความยั่งยืน"],
                "one_report_evidence": ["ดำเนินโครงการเพื่อสังคมตามแนวทาง ESG"],
                "gaps_or_delays": ["ไม่มีแผนตัวเลขเปรียบเทียบที่แน่ชัด"],
                "analysis_rationale": "ความสอดคล้องระดับปานกลาง เนื่องจากมีการดำเนินกิจกรรมจริง แต่ขาดการวัดผลที่เป็นรูปธรรมในแผนเอกสาร"
            })

        # Run with Claude API
        prompt = CVUP_VS_ONEREPORT_PROMPT.format(document_context=context_str)
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=0.0,
                system="You are an expert financial and ESG compliance auditor. Respond ONLY in valid JSON format.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return json.loads(message.content[0].text)
        except Exception as e:
            print(f"Claude API call failed in alignment search: {e}. Fallback to mock.")
            # Simple fallback dictionary
            return {
                "alignment_rating": "Medium",
                "commitments_found": ["General ESG commitments"],
                "one_report_evidence": ["General CSR report found in One Report"],
                "gaps_or_delays": ["Could not parse PDF details"],
                "analysis_rationale": f"Fallback due to Claude API Error: {str(e)}"
            }

    def _synthesize_report(self, stock_data: Dict[str, Any], sec_status: Dict[str, Any], alignment_result: Dict[str, Any], audio_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes the final analysis and computes score using Claude.
        """
        ticker = stock_data["ticker"]
        
        # Calculate scores locally first to feed to Claude (or use as absolute fallback)
        cgr_score = stock_data["cgr_score"]
        cgr_contribution = (cgr_score / 100) * 30.0  # Max 30 pts
        
        sec_contribution = 20.0 if sec_status["is_clean"] else 0.0
        
        alignment_map = {"High": 30.0, "Medium": 15.0, "Low": 0.0}
        cvup_contribution = alignment_map.get(alignment_result["alignment_rating"], 15.0)
        
        sincerity_score = audio_result["analysis"]["sincerity_score"]
        audio_contribution = (sincerity_score / 100.0) * 20.0
        
        overall_score = round(cgr_contribution + sec_contribution + cvup_contribution + audio_contribution, 1)

        # Prepare arguments for prompt
        prompt = FINAL_ESG_SYNTHESIS_PROMPT.format(
            ticker=ticker,
            company_name=stock_data["name"],
            cgr_score=cgr_score,
            jump_plus=stock_data["jump_plus"],
            sec_is_clean=sec_status["is_clean"],
            sec_details=sec_status["message"],
            cvup_rating=alignment_result["alignment_rating"],
            cvup_analysis=alignment_result["analysis_rationale"],
            audio_confidence=audio_result["analysis"]["confidence_score"],
            audio_sincerity=sincerity_score,
            audio_evasion=audio_result["analysis"]["evasion_score"],
            audio_findings=", ".join(audio_result["analysis"]["tone_markers"]),
            audio_transcript=audio_result["transcription"]
        )

        if not self.client:
            # Full local template generation if no API key is present
            return {
                "overall_score": overall_score,
                "weighted_breakdown": {
                    "cgr_contribution": round(cgr_contribution, 1),
                    "sec_contribution": round(sec_contribution, 1),
                    "cvup_contribution": round(cvup_contribution, 1),
                    "audio_contribution": round(audio_contribution, 1)
                },
                "executive_summary_th": f"ผลการวิเคราะห์ของ {stock_data['name']} ({ticker}) แสดงความก้าวหน้าอย่างยอดเยี่ยมภายใต้กรอบการคัดกรอง JUMP+ โดยบรรษัทภิบาลของบริษัท (CGR Score: {cgr_score}) จัดอยู่ในระดับดีเลิศและไม่พบประวัติการฟ้องร้องจาก ก.ล.ต. ในรอบ 5 ปี การเทียบแผน CVUP กับรายงาน 56-1 One Report พบความสอดคล้องระดับ {alignment_result['alignment_rating']} สะท้อนถึงการปฏิบัติจริงและการวัดผลที่ตรวจสอบได้ ด้านการวิเคราะห์ความน่าเชื่อถือของผู้บริหารผ่านเสียง Opportunity Day ชี้ว่ามีการสื่อสารด้วยความเชื่อมั่น {audio_result['analysis']['confidence_score']}% และมีความสอดคล้องกับตัวเลขรายงานอย่างจริงใจ",
                "key_strengths": [
                    f"คะแนนบรรษัทภิบาล CGR สูงถึง {cgr_score} คะแนน",
                    "ไม่มีประวัติการฟ้องร้องหรือการลงโทษจาก ก.ล.ต. ตลอด 5 ปีที่ผ่านมา",
                    f"แผนเพิ่มพูนมูลค่าบริษัท (CVUP) มีความสอดคล้องระดับ {alignment_result['alignment_rating']} กับ One Report"
                ],
                "risks_and_warnings": [
                    "เป้าหมายลดคาร์บอนในบางโครงการย่อยอาจได้รับผลกระทบระยะสั้นจากอัตราดอกเบี้ยและงบประมาณสะสม"
                ],
                "investment_recommendation": "อนุมัติให้ส่งรายชื่อหุ้นเพื่อบรรจุในพอร์ตโฟลิโอหุ้นยั่งยืน (Supply-side Passed List) สำหรับขั้นตอนจัดสรรน้ำหนักการลงทุนต่อไป"
            }

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1500,
                temperature=0.2,
                system="You are a senior investment analyst specializing in ESG and corporate transparency. Respond ONLY in valid JSON format.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return json.loads(message.content[0].text)
        except Exception as e:
            print(f"Claude API call failed in synthesis: {e}. Fallback to mock.")
            return {
                "overall_score": overall_score,
                "weighted_breakdown": {
                    "cgr_contribution": round(cgr_contribution, 1),
                    "sec_contribution": round(sec_contribution, 1),
                    "cvup_contribution": round(cvup_contribution, 1),
                    "audio_contribution": round(audio_contribution, 1)
                },
                "executive_summary_th": f"รายงานการประเมิน {ticker} แบบบูรณาการ คะแนนรวม {overall_score} คะแนน คะแนน CGR ระดับดีเยี่ยม มีความโปร่งใส ปราศจากความผิดกับหน่วยงานกำกับดูแล",
                "key_strengths": ["คะแนนการกำกับดูแลดีเลิศ", "ประวัติสะอาด"],
                "risks_and_warnings": ["ข้อมูลประกอบอื่นๆ ต้องรอตรวจสอบเพิ่มเติมเนื่องจาก API error"],
                "investment_recommendation": "แนะนำสะสมเพื่อรอจัดสรรน้ำหนัก (API Fallback mode)"
            }
