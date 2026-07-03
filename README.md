# 🏦 Multi-Agent Agentic AI Loan Approval System

A comprehensive, microservices-based automated loan approval system using multi-agent AI orchestration.

## 📋 Overview

This system automates loan application analysis using a distributed multi-agent architecture where specialized agents collaborate through an orchestration layer to make informed loan approval decisions. The system achieves:

- **Speed**: Most applications processed within seconds
- **Consistency**: Rule-based decision framework with explainability
- **Scalability**: Loosely coupled microservices architecture
- **Auditability**: Complete decision tracing and case documentation

## 🏗️ System Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Chatbot UI                    │
├─────────────────────────────────────────────────────────┤
│              FastAPI Microservice Layer                  │
├─────────────────────────────────────────────────────────┤
│           LangGraph Orchestration Engine                 │
├─────────────────────────────────────────────────────────┤
│                  Agent Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Applicant │  │Financial │  │  Loan    │  │Compliance│ │
│  │ Profile  │  │   Risk   │  │Decision  │  │ & Action │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
├─────────────────────────────────────────────────────────┤
│                  MCP Servers Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Applicant │  │RiskRules │  │Decision  │  │Notific.  │ │
│  │   DB     │  │   DB     │  │Synthesis │  │ System   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Service Architecture

| Service | Port | Purpose |
|---------|------|---------|
| Streamlit UI | 8501 | User interface |
| FastAPI | 8000 | Main API gateway |
| ApplicantDB MCP | 8001 | Applicant profile data |
| RiskRulesDB MCP | 8002 | Financial risk analysis |
| DecisionSynthesis MCP | 8003 | Loan decision logic |
| NotificationSystem MCP | 8004 | Notification & compliance |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- ANTHROPIC_API_KEY environment variable

### Installation

```bash
cd /path/to/Project1

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the System

#### Option 1: Automated Start (Recommended)

```bash
chmod +x run_all_services.sh
./run_all_services.sh
```

#### Option 2: Manual Start (Debug Mode)

**Terminal 1 - MCP Servers:**
```bash
# Terminal 1.1
python mcp_applicant_db.py

# Terminal 1.2 (new terminal)
python mcp_risk_rules.py

# Terminal 1.3 (new terminal)
python mcp_decision_synthesis.py

# Terminal 1.4 (new terminal)
python mcp_notification.py
```

**Terminal 2 - FastAPI Service:**
```bash
python main.py
# API will be available at http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

**Terminal 3 - Streamlit UI:**
```bash
streamlit run streamlit_app.py
# UI will be available at http://localhost:8501
```

### Testing

```bash
python test_api.py
```

This runs three test cases:
1. Strong applicant with high income and excellent credit
2. Risky applicant with low credit score
3. Moderate applicant with balanced profile

## 📊 Workflow Overview

### Application Processing Flow

```
1. User submits loan application via Streamlit UI
   ↓
2. FastAPI validates and receives application data
   ↓
3. Orchestration engine starts processing
   ↓
4. Applicant Profile Agent
   - Queries ApplicantDB MCP server
   - Retrieves income stability, employment history, credit history
   ↓
5. Financial Risk Agent
   - Queries RiskRulesDB MCP server
   - Calculates DTI ratio, credit risk level, loan risk
   - Detects anomalies
   ↓
6. Loan Decision Agent
   - Queries DecisionSynthesis MCP server
   - Synthesizes decision based on all factors
   - Calculates risk score and confidence level
   ↓
7. Compliance & Action Orchestrator Agent
   - Queries NotificationSystem MCP server
   - Generates case ID and sends notifications
   ↓
8. Results returned to UI and displayed to user
```

## 🤖 Agent Responsibilities

### 1. Applicant Profile Agent
**MCP Server**: ApplicantDB (Port 8001)

**Analyzes:**
- Income stability and employment history
- Credit history and previous default records
- Application completeness
- Employment risk assessment

**Output:**
- Income Stability Score (0-100)
- Employment Risk Level (Low/High)
- Credit History Summary
- Completeness Flags

### 2. Financial Risk Analysis Agent
**MCP Server**: RiskRulesDB (Port 8002)

**Analyzes:**
- Debt-to-Income (DTI) Ratio
- Credit score risk classification
- Loan-to-income assessment
- Anomaly detection

**Output:**
- DTI Ratio
- Credit Score Risk Level (Low/Medium/High/Very High)
- Loan Amount Risk (Low/Medium/High)
- Anomaly Indicators
- Risk Reasoning

### 3. Loan Decision Agent
**MCP Server**: DecisionSynthesis (Port 8003)

**Synthesizes:**
- All risk factors
- Historical patterns
- Regulatory thresholds
- Final decision logic

**Output:**
- Classification (Approve/Reject/Review)
- Risk Score (0-100)
- Confidence Level (0-1)
- Key Decision Factors
- Decision Explanation

### 4. Compliance & Action Orchestrator Agent
**MCP Server**: NotificationSystem (Port 8004)

**Executes:**
- Decision notifications
- Case logging
- Audit trail generation
- Action routing

**Output:**
- Action Taken
- Notification Status
- Case ID
- Timestamp
- Summary

## 📈 Decision Logic

### Risk Score Calculation

```
Base Score = 0

If Credit Score < 650:      +30 points
If Credit Score < 700:      +15 points
If DTI > 0.5:              +25 points
If DTI > 0.4:              +10 points
If Employment Risk = High:  +20 points
If Loan Amount Risk = High: +20 points
If Income Stability < 50:   +15 points

Final Score = Min(Total, 100)
```

### Classification Thresholds

```
Risk Score > 70     → REJECT
Risk Score 45-70    → REVIEW (Manual review required)
Risk Score < 45     → APPROVE
```

### Confidence Levels

```
APPROVE:  90% (if Risk < 30%) → 75% (if Risk 30-45%)
REJECT:   95% (if Risk > 70%)
REVIEW:   70% (Mixed indicators)
```

## 🔌 API Endpoints

### Main Application Endpoint

**Submit Loan Application**
```
POST /api/submit-loan-application

Request Body:
{
  "applicant_id": "APP001",
  "credit_score": 750,
  "loan_amount": 200000,
  "loan_tenure_months": 60,
  "existing_liabilities": 50000,
  "applicant_profile": {
    "applicant_id": "APP001",
    "age": 35,
    "income": 150000,
    "employment_type": "Full-time",
    "location": "New York"
  },
  "application_timestamp": "2024-07-01T10:30:00"
}

Response:
{
  "application_id": "APP001",
  "decision": "Approve",
  "risk_score": 25.5,
  "confidence_level": 0.92,
  "key_factors": [
    "Strong credit history",
    "Excellent income stability"
  ],
  "explanation": "Decision based on...",
  "case_id": "CASE-A1B2C3D4",
  "timestamp": "2024-07-01T10:30:05"
}
```

### Health Check

```
GET /api/health

Response:
{
  "status": "healthy",
  "service": "Loan Approval API",
  "version": "1.0.0"
}
```

### MCP Server Health Checks

Each MCP server has its own health endpoint:
```
GET http://localhost:800X/health
```

## 📁 Project Structure

```
Project1/
├── main.py                          # FastAPI application entry point
├── streamlit_app.py                 # Streamlit UI
├── config.py                        # Configuration management
├── schemas.py                       # Pydantic data models
├── orchestration.py                 # Orchestration engine
├── agents.py                        # Agent implementations
├── mcp_applicant_db.py             # Applicant Database MCP server
├── mcp_risk_rules.py               # Risk Rules MCP server
├── mcp_decision_synthesis.py       # Decision Synthesis MCP server
├── mcp_notification.py             # Notification System MCP server
├── test_api.py                     # API test suite
├── run_all_services.sh             # Service startup script
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## 🧪 Testing

### Run Test Suite

```bash
python test_api.py
```

### Manual Testing via Swagger UI

1. Start all services
2. Visit http://localhost:8000/docs
3. Try out the `/api/submit-loan-application` endpoint

### Test Data

Pre-configured test applicants:
- **APP001**: John Doe - Strong profile
- **APP002**: Jane Smith - Moderate profile with self-employment
- **APP003**: Bob Johnson - Risky profile with defaults

## 🔧 Configuration

Edit `config.py` to adjust:

```python
DTI_THRESHOLD = 0.5              # Debt-to-income ratio threshold
CREDIT_SCORE_THRESHOLD = 650     # Minimum credit score
MIN_INCOME = 20000               # Minimum income
MAX_LOAN_AMOUNT = 500000         # Maximum loan amount
MODEL_NAME = "claude-sonnet-4-20250514"  # LLM model
```

## 📝 Decision Audit Trail

Each application includes:
- **Case ID**: Unique identifier for tracking
- **Timestamp**: When decision was made
- **Risk Factors**: All factors considered
- **Confidence Level**: Model's confidence in decision
- **Explanation**: Reasoning for decision

All data is logged in the NotificationSystem for compliance.

## 🚨 Troubleshooting

### Services Won't Start

**Issue**: Connection refused
```bash
# Check if ports are in use
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003
lsof -i :8004

# Kill processes if needed
kill -9 <PID>
```

### API Returns Connection Errors

**Issue**: MCP servers not responding
```bash
# Test individual MCP servers
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

### Streamlit Can't Connect to API

**Issue**: Localhost connection issues
```bash
# Check FastAPI is running
curl http://localhost:8000/api/health

# Verify in streamlit_app.py that API_BASE_URL is correct
```

### Missing Dependencies

```bash
pip install --upgrade -r requirements.txt
```

## 📚 Architecture Patterns

### Microservices Pattern
- Each MCP server is independent and can be scaled separately
- Loose coupling via HTTP REST APIs
- Easy to add new agents or modify existing ones

### Orchestration Pattern
- Central orchestration engine coordinates agent workflows
- Clear state management
- Easy to modify decision logic

### MCP Pattern
- Standardized communication protocol
- Data isolation and access control
- Easy to swap implementations

## 🔐 Security Considerations

1. **API Key Management**: Store ANTHROPIC_API_KEY in environment variables
2. **CORS**: Currently allows all origins (configure for production)
3. **Rate Limiting**: Add for production deployment
4. **Authentication**: Implement API key-based auth for production
5. **Logging**: All decisions are logged for audit trails

## 📈 Scalability

### Horizontal Scaling
- Deploy multiple instances of FastAPI behind a load balancer
- Each MCP server can run on separate machines

### Vertical Scaling
- Increase model capacity for LLM calls
- Optimize database queries in MCP servers
- Add caching layer for frequent queries

## 🤝 Integration Points

### To Add a New Agent
1. Create a new MCP server file (e.g., `mcp_new_agent.py`)
2. Add corresponding Agent class to `agents.py`
3. Integrate into orchestration pipeline in `orchestration.py`

### To Add New Data Source
1. Create MCP server for data access
2. Add query method to corresponding agent
3. Update decision logic in orchestration

### To Modify Decision Logic
1. Edit risk calculation in `mcp_decision_synthesis.py`
2. Adjust thresholds in `config.py`
3. Update reasoning in response

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs in terminal output
3. Test individual services with health endpoints
4. Verify configuration in `.env`

## 📄 License

This is a demonstration system for educational purposes.

## 🚀 Next Steps

1. **Production Deployment**: Deploy with Docker/Kubernetes
2. **Database Integration**: Replace in-memory data with persistent DB
3. **Advanced Analytics**: Add historical analysis and reporting
4. **ML Model Integration**: Integrate ML models for risk scoring
5. **Real-time Notifications**: Add email/SMS notification service
6. **Compliance Reporting**: Add regulatory compliance reporting
