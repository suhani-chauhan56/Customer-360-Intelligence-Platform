const express = require('express');
const router = express.Router();

const dashboardRoutes = require('./dashboardRoutes');
const customerRoutes = require('./customerRoutes');
const rfmRoutes = require('./rfmRoutes');
const clvRoutes = require('./clvRoutes');
const churnRoutes = require('./churnRoutes');
const sentimentRoutes = require('./sentimentRoutes');
const recommendationRoutes = require('./recommendationRoutes');
const analyticsRoutes = require('./analyticsRoutes');
const dataQualityRoutes = require('./dataQualityRoutes');
const groundedAiRoutes = require('./groundedAiRoutes');

router.use('/dashboard', dashboardRoutes);
router.use('/customers', customerRoutes);
router.use('/rfm', rfmRoutes);
router.use('/clv', clvRoutes);
router.use('/churn', churnRoutes);
router.use('/sentiment', sentimentRoutes);
router.use('/recommendations', recommendationRoutes);
router.use('/analytics', analyticsRoutes);
router.use('/data-quality', dataQualityRoutes);
router.use('/grounded-ai', groundedAiRoutes);

router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'CustomerAtlas AI Backend REST API Engine',
    version: '2.0.0-prod',
  });
});

module.exports = router;
