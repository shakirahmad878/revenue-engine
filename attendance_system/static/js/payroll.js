/**
 * Payroll Calculation Engine, Payslip Renderer & Export Module
 */

const PayrollModule = {
  currentMonth: new Date().toISOString().slice(0, 7),
  cachedSummary: null,
  currencySymbol: '$',

  async init(currencySymbol = '$') {
    this.currencySymbol = currencySymbol;
    const monthSelect = document.getElementById('payroll-month-select');
    if (monthSelect) {
      this.populateMonthOptions(monthSelect);
      monthSelect.value = this.currentMonth;
      monthSelect.addEventListener('change', (e) => {
        this.currentMonth = e.target.value;
        this.loadPayroll();
      });
    }
    await this.loadPayroll();
  },

  populateMonthOptions(selectEl) {
    selectEl.innerHTML = '';
    const now = new Date();
    for (let i = 0; i < 6; i++) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const val = d.toISOString().slice(0, 7);
      const label = d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      const opt = document.createElement('option');
      opt.value = val;
      opt.textContent = label + (i === 0 ? ' (Current)' : '');
      selectEl.appendChild(opt);
    }
  },

  async loadPayroll() {
    try {
      const summary = await API.getPayrollSummary(this.currentMonth);
      this.cachedSummary = summary;
      this.renderSummaryStats(summary);
      this.renderTable(summary.records);
    } catch (err) {
      Toast.show('Failed to load payroll: ' + err.message, 'error');
    }
  },

  async generatePayroll() {
    try {
      Toast.show(`Calculating payroll for ${this.currentMonth}...`, 'info');
      const res = await API.generatePayroll(this.currentMonth);
      this.cachedSummary = res;
      this.renderSummaryStats(res);
      this.renderTable(res.records);
      Toast.show(`Payroll generated for ${res.count} staff members!`, 'success');
      AudioChime.playSuccess();
    } catch (err) {
      Toast.show('Error generating payroll: ' + err.message, 'error');
    }
  },

  renderSummaryStats(summary) {
    const netEl = document.getElementById('payroll-total-net');
    const otEl = document.getElementById('payroll-total-ot');
    const dedEl = document.getElementById('payroll-total-deductions');
    const countEl = document.getElementById('payroll-total-count');

    if (netEl) netEl.textContent = formatCurrency(summary.total_net_payout, this.currencySymbol);
    if (otEl) otEl.textContent = formatCurrency(summary.total_overtime_payout, this.currencySymbol);
    if (dedEl) dedEl.textContent = formatCurrency(summary.total_deductions, this.currencySymbol);
    if (countEl) countEl.textContent = summary.count;
  },

  renderTable(records) {
    const tbody = document.getElementById('payroll-table-body');
    if (!tbody) return;

    if (!records || records.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="9" class="px-6 py-12 text-center text-gray-400">
            <div class="flex flex-col items-center justify-center gap-2">
              <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              <span>No payroll generated yet for this period. Click "Run Payroll Calculation" to generate.</span>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = records.map(r => `
      <tr class="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
        <td class="px-5 py-4">
          <div class="flex items-center gap-3">
            <img src="${r.avatar_url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + r.employee_code}" class="w-9 h-9 rounded-full object-cover border border-white/10" alt="">
            <div>
              <div class="font-semibold text-white">${r.first_name} ${r.last_name}</div>
              <div class="text-xs text-gray-400 font-mono">${r.employee_code} • ${r.designation}</div>
            </div>
          </div>
        </td>
        <td class="px-5 py-4 text-xs">
          <span class="px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-gray-300 font-medium">
            ${r.salary_type === 'hourly' ? `${formatCurrency(r.hourly_rate, this.currencySymbol)}/hr` : 'Monthly Fixed'}
          </span>
        </td>
        <td class="px-5 py-4 text-sm font-mono text-gray-300">
          <div>${r.total_days_worked} days</div>
          <div class="text-xs text-gray-400">${r.total_regular_hours} hrs reg</div>
        </td>
        <td class="px-5 py-4 text-sm font-mono">
          <span class="${r.total_overtime_hours > 0 ? 'text-amber-400 font-semibold' : 'text-gray-400'}">
            ${r.total_overtime_hours}h (${formatCurrency(r.overtime_pay, this.currencySymbol)})
          </span>
        </td>
        <td class="px-5 py-4 text-sm font-mono text-rose-400">
          -${formatCurrency(r.late_deductions, this.currencySymbol)}
          <div class="text-xs text-gray-400">${r.total_late_minutes}m late</div>
        </td>
        <td class="px-5 py-4 text-sm font-mono font-bold text-emerald-400">
          ${formatCurrency(r.net_pay, this.currencySymbol)}
        </td>
        <td class="px-5 py-4 text-xs">
          <span class="px-2.5 py-1 rounded-full font-medium ${
            r.payment_status === 'paid' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
            r.payment_status === 'approved' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' :
            'bg-amber-500/10 text-amber-400 border border-amber-500/20'
          }">
            ${r.payment_status.toUpperCase()}
          </span>
        </td>
        <td class="px-5 py-4 text-right">
          <div class="flex items-center justify-end gap-2">
            <button onclick="PayrollModule.viewPayslip('${r.payslip_number}')" class="px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600 text-indigo-200 hover:text-white border border-indigo-500/30 text-xs font-semibold transition-all">
              Payslip
            </button>
            ${r.payment_status !== 'paid' ? `
              <button onclick="PayrollModule.markAsPaid(${r.id})" class="px-3 py-1.5 rounded-lg bg-emerald-600/30 hover:bg-emerald-600 text-emerald-200 hover:text-white border border-emerald-500/30 text-xs font-semibold transition-all" title="Mark as Paid">
                Pay
              </button>
            ` : ''}
          </div>
        </td>
      </tr>
    `).join('');
  },

  async markAsPaid(id) {
    try {
      await API.updatePayrollStatus(id, 'paid');
      Toast.show('Payment marked as Completed!', 'success');
      AudioChime.playSuccess();
      this.loadPayroll();
    } catch (err) {
      Toast.show('Error updating status: ' + err.message, 'error');
    }
  },

  async viewPayslip(payslipNum) {
    try {
      const data = await API.getPayslip(payslipNum);
      if (!data) throw new Error('Payslip not found');
      this.renderPayslipModal(data);
    } catch (err) {
      Toast.show('Error loading payslip: ' + err.message, 'error');
    }
  },

  renderPayslipModal(data) {
    const p = data.payslip;
    const c = data.company;
    const cur = c.currency_symbol || '$';

    const modal = document.getElementById('payslip-modal');
    const content = document.getElementById('payslip-modal-content');
    if (!modal || !content) return;

    content.innerHTML = `
      <div id="printable-payslip" class="bg-slate-900 border border-white/10 rounded-2xl p-6 sm:p-8 max-w-2xl mx-auto text-gray-200 shadow-2xl">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-white/10 pb-6 mb-6 gap-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white text-lg">✦</span>
              <h2 class="text-xl font-bold text-white">${c.name}</h2>
            </div>
            <p class="text-xs text-gray-400 mt-1">${c.tagline || 'Official Salary & Earnings Statement'}</p>
          </div>
          <div class="text-left sm:text-right font-mono">
            <span class="px-3 py-1 rounded-full text-xs font-semibold ${p.payment_status === 'paid' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}">
              ${p.payment_status.toUpperCase()}
            </span>
            <div class="text-xs text-gray-400 mt-2 font-mono">Ref: ${p.payslip_number}</div>
            <div class="text-xs text-gray-400">Period: ${p.period_month}</div>
          </div>
        </div>

        <!-- Employee Info -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-slate-800/50 p-4 rounded-xl border border-white/5 mb-6 text-xs">
          <div>
            <div class="text-gray-400">Employee Name</div>
            <div class="font-semibold text-white text-sm mt-0.5">${p.first_name} ${p.last_name}</div>
          </div>
          <div>
            <div class="text-gray-400">Employee ID</div>
            <div class="font-semibold text-indigo-400 text-sm mt-0.5 font-mono">${p.employee_code}</div>
          </div>
          <div>
            <div class="text-gray-400">Designation</div>
            <div class="font-semibold text-white mt-0.5">${p.designation}</div>
          </div>
          <div>
            <div class="text-gray-400">Department</div>
            <div class="font-semibold text-white mt-0.5">${p.department_name || 'General'}</div>
          </div>
        </div>

        <!-- Attendance Summary -->
        <div class="grid grid-cols-3 gap-3 mb-6 text-center text-xs">
          <div class="p-3 bg-slate-800/30 rounded-lg border border-white/5">
            <div class="text-gray-400">Days Worked</div>
            <div class="text-base font-bold text-white font-mono mt-1">${p.total_days_worked} Days</div>
          </div>
          <div class="p-3 bg-slate-800/30 rounded-lg border border-white/5">
            <div class="text-gray-400">Regular Hours</div>
            <div class="text-base font-bold text-white font-mono mt-1">${p.total_regular_hours} hrs</div>
          </div>
          <div class="p-3 bg-slate-800/30 rounded-lg border border-white/5">
            <div class="text-gray-400">Overtime Hours</div>
            <div class="text-base font-bold text-amber-400 font-mono mt-1">${p.total_overtime_hours} hrs</div>
          </div>
        </div>

        <!-- Earnings & Deductions Tables -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
          <!-- Earnings -->
          <div class="bg-slate-800/40 rounded-xl p-4 border border-white/5">
            <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-3 flex items-center justify-between">
              <span>Earnings</span>
              <span>Amount</span>
            </h4>
            <div class="space-y-2 text-xs">
              <div class="flex justify-between text-gray-300">
                <span>Base Salary (${p.salary_type})</span>
                <span class="font-mono">${formatCurrency(p.base_salary_earned, cur)}</span>
              </div>
              <div class="flex justify-between text-gray-300">
                <span>Overtime (${p.total_overtime_hours}h @ 1.5x)</span>
                <span class="font-mono text-amber-400">+${formatCurrency(p.overtime_pay, cur)}</span>
              </div>
              <div class="flex justify-between text-gray-300">
                <span>Performance Allowance</span>
                <span class="font-mono text-emerald-400">+${formatCurrency(p.bonus_allowance, cur)}</span>
              </div>
              <div class="border-t border-white/10 pt-2 flex justify-between font-bold text-white">
                <span>Gross Earnings</span>
                <span class="font-mono">${formatCurrency(p.base_salary_earned + p.overtime_pay + p.bonus_allowance, cur)}</span>
              </div>
            </div>
          </div>

          <!-- Deductions -->
          <div class="bg-slate-800/40 rounded-xl p-4 border border-white/5">
            <h4 class="text-xs font-bold uppercase tracking-wider text-rose-400 mb-3 flex items-center justify-between">
              <span>Deductions</span>
              <span>Amount</span>
            </h4>
            <div class="space-y-2 text-xs">
              <div class="flex justify-between text-gray-300">
                <span>Late Arrival (${p.total_late_minutes} mins)</span>
                <span class="font-mono text-rose-400">-${formatCurrency(p.late_deductions, cur)}</span>
              </div>
              <div class="flex justify-between text-gray-300">
                <span>Statutory Tax Withholding (5%)</span>
                <span class="font-mono text-rose-400">-${formatCurrency(p.tax_deductions, cur)}</span>
              </div>
              <div class="border-t border-white/10 pt-2 flex justify-between font-bold text-rose-300">
                <span>Total Deductions</span>
                <span class="font-mono">-${formatCurrency(p.late_deductions + p.tax_deductions, cur)}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Net Take Home -->
        <div class="bg-gradient-to-r from-indigo-900/50 to-emerald-900/50 border border-emerald-500/30 rounded-xl p-5 flex items-center justify-between">
          <div>
            <div class="text-xs text-emerald-300 font-semibold uppercase tracking-wider">Net Take-Home Pay</div>
            <div class="text-xs text-gray-400">Direct Deposit / Bank Transfer</div>
          </div>
          <div class="text-2xl sm:text-3xl font-black text-emerald-400 font-mono">
            ${formatCurrency(p.net_pay, cur)}
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center justify-between mt-8 pt-4 border-t border-white/10 no-print">
          <div class="text-xs text-gray-400">Generated on ${p.generated_at || 'Today'}</div>
          <div class="flex gap-3">
            <button onclick="PayrollModule.printPayslip()" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-white/10 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
              Print / Save PDF
            </button>
            <button onclick="document.getElementById('payslip-modal').classList.add('hidden')" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold">
              Close
            </button>
          </div>
        </div>
      </div>
    `;

    modal.classList.remove('hidden');
  },

  printPayslip() {
    const printContent = document.getElementById('printable-payslip');
    if (!printContent) return;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>Official Payslip</title>
          <script src="https://cdn.tailwindcss.com"></script>
          <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
          <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; background: #fff; color: #111; padding: 20px; }
            #printable-payslip { background: #fff !important; color: #111 !important; border: 1px solid #e2e8f0 !important; box-shadow: none !important; }
            .text-white { color: #0f172a !important; }
            .text-gray-400 { color: #64748b !important; }
            .bg-slate-900, .bg-slate-800\\/50, .bg-slate-800\\/40, .bg-slate-800\\/30 { background: #f8fafc !important; border-color: #e2e8f0 !important; }
            .text-emerald-400, .text-emerald-300 { color: #059669 !important; }
            .text-rose-400, .text-rose-300 { color: #dc2626 !important; }
            .text-amber-400 { color: #d97706 !important; }
            .text-indigo-400 { color: #4f46e5 !important; }
            .no-print { display: none !important; }
          </style>
        </head>
        <body>
          ${printContent.outerHTML}
          <script>
            window.onload = () => { window.print(); window.close(); }
          </script>
        </body>
      </html>
    `);
    printWindow.document.close();
  },

  exportBankCSV() {
    if (!this.cachedSummary || !this.cachedSummary.records.length) {
      Toast.show('No payroll records to export.', 'warning');
      return;
    }

    const headers = ["Employee Code", "Full Name", "Email", "Department", "Designation", "Salary Type", "Days Worked", "Regular Hours", "Overtime Hours", "Overtime Pay", "Late Deductions", "Tax Deductions", "Net Payout", "Payment Status", "Payslip Reference"];
    const rows = this.cachedSummary.records.map(r => [
      r.employee_code,
      `"${r.first_name} ${r.last_name}"`,
      r.email,
      `"${r.department_name || 'General'}"`,
      `"${r.designation}"`,
      r.salary_type,
      r.total_days_worked,
      r.total_regular_hours,
      r.total_overtime_hours,
      r.overtime_pay,
      r.late_deductions,
      r.tax_deductions,
      r.net_pay,
      r.payment_status,
      r.payslip_number
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `payroll_summary_${this.currentMonth}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    Toast.show(`Downloaded Payroll CSV for ${this.currentMonth}`, 'success');
  }
};
