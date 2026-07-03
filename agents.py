import httpx
from typing import Dict, Any
from config import Config

class ApplicantProfileAgent:
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 8001):
        self.base_url = f"http://{mcp_host}:{mcp_port}"

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        applicant_id = data.get("applicant_id", "")
        try:
            async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/tools/get_applicant_profile",
                    json=data,
                )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "applicant_id": applicant_id}

class FinancialRiskAgent:
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 8002):
        self.base_url = f"http://{mcp_host}:{mcp_port}"

    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/tools/analyze_financial_risk",
                    json=data,
                )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "applicant_id": data.get("applicant_id")}

class LoanDecisionAgent:
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 8003):
        self.base_url = f"http://{mcp_host}:{mcp_port}"

    async def synthesize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/tools/synthesize_decision",
                    json=data,
                )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "applicant_id": data.get("applicant_id")}

class ComplianceOrchestrationAgent:
    def __init__(self, mcp_host: str = "localhost", mcp_port: int = 8004):
        self.base_url = f"http://{mcp_host}:{mcp_port}"

    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
                response = await client.post(
                    f"{self.base_url}/tools/send_notification",
                    json=data,
                )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "applicant_id": data.get("applicant_id")}
