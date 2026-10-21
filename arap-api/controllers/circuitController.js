const circuitGeometryRepository =
  require('../repositories/circuitGeometryRepository');

async function getSpaGeometry(req, res, next) {
  try {
    const circuit =
      await circuitGeometryRepository.findByName(
        'Circuit of Spa-Francorchamps'
      );

    if (!circuit) {
      return res.status(404).json({
        error: 'No se encontró la geometría en la base de datos'
      });
    }

    const { _id, ...geometry } = circuit;

    return res.status(200).json(geometry);
  } catch (error) {
    next(error);
  }
}

module.exports = { getSpaGeometry };