const express = require('express');
const router = express.Router();
const rfmController = require('../controllers/rfmController');

router.get('/', rfmController.getRfmOverview);
router.get('/compare', rfmController.compareSegments);
router.post('/cohort', rfmController.buildCohort);
router.get('/:segment', rfmController.getSegmentDetails);

module.exports = router;
