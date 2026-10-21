
function createSectorLengthDTO(circuitName, sectorName, lengthMeters) {
  return {
    circuitName,
    sectorName,
    lengthMeters,
    lengthKm: lengthMeters / 1000
  };
}

module.exports = { createSectorLengthDTO };
