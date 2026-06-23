import pytest
from backend.services.ocr_service import parse_50_tawi_ocr

def test_ocr_image_mock():
    # Pass arbitrary bytes (representing an image)
    image_bytes = b"fake-image-bytes"
    res = parse_50_tawi_ocr(image_bytes, filename="my_document.png")
    
    assert res.assessable_income == 1200000.0
    assert res.withholding_tax == 65000.0
    assert res.existing_deductions == 30000.0
    assert res.is_mock is True

def test_ocr_pdf_mock_detection():
    # Pass bytes starting with PDF magic bytes
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n..."
    res = parse_50_tawi_ocr(pdf_bytes, filename="test_document_low.pdf")
    
    # Since filename has "low", it should return low mock values
    assert res.assessable_income == 450000.0
    assert res.withholding_tax == 12500.0
    assert res.existing_deductions == 9000.0
    assert res.is_mock is True

def test_ocr_pdf_mock_high():
    pdf_bytes = b"%PDF-1.5\n..."
    res = parse_50_tawi_ocr(pdf_bytes, filename="document_high.pdf")
    
    # Since filename has "high", it should return high mock values
    assert res.assessable_income == 2100000.0
    assert res.withholding_tax == 185000.0
    assert res.existing_deductions == 42000.0
    assert res.is_mock is True

def test_ocr_pdf_no_esg():
    pdf_bytes = b"%PDF-1.4\n..."
    res = parse_50_tawi_ocr(pdf_bytes, filename="mock_tax_no_esg.pdf")
    assert res.assessable_income == 1200000.0
    assert res.withholding_tax == 55000.0
    assert res.existing_deductions == 200000.0
    assert res.already_purchased == 0.0

def test_ocr_pdf_with_esg():
    pdf_bytes = b"%PDF-1.4\n..."
    res = parse_50_tawi_ocr(pdf_bytes, filename="mock_tax_with_esg.pdf")
    assert res.assessable_income == 1200000.0
    assert res.withholding_tax == 55000.0
    assert res.existing_deductions == 200000.0
    assert res.already_purchased == 100000.0

def test_all_test_pdf_folder():
    import os
    test_dir = r"e:\AI-Finance\.test_pdf"
    if not os.path.exists(test_dir):
        pytest.skip(".test_pdf directory not found")
        
    for filename in os.listdir(test_dir):
        if not filename.endswith(".pdf"):
            continue
            
        filepath = os.path.join(test_dir, filename)
        with open(filepath, "rb") as f:
            pdf_bytes = f.read()
            
        res = parse_50_tawi_ocr(pdf_bytes, filename=filename)
        
        # Determine expected values based on filename logic (e.g., quota200000_withESG_4.pdf)
        import re
        match = re.search(r"quota(\d+)_(noESG|withESG)_(\d+)", filename)
        assert match is not None, f"Filename {filename} did not match expected pattern"
        
        expected_quota = float(match.group(1))
        
        # Calculate actual quota using calculator
        from backend.services.tax_calculator import calculate_thaiesg_quota, TaxCalculatorRequest
        calc_req = TaxCalculatorRequest(assessable_income=res.assessable_income, already_purchased=res.already_purchased)
        calc_res = calculate_thaiesg_quota(calc_req)
        
        assert abs(calc_res.remaining_quota - expected_quota) < 1.0, f"Mismatched quota for {filename}: expected {expected_quota}, got {calc_res.remaining_quota}"
