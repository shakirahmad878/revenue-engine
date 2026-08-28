"""
SQLite Database Layer for Enterprise School Attendance, Safety & Safety OS
Dual-Track Architecture: Students & Parent WhatsApp Alerts + Teachers & Staff Punctuality & Payroll
"""

import sqlite3
import os
import json
import uuid
import hashlib
import time
from datetime import datetime, timedelta, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "school_attendance.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. School Settings & Board Affiliation
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS school_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tagline TEXT,
        affiliation_board TEXT DEFAULT 'CBSE',
        affiliation_no TEXT DEFAULT 'CBSE/AFF/AS/2026/89401',
        school_code TEXT DEFAULT 'MVM-GUW-01',
        logo_url TEXT,
        principal_name TEXT DEFAULT 'Dr. S. K. Mahanta',
        principal_signature TEXT DEFAULT 'Dr. S. K. Mahanta, M.Sc, Ph.D, B.Ed',
        city TEXT DEFAULT 'Guwahati, Assam',
        currency_symbol TEXT DEFAULT '₹',
        gate_open_time TEXT DEFAULT '07:30',
        school_start_time TEXT DEFAULT '08:00',
        morning_strength_cutoff TEXT DEFAULT '08:15',
        absence_broadcast_time TEXT DEFAULT '08:30',
        gate_close_time TEXT DEFAULT '14:30',
        late_grace_minutes INTEGER DEFAULT 10,
        preferred_language TEXT DEFAULT 'en',
        whatsapp_gateway_status TEXT DEFAULT 'active_connected',
        dynamic_qr_secret TEXT DEFAULT 'mvm_assam_secret_2026',
        qr_refresh_seconds INTEGER DEFAULT 20,
        updated_at TEXT
    )
    """)

    # 2. Classes & Sections
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grade TEXT NOT NULL,
        section TEXT NOT NULL,
        class_teacher_name TEXT,
        room_no TEXT,
        capacity INTEGER DEFAULT 40,
        created_at TEXT,
        UNIQUE(grade, section)
    )
    """)

    # 3. Bus Routes & Transport
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bus_routes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_no TEXT UNIQUE NOT NULL,
        route_name TEXT NOT NULL,
        driver_name TEXT,
        driver_phone TEXT,
        conductor_name TEXT,
        conductor_phone TEXT,
        bus_number TEXT,
        created_at TEXT
    )
    """)

    # 4. Students
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admission_no TEXT UNIQUE NOT NULL,
        roll_no INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        student_name TEXT NOT NULL,
        gender TEXT DEFAULT 'Male',
        dob TEXT,
        blood_group TEXT DEFAULT 'O+',
        parent_guardian_name TEXT NOT NULL,
        parent_whatsapp_phone TEXT NOT NULL,
        emergency_phone TEXT,
        address TEXT,
        bus_route_no TEXT DEFAULT 'Self Transport',
        photo_url TEXT,
        qr_token TEXT UNIQUE NOT NULL,
        rfid_card_id TEXT UNIQUE,
        status TEXT DEFAULT 'active',
        created_at TEXT,
        FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
    )
    """)

    # 5. Student Attendance Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        gate_in_time TEXT,
        gate_out_time TEXT,
        bus_board_time TEXT,
        bus_drop_time TEXT,
        status TEXT DEFAULT 'present',
        late_minutes INTEGER DEFAULT 0,
        whatsapp_in_sent INTEGER DEFAULT 0,
        whatsapp_out_sent INTEGER DEFAULT 0,
        whatsapp_absence_sent INTEGER DEFAULT 0,
        scanned_by TEXT DEFAULT 'Main Gate Kiosk Laser',
        notes TEXT,
        created_at TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        UNIQUE(student_id, date)
    )
    """)

    # 6. Notification Logs (Live WhatsApp & SMS Deliveries)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        recipient_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        channel TEXT DEFAULT 'WhatsApp',
        notification_type TEXT NOT NULL,
        message_text TEXT NOT NULL,
        status TEXT DEFAULT 'Delivered',
        timestamp TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
    )
    """)

    # 7. Emergency Broadcasts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emergency_broadcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        target_audience TEXT DEFAULT 'all_parents',
        class_id INTEGER,
        bus_route_no TEXT,
        message_text TEXT NOT NULL,
        total_recipients INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Delivered',
        sent_at TEXT
    )
    """)

    # 8. Teachers & Staff Directory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers_staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_code TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        designation TEXT NOT NULL,
        subject_department TEXT,
        monthly_salary REAL DEFAULT 55000.0,
        pin_code TEXT DEFAULT '1234',
        qr_token TEXT UNIQUE NOT NULL,
        avatar_url TEXT,
        status TEXT DEFAULT 'active',
        join_date TEXT,
        created_at TEXT
    )
    """)

    # 9. Staff Attendance
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        check_in_time TEXT,
        check_out_time TEXT,
        total_hours REAL DEFAULT 0.0,
        status TEXT DEFAULT 'present',
        late_minutes INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY (staff_id) REFERENCES teachers_staff(id) ON DELETE CASCADE,
        UNIQUE(staff_id, date)
    )
    """)

    # 10. Staff Leave Requests
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff_leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL, -- 'Casual', 'Medical', 'Academic', 'Earned'
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        total_days INTEGER DEFAULT 1,
        reason TEXT,
        status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
        reviewed_by TEXT,
        reviewed_at TEXT,
        created_at TEXT,
        FOREIGN KEY (staff_id) REFERENCES teachers_staff(id) ON DELETE CASCADE
    )
    """)

    # 11. Staff Payroll Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payroll_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_month TEXT NOT NULL,
        staff_id INTEGER NOT NULL,
        total_days_worked INTEGER DEFAULT 0,
        total_regular_hours REAL DEFAULT 0.0,
        total_late_minutes INTEGER DEFAULT 0,
        base_salary_earned REAL DEFAULT 0.0,
        late_deductions REAL DEFAULT 0.0,
        bonus_allowance REAL DEFAULT 0.0,
        tax_deductions REAL DEFAULT 0.0,
        net_pay REAL DEFAULT 0.0,
        payment_status TEXT DEFAULT 'draft',
        payment_date TEXT,
        payslip_number TEXT UNIQUE NOT NULL,
        generated_at TEXT,
        FOREIGN KEY (staff_id) REFERENCES teachers_staff(id) ON DELETE CASCADE,
        UNIQUE(staff_id, period_month)
    )
    """)

    conn.commit()
    conn.close()


# --- School Settings ---
def get_school_settings():
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM school_settings WHERE id = 1").fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "id": 1,
        "name": "Maharishi Vidya Mandir Public School",
        "tagline": "Excellence in Education, Character & Safety",
        "affiliation_board": "CBSE, New Delhi",
        "affiliation_no": "CBSE/AFF/AS/2026/89401",
        "school_code": "MVM-GUW-01",
        "logo_url": "",
        "principal_name": "Dr. S. K. Mahanta",
        "principal_signature": "Dr. S. K. Mahanta, M.Sc, Ph.D, B.Ed",
        "city": "Guwahati, Assam",
        "currency_symbol": "₹",
        "gate_open_time": "07:30",
        "school_start_time": "08:00",
        "morning_strength_cutoff": "08:15",
        "absence_broadcast_time": "08:30",
        "gate_close_time": "14:30",
        "late_grace_minutes": 10,
        "preferred_language": "en",
        "whatsapp_gateway_status": "active_connected",
        "dynamic_qr_secret": "mvm_assam_secret_2026",
        "qr_refresh_seconds": 20
    }


def update_school_settings(data):
    conn = get_connection()
    cursor = conn.cursor()
    fields = [
        "name", "tagline", "affiliation_board", "affiliation_no", "school_code",
        "logo_url", "principal_name", "principal_signature", "city", "currency_symbol",
        "gate_open_time", "school_start_time", "morning_strength_cutoff", "absence_broadcast_time",
        "gate_close_time", "late_grace_minutes", "preferred_language", "whatsapp_gateway_status",
        "dynamic_qr_secret", "qr_refresh_seconds"
    ]
    updates = []
    values = []
    for f in fields:
        if f in data:
            updates.append(f"{f} = ?")
            values.append(data[f])

    if updates:
        values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        query = f"UPDATE school_settings SET {', '.join(updates)}, updated_at = ? WHERE id = 1"
        cursor.execute(query, values)
        conn.commit()
    conn.close()
    return get_school_settings()


# --- Classes & Bus Routes ---
def list_classes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, COUNT(s.id) as total_students
        FROM classes c
        LEFT JOIN students s ON s.class_id = c.id AND s.status = 'active'
        GROUP BY c.id
        ORDER BY c.grade ASC, c.section ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def list_bus_routes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, COUNT(s.id) as student_count
        FROM bus_routes b
        LEFT JOIN students s ON s.bus_route_no = b.route_no AND s.status = 'active'
        GROUP BY b.id
        ORDER BY b.route_no ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# --- Students Directory & Helpers ---
def list_students(class_id=None, bus_route_no=None, search=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT s.*, c.grade as class_grade, c.section, c.class_teacher_name
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE s.status = 'active'
    """
    params = []
    if class_id:
        query += " AND s.class_id = ?"
        params.append(class_id)
    if bus_route_no:
        query += " AND s.bus_route_no = ?"
        params.append(bus_route_no)
    if search:
        query += " AND (s.student_name LIKE ? OR s.admission_no LIKE ? OR s.parent_guardian_name LIKE ? OR s.parent_whatsapp_phone LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    query += " ORDER BY c.grade ASC, c.section ASC, s.roll_no ASC"
    rows = [dict(r) for r in cursor.execute(query, params).fetchall()]
    conn.close()
    return rows


def get_student(identifier):
    conn = get_connection()
    cursor = conn.cursor()
    if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
        row = cursor.execute("""
            SELECT s.*, c.grade as class_grade, c.section, c.class_teacher_name
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.id = ?
        """, (int(identifier),)).fetchone()
    else:
        ident_str = str(identifier).strip()
        row = cursor.execute("""
            SELECT s.*, c.grade as class_grade, c.section, c.class_teacher_name
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.admission_no = ? OR s.qr_token = ? OR s.rfid_card_id = ?
        """, (ident_str, ident_str, ident_str)).fetchone()
    conn.close()
    return dict(row) if row else None


# --- Principal's 8:15 AM Morning Strength Dashboard ---
def get_morning_strength_report(target_date=None):
    if not target_date:
        target_date = date.today().strftime("%Y-%m-%d")

    settings = get_school_settings()
    conn = get_connection()
    cursor = conn.cursor()

    total_students = cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'active'").fetchone()[0]
    
    today_records = cursor.execute("""
        SELECT a.status, a.late_minutes, a.gate_in_time
        FROM student_attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ? AND s.status = 'active' AND a.gate_in_time IS NOT NULL
    """, (target_date,)).fetchall()

    present_count = len(today_records)
    late_count = sum(1 for r in today_records if r["status"] == "late" or (r["late_minutes"] and r["late_minutes"] > 0))
    on_time_count = present_count - late_count
    absent_count = max(0, total_students - present_count)
    strength_pct = round((present_count / total_students * 100) if total_students > 0 else 100, 1)

    total_staff = cursor.execute("SELECT COUNT(*) FROM teachers_staff WHERE status = 'active'").fetchone()[0]
    staff_present = cursor.execute("SELECT COUNT(*) FROM staff_attendance WHERE date = ? AND check_in_time IS NOT NULL", (target_date,)).fetchone()[0]

    classes = cursor.execute("""
        SELECT c.id, c.grade, c.section, c.class_teacher_name, c.room_no,
               COUNT(s.id) as enrolled,
               SUM(CASE WHEN a.gate_in_time IS NOT NULL THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN a.status = 'late' OR a.late_minutes > 0 THEN 1 ELSE 0 END) as late
        FROM classes c
        LEFT JOIN students s ON s.class_id = c.id AND s.status = 'active'
        LEFT JOIN student_attendance a ON a.student_id = s.id AND a.date = ?
        GROUP BY c.id
        ORDER BY c.grade ASC, c.section ASC
    """, (target_date,)).fetchall()

    class_breakdown = []
    for cl in classes:
        enrolled = cl["enrolled"] or 0
        present = cl["present"] or 0
        late = cl["late"] or 0
        absent = max(0, enrolled - present)
        pct = round((present / enrolled * 100) if enrolled > 0 else 100, 1)
        class_breakdown.append({
            "class_id": cl["id"],
            "class_name": f"{cl['grade']}-{cl['section']}",
            "grade": cl["grade"],
            "section": cl["section"],
            "class_teacher": cl["class_teacher_name"],
            "room_no": cl["room_no"],
            "enrolled": enrolled,
            "present": present,
            "late": late,
            "absent": absent,
            "attendance_rate": pct
        })

    recent_deliveries = [dict(r) for r in cursor.execute("""
        SELECT n.*, s.student_name, s.photo_url, c.grade as class_grade, c.section
        FROM notification_logs n
        LEFT JOIN students s ON n.student_id = s.id
        LEFT JOIN classes c ON s.class_id = c.id
        ORDER BY n.id DESC LIMIT 10
    """).fetchall()]

    conn.close()

    return {
        "date": target_date,
        "school": settings,
        "summary": {
            "total_students": total_students,
            "present_students": present_count,
            "on_time_students": on_time_count,
            "late_students": late_count,
            "absent_students": absent_count,
            "strength_percentage": strength_pct,
            "total_staff": total_staff,
            "staff_present": staff_present
        },
        "classes": class_breakdown,
        "recent_alerts": recent_deliveries
    }


# --- High-Speed Gate Scan Engine (1.2s Throughput) ---
def record_student_gate_scan(identifier, scan_mode="auto", scanned_by="Main Gate Kiosk Laser"):
    student = get_student(identifier)
    if not student:
        return {"success": False, "message": f"Student ID / Badge not recognized: '{identifier}'"}

    settings = get_school_settings()
    today_str = date.today().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute("""
        SELECT * FROM student_attendance WHERE student_id = ? AND date = ?
    """, (student["id"], today_str)).fetchone()

    try:
        from notifier import dispatch_parent_notification
    except ImportError:
        from attendance_system.notifier import dispatch_parent_notification

    if not existing or not existing["gate_in_time"]:
        start_time_str = settings.get("school_start_time", "08:00")
        grace_min = settings.get("late_grace_minutes", 10)

        t_in = datetime.strptime(now_time, "%H:%M:%S").time()
        t_start = datetime.strptime(start_time_str, "%H:%M").time()
        in_m = t_in.hour * 60 + t_in.minute
        start_m = t_start.hour * 60 + t_start.minute + grace_min

        late_min = max(0, in_m - (t_start.hour * 60 + t_start.minute)) if in_m > start_m else 0
        status = "late" if late_min > 0 else "present"

        if existing:
            cursor.execute("""
                UPDATE student_attendance
                SET gate_in_time = ?, status = ?, late_minutes = ?, scanned_by = ?, whatsapp_in_sent = 1
                WHERE id = ?
            """, (now_time, status, late_min, scanned_by, existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO student_attendance (
                    student_id, date, gate_in_time, status, late_minutes, scanned_by, whatsapp_in_sent, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?)
            """, (student["id"], today_str, now_time, status, late_min, scanned_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()

        notif_type = "late" if late_min > 0 else "arrival"
        notif_res = dispatch_parent_notification(
            conn, student, notif_type,
            custom_params={"late_minutes": late_min},
            school_settings=settings,
            lang=settings.get("preferred_language", "en")
        )

        conn.close()

        return {
            "success": True,
            "action": "gate_in",
            "student": student,
            "status": status,
            "late_minutes": late_min,
            "time": now_time[:5],
            "notification": notif_res,
            "message": f"Welcome, {student['student_name']}! ({student['class_grade']}-{student['section']}) Checked in at {now_time[:5]}." + (f" [{late_min}m Late]" if late_min > 0 else " [On Time]")
        }

    elif not existing["gate_out_time"]:
        cursor.execute("""
            UPDATE student_attendance
            SET gate_out_time = ?, whatsapp_out_sent = 1
            WHERE id = ?
        """, (now_time, existing["id"]))
        conn.commit()

        notif_res = dispatch_parent_notification(
            conn, student, "departure",
            school_settings=settings,
            lang=settings.get("preferred_language", "en")
        )

        conn.close()

        return {
            "success": True,
            "action": "gate_out",
            "student": student,
            "status": "checked_out",
            "time": now_time[:5],
            "notification": notif_res,
            "message": f"Goodbye, {student['student_name']}! Campus exit recorded at {now_time[:5]}."
        }

    else:
        conn.close()
        return {
            "success": True,
            "action": "already_completed",
            "student": student,
            "message": f"{student['student_name']} has completed Gate In ({existing['gate_in_time'][:5]}) and Gate Out ({existing['gate_out_time'][:5]}) today."
        }


# --- School Bus Boarding Scan ---
def record_bus_scan(identifier, bus_route_no="Route #4", scan_type="board", conductor_name="Bus Conductor"):
    student = get_student(identifier)
    if not student:
        return {"success": False, "message": f"Student not found: '{identifier}'"}

    settings = get_school_settings()
    today_str = date.today().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute("""
        SELECT * FROM student_attendance WHERE student_id = ? AND date = ?
    """, (student["id"], today_str)).fetchone()

    if not existing:
        cursor.execute("""
            INSERT INTO student_attendance (
                student_id, date, bus_board_time, created_at
            ) VALUES (?, ?, ?, ?)
        """, (student["id"], today_str, now_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    else:
        field = "bus_board_time" if scan_type == "board" else "bus_drop_time"
        cursor.execute(f"UPDATE student_attendance SET {field} = ? WHERE id = ?", (now_time, existing["id"]))

    conn.commit()

    try:
        from notifier import dispatch_parent_notification
    except ImportError:
        from attendance_system.notifier import dispatch_parent_notification

    notif_type = "bus_board" if scan_type == "board" else "bus_drop"
    notif_res = dispatch_parent_notification(
        conn, student, notif_type,
        custom_params={"bus_route": bus_route_no},
        school_settings=settings,
        lang=settings.get("preferred_language", "en")
    )

    conn.close()

    return {
        "success": True,
        "action": f"bus_{scan_type}",
        "student": student,
        "time": now_time[:5],
        "notification": notif_res,
        "message": f"{student['student_name']} {scan_type}ed Bus {bus_route_no} at {now_time[:5]}."
    }


# --- 8:30 AM Absence Broadcast ---
def send_830_absence_broadcast(target_date=None):
    if not target_date:
        target_date = date.today().strftime("%Y-%m-%d")

    settings = get_school_settings()
    conn = get_connection()
    cursor = conn.cursor()

    absent_students = cursor.execute("""
        SELECT s.*, c.grade as class_grade, c.section
        FROM students s
        JOIN classes c ON s.class_id = c.id
        LEFT JOIN student_attendance a ON a.student_id = s.id AND a.date = ?
        WHERE s.status = 'active' AND (a.gate_in_time IS NULL OR a.id IS NULL)
    """, (target_date,)).fetchall()

    try:
        from notifier import dispatch_parent_notification
    except ImportError:
        from attendance_system.notifier import dispatch_parent_notification

    dispatched = []
    for s_row in absent_students:
        s = dict(s_row)
        cursor.execute("""
            INSERT INTO student_attendance (
                student_id, date, status, whatsapp_absence_sent, created_at
            ) VALUES (?, ?, 'absent', 1, ?)
            ON CONFLICT(student_id, date) DO UPDATE SET
                status = 'absent', whatsapp_absence_sent = 1
        """, (s["id"], target_date, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

        dispatch_parent_notification(
            conn, s, "absence_830",
            school_settings=settings,
            lang=settings.get("preferred_language", "en")
        )
        dispatched.append({"student_id": s["id"], "name": s["student_name"], "phone": s["parent_whatsapp_phone"], "status": "Delivered"})

    conn.close()

    return {
        "success": True,
        "date": target_date,
        "total_absent": len(absent_students),
        "dispatched_count": len(dispatched),
        "recipients": dispatched
    }


# --- Emergency Broadcast ---
def send_emergency_broadcast(title, message_text, target="all_parents", class_id=None, bus_route_no=None):
    settings = get_school_settings()
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.*, c.grade as class_grade, c.section
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE s.status = 'active'
    """
    params = []
    if target == "class_wise" and class_id:
        query += " AND s.class_id = ?"
        params.append(class_id)
    elif target == "bus_route" and bus_route_no:
        query += " AND s.bus_route_no = ?"
        params.append(bus_route_no)

    students = [dict(r) for r in cursor.execute(query, params).fetchall()]

    try:
        from notifier import dispatch_parent_notification
    except ImportError:
        from attendance_system.notifier import dispatch_parent_notification

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for s in students:
        dispatch_parent_notification(
            conn, s, "emergency",
            custom_params={"message": message_text},
            school_settings=settings,
            lang=settings.get("preferred_language", "en")
        )

    cursor.execute("""
        INSERT INTO emergency_broadcasts (
            title, target_audience, class_id, bus_route_no, message_text, total_recipients, status, sent_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'Delivered', ?)
    """, (title, target, class_id, bus_route_no, message_text, len(students), now_str))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "title": title,
        "total_delivered": len(students),
        "sent_at": now_str
    }


# --- CBSE / SEBA Monthly Register ---
def get_cbse_seba_monthly_register(year_month=None, class_id=None):
    if not year_month:
        year_month = date.today().strftime("%Y-%m")

    year, month = map(int, year_month.split("-"))
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    num_days = (next_month - date(year, month, 1)).days

    settings = get_school_settings()
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.*, c.grade as class_grade, c.section, c.class_teacher_name
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE s.status = 'active'
    """
    params = []
    if class_id:
        query += " AND s.class_id = ?"
        params.append(class_id)

    query += " ORDER BY c.grade ASC, c.section ASC, s.roll_no ASC"
    students = [dict(r) for r in cursor.execute(query, params).fetchall()]

    start_date = f"{year_month}-01"
    end_date = f"{year_month}-{num_days:02d}"

    records = [dict(r) for r in cursor.execute("""
        SELECT student_id, date, gate_in_time, status, late_minutes
        FROM student_attendance
        WHERE date >= ? AND date <= ?
    """, (start_date, end_date)).fetchall()]

    conn.close()

    lookup = {}
    for r in records:
        day = int(r["date"].split("-")[2])
        lookup[(r["student_id"], day)] = r

    total_working_days = 0
    day_headers = {}
    for d in range(1, num_days + 1):
        cur_dt = date(year, month, d)
        is_sunday = cur_dt.weekday() == 6
        if not is_sunday:
            total_working_days += 1
        day_headers[d] = {
            "day": d,
            "weekday": cur_dt.strftime("%a"),
            "is_holiday": is_sunday
        }

    matrix = []
    for s in students:
        days_data = {}
        present_count = 0
        late_count = 0
        absent_count = 0

        for d in range(1, num_days + 1):
            cur_dt = date(year, month, d)
            is_sunday = cur_dt.weekday() == 6

            if is_sunday:
                days_data[d] = {"marker": "SUN", "color": "text-gray-400 bg-slate-800/40"}
                continue

            rec = lookup.get((s["id"], d))
            if rec and rec["gate_in_time"]:
                if rec["status"] == "late" or rec["late_minutes"] > 0:
                    days_data[d] = {"marker": "L", "color": "text-amber-400 bg-amber-500/10"}
                    late_count += 1
                    present_count += 1
                else:
                    days_data[d] = {"marker": "P", "color": "text-emerald-400 bg-emerald-500/10"}
                    present_count += 1
            else:
                if cur_dt <= date.today():
                    days_data[d] = {"marker": "A", "color": "text-rose-400 bg-rose-500/10"}
                    absent_count += 1
                else:
                    days_data[d] = {"marker": "-", "color": "text-gray-600"}

        pct = round((present_count / total_working_days * 100) if total_working_days > 0 else 100, 1)

        matrix.append({
            "student": s,
            "days": days_data,
            "total_present": present_count,
            "total_late": late_count,
            "total_absent": absent_count,
            "attendance_percentage": pct,
            "cbse_compliance": "Eligible" if pct >= 75.0 else "Shortage (<75%)"
        })

    return {
        "school": settings,
        "year_month": year_month,
        "num_days": num_days,
        "total_working_days": total_working_days,
        "day_headers": day_headers,
        "matrix": matrix
    }


# --- Teachers & Staff Directory & Attendance ---
def list_teachers(search=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM teachers_staff WHERE status = 'active'"
    params = []
    if search:
        query += " AND (first_name LIKE ? OR last_name LIKE ? OR designation LIKE ? OR employee_code LIKE ?)"
        t = f"%{search}%"
        params.extend([t, t, t, t])
    query += " ORDER BY first_name ASC"
    rows = [dict(r) for r in cursor.execute(query, params).fetchall()]
    conn.close()
    return rows


def get_teacher(staff_id_or_code):
    conn = get_connection()
    cursor = conn.cursor()
    if isinstance(staff_id_or_code, int) or (isinstance(staff_id_or_code, str) and str(staff_id_or_code).isdigit()):
        row = cursor.execute("SELECT * FROM teachers_staff WHERE id = ?", (int(staff_id_or_code),)).fetchone()
    else:
        row = cursor.execute("SELECT * FROM teachers_staff WHERE employee_code = ? OR qr_token = ? OR email = ?", (str(staff_id_or_code), str(staff_id_or_code), str(staff_id_or_code))).fetchone()
    conn.close()
    return dict(row) if row else None


def create_teacher(data):
    conn = get_connection()
    cursor = conn.cursor()
    code = data.get("employee_code")
    if not code:
        count = cursor.execute("SELECT COUNT(*) FROM teachers_staff").fetchone()[0]
        code = f"FAC-{(count + 101):03d}"

    qr_token = f"FACULTY-{code}"

    cursor.execute("""
        INSERT INTO teachers_staff (
            employee_code, first_name, last_name, email, phone,
            designation, subject_department, monthly_salary, pin_code, qr_token, avatar_url,
            status, join_date, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
    """, (
        code, data.get("first_name", "").strip(), data.get("last_name", "").strip(),
        data.get("email", "").strip().lower(), data.get("phone", "+91 94350-00000"),
        data.get("designation", "Teacher"), data.get("subject_department", "General"),
        float(data.get("monthly_salary", 55000.0)), data.get("pin_code", "1234"),
        qr_token, data.get("avatar_url", f"https://api.dicebear.com/7.x/avataaars/svg?seed={code}"),
        date.today().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_teacher(new_id)


def update_teacher(staff_id, data):
    conn = get_connection()
    cursor = conn.cursor()
    fields = ["first_name", "last_name", "email", "phone", "designation", "subject_department", "monthly_salary", "pin_code", "avatar_url"]
    updates = []
    values = []
    for f in fields:
        if f in data:
            updates.append(f"{f} = ?")
            values.append(data[f])
    if updates:
        values.append(staff_id)
        cursor.execute(f"UPDATE teachers_staff SET {', '.join(updates)} WHERE id = ?", values)
        conn.commit()
    conn.close()
    return get_teacher(staff_id)


def record_staff_scan(identifier):
    conn = get_connection()
    cursor = conn.cursor()

    if isinstance(identifier, int) or (isinstance(identifier, str) and str(identifier).isdigit()):
        staff = cursor.execute("SELECT * FROM teachers_staff WHERE id = ?", (int(identifier),)).fetchone()
    else:
        staff = cursor.execute("SELECT * FROM teachers_staff WHERE employee_code = ? OR qr_token = ?", (str(identifier), str(identifier))).fetchone()

    if not staff:
        conn.close()
        return {"success": False, "message": f"Faculty/Staff not recognized: '{identifier}'"}

    today_str = date.today().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    existing = cursor.execute("""
        SELECT * FROM staff_attendance WHERE staff_id = ? AND date = ?
    """, (staff["id"], today_str)).fetchone()

    if not existing or not existing["check_in_time"]:
        cursor.execute("""
            INSERT INTO staff_attendance (
                staff_id, date, check_in_time, status, created_at
            ) VALUES (?, ?, ?, 'present', ?)
            ON CONFLICT(staff_id, date) DO UPDATE SET check_in_time = excluded.check_in_time
        """, (staff["id"], today_str, now_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return {
            "success": True,
            "action": "staff_check_in",
            "staff": dict(staff),
            "time": now_time[:5],
            "message": f"Staff Check-In: Welcome, {staff['first_name']} {staff['last_name']} ({staff['designation']})!"
        }
    elif not existing["check_out_time"]:
        t_in = datetime.strptime(existing["check_in_time"], "%H:%M:%S")
        t_out = datetime.strptime(now_time, "%H:%M:%S")
        tot_hours = round(max(0, (t_out - t_in).total_seconds() / 3600.0), 1)

        cursor.execute("""
            UPDATE staff_attendance
            SET check_out_time = ?, total_hours = ?
            WHERE id = ?
        """, (now_time, tot_hours, existing["id"]))
        conn.commit()
        conn.close()
        return {
            "success": True,
            "action": "staff_check_out",
            "staff": dict(staff),
            "time": now_time[:5],
            "message": f"Staff Check-Out: Goodbye, {staff['first_name']}! Logged {tot_hours} hrs."
        }
    else:
        conn.close()
        return {
            "success": True,
            "action": "already_completed",
            "staff": dict(staff),
            "message": f"{staff['first_name']} has completed today's attendance."
        }


def get_teacher_today_attendance():
    today_str = date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    
    rows = [dict(r) for r in cursor.execute("""
        SELECT 
            t.id as staff_id,
            t.employee_code,
            t.first_name,
            t.last_name,
            t.email,
            t.designation,
            t.subject_department,
            t.monthly_salary,
            t.avatar_url,
            a.check_in_time,
            a.check_out_time,
            a.total_hours,
            a.late_minutes,
            COALESCE(a.status, 'absent') as attendance_status
        FROM teachers_staff t
        LEFT JOIN staff_attendance a ON t.id = a.staff_id AND a.date = ?
        WHERE t.status = 'active'
        ORDER BY 
            CASE WHEN a.check_in_time IS NOT NULL THEN 1 ELSE 2 END,
            t.first_name ASC
    """, (today_str,)).fetchall()]
    
    conn.close()
    return rows


# --- Faculty Leave Requests ---
def list_teacher_leaves(status=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT l.*, t.employee_code, t.first_name, t.last_name, t.designation, t.subject_department
        FROM staff_leaves l
        JOIN teachers_staff t ON l.staff_id = t.id
        WHERE 1=1
    """
    params = []
    if status:
        query += " AND l.status = ?"
        params.append(status)
    query += " ORDER BY l.id DESC"
    rows = [dict(r) for r in cursor.execute(query, params).fetchall()]
    conn.close()
    return rows


def submit_teacher_leave(staff_id, leave_type, start_date_str, end_date_str, reason=""):
    conn = get_connection()
    cursor = conn.cursor()
    dt_start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    dt_end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    total_days = max(1, (dt_end - dt_start).days + 1)

    cursor.execute("""
        INSERT INTO staff_leaves (
            staff_id, leave_type, start_date, end_date, total_days, reason, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
    """, (staff_id, leave_type, start_date_str, end_date_str, total_days, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def review_teacher_leave(leave_id, status, reviewer="Principal"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE staff_leaves
        SET status = ?, reviewed_by = ?, reviewed_at = ?
        WHERE id = ?
    """, (status, reviewer, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), leave_id))
    conn.commit()
    conn.close()
    return True


# --- Faculty & Staff Payroll Engine ---
def generate_teacher_payroll(year_month=None):
    if not year_month:
        year_month = date.today().strftime("%Y-%m")

    settings = get_school_settings()
    cur_sym = settings.get("currency_symbol", "₹")

    conn = get_connection()
    cursor = conn.cursor()

    faculty = [dict(r) for r in cursor.execute("""
        SELECT * FROM teachers_staff WHERE status = 'active'
    """).fetchall()]

    start_date = f"{year_month}-01"
    end_date = f"{year_month}-31"

    generated = []

    for f in faculty:
        stats = cursor.execute("""
            SELECT 
                COUNT(*) as days_worked,
                SUM(total_hours) as tot_hours,
                SUM(late_minutes) as tot_late_min
            FROM staff_attendance
            WHERE staff_id = ? AND date >= ? AND date <= ? AND check_in_time IS NOT NULL
        """, (f["id"], start_date, end_date)).fetchone()

        days_worked = stats["days_worked"] or 22
        tot_hours = round(stats["tot_hours"] or (days_worked * 7.0), 1)
        tot_late = stats["tot_late_min"] or 0

        base_salary = f["monthly_salary"]
        late_deductions = round((tot_late // 15) * 250.0, 2)
        bonus_allowance = 2500.0 if days_worked >= 22 else 1000.0
        tax_deductions = round((base_salary + bonus_allowance) * 0.05, 2)
        net_pay = round(base_salary + bonus_allowance - late_deductions - tax_deductions, 2)

        payslip_num = f"PAY-{year_month.replace('-', '')}-{f['employee_code']}"

        cursor.execute("""
            INSERT INTO payroll_records (
                period_month, staff_id, total_days_worked, total_regular_hours,
                total_late_minutes, base_salary_earned, late_deductions, bonus_allowance,
                tax_deductions, net_pay, payment_status, payslip_number, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?)
            ON CONFLICT(staff_id, period_month) DO UPDATE SET
                total_days_worked = excluded.total_days_worked,
                total_regular_hours = excluded.total_regular_hours,
                base_salary_earned = excluded.base_salary_earned,
                late_deductions = excluded.late_deductions,
                bonus_allowance = excluded.bonus_allowance,
                tax_deductions = excluded.tax_deductions,
                net_pay = excluded.net_pay,
                generated_at = excluded.generated_at
        """, (
            year_month, f["id"], days_worked, tot_hours, tot_late,
            base_salary, late_deductions, bonus_allowance, tax_deductions,
            net_pay, payslip_num, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        generated.append(payslip_num)

    conn.commit()
    conn.close()

    return get_teacher_payroll_summary(year_month)


def get_teacher_payroll_summary(year_month=None):
    if not year_month:
        year_month = date.today().strftime("%Y-%m")

    conn = get_connection()
    cursor = conn.cursor()

    rows = [dict(r) for r in cursor.execute("""
        SELECT 
            p.*,
            t.employee_code,
            t.first_name,
            t.last_name,
            t.email,
            t.designation,
            t.subject_department,
            t.monthly_salary,
            t.avatar_url
        FROM payroll_records p
        JOIN teachers_staff t ON p.staff_id = t.id
        WHERE p.period_month = ?
        ORDER BY t.first_name ASC
    """, (year_month,)).fetchall()]

    conn.close()

    total_net = sum(r["net_pay"] for r in rows)
    total_deductions = sum(r["late_deductions"] + r["tax_deductions"] for r in rows)

    return {
        "period_month": year_month,
        "count": len(rows),
        "total_net_payout": round(total_net, 2),
        "total_deductions": round(total_deductions, 2),
        "records": rows
    }


def get_teacher_payslip(payslip_num):
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute("""
        SELECT p.*, t.employee_code, t.first_name, t.last_name, t.email, t.phone, t.designation, t.subject_department, t.monthly_salary, t.join_date
        FROM payroll_records p
        JOIN teachers_staff t ON p.staff_id = t.id
        WHERE p.payslip_number = ? OR p.id = ?
    """, (str(payslip_num), str(payslip_num))).fetchone()

    conn.close()
    if not row:
        return None

    settings = get_school_settings()
    return {
        "school": settings,
        "payslip": dict(row)
    }


def update_teacher_payroll_status(payroll_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    pay_date = date.today().strftime("%Y-%m-%d")
    cursor.execute("""
        UPDATE payroll_records
        SET payment_status = ?, payment_date = ?
        WHERE id = ?
    """, (status, pay_date if status == "paid" else None, payroll_id))
    conn.commit()
    conn.close()
    return True
