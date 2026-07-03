#!/usr/bin/env python3

import requests
import json
from datetime import datetime
from config import Config
from schemas import ApplicantProfileData, LoanApplicationData

API_BASE_URL = f"http://{Config.FASTAPI_HOST}:{Config.FASTAPI_PORT}/api"

TEST_CASES = [
    {
        "name": "Strong Applicant - High Income, Excellent Credit",
        "data": {
            "applicant_id": "APP001",
            "age": 35,
            "income": 150000,
            "employment_type": "Full-time",
            "location": "New York",
            "credit_score": 800,
            "loan_amount": 200000,
            "loan_tenure_months": 60,
            "existing_liabilities": 50000,
        },
    },
    {
        "name": "Risky Applicant - Low Credit Score",
        "data": {
            "applicant_id": "APP003",
            "age": 45,
            "income": 65000,
            "employment_type": "Full-time",
            "location": "Texas",
            "credit_score": 580,
            "loan_amount": 150000,
            "loan_tenure_months": 60,
            "existing_liabilities": 80000,
        },
    },
    {
        "name": "Moderate Applicant - Balanced Profile",
        "data": {
            "applicant_id": "APP002",
            "age": 28,
            "income": 85000,
            "employment_type": "Full-time",
            "location": "California",
            "credit_score": 700,
            "loan_amount": 120000,
            "loan_tenure_months": 48,
            "existing_liabilities": 35000,
        },
    },
]


def test_health():
    print("\n📍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        print(f"✓ Health check passed: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_loan_application(test_case):
    print(f"\n📋 Testing: {test_case['name']}")
    print("-" * 70)

    try:
        data = test_case["data"]
        applicant_profile = ApplicantProfileData(
            applicant_id=data["applicant_id"],
            age=data["age"],
            income=data["income"],
            employment_type=data["employment_type"],
            location=data["location"],
        )

        application_data = LoanApplicationData(
            applicant_id=data["applicant_id"],
            credit_score=data["credit_score"],
            loan_amount=data["loan_amount"],
            loan_tenure_months=data["loan_tenure_months"],
            existing_liabilities=data["existing_liabilities"],
            applicant_profile=applicant_profile,
        )

        response = requests.post(
            f"{API_BASE_URL}/submit-loan-application",
            json=application_data.model_dump(mode="json"),
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        print(f"✓ Application processed successfully")
        print(f"\n  Decision: {result['decision']}")
        print(f"  Risk Score: {result['risk_score']:.1f}/100")
        print(f"  Confidence: {result['confidence_level']:.0%}")
        print(f"  Case ID: {result['case_id']}")
        print(f"\n  Key Factors:")
        for factor in result.get("key_factors", []):
            print(f"    • {factor}")
        print(f"\n  Explanation: {result['explanation']}")

        return True

    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection error: {e}")
        print("  Make sure FastAPI service is running on port 8000")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ Request timeout")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("=" * 70)
    print("🏦 Loan Approval AI System - API Test Suite")
    print("=" * 70)

    if not test_health():
        print("\n❌ API is not reachable. Please start the FastAPI service first.")
        print("   Run: python main.py")
        return

    for test_case in TEST_CASES:
        test_loan_application(test_case)

    print("\n" + "=" * 70)
    print("✓ Test suite completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
