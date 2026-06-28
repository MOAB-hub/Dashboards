import json, re

with open('C:/Users/jennm/Desktop/Dashboard Files/dashboard_data.json') as f:
    raw = json.load(f)

data_js = json.dumps(raw, separators=(',',':'))

# Hospital config: facility name -> {id, leader, password, color}
HOSPITALS = [
    {'id':'h1','facility':'Carrollton Springs','leader':'Donald Duck','password':'dduck',
     'color':'#1a6eb5','colorLight':'#e8f0fa','region':'Central','location':'Carrollton, TX'},
    {'id':'h2','facility':'Collin Springs','leader':'John Smith','password':'jsmith',
     'color':'#2e7d32','colorLight':'#e8f5e9','region':'Central','location':'Carrollton, TX'},
    {'id':'h3','facility':'Columbus Springs Dublin','leader':'Brooke Hogan','password':'bhogan',
     'color':'#6a1b9a','colorLight':'#f3e5f5','region':'East','location':'Dublin, OH'},
    {'id':'h4','facility':'Columbus Springs East','leader':'Mickey Mouse','password':'mmouse',
     'color':'#c62828','colorLight':'#ffebee','region':'East','location':'Columbus, OH'},
]
ADMIN_PASSWORD = 'buttercup'

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Hospital System Dashboard | Executive Analytics</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
<style>
:root {{
  --brand-dark: #0d1b2a;
  --brand-mid: #1b2a3b;
  --brand-accent: #0077b6;
  --brand-light: #e8f4fd;
  --text-muted: #6c757d;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f4f8; color: #1a1a2e; }}

/* ===== LANDING ===== */
#landing {{ min-height: 100vh; background: linear-gradient(135deg, #0d1b2a 0%, #1b3a5c 50%, #0077b6 100%); display:flex; flex-direction:column; align-items:center; justify-content:center; padding: 40px 20px; }}
.landing-header {{ text-align:center; color:white; margin-bottom:50px; }}
.landing-header h1 {{ font-size:2.4rem; font-weight:700; letter-spacing:1px; }}
.landing-header p {{ font-size:1rem; opacity:.7; margin-top:8px; }}
.hipaa-badge {{ display:inline-flex; align-items:center; gap:6px; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.3); border-radius:20px; padding:6px 16px; font-size:.8rem; color:rgba(255,255,255,.8); margin-top:12px; }}
.hospital-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:24px; max-width:1100px; width:100%; }}
.hosp-card {{ background:white; border-radius:16px; padding:32px 24px; text-align:center; cursor:pointer; transition:all .3s; box-shadow:0 8px 32px rgba(0,0,0,.2); position:relative; overflow:hidden; }}
.hosp-card::before {{ content:''; position:absolute; top:0; left:0; right:0; height:5px; background: var(--hcolor); }}
.hosp-card:hover {{ transform:translateY(-6px); box-shadow:0 16px 48px rgba(0,0,0,.3); }}
.hosp-card .icon {{ width:64px; height:64px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 16px; font-size:1.8rem; }}
.hosp-card h3 {{ font-size:1.1rem; font-weight:700; color:#1a1a2e; margin-bottom:4px; }}
.hosp-card .sub {{ font-size:.8rem; color:#666; }}
.hosp-card .lock-badge {{ display:inline-flex; align-items:center; gap:4px; background:#f0f4f8; border-radius:12px; padding:4px 12px; font-size:.75rem; color:#666; margin-top:12px; }}
.admin-btn {{ margin-top:40px; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.3); color:white; border-radius:10px; padding:12px 28px; font-size:.85rem; cursor:pointer; transition:.2s; }}
.admin-btn:hover {{ background:rgba(255,255,255,.2); }}

/* ===== MODAL ===== */
.modal-overlay {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,.6); backdrop-filter:blur(4px); z-index:9000; align-items:center; justify-content:center; }}
.modal-overlay.active {{ display:flex; }}
.modal-box {{ background:white; border-radius:16px; padding:40px; max-width:420px; width:90%; box-shadow:0 24px 80px rgba(0,0,0,.3); }}
.modal-box h3 {{ font-size:1.2rem; font-weight:700; margin-bottom:6px; }}
.modal-box p {{ font-size:.85rem; color:#666; margin-bottom:24px; }}
.pwd-input {{ width:100%; border:2px solid #e0e0e0; border-radius:10px; padding:14px 16px; font-size:1rem; outline:none; transition:.2s; }}
.pwd-input:focus {{ border-color: var(--brand-accent); }}
.modal-btn {{ width:100%; padding:14px; border:none; border-radius:10px; font-size:1rem; font-weight:600; color:white; cursor:pointer; margin-top:12px; transition:.2s; }}
.modal-btn:hover {{ opacity:.9; }}
.error-msg {{ color:#dc3545; font-size:.82rem; margin-top:8px; display:none; }}
.modal-close {{ float:right; background:none; border:none; font-size:1.2rem; cursor:pointer; color:#666; }}

/* ===== DASHBOARD ===== */
.dashboard-page {{ display:none; min-height:100vh; background:#f0f4f8; }}
.dashboard-page.active {{ display:block; }}
.dash-header {{ background: var(--hcolor); color:white; padding:20px 32px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; }}
.dash-header h2 {{ font-size:1.4rem; font-weight:700; }}
.dash-header .meta {{ font-size:.82rem; opacity:.8; }}
.dash-nav {{ background:white; border-bottom:1px solid #e0e7ef; padding:0 32px; display:flex; gap:0; overflow-x:auto; }}
.dash-nav button {{ border:none; background:none; padding:14px 20px; font-size:.85rem; font-weight:500; color:#666; cursor:pointer; border-bottom:3px solid transparent; white-space:nowrap; transition:.2s; }}
.dash-nav button.active, .dash-nav button:hover {{ color: var(--hcolor); border-bottom-color: var(--hcolor); }}
.dash-content {{ padding:28px 32px; max-width:1400px; margin:0 auto; }}
.back-btn {{ background:rgba(255,255,255,.2); border:1px solid rgba(255,255,255,.4); color:white; border-radius:8px; padding:8px 16px; font-size:.82rem; cursor:pointer; transition:.2s; }}
.back-btn:hover {{ background:rgba(255,255,255,.3); }}

/* ===== KPI CARDS ===== */
.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin-bottom:28px; }}
.kpi-card {{ background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,.06); border-left:4px solid var(--hcolor); }}
.kpi-card .label {{ font-size:.75rem; color:#888; font-weight:500; text-transform:uppercase; letter-spacing:.5px; }}
.kpi-card .value {{ font-size:1.6rem; font-weight:700; color:#1a1a2e; margin:4px 0; }}
.kpi-card .sub {{ font-size:.75rem; color:#666; }}

/* ===== SECTION CARDS ===== */
.section-card {{ background:white; border-radius:14px; padding:24px; box-shadow:0 2px 12px rgba(0,0,0,.06); margin-bottom:24px; }}
.section-card h4 {{ font-size:1rem; font-weight:700; color:#1a1a2e; margin-bottom:4px; padding-bottom:12px; border-bottom:2px solid #f0f4f8; display:flex; align-items:center; gap:8px; }}
.chart-wrap {{ position:relative; }}
.chart-wrap canvas {{ max-height:320px; }}
.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
@media(max-width:900px){{ .two-col {{ grid-template-columns:1fr; }} }}

/* ===== TABLES ===== */
.data-table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
.data-table th {{ background:#f8f9fa; color:#555; font-weight:600; padding:10px 14px; text-align:left; border-bottom:2px solid #e9ecef; font-size:.78rem; text-transform:uppercase; letter-spacing:.4px; }}
.data-table td {{ padding:10px 14px; border-bottom:1px solid #f0f0f0; color:#333; }}
.data-table tr:last-child td {{ border-bottom:none; }}
.data-table tr:hover td {{ background:#f8f9fa; }}
.badge-fc {{ display:inline-block; padding:3px 10px; border-radius:12px; font-size:.72rem; font-weight:600; }}
.bar-cell {{ display:flex; align-items:center; gap:8px; }}
.bar-bg {{ flex:1; background:#f0f4f8; border-radius:4px; height:8px; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:4px; background: var(--hcolor); }}
.denial-rate-high {{ color:#dc3545; font-weight:700; }}
.denial-rate-low {{ color:#2e7d32; }}

/* ===== UPLOAD ===== */
.upload-zone {{ border:2px dashed #b0c4d8; border-radius:12px; padding:40px; text-align:center; cursor:pointer; transition:.2s; background:#f8fbff; }}
.upload-zone:hover {{ border-color: var(--brand-accent); background:#eef6ff; }}
.upload-zone i {{ font-size:2.5rem; color:#b0c4d8; }}
.upload-zone p {{ color:#666; margin-top:10px; }}
.upload-zone .hint {{ font-size:.78rem; color:#999; margin-top:6px; }}

/* ===== ADMIN ===== */
#admin-panel {{ display:none; min-height:100vh; background:#f0f4f8; }}
#admin-panel.active {{ display:block; }}
.admin-header {{ background: linear-gradient(135deg,#1a1a2e,#0d3b6e); color:white; padding:20px 32px; display:flex; align-items:center; justify-content:space-between; }}
.admin-content {{ padding:32px; max-width:900px; margin:0 auto; }}
.user-table-wrap {{ background:white; border-radius:14px; padding:24px; box-shadow:0 2px 12px rgba(0,0,0,.06); }}
.add-user-form {{ background:white; border-radius:14px; padding:24px; box-shadow:0 2px 12px rgba(0,0,0,.06); margin-bottom:24px; }}
.form-row {{ display:grid; grid-template-columns:1fr 1fr 1fr auto; gap:12px; align-items:end; }}
@media(max-width:700px){{ .form-row {{ grid-template-columns:1fr; }} }}
.form-group label {{ font-size:.8rem; font-weight:600; color:#555; display:block; margin-bottom:4px; }}
.form-group input, .form-group select {{ width:100%; border:2px solid #e0e0e0; border-radius:8px; padding:10px 12px; font-size:.9rem; }}
.btn-add {{ background:#0077b6; color:white; border:none; border-radius:8px; padding:10px 20px; font-size:.9rem; cursor:pointer; white-space:nowrap; }}
.btn-del {{ background:#dc3545; color:white; border:none; border-radius:6px; padding:5px 12px; font-size:.78rem; cursor:pointer; }}

/* ===== REGIONAL ===== */
.region-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }}
.region-card {{ background:white; border-radius:12px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,.06); border-top:4px solid; }}

/* ===== EXEC INSIGHTS ===== */
.insight-list {{ list-style:none; }}
.insight-list li {{ display:flex; gap:12px; padding:12px 0; border-bottom:1px solid #f0f4f8; align-items:flex-start; }}
.insight-list li:last-child {{ border-bottom:none; }}
.insight-icon {{ width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:1rem; }}

/* ===== COVERED LIVES ===== */
.lives-summary {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:20px; }}
.lives-kpi {{ background:#f8f9fa; border-radius:10px; padding:16px; text-align:center; }}
.lives-kpi .val {{ font-size:1.4rem; font-weight:700; }}
.lives-kpi .lbl {{ font-size:.75rem; color:#666; margin-top:2px; }}

/* ===== NAV TABS CONTENT ===== */
.tab-section {{ display:none; }}
.tab-section.active {{ display:block; }}

/* ===== RESPONSIVE ===== */
@media(max-width:600px){{
  .dash-content {{ padding:16px; }}
  .dash-header {{ padding:16px; }}
  .section-card {{ padding:16px; }}
}}
</style>
</head>
<body>

<!-- =================== LANDING PAGE =================== -->
<div id="landing">
  <div class="landing-header">
    <h1><i class="bi bi-hospital"></i> Hospital System Executive Dashboard</h1>
    <p>Secure Analytics Portal — Authorized Personnel Only</p>
    <div class="hipaa-badge"><i class="bi bi-shield-lock-fill"></i> HIPAA Compliant | No PHI Displayed</div>
  </div>

  <div class="hospital-grid">
'''

for h in HOSPITALS:
    icon = 'bi-building-fill-cross'
    html += f'''    <div class="hosp-card" style="--hcolor:{h['color']}" onclick="promptHospital('{h['id']}')">
      <div class="icon" style="background:{h['colorLight']};color:{h['color']}"><i class="bi {icon}"></i></div>
      <h3>{h['facility']}</h3>
      <div class="sub">{h['location']} | {h['region']} Region</div>
      <div class="lock-badge"><i class="bi bi-lock-fill"></i> Password Protected</div>
    </div>
'''

html += f'''  </div>

  <button class="admin-btn" onclick="promptAdmin()"><i class="bi bi-gear-fill"></i> Admin Panel</button>
</div>

<!-- =================== PASSWORD MODAL =================== -->
<div class="modal-overlay" id="pwd-modal">
  <div class="modal-box">
    <button class="modal-close" onclick="closeModal()">&times;</button>
    <h3 id="modal-title">Access Dashboard</h3>
    <p id="modal-sub">Enter your password to view this hospital's data.</p>
    <input type="password" class="pwd-input" id="modal-pwd" placeholder="Enter password" autocomplete="off">
    <div class="error-msg" id="modal-error">Incorrect password. Please try again.</div>
    <button class="modal-btn" id="modal-submit" style="background:#0077b6" onclick="submitPassword()">Access Dashboard</button>
  </div>
</div>

<!-- =================== ADMIN PANEL =================== -->
<div id="admin-panel">
  <div class="admin-header">
    <div>
      <h2 style="color:white;font-size:1.3rem"><i class="bi bi-shield-fill"></i> Admin Panel</h2>
      <div style="font-size:.8rem;opacity:.7;color:white">User &amp; Access Management</div>
    </div>
    <button class="back-btn" onclick="showLanding()"><i class="bi bi-arrow-left"></i> Back to Portal</button>
  </div>
  <div class="admin-content">
    <div class="add-user-form">
      <h4 style="font-size:1rem;font-weight:700;margin-bottom:16px"><i class="bi bi-person-plus"></i> Manage Access</h4>
      <div class="form-row">
        <div class="form-group">
          <label>Leader Name</label>
          <input type="text" id="new-name" placeholder="Full Name">
        </div>
        <div class="form-group">
          <label>Hospital</label>
          <select id="new-hospital">
            {''.join(f'<option value="{h["id"]}">{h["facility"]}</option>' for h in HOSPITALS)}
          </select>
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" id="new-password" placeholder="Set password">
        </div>
        <button class="btn-add" onclick="addUser()"><i class="bi bi-plus"></i> Add</button>
      </div>
    </div>
    <div class="user-table-wrap">
      <h4 style="font-size:1rem;font-weight:700;margin-bottom:16px"><i class="bi bi-people"></i> Current Users</h4>
      <table class="data-table" id="user-table">
        <thead><tr><th>Leader</th><th>Hospital</th><th>Password</th><th>Action</th></tr></thead>
        <tbody id="user-tbody"></tbody>
      </table>
    </div>
  </div>
</div>
'''

# Generate each hospital dashboard
for h in HOSPITALS:
    fac = h['facility']
    html += f'''
<!-- =================== {fac.upper()} DASHBOARD =================== -->
<div class="dashboard-page" id="{h['id']}-dash" style="--hcolor:{h['color']}">
  <div class="dash-header" style="background:{h['color']}">
    <div>
      <h2>{fac}</h2>
      <div class="meta">{h['location']} | {h['region']} Region | Leader: {h['leader']}</div>
    </div>
    <button class="back-btn" onclick="showLanding()"><i class="bi bi-arrow-left"></i> Portal Home</button>
  </div>
  <div class="dash-nav">
    <button class="active" onclick="showTab('{h['id']}','overview',this)">Overview</button>
    <button onclick="showTab('{h['id']}','payor-mix',this)">Payor Mix</button>
    <button onclick="showTab('{h['id']}','rolling-gross',this)">Top 5 Gross</button>
    <button onclick="showTab('{h['id']}','rolling-net',this)">Top 5 Net</button>
    <button onclick="showTab('{h['id']}','denials',this)">Denials 2026</button>
    <button onclick="showTab('{h['id']}','covered-lives',this)">Covered Lives</button>
    <button onclick="showTab('{h['id']}','regional',this)">Regional</button>
    <button onclick="showTab('{h['id']}','insights',this)">Exec Insights</button>
    <button onclick="showTab('{h['id']}','upload',this)">Upload Data</button>
  </div>
  <div class="dash-content">

    <!-- OVERVIEW TAB -->
    <div class="tab-section active" id="{h['id']}-overview">
      <div class="kpi-grid" id="{h['id']}-kpis"></div>
      <div class="two-col">
        <div class="section-card">
          <h4><i class="bi bi-pie-chart-fill" style="color:{h['color']}"></i> Payor Mix by Patient Days</h4>
          <div class="chart-wrap"><canvas id="{h['id']}-donut"></canvas></div>
        </div>
        <div class="section-card">
          <h4><i class="bi bi-bar-chart-fill" style="color:{h['color']}"></i> Program Type Mix</h4>
          <div class="chart-wrap"><canvas id="{h['id']}-program"></canvas></div>
        </div>
      </div>
      <div class="section-card">
        <h4><i class="bi bi-graph-up" style="color:{h['color']}"></i> Quarterly Trend — Patient Days &amp; Net Revenue</h4>
        <div class="chart-wrap"><canvas id="{h['id']}-trend"></canvas></div>
      </div>
    </div>

    <!-- PAYOR MIX TAB -->
    <div class="tab-section" id="{h['id']}-payor-mix">
      <div class="section-card">
        <h4><i class="bi bi-table" style="color:{h['color']}"></i> Payor Mix — Financial Class Detail</h4>
        <table class="data-table" id="{h['id']}-pm-table">
          <thead><tr><th>Financial Class (Payor Mix)</th><th>Patient Days (LOS)</th><th>% Mix</th><th>Admits</th><th>Avg LOS</th><th>Gross Revenue</th><th>Net Revenue</th><th>Rev / Patient Day</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
      <div class="two-col">
        <div class="section-card">
          <h4><i class="bi bi-pie-chart" style="color:{h['color']}"></i> LOS Distribution</h4>
          <div class="chart-wrap"><canvas id="{h['id']}-pm-pie"></canvas></div>
        </div>
        <div class="section-card">
          <h4><i class="bi bi-currency-dollar" style="color:{h['color']}"></i> Revenue per Patient Day by Payor</h4>
          <div class="chart-wrap"><canvas id="{h['id']}-pm-rpd"></canvas></div>
        </div>
      </div>
    </div>

    <!-- ROLLING GROSS TAB -->
    <div class="tab-section" id="{h['id']}-rolling-gross">
      <div class="section-card">
        <h4><i class="bi bi-graph-up-arrow" style="color:{h['color']}"></i> Rolling 5 Quarters — Inpatient Days, Top 5 Payors by Total Gross Charges</h4>
        <div class="chart-wrap" style="height:320px"><canvas id="{h['id']}-gross-chart"></canvas></div>
      </div>
      <div class="section-card">
        <h4><i class="bi bi-table" style="color:{h['color']}"></i> Detail Table — Patient Days by Quarter</h4>
        <table class="data-table" id="{h['id']}-gross-table">
          <thead><tr><th>Payor</th><th>1Q25</th><th>2Q25</th><th>3Q25</th><th>4Q25</th><th>1Q26</th><th>Total Gross</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- ROLLING NET TAB -->
    <div class="tab-section" id="{h['id']}-rolling-net">
      <div class="section-card">
        <h4><i class="bi bi-graph-up-arrow" style="color:{h['color']}"></i> Rolling 5 Quarters — Inpatient Days, Top 5 Payors by Total Net Charges</h4>
        <div class="chart-wrap" style="height:320px"><canvas id="{h['id']}-net-chart"></canvas></div>
      </div>
      <div class="section-card">
        <h4><i class="bi bi-table" style="color:{h['color']}"></i> Detail Table — Patient Days by Quarter</h4>
        <table class="data-table" id="{h['id']}-net-table">
          <thead><tr><th>Payor</th><th>1Q25</th><th>2Q25</th><th>3Q25</th><th>4Q25</th><th>1Q26</th><th>Total Net</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- DENIALS TAB -->
    <div class="tab-section" id="{h['id']}-denials">
      <div class="section-card">
        <h4><i class="bi bi-exclamation-triangle-fill" style="color:{h['color']}"></i> 2026 YTD Denial Rate by Payor</h4>
        <div class="chart-wrap" style="height:360px"><canvas id="{h['id']}-denial-chart"></canvas></div>
      </div>
      <div class="section-card">
        <h4><i class="bi bi-table" style="color:{h['color']}"></i> Denial Detail — All Payors (1Q26 YTD)</h4>
        <table class="data-table" id="{h['id']}-denial-table">
          <thead><tr><th>Payor</th><th>Gross Revenue</th><th>Net Revenue</th><th>Denial Adjustments</th><th>Denial Rate</th><th>Patient Days</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- COVERED LIVES TAB -->
    <div class="tab-section" id="{h['id']}-covered-lives">
      <div class="section-card">
        <h4><i class="bi bi-people-fill" style="color:{h['color']}"></i> Covered Lives — Market Intelligence</h4>
        <p style="font-size:.82rem;color:#666;margin-bottom:16px">Covered lives data reflects regional payor market representation, informing strategic payer contracting priorities.</p>
        <div class="lives-summary" id="{h['id']}-lives-summary"></div>
        <div class="two-col">
          <div class="chart-wrap"><canvas id="{h['id']}-lives-chart"></canvas></div>
          <div><table class="data-table" id="{h['id']}-lives-table">
            <thead><tr><th>Payor / Insurer</th><th>Total Lives</th><th>Medicare Adv.</th><th>Commercial</th><th>Managed Medicaid</th></tr></thead>
            <tbody></tbody>
          </table></div>
        </div>
      </div>
    </div>

    <!-- REGIONAL TAB -->
    <div class="tab-section" id="{h['id']}-regional">
      <div class="section-card">
        <h4><i class="bi bi-map-fill" style="color:{h['color']}"></i> Regional Roll-Up — {h['region']} Region</h4>
        <div class="region-grid" id="{h['id']}-region-grid"></div>
      </div>
      <div class="section-card" style="margin-top:20px">
        <h4><i class="bi bi-bar-chart" style="color:{h['color']}"></i> Regional Facility Comparison</h4>
        <div class="chart-wrap" style="height:300px"><canvas id="{h['id']}-region-chart"></canvas></div>
      </div>
    </div>

    <!-- EXEC INSIGHTS TAB -->
    <div class="tab-section" id="{h['id']}-insights">
      <div class="section-card">
        <h4><i class="bi bi-lightbulb-fill" style="color:{h['color']}"></i> Executive Insights &amp; Strategic Recommendations</h4>
        <ul class="insight-list" id="{h['id']}-insight-list"></ul>
      </div>
      <div class="section-card" style="margin-top:0">
        <h4><i class="bi bi-activity" style="color:{h['color']}"></i> Financial Class — IP Days / Revenue Ratio Analysis</h4>
        <div class="chart-wrap" style="height:300px"><canvas id="{h['id']}-ratio-chart"></canvas></div>
        <table class="data-table" style="margin-top:20px" id="{h['id']}-ratio-table">
          <thead><tr><th>Financial Class (Payor Mix)</th><th>Inpatient Days</th><th>Revenue / Patient Day</th><th>Days as % of Total</th><th>Net Rev as % of Total</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>

    <!-- UPLOAD TAB -->
    <div class="tab-section" id="{h['id']}-upload">
      <div class="section-card">
        <h4><i class="bi bi-cloud-upload" style="color:{h['color']}"></i> Update Dashboard Data</h4>
        <p style="font-size:.85rem;color:#666;margin-bottom:20px">Upload the latest "Hospital POC Base Data.xlsx" to update all charts and metrics. Once uploaded, that file becomes the permanent master data — it will remain active after any refresh until you upload a newer file.</p>
        <div id="{h['id']}-saved-notice" style="display:none;background:#e8f5e9;border:1px solid #a5d6a7;border-radius:8px;padding:12px 16px;margin-bottom:16px;font-size:.83rem;color:#2e7d32">
          <i class="bi bi-database-check"></i> <strong>Uploaded data is active.</strong> This dashboard is running from your uploaded file. It will remain until you upload a new file.
        </div>
        <div class="upload-zone" onclick="document.getElementById('{h['id']}-file').click()" id="{h['id']}-dropzone">
          <i class="bi bi-file-earmark-spreadsheet"></i>
          <p><strong>Click to upload</strong> or drag &amp; drop</p>
          <div class="hint">Accepts: Hospital POC Base Data.xlsx</div>
        </div>
        <input type="file" id="{h['id']}-file" accept=".xlsx,.xls" style="display:none" onchange="handleUpload(this)">
        <div id="{h['id']}-upload-status" style="margin-top:16px;font-size:.85rem;"></div>
      </div>
    </div>

  </div>
</div>
'''

# ===== JAVASCRIPT =====
hospital_config_js = json.dumps(HOSPITALS, separators=(',',':'))

html += f'''
<script>
// ===================================================
// DATA
// ===================================================
const STORAGE_KEY = 'hospital_dashboard_data';
const EMBEDDED_DATA = {data_js};

// On load: uploaded data in localStorage is always master.
// Embedded data is only used if no upload has ever been done.
function loadData() {{
  try {{
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {{
      const parsed = JSON.parse(saved);
      // Validate schema: must have hospitals with totals.gross as a real number
      const facs = Object.keys(parsed.hospitals || {{}});
      const valid = facs.length > 0 && facs.every(f => {{
        const t = parsed.hospitals[f].totals;
        return t && typeof t.gross === 'number' && t.gross > 0;
      }});
      if (valid) return parsed;
      // Invalid schema — clear it and fall through to embedded data
      localStorage.removeItem(STORAGE_KEY);
    }}
  }} catch(e) {{ localStorage.removeItem(STORAGE_KEY); }}
  return JSON.parse(JSON.stringify(EMBEDDED_DATA));
}}

const RAW_DATA = loadData();

function saveData() {{
  try {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(RAW_DATA));
  }} catch(e) {{
    console.warn('localStorage save failed (storage may be full):', e);
  }}
}}

const QUARTERS = ["1Q25","2Q25","3Q25","4Q25","1Q26"];
const FC_COLORS = {{
  "Commercial": "#1a6eb5",
  "Medicare": "#2e7d32",
  "Medicare Advantage": "#6a1b9a",
  "Managed Medicaid": "#e65100",
  "Medicaid": "#c62828",
  "Other Governmental": "#00695c",
  "Self Pay": "#757575"
}};
const CHART_PALETTE = ["#1a6eb5","#2e7d32","#6a1b9a","#c62828","#e65100","#00695c","#0077b6"];

const HOSPITALS_CFG = {hospital_config_js};
const ADMIN_PASSWORD = "{ADMIN_PASSWORD}";

// ===================================================
// USER MANAGEMENT (stored in memory, seeded from config)
// ===================================================
let users = HOSPITALS_CFG.map(h => ({{name:h.leader, hospitalId:h.id, password:h.password}}));

function renderUserTable() {{
  const tbody = document.getElementById('user-tbody');
  tbody.innerHTML = users.map((u,i) => {{
    const hosp = HOSPITALS_CFG.find(h=>h.id===u.hospitalId);
    return `<tr>
      <td>${{u.name}}</td>
      <td>${{hosp ? hosp.facility : u.hospitalId}}</td>
      <td><span style="font-family:monospace;background:#f0f4f8;padding:2px 8px;border-radius:4px">${{u.password}}</span></td>
      <td><button class="btn-del" onclick="deleteUser(${{i}})"><i class="bi bi-trash"></i> Remove</button></td>
    </tr>`;
  }}).join('');
}}

function addUser() {{
  const name = document.getElementById('new-name').value.trim();
  const hospitalId = document.getElementById('new-hospital').value;
  const password = document.getElementById('new-password').value.trim();
  if (!name || !password) {{ alert('Please fill all fields'); return; }}
  users.push({{name, hospitalId, password}});
  renderUserTable();
  document.getElementById('new-name').value = '';
  document.getElementById('new-password').value = '';
}}

function deleteUser(i) {{
  if (confirm('Remove this user?')) {{ users.splice(i,1); renderUserTable(); }}
}}

// ===================================================
// NAVIGATION
// ===================================================
let currentTarget = null;

function showLanding() {{
  document.getElementById('landing').style.display = 'flex';
  document.getElementById('admin-panel').classList.remove('active');
  HOSPITALS_CFG.forEach(h => {{
    const el = document.getElementById(h.id+'-dash');
    if (el) el.classList.remove('active');
  }});
}}

function promptHospital(hid) {{
  currentTarget = hid;
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  document.getElementById('modal-title').textContent = h.facility;
  document.getElementById('modal-sub').textContent = "Enter your authorized password to access this dashboard.";
  document.getElementById('modal-pwd').value = '';
  document.getElementById('modal-error').style.display = 'none';
  document.getElementById('modal-submit').style.background = h.color;
  document.getElementById('modal-modal-type') && (document.getElementById('modal-modal-type').value = 'hospital');
  document.getElementById('pwd-modal').classList.add('active');
  setTimeout(()=>document.getElementById('modal-pwd').focus(), 100);
  currentModalType = 'hospital';
}}

function promptAdmin() {{
  currentTarget = 'admin';
  document.getElementById('modal-title').textContent = 'Admin Panel';
  document.getElementById('modal-sub').textContent = 'Enter the administrator password to manage users and access settings.';
  document.getElementById('modal-pwd').value = '';
  document.getElementById('modal-error').style.display = 'none';
  document.getElementById('modal-submit').style.background = '#1a1a2e';
  document.getElementById('pwd-modal').classList.add('active');
  setTimeout(()=>document.getElementById('modal-pwd').focus(), 100);
  currentModalType = 'admin';
}}

let currentModalType = 'hospital';

function closeModal() {{
  document.getElementById('pwd-modal').classList.remove('active');
}}

function submitPassword() {{
  const pwd = document.getElementById('modal-pwd').value;
  if (currentModalType === 'admin') {{
    if (pwd === ADMIN_PASSWORD) {{
      closeModal();
      document.getElementById('landing').style.display = 'none';
      renderUserTable();
      document.getElementById('admin-panel').classList.add('active');
    }} else {{
      document.getElementById('modal-error').style.display = 'block';
    }}
    return;
  }}
  // Hospital login — check all users for this hospital
  const validUsers = users.filter(u => u.hospitalId === currentTarget && u.password === pwd);
  if (validUsers.length > 0) {{
    closeModal();
    document.getElementById('landing').style.display = 'none';
    openDashboard(currentTarget);
  }} else {{
    document.getElementById('modal-error').style.display = 'block';
  }}
}}

document.getElementById('modal-pwd').addEventListener('keydown', e => {{
  if (e.key === 'Enter') submitPassword();
}});

document.getElementById('pwd-modal').addEventListener('click', e => {{
  if (e.target === document.getElementById('pwd-modal')) closeModal();
}});

// ===================================================
// DASHBOARD TABS
// ===================================================
function showTab(hid, tabName, btn) {{
  document.querySelectorAll(`#${{hid}}-dash .tab-section`).forEach(s => s.classList.remove('active'));
  document.querySelectorAll(`#${{hid}}-dash .dash-nav button`).forEach(b => b.classList.remove('active'));
  document.getElementById(`${{hid}}-${{tabName}}`).classList.add('active');
  btn.classList.add('active');
}}

// ===================================================
// CHART REGISTRY (destroy before re-create)
// ===================================================
const chartRegistry = {{}};
function makeChart(id, config) {{
  if (chartRegistry[id]) {{ chartRegistry[id].destroy(); }}
  const ctx = document.getElementById(id);
  if (!ctx) return;
  chartRegistry[id] = new Chart(ctx, config);
  return chartRegistry[id];
}}

// ===================================================
// FORMAT HELPERS
// ===================================================
function fmtDollar(v) {{ return '$' + Number(v||0).toLocaleString('en-US',{{minimumFractionDigits:0,maximumFractionDigits:0}}); }}
const fmtN = v => (v||0).toLocaleString('en-US');
const fmtPct = v => (v||0).toFixed(1) + '%';

// ===================================================
// OPEN DASHBOARD
// ===================================================
const dashBuilt = {{}};

function openDashboard(hid) {{
  HOSPITALS_CFG.forEach(h => {{
    const el = document.getElementById(h.id+'-dash');
    if (el) el.classList.remove('active');
  }});
  const el = document.getElementById(hid+'-dash');
  if (el) el.classList.add('active');
  if (!dashBuilt[hid]) {{
    buildDashboard(hid);
    dashBuilt[hid] = true;
  }}
}}

function buildDashboard(hid) {{
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  const fac = h.facility;
  const hosp = RAW_DATA.hospitals[fac];
  if (!hosp) {{ console.error('No data for', fac); return; }}

  buildKPIs(hid, hosp, h.color);
  buildDonut(hid, hosp, h.color);
  buildProgram(hid, hosp, h.color);
  buildTrend(hid, hosp, h.color);
  buildPayorMixTable(hid, hosp, h.color);
  buildPayorMixCharts(hid, hosp, h.color);
  buildRollingGross(hid, hosp, h.color);
  buildRollingNet(hid, hosp, h.color);
  buildDenials(hid, hosp, h.color);
  buildCoveredLives(hid, h.color);
  buildRegional(hid, h, hosp);
  buildInsights(hid, hosp, h);
  buildRatioAnalysis(hid, hosp, h.color);
}}

// ===== KPIs =====
function buildKPIs(hid, hosp, color) {{
  const t = hosp.totals;
  const revPerDay = t.net / t.los;
  const avgLos = t.los / t.admits;
  const margin = (t.net / t.gross * 100);
  const kpis = [
    {{label:'Total Patient Days', value:fmtN(t.los), sub:'All Financial Classes', icon:'bi-calendar-check'}},
    {{label:'Total Admits', value:fmtN(t.admits), sub:'1Q25 – 1Q26', icon:'bi-person-check'}},
    {{label:'Avg Length of Stay', value:avgLos.toFixed(1)+' days', sub:'Per admission', icon:'bi-clock-history'}},
    {{label:'Total Gross Revenue', value:fmtDollar(t.gross), sub:'All Payors', icon:'bi-cash-stack'}},
    {{label:'Total Net Revenue', value:fmtDollar(t.net), sub:'All Payors', icon:'bi-currency-dollar'}},
    {{label:'Net Rev / Patient Day', value:fmtDollar(revPerDay), sub:'Blended rate', icon:'bi-graph-up'}},
    {{label:'Net Margin %', value:fmtPct(margin), sub:'Net ÷ Gross', icon:'bi-percent'}},
  ];
  const el = document.getElementById(hid+'-kpis');
  el.innerHTML = kpis.map(k=>`
    <div class="kpi-card" style="--hcolor:${{color}}">
      <div class="label"><i class="bi ${{k.icon}}"></i> ${{k.label}}</div>
      <div class="value">${{k.value}}</div>
      <div class="sub">${{k.sub}}</div>
    </div>`).join('');
}}

// ===== DONUT =====
function buildDonut(hid, hosp, color) {{
  const pm = hosp.payor_mix;
  const labels = Object.keys(pm).sort((a,b)=>pm[b].pct-pm[a].pct);
  const vals = labels.map(l=>pm[l].los);
  const colors = labels.map(l=>FC_COLORS[l]||'#999');
  makeChart(hid+'-donut', {{
    type:'doughnut',
    data:{{ labels, datasets:[{{data:vals, backgroundColor:colors, borderWidth:2, borderColor:'#fff'}}] }},
    options:{{
      responsive:true, maintainAspectRatio:true,
      plugins:{{
        legend:{{position:'right',labels:{{font:{{size:11}},boxWidth:12}}}},
        tooltip:{{callbacks:{{label:ctx=>` ${{ctx.label}}: ${{fmtN(ctx.raw)}} days (${{fmtPct(ctx.raw/vals.reduce((a,b)=>a+b,0)*100)}})` }}}}
      }}
    }}
  }});
}}

// ===== PROGRAM MIX =====
function buildProgram(hid, hosp, color) {{
  const pm = hosp.program_mix;
  const labels = Object.keys(pm);
  const vals = labels.map(l=>pm[l].los);
  const netVals = labels.map(l=>pm[l].net);
  makeChart(hid+'-program', {{
    type:'bar',
    data:{{
      labels,
      datasets:[
        {{label:'Patient Days',data:vals,backgroundColor:color+'cc',yAxisID:'y'}},
        {{label:'Net Revenue',data:netVals,backgroundColor:'#00695c88',yAxisID:'y1'}},
      ]
    }},
    options:{{
      responsive:true,maintainAspectRatio:true,
      plugins:{{legend:{{position:'top',labels:{{font:{{size:11}}}}}}}},
      scales:{{
        y:{{position:'left',title:{{display:true,text:'Patient Days'}},ticks:{{callback:v=>fmtN(v)}}}},
        y1:{{position:'right',title:{{display:true,text:'Net Revenue'}},grid:{{drawOnChartArea:false}},ticks:{{callback:v=>fmtDollar(v)}}}}
      }}
    }}
  }});
}}

// ===== QUARTERLY TREND =====
function buildTrend(hid, hosp, color) {{
  const qs = QUARTERS;
  const los = qs.map(q=>hosp.qtr_summary[q]?.los||0);
  const net = qs.map(q=>hosp.qtr_summary[q]?.net||0);
  makeChart(hid+'-trend', {{
    type:'bar',
    data:{{
      labels:qs,
      datasets:[
        {{type:'bar',label:'Patient Days',data:los,backgroundColor:'#2e7d32',yAxisID:'y',order:2}},
        {{type:'line',label:'Net Revenue',data:net,borderColor:'#0077b6',backgroundColor:'#0077b622',yAxisID:'y1',order:1,tension:.3,fill:true,pointRadius:5}},
      ]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top'}}}},
      scales:{{
        y:{{title:{{display:true,text:'Patient Days'}},ticks:{{callback:v=>fmtN(v)}}}},
        y1:{{position:'right',title:{{display:true,text:'Net Revenue'}},grid:{{drawOnChartArea:false}},ticks:{{callback:v=>fmtDollar(v)}}}}
      }}
    }}
  }});
}}

// ===== PAYOR MIX TABLE =====
function buildPayorMixTable(hid, hosp, color) {{
  const pm = hosp.payor_mix;
  const sorted = Object.entries(pm).sort((a,b)=>b[1].pct-a[1].pct);
  const tbody = document.querySelector(`#${{hid}}-pm-table tbody`);
  tbody.innerHTML = sorted.map(([fc,v])=>{{
    const fcColor = FC_COLORS[fc]||'#999';
    return `<tr>
      <td><span class="badge-fc" style="background:${{fcColor}}22;color:${{fcColor}}">${{fc}}</span></td>
      <td>${{fmtN(v.los)}}</td>
      <td>
        <div class="bar-cell">
          <div class="bar-bg" style="--hcolor:${{fcColor}}"><div class="bar-fill" style="width:${{v.pct}}%;background:${{fcColor}}"></div></div>
          <span style="font-size:.8rem;font-weight:600;color:${{fcColor}}">${{v.pct}}%</span>
        </div>
      </td>
      <td>${{fmtN(v.admits)}}</td>
      <td>${{v.avg_los}}</td>
      <td>${{fmtDollar(v.gross)}}</td>
      <td>${{fmtDollar(v.net)}}</td>
      <td><strong>${{fmtDollar(v.rev_per_day)}}</strong></td>
    </tr>`;
  }}).join('');
  // Totals row
  const totLOS = sorted.reduce((s,[,v])=>s+v.los,0);
  const totGross = sorted.reduce((s,[,v])=>s+v.gross,0);
  const totNet = sorted.reduce((s,[,v])=>s+v.net,0);
  const totAdmits = sorted.reduce((s,[,v])=>s+v.admits,0);
  tbody.innerHTML += `<tr style="font-weight:700;background:#f8f9fa">
    <td>TOTAL</td><td>${{fmtN(totLOS)}}</td><td>100%</td><td>${{fmtN(totAdmits)}}</td><td>—</td>
    <td>${{fmtDollar(totGross)}}</td><td>${{fmtDollar(totNet)}}</td><td>${{fmtDollar(totNet/totLOS)}}</td>
  </tr>`;
}}

// ===== PAYOR MIX CHARTS =====
function buildPayorMixCharts(hid, hosp, color) {{
  const pm = hosp.payor_mix;
  const sorted = Object.entries(pm).sort((a,b)=>b[1].pct-a[1].pct);
  const labels = sorted.map(([fc])=>fc);
  const colors = labels.map(l=>FC_COLORS[l]||'#999');

  makeChart(hid+'-pm-pie', {{
    type:'doughnut',
    data:{{labels,datasets:[{{data:sorted.map(([,v])=>v.los),backgroundColor:colors,borderWidth:2,borderColor:'#fff'}}]}},
    options:{{responsive:true,maintainAspectRatio:true,plugins:{{legend:{{position:'bottom',labels:{{font:{{size:10}},boxWidth:10}}}}}}}}
  }});

  makeChart(hid+'-pm-rpd', {{
    type:'bar',
    data:{{labels,datasets:[{{label:'Rev/Patient Day',data:sorted.map(([,v])=>v.rev_per_day),backgroundColor:colors}}]}},
    options:{{
      responsive:true,maintainAspectRatio:true,indexAxis:'y',
      plugins:{{legend:{{display:false}}}},
      scales:{{x:{{ticks:{{callback:v=>fmtDollar(v)}}}}}}
    }}
  }});
}}

// ===== ROLLING GROSS =====
function buildRollingGross(hid, hosp, color) {{
  const t5 = hosp.top5_gross;
  const payors = hosp.top5_gross_payors;
  const datasets = payors.map((p,i)=>{{
    const c = CHART_PALETTE[i%CHART_PALETTE.length];
    return {{label:p,data:QUARTERS.map(q=>t5[p].qtr_los[q]||0),borderColor:c,backgroundColor:c+'44',tension:.3,fill:false,pointRadius:5}};
  }});
  makeChart(hid+'-gross-chart', {{
    type:'line',
    data:{{labels:QUARTERS,datasets}},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top'}}}},
      scales:{{y:{{title:{{display:true,text:'Patient Days (LOS)'}},ticks:{{callback:v=>fmtN(v)}}}}}}
    }}
  }});
  const tbody = document.querySelector(`#${{hid}}-gross-table tbody`);
  tbody.innerHTML = payors.map((p,i)=>{{
    const c = CHART_PALETTE[i%CHART_PALETTE.length];
    const qtds = QUARTERS.map(q=>`<td>${{fmtN(t5[p].qtr_los[q]||0)}}</td>`).join('');
    return `<tr><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${{c}};margin-right:6px"></span>${{p}}</td>${{qtds}}<td><strong>${{fmtDollar(t5[p].total_gross)}}</strong></td></tr>`;
  }}).join('');
}}

// ===== ROLLING NET =====
function buildRollingNet(hid, hosp, color) {{
  const t5 = hosp.top5_net;
  const payors = hosp.top5_net_payors;
  const datasets = payors.map((p,i)=>{{
    const c = CHART_PALETTE[i%CHART_PALETTE.length];
    return {{label:p,data:QUARTERS.map(q=>t5[p].qtr_los[q]||0),borderColor:c,backgroundColor:c+'44',tension:.3,fill:false,pointRadius:5}};
  }});
  makeChart(hid+'-net-chart', {{
    type:'line',
    data:{{labels:QUARTERS,datasets}},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top'}}}},
      scales:{{y:{{title:{{display:true,text:'Patient Days (LOS)'}},ticks:{{callback:v=>fmtN(v)}}}}}}
    }}
  }});
  const tbody = document.querySelector(`#${{hid}}-net-table tbody`);
  tbody.innerHTML = payors.map((p,i)=>{{
    const c = CHART_PALETTE[i%CHART_PALETTE.length];
    const qtds = QUARTERS.map(q=>`<td>${{fmtN(t5[p].qtr_los[q]||0)}}</td>`).join('');
    return `<tr><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${{c}};margin-right:6px"></span>${{p}}</td>${{qtds}}<td><strong>${{fmtDollar(t5[p].total_net)}}</strong></td></tr>`;
  }}).join('');
}}

// ===== DENIALS =====
function buildDenials(hid, hosp, color) {{
  const dr = hosp.denial_rate;
  const payors = Object.keys(dr).filter(p=>dr[p].gross>0).sort((a,b)=>dr[b].rate-dr[a].rate);
  const rates = payors.map(p=>dr[p].rate);
  const bgColors = rates.map(r=>r>5?'#dc3545':r>1?'#ff9800':'#2e7d32');

  makeChart(hid+'-denial-chart', {{
    type:'bar',
    data:{{labels:payors,datasets:[{{label:'Denial Rate %',data:rates,backgroundColor:bgColors,borderRadius:4}}]}},
    options:{{
      responsive:true,maintainAspectRatio:false,indexAxis:'y',
      plugins:{{legend:{{display:false}},tooltip:{{callbacks:{{label:ctx=>` Denial Rate: ${{ctx.raw.toFixed(2)}}%`}}}}}},
      scales:{{x:{{title:{{display:true,text:'Denial Rate (%)'}},ticks:{{callback:v=>v+'%'}}}}}}
    }}
  }});

  const tbody = document.querySelector(`#${{hid}}-denial-table tbody`);
  const totalGross = payors.reduce((s,p)=>s+dr[p].gross,0);
  const totalDenial = payors.reduce((s,p)=>s+dr[p].denial_adj,0);
  const overallRate = totalGross ? (totalDenial/totalGross*100) : 0;
  tbody.innerHTML = payors.map(p=>{{
    const v = dr[p];
    const rateClass = v.rate>5?'denial-rate-high':v.rate>0?'':'denial-rate-low';
    return `<tr>
      <td>${{p}}</td>
      <td>${{fmtDollar(v.gross)}}</td>
      <td>${{fmtDollar(v.net)}}</td>
      <td>${{fmtDollar(v.denial_adj)}}</td>
      <td class="${{rateClass}}">${{v.rate.toFixed(2)}}%</td>
      <td>${{fmtN(v.los)}}</td>
    </tr>`;
  }}).join('');
  tbody.innerHTML += `<tr style="font-weight:700;background:#f8f9fa">
    <td>TOTAL</td><td>${{fmtDollar(totalGross)}}</td><td>—</td><td>${{fmtDollar(totalDenial)}}</td>
    <td class="${{overallRate>5?'denial-rate-high':''}}">${{overallRate.toFixed(2)}}%</td><td>—</td>
  </tr>`;
}}

// ===== COVERED LIVES =====
function buildCoveredLives(hid, color) {{
  const cl = RAW_DATA.covered_lives;
  const totals = {{total:0,ma:0,commercial:0,mm:0}};
  cl.forEach(r=>{{
    totals.total += r.total||0;
    totals.ma += r.medicare_advantage||0;
    totals.commercial += r.commercial||0;
    totals.mm += r.managed_medicaid||0;
  }});

  const summaryEl = document.getElementById(hid+'-lives-summary');
  summaryEl.innerHTML = [
    {{label:'Total Covered Lives',val:fmtN(totals.total),icon:'bi-people'}},
    {{label:'Medicare Advantage',val:fmtN(totals.ma),icon:'bi-heart-pulse'}},
    {{label:'Commercial',val:fmtN(totals.commercial),icon:'bi-briefcase'}},
    {{label:'Managed Medicaid',val:fmtN(totals.mm),icon:'bi-shield-plus'}},
  ].map(k=>`<div class="lives-kpi">
    <div class="val">${{k.val}}</div>
    <div class="lbl"><i class="bi ${{k.icon}}"></i> ${{k.label}}</div>
  </div>`).join('');

  // Top 10 by total
  const top10 = [...cl].sort((a,b)=>(b.total||0)-(a.total||0)).slice(0,10);
  makeChart(hid+'-lives-chart', {{
    type:'bar',
    data:{{
      labels:top10.map(r=>r.payor.length>18?r.payor.slice(0,18)+'…':r.payor),
      datasets:[
        {{label:'Medicare Advantage',data:top10.map(r=>r.medicare_advantage||0),backgroundColor:'#6a1b9a88'}},
        {{label:'Commercial',data:top10.map(r=>r.commercial||0),backgroundColor:'#1a6eb588'}},
        {{label:'Managed Medicaid',data:top10.map(r=>r.managed_medicaid||0),backgroundColor:'#e6510088'}},
      ]
    }},
    options:{{
      responsive:true,maintainAspectRatio:true,indexAxis:'y',
      plugins:{{legend:{{position:'top'}}}},
      scales:{{x:{{stacked:true,ticks:{{callback:v=>fmtN(v)}}}},y:{{stacked:true}}}}
    }}
  }});

  const tbody = document.querySelector(`#${{hid}}-lives-table tbody`);
  tbody.innerHTML = top10.map(r=>`<tr>
    <td><strong>${{r.payor}}</strong></td>
    <td>${{fmtN(r.total)}}</td>
    <td>${{fmtN(r.medicare_advantage)}}</td>
    <td>${{fmtN(r.commercial)}}</td>
    <td>${{fmtN(r.managed_medicaid)}}</td>
  </tr>`).join('');
}}

// ===== REGIONAL =====
function buildRegional(hid, h, hosp) {{
  const region = h.region;
  const regionFacilities = RAW_DATA.facilities.filter(f => {{
    const ri = RAW_DATA.regional_info.find(r=>r.name && r.name.trim().includes(f.split(' ')[0]));
    return ri && ri.region === region;
  }});

  // Use all 4 facilities for comparison since we have data for all
  const allFacs = RAW_DATA.facilities;
  const grid = document.getElementById(hid+'-region-grid');
  const hosps_cfg = HOSPITALS_CFG;

  grid.innerHTML = allFacs.map(fac=>{{
    const fd = RAW_DATA.hospitals[fac];
    const hcfg = hosps_cfg.find(x=>x.facility===fac);
    const col = hcfg ? hcfg.color : '#1a6eb5';
    const isThis = fac===h.facility;
    return `<div class="region-card" style="border-top-color:${{col}};${{isThis?'box-shadow:0 4px 20px rgba(0,0,0,.15);':''}}">
      <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;color:${{col}};letter-spacing:.5px;margin-bottom:6px">
        ${{isThis?'&#9679; ':''}}&nbsp;${{fac}}
      </div>
      <div style="font-size:.82rem;color:#666;margin-bottom:10px">${{hcfg?.location||''}}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <div><div style="font-size:.7rem;color:#999">Patient Days</div><div style="font-weight:700">${{fmtN(fd.totals.los)}}</div></div>
        <div><div style="font-size:.7rem;color:#999">Admits</div><div style="font-weight:700">${{fmtN(fd.totals.admits)}}</div></div>
        <div><div style="font-size:.7rem;color:#999">Gross Rev</div><div style="font-weight:700;font-size:.85rem">${{fmtDollar(fd.totals.gross)}}</div></div>
        <div><div style="font-size:.7rem;color:#999">Net Rev</div><div style="font-weight:700;font-size:.85rem">${{fmtDollar(fd.totals.net)}}</div></div>
      </div>
    </div>`;
  }}).join('');

  makeChart(hid+'-region-chart', {{
    type:'bar',
    data:{{
      labels:allFacs.map(f=>f.replace('Columbus Springs ','CS ')),
      datasets:[
        {{label:'Patient Days',data:allFacs.map(f=>RAW_DATA.hospitals[f].totals.los),backgroundColor:hosps_cfg.map(hc=>hc.color+'99'),yAxisID:'y'}},
        {{label:'Net Revenue',data:allFacs.map(f=>RAW_DATA.hospitals[f].totals.net),backgroundColor:hosps_cfg.map(hc=>hc.color+'44'),yAxisID:'y1'}},
      ]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top'}}}},
      scales:{{
        y:{{title:{{display:true,text:'Patient Days'}},ticks:{{callback:v=>fmtN(v)}}}},
        y1:{{position:'right',title:{{display:true,text:'Net Revenue'}},grid:{{drawOnChartArea:false}},ticks:{{callback:v=>fmtDollar(v)}}}}
      }}
    }}
  }});
}}

// ===== EXEC INSIGHTS =====
function buildInsights(hid, hosp, h) {{
  const pm = hosp.payor_mix;
  const t = hosp.totals;
  const avgRevPerDay = t.net/t.los;
  const netMargin = (t.net/t.gross*100).toFixed(1);
  const commPct = pm['Commercial']?.pct||0;
  const medAdv = pm['Medicare Advantage']?.pct||0;
  const mmPct = pm['Managed Medicaid']?.pct||0;
  const selfPay = pm['Self Pay']?.pct||0;
  const medRPD = pm['Medicare']?.rev_per_day||0;
  const commRPD = pm['Commercial']?.rev_per_day||0;

  // Denial data for 2026
  const dr = hosp.denial_rate;
  const totalGross2026 = Object.values(dr).reduce((s,v)=>s+v.gross,0);
  const totalDenial2026 = Object.values(dr).reduce((s,v)=>s+v.denial_adj,0);
  const overallDenialRate = totalGross2026 ? (totalDenial2026/totalGross2026*100) : 0;

  // Quarterly trend
  const q1_25 = hosp.qtr_summary['1Q25'];
  const q1_26 = hosp.qtr_summary['1Q26'];
  const losTrend = q1_26 && q1_25 ? ((q1_26.los - q1_25.los)/q1_25.los*100) : 0;
  const netTrend = q1_26 && q1_25 ? ((q1_26.net - q1_25.net)/q1_25.net*100) : 0;

  // Top payor by gross
  const topGrossPayor = hosp.top5_gross_payors[0];

  const insights = [
    {{
      icon:'bi-graph-up-arrow', bg:'#e8f5e9', color:'#2e7d32',
      title:'Revenue Yield Optimization',
      text:`Net revenue per patient day is <strong>${{fmtDollar(avgRevPerDay)}}</strong> (blended). Medicare yields the highest rate at <strong>${{fmtDollar(medRPD)}}/day</strong> vs. Commercial at <strong>${{fmtDollar(commRPD)}}/day</strong>. Focus on clinical documentation improvement (CDI) to maximize Medicare DRG optimization.`
    }},
    {{
      icon:'bi-pie-chart', bg:'#e8f0fa', color:'#1a6eb5',
      title:'Payor Mix Strategy',
      text:`Commercial accounts for <strong>${{commPct}}%</strong> of patient days — the highest-yield non-government segment. Managed Medicaid represents <strong>${{mmPct}}%</strong> of days with lower yield. Evaluate contract renegotiation opportunities with top Managed Medicaid payors to improve rate realization.`
    }},
    {{
      icon:'bi-shield-exclamation', bg:'#fff3e0', color:'#e65100',
      title:'Denial Management Priority',
      text:`2026 YTD overall denial adjustment rate is <strong>${{overallDenialRate.toFixed(2)}}%</strong>. Implement concurrent review workflows and pre-authorization tracking, especially for ${{topGrossPayor}} (largest gross payor). Target reduction to under 2% through real-time denial tracking.`
    }},
    {{
      icon:'bi-person-x', bg:'#fce4ec', color:'#c62828',
      title:'Self-Pay Risk Mitigation',
      text:`Self-Pay comprises <strong>${{selfPay}}%</strong> of patient days. Deploy financial counselors at point-of-service to connect patients with Medicaid eligibility, charity programs, and payment plans. Early intervention reduces bad debt and improves community benefit metrics.`
    }},
    {{
      icon:'bi-arrow-up-circle', bg:'#e0f7fa', color:'#00695c',
      title:'Volume & Net Revenue Trend',
      text:`Comparing 1Q25 vs. 1Q26: patient days changed by <strong>${{losTrend.toFixed(1)}}%</strong> and net revenue changed by <strong>${{netTrend.toFixed(1)}}%</strong>. Note: 1Q26 reflects partial quarter data. Monitor census trends weekly to project full-year performance and adjust staffing ratios accordingly.`
    }},
    {{
      icon:'bi-star-fill', bg:'#f3e5f5', color:'#6a1b9a',
      title:'Medicare Advantage Growth Opportunity',
      text:`Medicare Advantage represents <strong>${{medAdv}}%</strong> of patient days with a yield of <strong>${{fmtDollar(pm['Medicare Advantage']?.rev_per_day||0)}}/day</strong>. With covered lives data showing UnitedHealth Group (371K) and Anthem/BCBS (200K) as market leaders, strengthening in-network contracts with these carriers can drive high-yield MA volume growth.`
    }},
    {{
      icon:'bi-buildings', bg:'#e8f4fd', color:'#0077b6',
      title:'Program Mix Efficiency',
      text:`Inpatient (IP) days carry the highest revenue per day. PHP and IOP programs serve higher volumes with lower per-day yields. Evaluate throughput and length-of-stay protocols for IP to ensure appropriate level-of-care transitions that optimize both clinical outcomes and financial performance.`
    }},
  ];

  const el = document.getElementById(hid+'-insight-list');
  el.innerHTML = insights.map(ins=>`
    <li>
      <div class="insight-icon" style="background:${{ins.bg}};color:${{ins.color}}"><i class="bi ${{ins.icon}}"></i></div>
      <div>
        <div style="font-weight:700;font-size:.9rem;margin-bottom:2px">${{ins.title}}</div>
        <div style="font-size:.83rem;color:#444;line-height:1.5">${{ins.text}}</div>
      </div>
    </li>`).join('');
}}

// ===== RATIO ANALYSIS =====
function buildRatioAnalysis(hid, hosp, color) {{
  const pm = hosp.payor_mix;
  const sorted = Object.entries(pm).sort((a,b)=>b[1].los-a[1].los);
  const totLOS = sorted.reduce((s,[,v])=>s+v.los,0);
  const totNet = sorted.reduce((s,[,v])=>s+v.net,0);

  makeChart(hid+'-ratio-chart', {{
    type:'bar',
    data:{{
      labels:sorted.map(([fc])=>fc),
      datasets:[
        {{label:'Patient Days',data:sorted.map(([,v])=>v.los),backgroundColor:sorted.map(([fc])=>FC_COLORS[fc]||'#999'),yAxisID:'y'}},
        {{label:'Rev/Patient Day',data:sorted.map(([,v])=>v.rev_per_day),type:'line',borderColor:'#0077b6',yAxisID:'y1',tension:.3,pointRadius:5}},
      ]
    }},
    options:{{
      responsive:true,maintainAspectRatio:false,
      plugins:{{legend:{{position:'top'}}}},
      scales:{{
        y:{{title:{{display:true,text:'Patient Days'}},ticks:{{callback:v=>fmtN(v)}}}},
        y1:{{position:'right',title:{{display:true,text:'Rev/Patient Day'}},grid:{{drawOnChartArea:false}},ticks:{{callback:v=>fmtDollar(v)}}}}
      }}
    }}
  }});

  const tbody = document.querySelector(`#${{hid}}-ratio-table tbody`);
  tbody.innerHTML = sorted.map(([fc,v])=>{{
    const daysPct = totLOS ? (v.los/totLOS*100) : 0;
    const netPct = totNet ? (v.net/totNet*100) : 0;
    const fcColor = FC_COLORS[fc]||'#999';
    return `<tr>
      <td><span class="badge-fc" style="background:${{fcColor}}22;color:${{fcColor}}">${{fc}}</span></td>
      <td>${{fmtN(v.los)}}</td>
      <td><strong>${{fmtDollar(v.rev_per_day)}}</strong></td>
      <td>
        <div class="bar-cell">
          <div class="bar-bg"><div class="bar-fill" style="width:${{daysPct}}%;background:${{fcColor}}"></div></div>
          <span style="font-size:.8rem">${{daysPct.toFixed(1)}}%</span>
        </div>
      </td>
      <td>
        <div class="bar-cell">
          <div class="bar-bg"><div class="bar-fill" style="width:${{netPct}}%;background:#2e7d32"></div></div>
          <span style="font-size:.8rem">${{netPct.toFixed(1)}}%</span>
        </div>
      </td>
    </tr>`;
  }}).join('');
}}

// ===================================================
// FILE UPLOAD (SheetJS)
// ===================================================
function handleUpload(input) {{
  const file = input.files[0];
  if (!file) return;
  const hid = input.id.replace('-file','');
  const statusEl = document.getElementById(hid+'-upload-status');
  statusEl.innerHTML = '<i class="bi bi-hourglass-split"></i> Reading file...';

  const reader = new FileReader();
  reader.onload = function(e) {{
    try {{
      const wb = XLSX.read(e.target.result, {{type:'array',cellDates:true}});
      const ws = wb.Sheets['Base Data'];
      if (!ws) {{ statusEl.innerHTML = '<span style="color:red"><i class="bi bi-x-circle"></i> Sheet "Base Data" not found.</span>'; return; }}
      const rows = XLSX.utils.sheet_to_json(ws, {{header:1,raw:false}});
      statusEl.innerHTML = `<span style="color:green"><i class="bi bi-check-circle"></i> File loaded: ${{rows.length-1}} records found. Refreshing dashboard...</span>`;
      // Full re-parse and rebuild
      rebuildFromRows(rows, hid);
    }} catch(err) {{
      statusEl.innerHTML = `<span style="color:red"><i class="bi bi-x-circle"></i> Error: ${{err.message}}</span>`;
    }}
  }};
  reader.readAsArrayBuffer(file);
}}

function rebuildFromRows(rows, hid) {{
  // Parse rows into data records
  const headers = rows[0];
  const COL = {{}};
  headers.forEach((h,i)=>{{ COL[h]=i; }});

  const records = [];
  for (let i=1;i<rows.length;i++) {{
    const r = rows[i];
    if (!r[COL['Facility Name']]) continue;
    records.push({{
      facility: r[COL['Facility Name']],
      admits: parseFloat(r[COL['Admits']])||0,
      payor_summary: r[COL['Payor Summary']],
      qtr: r[COL['QTR']],
      program_type: r[COL['Program Type']],
      financial_class: r[COL['Financial Class']],
      los: parseFloat(r[COL['LOS']])||0,
      gross_charges: parseFloat(r[COL['Total Gross Charges']])||0,
      net_charges: parseFloat(r[COL['Total Net Charges']])||0,
      denial_adj: parseFloat(r[COL['Denial Adjustments']])||0,
    }});
  }};

  // Rebuild facility data
  const facilities = [...new Set(records.map(r=>r.facility))];
  facilities.forEach(fac => {{
    const recs = records.filter(r=>r.facility===fac);
    RAW_DATA.hospitals[fac] = computeHospitalData(recs);
  }});
  RAW_DATA.facilities = facilities;

  // Persist to localStorage so data survives page refresh
  saveData();

  // Rebuild dashboards
  Object.keys(dashBuilt).forEach(hid => {{ dashBuilt[hid] = false; }});
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  if (h) buildDashboard(hid);

  const statusEl = document.getElementById(hid+'-upload-status');
  statusEl.innerHTML = `<span style="color:green"><i class="bi bi-check2-all"></i> Upload complete — this is now the master data. It will remain active until you upload a new file.</span>`;
  document.querySelectorAll('[id$="-saved-notice"]').forEach(el => el.style.display = 'block');
}}

function computeHospitalData(recs) {{
  const QTRS = ["1Q25","2Q25","3Q25","4Q25","1Q26"];
  const agg = (arr, field) => arr.reduce((s,r)=>s+(r[field]||0),0);
  const groupBy = (arr, key) => arr.reduce((g,r)=>{{ (g[r[key]]=g[r[key]]||[]).push(r); return g; }}, {{}});

  const fc_groups = groupBy(recs, 'financial_class');
  const payor_groups = groupBy(recs, 'payor_summary');
  const qtr_groups = groupBy(recs, 'qtr');
  const prog_groups = groupBy(recs, 'program_type');

  const totLOS = agg(recs,'los');
  const payor_mix = {{}};
  Object.entries(fc_groups).forEach(([fc,arr])=>{{
    const los=agg(arr,'los'), gross=agg(arr,'gross_charges'), net=agg(arr,'net_charges'), admits=agg(arr,'admits');
    payor_mix[fc]={{los,gross:Math.round(gross*100)/100,net:Math.round(net*100)/100,admits,
      pct:Math.round(los/totLOS*1000)/10, rev_per_day:los?Math.round(net/los*100)/100:0,
      avg_los:admits?Math.round(los/admits*10)/10:0}};
  }});

  const payor_gross = {{}};
  const payor_net = {{}};
  Object.entries(payor_groups).forEach(([p,arr])=>{{
    payor_gross[p]=agg(arr,'gross_charges');
    payor_net[p]=agg(arr,'net_charges');
  }});
  const top5g = Object.entries(payor_gross).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([p])=>p);
  const top5n = Object.entries(payor_net).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([p])=>p);

  const mkTop5 = (payors, totalField) => {{
    const res={{}};
    payors.forEach(p=>{{
      const qtr_los={{}};
      QTRS.forEach(q=>{{ qtr_los[q]=agg((payor_groups[p]||[]).filter(r=>r.qtr===q),'los'); }});
      res[p]={{qtr_los, [totalField]: Math.round(payor_gross[p]*100)/100}};
    }});
    return res;
  }};

  const qtr_summary={{}};
  QTRS.forEach(q=>{{
    const arr=qtr_groups[q]||[];
    qtr_summary[q]={{los:agg(arr,'los'),gross:Math.round(agg(arr,'gross_charges')*100)/100,
      net:Math.round(agg(arr,'net_charges')*100)/100,admits:agg(arr,'admits')}};
  }});

  const program_mix={{}};
  Object.entries(prog_groups).forEach(([pt,arr])=>{{
    program_mix[pt||'Unknown']={{los:agg(arr,'los'),gross:Math.round(agg(arr,'gross_charges')*100)/100,
      net:Math.round(agg(arr,'net_charges')*100)/100,admits:agg(arr,'admits')}};
  }});

  const recs2026=recs.filter(r=>r.qtr==='1Q26');
  const pg2026=groupBy(recs2026,'payor_summary');
  const denial_rate={{}};
  Object.entries(pg2026).forEach(([p,arr])=>{{
    const gross=agg(arr,'gross_charges'), net=agg(arr,'net_charges'), denial=arr.reduce((s,r)=>s+Math.abs(r.denial_adj||0),0), los=agg(arr,'los'), admits=agg(arr,'admits');
    denial_rate[p]={{gross:Math.round(gross*100)/100,net:Math.round(net*100)/100,denial_adj:Math.round(denial*100)/100,
      rate:gross?Math.round(denial/gross*10000)/100:0,los,admits}};
  }});

  return {{payor_mix,top5_gross:mkTop5(top5g,'total_gross'),top5_gross_payors:top5g,
    top5_net:mkTop5(top5n,'total_net'),top5_net_payors:top5n,
    denial_rate,qtr_summary,program_mix,
    totals:{{los:agg(recs,'los'),gross:Math.round(agg(recs,'gross_charges')*100)/100,
      net:Math.round(agg(recs,'net_charges')*100)/100,admits:agg(recs,'admits')}}}};
}}

// Show uploaded-data notice on load if localStorage has data
(function() {{
  try {{
    if (localStorage.getItem(STORAGE_KEY)) {{
      document.querySelectorAll('[id$="-saved-notice"]').forEach(el => el.style.display = 'block');
    }}
  }} catch(e) {{}}
}})();

// Drag and drop support
document.querySelectorAll('.upload-zone').forEach(zone => {{
  zone.addEventListener('dragover', e => {{ e.preventDefault(); zone.style.borderColor='#0077b6'; }});
  zone.addEventListener('dragleave', () => {{ zone.style.borderColor=''; }});
  zone.addEventListener('drop', e => {{
    e.preventDefault();
    zone.style.borderColor='';
    const hid = zone.id.replace('-dropzone','');
    const fileInput = document.getElementById(hid+'-file');
    fileInput.files = e.dataTransfer.files;
    handleUpload(fileInput);
  }});
}});
</script>
</body>
</html>'''

with open('C:/Users/jennm/Desktop/Dashboard Files/hospital_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Done! hospital_dashboard.html created ({len(html):,} bytes)")
