let tempChart = null;
let pressureChart = null;

function initCharts() {
  const ctxTemp = document.getElementById('tempChart').getContext('2d');
  const ctxPressure = document.getElementById('pressureChart').getContext('2d');

  tempChart = new Chart(ctxTemp, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Temperatura (°C)',
          data: [],
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          fill: true,
          tension: 0.35,
          pointRadius: 2
        },
        {
          label: 'Sensação Térmica (°C)',
          data: [],
          borderColor: '#f59e0b',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          tension: 0.35,
          pointRadius: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } } }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } }
      }
    }
  });

  pressureChart = new Chart(ctxPressure, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Pressão (hPa)',
          data: [],
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          yAxisID: 'y',
          tension: 0.35,
          pointRadius: 2
        },
        {
          label: 'Chuva (%)',
          data: [],
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.2)',
          yAxisID: 'y1',
          type: 'bar'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } } }
      },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
        y: {
          type: 'linear',
          position: 'left',
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#3b82f6' }
        },
        y1: {
          type: 'linear',
          position: 'right',
          grid: { drawOnChartArea: false },
          ticks: { color: '#06b6d4' },
          min: 0,
          max: 100
        }
      }
    }
  });
}

function updateChartsData(history) {
  if (!tempChart || !pressureChart || !history.length) return;

  const labels = history.map(item => {
    const d = new Date(item.data_hora);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
  });

  const temps = history.map(item => item.temperatura);
  const heatIndexes = history.map(item => item.sensacao_termica || item.temperatura);
  const pressures = history.map(item => item.pressao);
  const rainIntensities = history.map(item => item.chuva_intensidade);

  tempChart.data.labels = labels;
  tempChart.data.datasets[0].data = temps;
  tempChart.data.datasets[1].data = heatIndexes;
  tempChart.update();

  pressureChart.data.labels = labels;
  pressureChart.data.datasets[0].data = pressures;
  pressureChart.data.datasets[1].data = rainIntensities;
  pressureChart.update();
}
