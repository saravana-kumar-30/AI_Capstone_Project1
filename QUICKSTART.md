# Quick Start Guide - 5 Minutes to Loan Approval AI

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- ~2 minutes of installation time

## Step 1: Clone/Navigate to Project

```bash
cd /home/ubuntu/Desktop/Project1
```

## Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

This isolates the project dependencies and avoids "externally managed environment" errors.

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected time:** 2-3 minutes
**Note:** All installations now happen in the virtual environment

## Step 4: Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY if needed
```

## Step 5: Start All Services (Easiest Way)

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Make the startup script executable
chmod +x run_all_services.sh

# Run it
./run_all_services.sh
```

This starts:
- ✅ ApplicantDB MCP Server (Port 8001)
- ✅ RiskRulesDB MCP Server (Port 8002)  
- ✅ DecisionSynthesis MCP Server (Port 8003)
- ✅ NotificationSystem MCP Server (Port 8004)
- ✅ FastAPI Service (Port 8000)
- ✅ Streamlit UI (Port 8501)

**Wait for:** All services to start successfully

## Step 5: Access the System

### 🎨 User Interface (Recommended)
Open your browser and go to:
```
http://localhost:8501
```

### 🔧 API Testing
Open Swagger UI at:
```
http://localhost:8000/docs
```

### 🧪 Automated Tests
In a new terminal (while services are running):
```bash
python test_api.py
```

## Using the Streamlit UI

### Submitting an Application

1. **Go to "New Application" tab**
2. **Fill in Applicant Information:**
   - Applicant ID: `APP001` (or try `APP002`, `APP003`)
   - Age: Between 18-100
   - Income: Annual income in dollars
   - Employment Type: Full-time, Self-employed, etc.
   - Location: City/State

3. **Fill in Loan Details:**
   - Credit Score: 300-850
   - Loan Amount: Requested amount
   - Loan Tenure: In months (12-360)
   - Existing Liabilities: Current debt

4. **Click "Submit Application"**

5. **View Results:**
   - Decision: Approve, Reject, or Review
   - Risk Score: 0-100
   - Confidence Level: Percentage
   - Key Decision Factors
   - Detailed Explanation

### Viewing Results
- Click "Results" tab to see detailed analysis
- Download results as JSON
- Submit another application

## Test Cases to Try

### Test 1: Strong Applicant (Should Approve ✅)
- Applicant ID: `APP001`
- Age: 35
- Income: $150,000
- Credit Score: 800
- Loan Amount: $200,000
- Tenure: 60 months
- Existing Liabilities: $50,000

### Test 2: Risky Applicant (Should Reject ❌)
- Applicant ID: `APP003`
- Age: 45
- Income: $65,000
- Credit Score: 580
- Loan Amount: $150,000
- Tenure: 60 months
- Existing Liabilities: $80,000

### Test 3: Moderate Applicant (Should Review 🔄)
- Applicant ID: `APP002`
- Age: 28
- Income: $85,000
- Credit Score: 700
- Loan Amount: $120,000
- Tenure: 48 months
- Existing Liabilities: $35,000

## Understanding the Results

### Decision Types

**🟢 APPROVE**
- Low risk profile
- Good credit and income
- Manageable debt levels
- Ready for funding

**🔴 REJECT**
- High risk indicators
- Low credit score
- High debt-to-income ratio
- Cannot approve with current profile

**🟡 REVIEW**
- Mixed indicators
- Moderate risk
- Requires manual review
- May provide additional documentation

### Risk Score Interpretation

```
0-30:    Low Risk     ✅ Good to approve
30-45:   Moderate    ⚠️ Acceptable with conditions
45-70:   High Risk   🔄 Requires manual review
70-100:  Very High   ❌ Likely rejection
```

### Key Decision Factors

Common factors you'll see:
- **Low/High credit score** - Payment history indicator
- **High DTI ratio** - Too much existing debt relative to income
- **Employment risk** - Job stability concerns
- **High loan amount** - Loan-to-income ratio too high
- **Income stability issues** - Inconsistent or unstable income

## API Usage (For Developers)

### Direct API Call Example

```bash
curl -X POST http://localhost:8000/api/submit-loan-application \
  -H "Content-Type: application/json" \
  -d '{
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
    }
  }'
```

### Expected Response

```json
{
  "application_id": "APP001",
  "decision": "Approve",
  "risk_score": 25.5,
  "confidence_level": 0.92,
  "key_factors": [
    "Strong credit history",
    "Excellent income stability"
  ],
  "explanation": "Application approved based on...",
  "case_id": "CASE-A1B2C3D4",
  "timestamp": "2024-07-01T10:30:05.123456"
}
```

## Stopping the Services

### Press Ctrl+C in the terminal

The script will gracefully shut down all services:
```
^C
Stopping services...
✓ All services stopped
```

## Troubleshooting

### Problem: "Connection refused"
**Solution:** Wait 10 seconds after starting services - they need time to initialize

### Problem: Port already in use
**Solution:** 
```bash
# Find what's using the port
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Problem: "Module not found" error
**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### Problem: Streamlit shows "API unavailable"
**Solution:** Check that FastAPI is running
```bash
curl http://localhost:8000/api/health
```

### Problem: Services won't start
**Solution:** Check Python version
```bash
python --version  # Should be 3.8+
```

## Next Steps

1. **Explore the System:**
   - Try different applicant profiles
   - Review decision explanations
   - Check case IDs in audit trail

2. **Read the Documentation:**
   - [Full Architecture Guide](ARCHITECTURE.md)
   - [Complete README](README.md)
   - [API Documentation](http://localhost:8000/docs)

3. **Customize for Your Use Case:**
   - Edit decision logic in `mcp_decision_synthesis.py`
   - Adjust thresholds in `config.py`
   - Add new data sources as MCP servers

4. **Deploy to Production:**
   - See [ARCHITECTURE.md](ARCHITECTURE.md) for deployment guidelines
   - Docker support included
   - Kubernetes ready

## Service Endpoints Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Streamlit UI | http://localhost:8501 | User interface |
| FastAPI | http://localhost:8000 | Main API |
| Swagger Docs | http://localhost:8000/docs | API documentation |
| ApplicantDB | http://localhost:8001 | Profile data |
| RiskRulesDB | http://localhost:8002 | Risk analysis |
| DecisionSynthesis | http://localhost:8003 | Decision logic |
| NotificationSystem | http://localhost:8004 | Audit trail |

## Support

For detailed information:
- Check [README.md](README.md) for complete documentation
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Review code comments in source files
- Check terminal output for detailed logs

## What's Next?

Once you're comfortable with the system:

1. **Customize Decision Logic:**
   - Edit `mcp_decision_synthesis.py`
   - Modify risk scoring algorithm
   - Adjust approval thresholds

2. **Add New Data Sources:**
   - Create new MCP servers
   - Integrate with credit bureaus
   - Connect to banking systems

3. **Enhance Analytics:**
   - Track decision trends
   - Build dashboards
   - Generate compliance reports

4. **Production Deployment:**
   - Use Docker for containerization
   - Set up Kubernetes cluster
   - Configure monitoring and alerts

---

**Happy lending! 🏦**

For help, refer to the full documentation or check the troubleshooting section above.
