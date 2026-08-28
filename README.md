# Staff Attendance, Dynamic QR Check-In & Payroll SaaS Platform

> **Commercial-Grade B2B Workforce Operating System**  
> Dynamic Anti-Spoof QR Attendance • Real-time Monitoring • Automated Overtime & Deductions • 1-Click Itemized Payslips • B2B Client Reseller Kit

---

## 🌟 Key Capabilities

### 1. Dual-Mode QR Check-in / Check-out
- **Dynamic Office Kiosk Mode (`/kiosk`)**:
  - Live rotating QR code with auto-refreshing security tokens (fraud-proof; prevents photo sharing).
  - Staff scan with their smartphone camera to instantly log arrival/departure.
  - Optional PIN-based quick check-in for staff without phones.
- **Webcam ID Badge Scanner**:
  - Front-desk tablet or webcam reads physical or digital ID badges with instant synthesized audio chime feedback.
- **Mobile Employee Portal (`/scan`)**:
  - Point phone camera at office kiosk screen for instant check-in.
  - Digital ID badge pass mode.

### 2. Live Attendance Monitoring & Reports
- **Executive Dashboard (`/`)**:
  - Real-time arrival ticker and today's attendance summary (Present, On-Time, Late, On Leave, Absent).
  - 7-Day attendance trend graph and department workforce distribution (Chart.js).
  - Detailed audit trail logs.
- **Historical Reports & Timesheets**:
  - Date-range and department filtering.
  - 1-Click Export to CSV and printable summary.

### 3. Automated Payroll Engine & Payslips
- **Automated Wage Calculation**:
  - Handles hourly contracts and monthly fixed salaries.
  - Automatic 1.5x overtime multiplier computation.
  - Configurable late-arrival penalty deductions.
  - Statutory 5% tax withholding and performance allowances.
- **Official Itemized Payslips**:
  - Clean modal statement breakdown (Base pay, Overtime, Deductions, Net Pay).
  - Direct print & PDF download layout.
- **Bank & Accounting CSV Export**:
  - Direct batch upload for direct deposits (QuickBooks, Xero, Excel).

### 4. Staff Management & Leave Requests
- **Staff Directory & Badges**:
  - Employee profiles with salary details, departments, and PINs.
  - Printable batch sheet ID Cards (`/badges`) formatted for CR80 cards and A4 printing.
- **Leave Request Workflow (`/portal`)**:
  - Employees submit Vacation, Sick, Casual, or Unpaid leave.
  - Managers approve/reject directly from dashboard.

### 5. B2B Client Reseller & Pitch Kit (`/pitch`)
- **Public Sales Page & ROI Calculator**:
  - Dynamic annual savings estimator based on company size and average wages.
  - Value comparison table vs legacy biometric hardware.
- **Multi-Industry Demo Presets**:
  - Tech & SaaS Agency
  - Retail & Supermarkets (₦ NGN / Multi-currency)

---

## 🚀 Quick Start Guide

### 1. Run with Python (Zero external dependencies)
```bash
python run.py
```
Or double-click `start_attendance.bat` on Windows.

### 2. Access the Application:
- **Admin Dashboard**: `http://localhost:5000/`
- **Office Kiosk Display**: `http://localhost:5000/kiosk`
- **Mobile Employee Scanner**: `http://localhost:5000/scan`
- **Staff Self-Service Portal**: `http://localhost:5000/portal`
- **Printable ID Badges**: `http://localhost:5000/badges`
- **Commercial B2B Pitch Landing**: `http://localhost:5000/pitch`

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | GET | System health & active company settings |
| `/api/kiosk/token` | GET | Current dynamic rotating QR token |
| `/api/attendance/quick-toggle` | POST | 1-touch Check-In / Check-Out toggle (Badge / PIN) |
| `/api/attendance/check-in` | POST | Log check-in with time & late calculation |
| `/api/attendance/check-out` | POST | Log check-out with overtime calculation |
| `/api/attendance/today` | GET | Today's real-time attendance matrix |
| `/api/attendance/history` | GET | Query past attendance by date & department |
| `/api/dashboard/stats` | GET | Metrics summary and live activity stream |
| `/api/dashboard/charts` | GET | Chart.js 7-day trend and department counts |
| `/api/employees` | GET, POST | List or register employees |
| `/api/employees/<id>` | GET, PUT, DELETE | Manage individual staff records |
| `/api/leaves` | GET, POST | List or submit leave applications |
| `/api/leaves/<id>/status` | PUT | Approve or reject leave request |
| `/api/payroll/summary` | GET | Monthly payroll breakdown |
| `/api/payroll/generate` | POST | Auto-compute hours, overtime, deductions & net pay |
| `/api/payroll/payslip/<ref>` | GET | Itemized payslip data for print/PDF |
| `/api/settings` | GET, POST | Update company branding, shifts & currency |
| `/api/demo/preset` | POST | Load Tech or Retail industry presets |

---

## 💼 Commercial Selling Strategy (How to Sell to Companies)

1. **The Pitch**: Most businesses lose 5–10% of payroll to buddy punching, lateness, and manual spreadsheet calculations. Show them the **ROI Calculator** on `/pitch`.
2. **The Demo**: Open `/kiosk` on a tablet and `/scan` on your phone to show 0.8-second anti-fraud check-in.
3. **The Close**: Open `/` and click **"Run Payroll Calculation"** to demonstrate instant itemized payslips and bank export.
