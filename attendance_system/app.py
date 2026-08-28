"""
Staff Attendance, QR Check-in & Payroll SaaS Application Server
Pure Python Standard Library - Zero External Dependencies
"""

import os
import sys
import json
import time
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure attendance_system is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import (
    init_db, get_connection, log_activity,
    get_company_settings, update_company_settings,
    get_current_kiosk_qr_token, validate_kiosk_qr_token,
    list_departments, create_department,
    list_employees, get_employee, create_employee, update_employee, delete_employee,
    record_check_in, record_check_out, toggle_attendance_quick,
    get_today_attendance, get_attendance_history, get_monthly_attendance_matrix,
    get_dashboard_stats, get_chart_data,
    list_leave_requests, submit_leave_request, review_leave_request,
    generate_monthly_payroll, get_payroll_summary, get_payslip, update_payroll_status
)
from seed_data import populate_seed_data, PRESETS


STATIC_DIR = os.path.join(BASE_DIR, "static")


class AttendanceHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]} {args[1]}\n")

    def send_json_response(self, data, status_code=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def parse_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return {}

    def get_client_ip(self):
        forwarded = self.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.client_address[0] if self.client_address else "127.0.0.1"

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Page Routes
        if path in ["/", "/index.html"]:
            return self.serve_file(os.path.join(STATIC_DIR, "index.html"), "text/html")
        elif path == "/kiosk":
            return self.serve_file(os.path.join(STATIC_DIR, "kiosk.html"), "text/html")
        elif path == "/scan":
            return self.serve_file(os.path.join(STATIC_DIR, "scan.html"), "text/html")
        elif path == "/portal":
            return self.serve_file(os.path.join(STATIC_DIR, "staff_portal.html"), "text/html")
        elif path == "/pitch":
            return self.serve_file(os.path.join(STATIC_DIR, "pitch_landing.html"), "text/html")
        elif path == "/badges":
            return self.serve_file(os.path.join(STATIC_DIR, "print_badges.html"), "text/html")

        # 2. REST API Routes
        if path.startswith("/api/"):
            return self.handle_api_get(path, query)

        # 3. Default Static File Handling
        super().do_GET()

    def serve_file(self, full_path, mime_type):
        if not os.path.exists(full_path):
            self.send_error(404, "File Not Found")
            return
        with open(full_path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def handle_api_get(self, path, query):
        try:
            if path == "/api/status":
                settings = get_company_settings()
                kiosk_token = get_current_kiosk_qr_token()
                return self.send_json_response({
                    "status": "online",
                    "system": "Staff Attendance & Payroll SaaS",
                    "version": "2.0.0",
                    "company": settings,
                    "kiosk_token": kiosk_token,
                    "server_time": datetime.now().isoformat()
                })

            elif path == "/api/kiosk/token":
                token_data = get_current_kiosk_qr_token()
                return self.send_json_response(token_data)

            elif path == "/api/settings":
                return self.send_json_response(get_company_settings())

            elif path == "/api/dashboard/stats":
                return self.send_json_response(get_dashboard_stats())

            elif path == "/api/dashboard/charts":
                return self.send_json_response(get_chart_data())

            elif path == "/api/attendance/today":
                return self.send_json_response(get_today_attendance())

            elif path == "/api/attendance/history":
                start_date = query.get("start_date", [None])[0]
                end_date = query.get("end_date", [None])[0]
                dep_id = query.get("department_id", [None])[0]
                emp_id = query.get("employee_id", [None])[0]
                status = query.get("status", [None])[0]
                return self.send_json_response(get_attendance_history(start_date, end_date, dep_id, emp_id, status))

            elif path == "/api/attendance/monthly-matrix":
                month = query.get("month", [None])[0]
                return self.send_json_response(get_monthly_attendance_matrix(month))

            elif path == "/api/departments":
                return self.send_json_response(list_departments())

            elif path == "/api/employees":
                dep_id = query.get("department_id", [None])[0]
                status = query.get("status", [None])[0]
                search = query.get("search", [None])[0]
                return self.send_json_response(list_employees(dep_id, status, search))

            elif path.startswith("/api/employees/"):
                parts = path.strip("/").split("/")
                if len(parts) == 3:
                    emp_id = parts[2]
                    emp = get_employee(emp_id)
                    if emp:
                        return self.send_json_response(emp)
                    return self.send_json_response({"error": "Employee not found"}, 404)
                elif len(parts) == 4 and parts[3] == "history":
                    emp_id = parts[2]
                    history = get_attendance_history(employee_id=emp_id)
                    return self.send_json_response(history)

            elif path == "/api/leaves":
                status = query.get("status", [None])[0]
                emp_id = query.get("employee_id", [None])[0]
                return self.send_json_response(list_leave_requests(status, emp_id))

            elif path == "/api/payroll/summary":
                month = query.get("month", [None])[0]
                return self.send_json_response(get_payroll_summary(month))

            elif path.startswith("/api/payroll/payslip/"):
                payslip_ref = path.split("/")[-1]
                data = get_payslip(payslip_ref)
                if data:
                    return self.send_json_response(data)
                return self.send_json_response({"error": "Payslip not found"}, 404)

            elif path == "/api/demo/presets":
                return self.send_json_response({"presets": list(PRESETS.keys())})

            else:
                return self.send_json_response({"error": "Endpoint not found"}, 404)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.parse_json_body()
        ip = self.get_client_ip()

        try:
            # 1. Quick Check-In / Check-Out Toggle (Webcam Badge / PIN / Kiosk)
            if path == "/api/attendance/quick-toggle":
                identifier = body.get("identifier") or body.get("employee_code") or body.get("token") or body.get("pin")
                if not identifier:
                    return self.send_json_response({"success": False, "message": "Identifier required"}, 400)
                
                method = body.get("method", "badge_scan")
                res = toggle_attendance_quick(identifier, method=method, ip_address=ip, location_lat=body.get("lat"), location_lng=body.get("lng"))
                return self.send_json_response(res, 200 if res.get("success") else 400)

            # 2. Dynamic Kiosk QR Scan Check-In (Mobile Phone Scan)
            elif path == "/api/attendance/check-in":
                emp_id = body.get("employee_id")
                emp_code = body.get("employee_code")
                kiosk_token = body.get("kiosk_token")

                # If dynamic token provided, validate it
                if kiosk_token:
                    if not validate_kiosk_qr_token(kiosk_token):
                        return self.send_json_response({
                            "success": False,
                            "message": "Invalid or Expired Kiosk QR Code. Please scan the live screen again."
                        }, 400)

                # Resolve employee
                if not emp_id and emp_code:
                    emp = get_employee(emp_code)
                    if emp:
                        emp_id = emp["id"]

                if not emp_id:
                    return self.send_json_response({"success": False, "message": "Employee ID or Code is required"}, 400)

                res = record_check_in(
                    emp_id,
                    check_in_type=body.get("check_in_type", "mobile_scan"),
                    custom_time=body.get("time"),
                    custom_date=body.get("date"),
                    notes=body.get("notes"),
                    ip_address=ip,
                    location_lat=body.get("lat"),
                    location_lng=body.get("lng")
                )
                return self.send_json_response(res, 200 if res.get("success") else 400)

            # 3. Check-Out
            elif path == "/api/attendance/check-out":
                emp_id = body.get("employee_id")
                emp_code = body.get("employee_code")
                kiosk_token = body.get("kiosk_token")

                if kiosk_token:
                    if not validate_kiosk_qr_token(kiosk_token):
                        return self.send_json_response({
                            "success": False,
                            "message": "Invalid or Expired Kiosk QR Code. Please scan the live screen again."
                        }, 400)

                if not emp_id and emp_code:
                    emp = get_employee(emp_code)
                    if emp:
                        emp_id = emp["id"]

                if not emp_id:
                    return self.send_json_response({"success": False, "message": "Employee ID or Code is required"}, 400)

                res = record_check_out(
                    emp_id,
                    check_out_type=body.get("check_out_type", "mobile_scan"),
                    custom_time=body.get("time"),
                    custom_date=body.get("date"),
                    notes=body.get("notes"),
                    ip_address=ip,
                    location_lat=body.get("lat"),
                    location_lng=body.get("lng")
                )
                return self.send_json_response(res, 200 if res.get("success") else 400)

            # 4. Create Employee
            elif path == "/api/employees":
                new_emp = create_employee(body)
                return self.send_json_response(new_emp, 201)

            # 5. Create Department
            elif path == "/api/departments":
                dep_id = create_department(body.get("name"), body.get("manager_name", ""), body.get("color", "#3B82F6"))
                return self.send_json_response({"id": dep_id, "name": body.get("name")}, 201)

            # 6. Submit Leave Request
            elif path == "/api/leaves":
                emp_id = body.get("employee_id")
                if not emp_id and body.get("employee_code"):
                    emp = get_employee(body.get("employee_code"))
                    if emp:
                        emp_id = emp["id"]
                
                leave_id = submit_leave_request(
                    emp_id,
                    body.get("leave_type", "vacation"),
                    body.get("start_date"),
                    body.get("end_date"),
                    body.get("reason", "")
                )
                return self.send_json_response({"success": True, "leave_id": leave_id}, 201)

            # 7. Generate Payroll
            elif path == "/api/payroll/generate":
                month = body.get("month") or datetime.now().strftime("%Y-%m")
                summary = generate_monthly_payroll(month)
                return self.send_json_response(summary, 200)

            # 8. Update Company Settings
            elif path == "/api/settings":
                updated = update_company_settings(body)
                return self.send_json_response(updated)

            # 9. Load Demo Preset
            elif path == "/api/demo/preset":
                preset_name = body.get("preset", "tech")
                populate_seed_data(preset_name)
                return self.send_json_response({
                    "success": True,
                    "message": f"Successfully loaded '{preset_name}' industry demo dataset.",
                    "settings": get_company_settings()
                })

            else:
                return self.send_json_response({"error": "Endpoint not found"}, 404)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.parse_json_body()

        try:
            if path.startswith("/api/employees/"):
                emp_id = int(path.split("/")[-1])
                updated = update_employee(emp_id, body)
                return self.send_json_response(updated)

            elif path.startswith("/api/leaves/") and path.endswith("/status"):
                parts = path.strip("/").split("/")
                leave_id = int(parts[2])
                status = body.get("status", "approved")
                reviewer = body.get("reviewer_name", "Admin")
                review_leave_request(leave_id, status, reviewer)
                return self.send_json_response({"success": True, "status": status})

            elif path.startswith("/api/payroll/") and path.endswith("/status"):
                parts = path.strip("/").split("/")
                payroll_id = int(parts[2])
                status = body.get("status", "paid")
                update_payroll_status(payroll_id, status, body.get("payment_date"))
                return self.send_json_response({"success": True, "status": status})

            else:
                return self.send_json_response({"error": "Endpoint not found"}, 404)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            if path.startswith("/api/employees/"):
                emp_id = int(path.split("/")[-1])
                delete_employee(emp_id)
                return self.send_json_response({"success": True})
            else:
                return self.send_json_response({"error": "Endpoint not found"}, 404)
        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)


def run_server(port=5000):
    init_db()
    # Check if empty, then seed
    conn = get_connection()
    count = conn.cursor().execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    conn.close()
    if count == 0:
        populate_seed_data("tech")

    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, AttendanceHTTPRequestHandler)
    print(f"============================================================")
    print(f"  STAFF ATTENDANCE, QR CHECK-IN & PAYROLL SYSTEM")
    print(f"  Live Server Running on: http://localhost:{port}")
    print(f"  - Admin Dashboard:       http://localhost:{port}/")
    print(f"  - Office Kiosk Screen:   http://localhost:{port}/kiosk")
    print(f"  - Mobile QR Scan:        http://localhost:{port}/scan")
    print(f"  - Staff Self-Service:    http://localhost:{port}/portal")
    print(f"  - Print ID Badges:       http://localhost:{port}/badges")
    print(f"  - B2B Pitch Landing:     http://localhost:{port}/pitch")
    print(f"============================================================")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    run_server(port)
