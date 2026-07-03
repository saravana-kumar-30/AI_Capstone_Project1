from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from schemas import LoanApplicationData, LoanApplicationResponse
from orchestration import LoanProcessingOrchestrator
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Loan Approval AI System",
    description="Multi-Agent AI system for automated loan application processing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = LoanProcessingOrchestrator()

@app.post("/api/submit-loan-application", response_model=LoanApplicationResponse)
async def submit_loan_application(application: LoanApplicationData):
    try:
        logger.info(f"Processing loan application for {application.applicant_id}")
        result = await orchestrator.process_application(application)
        logger.info(f"Application processed: {result.application_id} - Decision: {result.decision}")
        return result
    except Exception as e:
        logger.error(f"Error processing application: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "Loan Approval API",
        "version": "1.0.0",
    }

@app.get("/api/application/{application_id}")
async def get_application_status(application_id: str):
    return {
        "application_id": application_id,
        "status": "Processing",
        "message": "Check back soon for updates",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Config.FASTAPI_HOST,
        port=Config.FASTAPI_PORT,
        reload=False,
    )
