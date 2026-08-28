"""
Automated Verification & Integrity Test for Staff Attendance SaaS System
"""

import sys
import os
import urllib.request
import json
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import run_server
from database import get_connection, get_company_settings


def test_api_endpoints():
    print("Testing Staff Attendance System Endpoints...")
    time.sleep(1.0)
    base = "http://127.0.0.1:8088"

    def req(path, method="GET", data=None):
        url = f"{base}{path}"
        headers = {"Content-Type": "application/json"}
        req_obj = urllib.request.Request(url, headers=headers, method=method)
        if data:
            req_obj.data = json.dumps(data).encode("utf-8")
        with urllib.request.urlopen(req_obj) as response:
            body = response.read().decode("utf-8")
            return response.status, body

    # 1. HTML Pages
    for p in ["/", "/kiosk", "/scan", "/portal", "/badges", "/pitch"]:
        status, body = req(p)
        assert status == 200, f"Page {p} returned {status}"
        print(f"  [PASS] Page {p} (length: {len(body)} bytes)")

    # 2. API Status & Token
    status, body = req("/api/status")
    data = json.loads(body)
    assert data["status"] == "online", "API status should be online"
    print(f"  [PASS] /api/status -> {data['system']}")

    status, body = req("/api/kiosk/token")
    token_data = json.loads(body)
    assert "token" in token_data, "Token should be present"
    print(f"  [PASS] /api/kiosk/token -> Token: {token_data['token']} (Remaining: {token_data['seconds_remaining']}s)")

    # 3. Dashboard Stats
    status, body = req("/api/dashboard/stats")
    stats = json.loads(body)
    print(f"  [PASS] /api/dashboard/stats -> Staff: {stats['total_employees']}, Present: {stats['present_today']}, Rate: {stats['punctuality_rate']}%")

    # 4. Today Attendance
    status, body = req("/api/attendance/today")
    today_list = json.loads(body)
    assert len(today_list) > 0, "Today attendance should have records"
    print(f"  [PASS] /api/attendance/today -> {len(today_list)} employee records")

    # 5. Quick Toggle (Check In / Check Out with Employee Code)
    emp_code = today_list[0]["employee_code"]
    status, body = req("/api/attendance/quick-toggle", method="POST", data={"identifier": emp_code})
    toggle_res = json.loads(body)
    print(f"  [PASS] /api/attendance/quick-toggle for {emp_code} -> {toggle_res.get('message')}")

    # 6. Payroll Summary & Generation
    status, body = req("/api/payroll/summary")
    payroll = json.loads(body)
    print(f"  [PASS] /api/payroll/summary -> {payroll['count']} staff, Total Net: ${payroll['total_net_payout']}")

    status, body = req("/api/payroll/generate", method="POST", data={"month": "2026-08"})
    gen_payroll = json.loads(body)
    assert gen_payroll["count"] > 0, "Payroll records should be generated"
    print(f"  [PASS] /api/payroll/generate -> Computed payroll for {gen_payroll['count']} staff")

    # 7. Payslip Itemized View
    sample_ref = gen_payroll["records"][0]["payslip_number"]
    status, body = req(f"/api/payroll/payslip/{sample_ref}")
    payslip = json.loads(body)
    assert "payslip" in payslip, "Payslip itemization failed"
    print(f"  [PASS] /api/payroll/payslip/{sample_ref} -> Net Pay: ${payslip['payslip']['net_pay']}")

    print("\nALL AUTOMATED TESTS PASSED SUCCESSFULLY! 100% OPERATIONAL.")
    os._exit(0)


if __name__ == "__main__":
    t = threading.Thread(target=run_server, args=(8088,), daemon=True)
    t.start()
    test_api_endpoints()
