import express from 'express';
import { getOverview } from '../controllers/overviewController.js';
import { getCustomersList, getCustomerDetails, getCustomerOrders } from '../controllers/customerController.js';
import { getSegmentsOverview, compareSegments } from '../controllers/segmentController.js';
import { getChurnOverview, handleChurnSimulation } from '../controllers/churnController.js';
import { getCLVOverview, handleCLVSimulation } from '../controllers/clvController.js';
import { getSentimentOverview } from '../controllers/sentimentController.js';
import { getProductAndRevenueAnalytics } from '../controllers/productController.js';
import { getRecommendationsOverview } from '../controllers/recommendationController.js';
import { getDataQualityAudit } from '../controllers/dataQualityController.js';
import { handleGroundedAIQuery } from '../controllers/aiController.js';

const router = express.Router();

// Executive Overview
router.get('/dashboard/overview', getOverview);

// Customer Directory & 360 Dossier
router.get('/customers', getCustomersList);
router.get('/customers/:id', getCustomerDetails);
router.get('/customers/:id/orders', getCustomerOrders);

// Segmentation & RFM
router.get('/segments', getSegmentsOverview);
router.get('/segments/compare', compareSegments);

// Churn & Risk Intelligence
router.get('/churn', getChurnOverview);
router.post('/churn/simulate', handleChurnSimulation);

// Customer Lifetime Value (CLV)
router.get('/clv', getCLVOverview);
router.post('/clv/simulate', handleCLVSimulation);

// Sentiment Intelligence & CSAT
router.get('/sentiment', getSentimentOverview);

// Revenue & Product Analytics
router.get('/products', getProductAndRevenueAnalytics);

// Recommendations Engine
router.get('/recommendations', getRecommendationsOverview);

// Data Quality & MLOps Governance
router.get('/data-quality', getDataQualityAudit);

// Grounded AI Decision Support
router.post('/ai/ask', handleGroundedAIQuery);

export default router;
