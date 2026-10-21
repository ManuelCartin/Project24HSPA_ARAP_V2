const express = require('express');
const router = express.Router();

const telemetryController = require('../controllers/telemetryController');

router.get('/gt3/:sessionId', telemetryController.getStintData);

module.exports = router;
