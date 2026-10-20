let leafletMap = null;
let stationMarker = null;
let coverageCircle = null;
let userMarker = null;

const DEFAULT_STATION = {
  lat: -23.550520,
  lon: -46.633308,
  radiusKm: 5.0,
  name: "Estação Piloto UNIP - Smart Cities"
};

function initMap(stationLat = DEFAULT_STATION.lat, stationLon = DEFAULT_STATION.lon, radiusKm = DEFAULT_STATION.radiusKm) {
  leafletMap = L.map('map').setView([stationLat, stationLon], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(leafletMap);

  // Marcador da Estação
  stationMarker = L.marker([stationLat, stationLon])
    .addTo(leafletMap)
    .bindPopup(`<b>${DEFAULT_STATION.name}</b><br>Monitoramento Ativo`)
    .openPopup();

  // Círculo Analítico da Cobertura (Geometria Analítica: (x-x0)^2 + (y-y0)^2 <= r^2)
  coverageCircle = L.circle([stationLat, stationLon], {
    color: '#3b82f6',
    fillColor: '#3b82f6',
    fillOpacity: 0.15,
    radius: radiusKm * 1000 // metros
  }).addTo(leafletMap);
}

function handleUserLocation(apiBaseUrl) {
  const btn = document.getElementById('btn-geolocation');
  const resultBox = document.getElementById('geo-result');

  if (!navigator.geolocation) {
    alert("Geolocalização não suportada pelo seu navegador.");
    return;
  }

  btn.textContent = "Obtendo GPS...";
  btn.disabled = true;

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const userLat = position.coords.latitude;
      const userLon = position.coords.longitude;

      if (userMarker) {
        leafletMap.removeLayer(userMarker);
      }

      userMarker = L.marker([userLat, userLon], {
        icon: L.icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41]
        })
      }).addTo(leafletMap).bindPopup("<b>Sua Localização</b>").openPopup();

      // Ajusta zoom para englobar usuário e estação
      const group = new L.featureGroup([stationMarker, userMarker, coverageCircle]);
      leafletMap.fitBounds(group.getBounds().pad(0.1));

      // Consulta a API de Geometria Analítica
      try {
        const res = await fetch(`${apiBaseUrl}/api/v1/analysis/geometry?user_lat=${userLat}&user_lon=${userLon}`);
        if (res.ok) {
          const data = await res.json();
          resultBox.style.display = "block";
          resultBox.innerHTML = `
            <strong>📍 Análise Geoanalítica Concluída:</strong><br>
            ${data.mensagem}
          `;
        }
      } catch (err) {
        console.error("Erro ao consultar geometria:", err);
      } finally {
        btn.textContent = "📍 Minha Localização";
        btn.disabled = false;
      }
    },
    (err) => {
      alert("Não foi possível obter sua localização: " + err.message);
      btn.textContent = "📍 Minha Localização";
      btn.disabled = false;
    }
  );
}
