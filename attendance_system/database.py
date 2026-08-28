"""
SQLite Database Layer & Business Logic for Staff Attendance & Payroll System
"""

import sqlite3
import os
import json
import uuid
import hashlib
import time
from datetime import datetime, timedelta, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Company Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tagline TEXT,
        logo_url TEXT,
        currency_symbol TEXT DEFAULT '$',
        currency_code TEXT DEFAULT 'USD',
        timezone TEXT DEFAULT 'America/New_York',
        work_start_time TEXT DEFAULT '09:00',
        work_end_time TEXT DEFAULT '17:00',
        late_grace_minutes INTEGER DEFAULT 15,
        half_day_hours REAL DEFAULT 4.0,
        full_day_hours REAL DEFAULT 8.0,
        overtime_multiplier REAL DEFAULT 1.5,
        late_deduction_rate REAL DEFAULT 5.0,
        dynamic_qr_secret TEXT,
        qr_refresh_seconds INTEGER DEFAULT 20,
        geofence_enabled INTEGER DEFAULT 0,
        office_lat REAL DEFAULT 40.7128,
        office_lng REAL DEFAULT -74.0060,
        geofence_radius_meters INTEGER DEFAULT 200,
        updated_at TEXT
    )
    """)

    # 2. Departments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        manager_name TEXT,
        color TEXT DEFAULT '#3B82F6',
        created_at TEXT
    )
    """)

    # 3. Employees
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_code TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        department_id INTEGER,
        designation TEXT,
        salary_type TEXT DEFAULT 'monthly', -- 'monthly' or 'hourly'
        hourly_rate REAL DEFAULT 25.0,
        monthly_salary REAL DEFAULT 4500.0,
        pin_code TEXT DEFAULT '1234',
        qr_token TEXT UNIQUE NOT NULL,
        avatar_url TEXT,
        status TEXT DEFAULT 'active', -- 'active', 'on_leave', 'inactive'
        join_date TEXT,
        created_at TEXT,
        FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
    )
    """)

    # 4. Attendance Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        date TEXT NOT NULL, -- YYYY-MM-DD
        check_in_time TEXT, -- HH:MM:SS
        check_out_time TEXT, -- HH:MM:SS
        check_in_type TEXT DEFAULT 'kiosk_qr', -- 'kiosk_qr', 'mobile_scan', 'badge_scan', 'manual_pin', 'admin_override'
        check_out_type TEXT,
        total_hours REAL DEFAULT 0.0,
        regular_hours REAL DEFAULT 0.0,
        overtime_hours REAL DEFAULT 0.0,
        late_minutes INTEGER DEFAULT 0,
        early_leave_minutes INTEGER DEFAULT 0,
        status TEXT DEFAULT 'present', -- 'on_time', 'late', 'half_day', 'absent', 'on_leave', 'present', 'checked_out'
        notes TEXT,
        ip_address TEXT,
        location_lat REAL,
        location_lng REAL,
        created_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
        UNIQUE(employee_id, date)
    )
    """)

    # 5. Leave Requests
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL, -- 'vacation', 'sick', 'casual', 'unpaid', 'maternity'
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        total_days INTEGER DEFAULT 1,
        reason TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
        reviewed_by TEXT,
        reviewed_at TEXT,
        created_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
    )
    """)

    # 6. Payroll Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payroll_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_month TEXT NOT NULL, -- YYYY-MM
        employee_id INTEGER NOT NULL,
        total_days_worked INTEGER DEFAULT 0,
        total_regular_hours REAL DEFAULT 0.0,
        total_overtime_hours REAL DEFAULT 0.0,
        total_late_minutes INTEGER DEFAULT 0,
        base_salary_earned REAL DEFAULT 0.0,
        overtime_pay REAL DEFAULT 0.0,
        late_deductions REAL DEFAULT 0.0,
        bonus_allowance REAL DEFAULT 0.0,
        tax_deductions REAL DEFAULT 0.0,
        net_pay REAL DEFAULT 0.0,
        payment_status TEXT DEFAULT 'draft', -- 'draft', 'approved', 'paid'
        payment_date TEXT,
        payslip_number TEXT UNIQUE NOT NULL,
        notes TEXT,
        generated_at TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
        UNIQUE(employee_id, period_month)
    )
    """)

    # 7. Activity Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        details TEXT,
        user_agent TEXT,
        ip_address TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def log_activity(action, details="", user_agent="", ip_address=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activity_logs (action, details, user_agent, ip_address, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (action, details, user_agent, ip_address, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


# --- Company Settings ---
def get_company_settings():
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM company_settings WHERE id = 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "id": 1,
        "name": "Apex Innovations Inc.",
        "tagline": "Enterprise Workforce Solutions",
        "logo_url": "",
        "currency_symbol": "$",
        "currency_code": "USD",
        "timezone": "America/New_York",
        "work_start_time": "09:00",
        "work_end_time": "17:00",
        "late_grace_minutes": 15,
        "half_day_hours": 4.0,
        "full_day_hours": 8.0,
        "overtime_multiplier": 1.5,
        "late_deduction_rate": 5.0,
        "dynamic_qr_secret": "apex_secret_key_2026",
        "qr_refresh_seconds": 20,
        "geofence_enabled": 0,
        "office_lat": 40.7128,
        "office_lng": -74.0060,
        "geofence_radius_meters": 200
    }


def update_company_settings(data):
    conn = get_connection()
    cursor = conn.cursor()
    fields = [
        "name", "tagline", "logo_url", "currency_symbol", "currency_code", "timezone",
        "work_start_time", "work_end_time", "late_grace_minutes", "half_day_hours",
        "full_day_hours", "overtime_multiplier", "late_deduction_rate", "dynamic_qr_secret",
        "qr_refresh_seconds", "geofence_enabled", "office_lat", "office_lng", "geofence_radius_meters"
    ]
    updates = []
    values = []
    for f in fields:
        if f in data:
            updates.append(f"{f} = ?")
            values.append(data[f])

    if updates:
        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        query = f"UPDATE company_settings SET {', '.join(updates)}, updated_at = ? WHERE id = 1"
        cursor.execute(query, values)
        conn.commit()
    conn.close()
    return get_company_settings()


# --- Dynamic Kiosk QR Generation & Validation ---
def get_current_kiosk_qr_token():
    settings = get_company_settings()
    secret = settings.get("dynamic_qr_secret") or "apex_default_qr_secret"
    refresh_sec = settings.get("qr_refresh_seconds", 20)
    
    current_time_slot = int(time.time()) // refresh_sec
    time_remaining = refresh_sec - (int(time.time()) % refresh_sec)
    
    raw = f"{secret}:{current_time_slot}"
    token_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
    token = f"KIOSK-{token_hash}"
    
    return {
        "token": token,
        "time_slot": current_time_slot,
        "seconds_remaining": time_remaining,
        "refresh_interval": refresh_sec,
        "timestamp": datetime.now().isoformat()
    }


def validate_kiosk_qr_token(token):
    settings = get_company_settings()
    secret = settings.get("dynamic_qr_secret") or "apex_default_qr_secret"
    refresh_sec = settings.get("qr_refresh_seconds", 20)
    current_time_slot = int(time.time()) // refresh_sec

    # Accept current and immediately preceding time slot to account for clock skew/scan delays
    for slot in [current_time_slot, current_time_slot - 1]:
        raw = f"{secret}:{slot}"
        expected_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        expected_token = f"KIOSK-{expected_hash}"
        if token == expected_token:
            return True
    return False


# --- Departments ---
def list_departments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.*, COUNT(e.id) as employee_count
        FROM departments d
        LEFT JOIN employees e ON e.department_id = d.id AND e.status != 'inactive'
        GROUP BY d.id
        ORDER BY d.name ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def create_department(name, manager_name="", color="#3B82F6"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO departments (name, manager_name, color, created_at)
        VALUES (?, ?, ?, ?)
    """, (name, manager_name, color, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    dep_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return dep_id


# --- Employees ---
def list_employees(department_id=None, status=None, search=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT e.*, d.name as department_name, d.color as department_color
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE 1=1
    """
    params = []
    if department_id:
        query += " AND e.department_id = ?"
        params.append(department_id)
    if status:
        query += " AND e.status = ?"
        params.append(status)
    if search:
        query += " AND (e.first_name LIKE ? OR e.last_name LIKE ? OR e.email LIKE ? OR e.employee_code LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    query += " ORDER BY e.first_name ASC, e.last_name ASC"
    rows = [dict(r) for r in cursor.execute(query, params).fetchall()]
    conn.close()
    return rows


def get_employee(employee_id_or_code):
    conn = get_connection()
    cursor = conn.cursor()
    if isinstance(employee_id_or_code, int) or (isinstance(employee_id_or_code, str) and str(employee_id_or_code).isdigit()):
        row = cursor.execute("""
            SELECT e.*, d.name as department_name, d.color as department_color
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.id = ?
        """, (int(employee_id_or_code),)).fetchone()
    else:
        row = cursor.execute("""
            SELECT e.*, d.name as department_name, d.color as department_color
            FROM employees e
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.employee_code = ? OR e.qr_token = ? OR e.email = ?
        """, (str(employee_id_or_code), str(employee_id_or_code), str(employee_id_or_code))).fetchone()
    conn.close()
    return dict(row) if row else None


def create_employee(data):
    conn = get_connection()
    cursor = conn.cursor()

    # Generate employee code if not provided
    emp_code = data.get("employee_code")
    if not emp_code:
        count = cursor.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        emp_code = f"EMP-{(count + 101):03d}"

    # Generate unique QR token
    qr_token = data.get("qr_token") or f"BADGE-{uuid.uuid4().hex[:12].upper()}"

    cursor.execute("""
        INSERT INTO employees (
            employee_code, first_name, last_name, email, phone,
            department_id, designation, salary_type, hourly_rate,
            monthly_salary, pin_code, qr_token, avatar_url, status,
            join_date, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        emp_code,
        data.get("first_name", "").strip(),
        data.get("last_name", "").strip(),
        data.get("email", "").strip().lower(),
        data.get("phone", ""),
        data.get("department_id"),
        data.get("designation", "Staff Member"),
        data.get("salary_type", "monthly"),
        float(data.get("hourly_rate", 25.0)),
        float(data.get("monthly_salary", 4500.0)),
        data.get("pin_code", "1234"),
        qr_token,
        data.get("avatar_url", f"https://api.dicebear.com/7.x/avataaars/svg?seed={emp_code}"),
        data.get("status", "active"),
        data.get("join_date", date.today().strftime("%Y-%m-%d")),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_employee(new_id)


def update_employee(emp_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    fields = [
        "first_name", "last_name", "email", "phone", "department_id",
        "designation", "salary_type", "hourly_rate", "monthly_salary",
        "pin_code", "avatar_url", "status", "join_date"
    ]
    updates = []
    values = []
    for f in fields:
        if f in data:
            updates.append(f"{f} = ?")
            values.append(data[f])

    if updates:
        values.append(emp_id)
        query = f"UPDATE employees SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    conn.close()
    return get_employee(emp_id)


def delete_employee(emp_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE employees SET status = 'inactive' WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()
    return True


# --- Attendance Engine ---
def calculate_late_minutes(check_in_time_str, work_start_time_str, grace_minutes=15):
    try:
        t_in = datetime.strptime(check_in_time_str, "%H:%M:%S").time()
    except ValueError:
        t_in = datetime.strptime(check_in_time_str, "%H:%M").time()

    t_start = datetime.strptime(work_start_time_str, "%H:%M").time()
    
    in_minutes = t_in.hour * 60 + t_in.minute
    start_minutes = t_start.hour * 60 + t_start.minute + grace_minutes

    if in_minutes > start_minutes:
        return in_minutes - (t_start.hour * 60 + t_start.minute)
    return 0


def calculate_hours_and_overtime(check_in_time_str, check_out_time_str, full_day_hours=8.0, half_day_hours=4.0):
    try:
        dt_in = datetime.strptime(check_in_time_str, "%H:%M:%S")
    except ValueError:
        dt_in = datetime.strptime(check_in_time_str, "%H:%M")

    try:
        dt_out = datetime.strptime(check_out_time_str, "%H:%M:%S")
    except ValueError:
        dt_out = datetime.strptime(check_out_time_str, "%H:%M")

    delta_sec = (dt_out - dt_in).total_seconds()
    if delta_sec < 0:
        delta_sec = 0

    total_hours = round(delta_sec / 3600.0, 2)
    regular_hours = min(total_hours, full_day_hours)
    overtime_hours = round(max(0.0, total_hours - full_day_hours), 2)
    
    return total_hours, regular_hours, overtime_hours


def record_check_in(employee_id, check_in_type="kiosk_qr", custom_time=None, custom_date=None, notes=None, ip_address="", location_lat=None, location_lng=None):
    conn = get_connection()
    cursor = conn.cursor()
    settings = get_company_settings()

    target_date = custom_date or date.today().strftime("%Y-%m-%d")
    now_time = custom_time or datetime.now().strftime("%H:%M:%S")

    existing = cursor.execute("""
        SELECT * FROM attendance_records WHERE employee_id = ? AND date = ?
    """, (employee_id, target_date)).fetchone()

    late_min = calculate_late_minutes(now_time, settings.get("work_start_time", "09:00"), settings.get("late_grace_minutes", 15))
    status = "late" if late_min > 0 else "on_time"

    if existing:
        if existing["check_in_time"]:
            conn.close()
            return {"success": False, "message": "Employee already checked in today", "record": dict(existing)}
        cursor.execute("""
            UPDATE attendance_records
            SET check_in_time = ?, check_in_type = ?, late_minutes = ?, status = ?, notes = ?, ip_address = ?, location_lat = ?, location_lng = ?
            WHERE id = ?
        """, (now_time, check_in_type, late_min, status, notes, ip_address, location_lat, location_lng, existing["id"]))
        rec_id = existing["id"]
    else:
        cursor.execute("""
            INSERT INTO attendance_records (
                employee_id, date, check_in_time, check_in_type, late_minutes, status, notes, ip_address, location_lat, location_lng, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_id, target_date, now_time, check_in_type, late_min, status, notes, ip_address, location_lat, location_lng,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        rec_id = cursor.lastrowid

    conn.commit()
    updated_rec = cursor.execute("SELECT * FROM attendance_records WHERE id = ?", (rec_id,)).fetchone()
    emp = get_employee(employee_id)
    conn.close()

    log_activity("CHECK_IN", f"{emp['first_name']} {emp['last_name']} ({emp['employee_code']}) checked in at {now_time} [{status}]", ip_address=ip_address)

    return {
        "success": True,
        "action": "check_in",
        "employee": emp,
        "record": dict(updated_rec),
        "status": status,
        "late_minutes": late_min,
        "message": f"Welcome, {emp['first_name']}! Checked in at {now_time[:5]}." + (f" ({late_min}m late)" if late_min > 0 else " (On Time)")
    }


def record_check_out(employee_id, check_out_type="kiosk_qr", custom_time=None, custom_date=None, notes=None, ip_address="", location_lat=None, location_lng=None):
    conn = get_connection()
    cursor = conn.cursor()
    settings = get_company_settings()

    target_date = custom_date or date.today().strftime("%Y-%m-%d")
    now_time = custom_time or datetime.now().strftime("%H:%M:%S")

    existing = cursor.execute("""
        SELECT * FROM attendance_records WHERE employee_id = ? AND date = ?
    """, (employee_id, target_date)).fetchone()

    if not existing or not existing["check_in_time"]:
        conn.close()
        return {"success": False, "message": "No active check-in record found for today."}

    check_in_time = existing["check_in_time"]
    total_hours, regular_hours, overtime_hours = calculate_hours_and_overtime(
        check_in_time, now_time,
        full_day_hours=settings.get("full_day_hours", 8.0),
        half_day_hours=settings.get("half_day_hours", 4.0)
    )

    status = existing["status"]
    if total_hours < settings.get("half_day_hours", 4.0):
        status = "half_day"
    elif status not in ["late"]:
        status = "present"

    cursor.execute("""
        UPDATE attendance_records
        SET check_out_time = ?, check_out_type = ?, total_hours = ?, regular_hours = ?, overtime_hours = ?, status = ?, notes = COALESCE(?, notes)
        WHERE id = ?
    """, (now_time, check_out_type, total_hours, regular_hours, overtime_hours, status, notes, existing["id"]))

    conn.commit()
    updated_rec = cursor.execute("SELECT * FROM attendance_records WHERE id = ?", (existing["id"],)).fetchone()
    emp = get_employee(employee_id)
    conn.close()

    log_activity("CHECK_OUT", f"{emp['first_name']} {emp['last_name']} ({emp['employee_code']}) checked out at {now_time}. Total: {total_hours}h", ip_address=ip_address)

    return {
        "success": True,
        "action": "check_out",
        "employee": emp,
        "record": dict(updated_rec),
        "total_hours": total_hours,
        "overtime_hours": overtime_hours,
        "message": f"Goodbye, {emp['first_name']}! Checked out at {now_time[:5]}. Total time: {total_hours} hrs."
    }


def toggle_attendance_quick(identifier, method="badge_scan", ip_address="", location_lat=None, location_lng=None):
    emp = get_employee(identifier)
    if not emp:
        return {"success": False, "message": f"Invalid Employee Code / Badge token: '{identifier}'"}

    today_str = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    rec = cursor.execute("""
        SELECT * FROM attendance_records WHERE employee_id = ? AND date = ?
    """, (emp["id"], today_str)).fetchone()
    conn.close()

    if not rec or not rec["check_in_time"]:
        return record_check_in(emp["id"], check_in_type=method, ip_address=ip_address, location_lat=location_lat, location_lng=location_lng)
    elif not rec["check_out_time"]:
        return record_check_out(emp["id"], check_out_type=method, ip_address=ip_address, location_lat=location_lat, location_lng=location_lng)
    else:
        return {
            "success": True,
            "action": "already_completed",
            "employee": emp,
            "record": dict(rec),
            "message": f"{emp['first_name']} has already completed attendance today ({rec['check_in_time'][:5]} - {rec['check_out_time'][:5]}, {rec['total_hours']}h)."
        }


def get_today_attendance():
    today_str = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            e.id as employee_id,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.email,
            e.designation,
            e.avatar_url,
            d.name as department_name,
            d.color as department_color,
            a.id as attendance_id,
            a.date,
            a.check_in_time,
            a.check_out_time,
            a.check_in_type,
            a.check_out_type,
            a.total_hours,
            a.regular_hours,
            a.overtime_hours,
            a.late_minutes,
            COALESCE(a.status, CASE WHEN e.status = 'on_leave' THEN 'on_leave' ELSE 'absent' END) as attendance_status
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN attendance_records a ON e.id = a.employee_id AND a.date = ?
        WHERE e.status != 'inactive'
        ORDER BY 
            CASE 
                WHEN a.check_in_time IS NOT NULL AND a.check_out_time IS NULL THEN 1
                WHEN a.check_in_time IS NOT NULL THEN 2
                ELSE 3
            END,
            e.first_name ASC
    """, (today_str,))
    
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_attendance_history(start_date=None, end_date=None, department_id=None, employee_id=None, status=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            a.*,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.email,
            e.designation,
            e.avatar_url,
            d.name as department_name,
            d.color as department_color
        FROM attendance_records a
        JOIN employees e ON a.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND a.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND a.date <= ?"
        params.append(end_date)
    if department_id:
        query += " AND e.department_id = ?"
        params.append(department_id)
    if employee_id:
        query += " AND a.employee_id = ?"
        params.append(employee_id)
    if status:
        query += " AND a.status = ?"
        params.append(status)

    query += " ORDER BY a.date DESC, a.check_in_time DESC"
    rows = [dict(r) for r in cursor.execute(query, params).fetchall()]
    conn.close()
    return rows


def get_monthly_attendance_matrix(year_month=None):
    if not year_month:
        year_month = date.today().strftime("%Y-%m")
    
    year, month = map(int, year_month.split("-"))
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    num_days = (next_month - date(year, month, 1)).days

    conn = get_connection()
    cursor = conn.cursor()
    
    employees = [dict(r) for r in cursor.execute("""
        SELECT e.id, e.employee_code, e.first_name, e.last_name, e.designation, d.name as department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.status != 'inactive'
        ORDER BY e.first_name ASC
    """).fetchall()]

    start_date = f"{year_month}-01"
    end_date = f"{year_month}-{num_days:02d}"

    records = [dict(r) for r in cursor.execute("""
        SELECT employee_id, date, check_in_time, check_out_time, total_hours, status, late_minutes, overtime_hours
        FROM attendance_records
        WHERE date >= ? AND date <= ?
    """, (start_date, end_date)).fetchall()]
    conn.close()

    lookup = {}
    for r in records:
        day = int(r["date"].split("-")[2])
        lookup[(r["employee_id"], day)] = r

    result = []
    for emp in employees:
        days_data = {}
        total_present = 0
        total_late = 0
        total_hours = 0.0
        total_overtime = 0.0

        for d in range(1, num_days + 1):
            rec = lookup.get((emp["id"], d))
            if rec:
                days_data[d] = {
                    "status": rec["status"],
                    "hours": rec["total_hours"],
                    "in": rec["check_in_time"],
                    "out": rec["check_out_time"],
                    "late_min": rec["late_minutes"],
                    "ot": rec["overtime_hours"]
                }
                if rec["status"] in ["present", "on_time", "late", "half_day"]:
                    total_present += 1
                if rec["late_minutes"] > 0:
                    total_late += 1
                total_hours += rec["total_hours"] or 0
                total_overtime += rec["overtime_hours"] or 0
            else:
                cur_dt = date(year, month, d)
                is_weekend = cur_dt.weekday() >= 5
                days_data[d] = {
                    "status": "weekend" if is_weekend else "absent",
                    "hours": 0,
                    "in": None,
                    "out": None
                }

        result.append({
            "employee": emp,
            "days": days_data,
            "total_present": total_present,
            "total_late": total_late,
            "total_hours": round(total_hours, 1),
            "total_overtime": round(total_overtime, 1)
        })

    return {
        "year_month": year_month,
        "num_days": num_days,
        "matrix": result
    }


# --- Dashboard Stats & Charts ---
def get_dashboard_stats():
    today_str = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()

    total_employees = cursor.execute("SELECT COUNT(*) FROM employees WHERE status != 'inactive'").fetchone()[0]
    
    today_records = cursor.execute("""
        SELECT a.status, a.late_minutes, a.total_hours
        FROM attendance_records a
        JOIN employees e ON a.employee_id = e.id
        WHERE a.date = ? AND e.status != 'inactive'
    """, (today_str,)).fetchall()

    present_count = len(today_records)
    on_time_count = sum(1 for r in today_records if r["status"] == "on_time")
    late_count = sum(1 for r in today_records if r["status"] == "late" or (r["late_minutes"] and r["late_minutes"] > 0))
    
    leaves_today = cursor.execute("""
        SELECT COUNT(*) FROM leave_requests
        WHERE status = 'approved' AND start_date <= ? AND end_date >= ?
    """, (today_str, today_str)).fetchone()[0]

    absent_count = max(0, total_employees - present_count - leaves_today)
    total_hours_today = round(sum((r["total_hours"] or 0) for r in today_records), 1)

    punctuality_rate = round((on_time_count / present_count * 100) if present_count > 0 else 100, 1)

    recent_logs = [dict(r) for r in cursor.execute("""
        SELECT * FROM activity_logs ORDER BY id DESC LIMIT 8
    """).fetchall()]

    conn.close()
    return {
        "total_employees": total_employees,
        "present_today": present_count,
        "on_time_today": on_time_count,
        "late_today": late_count,
        "absent_today": absent_count,
        "on_leave_today": leaves_today,
        "punctuality_rate": punctuality_rate,
        "total_hours_today": total_hours_today,
        "recent_logs": recent_logs
    }


def get_chart_data():
    conn = get_connection()
    cursor = conn.cursor()

    today = date.today()
    trend_labels = []
    trend_present = []
    trend_late = []
    trend_absent = []

    total_employees = cursor.execute("SELECT COUNT(*) FROM employees WHERE status != 'inactive'").fetchone()[0] or 1

    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        day_label = d.strftime("%a %d")
        trend_labels.append(day_label)

        records = cursor.execute("SELECT status, late_minutes FROM attendance_records WHERE date = ?", (d_str,)).fetchall()
        p = len(records)
        l = sum(1 for r in records if r["status"] == "late" or (r["late_minutes"] and r["late_minutes"] > 0))
        if d.weekday() >= 5:
            ab = 0
        else:
            ab = max(0, total_employees - p)

        trend_present.append(p)
        trend_late.append(l)
        trend_absent.append(ab)

    dep_rows = cursor.execute("""
        SELECT d.name, COUNT(e.id) as staff_count,
               SUM(CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END) as present_count
        FROM departments d
        LEFT JOIN employees e ON e.department_id = d.id AND e.status != 'inactive'
        LEFT JOIN attendance_records a ON a.employee_id = e.id AND a.date = ?
        GROUP BY d.id
    """, (today.strftime("%Y-%m-%d"),)).fetchall()

    dep_labels = [r["name"] for r in dep_rows]
    dep_present = [r["present_count"] for r in dep_rows]
    dep_staff = [r["staff_count"] for r in dep_rows]

    conn.close()
    return {
        "trend": {
            "labels": trend_labels,
            "present": trend_present,
            "late": trend_late,
            "absent": trend_absent
        },
        "departments": {
            "labels": dep_labels,
            "present": dep_present,
            "staff": dep_staff
        }
    }


# --- Leave Requests ---
def list_leave_requests(status=None, employee_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT l.*, e.employee_code, e.first_name, e.last_name, e.designation, d.name as department_name
        FROM leave_requests l
        JOIN employees e ON l.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND l.status = ?"
        params.append(status)
    if employee_id:
        query += " AND l.employee_id = ?"
        params.append(employee_id)

    query += " ORDER BY l.id DESC"
    rows = [dict(r) for r in cursor.execute(query, params).fetchall()]
    conn.close()
    return rows


def submit_leave_request(employee_id, leave_type, start_date_str, end_date_str, reason=""):
    conn = get_connection()
    cursor = conn.cursor()

    dt_start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    dt_end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    total_days = max(1, (dt_end - dt_start).days + 1)

    cursor.execute("""
        INSERT INTO leave_requests (
            employee_id, leave_type, start_date, end_date, total_days, reason, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
    """, (employee_id, leave_type, start_date_str, end_date_str, total_days, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    emp = get_employee(employee_id)
    log_activity("LEAVE_REQUEST", f"{emp['first_name']} {emp['last_name']} requested {total_days} days {leave_type} leave ({start_date_str} to {end_date_str})")
    return new_id


def review_leave_request(leave_id, status, reviewer_name="Admin"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE leave_requests
        SET status = ?, reviewed_by = ?, reviewed_at = ?
        WHERE id = ?
    """, (status, reviewer_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), leave_id))
    
    leave = cursor.execute("SELECT * FROM leave_requests WHERE id = ?", (leave_id)).fetchone() if False else cursor.execute("SELECT * FROM leave_requests WHERE id = ?", (leave_id,)).fetchone()
    if leave and status == "approved":
        today_str = date.today().strftime("%Y-%m-%d")
        if leave["start_date"] <= today_str <= leave["end_date"]:
            cursor.execute("UPDATE employees SET status = 'on_leave' WHERE id = ?", (leave["employee_id"],))

    conn.commit()
    conn.close()
    return True


# --- Payroll Engine ---
def generate_monthly_payroll(year_month=None):
    if not year_month:
        year_month = date.today().strftime("%Y-%m")

    settings = get_company_settings()
    ot_mult = settings.get("overtime_multiplier", 1.5)
    late_ded_rate = settings.get("late_deduction_rate", 5.0)

    conn = get_connection()
    cursor = conn.cursor()

    employees = [dict(r) for r in cursor.execute("""
        SELECT e.*, d.name as department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.status != 'inactive'
    """).fetchall()]

    start_date = f"{year_month}-01"
    end_date = f"{year_month}-31"

    generated_records = []

    for emp in employees:
        stats = cursor.execute("""
            SELECT 
                COUNT(*) as days_worked,
                SUM(regular_hours) as reg_hours,
                SUM(overtime_hours) as ot_hours,
                SUM(late_minutes) as total_late_min
            FROM attendance_records
            WHERE employee_id = ? AND date >= ? AND date <= ? AND (check_in_time IS NOT NULL OR total_hours > 0)
        """, (emp["id"], start_date, end_date)).fetchone()

        days_worked = stats["days_worked"] or 0
        reg_hours = round(stats["reg_hours"] or 0.0, 1)
        ot_hours = round(stats["ot_hours"] or 0.0, 1)
        late_min = stats["total_late_min"] or 0

        if emp["salary_type"] == "hourly":
            hourly = emp["hourly_rate"]
            base_earned = round(reg_hours * hourly, 2)
            ot_pay = round(ot_hours * (hourly * ot_mult), 2)
        else:
            base_salary = emp["monthly_salary"]
            standard_days = 22
            if days_worked >= 18:
                base_earned = base_salary
            else:
                base_earned = round((base_salary / standard_days) * max(1, days_worked), 2)
            
            equiv_hourly = base_salary / (standard_days * 8.0)
            ot_pay = round(ot_hours * (equiv_hourly * ot_mult), 2)

        late_deductions = round((late_min // 15) * late_ded_rate, 2)
        bonus_allowance = 100.0 if days_worked >= 20 else 50.0
        gross_pay = base_earned + ot_pay + bonus_allowance
        tax_deductions = round(gross_pay * 0.05, 2)
        net_pay = round(gross_pay - late_deductions - tax_deductions, 2)

        payslip_num = f"PAY-{year_month.replace('-', '')}-{emp['employee_code']}"

        cursor.execute("""
            INSERT INTO payroll_records (
                period_month, employee_id, total_days_worked, total_regular_hours,
                total_overtime_hours, total_late_minutes, base_salary_earned,
                overtime_pay, late_deductions, bonus_allowance, tax_deductions,
                net_pay, payment_status, payslip_number, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)
            ON CONFLICT(employee_id, period_month) DO UPDATE SET
                total_days_worked = excluded.total_days_worked,
                total_regular_hours = excluded.total_regular_hours,
                total_overtime_hours = excluded.total_overtime_hours,
                total_late_minutes = excluded.total_late_minutes,
                base_salary_earned = excluded.base_salary_earned,
                overtime_pay = excluded.overtime_pay,
                late_deductions = excluded.late_deductions,
                bonus_allowance = excluded.bonus_allowance,
                tax_deductions = excluded.tax_deductions,
                net_pay = excluded.net_pay,
                generated_at = excluded.generated_at
        """, (
            year_month, emp["id"], days_worked, reg_hours, ot_hours, late_min,
            base_earned, ot_pay, late_deductions, bonus_allowance, tax_deductions,
            net_pay, payslip_num, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        generated_records.append(payslip_num)

    conn.commit()
    conn.close()

    log_activity("PAYROLL_GENERATED", f"Calculated payroll for {len(generated_records)} staff for period {year_month}")
    return get_payroll_summary(year_month)


def get_payroll_summary(year_month=None):
    if not year_month:
        year_month = date.today().strftime("%Y-%m")

    conn = get_connection()
    cursor = conn.cursor()

    rows = [dict(r) for r in cursor.execute("""
        SELECT 
            p.*,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.email,
            e.designation,
            e.salary_type,
            e.hourly_rate,
            e.monthly_salary,
            e.avatar_url,
            d.name as department_name
        FROM payroll_records p
        JOIN employees e ON p.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE p.period_month = ?
        ORDER BY e.first_name ASC
    """, (year_month,)).fetchall()]

    conn.close()

    total_net = sum(r["net_pay"] for r in rows)
    total_ot = sum(r["overtime_pay"] for r in rows)
    total_deductions = sum(r["late_deductions"] + r["tax_deductions"] for r in rows)

    return {
        "period_month": year_month,
        "count": len(rows),
        "total_net_payout": round(total_net, 2),
        "total_overtime_payout": round(total_ot, 2),
        "total_deductions": round(total_deductions, 2),
        "records": rows
    }


def get_payslip(payslip_id_or_num):
    conn = get_connection()
    cursor = conn.cursor()

    if isinstance(payslip_id_or_num, int) or (isinstance(payslip_id_or_num, str) and str(payslip_id_or_num).isdigit()):
        row = cursor.execute("""
            SELECT p.*, e.employee_code, e.first_name, e.last_name, e.email, e.phone, e.designation, e.salary_type, e.hourly_rate, e.monthly_salary, e.join_date, d.name as department_name
            FROM payroll_records p
            JOIN employees e ON p.employee_id = e.id
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE p.id = ?
        """, (int(payslip_id_or_num),)).fetchone()
    else:
        row = cursor.execute("""
            SELECT p.*, e.employee_code, e.first_name, e.last_name, e.email, e.phone, e.designation, e.salary_type, e.hourly_rate, e.monthly_salary, e.join_date, d.name as department_name
            FROM payroll_records p
            JOIN employees e ON p.employee_id = e.id
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE p.payslip_number = ?
        """, (str(payslip_id_or_num),)).fetchone()

    conn.close()
    if not row:
        return None

    settings = get_company_settings()
    return {
        "company": settings,
        "payslip": dict(row)
    }


def update_payroll_status(payroll_id, status, payment_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    pay_date = payment_date or date.today().strftime("%Y-%m-%d")
    cursor.execute("""
        UPDATE payroll_records
        SET payment_status = ?, payment_date = ?
        WHERE id = ?
    """, (status, pay_date if status == "paid" else None, payroll_id))
    conn.commit()
    conn.close()
    return True
