
const mongoose = require('mongoose');

const telemetryGT3Schema = new mongoose.Schema(
  {
    sessionId: {
      type: String,
      required: true,
      index: true
    },

    timestamp: {
      type: Date,
      required: true
    },

    speed_kmh: {
      type: Number,
      min: 0
    },

    engine_rpm: {
      type: Number,
      min: 0,
      validate: Number.isInteger
    },

    gear: {
      type: Number,
      validate: Number.isInteger
    },

    fuel_level_liters: {
      type: Number,
      min: 0
    },

    lap_number: {
      type: Number,
      min: 0,
      validate: Number.isInteger
    },

    lap_time_seconds: {
      type: Number,
      min: 0
    }
  },
  {
    collection: 'Telemetry_Audi_GT3',
    versionKey: false
  }
);

module.exports = mongoose.model(
  'TelemetryGT3',
  telemetryGT3Schema
);
