/**
 * Unified School Attendance, Safety, Parent WhatsApp & Faculty Payroll API Client
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

  // 1. School & Settings
  getStatus: () => API.get(`${API_BASE}/school/status`),
  getSettings: () => API.get(`${API_BASE}/school/settings`),
  updateSettings: (data) => API.post(`${API_BASE}/school/settings`, data),
  getMorningStrength: (date) => API.get(`${API_BASE}/school/morning-strength`, { date }),
  
  // 2. Student Gate & Bus Scanning
  gateScan: (identifier, scanned_by = 'Main Gate Kiosk Laser') => 
    API.post(`${API_BASE}/school/gate-scan`, { identifier, scanned_by }),
  busScan: (identifier, bus_route = 'Route #4', scan_type = 'board', conductor = 'Bus Conductor') =>
    API.post(`${API_BASE}/school/bus-scan`, { identifier, bus_route, scan_type, conductor_name: conductor }),
  
  // 3. Parent WhatsApp Broadcasts
  send830AbsenceBroadcast: (date) => API.post(`${API_BASE}/school/send-830-absence`, { date }),
  sendEmergencyBroadcast: (title, message, target = 'all_parents', class_id = null, bus_route = null) =>
    API.post(`${API_BASE}/school/emergency-broadcast`, { title, message, target, class_id, bus_route }),
  getNotifications: () => API.get(`${API_BASE}/school/notifications`),

  // 4. Students & Classes
  getClasses: () => API.get(`${API_BASE}/school/classes`),
  getBusRoutes: () => API.get(`${API_BASE}/school/bus-routes`),
  getStudents: (params) => API.get(`${API_BASE}/school/students`, params),
  getStudent: (id) => API.get(`${API_BASE}/school/students/${id}`),
  getCbseRegister: (month, class_id) => API.get(`${API_BASE}/school/cbse-register`, { month, class_id }),

  // 5. Teachers & Staff Attendance
  getTeachers: (search) => API.get(`${API_BASE}/teachers`, { search }),
  getTeacherTodayAttendance: () => API.get(`${API_BASE}/teachers/today`),
  staffScan: (identifier) => API.post(`${API_BASE}/school/staff-scan`, { identifier }),
  createTeacher: (data) => API.post(`${API_BASE}/teachers`, data),
  updateTeacher: (id, data) => API.put(`${API_BASE}/teachers/${id}`, data),

  // 6. Teacher Leaves
  getLeaves: (status) => API.get(`${API_BASE}/leaves`, { status }),
  submitLeave: (data) => API.post(`${API_BASE}/leaves`, data),
  reviewLeave: (id, status, reviewer = 'Principal') => API.put(`${API_BASE}/leaves/${id}/status`, { status, reviewer }),

  // 7. Teacher & Staff Payroll
  getPayrollSummary: (month) => API.get(`${API_BASE}/payroll/summary`, { month }),
  generatePayroll: (month) => API.post(`${API_BASE}/payroll/generate`, { month }),
  getPayslip: (ref) => API.get(`${API_BASE}/payroll/payslip/${ref}`),
  updatePayrollStatus: (id, status) => API.put(`${API_BASE}/payroll/${id}/status`, { status }),

  // 8. Demo reset
  resetDemo: () => API.post(`${API_BASE}/school/reset-demo`, {})
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

// Web Audio API Synthesizer (High-quality Ding Chime)
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
      const osc1 = this.ctx.createOscillator();
      const osc2 = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc1.type = 'sine';
      osc2.type = 'triangle';

      osc1.frequency.setValueAtTime(587.33, now);
      osc1.frequency.exponentialRampToValueAtTime(880.00, now + 0.18);

      osc2.frequency.setValueAtTime(739.99, now);
      osc2.frequency.exponentialRampToValueAtTime(1174.66, now + 0.22);

      gain.gain.setValueAtTime(0.35, now);
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
      osc.frequency.setValueAtTime(160, now + 0.2);

      gain.gain.setValueAtTime(0.3, now);
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

function formatCurrency(val, symbol = '₹') {
  if (val === null || val === undefined) return `${symbol}0.00`;
  return `${symbol}${Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
