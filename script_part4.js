// ===== COVERED LIVES (no Program Type filter — payor market data, not encounter data) =====
function buildCoveredLives(hid, color) {
  const cl = COVERED_LIVES;
  const totals = {total:0,ma:0,commercial:0,mm:0};
  cl.forEach(r=>{
    totals.total += r.total||0;
    totals.ma += r.medicare_advantage||0;
    totals.commercial += r.commercial||0;
    totals.mm += r.managed_medicaid||0;
  });

  const summaryEl = document.getElementById(hid+'-lives-summary');
  summaryEl.innerHTML = [
    {label:'Total Covered Lives',val:fmtN(totals.total),icon:'bi-people'},
    {label:'Medicare Advantage',val:fmtN(totals.ma),icon:'bi-heart-pulse'},
    {label:'Commercial',val:fmtN(totals.commercial),icon:'bi-briefcase'},
    {label:'Managed Medicaid',val:fmtN(totals.mm),icon:'bi-shield-plus'},
  ].map(k=>`<div class="lives-kpi">
    <div class="val">${k.val}</div>
    <div class="lbl"><i class="bi ${k.icon}"></i> ${k.label}</div>
  </div>`).join('');

  const top10 = [...cl].sort((a,b)=>(b.total||0)-(a.total||0)).slice(0,10);
  makeChart(hid+'-lives-chart', {
    type:'bar',
    data:{
      labels:top10.map(r=>r.payor.length>18?r.payor.slice(0,18)+'…':r.payor),
      datasets:[
        {label:'Medicare Advantage',data:top10.map(r=>r.medicare_advantage||0),backgroundColor:'#6a1b9a88'},
        {label:'Commercial',data:top10.map(r=>r.commercial||0),backgroundColor:'#1a6eb588'},
        {label:'Managed Medicaid',data:top10.map(r=>r.managed_medicaid||0),backgroundColor:'#e6510088'},
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:true,indexAxis:'y',
      plugins:{legend:{position:'top'}},
      scales:{x:{stacked:true,ticks:{callback:v=>fmtN(v)}},y:{stacked:true}}
    }
  });

  const tbody = document.querySelector(`#${hid}-lives-table tbody`);
  tbody.innerHTML = top10.map(r=>`<tr>
    <td><strong>${r.payor}</strong></td>
    <td>${fmtN(r.total)}</td>
    <td>${fmtN(r.medicare_advantage)}</td>
    <td>${fmtN(r.commercial)}</td>
    <td>${fmtN(r.managed_medicaid)}</td>
  </tr>`).join('');
}

// ===== REGIONAL (Program Type filter — recomputes each facility's totals for that type) =====
function buildRegionalSection(hid) {
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  const filter = getFilter(hid, 'regional');
  const container = document.getElementById(hid+'-regional');
  injectFilterBar(container, hid, 'regional', h.color, false);

  const facTotals = {};
  FACILITIES.forEach(fac => {
    const recs = RAW_DATA.filter(r => r.f === fac && (filter.programType === 'All' || r.pt === filter.programType));
    facTotals[fac] = aggregateRecords(recs).totals;
  });
  buildRegional(hid, h, facTotals);
}

function buildRegional(hid, h, facTotals) {
  const grid = document.getElementById(hid+'-region-grid');
  const allFacs = FACILITIES;

  grid.innerHTML = allFacs.map(fac=>{
    const fd = facTotals[fac];
    const hcfg = HOSPITALS_CFG.find(x=>x.facility===fac);
    const col = hcfg ? hcfg.color : '#1a6eb5';
    const isThis = fac===h.facility;
    return `<div class="region-card" style="border-top-color:${col};${isThis?'box-shadow:0 4px 20px rgba(0,0,0,.15);':''}">
      <div style="font-size:.7rem;font-weight:700;text-transform:uppercase;color:${col};letter-spacing:.5px;margin-bottom:6px">
        ${isThis?'&#9679; ':''}&nbsp;${fac}
      </div>
      <div style="font-size:.82rem;color:#666;margin-bottom:10px">${hcfg?.location||''}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <div><div style="font-size:.7rem;color:#999">Patient Days</div><div style="font-weight:700">${fmtN(fd.los)}</div></div>
        <div><div style="font-size:.7rem;color:#999">Admits</div><div style="font-weight:700">${fmtN(fd.admits)}</div></div>
        <div><div style="font-size:.7rem;color:#999">Gross Rev</div><div style="font-weight:700;font-size:.85rem">${fmtDollar(fd.gross)}</div></div>
        <div><div style="font-size:.7rem;color:#999">Net Rev</div><div style="font-weight:700;font-size:.85rem">${fmtDollar(fd.net)}</div></div>
      </div>
    </div>`;
  }).join('');

  makeChart(hid+'-region-chart', {
    type:'bar',
    data:{
      labels:allFacs.map(f=>f.replace('Columbus Springs ','CS ')),
      datasets:[
        {label:'Patient Days',data:allFacs.map(f=>facTotals[f].los),backgroundColor:HOSPITALS_CFG.map(hc=>hc.color+'99'),yAxisID:'y'},
        {label:'Net Revenue',data:allFacs.map(f=>facTotals[f].net),backgroundColor:HOSPITALS_CFG.map(hc=>hc.color+'44'),yAxisID:'y1'},
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

// ===== EXEC INSIGHTS + RATIO ANALYSIS (shared Program Type filter) =====
function buildInsightsSection(hid) {
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  const filter = getFilter(hid, 'insights');
  const hosp = aggregateRecords(filterRecords(hid, {programType: filter.programType}));
  const container = document.getElementById(hid+'-insights');
  injectFilterBar(container, hid, 'insights', h.color, false);
  buildInsights(hid, hosp, h);
  buildRatioAnalysis(hid, hosp);
}

function buildInsights(hid, hosp, h) {
  const pm = hosp.payor_mix;
  const t = hosp.totals;
  const avgRevPerDay = t.los ? t.net/t.los : 0;
  const netMargin = t.gross ? (t.net/t.gross*100).toFixed(1) : '0.0';
  const commPct = pm['Commercial']?.pct||0;
  const medAdv = pm['Medicare Advantage']?.pct||0;
  const mmPct = pm['Managed Medicaid']?.pct||0;
  const selfPay = pm['Self Pay']?.pct||0;
  const medRPD = pm['Medicare']?.rev_per_day||0;
  const commRPD = pm['Commercial']?.rev_per_day||0;

  const dr = hosp.denial_rate;
  const totalGross2026 = Object.values(dr).reduce((s,v)=>s+v.gross,0);
  const totalDenial2026 = Object.values(dr).reduce((s,v)=>s+v.denial_adj,0);
  const overallDenialRate = totalGross2026 ? (totalDenial2026/totalGross2026*100) : 0;

  const q1_25 = hosp.qtr_summary['1Q25'];
  const q1_26 = hosp.qtr_summary['1Q26'];
  const losTrend = (q1_26 && q1_25 && q1_25.los) ? ((q1_26.los - q1_25.los)/q1_25.los*100) : 0;
  const netTrend = (q1_26 && q1_25 && q1_25.net) ? ((q1_26.net - q1_25.net)/q1_25.net*100) : 0;

  const topGrossPayor = hosp.top5_gross_payors[0] || '—';

  const insights = [
    {
      icon:'bi-graph-up-arrow', bg:'#e8f5e9', color:'#2e7d32',
      title:'Revenue Yield Optimization',
      text:`Net revenue per patient day is <strong>${fmtDollar(avgRevPerDay)}</strong> (blended). Medicare yields the highest rate at <strong>${fmtDollar(medRPD)}/day</strong> vs. Commercial at <strong>${fmtDollar(commRPD)}/day</strong>. Focus on clinical documentation improvement (CDI) to maximize Medicare DRG optimization.`
    },
    {
      icon:'bi-pie-chart', bg:'#e8f0fa', color:'#1a6eb5',
      title:'Payor Mix Strategy',
      text:`Commercial accounts for <strong>${commPct}%</strong> of patient days — the highest-yield non-government segment. Managed Medicaid represents <strong>${mmPct}%</strong> of days with lower yield. Evaluate contract renegotiation opportunities with top Managed Medicaid payors to improve rate realization.`
    },
    {
      icon:'bi-shield-exclamation', bg:'#fff3e0', color:'#e65100',
      title:'Denial Management Priority',
      text:`2026 YTD overall denial adjustment rate is <strong>${overallDenialRate.toFixed(2)}%</strong>. Implement concurrent review workflows and pre-authorization tracking, especially for ${topGrossPayor} (largest gross payor). Target reduction to under 2% through real-time denial tracking.`
    },
    {
      icon:'bi-person-x', bg:'#fce4ec', color:'#c62828',
      title:'Self-Pay Risk Mitigation',
      text:`Self-Pay comprises <strong>${selfPay}%</strong> of patient days. Deploy financial counselors at point-of-service to connect patients with Medicaid eligibility, charity programs, and payment plans. Early intervention reduces bad debt and improves community benefit metrics.`
    },
    {
      icon:'bi-arrow-up-circle', bg:'#e0f7fa', color:'#00695c',
      title:'Volume & Net Revenue Trend',
      text:`Comparing 1Q25 vs. 1Q26: patient days changed by <strong>${losTrend.toFixed(1)}%</strong> and net revenue changed by <strong>${netTrend.toFixed(1)}%</strong>. Note: 1Q26 reflects partial quarter data. Monitor census trends weekly to project full-year performance and adjust staffing ratios accordingly.`
    },
    {
      icon:'bi-star-fill', bg:'#f3e5f5', color:'#6a1b9a',
      title:'Medicare Advantage Growth Opportunity',
      text:`Medicare Advantage represents <strong>${medAdv}%</strong> of patient days with a yield of <strong>${fmtDollar(pm['Medicare Advantage']?.rev_per_day||0)}/day</strong>. With covered lives data showing UnitedHealth Group (371K) and Anthem/BCBS (200K) as market leaders, strengthening in-network contracts with these carriers can drive high-yield MA volume growth.`
    },
    {
      icon:'bi-buildings', bg:'#e8f4fd', color:'#0077b6',
      title:'Program Mix Efficiency',
      text:`Inpatient (IP) days carry the highest revenue per day. PHP and IOP programs serve higher volumes with lower per-day yields. Evaluate throughput and length-of-stay protocols for IP to ensure appropriate level-of-care transitions that optimize both clinical outcomes and financial performance.`
    },
  ];

  const el = document.getElementById(hid+'-insight-list');
  el.innerHTML = insights.map(ins=>`
    <li>
      <div class="insight-icon" style="background:${ins.bg};color:${ins.color}"><i class="bi ${ins.icon}"></i></div>
      <div>
        <div style="font-weight:700;font-size:.9rem;margin-bottom:2px">${ins.title}</div>
        <div style="font-size:.83rem;color:#444;line-height:1.5">${ins.text}</div>
      </div>
    </li>`).join('');
}

function buildRatioAnalysis(hid, hosp) {
  const pm = hosp.payor_mix;
  const sorted = Object.entries(pm).sort((a,b)=>b[1].los-a[1].los);
  const totLOS = sorted.reduce((s,[,v])=>s+v.los,0);
  const totNet = sorted.reduce((s,[,v])=>s+v.net,0);

  makeChart(hid+'-ratio-chart', {
    type:'bar',
    data:{
      labels:sorted.map(([fc])=>fc),
      datasets:[
        {label:'Patient Days',data:sorted.map(([,v])=>v.los),backgroundColor:sorted.map(([fc])=>FC_COLORS[fc]||'#999'),yAxisID:'y'},
        {label:'Rev/Patient Day',data:sorted.map(([,v])=>v.rev_per_day),type:'line',borderColor:'#0077b6',yAxisID:'y1',tension:.3,pointRadius:5},
      ]
    },
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:'top'}},
      scales:{
        y:{title:{display:true,text:'Patient Days'},ticks:{callback:v=>fmtN(v)}},
        y1:{position:'right',title:{display:true,text:'Rev/Patient Day'},grid:{drawOnChartArea:false},ticks:{callback:v=>fmtDollar(v)}}
      }
    }
  });

  const tbody = document.querySelector(`#${hid}-ratio-table tbody`);
  tbody.innerHTML = sorted.map(([fc,v])=>{
    const daysPct = totLOS ? (v.los/totLOS*100) : 0;
    const netPct = totNet ? (v.net/totNet*100) : 0;
    const fcColor = FC_COLORS[fc]||'#999';
    return `<tr>
      <td><span class="badge-fc" style="background:${fcColor}22;color:${fcColor}">${fc}</span></td>
      <td>${fmtN(v.los)}</td>
      <td><strong>${fmtDollar(v.rev_per_day)}</strong></td>
      <td>
        <div class="bar-cell">
          <div class="bar-bg"><div class="bar-fill" style="width:${daysPct}%;background:${fcColor}"></div></div>
          <span style="font-size:.8rem">${daysPct.toFixed(1)}%</span>
        </div>
      </td>
      <td>
        <div class="bar-cell">
          <div class="bar-bg"><div class="bar-fill" style="width:${netPct}%;background:#2e7d32"></div></div>
          <span style="font-size:.8rem">${netPct.toFixed(1)}%</span>
        </div>
      </td>
    </tr>`;
  }).join('');
}
