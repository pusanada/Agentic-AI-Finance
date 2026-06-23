from pydantic import BaseModel, Field

class TaxCalculatorRequest(BaseModel):
    assessable_income: float = Field(..., ge=0, description="Total assessable income (เงินได้พึงประเมิน)")
    already_purchased: float = Field(default=0.0, ge=0, description="Amount already invested in ThaiESG this year")

class TaxCalculatorResponse(BaseModel):
    assessable_income: float
    already_purchased: float
    max_quota: float
    remaining_quota: float
    holding_period_years: int = 5
    percentage_limit: float = 0.30
    cap_limit: float = 300000.0

def calculate_thaiesg_quota(request: TaxCalculatorRequest) -> TaxCalculatorResponse:
    """
    Calculates the ThaiESG tax deduction quota for Tax Year 2569.
    Rules:
    - Maximum 30% of assessable income.
    - Capped at 300,000 THB.
    - Holding period is 5 years.
    """
    assessable_income = request.assessable_income
    already_purchased = request.already_purchased
    
    # Calculate raw limit (30% of assessable income)
    raw_limit = assessable_income * 0.30
    
    # Cap limit at 300,000 THB
    max_quota = min(raw_limit, 300000.0)
    
    # Calculate remaining quota
    remaining_quota = max(0.0, max_quota - already_purchased)
    
    return TaxCalculatorResponse(
        assessable_income=assessable_income,
        already_purchased=already_purchased,
        max_quota=max_quota,
        remaining_quota=remaining_quota
    )
