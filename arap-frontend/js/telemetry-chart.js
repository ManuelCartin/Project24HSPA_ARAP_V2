
async function fetchTelemetryData() {
  try {
    const sessionId = 'SESSION_SPA_01';

    const response = await fetch(
      `http://localhost:3000/api/v1/telemetry/gt3/${sessionId}`
    );

    if (!response.ok) {
      throw new Error(
        `Error al consultar la telemetría: HTTP ${response.status}`
      );
    }

    const data = await response.json();

    if (!Array.isArray(data) || data.length === 0) {
      throw new Error('La sesión no contiene muestras de telemetría');
    }

    telemetryChart.data.labels = data.map(d =>
      new Date(d.timestamp).toLocaleTimeString()
    );

    telemetryChart.data.datasets[0].data = data.map(d =>
      d.speedKmh ?? d.speed_kmh
    );

    telemetryChart.update();
  } catch (err) {
    console.error('No se pudo actualizar la telemetría:', err.message);
  }
}
