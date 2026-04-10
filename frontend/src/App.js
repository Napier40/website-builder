import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

// Layout Components
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Sidebar from './components/layout/Sidebar';

// Page Components
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Websites from './pages/Websites';
import WebsiteBuilder from './pages/WebsiteBuilder';
import Subscriptions from './pages/Subscriptions';
import Checkout from './pages/Checkout';
import Account from './pages/Account';
import NotFound from './pages/NotFound';

// Context
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/routing/PrivateRoute';

// Styles
import './App.css';

// Initialize Stripe
const stripePromise = loadStripe('your_stripe_publishable_key');

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Header />
          <div className="main-container">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected Routes */}
              <Route path="/dashboard" element={
                <PrivateRoute>
                  <div className="dashboard-layout">
                    <Sidebar />
                    <Dashboard />
                  </div>
                </PrivateRoute>
              } />
              
              <Route path="/websites" element={
                <PrivateRoute>
                  <div className="dashboard-layout">
                    <Sidebar />
                    <Websites />
                  </div>
                </PrivateRoute>
              } />
              
              <Route path="/builder/:id" element={
                <PrivateRoute>
                  <WebsiteBuilder />
                </PrivateRoute>
              } />
              
              <Route path="/subscriptions" element={
                <PrivateRoute>
                  <div className="dashboard-layout">
                    <Sidebar />
                    <Subscriptions />
                  </div>
                </PrivateRoute>
              } />
              
              <Route path="/checkout/:id" element={
                <PrivateRoute>
                  <Elements stripe={stripePromise}>
                    <div className="dashboard-layout">
                      <Sidebar />
                      <Checkout />
                    </div>
                  </Elements>
                </PrivateRoute>
              } />
              
              <Route path="/account" element={
                <PrivateRoute>
                  <div className="dashboard-layout">
                    <Sidebar />
                    <Account />
                  </div>
                </PrivateRoute>
              } />
              
              {/* 404 Route */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;