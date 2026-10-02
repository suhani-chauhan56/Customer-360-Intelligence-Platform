const express = require('express');
const router = express.Router();
const analyticsController = require('../controllers/analyticsController');

router.get('/explorer', analyticsController.getAnalyticsExplorer);
router.get('/export', analyticsController.exportCohortCsv);

module.exports = router;
