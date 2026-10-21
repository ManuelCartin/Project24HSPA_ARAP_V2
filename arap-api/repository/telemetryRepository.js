
const TelemetryGT3 = require('../models/TelemetryGT3');

function findBySessionIdOrderByTimestampAsc(sessionId) {
  return TelemetryGT3.find({ sessionId })
    .sort({ timestamp: 1 })
    .lean();
}

module.exports = {
  findBySessionIdOrderByTimestampAsc
};


async function getStintSummaryBySessionId(sessionId) {
  const results = await TelemetryGT3.aggregate([
    {
      $match: { sessionId }
    },
    {
      $group: {
        _id: '$sessionId',
        avgSpeedKmh: { $avg: '$speed_kmh' },
        topSpeedKmh: { $max: '$speed_kmh' },
        bestLapTime: { $min: '$lap_time_seconds' },
        avgLapTime: { $avg: '$lap_time_seconds' },
        totalLapsCompleted: { $max: '$lap_number' }
      }
    },
    {
      $project: {
        _id: 0,
        sessionId: '$_id',
        avgSpeedKmh: 1,
        topSpeedKmh: 1,
        bestLapTime: 1,
        avgLapTime: 1,
        totalLapsCompleted: 1
      }
    }
  ]);

  return results[0] ?? null;
}
