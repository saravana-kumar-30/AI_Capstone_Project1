from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("RiskRulesDB MCP Server")


def calculate_dti_ratio(loan_amount: float, tenure_months: int, income: float, existing_liabilities: float = 0) -> float:
    monthly_income = income / 12
    monthly_payment = loan_amount / tenure_months
    dti = (monthly_payment + existing_liabilities / 12) / monthly_income if monthly_income > 0 else 1.0
    return min(dti, 1.0)


def get_credit_risk_level(credit_score: int) -> str:
    if credit_score >= 750:
        return "Low"
    elif credit_score >= 700:
        return "Medium"
    elif credit_score >= 650:
        return "High"
    else:
        return "Very High"


def get_loan_amount_risk(loan_amount: float, income: float) -> str:
    loan_to_income = loan_amount / income if income > 0 else float("inf")
    if loan_to_income <= 2:
        return "Low"
    elif loan_to_income <= 5:
        return "Medium"
    else:
        return "High"


@mcp.tool()
def analyze_financial_risk(
    applicant_id: str,
    credit_score: int,
    loan_amount: float,
    existing_liabilities: float,
    income: float,
    loan_tenure_months: int,
) -> dict:
    """Compute DTI ratio, credit risk level, loan amount risk, and anomaly flags."""
    dti_ratio = calculate_dti_ratio(loan_amount, loan_tenure_months, income, existing_liabilities)
    credit_risk = get_credit_risk_level(credit_score)
    loan_risk = get_loan_amount_risk(loan_amount, income)

    anomaly_detected = dti_ratio > 0.5 or credit_score < 650 or loan_amount > income * 5

    reasoning = []
    if dti_ratio > 0.5:
        reasoning.append(f"High DTI ratio ({dti_ratio:.2f})")
    if credit_score < 650:
        reasoning.append(f"Low credit score ({credit_score})")
    if loan_amount > income * 5:
        reasoning.append("Loan-to-income ratio exceeds 5x")

    return {
        "applicant_id": applicant_id,
        "debt_to_income_ratio": dti_ratio,
        "credit_score_risk_level": credit_risk,
        "loan_amount_risk": loan_risk,
        "anomaly_detected": anomaly_detected,
        "reasoning": "; ".join(reasoning) if reasoning else "No major anomalies detected",
    }


# Legacy HTTP shim
@mcp.custom_route("/tools/analyze_financial_risk", methods=["POST"])
async def _http_analyze_financial_risk(request: Request) -> JSONResponse:
    body = await request.json()
    result = analyze_financial_risk(
        applicant_id=body.get("applicant_id", ""),
        credit_score=body.get("credit_score", 0),
        loan_amount=body.get("loan_amount", 0.0),
        existing_liabilities=body.get("existing_liabilities", 0.0),
        income=body.get("income", 1.0),
        loan_tenure_months=body.get("loan_tenure_months", 1),
    )
    return JSONResponse(result)


@mcp.custom_route("/health", methods=["GET"])
async def _health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "RiskRulesDB"})


app = mcp.http_app()

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_http_async(host="0.0.0.0", port=8002, show_banner=False))
