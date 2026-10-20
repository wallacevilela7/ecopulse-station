// ==============================================================
// EcoPulse Urbano - Dashboard Controller
// ==============================================================

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000'
  : ''; // Usa proxy relativo em produção

const POLLING_INTERVAL_MS = 15000; // Atualiza a cada 15 segundos

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initCharts();
  initMap();

  // Botão de Geolocalização
  const geoBtn = document.getElementById('btn-geolocation');
  if (geoBtn) {
    geoBtn.addEventListener('click', () => handleUserLocation(API_BASE_URL));
  }

  // Primeiro ciclo de busca e agendamento de polling
  fetchDashboardData();
  setInterval(fetchDashboardData, POLLING_INTERVAL_MS);
});

// Theme Toggle (Dark / Light)
function initThemeToggle() {
  const themeBtn = document.getElementById('theme-btn');
  const savedTheme = localStorage.getItem('theme') || 'dark';

  document.documentElement.setAttribute('data-theme', savedTheme);
  themeBtn.textContent = savedTheme === 'dark' ? '🌙' : '☀️';

  themeBtn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    themeBtn.textContent = next === 'dark' ? '🌙' : '☀️';
  });
}

// Ingestão e Atualização dos Indicadores
async function fetchDashboardData() {
  const connDot = document.querySelector('.status-dot');
  const connText = document.getElementById('conn-text');
  const lastUpdate = document.getElementById('last-update');

  try {
    // 1. Busca medição mais recente
    const resLatest = await fetch(`${API_BASE_URL}/api/v1/telemetry/latest`);
    if (resLatest.ok) {
      const data = await resLatest.json();
      updateMetricCards(data);

      connDot.classList.add('online');
      connText.textContent = `Online (${data.estacao_id})`;
      const now = new Date();
      lastUpdate.textContent = `Última sincronização: ${now.toLocaleTimeString()}`;
    } else {
      throw new Error(`HTTP ${resLatest.status}`);
    }

    // 2. Busca histórico das últimas 24h para os gráficos
    const resHistory = await fetch(`${API_BASE_URL}/api/v1/telemetry/history?hours=24&limit=100`);
    if (resHistory.ok) {
      const history = await resHistory.json();
      updateChartsData(history);
    }

    // 3. Busca alertas ativos de defesa civil
    const resAlerts = await fetch(`${API_BASE_URL}/api/v1/alerts/active`);
    if (resAlerts.ok) {
      const alerts = await resAlerts.json();
      renderAlerts(alerts);
    }

  } catch (err) {
    console.warn("Falha na sincronização:", err.message);
    connDot.classList.remove('online');
    connText.textContent = "Aguardando telemetria...";
  }
}

function updateMetricCards(data) {
  // Temperatura e Sensação
  document.getElementById('val-temp').textContent = Number(data.temperatura).toFixed(1);
  document.getElementById('val-heat-index').textContent = Number(data.sensacao_termica || data.temperatura).toFixed(1);

  // Umidade
  document.getElementById('val-humidity').textContent = Number(data.umidade).toFixed(1);

  // Ponto de Orvalho aproximado
  const t = Number(data.temperatura);
  const rh = Number(data.umidade);
  const dp = t - ((100 - rh) / 5);
  document.getElementById('val-dew-point').textContent = dp.toFixed(1);

  // Pressão e Altitude
  document.getElementById('val-pressure').textContent = Number(data.pressao).toFixed(1);
  document.getElementById('val-altitude').textContent = data.altitude_m ? Number(data.altitude_m).toFixed(0) : '760';

  // Qualidade do Ar (AQI)
  document.getElementById('val-aqi').textContent = Number(data.qualidade_ar).toFixed(0);
  const aqiBadge = document.getElementById('val-aqi-class');
  const aqiClass = data.aqi_classificacao || 'Moderada';
  aqiBadge.textContent = aqiClass;
  applyAqiBadgeColor(aqiBadge, aqiClass);

  // Luminosidade
  const lightPct = Number(data.luminosidade);
  document.getElementById('val-light').textContent = lightPct.toFixed(0);
  const lightStatus = document.getElementById('val-light-status');
  if (lightPct > 70) lightStatus.textContent = "Sol Pleno";
  else if (lightPct > 30) lightStatus.textContent = "Nublado / Difusa";
  else lightStatus.textContent = "Noite / Escuro";

  // Chuva
  const rainPct = Number(data.chuva_intensidade);
  document.getElementById('val-rain').textContent = rainPct.toFixed(0);
  const rainStatus = document.getElementById('val-rain-status');
  if (data.chuva_detectada || rainPct > 15) {
    rainStatus.textContent = `Chovendo (${rainPct.toFixed(0)}%)`;
    rainStatus.style.color = '#38bdf8';
  } else {
    rainStatus.textContent = "Sem Chuva";
    rainStatus.style.color = 'inherit';
  }
}

function applyAqiBadgeColor(element, classification) {
  switch (classification) {
    case 'Boa':
      element.style.background = 'rgba(16, 185, 129, 0.2)';
      element.style.color = '#34d399';
      break;
    case 'Moderada':
      element.style.background = 'rgba(234, 179, 8, 0.2)';
      element.style.color = '#fde047';
      break;
    case 'Inadequada':
      element.style.background = 'rgba(249, 115, 22, 0.2)';
      element.style.color = '#fb923c';
      break;
    case 'Má':
    case 'Muito Má':
    case 'Crítica':
      element.style.background = 'rgba(239, 68, 68, 0.2)';
      element.style.color = '#f87171';
      break;
    default:
      element.style.background = 'rgba(148, 163, 184, 0.2)';
      element.style.color = '#cbd5e1';
  }
}

function renderAlerts(alerts) {
  const container = document.getElementById('alerts-container');
  if (!alerts || alerts.length === 0) {
    container.innerHTML = '';
    return;
  }

  container.innerHTML = alerts.map(alert => `
    <div class="alert-banner ${alert.severidade === 'ATENCAO' ? 'warning' : ''}">
      <div class="alert-icon">⚠️</div>
      <div class="alert-content">
        <h4>[${alert.severidade}] ${alert.tipo_evento.replace(/_/g, ' ')}</h4>
        <p>${alert.mensagem} &bull; <em>Recomendação: ${alert.recomendacao_cidadao}</em></p>
      </div>
    </div>
  `).join('');
}
