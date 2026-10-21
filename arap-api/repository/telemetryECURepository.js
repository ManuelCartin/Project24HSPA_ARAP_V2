
const TelemetryECU = require('../models/TelemetryECU');

function findBySessionIdOrderByTimestampAsc(sessionId) {
  return TelemetryECU.find({ sessionId })
    .sort({ timestamp: 1 })
    .lean();
}

module.exports = {
  findBySessionIdOrderByTimestampAsc
};
