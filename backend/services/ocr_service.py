import base64
import json
import logging
from openai import OpenAI
from pydantic import BaseModel, Field
from backend.config import settings

logger = logging.getLogger(__name__)

class OCRResult(BaseModel):
    assessable_income: float = Field(..., description="Total assessable income (เงินได้สะสม / ยอดเงินรวมที่จ่าย)")
    withholding_tax: float = Field(..., description="Total tax withheld (ภาษีหัก ณ ที่จ่าย)")
    existing_deductions: float = Field(default=0.0, description="Other identified deductions (e.g., social security, provident fund)")
    already_purchased: float = Field(default=0.0, description="Any existing ThaiESG purchases identified on the document")
    document_type: str = Field(..., description="Detected document type")
    confidence: float = Field(..., description="Confidence score of the extraction (0.0 to 1.0)")
    is_mock: bool = Field(default=False, description="Indicates if this is a mock result")

def encode_image(image_bytes: bytes) -> str:
    """Encodes a raw bytes image into a base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")

def extract_values_from_pdf_text(pdf_bytes: bytes) -> dict:
    """Attempts to extract tax figures from a digital PDF's text layer directly, handling word wraps."""
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        
        # Clean text
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        
        # Helper function to find the first numeric value following an index (handles word-wraps)
        def find_next_number(start_idx, max_lookahead=3):
            for i in range(start_idx, min(len(lines), start_idx + max_lookahead)):
                clean_val = lines[i].replace(",", "").replace("-", "").strip()
                try:
                    return float(clean_val)
                except ValueError:
                    continue
            return None

        # Parse fields
        assessable_income = None
        withholding_tax = None
        existing_deductions = None
        already_purchased = 0.0
        
        net_income_before_esg = None
        net_income_after_esg = None
        net_income_general = None
        total_deductions = None
        
        for idx, line in enumerate(lines):
            # 1. Assessable Income (excluding net income lines)
            if ("เงินได้พึงประเมิน" in line or "เงินพึงประเมิน" in line) and "ก่อน" not in line and "หลัง" not in line:
                val = find_next_number(idx + 1)
                if val is not None:
                    assessable_income = val
            
            # 2. Withholding Tax
            if "ภาษีหัก ณ ที่จ่าย" in line or "ภาษีที่หัก ณ ที่จ่าย" in line:
                val = find_next_number(idx + 1)
                if val is not None:
                    withholding_tax = val
            
            # 3. ESG Deduction (ThaiESG)
            if "ไทยเพื่อความยั่งยืน" in line or "Thai ESG" in line or "ThaiESG" in line or "กองทุน ESG" in line:
                val = find_next_number(idx + 1)
                if val is not None:
                    already_purchased = val
            
            # 4. Basic deductions (new files)
            if "หัก ค่าใช้จ่าย / ค่าลดหย่อนพื้นฐาน" in line:
                val = find_next_number(idx + 1)
                if val is not None:
                    existing_deductions = val
            
            # 5. Total deductions (old files)
            if "รวมลดหย่อน/บริจาคทั้งสิ้น" in line:
                val = find_next_number(idx + 1)
                if val is not None:
                    total_deductions = val
            
            # 6. Net income lines for mathematical deductions retrieval
            if "เงินได้สุทธิ" in line:
                val = find_next_number(idx + 1)
                if val is not None:
                    if "ก่อน" in line:
                        net_income_before_esg = val
                    elif "หลัง" in line:
                        net_income_after_esg = val
                    else:
                        net_income_general = val
        
        # Calculate existing deductions if not directly stated
        if assessable_income is not None:
            if existing_deductions is None:
                if net_income_before_esg is not None:
                    existing_deductions = max(0.0, assessable_income - net_income_before_esg)
                elif net_income_after_esg is not None:
                    existing_deductions = max(0.0, assessable_income - net_income_after_esg - already_purchased)
                elif net_income_general is not None:
                    if already_purchased > 0.0:
                        existing_deductions = max(0.0, assessable_income - net_income_general - already_purchased)
                    else:
                        existing_deductions = max(0.0, assessable_income - net_income_general)
                elif total_deductions is not None:
                    existing_deductions = max(0.0, total_deductions - already_purchased)

            return {
                "assessable_income": assessable_income,
                "withholding_tax": withholding_tax or 0.0,
                "existing_deductions": existing_deductions or 0.0,
                "already_purchased": already_purchased
            }
    except Exception as e:
        logger.error(f"Failed to parse PDF text layer: {str(e)}")
        
    return None

def parse_50_tawi_ocr(image_bytes: bytes, filename: str = "") -> OCRResult:
    """
    Parses the 50 Tawi form image or PDF using Typhoon2-Vision.
    Falls back to mock extraction if the API key is not configured or an error occurs.
    """
    # Detect if the file is a PDF
    if image_bytes.startswith(b'%PDF'):
        logger.info("PDF document detected. Attempting to parse text layer...")
        parsed_data = extract_values_from_pdf_text(image_bytes)
        if parsed_data:
            logger.info(f"Successfully extracted data from PDF text layer: {parsed_data}")
            return OCRResult(
                assessable_income=parsed_data["assessable_income"],
                withholding_tax=parsed_data["withholding_tax"],
                existing_deductions=parsed_data["existing_deductions"],
                already_purchased=parsed_data["already_purchased"],
                document_type="PDF Tax Document (Digital Text parsed)",
                confidence=1.0,
                is_mock=False
            )
        
        logger.info("PDF text layer is empty or unparsable. Converting first page to PNG...")
        try:
            import fitz
            doc = fitz.open(stream=image_bytes, filetype="pdf")
            if len(doc) == 0:
                raise ValueError("PDF document has no pages.")
            page = doc.load_page(0)
            pix = page.get_pixmap()
            image_bytes = pix.tobytes("png")
        except Exception as e:
            logger.error(f"Error converting PDF to image: {str(e)}")
            if settings.typhoon_api_key != "mock_key" and settings.typhoon_api_key:
                raise ValueError(f"Failed to extract image from PDF: {str(e)}")

    # Check if mock mode is active
    if settings.typhoon_api_key == "mock_key" or not settings.typhoon_api_key:
        logger.info("Typhoon API key is default or empty. Returning mock OCR result.")
        return get_mock_ocr_result(filename)

    try:
        base64_image = encode_image(image_bytes)
        
        # Initialize OpenAI compatible client for Typhoon
        client = OpenAI(
            api_key=settings.typhoon_api_key,
            base_url=settings.typhoon_api_base
        )
        
        prompt = """
        You are an expert Thai document OCR extraction system.
        Analyze this image of a Thai "50 Tawi" (50 ทวิ) tax withholding certificate or personal tax breakdown document.
        Extract the following fields and return them strictly in JSON format:
        1. "assessable_income": Look for the total amount paid before tax (เงินได้สะสม / ยอดเงินรวมที่จ่าย / เงินได้พึงประเมิน). This is typically a large number, e.g., 500,000 to 2,000,000 THB.
        2. "withholding_tax": Look for the total tax withheld (ภาษีหัก ณ ที่จ่าย / รวมภาษีที่นำส่ง).
        3. "existing_deductions": Look for any pension, provident fund (กองทุนสำรองเลี้ยงชีพ), RMF, SSF, or social security (ประกันสังคม) contributions listed. If not found, return 0.
        4. "already_purchased": Look for any Thailand ESG Fund (ThaiESG / กองทุนรวมไทยเพื่อความยั่งยืน) contributions listed. If not found, return 0.
        5. "document_type": A string identifying if this is "50 Tawi" or another document.
        6. "confidence": Estimate your confidence in the numbers extracted as a float between 0.0 and 1.0.

        Response format must be valid JSON matching this schema:
        {
            "assessable_income": float,
            "withholding_tax": float,
            "existing_deductions": float,
            "already_purchased": float,
            "document_type": string,
            "confidence": float
        }
        """

        response = client.chat.completions.create(
            model=settings.typhoon_model_vision,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        
        return OCRResult(
            assessable_income=float(data.get("assessable_income", 0.0)),
            withholding_tax=float(data.get("withholding_tax", 0.0)),
            existing_deductions=float(data.get("existing_deductions", 0.0)),
            already_purchased=float(data.get("already_purchased", 0.0)),
            document_type=data.get("document_type", "50 Tawi (หนังสือรับรองการหักภาษี ณ ที่จ่าย)"),
            confidence=float(data.get("confidence", 0.9)),
            is_mock=False
        )

    except Exception as e:
        logger.error(f"Error calling Typhoon Vision API: {str(e)}. Falling back to mock result.")
        return get_mock_ocr_result(filename)

def get_mock_ocr_result(filename: str = "") -> OCRResult:
    """Returns a realistic mock result for 50 Tawi document extraction."""
    # Check for specific files mock_tax_no_esg.pdf and mock_tax_with_esg.pdf
    fn_lower = filename.lower()
    if "no_esg" in fn_lower:
        assessable_income = 1200000.0
        withholding_tax = 55000.0
        existing_deductions = 200000.0  # Sum of PVD(60k), RMF(30k), Personal(60k), Life/Health(45k), Donation(5k)
        already_purchased = 0.0
    elif "with_esg" in fn_lower:
        assessable_income = 1200000.0
        withholding_tax = 55000.0
        existing_deductions = 200000.0
        already_purchased = 100000.0
    elif "low" in fn_lower:
        assessable_income = 450000.0
        withholding_tax = 12500.0
        existing_deductions = 9000.0
        already_purchased = 0.0
    elif "high" in fn_lower:
        assessable_income = 2100000.0
        withholding_tax = 185000.0
        existing_deductions = 42000.0
        already_purchased = 0.0
    else:
        assessable_income = 1200000.0
        withholding_tax = 65000.0
        existing_deductions = 30000.0
        already_purchased = 0.0

    return OCRResult(
        assessable_income=assessable_income,
        withholding_tax=withholding_tax,
        existing_deductions=existing_deductions,
        already_purchased=already_purchased,
        document_type="50 Tawi (หนังสือรับรองการหักภาษี ณ ที่จ่าย) [MOCKED]",
        confidence=0.95,
        is_mock=True
    )
