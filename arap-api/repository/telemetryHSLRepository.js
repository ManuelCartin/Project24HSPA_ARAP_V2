const TelemetryHSL = require('../models/TelemetryHSL');

function findBySessionIdOrderByTimestampAsc(sessionId) {
  return TelemetryHSL.find({ sessionId })
    .sort({ timestamp: 1 })
    .lean();
}

module.exports = {
  findBySessionIdOrderByTimestampAsc
};