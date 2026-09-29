const express = require('express');
const router = express.Router();
const dataQualityController = require('../controllers/dataQualityController');

router.get('/', dataQualityController.getDataQualityOverview);
router.post('/audit', dataQualityController.recordAudit);

module.exports = router;
