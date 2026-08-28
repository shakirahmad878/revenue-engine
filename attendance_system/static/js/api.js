/**
 * Client API Layer & Utility Helpers for Staff Attendance SaaS
 */

const API_BASE = '/api';

const API = {
  async get(endpoint, params = {}) {
    const url = new URL(endpoint, window.location.origin);
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        url.searchParams.append(key, params[key]);
      }
    });
    try {
      const res = await fetch(url.toString(), {
        headers: { 'Accept': 'application/json' }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.message || 'API request failed');
      return data;
    } catch (err) {
      console.error(`GET ${endpoint} Error:`, err);
      throw err;
    }
  },

  async post(endpoint, body = {}) {
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.message || 'API request failed');
      return data;
    } catch (err) {
      console.error(`POST ${endpoint} Error:`, err);
      throw err;
    }
  },

  async put(endpoint, body = {}) {
    try {
      const res = await fetch(endpoint, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.message || 'API request failed');
      return data;
    } catch (err) {
      console.error(`PUT ${endpoint} Error:`, err);
      throw err;
    }
  },

  async delete(endpoint) {
    try {
      const res = await fetch(endpoint, {
        method: 'DELETE',
        headers: { 'Accept': 'application/json' }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || data.message || 'API request failed');
      return data;
    } catch (err) {
      console.error(`DELETE ${endpoint} Error:`, err);
      throw err;
    }
  },

  // Specific API calls
  getStatus: () => API.get(`${API_BASE}/status`),
  getKioskToken: () => API.get(`${API_BASE}/kiosk/token`),
  getSettings: () => API.get(`${API_BASE}/settings`),
  updateSettings: (data) => API.post(`${API_BASE}/settings`, data),
  getDashboardStats: () => API.get(`${API_BASE}/dashboard/stats`),
  getChartData: () => API.get(`${API_BASE}/dashboard/charts`),
  
  // Attendance
  getTodayAttendance: () => API.get(`${API_BASE}/attendance/today`),
  getAttendanceHistory: (params) => API.get(`${API_BASE}/attendance/history`, params),
  getMonthlyMatrix: (month) => API.get(`${API_BASE}/attendance/monthly-matrix`, { month }),
  checkIn: (data) => API.post(`${API_BASE}/attendance/check-in`, data),
  checkOut: (data) => API.post(`${API_BASE}/attendance/check-out`, data),
  quickToggle: (identifier, method = 'badge_scan', lat = null, lng = null) => 
    API.post(`${API_BASE}/attendance/quick-toggle`, { identifier, method, lat, lng }),

  // Employees & Depts
  getEmployees: (params) => API.get(`${API_BASE}/employees`, params),
  getEmployee: (id) => API.get(`${API_BASE}/employees/${id}`),
  getEmployeeHistory: (id) => API.get(`${API_BASE}/employees/${id}/history`),
  createEmployee: (data) => API.post(`${API_BASE}/employees`, data),
  updateEmployee: (id, data) => API.put(`${API_BASE}/employees/${id}`, data),
  deleteEmployee: (id) => API.delete(`${API_BASE}/employees/${id}`),
  getDepartments: () => API.get(`${API_BASE}/departments`),

  // Leaves
  getLeaves: (params) => API.get(`${API_BASE}/leaves`, params),
  submitLeave: (data) => API.post(`${API_BASE}/leaves`, data),
  reviewLeave: (id, status, reviewer = 'Admin') => API.put(`${API_BASE}/leaves/${id}/status`, { status, reviewer_name: reviewer }),

  // Payroll
  getPayrollSummary: (month) => API.get(`${API_BASE}/payroll/summary`, { month }),
  generatePayroll: (month) => API.post(`${API_BASE}/payroll/generate`, { month }),
  getPayslip: (idOrRef) => API.get(`${API_BASE}/payroll/payslip/${idOrRef}`),
  updatePayrollStatus: (id, status) => API.put(`${API_BASE}/payroll/${id}/status`, { status }),

  // Demo
  loadDemoPreset: (preset) => API.post(`${API_BASE}/demo/preset`, { preset })
};

// Global Toast Notifications
const Toast = {
  show(message, type = 'info', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const colors = {
      success: 'bg-emerald-500/90 border-emerald-400 text-white',
      error: 'bg-rose-500/90 border-rose-400 text-white',
      warning: 'bg-amber-500/90 border-amber-400 text-white',
      info: 'bg-indigo-600/90 border-indigo-400 text-white'
    };

    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ'
    };

    toast.className = `toast flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-md shadow-2xl text-sm font-medium ${colors[type] || colors.info}`;
    toast.innerHTML = `
      <span class="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center font-bold text-xs">${icons[type] || '•'}</span>
      <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
};

// Web Audio API Synthesizer (No external audio file downloads required!)
const AudioChime = {
  ctx: null,

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
  },

  playSuccess() {
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();

      const now = this.ctx.currentTime;
      // Elegant 2-tone chime (523.25Hz C5 -> 659.25Hz E5 -> 783.99Hz G5)
      const osc1 = this.ctx.createOscillator();
      const osc2 = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc1.type = 'sine';
      osc2.type = 'triangle';

      osc1.frequency.setValueAtTime(523.25, now);
      osc1.frequency.exponentialRampToValueAtTime(783.99, now + 0.18);

      osc2.frequency.setValueAtTime(659.25, now);
      osc2.frequency.exponentialRampToValueAtTime(1046.50, now + 0.22);

      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(this.ctx.destination);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 0.6);
      osc2.stop(now + 0.6);
    } catch (e) {
      console.warn('Audio chime error:', e);
    }
  },

  playError() {
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();

      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(220, now);
      osc.frequency.setValueAtTime(180, now + 0.15);

      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.4);
    } catch (e) {
      console.warn('Audio error chime:', e);
    }
  }
};

// Formatting helpers
function formatCurrency(amount, symbol = '$') {
  if (isNaN(amount) || amount === null) return `${symbol}0.00`;
  return `${symbol}${Number(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatTime(timeStr) {
  if (!timeStr) return '--:--';
  const parts = timeStr.split(':');
  if (parts.length < 2) return timeStr;
  let h = parseInt(parts[0], 10);
  const m = parts[1];
  const ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12;
  h = h ? h : 12;
  return `${h}:${m} ${ampm}`;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
