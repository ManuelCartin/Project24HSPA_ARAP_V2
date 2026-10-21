
const telemetryRepository = require('../repositories/telemetryRepository');

async function getStintSummary(sessionId) {
  if (!sessionId || !sessionId.trim()) {
    throw new Error('sessionId es obligatorio');
  }

  return telemetryRepository.getStintSummaryBySessionId(
    sessionId.trim()
  );
}

module.exports = {
  getStintSummary
};
