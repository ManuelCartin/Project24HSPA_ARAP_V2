const telemetryRepository = require('../repositories/telemetryRepository');

async function getStintData(req, res, next) {
  try {
    const { sessionId } = req.params;

    const data =
      await telemetryRepository.findBySessionIdOrderByTimestampAsc(
        sessionId
      );

    if (data.length === 0) {
      return res.status(404).json({
        message: 'No se encontró telemetría para esta sesión'
      });
    }

    return res.status(200).json(data);
  } catch (error) {
    next(error);
  }
}

module.exports = {
  getStintData
};
