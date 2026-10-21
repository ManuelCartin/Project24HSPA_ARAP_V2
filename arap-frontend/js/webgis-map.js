let map;
let geoJsonLayer;

function initMap() {
    // Coordenadas iniciales centradas en Spa-Francorchamps
    map = L.map('map').setView([50.4372, 5.9714], 14);

    L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
            attribution: 'Tiles &copy; Esri',
            maxZoom: 18
        }
    ).addTo(map);

    loadSpaGeometry();
}

async function loadSpaGeometry() {
    try {
        const response = await fetch(
        'http://localhost:3000/api/v1/circuit/spa-geometry'
        );

        if (!response.ok) {
        throw new Error('Error al consultar la API de ARAP');
        }
        
        const geojson = await response.json();
        
        if (geoJsonLayer) map.removeLayer(geoJsonLayer);

        geoJsonLayer = L.geoJSON(geojson, {
            // 1. Estilos dinámicos para los sectores (LineString)
            style: (feature) => {
                const sectorName = feature.properties?.name;
                switch (sectorName) {
                    case 'Sector 1':
                        return { color: '#ef4444', weight: 4, opacity: 0.9 }; // Red GT3
                    case 'Sector 2':
                        return { color: '#10b981', weight: 4, opacity: 0.9 }; // Emerald
                    case 'Sector 3':
                        return { color: '#3b82f6', weight: 4, opacity: 0.9 }; // Blue
                    default:
                        return { color: '#f59e0b', weight: 3, opacity: 0.8 }; // Amber
                }
            },

            // 2. Renderizado de curvas e hitos clave (Point)
            pointToLayer: (feature, latlng) => {
                return L.circleMarker(latlng, {
                    radius: 4,
                    fillColor: '#f59e0b', // Ámbar
                    color: '#020617',     // Slate-950
                    weight: 1.5,
                    opacity: 1,
                    fillOpacity: 0.9
                });
            },

            // 3. Popups interactivos estilizados
            onEachFeature: (feature, layer) => {
    if (feature.properties && feature.properties.name) {
        const coordinates = feature.geometry?.coordinates;

        let altitudeValue;

        if (feature.geometry?.type === 'Point') {
            altitudeValue = coordinates?.[2];
        } else if (feature.geometry?.type === 'LineString') {
            altitudeValue = coordinates?.[0]?.[2];
        }

                const altitude =
                    typeof altitudeValue === 'number' && altitudeValue > 0
                        ? `<br><span class="text-xs text-slate-400 font-mono">
                            Altitud: ${altitudeValue.toFixed(1)} m
                        </span>`
                        : '';

                layer.bindPopup(`
                    <div class="font-sans text-slate-100 p-1">
                        <strong class="text-sm font-bold text-slate-200">${feature.properties.name}</strong>
                        ${altitude}
                    </div>
                `);
            }
        }
        }).addTo(map);

        // Ajustar el zoom automáticamente al encuadre del circuito
        map.fitBounds(geoJsonLayer.getBounds(), { padding: [15, 15] });

    } catch (err) {
        console.warn('Cargando geometría estática de respaldo para Spa-Francorchamps:', err.message);
    }
}

document.addEventListener('DOMContentLoaded', initMap);