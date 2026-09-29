const express = require('express');
const router = express.Router();
const clvController = require('../controllers/clvController');

router.get('/', clvController.getClvOverview);
router.post('/simulate', clvController.simulateClvScenario);

module.exports = router;
