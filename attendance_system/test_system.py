"""
Automated School System Verification Test Suite
Tests Unified Dashboard: Students, Parent WhatsApp, Bus Scanner, Faculty Attendance & Automated Payroll Engine
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


def test_unified_school_endpoints():
    print("Testing Unified School Attendance, Safety & Faculty Payroll Endpoints...")
    time.sleep(1.0)
    base = "http://127.0.0.1:8089"

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
    for p in ["/", "/kiosk", "/scan", "/bus", "/badges", "/broadcast", "/register", "/portal", "/pitch"]:
        status, body = req(p)
        assert status == 200, f"Page {p} returned {status}"
        print(f"  [PASS] Page {p} (length: {len(body)} bytes)")

    # 2. School Status
    status, body = req("/api/school/status")
    data = json.loads(body)
    assert data["status"] == "online", "API status should be online"
    print(f"  [PASS] /api/school/status -> School: {data['school']['name']} ({data['school']['affiliation_board']})")

    # 3. Morning Strength Report (8:15 AM Cutoff)
    status, body = req("/api/school/morning-strength")
    strength = json.loads(body)
    summary = strength["summary"]
    print(f"  [PASS] /api/school/morning-strength -> Enrolled: {summary['total_students']}, Present: {summary['present_students']} ({summary['strength_percentage']}%), Absent: {summary['absent_students']}")

    # 4. Student Gate Scan
    sample_adm = "MVM-2026-0101"
    status, body = req("/api/school/gate-scan", method="POST", data={"identifier": sample_adm})
    scan_res = json.loads(body)
    assert scan_res["success"] is True
    print(f"  [PASS] /api/school/gate-scan -> {scan_res.get('message')[:50]}...")

    # 5. Teacher Live Attendance List
    status, body = req("/api/teachers/today")
    teachers_today = json.loads(body)
    assert len(teachers_today) > 0
    print(f"  [PASS] /api/teachers/today -> Found {len(teachers_today)} faculty members on daily board")

    # 6. Teacher Scan / Punch
    status, body = req("/api/school/staff-scan", method="POST", data={"identifier": "FAC-101"})
    staff_res = json.loads(body)
    assert staff_res["success"] is True
    print(f"  [PASS] /api/school/staff-scan -> {staff_res.get('message')}")

    # 7. Faculty Payroll Generation
    status, body = req("/api/payroll/generate", method="POST", data={"month": "2026-08"})
    pay_res = json.loads(body)
    assert pay_res["count"] > 0
    print(f"  [PASS] /api/payroll/generate -> Processed {pay_res['count']} faculty payslips (Total Net: ₹{pay_res['total_net_payout']})")

    # 8. Faculty Payslip Voucher View
    sample_slip = pay_res["records"][0]["payslip_number"]
    status, body = req(f"/api/payroll/payslip/{sample_slip}")
    slip_res = json.loads(body)
    assert "payslip" in slip_res
    print(f"  [PASS] /api/payroll/payslip/{sample_slip} -> Employee: {slip_res['payslip']['first_name']}, Net Pay: ₹{slip_res['payslip']['net_pay']}")

    # 9. Teacher Leaves
    status, body = req("/api/leaves")
    leaves_res = json.loads(body)
    print(f"  [PASS] /api/leaves -> Leaves queue accessible (count: {len(leaves_res)})")

    # 10. 8:30 AM Absence Broadcast
    status, body = req("/api/school/send-830-absence", method="POST", data={})
    abs_res = json.loads(body)
    assert abs_res["success"] is True
    print(f"  [PASS] /api/school/send-830-absence -> Dispatched {abs_res['dispatched_count']} WhatsApp notices to parents")

    print("\nALL UNIFIED SCHOOL ATTENDANCE & PAYROLL TESTS PASSED WITH 100% SUCCESS!")
    os._exit(0)


if __name__ == "__main__":
    t = threading.Thread(target=run_server, args=(8089,), daemon=True)
    t.start()
    test_unified_school_endpoints()
