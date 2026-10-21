const express = require('express');
const router = express.Router();

const circuitController = require('../controllers/circuitController');

router.get('/spa-geometry', circuitController.getSpaGeometry);

module.exports = router;
