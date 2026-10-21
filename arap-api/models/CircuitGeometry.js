
const mongoose = require('mongoose');

const circuitGeometrySchema = new mongoose.Schema(
  {
    type: {
      type: String,
      required: true
    },

    name: {
      type: String,
      required: true
    },

    // Conserva los objetos GeoJSON originales.
    features: {
      type: [mongoose.Schema.Types.Mixed],
      default: []
    }
  },
  {
    collection: 'CircuitGeometry',
    versionKey: false
  }
);

module.exports = mongoose.model(
  'CircuitGeometry',
  circuitGeometrySchema
);
