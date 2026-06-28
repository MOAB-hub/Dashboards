// ===================================================
// USER MANAGEMENT
// ===================================================
let users = HOSPITALS_CFG.map(h => ({name:h.leader, hospitalId:h.id, password:h.password}));

function renderUserTable() {
  const tbody = document.getElementById('user-tbody');
  tbody.innerHTML = users.map((u,i) => {
    const hosp = HOSPITALS_CFG.find(h=>h.id===u.hospitalId);
    return `<tr>
      <td>${u.name}</td>
      <td>${hosp ? hosp.facility : u.hospitalId}</td>
      <td><span style="font-family:monospace;background:#f0f4f8;padding:2px 8px;border-radius:4px">${u.password}</span></td>
      <td><button class="btn-del" onclick="deleteUser(${i})"><i class="bi bi-trash"></i> Remove</button></td>
    </tr>`;
  }).join('');
}

function addUser() {
  const name = document.getElementById('new-name').value.trim();
  const hospitalId = document.getElementById('new-hospital').value;
  const password = document.getElementById('new-password').value.trim();
  if (!name || !password) { alert('Please fill all fields'); return; }
  users.push({name, hospitalId, password});
  renderUserTable();
  document.getElementById('new-name').value = '';
  document.getElementById('new-password').value = '';
}

function deleteUser(i) {
  if (confirm('Remove this user?')) { users.splice(i,1); renderUserTable(); }
}

// ===================================================
// NAVIGATION
// ===================================================
let currentTarget = null;
let currentModalType = 'hospital';

function showLanding() {
  document.getElementById('landing').style.display = 'flex';
  document.getElementById('admin-panel').classList.remove('active');
  HOSPITALS_CFG.forEach(h => {
    const el = document.getElementById(h.id+'-dash');
    if (el) el.classList.remove('active');
  });
}

function promptHospital(hid) {
  currentTarget = hid;
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  document.getElementById('modal-title').textContent = h.facility;
  document.getElementById('modal-sub').textContent = "Enter your authorized password to access this dashboard.";
  document.getElementById('modal-pwd').value = '';
  document.getElementById('modal-error').style.display = 'none';
  document.getElementById('modal-submit').style.background = h.color;
  document.getElementById('pwd-modal').classList.add('active');
  setTimeout(()=>document.getElementById('modal-pwd').focus(), 100);
  currentModalType = 'hospital';
}

function promptAdmin() {
  currentTarget = 'admin';
  document.getElementById('modal-title').textContent = 'Admin Panel';
  document.getElementById('modal-sub').textContent = 'Enter the administrator password to manage users and access settings.';
  document.getElementById('modal-pwd').value = '';
  document.getElementById('modal-error').style.display = 'none';
  document.getElementById('modal-submit').style.background = '#1a1a2e';
  document.getElementById('pwd-modal').classList.add('active');
  setTimeout(()=>document.getElementById('modal-pwd').focus(), 100);
  currentModalType = 'admin';
}

function closeModal() {
  document.getElementById('pwd-modal').classList.remove('active');
}

function submitPassword() {
  const pwd = document.getElementById('modal-pwd').value;
  if (currentModalType === 'admin') {
    if (pwd === ADMIN_PASSWORD) {
      closeModal();
      document.getElementById('landing').style.display = 'none';
      renderUserTable();
      document.getElementById('admin-panel').classList.add('active');
    } else {
      document.getElementById('modal-error').style.display = 'block';
    }
    return;
  }
  const validUsers = users.filter(u => u.hospitalId === currentTarget && u.password === pwd);
  if (validUsers.length > 0) {
    closeModal();
    document.getElementById('landing').style.display = 'none';
    openDashboard(currentTarget);
  } else {
    document.getElementById('modal-error').style.display = 'block';
  }
}

document.getElementById('modal-pwd').addEventListener('keydown', e => {
  if (e.key === 'Enter') submitPassword();
});
document.getElementById('pwd-modal').addEventListener('click', e => {
  if (e.target === document.getElementById('pwd-modal')) closeModal();
});

// ===================================================
// DASHBOARD TABS
// ===================================================
function showTab(hid, tabName, btn) {
  document.querySelectorAll(`#${hid}-dash .tab-section`).forEach(s => s.classList.remove('active'));
  document.querySelectorAll(`#${hid}-dash .dash-nav button`).forEach(b => b.classList.remove('active'));
  document.getElementById(`${hid}-${tabName}`).classList.add('active');
  btn.classList.add('active');
}

// ===================================================
// CHART REGISTRY
// ===================================================
const chartRegistry = {};
function makeChart(id, config) {
  if (chartRegistry[id]) { chartRegistry[id].destroy(); }
  const ctx = document.getElementById(id);
  if (!ctx) return;
  chartRegistry[id] = new Chart(ctx, config);
  return chartRegistry[id];
}

// ===================================================
// FORMAT HELPERS
// ===================================================
function fmtDollar(v) { return '$' + Number(v||0).toLocaleString('en-US',{minimumFractionDigits:0,maximumFractionDigits:0}); }
const fmtN = v => (v||0).toLocaleString('en-US');
const fmtPct = v => (v||0).toFixed(1) + '%';

// ===================================================
// OPEN / BUILD DASHBOARD
// ===================================================
const dashBuilt = {};

function openDashboard(hid) {
  HOSPITALS_CFG.forEach(h => {
    const el = document.getElementById(h.id+'-dash');
    if (el) el.classList.remove('active');
  });
  const el = document.getElementById(hid+'-dash');
  if (el) el.classList.add('active');
  if (!dashBuilt[hid]) {
    buildDashboard(hid);
    dashBuilt[hid] = true;
  }
}

function buildDashboard(hid) {
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  buildOverview(hid);
  buildPayorMixSection(hid);
  buildRollingGrossSection(hid);
  buildRollingNetSection(hid);
  buildDenialsSection(hid);
  buildCoveredLives(hid, h.color);
  buildRegionalSection(hid);
  buildInsightsSection(hid);
}

// ===== OVERVIEW (Year + Program Type filters) =====
function buildOverview(hid) {
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  const filter = getFilter(hid, 'overview');
  const recs = filterRecords(hid, {year: filter.year, programType: filter.programType});
  const hosp = aggregateRecords(recs);
  const container = document.getElementById(hid+'-overview');
  injectFilterBar(container, hid, 'overview', h.color, true);

  buildKPIs(hid, hosp, h.color);
  buildDonut(hid, hosp, h.color);
  // Program Type Mix chart always reflects the full program breakdown for the selected year
  const yearHosp = aggregateRecords(filterRecords(hid, {year: filter.year}));
  buildProgram(hid, yearHosp, h.color);
  buildTrend(hid, hosp, h.color);
}

// ===== KPIs =====
function buildKPIs(hid, hosp, color) {
  const t = hosp.totals;
  const revPerDay = t.los ? t.net / t.los : 0;
  const avgLos = t.admits ? t.los / t.admits : 0;
  const margin = t.gross ? (t.net / t.gross * 100) : 0;
  const kpis = [
    {label:'Total Patient Days', value:fmtN(t.los), sub:'Selected scope', icon:'bi-calendar-check'},
    {label:'Total Admits', value:fmtN(t.admits), sub:'Selected scope', icon:'bi-person-check'},
    {label:'Avg Length of Stay', value:avgLos.toFixed(1)+' days', sub:'Per admission', icon:'bi-clock-history'},
    {label:'Total Gross Revenue', value:fmtDollar(t.gross), sub:'All Payors', icon:'bi-cash-stack'},
    {label:'Total Net Revenue', value:fmtDollar(t.net), sub:'Gross + Contractual Adj.', icon:'bi-currency-dollar'},
    {label:'Net Rev / Patient Day', value:fmtDollar(revPerDay), sub:'Blended rate', icon:'bi-graph-up'},
    {label:'Net Margin %', value:fmtPct(margin), sub:'Net ÷ Gross', icon:'bi-percent'},
  ];
  const el = document.getElementById(hid+'-kpis');
  el.innerHTML = kpis.map(k=>`
    <div class="kpi-card" style="--hcolor:${color}">
      <div class="label"><i class="bi ${k.icon}"></i> ${k.label}</div>
      <div class="value">${k.value}</div>
      <div class="sub">${k.sub}</div>
    </div>`).join('');
}

// ===== DONUT =====
function buildDonut(hid, hosp, color) {
  const pm = hosp.payor_mix;
  const labels = Object.keys(pm).sort((a,b)=>pm[b].pct-pm[a].pct);
  const vals = labels.map(l=>pm[l].los);
  const colors = labels.map(l=>FC_COLORS[l]||'#999');
  const total = vals.reduce((a,b)=>a+b,0);
  makeChart(hid+'-donut', {
    type:'doughnut',
    data:{ labels, datasets:[{data:vals, backgroundColor:colors, borderWidth:2, borderColor:'#fff'}] },
    options:{
      responsive:true, maintainAspectRatio:true,
      plugins:{
        legend:{position:'right',labels:{font:{size:11},boxWidth:12}},
        tooltip:{callbacks:{label:ctx=>` ${ctx.label}: ${fmtN(ctx.raw)} days (${fmtPct(total ? ctx.raw/total*100 : 0)})` }}
      }
    }
  });
}

// ===== PROGRAM MIX =====
function buildProgram(hid, hosp, color) {
  const pm = hosp.program_mix;
  const labels = PROGRAM_TYPES.filter(p => pm[p]).concat(Object.keys(pm).filter(p=>!PROGRAM_TYPES.includes(p)));
  const vals = labels.map(l=>pm[l].los);
  const netVals = labels.map(l=>pm[l].net);
  makeChart(hid+'-program', {
    type:'bar',
    data:{
      labels,
      datasets:[
        {label:'Patient Days',data:vals,backgroundColor:color+'cc',yAxisID:'y'},
        {label:'Net Revenue',data:netVals,backgroundColor:'#00695c88',yAxisID:'y1'},
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:true,
      plugins:{legend:{position:'top',labels:{font:{size:11}}}},
      scales:{
        y:{position:'left',title:{display:true,text:'Patient Days'},ticks:{callback:v=>fmtN(v)}},
        y1:{position:'right',title:{display:true,text:'Net Revenue'},grid:{drawOnChartArea:false},ticks:{callback:v=>fmtDollar(v)}}
      }
    }
  });
}

// ===== QUARTERLY TREND =====
function buildTrend(hid, hosp, color) {
  const qs = QUARTERS;
  const los = qs.map(q=>hosp.qtr_summary[q]?.los||0);
  const net = qs.map(q=>hosp.qtr_summary[q]?.net||0);
  makeChart(hid+'-trend', {
    type:'bar',
    data:{
      labels:qs,
      datasets:[
        {type:'bar',label:'Patient Days',data:los,backgroundColor:'#2e7d32',yAxisID:'y',order:2},
        {type:'line',label:'Net Revenue',data:net,borderColor:'#0077b6',backgroundColor:'#0077b622',yAxisID:'y1',order:1,tension:.3,fill:true,pointRadius:5},
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:'top'}},
      scales:{
        y:{title:{display:true,text:'Patient Days'},ticks:{callback:v=>fmtN(v)}},
        y1:{position:'right',title:{display:true,text:'Net Revenue'},grid:{drawOnChartArea:false},ticks:{callback:v=>fmtDollar(v)}}
      }
    }
  });
}
