import uuid
import asyncio
import aiosqlite
from datetime import datetime
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

mcp = FastMCP("NotificationSystem MCP Server")

DB_PATH = "notifications.db"

# Compliance rules: hard limits that must be met before approval
COMPLIANCE_RULES = [
    {"name": "minimum_credit_score", "check": lambda r: r["credit_score"] >= 500 if "credit_score" in r else True, "flag": "Credit score below minimum threshold of 500"},
    {"name": "max_risk_score",       "check": lambda r: r["risk_score"] <= 95,                                        "flag": "Risk score exceeds regulatory ceiling of 95"},
    {"name": "valid_decision",       "check": lambda r: r["decision"] in ("Approve", "Review", "Reject"),            "flag": "Decision value is not a recognised classification"},
]


async def _init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                case_id     TEXT PRIMARY KEY,
                applicant_id TEXT NOT NULL,
                decision    TEXT NOT NULL,
                risk_score  REAL NOT NULL,
                explanation TEXT,
                action_taken TEXT,
                compliance_flags TEXT,
                timestamp   TEXT NOT NULL
            )
        """)
        await db.commit()


async def _persist(record: dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO notifications
               (case_id, applicant_id, decision, risk_score, explanation,
                action_taken, compliance_flags, timestamp)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                record["case_id"],
                record["applicant_id"],
                record["decision"],
                record["risk_score"],
                record.get("explanation", ""),
                record.get("action_taken", ""),
                record.get("compliance_flags", ""),
                record["timestamp"],
            ),
        )
        await db.commit()


async def _fetch_all() -> list:
    await _init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM notifications ORDER BY timestamp DESC") as cursor:
            rows = await cursor.fetchall()
    return [dict(r) for r in rows]


def _run_compliance_checks(applicant_id: str, decision: str, risk_score: float) -> list[str]:
    """Return a list of compliance flag strings for any rule violations."""
    context = {"applicant_id": applicant_id, "decision": decision, "risk_score": risk_score}
    flags = []
    for rule in COMPLIANCE_RULES:
        if not rule["check"](context):
            flags.append(rule["flag"])
    return flags


@mcp.tool()
async def send_notification(
    applicant_id: str,
    decision: str,
    risk_score: float,
    explanation: str,
) -> dict:
    """Log a loan decision, run compliance checks, and persist to SQLite."""
    await _init_db()

    compliance_flags = _run_compliance_checks(applicant_id, decision, risk_score)

    case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.utcnow().isoformat()

    action_map = {
        "Approve": "Application approved and forwarded for funding",
        "Reject":  "Application rejected. Applicant notified",
        "Review":  "Application flagged for manual review by compliance team",
    }
    action_taken = action_map.get(decision, "Unknown action")

    if compliance_flags:
        action_taken = f"COMPLIANCE HOLD — {action_taken}. Flags: {'; '.join(compliance_flags)}"

    record = {
        "case_id": case_id,
        "applicant_id": applicant_id,
        "decision": decision,
        "risk_score": risk_score,
        "explanation": explanation,
        "action_taken": action_taken,
        "compliance_flags": "; ".join(compliance_flags),
        "timestamp": timestamp,
    }
    await _persist(record)

    return {
        "action_taken": action_taken,
        "notification_sent": True,
        "case_id": case_id,
        "timestamp": timestamp,
        "summary": f"Notification processed for {applicant_id}",
        "compliance_flags": compliance_flags,
    }


# Legacy HTTP shim
@mcp.custom_route("/tools/send_notification", methods=["POST"])
async def _http_send_notification(request: Request) -> JSONResponse:
    body = await request.json()
    result = await send_notification(
        applicant_id=body.get("applicant_id", ""),
        decision=body.get("decision", "Review"),
        risk_score=body.get("risk_score", 50.0),
        explanation=body.get("explanation", ""),
    )
    return JSONResponse(result)


@mcp.custom_route("/notifications", methods=["GET"])
async def _http_get_notifications(request: Request) -> JSONResponse:
    rows = await _fetch_all()
    return JSONResponse({"notifications": rows})


@mcp.custom_route("/health", methods=["GET"])
async def _health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "NotificationSystem"})


app = mcp.http_app()

if __name__ == "__main__":
    asyncio.run(mcp.run_http_async(host="0.0.0.0", port=8004, show_banner=False))
