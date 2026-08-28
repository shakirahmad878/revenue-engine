/**
 * Office Reception Kiosk Display Controller
 * Supports Dynamic Rotating Anti-Spoof QR & Webcam Badge Scanner
 */

let qrRefreshTimer = null;
let countdownInterval = null;
let currentSecondsLeft = 20;
let totalRefreshInterval = 20;
let html5QrScanner = null;
let isScanLocked = false;
let currentKioskMode = 'dynamic_qr'; // 'dynamic_qr' or 'webcam_scanner'

document.addEventListener('DOMContentLoaded', async () => {
  initKioskClock();
  await loadKioskSettings();
  setupKioskModeSwitch();
  startDynamicQRWorkflow();
  loadKioskLiveFeed();
  setupPinPad();

  // Poll live feed every 10s
  setInterval(loadKioskLiveFeed, 10000);
});

// Digital Live Clock
function initKioskClock() {
  const timeEl = document.getElementById('kiosk-live-time');
  const dateEl = document.getElementById('kiosk-live-date');
  function tick() {
    const now = new Date();
    if (timeEl) timeEl.textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  }
  tick();
  setInterval(tick, 1000);
}

// Load Settings
async function loadKioskSettings() {
  try {
    const s = await API.getSettings();
    document.querySelectorAll('.kiosk-company-name').forEach(el => el.textContent = s.name);
    document.querySelectorAll('.kiosk-work-hours').forEach(el => el.textContent = `${formatTime(s.work_start_time)} - ${formatTime(s.work_end_time)}`);
    totalRefreshInterval = s.qr_refresh_seconds || 20;
  } catch (err) {
    console.error('Kiosk settings load error:', err);
  }
}

// Switch between Mode A (Dynamic QR) and Mode B (Webcam Badge Scanner)
function setupKioskModeSwitch() {
  const btnQrMode = document.getElementById('btn-mode-qr');
  const btnCamMode = document.getElementById('btn-mode-cam');
  const viewQr = document.getElementById('kiosk-view-qr');
  const viewCam = document.getElementById('kiosk-view-cam');

  if (btnQrMode && btnCamMode) {
    btnQrMode.addEventListener('click', () => {
      currentKioskMode = 'dynamic_qr';
      btnQrMode.classList.add('bg-indigo-600', 'text-white');
      btnQrMode.classList.remove('text-gray-400', 'bg-slate-800');
      btnCamMode.classList.remove('bg-indigo-600', 'text-white');
      btnCamMode.classList.add('text-gray-400', 'bg-slate-800');

      viewQr.classList.remove('hidden');
      viewCam.classList.add('hidden');
      stopWebcamScanner();
      startDynamicQRWorkflow();
    });

    btnCamMode.addEventListener('click', () => {
      currentKioskMode = 'webcam_scanner';
      btnCamMode.classList.add('bg-indigo-600', 'text-white');
      btnCamMode.classList.remove('text-gray-400', 'bg-slate-800');
      btnQrMode.classList.remove('bg-indigo-600', 'text-white');
      btnQrMode.classList.add('text-gray-400', 'bg-slate-800');

      viewCam.classList.remove('hidden');
      viewQr.classList.add('hidden');
      stopDynamicQRWorkflow();
      startWebcamScanner();
    });
  }
}

// ----------------------------------------------------
// MODE A: DYNAMIC LIVE ROTATING QR CODE
// ----------------------------------------------------
async function startDynamicQRWorkflow() {
  stopDynamicQRWorkflow();
  await refreshKioskToken();

  countdownInterval = setInterval(() => {
    currentSecondsLeft--;
    updateCountdownUI(currentSecondsLeft);
    if (currentSecondsLeft <= 0) {
      refreshKioskToken();
    }
  }, 1000);
}

function stopDynamicQRWorkflow() {
  if (countdownInterval) clearInterval(countdownInterval);
  if (qrRefreshTimer) clearTimeout(qrRefreshTimer);
}

async function refreshKioskToken() {
  try {
    const data = await API.getKioskToken();
    currentSecondsLeft = data.seconds_remaining;
    totalRefreshInterval = data.refresh_interval;
    updateCountdownUI(currentSecondsLeft);

    // Generate Full Mobile URL or Token payload
    // If scanned by generic smartphone camera app, it opens the check-in web portal with token pre-filled!
    const scanUrl = `${window.location.origin}/scan?kiosk_token=${encodeURIComponent(data.token)}`;
    renderQRCode(scanUrl);

    const tokenDisplay = document.getElementById('kiosk-token-hash');
    if (tokenDisplay) tokenDisplay.textContent = data.token;
  } catch (err) {
    console.error('Error refreshing kiosk token:', err);
  }
}

function renderQRCode(text) {
  const container = document.getElementById('kiosk-qr-canvas');
  if (!container) return;
  container.innerHTML = '';
  
  if (window.QRCode) {
    new QRCode(container, {
      text: text,
      width: 250,
      height: 250,
      colorDark: "#090d16",
      colorLight: "#ffffff",
      correctLevel: QRCode.CorrectLevel.M
    });
  }
}

function updateCountdownUI(sec) {
  const secEl = document.getElementById('kiosk-countdown-sec');
  const barEl = document.getElementById('kiosk-countdown-bar');
  if (secEl) secEl.textContent = `${Math.max(0, sec)}s`;
  if (barEl) {
    const pct = Math.max(0, (sec / totalRefreshInterval) * 100);
    barEl.style.width = `${pct}%`;
  }
}

// ----------------------------------------------------
// MODE B: WEBCAM BADGE SCANNER
// ----------------------------------------------------
async function startWebcamScanner() {
  const qrReaderContainer = document.getElementById('kiosk-webcam-reader');
  if (!qrReaderContainer) return;

  if (typeof Html5Qrcode === 'undefined') {
    Toast.show('QR Scanner Library loading... please wait', 'info');
    return;
  }

  try {
    html5QrScanner = new Html5Qrcode("kiosk-webcam-reader");
    const cameras = await Html5Qrcode.getCameras();
    if (cameras && cameras.length) {
      const cameraId = cameras[0].id;
      await html5QrScanner.start(
        cameraId,
        {
          fps: 10,
          qrbox: { width: 260, height: 260 }
        },
        onQrCodeSuccess,
        onQrCodeError
      );
    } else {
      Toast.show('No webcam found on this device.', 'warning');
    }
  } catch (err) {
    console.error('Webcam start error:', err);
    Toast.show('Camera access error: ' + err.message, 'error');
  }
}

function stopWebcamScanner() {
  if (html5QrScanner) {
    html5QrScanner.stop().then(() => {
      html5QrScanner.clear();
      html5QrScanner = null;
    }).catch(err => console.warn('Scanner stop error:', err));
  }
}

async function onQrCodeSuccess(decodedText) {
  if (isScanLocked) return;
  isScanLocked = true;

  try {
    // Process Token or Employee Badge Code
    let token = decodedText.trim();
    // If URL passed in, extract query params
    if (token.startsWith('http')) {
      const url = new URL(token);
      token = url.searchParams.get('kiosk_token') || token;
    }

    const res = await API.quickToggle(token, 'badge_scan');
    
    if (res.success) {
      AudioChime.playSuccess();
      showScanSuccessModal(res);
      loadKioskLiveFeed();
    } else {
      AudioChime.playError();
      Toast.show(res.message || 'Badge not recognized', 'error');
    }
  } catch (err) {
    AudioChime.playError();
    Toast.show('Scan error: ' + err.message, 'error');
  } finally {
    // Unlock after 4 seconds debounce
    setTimeout(() => {
      isScanLocked = false;
    }, 4000);
  }
}

function onQrCodeError(errorMessage) {
  // Silent frame scan errors
}

// ----------------------------------------------------
// SCAN CONFIRMATION OVERLAY MODAL
// ----------------------------------------------------
function showScanSuccessModal(res) {
  const modal = document.getElementById('kiosk-success-modal');
  const emp = res.employee;
  const isCheckIn = res.action === 'check_in';
  const isCheckOut = res.action === 'check_out';

  if (!modal || !emp) return;

  const content = document.getElementById('kiosk-success-modal-content');
  const now = new Date();
  const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

  content.innerHTML = `
    <div class="p-8 text-center flex flex-col items-center">
      <!-- Glow Ring & Avatar -->
      <div class="relative mb-5">
        <div class="w-28 h-28 rounded-full ${isCheckIn ? 'bg-emerald-500/20 border-emerald-400' : 'bg-indigo-500/20 border-indigo-400'} border-4 flex items-center justify-center p-1 shadow-2xl">
          <img src="${emp.avatar_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + emp.employee_code}" class="w-full h-full rounded-full object-cover" alt="">
        </div>
        <span class="absolute bottom-0 right-0 w-8 h-8 rounded-full ${isCheckIn ? 'bg-emerald-500' : 'bg-indigo-600'} text-white flex items-center justify-center font-bold text-sm shadow-lg">
          ${isCheckIn ? '✓' : '⇥'}
        </span>
      </div>

      <!-- Action Badge -->
      <span class="px-4 py-1 rounded-full font-mono font-bold text-xs uppercase tracking-widest ${isCheckIn ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'} mb-2">
        ${isCheckIn ? 'CHECKED IN' : isCheckOut ? 'CHECKED OUT' : 'ATTENDANCE LOGGED'}
      </span>

      <h2 class="text-2xl sm:text-3xl font-extrabold text-white">${emp.first_name} ${emp.last_name}</h2>
      <p class="text-sm text-indigo-300 font-medium mt-0.5">${emp.designation} • ${emp.department_name || 'Staff'}</p>
      
      <!-- Timestamp Card -->
      <div class="mt-5 w-full bg-slate-800/80 border border-white/10 rounded-2xl p-4 flex items-center justify-around">
        <div>
          <div class="text-[10px] text-gray-400 uppercase tracking-wider">Time Recorded</div>
          <div class="text-xl font-bold font-mono text-white mt-0.5">${timeStr}</div>
        </div>
        <div class="h-8 w-px bg-white/10"></div>
        <div>
          <div class="text-[10px] text-gray-400 uppercase tracking-wider">Status</div>
          <div class="text-sm font-bold font-mono ${res.late_minutes > 0 ? 'text-rose-400' : 'text-emerald-400'} mt-0.5">
            ${res.late_minutes > 0 ? `Late (+${res.late_minutes}m)` : isCheckOut ? `${res.total_hours}h total` : 'On Time'}
          </div>
        </div>
      </div>

      <div class="text-xs text-gray-400 mt-6 flex items-center gap-1.5 font-mono">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
        Auto-dismissing in 3 seconds...
      </div>
    </div>
  `;

  modal.classList.remove('hidden');

  setTimeout(() => {
    modal.classList.add('hidden');
  }, 3500);
}

// ----------------------------------------------------
// PIN PAD FOR QUICK CHECK-IN
// ----------------------------------------------------
let enteredPin = "";

function setupPinPad() {
  const modal = document.getElementById('kiosk-pin-modal');
  const openBtn = document.getElementById('btn-open-pin-modal');
  const closeBtn = document.getElementById('btn-close-pin-modal');
  const display = document.getElementById('pin-display');

  if (openBtn) {
    openBtn.addEventListener('click', () => {
      enteredPin = "";
      updatePinDisplay();
      modal.classList.remove('hidden');
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
  }

  document.querySelectorAll('.pin-key').forEach(key => {
    key.addEventListener('click', () => {
      const val = key.dataset.val;
      if (val === 'C') {
        enteredPin = "";
      } else if (val === 'DEL') {
        enteredPin = enteredPin.slice(0, -1);
      } else if (enteredPin.length < 6) {
        enteredPin += val;
      }
      updatePinDisplay();
      if (enteredPin.length === 4) {
        submitPinCheckIn(enteredPin);
      }
    });
  });
}

function updatePinDisplay() {
  const display = document.getElementById('pin-display');
  if (!display) return;
  if (!enteredPin) {
    display.textContent = "Enter 4-Digit PIN";
    display.classList.add('text-gray-500');
  } else {
    display.textContent = "• ".repeat(enteredPin.length).trim();
    display.classList.remove('text-gray-500');
  }
}

async function submitPinCheckIn(pin) {
  try {
    const res = await API.quickToggle(pin, 'manual_pin');
    document.getElementById('kiosk-pin-modal').classList.add('hidden');
    enteredPin = "";
    updatePinDisplay();

    if (res.success) {
      AudioChime.playSuccess();
      showScanSuccessModal(res);
      loadKioskLiveFeed();
    } else {
      AudioChime.playError();
      Toast.show(res.message || 'Invalid PIN code', 'error');
    }
  } catch (err) {
    AudioChime.playError();
    Toast.show('PIN check-in failed: ' + err.message, 'error');
  }
}

// ----------------------------------------------------
// LIVE FEED SIDEBAR
// ----------------------------------------------------
async function loadKioskLiveFeed() {
  const container = document.getElementById('kiosk-live-feed-list');
  if (!container) return;

  try {
    const list = await API.getTodayAttendance();
    const checkedIn = list.filter(i => i.check_in_time);

    if (!checkedIn.length) {
      container.innerHTML = `<div class="text-xs text-gray-500 py-6 text-center">No check-ins recorded yet today.</div>`;
      return;
    }

    container.innerHTML = checkedIn.slice(0, 7).map(item => `
      <div class="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-white/5 text-xs">
        <div class="flex items-center gap-3">
          <img src="${item.avatar_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + item.employee_code}" class="w-8 h-8 rounded-full object-cover border border-white/10" alt="">
          <div>
            <div class="font-semibold text-white">${item.first_name} ${item.last_name}</div>
            <div class="text-[10px] text-gray-400 font-mono">${item.department_name || 'Staff'}</div>
          </div>
        </div>
        <div class="text-right font-mono">
          <div class="text-emerald-400 font-bold">${formatTime(item.check_in_time)}</div>
          <div class="text-[10px] ${item.late_minutes > 0 ? 'text-rose-400' : 'text-gray-400'}">${item.late_minutes > 0 ? `Late +${item.late_minutes}m` : 'On Time'}</div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error('Error loading kiosk live feed:', err);
  }
}
