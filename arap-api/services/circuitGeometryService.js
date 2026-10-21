const { createSectorLengthDTO } =
  require('../dto/sectorLengthDTO');

const circuitGeometryRepository = require('../repositories/circuitGeometryRepository');

const EARTH_RADIUS_METERS = 6371000;

async function getCircuitByName(circuitName) {
  if (!circuitName || !circuitName.trim()) {
    throw new Error('El nombre del circuito es obligatorio');
  }

  return circuitGeometryRepository.findByName(
    circuitName.trim()
  );
}

async function getSectorLength(circuitName, sectorName) {
  if (!sectorName || !sectorName.trim()) {
    throw new Error('El nombre del sector es obligatorio');
  }

  const circuit = await getCircuitByName(circuitName);

  if (!circuit || !Array.isArray(circuit.features)) {
    return null;
  }

  const feature = circuit.features.find((item) => {
    const name = item?.properties?.name;

    return typeof name === 'string' &&
      name.toLowerCase() === sectorName.trim().toLowerCase();
  });

  if (!feature || feature.geometry?.type !== 'LineString') {
    return null;
  }

  const coordinates = feature.geometry.coordinates;

  if (!Array.isArray(coordinates) || coordinates.length < 2) {
    return null;
  }

  const meters = calculateLineStringLength(coordinates);

  return createSectorLengthDTO(
  circuitName,
  sectorName,
  meters
);
}

function calculateLineStringLength(coordinates) {
  let totalDistance = 0;

  for (let i = 0; i < coordinates.length - 1; i++) {
    const [lon1, lat1] = coordinates[i];
    const [lon2, lat2] = coordinates[i + 1];

    totalDistance += haversine(lat1, lon1, lat2, lon2);
  }

  return totalDistance;
}

function haversine(lat1, lon1, lat2, lon2) {
  const toRadians = (degrees) => degrees * Math.PI / 180;

  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) *
    Math.cos(toRadians(lat2)) *
    Math.sin(dLon / 2) ** 2;

  const c = 2 * Math.atan2(
    Math.sqrt(a),
    Math.sqrt(1 - a)
  );

  return EARTH_RADIUS_METERS * c;
}

module.exports = {
  getCircuitByName,
  getSectorLength
};
