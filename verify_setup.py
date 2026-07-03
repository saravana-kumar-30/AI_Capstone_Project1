#!/usr/bin/env python3

import subprocess
import time
import requests
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_success(text):
    print(f"  ✓ {text}")

def print_error(text):
    print(f"  ✗ {text}")

def print_warning(text):
    print(f"  ⚠ {text}")

def check_file_exists(filepath):
    return Path(filepath).exists()

def check_service_health(url, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass

        if attempt < max_retries - 1:
            time.sleep(1)

    return False

def main():
    print_header("🏦 Loan Approval AI System - Setup Verification")

    # 1. Check project structure
    print("1️⃣  Checking Project Structure...")

    required_files = [
        "requirements.txt",
        "config.py",
        "schemas.py",
        "main.py",
        "streamlit_app.py",
        "orchestration.py",
        "agents.py",
        "mcp_applicant_db.py",
        "mcp_risk_rules.py",
        "mcp_decision_synthesis.py",
        "mcp_notification.py",
        "test_api.py",
        "run_all_services.sh",
        "README.md",
        "QUICKSTART.md",
        "ARCHITECTURE.md",
    ]

    all_files_exist = True
    for file in required_files:
        if check_file_exists(file):
            print_success(file)
        else:
            print_error(f"{file} - NOT FOUND")
            all_files_exist = False

    if not all_files_exist:
        print_header("❌ Setup Incomplete")
        print("Some required files are missing. Please re-run the setup.")
        sys.exit(1)

    print_success("All project files present")

    # 2. Check dependencies
    print("\n2️⃣  Checking Dependencies...")

    required_packages = [
        "fastapi",
        "uvicorn",
        "streamlit",
        "langgraph",
        "langchain",
        "anthropic",
        "pydantic",
        "requests",
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package}")
        except ImportError:
            print_warning(f"{package} - NOT INSTALLED")
            missing_packages.append(package)

    if missing_packages:
        print_warning("Some packages are not installed")
        print("\nInstall missing packages with:")
        print(f"  pip install {' '.join(missing_packages)}")
    else:
        print_success("All dependencies installed")

    # 3. Check environment
    print("\n3️⃣  Checking Environment...")

    env_file_exists = check_file_exists(".env")
    if env_file_exists:
        print_success(".env file found")
    else:
        print_warning(".env file not found")
        print("  → Run: cp .env.example .env")

    # 4. Network ports
    print("\n4️⃣  Checking Port Availability...")

    ports_to_check = {
        8501: "Streamlit UI",
        8000: "FastAPI",
        8001: "ApplicantDB MCP",
        8002: "RiskRulesDB MCP",
        8003: "DecisionSynthesis MCP",
        8004: "NotificationSystem MCP",
    }

    import socket

    busy_ports = []
    for port, service in ports_to_check.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result == 0:
                print_warning(f"Port {port} ({service}) - IN USE")
                busy_ports.append((port, service))
            else:
                print_success(f"Port {port} ({service}) - Available")
        except Exception as e:
            print_error(f"Port {port} ({service}) - Error: {e}")

    if busy_ports:
        print_warning("Some ports are already in use")
        print("  → You may need to stop existing services")
        print("  → Use: lsof -i :PORT to find process")
        print("  → Use: kill -9 PID to stop process")

    # 5. Documentation check
    print("\n5️⃣  Checking Documentation...")

    docs = {
        "README.md": "Main documentation",
        "QUICKSTART.md": "Quick start guide",
        "ARCHITECTURE.md": "Architecture details",
    }

    for doc, description in docs.items():
        if check_file_exists(doc):
            print_success(f"{doc} - {description}")
        else:
            print_error(f"{doc} - NOT FOUND")

    # Summary
    print_header("✓ Verification Complete")

    if all_files_exist and not missing_packages and not busy_ports:
        print("🎉 Your system is ready to run!")
        print("\nNext steps:")
        print("  1. Review the QUICKSTART.md file")
        print("  2. Run: ./run_all_services.sh")
        print("  3. Open: http://localhost:8501")
        print("\nFor detailed info, see:")
        print("  • README.md - Full documentation")
        print("  • ARCHITECTURE.md - Technical details")
        print("  • QUICKSTART.md - 5-minute setup guide")
        return True
    else:
        print("⚠️  Please address the issues above before running the system")
        print("\nCommon fixes:")
        print("  • Missing files: Re-run setup")
        print("  • Missing packages: pip install -r requirements.txt")
        print("  • Ports in use: Kill existing processes")
        print("  • Missing .env: cp .env.example .env")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
