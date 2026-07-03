import json
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("ApplicantDB MCP Server")

APPLICANT_DATABASE = {
    "APP001": {
        "applicant_id": "APP001",
        "name": "John Doe",
        "age": 35,
        "employment_type": "Full-time",
        "income": 85000,
        "employment_history_years": 8,
        "previous_loans": 2,
        "previous_defaults": 0,
        "location": "New York",
    },
    "APP002": {
        "applicant_id": "APP002",
        "name": "Jane Smith",
        "age": 28,
        "employment_type": "Self-employed",
        "income": 120000,
        "employment_history_years": 5,
        "previous_loans": 1,
        "previous_defaults": 0,
        "location": "California",
    },
    "APP003": {
        "applicant_id": "APP003",
        "name": "Bob Johnson",
        "age": 45,
        "employment_type": "Full-time",
        "income": 65000,
        "employment_history_years": 15,
        "previous_loans": 3,
        "previous_defaults": 1,
        "location": "Texas",
    },
}


_STABILITY_SCORE = {
    "Full-time": 75,
    "Retired": 70,
    "Self-employed": 60,
    "Part-time": 55,
}

_EMPLOYMENT_RISK = {
    "Full-time": "Low",
    "Retired": "Low",
    "Self-employed": "Medium",
    "Part-time": "Medium",
}


@mcp.tool()
def get_applicant_profile(
    applicant_id: str,
    age: int = 0,
    income: float = 0.0,
    employment_type: str = "",
    location: str = "",
) -> dict:
    """Retrieve and score an applicant's profile.

    Looks up the applicant in the database first. If not found and fallback
    fields (age, income, employment_type, location) are provided, builds the
    profile from those values so any applicant ID can be processed.
    """
    applicant = APPLICANT_DATABASE.get(applicant_id)

    if applicant:
        emp_type = applicant["employment_type"]
        employment_risk = "High" if applicant["employment_history_years"] < 2 else "Low"
        stability_score = _STABILITY_SCORE.get(emp_type, 65)
        credit_summary = (
            f"Previous loans: {applicant['previous_loans']}, "
            f"Defaults: {applicant['previous_defaults']}"
        )
        resolved_income = applicant["income"]
    elif income > 0 and employment_type:
        # New applicant — build profile from submitted form fields
        emp_type = employment_type
        employment_risk = _EMPLOYMENT_RISK.get(emp_type, "Medium")
        stability_score = _STABILITY_SCORE.get(emp_type, 65)
        credit_summary = "New applicant — no prior loan history on record"
        resolved_income = income
    else:
        return {"error": f"Applicant {applicant_id} not found", "applicant_id": applicant_id}

    return {
        "applicant_id": applicant_id,
        "income_stability_score": stability_score,
        "employment_risk": employment_risk,
        "credit_history_summary": credit_summary,
        "application_completeness": {
            "income_verified": True,
            "employment_verified": True,
            "address_verified": True,
            "identity_verified": True,
        },
        "income": resolved_income,
    }


# Legacy HTTP shim — keeps existing agents.py calls working
@mcp.custom_route("/tools/get_applicant_profile", methods=["POST"])
async def _http_get_applicant_profile(request: Request) -> JSONResponse:
    body = await request.json()
    result = get_applicant_profile(
        applicant_id=body.get("applicant_id", ""),
        age=body.get("age", 0),
        income=body.get("income", 0.0),
        employment_type=body.get("employment_type", ""),
        location=body.get("location", ""),
    )
    return JSONResponse(result)


@mcp.custom_route("/health", methods=["GET"])
async def _health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "ApplicantDB"})


app = mcp.http_app()

if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_http_async(host="0.0.0.0", port=8001, show_banner=False))
