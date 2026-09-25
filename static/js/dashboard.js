// Column order and label for every KPI shown in the route table, the one
// place to edit when a new KPI needs to appear on screen.
const TABLE_COLUMNS = [
  { key: "route_code", label: "Ma Route" },
  { key: "route_name", label: "Ten Route" },
  { key: "vol_target", label: "Vol Target" },
  { key: "volume_actual", label: "Volume Actual" },
  { key: "aso_coverage", label: "ASO Coverage" },
  { key: "aso_photographed", label: "ASO Photographed" },
  { key: "aso_not_photographed", label: "ASO Not Photographed" },
  { key: "spvb_shop_target", label: "SPVB Shop Target" },
  { key: "spvb_shop_installed", label: "SPVB Shop Installed" },
];

async function loadMonths() {
  // Fills the month dropdown from the API and triggers the first render.
  const res = await fetch("/api/months");
  const data = await res.json();
  const sel = document.getElementById("sel-month");
  sel.innerHTML = "";
  data.months.forEach((m) => {
    const opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    sel.appendChild(opt);
  });
  sel.addEventListener("change", () => loadDashboard(sel.value));
  if (data.months.length > 0) {
    loadDashboard(data.months[0]);
  } else {
    document.getElementById("main").innerHTML = '<div class="loading">Chưa có dữ liệu, hãy upload báo cáo trong trang Admin.</div>';
  }
}

function sumColumn(routes, key) {
  // Adds up one KPI column across every route, used for the summary cards.
  return routes.reduce((total, r) => total + (r[key] || 0), 0);
}

function formatNumber(n) {
  // Renders a number the Vietnamese way, with dot as the thousands separator.
  return Math.round(n).toLocaleString("vi-VN");
}

async function loadDashboard(month) {
  // Fetches the KPI rows for the selected month and renders the summary
  // cards and the route level table.
  const res = await fetch("/api/dashboard?month=" + encodeURIComponent(month));
  const data = await res.json();
  const routes = data.routes;

  let html = '<div class="kpi-row">';
  html += kpiCard("Vol Target", sumColumn(routes, "vol_target"));
  html += kpiCard("Volume Actual", sumColumn(routes, "volume_actual"));
  html += kpiCard("ASO Coverage", sumColumn(routes, "aso_coverage"));
  html += kpiCard("ASO Not Photographed", sumColumn(routes, "aso_not_photographed"));
  html += kpiCard("SPVB Shop Installed", sumColumn(routes, "spvb_shop_installed"));
  html += "</div>";

  html += '<div class="section-table"><table><thead><tr>';
  TABLE_COLUMNS.forEach((c) => (html += "<th>" + c.label + "</th>"));
  html += "</tr></thead><tbody>";
  routes.forEach((r) => {
    html += "<tr>";
    TABLE_COLUMNS.forEach((c) => {
      const v = r[c.key];
      const cell = typeof v === "number" ? formatNumber(v) : v || "-";
      html += "<td>" + cell + "</td>";
    });
    html += "</tr>";
  });
  html += "</tbody></table></div>";

  document.getElementById("main").innerHTML = html;
}

function kpiCard(label, value) {
  // Builds the HTML for one summary card at the top of the dashboard.
  return (
    '<div class="kpi-card"><div class="lbl">' +
    label +
    '</div><div class="val">' +
    formatNumber(value) +
    "</div></div>"
  );
}

loadMonths();
