"""
Root Launcher for Staff Attendance & Payroll SaaS System
Port: 5000 (Dedicated Local Server)
"""

import os
import sys

# Ensure local attendance_system directory is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "attendance_system")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app import run_server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    run_server(port)
