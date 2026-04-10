const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../../server'); // Import the Express app
const User = require('../../models/User');

describe('Auth API', () => {
  describe('POST /api/auth/register', () => {
    it('should register a new user', async () => {
      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };
      
      const res = await request(app)
        .post('/api/auth/register')
        .send(userData);
      
      expect(res.statusCode).toBe(201);
      expect(res.body.success).toBe(true);
      expect(res.body.user).toBeDefined();
      expect(res.body.user.name).toBe(userData.name);
      expect(res.body.user.email).toBe(userData.email);
      expect(res.body.token).toBeDefined();
      
      // Verify user was created in database
      const user = await User.findOne({ email: userData.email });
      expect(user).toBeDefined();
      expect(user.name).toBe(userData.name);
    });
    
    it('should not register a user with missing fields', async () => {
      const userData = {
        name: 'Test User',
        // Missing email and password
      };
      
      const res = await request(app)
        .post('/api/auth/register')
        .send(userData);
      
      expect(res.statusCode).toBe(400);
      expect(res.body.success).toBe(false);
    });
    
    it('should not register a user with an existing email', async () => {
      // Create user first
      await User.create({
        name: 'Existing User',
        email: 'existing@example.com',
        password: 'password123'
      });
      
      const userData = {
        name: 'Test User',
        email: 'existing@example.com', // Same email
        password: 'password123'
      };
      
      const res = await request(app)
        .post('/api/auth/register')
        .send(userData);
      
      expect(res.statusCode).toBe(400);
      expect(res.body.success).toBe(false);
      expect(res.body.message).toBe('User already exists');
    });
  });
  
  describe('POST /api/auth/login', () => {
    it('should login a user', async () => {
      // Create user first
      const password = 'password123';
      const user = await User.create({
        name: 'Test User',
        email: 'test@example.com',
        password
      });
      
      const loginData = {
        email: 'test@example.com',
        password
      };
      
      const res = await request(app)
        .post('/api/auth/login')
        .send(loginData);
      
      expect(res.statusCode).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.user).toBeDefined();
      expect(res.body.user.email).toBe(loginData.email);
      expect(res.body.token).toBeDefined();
    });
    
    it('should not login with invalid credentials', async () => {
      // Create user first
      await User.create({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      
      const loginData = {
        email: 'test@example.com',
        password: 'wrongpassword'
      };
      
      const res = await request(app)
        .post('/api/auth/login')
        .send(loginData);
      
      expect(res.statusCode).toBe(401);
      expect(res.body.success).toBe(false);
      expect(res.body.message).toBe('Invalid credentials');
    });
  });
  
  describe('GET /api/auth/me', () => {
    it('should get current user profile', async () => {
      // Create user first
      const user = await User.create({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      
      // Login to get token
      const loginRes = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'password123'
        });
      
      const token = loginRes.body.token;
      
      // Get current user
      const res = await request(app)
        .get('/api/auth/me')
        .set('Authorization', `Bearer ${token}`);
      
      expect(res.statusCode).toBe(200);
      expect(res.body.success).toBe(true);
      expect(res.body.user).toBeDefined();
      expect(res.body.user._id).toBe(user._id.toString());
      expect(res.body.user.email).toBe(user.email);
    });
    
    it('should not get profile without token', async () => {
      const res = await request(app)
        .get('/api/auth/me');
      
      expect(res.statusCode).toBe(401);
      expect(res.body.success).toBe(false);
    });
    
    it('should not get profile with invalid token', async () => {
      const res = await request(app)
        .get('/api/auth/me')
        .set('Authorization', 'Bearer invalidtoken');
      
      expect(res.statusCode).toBe(401);
      expect(res.body.success).toBe(false);
    });
  });
});