"""
Unified Smart School Attendance, Safety, Parent WhatsApp & Faculty Payroll Server
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import (
    init_db, get_connection,
    get_school_settings, update_school_settings,
    list_classes, list_bus_routes, list_students, get_student,
    get_morning_strength_report, record_student_gate_scan, record_bus_scan,
    send_830_absence_broadcast, send_emergency_broadcast,
    get_cbse_seba_monthly_register, list_teachers, get_teacher, create_teacher, update_teacher,
    record_staff_scan, get_teacher_today_attendance,
    list_teacher_leaves, submit_teacher_leave, review_teacher_leave,
    generate_teacher_payroll, get_teacher_payroll_summary, get_teacher_payslip, update_teacher_payroll_status
)
from seed_data import populate_school_seed_data


STATIC_DIR = os.path.join(BASE_DIR, "static")


class UnifiedSchoolHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def log_message(self, format, *args):
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
        elif path == "/bus":
            return self.serve_file(os.path.join(STATIC_DIR, "bus.html"), "text/html")
        elif path == "/badges":
            return self.serve_file(os.path.join(STATIC_DIR, "print_badges.html"), "text/html")
        elif path == "/broadcast":
            return self.serve_file(os.path.join(STATIC_DIR, "broadcast.html"), "text/html")
        elif path == "/register":
            return self.serve_file(os.path.join(STATIC_DIR, "register_export.html"), "text/html")
        elif path == "/portal":
            return self.serve_file(os.path.join(STATIC_DIR, "staff_portal.html"), "text/html")
        elif path == "/pitch":
            return self.serve_file(os.path.join(STATIC_DIR, "pitch_landing.html"), "text/html")

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
            if path in ["/api/status", "/api/school/status"]:
                settings = get_school_settings()
                return self.send_json_response({
                    "status": "online",
                    "system": "Smart School Attendance & Safety System",
                    "version": "3.0.0",
                    "school": settings,
                    "server_time": datetime.now().isoformat()
                })

            elif path in ["/api/school/morning-strength", "/api/dashboard/stats"]:
                date_val = query.get("date", [None])[0]
                report = get_morning_strength_report(date_val)
                return self.send_json_response(report)

            elif path in ["/api/school/classes", "/api/departments"]:
                return self.send_json_response(list_classes())

            elif path == "/api/school/bus-routes":
                return self.send_json_response(list_bus_routes())

            elif path in ["/api/school/students", "/api/students", "/api/employees"]:
                class_id = query.get("class_id", [None])[0]
                bus_route = query.get("bus_route", [None])[0]
                search = query.get("search", [None])[0]
                return self.send_json_response(list_students(class_id, bus_route, search))

            elif path.startswith("/api/school/students/") or path.startswith("/api/students/"):
                st_id = path.split("/")[-1]
                st = get_student(st_id)
                if st:
                    return self.send_json_response(st)
                return self.send_json_response({"error": "Student not found"}, 404)

            elif path in ["/api/school/cbse-register", "/api/cbse-register", "/api/reports/cbse-register"]:
                month = query.get("month", [None])[0]
                class_id = query.get("class_id", [None])[0]
                return self.send_json_response(get_cbse_seba_monthly_register(month, class_id))

            # Teacher & Faculty endpoints
            elif path in ["/api/school/teachers", "/api/teachers"]:
                search = query.get("search", [None])[0]
                return self.send_json_response(list_teachers(search))

            elif path in ["/api/teachers/today", "/api/attendance/today"]:
                return self.send_json_response(get_teacher_today_attendance())

            elif path in ["/api/payroll/summary", "/api/school/payroll/summary"]:
                month = query.get("month", [None])[0]
                return self.send_json_response(get_teacher_payroll_summary(month))

            elif path.startswith("/api/payroll/payslip/"):
                ref = path.split("/")[-1]
                data = get_teacher_payslip(ref)
                if data:
                    return self.send_json_response(data)
                return self.send_json_response({"error": "Payslip not found"}, 404)

            elif path in ["/api/leaves", "/api/school/leaves"]:
                status = query.get("status", [None])[0]
                return self.send_json_response(list_teacher_leaves(status))

            elif path in ["/api/school/settings", "/api/settings"]:
                return self.send_json_response(get_school_settings())

            elif path in ["/api/school/notifications", "/api/notifications"]:
                conn = get_connection()
                logs = [dict(r) for r in conn.cursor().execute("""
                    SELECT n.*, s.student_name, s.photo_url, c.grade as class_grade, c.section
                    FROM notification_logs n
                    LEFT JOIN students s ON n.student_id = s.id
                    LEFT JOIN classes c ON s.class_id = c.id
                    ORDER BY n.id DESC LIMIT 50
                """).fetchall()]
                conn.close()
                return self.send_json_response(logs)

            # 3. Dynamic Gate Token for anti-proxy QR
            elif path == "/api/kiosk/token":
                settings = get_school_settings()
                secret = settings.get("dynamic_qr_secret", "mvm_secret")
                refresh_sec = settings.get("qr_refresh_seconds", 20)
                cur_slot = int(time.time()) // refresh_sec
                time_rem = refresh_sec - (int(time.time()) % refresh_sec)
                raw = f"{secret}:{cur_slot}"
                token_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
                return self.send_json_response({
                    "token": f"GATE-{token_hash}",
                    "seconds_remaining": time_rem,
                    "refresh_interval": refresh_sec
                })

            else:
                return self.send_json_response({"error": "Endpoint not found"}, 404)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.parse_json_body()

        try:
            # 1. Student Gate Scan (1.2s Throughput)
            if path in ["/api/school/gate-scan", "/api/scan/gate", "/api/attendance/quick-toggle"]:
                identifier = body.get("identifier") or body.get("admission_no") or body.get("token") or body.get("rfid_card_id")
                if not identifier:
                    return self.send_json_response({"success": False, "message": "Identifier required"}, 400)
                
                scanned_by = body.get("scanned_by", "Main Gate Kiosk Laser")
                res = record_student_gate_scan(identifier, scanned_by=scanned_by)
                return self.send_json_response(res, 200 if res.get("success") else 400)

            # 2. School Bus Boarding Scan (Conductor Mode)
            elif path == "/api/school/bus-scan":
                identifier = body.get("identifier")
                bus_route = body.get("bus_route", "Route #4")
                scan_type = body.get("scan_type", "board")
                conductor = body.get("conductor_name", "Bus Conductor")
                res = record_bus_scan(identifier, bus_route, scan_type, conductor)
                return self.send_json_response(res, 200 if res.get("success") else 400)

            # 3. 8:30 AM Absence WhatsApp Broadcast
            elif path == "/api/school/send-830-absence":
                date_val = body.get("date")
                res = send_830_absence_broadcast(date_val)
                return self.send_json_response(res, 200)

            # 4. Emergency Broadcast
            elif path == "/api/school/emergency-broadcast":
                title = body.get("title", "Emergency Alert")
                message = body.get("message", "")
                target = body.get("target", "all_parents")
                class_id = body.get("class_id")
                bus_route = body.get("bus_route")
                res = send_emergency_broadcast(title, message, target, class_id, bus_route)
                return self.send_json_response(res, 200)

            # 5. Teacher Attendance Scan
            elif path in ["/api/school/staff-scan", "/api/teachers/scan"]:
                identifier = body.get("identifier")
                res = record_staff_scan(identifier)
                return self.send_json_response(res, 200 if res.get("success") else 400)

            # 6. Faculty Payroll Generation
            elif path in ["/api/payroll/generate", "/api/school/payroll/generate"]:
                month = body.get("month") or datetime.now().strftime("%Y-%m")
                summary = generate_teacher_payroll(month)
                return self.send_json_response(summary, 200)

            # 7. Teacher Leave Submission
            elif path in ["/api/leaves", "/api/school/leaves"]:
                staff_id = body.get("staff_id") or body.get("employee_id")
                leave_id = submit_teacher_leave(
                    staff_id,
                    body.get("leave_type", "Casual"),
                    body.get("start_date"),
                    body.get("end_date"),
                    body.get("reason", "")
                )
                return self.send_json_response({"success": True, "leave_id": leave_id}, 201)

            # 8. Create Teacher
            elif path in ["/api/teachers", "/api/school/teachers"]:
                new_t = create_teacher(body)
                return self.send_json_response(new_t, 201)

            # 9. Update Settings
            elif path in ["/api/school/settings", "/api/settings"]:
                updated = update_school_settings(body)
                return self.send_json_response(updated)

            # 10. Reset Demo Data
            elif path == "/api/school/reset-demo":
                populate_school_seed_data()
                return self.send_json_response({
                    "success": True,
                    "message": "Successfully refreshed Maharishi Vidya Mandir School dataset."
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
            if path.startswith("/api/leaves/") and path.endswith("/status"):
                leave_id = int(path.strip("/").split("/")[2])
                status = body.get("status", "approved")
                review_teacher_leave(leave_id, status, body.get("reviewer", "Principal"))
                return self.send_json_response({"success": True, "status": status})

            elif path.startswith("/api/payroll/") and path.endswith("/status"):
                payroll_id = int(path.strip("/").split("/")[2])
                status = body.get("status", "paid")
                update_teacher_payroll_status(payroll_id, status)
                return self.send_json_response({"success": True, "status": status})

            elif path.startswith("/api/teachers/"):
                staff_id = int(path.split("/")[-1])
                updated = update_teacher(staff_id, body)
                return self.send_json_response(updated)

            else:
                return self.send_json_response({"error": "Endpoint not found"}, 404)

        except Exception as e:
            return self.send_json_response({"error": str(e)}, 500)


def run_server(port=5000):
    init_db()
    conn = get_connection()
    count = conn.cursor().execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()
    if count == 0:
        populate_school_seed_data()

    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, UnifiedSchoolHTTPRequestHandler)
    print(f"============================================================")
    print(f"  UNIFIED SMART SCHOOL & FACULTY PAYROLL OS")
    print(f"  Live Server Running on: http://localhost:{port}")
    print(f"  - Master Principal Dashboard:  http://localhost:{port}/")
    print(f"  - High-Speed Gate Kiosk:       http://localhost:{port}/kiosk")
    print(f"  - Mobile Gate Scanner:         http://localhost:{port}/scan")
    print(f"  - Bus Conductor App:           http://localhost:{port}/bus")
    print(f"  - PVC Student ID Badges:       http://localhost:{port}/badges")
    print(f"  - Emergency WhatsApp Center:   http://localhost:{port}/broadcast")
    print(f"  - CBSE/SEBA Official Register: http://localhost:{port}/register")
    print(f"  - Teacher & Staff Portal:      http://localhost:{port}/portal")
    print(f"  - School B2B Pitch Deck:       http://localhost:{port}/pitch")
    print(f"============================================================")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    run_server(port)
