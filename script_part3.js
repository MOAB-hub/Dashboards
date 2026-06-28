// ===== PAYOR MIX (Program Type filter) =====
function buildPayorMixSection(hid) {
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  const filter = getFilter(hid, 'payorMix');
  const hosp = aggregateRecords(filterRecords(hid, {programType: filter.programType}));
  const container = document.getElementById(hid+'-payor-mix');
  injectFilterBar(container, hid, 'payorMix', h.color, false);
  buildPayorMixTable(hid, hosp, h.color);
  buildPayorMixCharts(hid, hosp, h.color);
}

function buildPayorMixTable(hid, hosp, color) {
  const pm = hosp.payor_mix;
  const sorted = Object.entries(pm).sort((a,b)=>b[1].pct-a[1].pct);
  const tbody = document.querySelector(`#${hid}-pm-table tbody`);
  tbody.innerHTML = sorted.map(([fc,v])=>{
    const fcColor = FC_COLORS[fc]||'#999';
    return `<tr>
      <td><span class="badge-fc" style="background:${fcColor}22;color:${fcColor}">${fc}</span></td>
      <td>${fmtN(v.los)}</td>
      <td>
        <div class="bar-cell">
          <div class="bar-bg" style="--hcolor:${fcColor}"><div class="bar-fill" style="width:${v.pct}%;background:${fcColor}"></div></div>
          <span style="font-size:.8rem;font-weight:600;color:${fcColor}">${v.pct}%</span>
        </div>
      </td>
      <td>${fmtN(v.admits)}</td>
      <td>${v.avg_los}</td>
      <td>${fmtDollar(v.gross)}</td>
      <td>${fmtDollar(v.net)}</td>
      <td><strong>${fmtDollar(v.rev_per_day)}</strong></td>
    </tr>`;
  }).join('');
  const totLOS = sorted.reduce((s,[,v])=>s+v.los,0);
  const totGross = sorted.reduce((s,[,v])=>s+v.gross,0);
  const totNet = sorted.reduce((s,[,v])=>s+v.net,0);
  const totAdmits = sorted.reduce((s,[,v])=>s+v.admits,0);
  tbody.innerHTML += `<tr style="font-weight:700;background:#f8f9fa">
    <td>TOTAL</td><td>${fmtN(totLOS)}</td><td>100%</td><td>${fmtN(totAdmits)}</td><td>—</td>
    <td>${fmtDollar(totGross)}</td><td>${fmtDollar(totNet)}</td><td>${totLOS ? fmtDollar(totNet/totLOS) : fmtDollar(0)}</td>
  </tr>`;
}

function buildPayorMixCharts(hid, hosp, color) {
  const pm = hosp.payor_mix;
  const sorted = Object.entries(pm).sort((a,b)=>b[1].pct-a[1].pct);
  const labels = sorted.map(([fc])=>fc);
  const colors = labels.map(l=>FC_COLORS[l]||'#999');

  makeChart(hid+'-pm-pie', {
    type:'doughnut',
    data:{labels,datasets:[{data:sorted.map(([,v])=>v.los),backgroundColor:colors,borderWidth:2,borderColor:'#fff'}]},
    options:{responsive:true,maintainAspectRatio:true,plugins:{legend:{position:'bottom',labels:{font:{size:10},boxWidth:10}}}}
  });

  makeChart(hid+'-pm-rpd', {
    type:'bar',
    data:{labels,datasets:[{label:'Rev/Patient Day',data:sorted.map(([,v])=>v.rev_per_day),backgroundColor:colors}]},
    options:{
      responsive:true,maintainAspectRatio:true,indexAxis:'y',
      plugins:{legend:{display:false}},
      scales:{x:{ticks:{callback:v=>fmtDollar(v)}}}
    }
  });
}

// ===== TOP 5 GROSS (Program Type filter) =====
function buildRollingGrossSection(hid) {
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  const filter = getFilter(hid, 'rollingGross');
  const hosp = aggregateRecords(filterRecords(hid, {programType: filter.programType}));
  const container = document.getElementById(hid+'-rolling-gross');
  injectFilterBar(container, hid, 'rollingGross', h.color, false);
  buildRollingGross(hid, hosp);
}

function buildRollingGross(hid, hosp) {
  const t5 = hosp.top5_gross;
  const payors = hosp.top5_gross_payors;
  const datasets = payors.map((p,i)=>{
    const c = CHART_PALETTE[i%CHART_PALETTE.length];
    return {label:p,data:QUARTERS.map(q=>t5[p].qtr_los[q]||0),borderColor:c,backgroundColor:c+'44',tension:.3,fill:false,pointRadius:5};
  });
  makeChart(hid+'-gross-chart', {
    type:'line',
    data:{labels:QUARTERS,datasets},
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:'top'}},
      scales:{y:{title:{display:true,text:'Patient Days (LOS)'},ticks:{callback:v=>fmtN(v)}}}
    }
  });
  const tbody = document.querySelector(`#${hid}-gross-table tbody`);
  tbody.innerHTML = payors.map((p,i)=>{
    const c = CHART_PALETTE[i%CHART_PALETTE.length];
    const qtds = QUARTERS.map(q=>`<td>${fmtN(t5[p].qtr_los[q]||0)}</td>`).join('');
    return `<tr><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${c};margin-right:6px"></span>${p}</td>${qtds}<td><strong>${fmtDollar(t5[p].total_gross)}</strong></td></tr>`;
  }).join('');
}

// ===== TOP 5 NET (Program Type filter) =====
function buildRollingNetSection(hid) {
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  const filter = getFilter(hid, 'rollingNet');
  const hosp = aggregateRecords(filterRecords(hid, {programType: filter.programType}));
  const container = document.getElementById(hid+'-rolling-net');
  injectFilterBar(container, hid, 'rollingNet', h.color, false);
  buildRollingNet(hid, hosp);
}

function buildRollingNet(hid, hosp) {
  const t5 = hosp.top5_net;
  const payors = hosp.top5_net_payors;
  const datasets = payors.map((p,i)=>{
    const c = CHART_PALETTE[i%CHART_PALETTE.length];
    return {label:p,data:QUARTERS.map(q=>t5[p].qtr_los[q]||0),borderColor:c,backgroundColor:c+'44',tension:.3,fill:false,pointRadius:5};
  });
  makeChart(hid+'-net-chart', {
    type:'line',
    data:{labels:QUARTERS,datasets},
    options:{
      responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:'top'}},
      scales:{y:{title:{display:true,text:'Patient Days (LOS)'},ticks:{callback:v=>fmtN(v)}}}
    }
  });
  const tbody = document.querySelector(`#${hid}-net-table tbody`);
  tbody.innerHTML = payors.map((p,i)=>{
    const c = CHART_PALETTE[i%CHART_PALETTE.length];
    const qtds = QUARTERS.map(q=>`<td>${fmtN(t5[p].qtr_los[q]||0)}</td>`).join('');
    return `<tr><td><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${c};margin-right:6px"></span>${p}</td>${qtds}<td><strong>${fmtDollar(t5[p].total_net)}</strong></td></tr>`;
  }).join('');
}

// ===== DENIALS (Program Type filter; data is always 1Q26 YTD) =====
function buildDenialsSection(hid) {
  const h = HOSPITALS_CFG.find(x=>x.id===hid);
  const filter = getFilter(hid, 'denials');
  const hosp = aggregateRecords(filterRecords(hid, {programType: filter.programType}));
  const container = document.getElementById(hid+'-denials');
  injectFilterBar(container, hid, 'denials', h.color, false);
  buildDenials(hid, hosp);
}

function buildDenials(hid, hosp) {
  const dr = hosp.denial_rate;
  const payors = Object.keys(dr).filter(p=>dr[p].gross>0).sort((a,b)=>dr[b].rate-dr[a].rate);
  const rates = payors.map(p=>dr[p].rate);
  const bgColors = rates.map(r=>r>5?'#dc3545':r>1?'#ff9800':'#2e7d32');

  makeChart(hid+'-denial-chart', {
    type:'bar',
    data:{labels:payors,datasets:[{label:'Denial Rate %',data:rates,backgroundColor:bgColors,borderRadius:4}]},
    options:{
      responsive:true,maintainAspectRatio:false,indexAxis:'y',
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>` Denial Rate: ${ctx.raw.toFixed(2)}%`}}},
      scales:{x:{title:{display:true,text:'Denial Rate (%)'},ticks:{callback:v=>v+'%'}}}
    }
  });

  const tbody = document.querySelector(`#${hid}-denial-table tbody`);
  const totalGross = payors.reduce((s,p)=>s+dr[p].gross,0);
  const totalDenial = payors.reduce((s,p)=>s+dr[p].denial_adj,0);
  const overallRate = totalGross ? (totalDenial/totalGross*100) : 0;
  if (payors.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#999;padding:24px">No 1Q26 YTD records for this Program Type.</td></tr>`;
    return;
  }
  tbody.innerHTML = payors.map(p=>{
    const v = dr[p];
    const rateClass = v.rate>5?'denial-rate-high':v.rate>0?'':'denial-rate-low';
    return `<tr>
      <td>${p}</td>
      <td>${fmtDollar(v.gross)}</td>
      <td>${fmtDollar(v.net)}</td>
      <td>${fmtDollar(v.denial_adj)}</td>
      <td class="${rateClass}">${v.rate.toFixed(2)}%</td>
      <td>${fmtN(v.los)}</td>
    </tr>`;
  }).join('');
  tbody.innerHTML += `<tr style="font-weight:700;background:#f8f9fa">
    <td>TOTAL</td><td>${fmtDollar(totalGross)}</td><td>—</td><td>${fmtDollar(totalDenial)}</td>
    <td class="${overallRate>5?'denial-rate-high':''}">${overallRate.toFixed(2)}%</td><td>—</td>
  </tr>`;
}
