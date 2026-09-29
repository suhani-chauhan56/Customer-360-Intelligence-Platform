require('dotenv').config({ path: '../.env' });
const mongoose = require('mongoose');
const connectDB = require('../config/db');
const Customer = require('../models/Customer');
const { initializeData, getCustomers } = require('../services/dataService');

const seedData = async () => {
  try {
    console.log('[Seed] Connecting to MongoDB...');
    const connected = await connectDB();
    if (!connected) {
      console.error('[Seed] Could not connect to MongoDB. Exiting.');
      process.exit(1);
    }

    console.log('[Seed] Ingesting CSV feature store...');
    await initializeData();
    const customers = getCustomers();

    console.log(`[Seed] Found ${customers.length.toLocaleString()} customer profiles. Inserting into MongoDB...`);
    await Customer.deleteMany({});
    
    // Batch insert for performance
    const batchSize = 2500;
    for (let i = 0; i < customers.length; i += batchSize) {
      const batch = customers.slice(i, i + batchSize);
      await Customer.insertMany(batch, { ordered: false });
      console.log(`[Seed] Inserted ${Math.min(i + batchSize, customers.length).toLocaleString()} / ${customers.length.toLocaleString()} records...`);
    }

    console.log('[Seed] Database seeding completed successfully!');
    process.exit(0);
  } catch (err) {
    console.error('[Seed] Seeding error:', err);
    process.exit(1);
  }
};

seedData();
