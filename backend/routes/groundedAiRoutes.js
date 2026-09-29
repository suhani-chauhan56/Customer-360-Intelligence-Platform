const express = require('express');
const router = express.Router();
const groundedAiController = require('../controllers/groundedAiController');

router.post('/ask', groundedAiController.askGroundedQuestion);

module.exports = router;
