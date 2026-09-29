const express = require('express');
const router = express.Router();
const sentimentController = require('../controllers/sentimentController');

router.get('/', sentimentController.getSentimentOverview);
router.get('/reviews', sentimentController.searchReviews);

module.exports = router;
