
const mongoose = require('mongoose');

const telemetryHSLSchema = new mongoose.Schema(
  {
    timestamp: { type: Date, required: true },
    sessionId: { type: String, required: true, index: true },

    BRAKE_TORQUE_LF: Number,
    BRAKE_TORQUE_RF: Number,
    BRAKE_TORQUE_LR: Number,
    BRAKE_TORQUE_RR: Number,

    BRAKE_TEMP_LF: Number,
    BRAKE_TEMP_RF: Number,
    BRAKE_TEMP_LR: Number,
    BRAKE_TEMP_RR: Number,

    TYRE_PRESS_LF: Number,
    TYRE_PRESS_RF: Number,
    TYRE_PRESS_LR: Number,
    TYRE_PRESS_RR: Number,

    TYRE_TAIR_LF: Number,
    TYRE_TAIR_RF: Number,
    TYRE_TAIR_LR: Number,
    TYRE_TAIR_RR: Number,

    C_SURF_TEMP_LF: Number,
    C_SURF_TEMP_RF: Number,
    C_SURF_TEMP_LR: Number,
    C_SURF_TEMP_RR: Number,

    L_SURF_TEMP_LF: Number,
    L_SURF_TEMP_RF: Number,
    L_SURF_TEMP_LR: Number,
    L_SURF_TEMP_RR: Number,

    R_SURF_TEMP_LF: Number,
    R_SURF_TEMP_RF: Number,
    R_SURF_TEMP_LR: Number,
    R_SURF_TEMP_RR: Number,

    SUS_TRAVEL_LF: Number,
    SUS_TRAVEL_RF: Number,
    SUS_TRAVEL_LR: Number,
    SUS_TRAVEL_RR: Number,

    BUMPSTOPUP_TRAVEL_LF: Number,
    BUMPSTOPUP_TRAVEL_RF: Number,
    BUMPSTOPUP_TRAVEL_LR: Number,
    BUMPSTOPUP_TRAVEL_RR: Number,

    WHEEL_SR_LF: Number,
    WHEEL_SR_RF: Number,
    WHEEL_SR_LR: Number,
    WHEEL_SR_RR: Number,

    AIR_TEMP: Number,
    ROAD_TEMP: Number
  },
  {
    collection: 'Telemetry_Audi_GT3_HSL',
    versionKey: false
  }
);

module.exports = mongoose.model('TelemetryHSL', telemetryHSLSchema);
