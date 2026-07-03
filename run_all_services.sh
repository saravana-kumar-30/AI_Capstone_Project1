#!/bin/bash

set -e

echo "🚀 Starting Loan Approval AI System..."
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
fi

echo "Starting MCP Servers..."
python mcp_applicant_db.py &
APPLICANT_PID=$!
echo "  ✓ ApplicantDB server started (PID: $APPLICANT_PID)"

sleep 2

python mcp_risk_rules.py &
RISK_PID=$!
echo "  ✓ RiskRulesDB server started (PID: $RISK_PID)"

sleep 2

python mcp_decision_synthesis.py &
DECISION_PID=$!
echo "  ✓ DecisionSynthesis server started (PID: $DECISION_PID)"

sleep 2

python mcp_notification.py &
NOTIFICATION_PID=$!
echo "  ✓ NotificationSystem server started (PID: $NOTIFICATION_PID)"

sleep 2

echo ""
echo "Starting FastAPI microservice..."
python main.py &
FASTAPI_PID=$!
echo "  ✓ FastAPI service started (PID: $FASTAPI_PID)"

sleep 3

echo ""
echo "Starting Streamlit UI..."
streamlit run streamlit_app.py --logger.level=info &
STREAMLIT_PID=$!
echo "  ✓ Streamlit UI started (PID: $STREAMLIT_PID)"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✓ All services started successfully!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📍 Service Endpoints:"
echo "   • ApplicantDB MCP Server: http://localhost:8001"
echo "   • RiskRulesDB MCP Server: http://localhost:8002"
echo "   • DecisionSynthesis MCP Server: http://localhost:8003"
echo "   • NotificationSystem MCP Server: http://localhost:8004"
echo "   • FastAPI Service: http://localhost:8000"
echo "   • Streamlit UI: http://localhost:8501"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo ""
echo "🛑 To stop all services, press Ctrl+C"
echo "═══════════════════════════════════════════════════════════════"
echo ""

trap "kill $APPLICANT_PID $RISK_PID $DECISION_PID $NOTIFICATION_PID $FASTAPI_PID $STREAMLIT_PID 2>/dev/null || true" SIGINT SIGTERM

wait
