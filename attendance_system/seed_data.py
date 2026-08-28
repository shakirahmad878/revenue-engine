"""
Authentic Seed Dataset for Maharishi Vidya Mandir Public School, Guwahati (CBSE/SEBA)
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

from database import get_connection, init_db


CLASSES_DATA = [
    ("Class 6", "A", "Mrs. Mousumi Barua", "Room 101", 35),
    ("Class 6", "B", "Mr. Pranjal Medhi", "Room 102", 35),
    ("Class 7", "A", "Mrs. Archana Goswami", "Room 201", 36),
    ("Class 8", "A", "Mr. Rituraj Sharma", "Room 202", 38),
    ("Class 9", "A", "Mrs. Deepali Hazarika", "Room 301", 40),
    ("Class 9", "B", "Mr. Bhaskar Jyoti Das", "Room 302", 40),
    ("Class 10", "A", "Mrs. Manju Kakati", "Room 401", 42),
    ("Class 10", "B", "Mr. Nabajit Saikia", "Room 402", 42),
    ("Class 11", "A (Sci)", "Dr. Ankur Borthakur", "Science Block S-1", 35),
    ("Class 12", "A (Sci)", "Mrs. Sharmistha Roy", "Science Block S-2", 35)
]

BUS_ROUTES_DATA = [
    ("Route #1", "Jalukbari - Maligaon - Bharalumukh to School", "Pankaj Kalita", "+91 94350-11223", "Bhaben Roy", "+91 98540-33445", "AS-01-FC-2451"),
    ("Route #2", "Beltola - Six Mile - VIP Road to School", "Dipen Deka", "+91 94351-22334", "Gopal Barman", "+91 98541-44556", "AS-01-FC-3892"),
    ("Route #3", "Chandmari - Noonmati - Geetanagar to School", "Jitumoni Nath", "+91 94352-33445", "Raju Das", "+91 98542-55667", "AS-01-FC-5120"),
    ("Route #4", "Zoo Road - Christian Basti - Dispur to School", "Mukesh Sarma", "+91 94353-44556", "Hiren Borah", "+91 98543-66778", "AS-01-FC-7833")
]

STUDENTS_DATA = [
    {"name": "Aman Borah", "class": ("Class 9", "A"), "roll": 14, "parent": "Mr. Bipul Borah", "phone": "+91 98640-12845", "bg": "O+", "bus": "Route #4", "photo": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80"},
    {"name": "Priyanshu Sarma", "class": ("Class 9", "A"), "roll": 15, "parent": "Mrs. Rina Sarma", "phone": "+91 98640-23910", "bg": "A+", "bus": "Route #4", "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"},
    {"name": "Ananya Das", "class": ("Class 9", "A"), "roll": 16, "parent": "Dr. Dilip Das", "phone": "+91 98640-34567", "bg": "B+", "bus": "Route #2", "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"},
    {"name": "Deepjyoti Kalita", "class": ("Class 9", "A"), "roll": 17, "parent": "Mr. Hemen Kalita", "phone": "+91 98640-45678", "bg": "AB+", "bus": "Route #1", "photo": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"},
    {"name": "Tanvi Goswami", "class": ("Class 9", "A"), "roll": 18, "parent": "Mrs. Runumi Goswami", "phone": "+91 98640-56789", "bg": "O+", "bus": "Self Transport", "photo": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80"},

    {"name": "Himangshu Barman", "class": ("Class 9", "B"), "roll": 1, "parent": "Mr. Naren Barman", "phone": "+91 98640-67890", "bg": "A-", "bus": "Route #3", "photo": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"},
    {"name": "Sneha Hazarika", "class": ("Class 9", "B"), "roll": 2, "parent": "Mr. Ranjit Hazarika", "phone": "+91 98640-78901", "bg": "B+", "bus": "Route #2", "photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"},
    {"name": "Raktim Saikia", "class": ("Class 9", "B"), "roll": 3, "parent": "Mrs. Gitashree Saikia", "phone": "+91 98640-89012", "bg": "O+", "bus": "Route #4", "photo": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80"},
    {"name": "Debajit Roy", "class": ("Class 9", "B"), "roll": 4, "parent": "Mr. Subhash Roy", "phone": "+91 98640-90123", "bg": "AB-", "bus": "Route #1", "photo": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&auto=format&fit=crop&q=80"},

    {"name": "Barnali Deka", "class": ("Class 10", "A"), "roll": 10, "parent": "Dr. Prabin Deka", "phone": "+91 98641-01234", "bg": "O+", "bus": "Route #4", "photo": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80"},
    {"name": "Rohan Phukan", "class": ("Class 10", "A"), "roll": 11, "parent": "Mr. Trailokya Phukan", "phone": "+91 98641-12345", "bg": "A+", "bus": "Route #3", "photo": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80"},
    {"name": "Nilakshi Kakati", "class": ("Class 10", "A"), "roll": 12, "parent": "Mrs. Minoti Kakati", "phone": "+91 98641-23456", "bg": "B+", "bus": "Route #2", "photo": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=150&auto=format&fit=crop&q=80"},

    {"name": "Kaushik Talukdar", "class": ("Class 10", "B"), "roll": 5, "parent": "Mr. Girish Talukdar", "phone": "+91 98641-34567", "bg": "O+", "bus": "Route #1", "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"},
    {"name": "Dikshita Baishya", "class": ("Class 10", "B"), "roll": 6, "parent": "Mrs. Anita Baishya", "phone": "+91 98641-45678", "bg": "A+", "bus": "Self Transport", "photo": "https://images.unsplash.com/photo-1548142813-c348350df52b?w=150&auto=format&fit=crop&q=80"},

    {"name": "Abhinav Choudhury", "class": ("Class 11", "A (Sci)"), "roll": 1, "parent": "Mr. Manoj Choudhury", "phone": "+91 98641-56789", "bg": "B-", "bus": "Route #4", "photo": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80"},
    {"name": "Trishna Mahanta", "class": ("Class 11", "A (Sci)"), "roll": 2, "parent": "Dr. Sailen Mahanta", "phone": "+91 98641-67890", "bg": "O+", "bus": "Route #3", "photo": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"},

    {"name": "Bikramjit Nath", "class": ("Class 12", "A (Sci)"), "roll": 21, "parent": "Mr. Diganta Nath", "phone": "+91 98641-78901", "bg": "A+", "bus": "Route #2", "photo": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"},
    {"name": "Jyotishmita Das", "class": ("Class 12", "A (Sci)"), "roll": 22, "parent": "Mrs. Bandana Das", "phone": "+91 98641-89012", "bg": "O+", "bus": "Route #1", "photo": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150&auto=format&fit=crop&q=80"},

    {"name": "Bhrigu Kumar Barua", "class": ("Class 6", "A"), "roll": 1, "parent": "Mr. Rupom Barua", "phone": "+91 98641-90123", "bg": "O+", "bus": "Route #4", "photo": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"},
    {"name": "Pallavi Chetia", "class": ("Class 6", "A"), "roll": 2, "parent": "Mrs. Jonali Chetia", "phone": "+91 98642-01234", "bg": "B+", "bus": "Route #3", "photo": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80"},
    {"name": "Arindam Dutta", "class": ("Class 7", "A"), "roll": 8, "parent": "Mr. Bhaskar Dutta", "phone": "+91 98642-12345", "bg": "A+", "bus": "Route #1", "photo": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80"},
    {"name": "Monisha Bharali", "class": ("Class 8", "A"), "roll": 14, "parent": "Dr. Jayanta Bharali", "phone": "+91 98642-23456", "bg": "O-", "bus": "Route #2", "photo": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"}
]

TEACHERS_DATA = [
    {"code": "FAC-101", "first": "Dr. S. K.", "last": "Mahanta", "desig": "Principal", "dept": "Administration", "sal": 95000.0, "pin": "1001", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"},
    {"code": "FAC-102", "first": "Deepali", "last": "Hazarika", "desig": "PGT English & Senior Coordinator", "dept": "Languages", "sal": 58000.0, "pin": "1002", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"},
    {"code": "FAC-103", "first": "Bhaskar", "last": "Das", "desig": "PGT Mathematics", "dept": "Mathematics", "sal": 55000.0, "pin": "1003", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"},
    {"code": "FAC-104", "first": "Dr. Ankur", "last": "Borthakur", "desig": "PGT Physics", "dept": "Science", "sal": 60000.0, "pin": "1004", "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"},
    {"code": "FAC-105", "first": "Mousumi", "last": "Barua", "desig": "TGT Social Science", "dept": "Social Studies", "sal": 45000.0, "pin": "1005", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"},
    {"code": "FAC-106", "first": "Pankaj", "last": "Kalita", "desig": "Chief Transport & Safety In-Charge", "dept": "Operations", "sal": 35000.0, "pin": "1006", "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80"}
]


def populate_school_seed_data():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    # 1. School Settings
    cursor.execute("DELETE FROM school_settings")
    cursor.execute("""
        INSERT INTO school_settings (
            id, name, tagline, affiliation_board, affiliation_no, school_code,
            logo_url, principal_name, principal_signature, city, currency_symbol,
            gate_open_time, school_start_time, morning_strength_cutoff, absence_broadcast_time,
            gate_close_time, late_grace_minutes, preferred_language, whatsapp_gateway_status,
            dynamic_qr_secret, qr_refresh_seconds, updated_at
        ) VALUES (
            1, 'Maharishi Vidya Mandir Public School', 'Excellence in Education, Character & Student Safety',
            'CBSE, New Delhi (Affiliated)', 'CBSE/AFF/AS/2026/89401', 'MVM-GUW-01',
            '', 'Dr. S. K. Mahanta', 'Dr. S. K. Mahanta, M.Sc, Ph.D, B.Ed', 'Guwahati, Assam', '₹',
            '07:30', '08:00', '08:15', '08:30', '14:30', 10, 'en', 'active_connected',
            'mvm_assam_secret_2026', 20, ?
        )
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

    # Clear other tables
    cursor.execute("DELETE FROM notification_logs")
    cursor.execute("DELETE FROM emergency_broadcasts")
    cursor.execute("DELETE FROM payroll_records")
    cursor.execute("DELETE FROM staff_attendance")
    cursor.execute("DELETE FROM teachers_staff")
    cursor.execute("DELETE FROM student_attendance")
    cursor.execute("DELETE FROM students")
    cursor.execute("DELETE FROM bus_routes")
    cursor.execute("DELETE FROM classes")

    # 2. Insert Classes
    class_map = {}
    for grade, sec, teacher, room, cap in CLASSES_DATA:
        cursor.execute("""
            INSERT INTO classes (grade, section, class_teacher_name, room_no, capacity, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (grade, sec, teacher, room, cap, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        class_map[(grade, sec)] = cursor.lastrowid

    # 3. Insert Bus Routes
    for r_no, r_name, d_name, d_phone, c_name, c_phone, b_no in BUS_ROUTES_DATA:
        cursor.execute("""
            INSERT INTO bus_routes (route_no, route_name, driver_name, driver_phone, conductor_name, conductor_phone, bus_number, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (r_no, r_name, d_name, d_phone, c_name, c_phone, b_no, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    # 4. Insert Students
    student_ids = []
    student_records = []
    for idx, s in enumerate(STUDENTS_DATA):
        c_id = class_map[s["class"]]
        adm_no = f"MVM-2026-{(idx + 101):04d}"
        qr_token = f"STUDENT-{adm_no}"
        rfid_card = f"RFID-{random.randint(100000, 999999)}"

        cursor.execute("""
            INSERT INTO students (
                admission_no, roll_no, class_id, student_name, blood_group,
                parent_guardian_name, parent_whatsapp_phone, emergency_phone,
                address, bus_route_no, photo_url, qr_token, rfid_card_id, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Guwahati, Assam', ?, ?, ?, ?, 'active', ?)
        """, (
            adm_no, s["roll"], c_id, s["name"], s["bg"],
            s["parent"], s["phone"], s["phone"], s["bus"],
            s["photo"], qr_token, rfid_card, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        s_id = cursor.lastrowid
        student_ids.append(s_id)
        student_records.append((s_id, s, adm_no, qr_token))

    # 5. Insert Teachers & Staff
    for f in TEACHERS_DATA:
        token = f"FACULTY-{f['code']}"
        email = f"{f['first'].lower().replace(' ', '').replace('.', '')}.{f['last'].lower()}@mvmguwahati.edu.in"
        cursor.execute("""
            INSERT INTO teachers_staff (
                employee_code, first_name, last_name, email, phone, designation,
                subject_department, monthly_salary, pin_code, qr_token, avatar_url, status, join_date, created_at
            ) VALUES (?, ?, ?, ?, '+91 94350-00000', ?, ?, ?, ?, ?, ?, 'active', '2022-04-01', ?)
        """, (
            f["code"], f["first"], f["last"], email, f["desig"], f["dept"],
            f["sal"], f["pin"], token, f["avatar"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    conn.commit()

    # 6. Past 30 Days Authentic Student Attendance
    today = date.today()
    random.seed(42)

    for days_ago in range(30, 0, -1):
        cur_date = today - timedelta(days=days_ago)
        cur_date_str = cur_date.strftime("%Y-%m-%d")

        # Skip Sundays
        if cur_date.weekday() == 6:
            continue

        for s_id, s_info, adm_no, qr_tok in student_records:
            roll = random.random()
            if roll < 0.05: # 5% absent
                continue

            is_late = roll > 0.88
            if is_late:
                late_min = random.randint(11, 28)
                arr_h = 8
                arr_m = late_min
                status = "late"
            else:
                early_min = random.randint(10, 25)
                tot_m = 8 * 60 - early_min
                arr_h = tot_m // 60
                arr_m = tot_m % 60
                status = "present"
                late_min = 0

            in_time_str = f"{arr_h:02d}:{arr_m:02d}:{random.randint(10, 59):02d}"
            out_time_str = f"14:{random.randint(25, 45):02d}:{random.randint(10, 59):02d}"

            cursor.execute("""
                INSERT INTO student_attendance (
                    student_id, date, gate_in_time, gate_out_time, status, late_minutes,
                    whatsapp_in_sent, whatsapp_out_sent, scanned_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, 1, 'Main Gate Kiosk Laser', ?)
            """, (
                s_id, cur_date_str, in_time_str, out_time_str, status, late_min,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

    # 7. Today's Live Gate Attendance (Morning 8:15 AM State)
    today_str = today.strftime("%Y-%m-%d")
    for i, (s_id, s_info, adm_no, qr_tok) in enumerate(student_records):
        if i >= len(student_records) - 2:
            # Leave 2 students absent (to test 8:30 AM Absence broadcast!)
            continue

        is_late = (i % 5 == 0) # Some late
        if is_late:
            late_min = random.randint(12, 22)
            arr_h = 8
            arr_m = late_min
            status = "late"
        else:
            late_min = 0
            arr_h = 7
            arr_m = random.randint(42, 58)
            status = "present"

        in_time_str = f"{arr_h:02d}:{arr_m:02d}:15"

        cursor.execute("""
            INSERT INTO student_attendance (
                student_id, date, gate_in_time, status, late_minutes,
                whatsapp_in_sent, scanned_by, created_at
            ) VALUES (?, ?, ?, ?, ?, 1, 'Main Gate Kiosk Laser', ?)
        """, (s_id, today_str, in_time_str, status, late_min, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # Seed sample live notification log
        cursor.execute("""
            INSERT INTO notification_logs (
                student_id, recipient_name, phone_number, channel, notification_type, message_text, status, timestamp
            ) VALUES (?, ?, ?, 'WhatsApp', ?, ?, 'Delivered', ?)
        """, (
            s_id, s_info["parent"], s_info["phone"], "ARRIVAL" if late_min == 0 else "LATE",
            f"Dear {s_info['parent']}, your child {s_info['name']} ({s_info['class'][0]}-{s_info['class'][1]}, Roll #{s_info['roll']}) has safely arrived at Maharishi Vidya Mandir at {in_time_str[:5]}." + (f" [Late by {late_min} mins]" if late_min > 0 else ""),
            f"{today_str} {in_time_str}"
        ))

    # 8. Teachers Live Check-In Today
    for f in TEACHERS_DATA:
        cursor.execute("SELECT id FROM teachers_staff WHERE employee_code = ?", (f["code"],))
        t_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO staff_attendance (
                staff_id, date, check_in_time, status, created_at
            ) VALUES (?, ?, '07:45:00', 'present', ?)
        """, (t_id, today_str, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    print(f"✅ Successfully seeded Maharishi Vidya Mandir School database ({len(student_records)} students, {len(TEACHERS_DATA)} faculty, classes, bus routes, and attendance).")


if __name__ == "__main__":
    populate_school_seed_data()
