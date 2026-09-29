const express = require('express');
const router = express.Router();
const recommendationController = require('../controllers/recommendationController');

router.get('/', recommendationController.getRecommendationsOverview);
router.get('/customer/:customerId', recommendationController.getCustomerNextBestCategory);

module.exports = router;
