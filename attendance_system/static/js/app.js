/**
 * Admin Dashboard Controller & Interactive UI Manager
 */

let appSettings = null;
let trendChart = null;
let deptChart = null;

document.addEventListener('DOMContentLoaded', async () => {
  initLiveClock();
  await loadInitialSettings();
  await loadDashboardData();
  setupNavigationTabs();
  setupEventListeners();

  // Auto-refresh live attendance every 20 seconds
  setInterval(() => {
    const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab;
    if (activeTab === 'live') {
      loadTodayAttendance();
      loadDashboardStats();
    }
  }, 20000);
});

// Live Clock
function initLiveClock() {
  const timeEl = document.getElementById('header-live-time');
  const dateEl = document.getElementById('header-live-date');

  function update() {
    const now = new Date();
    if (timeEl) timeEl.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
  }
  update();
  setInterval(update, 1000);
}

// Initial Settings
async function loadInitialSettings() {
  try {
    const settings = await API.getSettings();
    appSettings = settings;

    // Update Company Headers & Titles
    document.querySelectorAll('.company-name-display').forEach(el => el.textContent = settings.name);
    document.querySelectorAll('.company-tagline-display').forEach(el => el.textContent = settings.tagline || '');
    
    // Currency displays
    document.querySelectorAll('.currency-symbol-display').forEach(el => el.textContent = settings.currency_symbol);

    // Populate Settings Form
    populateSettingsForm(settings);

    // Initialize Payroll with currency
    PayrollModule.init(settings.currency_symbol);

    // Populate Department dropdowns
    await loadDepartmentsDropdown();
  } catch (err) {
    console.error('Failed to load settings:', err);
  }
}

// Navigation Tabs
function setupNavigationTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  const panes = document.querySelectorAll('.tab-pane');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => {
        t.classList.remove('active', 'bg-indigo-600', 'text-white');
        t.classList.add('text-gray-400', 'hover:text-white', 'hover:bg-white/5');
      });
      tab.classList.add('active', 'bg-indigo-600', 'text-white');
      tab.classList.remove('text-gray-400', 'hover:text-white', 'hover:bg-white/5');

      const target = tab.dataset.tab;
      panes.forEach(pane => {
        if (pane.id === `tab-${target}`) {
          pane.classList.remove('hidden');
        } else {
          pane.classList.add('hidden');
        }
      });

      // Trigger sub-tab loads
      if (target === 'live') {
        loadTodayAttendance();
        loadDashboardStats();
      } else if (target === 'reports') {
        loadAttendanceHistory();
      } else if (target === 'payroll') {
        PayrollModule.loadPayroll();
      } else if (target === 'staff') {
        loadStaffDirectory();
      } else if (target === 'leaves') {
        loadLeaveRequests();
      }
    });
  });
}

// Load Dashboard Data & Stats
async function loadDashboardData() {
  await Promise.all([
    loadDashboardStats(),
    loadTodayAttendance(),
    initCharts()
  ]);
}

async function loadDashboardStats() {
  try {
    const stats = await API.getDashboardStats();
    
    const countTotal = document.getElementById('stat-total-staff');
    const countPresent = document.getElementById('stat-present-today');
    const ratePunctual = document.getElementById('stat-punctuality-rate');
    const countLate = document.getElementById('stat-late-today');
    const countLeaves = document.getElementById('stat-on-leave-today');
    const totalHours = document.getElementById('stat-total-hours');

    if (countTotal) countTotal.textContent = stats.total_employees;
    if (countPresent) countPresent.textContent = stats.present_today;
    if (ratePunctual) ratePunctual.textContent = stats.punctuality_rate + '%';
    if (countLate) countLate.textContent = stats.late_today;
    if (countLeaves) countLeaves.textContent = stats.on_leave_today;
    if (totalHours) totalHours.textContent = stats.total_hours_today + 'h';

    // Render Recent Live Activity Ticker
    renderActivityTicker(stats.recent_logs);
  } catch (err) {
    console.error('Error loading dashboard stats:', err);
  }
}

function renderActivityTicker(logs) {
  const container = document.getElementById('recent-activity-ticker');
  if (!container) return;

  if (!logs || logs.length === 0) {
    container.innerHTML = `<div class="text-xs text-gray-500 py-3 text-center">No recent activity logged yet.</div>`;
    return;
  }

  container.innerHTML = logs.map(l => {
    const isCheckIn = l.action === 'CHECK_IN';
    const isCheckOut = l.action === 'CHECK_OUT';
    const badgeColor = isCheckIn ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
                       isCheckOut ? 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20' :
                       'text-amber-400 bg-amber-500/10 border-amber-500/20';

    return `
      <div class="flex items-start gap-3 py-2.5 border-b border-white/5 last:border-0 text-xs">
        <span class="px-2 py-0.5 rounded font-mono font-bold text-[10px] uppercase border ${badgeColor}">
          ${l.action}
        </span>
        <div class="flex-1">
          <div class="text-gray-200">${l.details}</div>
          <div class="text-[10px] text-gray-500 font-mono mt-0.5">${l.timestamp.slice(11, 19)}</div>
        </div>
      </div>
    `;
  }).join('');
}

// Load Today's Attendance Table
async function loadTodayAttendance() {
  const tbody = document.getElementById('today-attendance-tbody');
  if (!tbody) return;

  try {
    const list = await API.getTodayAttendance();
    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-gray-400">No employee records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(item => {
      const status = item.attendance_status;
      let statusBadge = '';
      if (status === 'on_time') {
        statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">On-Time</span>`;
      } else if (status === 'late') {
        statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">Late (+${item.late_minutes}m)</span>`;
      } else if (status === 'present') {
        statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">Checked Out</span>`;
      } else if (status === 'on_leave') {
        statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">On Leave</span>`;
      } else {
        statusBadge = `<span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-gray-400 border border-slate-700">Absent</span>`;
      }

      return `
        <tr class="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
          <td class="px-5 py-4">
            <div class="flex items-center gap-3">
              <img src="${item.avatar_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + item.employee_code}" class="w-9 h-9 rounded-full object-cover border border-white/10" alt="">
              <div>
                <div class="font-semibold text-white">${item.first_name} ${item.last_name}</div>
                <div class="text-xs text-gray-400 font-mono">${item.employee_code} • ${item.designation}</div>
              </div>
            </div>
          </td>
          <td class="px-5 py-4 text-xs">
            <span class="px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-gray-300">
              ${item.department_name || 'General'}
            </span>
          </td>
          <td class="px-5 py-4 font-mono text-sm">
            ${item.check_in_time ? `
              <div class="text-white font-medium">${formatTime(item.check_in_time)}</div>
              <div class="text-[10px] text-gray-500 uppercase">${item.check_in_type}</div>
            ` : '<span class="text-gray-500 font-normal">--:--</span>'}
          </td>
          <td class="px-5 py-4 font-mono text-sm">
            ${item.check_out_time ? `
              <div class="text-white font-medium">${formatTime(item.check_out_time)}</div>
              <div class="text-[10px] text-gray-500 uppercase">${item.check_out_type || 'kiosk'}</div>
            ` : '<span class="text-gray-500 font-normal">--:--</span>'}
          </td>
          <td class="px-5 py-4 font-mono text-sm text-gray-300">
            ${item.total_hours ? `${item.total_hours} hrs` : '--'}
          </td>
          <td class="px-5 py-4">
            ${statusBadge}
          </td>
          <td class="px-5 py-4 text-right">
            <button onclick="quickCheckInOutPrompt(${item.employee_id}, '${item.first_name} ${item.last_name}', '${item.check_in_time ? 'out' : 'in'}')" class="px-3 py-1.5 rounded-lg ${item.check_in_time && !item.check_out_time ? 'bg-amber-600/20 hover:bg-amber-600 text-amber-300 hover:text-white border-amber-500/30' : 'bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border-indigo-500/30'} border text-xs font-semibold transition-all">
              ${item.check_in_time && !item.check_out_time ? 'Check Out' : 'Check In'}
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    console.error('Error loading today attendance:', err);
  }
}

// Charts Initialization (Chart.js)
async function initCharts() {
  try {
    const chartData = await API.getChartData();

    // 1. 7-Day Trend
    const ctx1 = document.getElementById('attendance-trend-chart');
    if (ctx1) {
      if (trendChart) trendChart.destroy();
      trendChart = new Chart(ctx1, {
        type: 'bar',
        data: {
          labels: chartData.trend.labels,
          datasets: [
            {
              label: 'On-Time / Present',
              data: chartData.trend.present,
              backgroundColor: '#10B981',
              borderRadius: 6
            },
            {
              label: 'Late Arrivals',
              data: chartData.trend.late,
              backgroundColor: '#F59E0B',
              borderRadius: 6
            },
            {
              label: 'Absences',
              data: chartData.trend.absent,
              backgroundColor: '#EF4444',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#9CA3AF', font: { family: 'Plus Jakarta Sans', size: 11 } } }
          },
          scales: {
            x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9CA3AF' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9CA3AF', stepSize: 2 } }
          }
        }
      });
    }

    // 2. Department Breakdown
    const ctx2 = document.getElementById('department-rate-chart');
    if (ctx2) {
      if (deptChart) deptChart.destroy();
      deptChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
          labels: chartData.departments.labels,
          datasets: [{
            data: chartData.departments.staff,
            backgroundColor: ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EC4899', '#6366F1'],
            borderColor: '#0F172A',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: '#9CA3AF', font: { family: 'Plus Jakarta Sans', size: 11 } } }
          }
        }
      });
    }
  } catch (err) {
    console.error('Error initializing charts:', err);
  }
}

// Attendance Reports Tab
async function loadAttendanceHistory() {
  const start = document.getElementById('report-start-date')?.value;
  const end = document.getElementById('report-end-date')?.value;
  const dept = document.getElementById('report-dept-filter')?.value;
  const search = document.getElementById('report-search-input')?.value;

  const tbody = document.getElementById('reports-history-tbody');
  if (!tbody) return;

  try {
    const list = await API.getAttendanceHistory({ start_date: start, end_date: end, department_id: dept, search });
    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-10 text-gray-400">No historical records match your filter.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(r => `
      <tr class="border-b border-white/5 hover:bg-white/[0.02] text-xs">
        <td class="px-4 py-3 font-mono text-gray-300">${formatDate(r.date)}</td>
        <td class="px-4 py-3">
          <div class="font-semibold text-white">${r.first_name} ${r.last_name}</div>
          <div class="text-[10px] text-gray-400 font-mono">${r.employee_code}</div>
        </td>
        <td class="px-4 py-3 text-gray-300">${r.department_name || 'General'}</td>
        <td class="px-4 py-3 font-mono text-emerald-400 font-medium">${formatTime(r.check_in_time)}</td>
        <td class="px-4 py-3 font-mono text-indigo-400 font-medium">${formatTime(r.check_out_time)}</td>
        <td class="px-4 py-3 font-mono text-gray-200">${r.total_hours || 0} hrs</td>
        <td class="px-4 py-3 font-mono text-rose-400">${r.late_minutes > 0 ? `+${r.late_minutes}m` : '0m'}</td>
        <td class="px-4 py-3">
          <span class="px-2 py-0.5 rounded-full font-semibold ${
            r.status === 'on_time' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
            r.status === 'late' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
            'bg-blue-500/10 text-blue-400 border border-blue-500/20'
          }">
            ${r.status}
          </span>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    Toast.show('Error loading reports: ' + err.message, 'error');
  }
}

// Staff Directory Tab
async function loadStaffDirectory() {
  const container = document.getElementById('staff-cards-grid');
  if (!container) return;

  try {
    const list = await API.getEmployees();
    container.innerHTML = list.map(e => `
      <div class="glass-card rounded-2xl p-5 relative overflow-hidden group hover:border-indigo-500/40 transition-all">
        <div class="flex items-start justify-between mb-4">
          <img src="${e.avatar_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + e.employee_code}" class="w-14 h-14 rounded-2xl object-cover border border-white/10 shadow-lg" alt="">
          <div class="flex flex-col items-end gap-1.5">
            <span class="px-2.5 py-1 rounded-full text-[11px] font-bold font-mono ${
              e.status === 'active' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
              e.status === 'on_leave' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
              'bg-slate-800 text-gray-400 border border-slate-700'
            }">
              ${e.status.toUpperCase()}
            </span>
            <span class="text-xs font-mono text-indigo-400 font-bold">${e.employee_code}</span>
          </div>
        </div>

        <h3 class="text-base font-bold text-white">${e.first_name} ${e.last_name}</h3>
        <p class="text-xs text-indigo-300 font-medium">${e.designation}</p>
        <p class="text-xs text-gray-400 mt-0.5">${e.department_name || 'General'}</p>

        <div class="mt-4 pt-3 border-t border-white/5 grid grid-cols-2 gap-2 text-xs">
          <div>
            <div class="text-gray-400 text-[10px] uppercase tracking-wider">Salary Plan</div>
            <div class="font-mono text-gray-200 mt-0.5">${e.salary_type === 'hourly' ? `${formatCurrency(e.hourly_rate, appSettings?.currency_symbol)}/hr` : `${formatCurrency(e.monthly_salary, appSettings?.currency_symbol)}/mo`}</div>
          </div>
          <div>
            <div class="text-gray-400 text-[10px] uppercase tracking-wider">PIN Code</div>
            <div class="font-mono text-gray-200 mt-0.5">•••• (${e.pin_code})</div>
          </div>
        </div>

        <div class="mt-4 flex items-center justify-between gap-2 pt-2">
          <button onclick="showEmployeeBadgeModal('${e.employee_code}', '${e.first_name} ${e.last_name}', '${e.designation}', '${e.department_name || 'General'}', '${e.qr_token}', '${e.avatar_url}')" class="flex-1 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white border border-indigo-500/30 text-xs font-semibold transition-all text-center">
            QR Badge
          </button>
          <button onclick="editEmployeePrompt(${e.id})" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-gray-300 hover:text-white border border-white/5 text-xs font-semibold transition-all">
            Edit
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    Toast.show('Error loading staff: ' + err.message, 'error');
  }
}

// Show QR Badge Modal
function showEmployeeBadgeModal(code, name, role, dept, qrToken, avatar) {
  const modal = document.getElementById('employee-badge-modal');
  const card = document.getElementById('modal-badge-card-container');
  if (!modal || !card) return;

  card.innerHTML = `
    <div class="id-badge-card p-6 flex flex-col items-center justify-between text-center mx-auto">
      <div class="w-full flex items-center justify-between border-b border-white/10 pb-3">
        <div class="flex items-center gap-1.5">
          <span class="w-5 h-5 rounded bg-indigo-600 flex items-center justify-center font-bold text-white text-xs">✦</span>
          <span class="text-xs font-bold text-white tracking-wide">${appSettings?.name || 'Apex Company'}</span>
        </div>
        <span class="text-[10px] text-gray-400 font-mono">STAFF PASS</span>
      </div>

      <div class="my-4 flex flex-col items-center">
        <img src="${avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + code}" class="w-20 h-20 rounded-2xl object-cover border-2 border-indigo-500/40 shadow-xl mb-3" alt="">
        <h4 class="text-lg font-bold text-white">${name}</h4>
        <div class="text-xs text-indigo-400 font-medium">${role}</div>
        <div class="text-[11px] text-gray-400 mt-0.5">${dept}</div>
        <div class="text-xs font-mono font-bold text-gray-300 mt-1 bg-white/5 px-2.5 py-0.5 rounded-full border border-white/10">${code}</div>
      </div>

      <div class="bg-white p-2.5 rounded-xl shadow-inner mb-2" id="modal-qr-canvas-holder"></div>
      
      <div class="text-[10px] text-gray-400 font-mono tracking-widest uppercase">
        Scan at Kiosk to Check In
      </div>
    </div>
  `;

  // Render QR Code
  setTimeout(() => {
    const holder = document.getElementById('modal-qr-canvas-holder');
    if (holder && window.QRCode) {
      holder.innerHTML = '';
      new QRCode(holder, {
        text: qrToken,
        width: 110,
        height: 110,
        colorDark: "#090d16",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
      });
    }
  }, 50);

  modal.classList.remove('hidden');
}

// Leave Requests Tab
async function loadLeaveRequests() {
  const tbody = document.getElementById('leave-requests-tbody');
  if (!tbody) return;

  try {
    const list = await API.getLeaves();
    if (!list || list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-gray-400">No leave requests submitted.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(l => `
      <tr class="border-b border-white/5 hover:bg-white/[0.02] text-xs">
        <td class="px-5 py-4">
          <div class="font-semibold text-white">${l.first_name} ${l.last_name}</div>
          <div class="text-gray-400 font-mono">${l.employee_code} • ${l.department_name || 'General'}</div>
        </td>
        <td class="px-5 py-4">
          <span class="px-2.5 py-1 rounded-full font-semibold uppercase text-[10px] bg-slate-800 border border-slate-700 text-gray-300">
            ${l.leave_type}
          </span>
        </td>
        <td class="px-5 py-4 font-mono text-gray-300">
          ${l.start_date} to ${l.end_date} (${l.total_days} days)
        </td>
        <td class="px-5 py-4 text-gray-300 max-w-xs truncate">
          ${l.reason || 'No description'}
        </td>
        <td class="px-5 py-4">
          <span class="px-2.5 py-1 rounded-full font-semibold text-xs ${
            l.status === 'approved' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
            l.status === 'rejected' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
            'bg-amber-500/10 text-amber-400 border border-amber-500/20'
          }">
            ${l.status.toUpperCase()}
          </span>
        </td>
        <td class="px-5 py-4 text-right">
          ${l.status === 'pending' ? `
            <div class="flex items-center justify-end gap-2">
              <button onclick="reviewLeave(${l.id}, 'approved')" class="px-3 py-1.5 rounded-lg bg-emerald-600/30 hover:bg-emerald-600 text-emerald-200 hover:text-white border border-emerald-500/30 text-xs font-semibold transition-all">
                Approve
              </button>
              <button onclick="reviewLeave(${l.id}, 'rejected')" class="px-3 py-1.5 rounded-lg bg-rose-600/30 hover:bg-rose-600 text-rose-200 hover:text-white border border-rose-500/30 text-xs font-semibold transition-all">
                Reject
              </button>
            </div>
          ` : `<span class="text-xs text-gray-500">Reviewed</span>`}
        </td>
      </tr>
    `).join('');
  } catch (err) {
    Toast.show('Error loading leaves: ' + err.message, 'error');
  }
}

async function reviewLeave(id, status) {
  try {
    await API.reviewLeave(id, status);
    Toast.show(`Leave request has been ${status}!`, status === 'approved' ? 'success' : 'info');
    AudioChime.playSuccess();
    loadLeaveRequests();
    loadDashboardStats();
  } catch (err) {
    Toast.show('Error updating leave: ' + err.message, 'error');
  }
}

// Quick Manual Check-In/Out Prompt
async function quickCheckInOutPrompt(empId, name, type) {
  const verb = type === 'in' ? 'Check In' : 'Check Out';
  if (!confirm(`Confirm ${verb} for ${name} at current time?`)) return;

  try {
    let res;
    if (type === 'in') {
      res = await API.checkIn({ employee_id: empId, check_in_type: 'admin_override' });
    } else {
      res = await API.checkOut({ employee_id: empId, check_out_type: 'admin_override' });
    }

    Toast.show(res.message, 'success');
    AudioChime.playSuccess();
    loadTodayAttendance();
    loadDashboardStats();
  } catch (err) {
    Toast.show('Action failed: ' + err.message, 'error');
  }
}

// Settings Form Handling
function populateSettingsForm(s) {
  const f = document.getElementById('company-settings-form');
  if (!f) return;

  f.name.value = s.name || '';
  f.tagline.value = s.tagline || '';
  f.currency_symbol.value = s.currency_symbol || '$';
  f.work_start_time.value = s.work_start_time || '09:00';
  f.work_end_time.value = s.work_end_time || '17:00';
  f.late_grace_minutes.value = s.late_grace_minutes || 15;
  f.overtime_multiplier.value = s.overtime_multiplier || 1.5;
  f.late_deduction_rate.value = s.late_deduction_rate || 5.0;
  f.qr_refresh_seconds.value = s.qr_refresh_seconds || 20;
}

async function loadDepartmentsDropdown() {
  try {
    const depts = await API.getDepartments();
    const selects = document.querySelectorAll('.dept-select');
    selects.forEach(sel => {
      const cur = sel.value;
      sel.innerHTML = '<option value="">Select Department</option>' + depts.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
      if (cur) sel.value = cur;
    });
  } catch (err) {
    console.error('Error loading depts dropdown:', err);
  }
}

// Event Listeners setup
function setupEventListeners() {
  // Settings Form Submit
  const settingsForm = document.getElementById('company-settings-form');
  if (settingsForm) {
    settingsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = {
        name: settingsForm.name.value,
        tagline: settingsForm.tagline.value,
        currency_symbol: settingsForm.currency_symbol.value,
        work_start_time: settingsForm.work_start_time.value,
        work_end_time: settingsForm.work_end_time.value,
        late_grace_minutes: parseInt(settingsForm.late_grace_minutes.value, 10),
        overtime_multiplier: parseFloat(settingsForm.overtime_multiplier.value),
        late_deduction_rate: parseFloat(settingsForm.late_deduction_rate.value),
        qr_refresh_seconds: parseInt(settingsForm.qr_refresh_seconds.value, 10)
      };

      try {
        const updated = await API.updateSettings(data);
        appSettings = updated;
        Toast.show('Company settings saved successfully!', 'success');
        AudioChime.playSuccess();
        loadInitialSettings();
      } catch (err) {
        Toast.show('Error saving settings: ' + err.message, 'error');
      }
    });
  }

  // Preset Loaders
  document.querySelectorAll('.btn-load-preset').forEach(btn => {
    btn.addEventListener('click', async () => {
      const preset = btn.dataset.preset;
      if (!confirm(`Switch demo data to preset: "${preset.toUpperCase()}"? This will reload sample staff and attendance.`)) return;
      try {
        Toast.show(`Loading ${preset} preset...`, 'info');
        const res = await API.loadDemoPreset(preset);
        Toast.show(res.message, 'success');
        AudioChime.playSuccess();
        setTimeout(() => window.location.reload(), 800);
      } catch (err) {
        Toast.show('Error loading preset: ' + err.message, 'error');
      }
    });
  });

  // Add Employee Form
  const addEmpForm = document.getElementById('add-employee-form');
  if (addEmpForm) {
    addEmpForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        first_name: addEmpForm.first_name.value,
        last_name: addEmpForm.last_name.value,
        email: addEmpForm.email.value,
        phone: addEmpForm.phone.value,
        designation: addEmpForm.designation.value,
        department_id: addEmpForm.department_id.value ? parseInt(addEmpForm.department_id.value, 10) : null,
        salary_type: addEmpForm.salary_type.value,
        hourly_rate: parseFloat(addEmpForm.hourly_rate.value || 25),
        monthly_salary: parseFloat(addEmpForm.monthly_salary.value || 4500),
        pin_code: addEmpForm.pin_code.value || '1234'
      };

      try {
        const res = await API.createEmployee(payload);
        Toast.show(`Employee ${res.first_name} added with code ${res.employee_code}!`, 'success');
        AudioChime.playSuccess();
        document.getElementById('add-employee-modal').classList.add('hidden');
        addEmpForm.reset();
        loadStaffDirectory();
        loadDashboardStats();
      } catch (err) {
        Toast.show('Error creating staff: ' + err.message, 'error');
      }
    });
  }

  // Reports Filter buttons
  const applyReportFilterBtn = document.getElementById('btn-apply-report-filter');
  if (applyReportFilterBtn) {
    applyReportFilterBtn.addEventListener('click', loadAttendanceHistory);
  }

  // Export Daily Reports to CSV
  const exportReportsCsvBtn = document.getElementById('btn-export-reports-csv');
  if (exportReportsCsvBtn) {
    exportReportsCsvBtn.addEventListener('click', async () => {
      try {
        const list = await API.getAttendanceHistory({});
        if (!list || !list.length) return Toast.show('No records to export', 'warning');
        
        const headers = ["Date", "Employee Code", "Full Name", "Department", "Check-in", "Check-out", "Total Hours", "Late (mins)", "Status"];
        const rows = list.map(r => [
          r.date,
          r.employee_code,
          `"${r.first_name} ${r.last_name}"`,
          `"${r.department_name || 'General'}"`,
          r.check_in_time || '',
          r.check_out_time || '',
          r.total_hours || 0,
          r.late_minutes || 0,
          r.status
        ]);

        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `attendance_records_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        Toast.show('Downloaded Attendance CSV', 'success');
      } catch (err) {
        Toast.show('CSV export error: ' + err.message, 'error');
      }
    });
  }
}

// Edit Employee placeholder
async function editEmployeePrompt(id) {
  try {
    const emp = await API.getEmployee(id);
    if (!emp) return;
    const newRole = prompt(`Edit Designation for ${emp.first_name}:`, emp.designation);
    if (newRole === null) return;
    const newSal = prompt(`Edit Monthly Salary or Hourly Rate:`, emp.salary_type === 'hourly' ? emp.hourly_rate : emp.monthly_salary);
    if (newSal === null) return;

    const data = {
      designation: newRole,
      hourly_rate: emp.salary_type === 'hourly' ? parseFloat(newSal) : emp.hourly_rate,
      monthly_salary: emp.salary_type === 'monthly' ? parseFloat(newSal) : emp.monthly_salary
    };

    await API.updateEmployee(id, data);
    Toast.show('Employee updated successfully!', 'success');
    AudioChime.playSuccess();
    loadStaffDirectory();
  } catch (err) {
    Toast.show('Error updating employee: ' + err.message, 'error');
  }
}
