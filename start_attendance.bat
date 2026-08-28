@echo off
title Staff Attendance, QR Check-in & Payroll SaaS
echo ============================================================
echo   Starting Staff Attendance & Payroll SaaS Platform...
echo   Port: http://localhost:5000
echo ============================================================
echo.
echo Opening Admin Dashboard and Office Kiosk...
start http://localhost:5000/
start http://localhost:5000/kiosk
echo.
python run.py
pause
