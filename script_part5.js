// ===================================================
// FILE UPLOAD (SheetJS) — rebuilds GROUPED records from "Base Data" sheet
// Net Revenue is recomputed as: Total Gross Charges + Contractual Adjustments
// ===================================================
function handleUpload(input) {
  const file = input.files[0];
  if (!file) return;
  const hid = input.id.replace('-file','');
  const statusEl = document.getElementById(hid+'-upload-status');
  statusEl.innerHTML = '<i class="bi bi-hourglass-split"></i> Reading file...';

  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const wb = XLSX.read(e.target.result, {type:'array',cellDates:true});
      const ws = wb.Sheets['Base Data'];
      if (!ws) { statusEl.innerHTML = '<span style="color:red"><i class="bi bi-x-circle"></i> Sheet "Base Data" not found.</span>'; return; }
      const rows = XLSX.utils.sheet_to_json(ws, {header:1,raw:false});
      rebuildFromRows(rows, hid, statusEl);
    } catch(err) {
      statusEl.innerHTML = `<span style="color:red"><i class="bi bi-x-circle"></i> Error: ${err.message}</span>`;
    }
  };
  reader.readAsArrayBuffer(file);
}

function rebuildFromRows(rows, hid, statusEl) {
  const headers = rows[0];
  const COL = {};
  headers.forEach((h,i)=>{ COL[h]=i; });

  const hasContractual = COL['Contractual Adjustments'] !== undefined;
  if (!hasContractual) {
    statusEl.innerHTML = `<span style="color:#dc3545"><i class="bi bi-x-circle"></i> Upload aborted: column "Contractual Adjustments" not found. Net Revenue on this dashboard is defined as Total Gross Charges + Contractual Adjustments and requires that column.</span>`;
    return;
  }

  // Re-aggregate uploaded rows into the same compact grouped-record shape
  // used by GROUPED_RECORDS: {f,q,pt,fc,p,los,g,n,d,a}
  const groups = {};
  let rowCount = 0;
  for (let i=1;i<rows.length;i++) {
    const r = rows[i];
    const fac = r[COL['Facility Name']];
    if (!fac) continue;
    rowCount++;
    const qtr = r[COL['QTR']];
    const pt = r[COL['Program Type']] || 'Unknown';
    const fc = r[COL['Financial Class']];
    const payor = r[COL['Payor Summary']];
    const los = parseFloat(r[COL['LOS']])||0;
    const gross = parseFloat(r[COL['Total Gross Charges']])||0;
    const contr = parseFloat(r[COL['Contractual Adjustments']])||0;
    const net = gross + contr; // Net Revenue = Gross + Contractual Adjustments
    const denial = Math.abs(parseFloat(r[COL['Denial Adjustments']])||0);
    const admits = parseFloat(r[COL['Admits']])||0;

    const key = [fac,qtr,pt,fc,payor].join('|');
    if (!groups[key]) groups[key] = {f:fac,q:qtr,pt,fc,p:payor,los:0,g:0,n:0,d:0,a:0};
    const g = groups[key];
    g.los += los; g.g += gross; g.n += net; g.d += denial; g.a += admits;
  }

  const newRecords = Object.values(groups).map(g => ({
    f:g.f, q:g.q, pt:g.pt, fc:g.fc, p:g.p,
    los:g.los, g:round2(g.g), n:round2(g.n), d:round2(g.d), a:g.a
  }));

  // Replace RAW_DATA contents in place (it's a const array reference)
  RAW_DATA.length = 0;
  newRecords.forEach(r => RAW_DATA.push(r));
  saveData();

  // Force full rebuild of every dashboard (data changed for all facilities)
  Object.keys(dashBuilt).forEach(h => { dashBuilt[h] = false; });
  buildDashboard(hid);
  dashBuilt[hid] = true;

  statusEl.innerHTML = `<span style="color:green"><i class="bi bi-check2-all"></i> Upload complete — ${rowCount.toLocaleString()} records processed, Net Revenue recalculated as Gross + Contractual Adjustments. This is now the master data and will remain active until you upload a new file.</span>`;
  document.querySelectorAll('[id$="-saved-notice"]').forEach(el => el.style.display = 'block');
}

// Show uploaded-data notice on load if localStorage has data
(function() {
  try {
    if (localStorage.getItem(STORAGE_KEY)) {
      document.querySelectorAll('[id$="-saved-notice"]').forEach(el => el.style.display = 'block');
    }
  } catch(e) {}
})();

// Drag and drop support
document.querySelectorAll('.upload-zone').forEach(zone => {
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.style.borderColor='#0077b6'; });
  zone.addEventListener('dragleave', () => { zone.style.borderColor=''; });
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.style.borderColor='';
    const hid = zone.id.replace('-dropzone','');
    const fileInput = document.getElementById(hid+'-file');
    fileInput.files = e.dataTransfer.files;
    handleUpload(fileInput);
  });
});
