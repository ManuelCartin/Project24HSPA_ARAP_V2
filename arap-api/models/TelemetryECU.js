
const mongoose = require('mongoose');

const telemetryECUSchema = new mongoose.Schema(
  {
    timestamp: { type: Date, required: true },
    sessionId: { type: String, required: true, index: true },

    SPEED: Number,
    RPMS: Number,
    FUEL: Number,
    GEAR: Number,
    THROTTLE: Number,
    BRAKE: Number,
    CLUTCH: Number,
    STEERANGLE: Number,
    TC: Number,
    ABS: Number,

    G_LAT: Number,
    G_LON: Number,
    ROTY: Number,

    WHEEL_SPEED_LF: Number,
    WHEEL_SPEED_RF: Number,
    WHEEL_SPEED_LR: Number,
    WHEEL_SPEED_RR: Number,

    AERO_HEIGHT0: Number,
    AERO_HEIGHT1: Number,
    AERO_HEIGHT2: Number,
    AERO_HEIGHT3: Number,
    AERO_BALANCE: Number,
    LSD_LOCKING_TORQUE: Number,
    LAP_BEACON: Number
  },
  {
    collection: 'Telemetry_Audi_GT3_ECU',
    versionKey: false
  }
);

module.exports = mongoose.model('TelemetryECU', telemetryECUSchema);
