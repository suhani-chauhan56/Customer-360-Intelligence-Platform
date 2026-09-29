const express = require('express');
const router = express.Router();
const churnController = require('../controllers/churnController');

router.get('/', churnController.getChurnOverview);
router.post('/simulate', churnController.simulateChurnScenario);

module.exports = router;
