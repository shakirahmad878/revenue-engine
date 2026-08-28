"""
Realistic Seed Data Generator & Industry Presets for Staff Attendance System
"""

import os
import sys
import random
from datetime import datetime, timedelta, date

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database import (
    get_connection, init_db, get_company_settings,
    generate_monthly_payroll, update_payroll_status
)


PRESETS = {
    "tech": {
        "name": "Apex Innovations & Tech Labs",
        "tagline": "Next-Gen Software & Digital Engineering",
        "currency_symbol": "$",
        "currency_code": "USD",
        "timezone": "America/New_York",
        "work_start_time": "09:00",
        "work_end_time": "17:30",
        "late_grace_minutes": 15,
        "overtime_multiplier": 1.5,
        "late_deduction_rate": 10.0,
        "departments": [
            ("Software Engineering", "Marcus Vance", "#3B82F6"),
            ("Product & Design", "Elena Rostova", "#8B5CF6"),
            ("Sales & Enterprise Growth", "David Sterling", "#10B981"),
            ("DevOps & Cloud Operations", "Sarah Jenkins", "#F59E0B"),
            ("People Operations & HR", "Amara Okafor", "#EC4899")
        ],
        "employees": [
            {"code": "EMP-101", "first": "Marcus", "last": "Vance", "dept": "Software Engineering", "role": "Principal Systems Architect", "type": "monthly", "salary": 8500.0, "rate": 55.0, "pin": "1001", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-102", "first": "Elena", "last": "Rostova", "dept": "Product & Design", "role": "Head of Product Design", "type": "monthly", "salary": 7800.0, "rate": 50.0, "pin": "1002", "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-103", "first": "David", "last": "Sterling", "dept": "Sales & Enterprise Growth", "role": "VP of Global Sales", "type": "monthly", "salary": 9200.0, "rate": 60.0, "pin": "1003", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-104", "first": "Sarah", "last": "Jenkins", "dept": "DevOps & Cloud Operations", "role": "Lead Cloud Infrastructure Engineer", "type": "monthly", "salary": 7200.0, "rate": 45.0, "pin": "1004", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-105", "first": "Amara", "last": "Okafor", "dept": "People Operations & HR", "role": "Director of People & Culture", "type": "monthly", "salary": 6500.0, "rate": 40.0, "pin": "1005", "avatar": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-106", "first": "Lucas", "last": "Tanaka", "dept": "Software Engineering", "role": "Senior Full-Stack Developer", "type": "hourly", "salary": 5800.0, "rate": 35.0, "pin": "1006", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-107", "first": "Chloe", "last": "Dupont", "dept": "Product & Design", "role": "UI/UX Interaction Designer", "type": "hourly", "salary": 5200.0, "rate": 32.0, "pin": "1007", "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-108", "first": "Tariq", "last": "Al-Mansoor", "dept": "Sales & Enterprise Growth", "role": "Senior Account Executive", "type": "monthly", "salary": 6000.0, "rate": 38.0, "pin": "1008", "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-109", "first": "Rachel", "last": "Zimmerman", "dept": "Software Engineering", "role": "Frontend React Engineer", "type": "hourly", "salary": 4900.0, "rate": 30.0, "pin": "1009", "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-110", "first": "Derrick", "last": "Holloway", "dept": "DevOps & Cloud Operations", "role": "Site Reliability Specialist", "type": "hourly", "salary": 5100.0, "rate": 31.0, "pin": "1010", "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-111", "first": "Maya", "last": "Patel", "dept": "People Operations & HR", "role": "Talent Acquisition Lead", "type": "monthly", "salary": 4800.0, "rate": 28.0, "pin": "1011", "avatar": "https://images.unsplash.com/photo-1548142813-c348350df52b?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-112", "first": "Jordan", "last": "Rivera", "dept": "Software Engineering", "role": "QA Automation Engineer", "type": "hourly", "salary": 4600.0, "rate": 27.0, "pin": "1012", "avatar": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80"}
        ]
    },
    "retail": {
        "name": "Metro Grand Supermarkets & Retail",
        "tagline": "Fast, Fresh & Community-First Groceries",
        "currency_symbol": "₦",
        "currency_code": "NGN",
        "timezone": "Africa/Lagos",
        "work_start_time": "08:00",
        "work_end_time": "16:00",
        "late_grace_minutes": 10,
        "overtime_multiplier": 1.5,
        "late_deduction_rate": 1500.0,
        "departments": [
            ("Store Operations & Cashier", "Emeka Nwosu", "#10B981"),
            ("Inventory & Supply Chain", "Grace Adebayo", "#3B82F6"),
            ("Customer Experience", "Fatima Bello", "#F59E0B"),
            ("Security & Loss Prevention", "Oluwaseun Bakare", "#EF4444"),
            ("Branch Administration", "Chinedu Eze", "#8B5CF6")
        ],
        "employees": [
            {"code": "EMP-201", "first": "Emeka", "last": "Nwosu", "dept": "Store Operations & Cashier", "role": "Head Store Manager", "type": "monthly", "salary": 450000.0, "rate": 2500.0, "pin": "2001", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-202", "first": "Grace", "last": "Adebayo", "dept": "Inventory & Supply Chain", "role": "Warehouse & Logistics Lead", "type": "monthly", "salary": 380000.0, "rate": 2100.0, "pin": "2002", "avatar": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-203", "first": "Fatima", "last": "Bello", "dept": "Customer Experience", "role": "Front Desk Supervisor", "type": "hourly", "salary": 250000.0, "rate": 1400.0, "pin": "2003", "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-204", "first": "Oluwaseun", "last": "Bakare", "dept": "Security & Loss Prevention", "role": "Chief Security Officer", "type": "hourly", "salary": 220000.0, "rate": 1200.0, "pin": "2004", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"},
            {"code": "EMP-205", "first": "Chinedu", "last": "Eze", "dept": "Branch Administration", "role": "Operations Controller", "type": "monthly", "salary": 320000.0, "rate": 1800.0, "pin": "2005", "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"}
        ]
    }
}


def populate_seed_data(preset_key="tech"):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    preset = PRESETS.get(preset_key, PRESETS["tech"])

    # 1. Company Settings
    cursor.execute("DELETE FROM company_settings")
    cursor.execute("""
        INSERT INTO company_settings (
            id, name, tagline, logo_url, currency_symbol, currency_code, timezone,
            work_start_time, work_end_time, late_grace_minutes, half_day_hours,
            full_day_hours, overtime_multiplier, late_deduction_rate, dynamic_qr_secret,
            qr_refresh_seconds, geofence_enabled, office_lat, office_lng, geofence_radius_meters, updated_at
        ) VALUES (
            1, ?, ?, '', ?, ?, ?, ?, ?, ?, 4.0, 8.0, ?, ?, 'apex_secret_key_2026',
            20, 0, 40.7128, -74.0060, 200, ?
        )
    """, (
        preset["name"], preset["tagline"], preset["currency_symbol"], preset["currency_code"],
        preset["timezone"], preset["work_start_time"], preset["work_end_time"],
        preset["late_grace_minutes"], preset["overtime_multiplier"], preset["late_deduction_rate"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    # Clear tables
    cursor.execute("DELETE FROM activity_logs")
    cursor.execute("DELETE FROM payroll_records")
    cursor.execute("DELETE FROM leave_requests")
    cursor.execute("DELETE FROM attendance_records")
    cursor.execute("DELETE FROM employees")
    cursor.execute("DELETE FROM departments")

    # 2. Insert Departments
    dept_map = {}
    for d_name, d_mgr, d_color in preset["departments"]:
        cursor.execute("""
            INSERT INTO departments (name, manager_name, color, created_at)
            VALUES (?, ?, ?, ?)
        """, (d_name, d_mgr, d_color, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        dept_map[d_name] = cursor.lastrowid

    # 3. Insert Employees
    emp_ids = []
    emp_records = []
    for emp_info in preset["employees"]:
        d_id = dept_map.get(emp_info["dept"])
        badge_token = f"BADGE-{emp_info['code']}-{random.randint(1000, 9999)}"
        email = f"{emp_info['first'].lower()}.{emp_info['last'].lower()}@apexcompany.com"
        
        cursor.execute("""
            INSERT INTO employees (
                employee_code, first_name, last_name, email, phone,
                department_id, designation, salary_type, hourly_rate,
                monthly_salary, pin_code, qr_token, avatar_url, status,
                join_date, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
        """, (
            emp_info["code"], emp_info["first"], emp_info["last"], email,
            f"+1 (555) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
            d_id, emp_info["role"], emp_info["type"], emp_info["rate"],
            emp_info["salary"], emp_info["pin"], badge_token, emp_info["avatar"],
            "2024-01-15", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        emp_id = cursor.lastrowid
        emp_ids.append(emp_id)
        emp_records.append((emp_id, emp_info))

    conn.commit()

    # 4. Generate 30 Days of Realistic Past Attendance Data
    today = date.today()
    work_start_h, work_start_m = map(int, preset["work_start_time"].split(":"))

    random.seed(42) # Deterministic realistic seed

    for days_ago in range(30, 0, -1):
        cur_date = today - timedelta(days=days_ago)
        cur_date_str = cur_date.strftime("%Y-%m-%d")
        
        # Skip weekends (Saturday=5, Sunday=6)
        if cur_date.weekday() >= 5:
            continue

        for emp_id, emp_info in emp_records:
            # 5% chance absent, 80% on-time, 15% late
            roll = random.random()
            if roll < 0.05:
                # Absent - no record
                continue

            is_late = roll > 0.85
            if is_late:
                # Arrived 16-45 mins late
                late_min = random.randint(16, 45)
                arr_h = work_start_h + (work_start_m + late_min) // 60
                arr_m = (work_start_m + late_min) % 60
                check_in_str = f"{arr_h:02d}:{arr_m:02d}:{random.randint(10, 59):02d}"
                status = "late"
            else:
                # Arrived on time (between 15 min early to on-time)
                early_min = random.randint(-15, 10)
                tot_m = (work_start_h * 60 + work_start_m) + early_min
                arr_h = tot_m // 60
                arr_m = tot_m % 60
                check_in_str = f"{arr_h:02d}:{arr_m:02d}:{random.randint(10, 59):02d}"
                status = "on_time"
                late_min = 0

            # Check-out time: 8 hours work + overtime occasionally
            has_ot = random.random() < 0.30
            work_duration = 8.0 + (random.choice([1.0, 1.5, 2.0]) if has_ot else random.choice([-0.2, 0.0, 0.2, 0.5]))
            out_tot_m = (arr_h * 60 + arr_m) + int(work_duration * 60)
            dep_h = min(23, out_tot_m // 60)
            dep_m = out_tot_m % 60
            check_out_str = f"{dep_h:02d}:{dep_m:02d}:{random.randint(10, 59):02d}"

            total_h = round(work_duration, 2)
            reg_h = min(8.0, total_h)
            ot_h = round(max(0.0, total_h - 8.0), 2)

            check_in_method = random.choice(["kiosk_qr", "kiosk_qr", "badge_scan", "mobile_scan"])

            cursor.execute("""
                INSERT INTO attendance_records (
                    employee_id, date, check_in_time, check_out_time, check_in_type, check_out_type,
                    total_hours, regular_hours, overtime_hours, late_minutes, status, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, 'kiosk_qr', ?, ?, ?, ?, ?, '', ?)
            """, (
                emp_id, cur_date_str, check_in_str, check_out_str, check_in_method,
                total_h, reg_h, ot_h, late_min, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

    # 5. Populate Today's Live Attendance
    today_str = today.strftime("%Y-%m-%d")
    for i, (emp_id, emp_info) in enumerate(emp_records):
        if i == len(emp_records) - 1:
            # Leave one employee absent / not yet arrived
            continue
        elif i == len(emp_records) - 2:
            # One employee on approved leave
            cursor.execute("UPDATE employees SET status = 'on_leave' WHERE id = ?", (emp_id,))
            cursor.execute("""
                INSERT INTO leave_requests (
                    employee_id, leave_type, start_date, end_date, total_days, reason, status, reviewed_by, reviewed_at, created_at
                ) VALUES (?, 'vacation', ?, ?, 3, 'Annual family holiday', 'approved', 'Director Amara Okafor', ?, ?)
            """, (
                emp_id, today_str, (today + timedelta(days=2)).strftime("%Y-%m-%d"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            continue

        # Check-in today
        is_late = (i % 4 == 0) # Some late
        if is_late:
            late_min = random.randint(18, 35)
            arr_h = 9
            arr_m = late_min
            status = "late"
        else:
            late_min = 0
            arr_h = 8
            arr_m = random.randint(45, 58)
            status = "on_time"

        check_in_str = f"{arr_h:02d}:{arr_m:02d}:14"
        
        # 3 employees already completed full day and checked out, rest currently working
        if i < 3:
            check_out_str = f"17:{random.randint(15, 45):02d}:00"
            total_h = 8.5
            reg_h = 8.0
            ot_h = 0.5
            status = "present"
            out_type = "kiosk_qr"
        else:
            check_out_str = None
            total_h = 0.0
            reg_h = 0.0
            ot_h = 0.0
            out_type = None

        cursor.execute("""
            INSERT INTO attendance_records (
                employee_id, date, check_in_time, check_out_time, check_in_type, check_out_type,
                total_hours, regular_hours, overtime_hours, late_minutes, status, created_at
            ) VALUES (?, ?, ?, ?, 'kiosk_qr', ?, ?, ?, ?, ?, ?, ?)
        """, (
            emp_id, today_str, check_in_str, check_out_str, out_type,
            total_h, reg_h, ot_h, late_min, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    # 6. Sample Pending Leave Requests for Testing
    cursor.execute("""
        INSERT INTO leave_requests (
            employee_id, leave_type, start_date, end_date, total_days, reason, status, created_at
        ) VALUES (?, 'sick', ?, ?, 2, 'Severe flu & medical rest prescribed', 'pending', ?)
    """, (
        emp_ids[0], (today + timedelta(days=3)).strftime("%Y-%m-%d"),
        (today + timedelta(days=4)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    cursor.execute("""
        INSERT INTO leave_requests (
            employee_id, leave_type, start_date, end_date, total_days, reason, status, created_at
        ) VALUES (?, 'casual', ?, ?, 1, 'Attending family wedding anniversary', 'pending', ?)
    """, (
        emp_ids[1], (today + timedelta(days=7)).strftime("%Y-%m-%d"),
        (today + timedelta(days=7)).strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    # 7. Generate Pre-calculated Payroll
    prev_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    cur_month = today.strftime("%Y-%m")

    generate_monthly_payroll(prev_month)
    # Mark previous month as paid
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE payroll_records SET payment_status = 'paid', payment_date = ? WHERE period_month = ?", ((today - timedelta(days=10)).strftime("%Y-%m-%d"), prev_month))
    conn.commit()
    conn.close()

    # Generate current month draft payroll
    generate_monthly_payroll(cur_month)

    print(f"✅ Successfully seeded database with preset '{preset_key}' ({len(emp_records)} staff, 30-day attendance history, payroll & leaves).")


if __name__ == "__main__":
    populate_seed_data("tech")
