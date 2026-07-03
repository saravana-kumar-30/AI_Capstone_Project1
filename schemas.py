from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ApplicantProfileData(BaseModel):
    applicant_id: str
    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., gt=0)
    employment_type: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)

class LoanApplicationData(BaseModel):
    applicant_id: str
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., gt=0)
    loan_tenure_months: int = Field(..., gt=0)
    existing_liabilities: float = Field(..., ge=0)
    applicant_profile: ApplicantProfileData
    application_timestamp: datetime = Field(default_factory=datetime.utcnow)

class IncomeStabilityScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    employment_risk: str
    credit_history_summary: str
    application_completeness: Dict[str, bool]

class FinancialRiskAnalysis(BaseModel):
    debt_to_income_ratio: float
    credit_score_risk_level: str
    loan_amount_risk: str
    anomaly_detected: bool
    reasoning: str

class LoanDecision(BaseModel):
    classification: str = Field(..., pattern="^(Approve|Reject|Review)$")
    risk_score: float = Field(..., ge=0, le=100)
    confidence_level: float = Field(..., ge=0, le=1)
    key_decision_factors: list[str]
    explanation: str

class ComplianceAction(BaseModel):
    action_taken: str
    notification_sent: bool
    case_id: str
    timestamp: datetime
    summary: str

class LoanApplicationResponse(BaseModel):
    application_id: str
    decision: str
    risk_score: float
    confidence_level: float
    key_factors: list[str]
    explanation: str
    case_id: str
    timestamp: datetime
