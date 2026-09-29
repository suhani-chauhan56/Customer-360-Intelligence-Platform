require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const connectDB = require('./config/db');
const { initializeData } = require('./services/dataService');
const apiRoutes = require('./routes/api');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS
app.use(
  cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  })
);

// Body Parser Middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Mount API Routes
app.use('/api', apiRoutes);

// Root Welcome Endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'CustomerAtlas AI — Unified Customer Intelligence REST API Engine',
    version: '2.0.0',
    documentation: '/api/health',
    endpoints: [
      '/api/dashboard',
      '/api/customers',
      '/api/rfm',
      '/api/clv',
      '/api/churn',
      '/api/sentiment',
      '/api/recommendations',
      '/api/analytics/explorer',
      '/api/data-quality',
      '/api/grounded-ai/ask',
    ],
  });
});

// Error Handler Middleware
app.use(errorHandler);

// Initialize Data and Start Server
const startServer = async () => {
  try {
    // 1. Ingest CSV datasets into fast in-memory store
    await initializeData();

    // 2. Connect to MongoDB if configured
    if (process.env.MONGODB_URI) {
      await connectDB();
    } else {
      console.log('[Database] MONGODB_URI not provided. Running in high-performance in-memory feature cache mode.');
    }

    // 3. Start Express HTTP Server
    if (process.env.NODE_ENV !== 'test') {
      app.listen(PORT, () => {
        console.log(`[Server] CustomerAtlas REST API Server running on port ${PORT}`);
        console.log(`[Server] Health check available at http://localhost:${PORT}/api/health`);
      });
    }
  } catch (error) {
    console.error('[Server] Startup failure:', error);
  }
};

startServer();

module.exports = app;
