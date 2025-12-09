#!/usr/bin/env python3
"""
API Testing Script for Healthcare Insurance Verification APIs
Tests: Insurance Eligibility, CRM Intake, and pVerify MBI APIs
"""

import requests
import json
from datetime import datetime

# Disable SSL warnings for testing (remove in production)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================
# CONFIGURATION - API Credentials
# ============================================

# Insurance Eligibility API (Emdeon/Biologistic)
ELIGIBILITY_CONFIG = {
    "token_url": "https://emdeon.biologisticsolutions.com/token",
    "check_url": "https://emdeon.biologisticsolutions.com/v1/5867F2C5-EE0E-4DE4-9AE3-411C2DA7EE17/eligibility/check",
    "client_id": "F4397107-3BD2-4A1C-B9EC-5043F202A36C",
    "client_secret": "8470CD92-A562-484F-A823-9FEE441273FC",
}

# CRM Intake API
CRM_CONFIG = {
    "token_url": "https://accounts.biologisticsolutions.com/v1/token",
    "api_base_url": "https://api.biologisticsolutions.com",
    "client_id": "75D8726A-24B8-4AF1-A22D-643DB2C37FDB",
    "client_secret": "B04B5BEF-1AD7-4077-8D2F-A7F697DE3209",
    # NOTE: You need to provide these credentials
    "username": "",  # Fill in your CRM username
    "password": "",  # Fill in your CRM password
}

# pVerify MBI API
PVERIFY_CONFIG = {
    "token_url": "https://api.pverify.com/Token",
    "mbi_inquiry_url": "https://api.pverify.com/API/MBIInquiry",
    "mbi_response_url": "https://api.pverify.com/API/GetMBIResponse",
    # NOTE: You need to provide these credentials
    "username": "",  # Fill in your pVerify username
    "password": "",  # Fill in your pVerify password
}

# Test patient data (from documentation example)
TEST_PATIENT = {
    "FirstName": "Lyndsey",
    "LastName": "Burke",
    "DOB": "06/19/1957",
    "ZipCode": "03818",
    "Gender": "1",
    "NPI": "1629047436",
    "ParticipantId": "1T18UQ5PH65"
}


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_result(success, message, data=None):
    """Print formatted result"""
    status = "✓ SUCCESS" if success else "✗ FAILED"
    print(f"\n{status}: {message}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)[:1000]}")  # Limit output


# ============================================
# 1. INSURANCE ELIGIBILITY API TESTS
# ============================================

def test_eligibility_token():
    """Test getting OAuth token for Insurance Eligibility API"""
    print_header("TEST 1: Insurance Eligibility - Get Token")

    try:
        response = requests.post(
            ELIGIBILITY_CONFIG["token_url"],
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": ELIGIBILITY_CONFIG["client_id"],
                "client_secret": ELIGIBILITY_CONFIG["client_secret"],
                "grant_type": "client_credentials"
            },
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token", "")
            expires_in = data.get("expires_in", 0)
            print_result(True, f"Token obtained! Expires in {expires_in} seconds")
            print(f"Token (first 50 chars): {access_token[:50]}...")
            return access_token
        else:
            print_result(False, f"Failed to get token", response.json() if response.text else None)
            return None

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return None


def test_eligibility_check(access_token):
    """Test Insurance Eligibility Check"""
    print_header("TEST 2: Insurance Eligibility - Check Patient")

    if not access_token:
        print_result(False, "No access token available, skipping test")
        return None

    try:
        response = requests.post(
            ELIGIBILITY_CONFIG["check_url"],
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            },
            json=TEST_PATIENT,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            is_success = data.get("IsSucess", False)

            if is_success:
                patient_data = data.get("Data", {})
                status = patient_data.get("Status", "Unknown")
                result_code = patient_data.get("ResultCode", -1)
                billing_path = patient_data.get("BillingPath", -1)

                print_result(True, f"Eligibility Check Complete!")
                print(f"  - Status: {status}")
                print(f"  - ResultCode: {result_code} (1=Eligible, 2=Ineligible, 3=Unknown)")
                print(f"  - BillingPath: {billing_path} (1=Medicare B, 2=MedAdvPPO, 3=MedAdvHMO, 4=Commercial)")
                print(f"  - SearchId: {patient_data.get('SearchId')}")
                print(f"  - Part A: {patient_data.get('PartA')}")
                print(f"  - Part B: {patient_data.get('PartB')}")
                print(f"  - HostCode: {patient_data.get('HostCode')}")

                return data
            else:
                error = data.get("Error", {})
                print_result(False, f"API returned failure: {error.get('Message', 'Unknown error')}")
                return data
        else:
            print_result(False, f"HTTP Error", response.text)
            return None

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return None


# ============================================
# 2. CRM INTAKE API TESTS
# ============================================

def test_crm_token():
    """Test getting OAuth token for CRM Intake API"""
    print_header("TEST 3: CRM Intake - Get Token")

    if not CRM_CONFIG["username"] or not CRM_CONFIG["password"]:
        print_result(False, "CRM username/password not configured. Please set CRM_CONFIG credentials.")
        print("  Edit the script and fill in:")
        print('  - CRM_CONFIG["username"]')
        print('  - CRM_CONFIG["password"]')
        return None

    try:
        response = requests.post(
            CRM_CONFIG["token_url"],
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username": CRM_CONFIG["username"],
                "password": CRM_CONFIG["password"],
                "grant_type": "password",
                "client_id": CRM_CONFIG["client_id"],
                "client_secret": CRM_CONFIG["client_secret"]
            },
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token", "")
            expires_in = data.get("expires_in", 0)
            print_result(True, f"CRM Token obtained! Expires in {expires_in} seconds")
            return access_token
        else:
            print_result(False, f"Failed to get CRM token", response.json() if response.text else None)
            return None

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return None


def test_crm_verify_lead(access_token, lead_id="123456", phone="2063720955", agent="SurveyAgent1"):
    """Test CRM Lead Verification"""
    print_header("TEST 4: CRM Intake - Verify Lead")

    if not access_token:
        print_result(False, "No CRM access token available, skipping test")
        return None

    try:
        url = f"{CRM_CONFIG['api_base_url']}/v1/AI/Agent/Verify/Lead/{lead_id}/{phone}/{agent}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        print(f"URL: {url}")

        data = response.json() if response.text else {}

        if response.status_code == 200:
            print_result(True, "Lead verification successful")
            print(f"  - Record Found: {data.get('record_found', 'N/A')}")
            print(f"  - Message: {data.get('message', 'N/A')}")
        elif response.status_code == 409:
            print_result(True, "Lead already exists (409 Conflict)")
            print(f"  - Record Found: {data.get('record_found', 'N/A')}")
            print(f"  - ID: {data.get('id', 'N/A')}")
        else:
            print_result(False, f"Unexpected response", data)

        return data

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return None


def test_crm_verify_member_id(access_token, member_id="1T18UQ5PH65"):
    """Test CRM Member ID Verification"""
    print_header("TEST 5: CRM Intake - Verify Member ID")

    if not access_token:
        print_result(False, "No CRM access token available, skipping test")
        return None

    try:
        url = f"{CRM_CONFIG['api_base_url']}/v1/AI/Agent/Verify/Patient/MemberId/{member_id}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        data = response.json() if response.text else {}

        if response.status_code == 200:
            record_found = data.get('record_found', False)
            if not record_found:
                print_result(True, "Member ID not found - OK to proceed with order")
            else:
                print_result(True, "Member ID already exists")
            print(f"  - Message: {data.get('message', 'N/A')}")
        else:
            print_result(False, f"Verification failed", data)

        return data

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return None


# ============================================
# 3. PVERIFY MBI API TESTS
# ============================================

def test_pverify_token():
    """Test getting OAuth token for pVerify MBI API"""
    print_header("TEST 6: pVerify MBI - Get Token")

    if not PVERIFY_CONFIG["username"] or not PVERIFY_CONFIG["password"]:
        print_result(False, "pVerify username/password not configured. Please set PVERIFY_CONFIG credentials.")
        print("  Edit the script and fill in:")
        print('  - PVERIFY_CONFIG["username"]')
        print('  - PVERIFY_CONFIG["password"]')
        return None

    try:
        response = requests.post(
            PVERIFY_CONFIG["token_url"],
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={PVERIFY_CONFIG['username']}&password={PVERIFY_CONFIG['password']}&grant_type=password",
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token", "")
            expires_in = data.get("expires_in", 0)
            print_result(True, f"pVerify Token obtained! Expires in {expires_in} seconds")
            return access_token
        else:
            print_result(False, f"Failed to get pVerify token", response.json() if response.text else None)
            return None

    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return None


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    print("\n" + "=" * 60)
    print(" HEALTHCARE API TESTING SCRIPT")
    print(f" Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = {
        "eligibility_token": False,
        "eligibility_check": False,
        "crm_token": False,
        "crm_verify_lead": False,
        "crm_verify_member": False,
        "pverify_token": False,
    }

    # Test 1 & 2: Insurance Eligibility API
    eligibility_token = test_eligibility_token()
    results["eligibility_token"] = eligibility_token is not None

    if eligibility_token:
        eligibility_result = test_eligibility_check(eligibility_token)
        results["eligibility_check"] = eligibility_result is not None and eligibility_result.get("IsSucess", False)

    # Test 3, 4, 5: CRM Intake API
    crm_token = test_crm_token()
    results["crm_token"] = crm_token is not None

    if crm_token:
        lead_result = test_crm_verify_lead(crm_token)
        results["crm_verify_lead"] = lead_result is not None

        member_result = test_crm_verify_member_id(crm_token)
        results["crm_verify_member"] = member_result is not None

    # Test 6: pVerify MBI API
    pverify_token = test_pverify_token()
    results["pverify_token"] = pverify_token is not None

    # Summary
    print_header("TEST SUMMARY")
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL/SKIP"
        print(f"  {status}: {test_name}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    print(f"\n  Total: {passed_count}/{total_count} tests passed")

    return results


if __name__ == "__main__":
    main()
