from typing import Dict, Any, Optional, TypedDict
from datetime import datetime

from langgraph.graph import StateGraph, END

from agents import (
    ApplicantProfileAgent,
    FinancialRiskAgent,
    LoanDecisionAgent,
    ComplianceOrchestrationAgent,
)
from schemas import LoanApplicationData, LoanApplicationResponse


# ── State definition ──────────────────────────────────────────────────────────

class LoanApplicationState(TypedDict, total=False):
    """Shared state threaded through every node in the graph."""
    application: LoanApplicationData

    # outputs written by each node
    applicant_profile: Dict[str, Any]
    financial_risk: Dict[str, Any]
    decision: Dict[str, Any]
    compliance: Dict[str, Any]

    # set by any node that encounters a hard failure
    error: Optional[str]


# ── Node functions ─────────────────────────────────────────────────────────────

_applicant_agent = ApplicantProfileAgent()
_risk_agent = FinancialRiskAgent()
_decision_agent = LoanDecisionAgent()
_compliance_agent = ComplianceOrchestrationAgent()


async def node_applicant_profile(state: LoanApplicationState) -> LoanApplicationState:
    application = state["application"]
    profile_data = {
        "applicant_id": application.applicant_id,
        "age": application.applicant_profile.age,
        "income": application.applicant_profile.income,
        "employment_type": application.applicant_profile.employment_type,
        "location": application.applicant_profile.location,
    }
    result = await _applicant_agent.analyze(profile_data)
    if "error" in result:
        return {**state, "error": result["error"]}
    return {**state, "applicant_profile": result}


async def node_financial_risk(state: LoanApplicationState) -> LoanApplicationState:
    application = state["application"]
    profile = state["applicant_profile"]
    data = {
        "applicant_id": application.applicant_id,
        "credit_score": application.credit_score,
        "loan_amount": application.loan_amount,
        "existing_liabilities": application.existing_liabilities,
        "income": profile.get("income", application.applicant_profile.income),
        "loan_tenure_months": application.loan_tenure_months,
    }
    result = await _risk_agent.analyze(data)
    if "error" in result:
        return {**state, "error": result["error"]}
    return {**state, "financial_risk": result}


async def node_loan_decision(state: LoanApplicationState) -> LoanApplicationState:
    application = state["application"]
    profile = state["applicant_profile"]
    risk = state["financial_risk"]
    data = {
        "applicant_id": application.applicant_id,
        "income_stability_score": profile.get("income_stability_score", 70),
        "employment_risk": profile.get("employment_risk", "Low"),
        "debt_to_income_ratio": risk.get("debt_to_income_ratio", 0),
        "credit_score": application.credit_score,
        "credit_score_risk_level": risk.get("credit_score_risk_level", "Low"),
        "loan_amount_risk": risk.get("loan_amount_risk", "Low"),
        "loan_amount": application.loan_amount,
        "income": profile.get("income", application.applicant_profile.income),
    }
    result = await _decision_agent.synthesize(data)
    if "error" in result:
        return {**state, "error": result["error"]}
    return {**state, "decision": result}


async def node_compliance(state: LoanApplicationState) -> LoanApplicationState:
    application = state["application"]
    decision = state["decision"]
    data = {
        "applicant_id": application.applicant_id,
        "decision": decision.get("classification", "Review"),
        "risk_score": decision.get("risk_score", 50),
        "explanation": decision.get("explanation", ""),
    }
    result = await _compliance_agent.execute(data)
    # compliance failure is non-fatal — record result regardless
    return {**state, "compliance": result}


# ── Conditional routing ────────────────────────────────────────────────────────

def _route_after_profile(state: LoanApplicationState) -> str:
    return "error" if state.get("error") else "financial_risk"


def _route_after_risk(state: LoanApplicationState) -> str:
    return "error" if state.get("error") else "loan_decision"


def _route_after_decision(state: LoanApplicationState) -> str:
    return "error" if state.get("error") else "compliance"


# ── Graph construction ─────────────────────────────────────────────────────────

def _build_graph() -> Any:
    graph = StateGraph(LoanApplicationState)

    graph.add_node("applicant_profile", node_applicant_profile)
    graph.add_node("financial_risk", node_financial_risk)
    graph.add_node("loan_decision", node_loan_decision)
    graph.add_node("compliance", node_compliance)

    graph.set_entry_point("applicant_profile")

    graph.add_conditional_edges(
        "applicant_profile",
        _route_after_profile,
        {"financial_risk": "financial_risk", "error": END},
    )
    graph.add_conditional_edges(
        "financial_risk",
        _route_after_risk,
        {"loan_decision": "loan_decision", "error": END},
    )
    graph.add_conditional_edges(
        "loan_decision",
        _route_after_decision,
        {"compliance": "compliance", "error": END},
    )
    graph.add_edge("compliance", END)

    return graph.compile()


_compiled_graph = _build_graph()


# ── Public orchestrator ────────────────────────────────────────────────────────

class LoanProcessingOrchestrator:
    """Thin wrapper that runs the compiled LangGraph and maps state → response."""

    async def process_application(
        self, application: LoanApplicationData
    ) -> LoanApplicationResponse:
        initial_state: LoanApplicationState = {"application": application, "error": None}

        final_state: LoanApplicationState = await _compiled_graph.ainvoke(initial_state)

        if final_state.get("error"):
            return self._error_response(application, final_state["error"])

        decision = final_state.get("decision", {})
        compliance = final_state.get("compliance", {})

        return LoanApplicationResponse(
            application_id=application.applicant_id,
            decision=decision.get("classification", "Review"),
            risk_score=decision.get("risk_score", 50),
            confidence_level=decision.get("confidence_level", 0.5),
            key_factors=decision.get("key_decision_factors", []),
            explanation=decision.get("explanation", ""),
            case_id=compliance.get("case_id", "UNKNOWN"),
            timestamp=datetime.utcnow(),
        )

    @staticmethod
    def _error_response(
        application: LoanApplicationData, error: str
    ) -> LoanApplicationResponse:
        return LoanApplicationResponse(
            application_id=application.applicant_id,
            decision="Review",
            risk_score=50,
            confidence_level=0.0,
            key_factors=["Processing error"],
            explanation=f"Error during processing: {error}",
            case_id="ERROR",
            timestamp=datetime.utcnow(),
        )
