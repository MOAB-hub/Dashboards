// ===================================================
// DATA
// ===================================================
const STORAGE_KEY = 'hospital_dashboard_data_v2';

function round2(v) { return Math.round((v||0)*100)/100; }
function yearOf(qtr) { return '20' + qtr.slice(-2); }

// On load: uploaded data in localStorage is always master.
function loadData() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      const valid = Array.isArray(parsed) && parsed.length > 0 &&
        typeof parsed[0].f === 'string' && typeof parsed[0].g === 'number';
      if (valid) return parsed;
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch(e) { localStorage.removeItem(STORAGE_KEY); }
  return JSON.parse(JSON.stringify(GROUPED_RECORDS));
}

const RAW_DATA = loadData();

function saveData() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(RAW_DATA)); }
  catch(e) { console.warn('localStorage save failed:', e); }
}

const QUARTERS = ["1Q25","2Q25","3Q25","4Q25","1Q26"];
const PROGRAM_TYPES = ["Inpatient","PHP","IOP","OP"];
const FC_COLORS = {
  "Commercial": "#1a6eb5",
  "Medicare": "#2e7d32",
  "Medicare Advantage": "#6a1b9a",
  "Managed Medicaid": "#e65100",
  "Medicaid": "#c62828",
  "Other Governmental": "#00695c",
  "Self Pay": "#757575"
};
const CHART_PALETTE = ["#1a6eb5","#2e7d32","#6a1b9a","#c62828","#e65100","#00695c","#0077b6"];

const HOSPITALS_CFG = [{"id":"h1","facility":"Carrollton Springs","leader":"Donald Duck","password":"dduck","color":"#1a6eb5","colorLight":"#e8f0fa","region":"Central","location":"Carrollton, TX"},{"id":"h2","facility":"Collin Springs","leader":"John Smith","password":"jsmith","color":"#2e7d32","colorLight":"#e8f5e9","region":"Central","location":"Carrollton, TX"},{"id":"h3","facility":"Columbus Springs Dublin","leader":"Brooke Hogan","password":"bhogan","color":"#6a1b9a","colorLight":"#f3e5f5","region":"East","location":"Dublin, OH"},{"id":"h4","facility":"Columbus Springs East","leader":"Mickey Mouse","password":"mmouse","color":"#c62828","colorLight":"#ffebee","region":"East","location":"Columbus, OH"}];
const ADMIN_PASSWORD = "buttercup";

// ===================================================
// AGGREGATION ENGINE
// Records are pre-grouped at (facility, quarter, program type,
// financial class, payor) granularity with fields:
//   f=facility, q=quarter, pt=program type, fc=financial class,
//   p=payor, los, g=gross charges, n=net revenue (Gross + Contractual Adj.),
//   d=denial adjustments, a=admits
// ===================================================
function filterRecords(hid, opts) {
  opts = opts || {};
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  return RAW_DATA.filter(r => {
    if (r.f !== h.facility) return false;
    if (opts.programType && opts.programType !== 'All' && r.pt !== opts.programType) return false;
    if (opts.year && opts.year !== 'All' && yearOf(r.q) !== opts.year) return false;
    return true;
  });
}

function aggregateRecords(recs) {
  const agg = (arr, field) => arr.reduce((s,r)=>s+(r[field]||0), 0);
  const groupBy = (arr, key) => arr.reduce((g,r)=>{ (g[r[key]]=g[r[key]]||[]).push(r); return g; }, {});
  const totLOS = agg(recs, 'los');

  // Payor mix by Financial Class
  const fcGroups = groupBy(recs, 'fc');
  const payor_mix = {};
  Object.entries(fcGroups).forEach(([fc, arr]) => {
    const los = agg(arr,'los'), gross = agg(arr,'g'), net = agg(arr,'n'), admits = agg(arr,'a');
    payor_mix[fc] = {
      los, gross: round2(gross), net: round2(net), admits,
      pct: totLOS ? Math.round(los/totLOS*1000)/10 : 0,
      rev_per_day: los ? Math.round(net/los*100)/100 : 0,
      avg_los: admits ? Math.round(los/admits*10)/10 : 0
    };
  });

  // Top 5 payors by gross / net
  const payorGroups = groupBy(recs, 'p');
  const payorTotals = Object.entries(payorGroups).map(([p,arr])=>({p, gross:agg(arr,'g'), net:agg(arr,'n')}));
  const top5g = [...payorTotals].sort((a,b)=>b.gross-a.gross).slice(0,5).map(x=>x.p);
  const top5n = [...payorTotals].sort((a,b)=>b.net-a.net).slice(0,5).map(x=>x.p);
  const mkTop5 = (payors, totalField, srcField) => {
    const res = {};
    payors.forEach(p => {
      const arr = payorGroups[p] || [];
      const qtr_los = {};
      QUARTERS.forEach(q => { qtr_los[q] = agg(arr.filter(r=>r.q===q), 'los'); });
      res[p] = {qtr_los, [totalField]: round2(agg(arr, srcField))};
    });
    return res;
  };

  // Quarterly summary
  const qtrGroups = groupBy(recs, 'q');
  const qtr_summary = {};
  QUARTERS.forEach(q => {
    const arr = qtrGroups[q] || [];
    qtr_summary[q] = {los: agg(arr,'los'), gross: round2(agg(arr,'g')), net: round2(agg(arr,'n')), admits: agg(arr,'a')};
  });

  // Program type mix
  const ptGroups = groupBy(recs, 'pt');
  const program_mix = {};
  Object.entries(ptGroups).forEach(([pt, arr]) => {
    program_mix[pt] = {los: agg(arr,'los'), gross: round2(agg(arr,'g')), net: round2(agg(arr,'n')), admits: agg(arr,'a')};
  });

  // Denial detail — 2026 YTD (1Q26)
  const recs2026 = recs.filter(r => r.q === '1Q26');
  const pg2026 = groupBy(recs2026, 'p');
  const denial_rate = {};
  Object.entries(pg2026).forEach(([p, arr]) => {
    const gross = agg(arr,'g'), net = agg(arr,'n'), denial = agg(arr,'d'), los = agg(arr,'los'), admits = agg(arr,'a');
    denial_rate[p] = {
      gross: round2(gross), net: round2(net), denial_adj: round2(denial),
      rate: gross ? Math.round(denial/gross*10000)/100 : 0, los, admits
    };
  });

  return {
    payor_mix,
    top5_gross: mkTop5(top5g, 'total_gross', 'g'), top5_gross_payors: top5g,
    top5_net: mkTop5(top5n, 'total_net', 'n'), top5_net_payors: top5n,
    denial_rate, qtr_summary, program_mix,
    totals: {los: totLOS, gross: round2(agg(recs,'g')), net: round2(agg(recs,'n')), admits: agg(recs,'a')}
  };
}

// ===================================================
// PER-SECTION FILTER STATE  (defaults: Inpatient / 2026 YTD)
// ===================================================
const sectionFilters = {};
function getFilter(hid, section) {
  const key = hid + '|' + section;
  if (!sectionFilters[key]) sectionFilters[key] = {programType: 'Inpatient', year: '2026'};
  return sectionFilters[key];
}

function programTypeSelectorHTML(hid, section, color) {
  const f = getFilter(hid, section);
  const opts = PROGRAM_TYPES.concat(['All']).map(pt => {
    const label = pt === 'All' ? 'All Program Types' : pt;
    return `<option value="${pt}" ${f.programType===pt?'selected':''}>${label}</option>`;
  }).join('');
  return `<div style="display:flex;align-items:center;gap:8px">
    <label style="font-size:.74rem;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.4px">Program Type</label>
    <select onchange="onProgramTypeChange('${hid}','${section}',this.value)" style="border:1.5px solid #d8e0e8;border-radius:8px;padding:6px 14px;font-size:.83rem;color:${color};font-weight:600;background:#fff;cursor:pointer">
      ${opts}
    </select>
  </div>`;
}

function yearToggleHTML(hid, color) {
  const f = getFilter(hid, 'overview');
  const mk = (val, label, side) => `<button onclick="onYearChange('${hid}','${val}')" style="padding:7px 18px;font-size:.8rem;font-weight:700;border:1.5px solid ${color};cursor:pointer;background:${f.year===val?color:'#fff'};color:${f.year===val?'#fff':color};${side==='l'?'border-radius:8px 0 0 8px;border-right:none':'border-radius:0 8px 8px 0'}">${label}</button>`;
  return `<div style="display:inline-flex">${mk('2026','2026 YTD','l')}${mk('2025','2025 Full Year','r')}</div>`;
}

function injectFilterBar(container, hid, section, color, includeYear) {
  const cls = 'filter-bar-' + section;
  const existing = container.querySelector(':scope > .' + cls);
  const html = `<div class="${cls}" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;background:#fff;border-radius:12px;padding:14px 20px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06)">
    ${includeYear ? yearToggleHTML(hid, color) : '<div></div>'}
    ${programTypeSelectorHTML(hid, section, color)}
  </div>`;
  if (existing) existing.outerHTML = html;
  else container.insertAdjacentHTML('afterbegin', html);
}

function onProgramTypeChange(hid, section, val) {
  getFilter(hid, section).programType = val;
  rebuildSection(hid, section);
}
function onYearChange(hid, year) {
  getFilter(hid, 'overview').year = year;
  buildOverview(hid);
}
function rebuildSection(hid, section) {
  const map = {
    overview: buildOverview,
    payorMix: buildPayorMixSection,
    rollingGross: buildRollingGrossSection,
    rollingNet: buildRollingNetSection,
    denials: buildDenialsSection,
    regional: buildRegionalSection,
    insights: buildInsightsSection
  };
  if (map[section]) map[section](hid);
}
