@echo off
title Autonomous Revenue Engine - 24/7 Watchdog
color 0A

echo ========================================================
echo  AUTONOMOUS REVENUE ENGINE - 24/7 SELF-HEALING LAUNCHER
echo ========================================================
echo.

:loop
echo [%date% %time%] Starting server.py...
python -u sales_engine\server.py
echo.
echo [WARNING] Server stopped unexpectedly! Auto-restarting in 3 seconds...
timeout /t 3 /nobreak >nul
goto loop
