const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Import routes
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const subscriptionRoutes = require('./routes/subscriptions');
const websiteRoutes = require('./routes/websites');
const paymentRoutes = require('./routes/payments');
const adminRoutes = require('./routes/admin');
const pluginRoutes = require('./routes/plugins');
const templateRoutes = require('./routes/templates');

// Import error handler
const errorHandler = require('./middleware/errorHandler');

// Import plugin manager
const pluginManager = require('./services/pluginManager');

// Use routes
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/subscriptions', subscriptionRoutes);
app.use('/api/websites', websiteRoutes);
app.use('/api/payments', paymentRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/plugins', pluginRoutes);
app.use('/api/templates', templateRoutes);

// Connect to MongoDB
const connectDB = require('./config/db');
connectDB();

// Serve static assets in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../frontend/build')));
  
  app.get('*', (req, res) => {
    res.sendFile(path.resolve(__dirname, '../frontend', 'build', 'index.html'));
  });
}

// Error handler middleware (must be after routes)
app.use(errorHandler);

// Define port
const PORT = process.env.PORT || 5000;

// Initialize plugin manager
pluginManager.initialize().catch(err => {
  console.error('Failed to initialize plugin manager:', err);
});

// Start server
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));