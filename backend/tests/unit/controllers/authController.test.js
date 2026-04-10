const mongoose = require('mongoose');
const { register, login, getMe } = require('../../../controllers/authController');
const User = require('../../../models/User');
const jwt = require('jsonwebtoken');

// Mock response object
const mockResponse = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

describe('Auth Controller', () => {
  describe('register', () => {
    it('should register a new user and return token', async () => {
      // Mock request and response
      const req = {
        body: {
          name: 'Test User',
          email: 'test@example.com',
          password: 'password123'
        }
      };
      const res = mockResponse();
      
      // Call register function
      await register(req, res);
      
      // Check response
      expect(res.status).toHaveBeenCalledWith(201);
      expect(res.json).toHaveBeenCalled();
      
      // Get response data
      const responseData = res.json.mock.calls[0][0];
      expect(responseData.success).toBe(true);
      expect(responseData.user).toBeDefined();
      expect(responseData.user.name).toBe(req.body.name);
      expect(responseData.user.email).toBe(req.body.email);
      expect(responseData.token).toBeDefined();
      
      // Verify user was created in database
      const user = await User.findOne({ email: req.body.email });
      expect(user).toBeDefined();
      expect(user.name).toBe(req.body.name);
    });
    
    it('should return error if user already exists', async () => {
      // Create user first
      await User.create({
        name: 'Existing User',
        email: 'existing@example.com',
        password: 'password123'
      });
      
      // Mock request and response
      const req = {
        body: {
          name: 'Test User',
          email: 'existing@example.com', // Same email
          password: 'password123'
        }
      };
      const res = mockResponse();
      
      // Call register function
      await register(req, res);
      
      // Check response
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.json).toHaveBeenCalled();
      
      // Get response data
      const responseData = res.json.mock.calls[0][0];
      expect(responseData.success).toBe(false);
      expect(responseData.message).toBe('User already exists');
    });
  });
  
  describe('login', () => {
    it('should login user and return token', async () => {
      // Create user first
      const password = 'password123';
      const user = await User.create({
        name: 'Test User',
        email: 'test@example.com',
        password
      });
      
      // Mock request and response
      const req = {
        body: {
          email: 'test@example.com',
          password
        }
      };
      const res = mockResponse();
      
      // Call login function
      await login(req, res);
      
      // Check response
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalled();
      
      // Get response data
      const responseData = res.json.mock.calls[0][0];
      expect(responseData.success).toBe(true);
      expect(responseData.user).toBeDefined();
      expect(responseData.user.email).toBe(req.body.email);
      expect(responseData.token).toBeDefined();
      
      // Verify token
      const decoded = jwt.verify(responseData.token, process.env.JWT_SECRET);
      expect(decoded.id).toBe(user._id.toString());
    });
    
    it('should return error if user does not exist', async () => {
      // Mock request and response
      const req = {
        body: {
          email: 'nonexistent@example.com',
          password: 'password123'
        }
      };
      const res = mockResponse();
      
      // Call login function
      await login(req, res);
      
      // Check response
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalled();
      
      // Get response data
      const responseData = res.json.mock.calls[0][0];
      expect(responseData.success).toBe(false);
      expect(responseData.message).toBe('Invalid credentials');
    });
    
    it('should return error if password is incorrect', async () => {
      // Create user first
      await User.create({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      
      // Mock request and response
      const req = {
        body: {
          email: 'test@example.com',
          password: 'wrongpassword'
        }
      };
      const res = mockResponse();
      
      // Call login function
      await login(req, res);
      
      // Check response
      expect(res.status).toHaveBeenCalledWith(401);
      expect(res.json).toHaveBeenCalled();
      
      // Get response data
      const responseData = res.json.mock.calls[0][0];
      expect(responseData.success).toBe(false);
      expect(responseData.message).toBe('Invalid credentials');
    });
  });
  
  describe('getMe', () => {
    it('should return current user', async () => {
      // Create user first
      const user = await User.create({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      
      // Mock request and response
      const req = {
        user: await User.findById(user._id).select('-password')
      };
      const res = mockResponse();
      
      // Call getMe function
      await getMe(req, res);
      
      // Check response
      expect(res.status).toHaveBeenCalledWith(200);
      expect(res.json).toHaveBeenCalled();
      
      // Get response data
      const responseData = res.json.mock.calls[0][0];
      expect(responseData.success).toBe(true);
      expect(responseData.user).toBeDefined();
      expect(responseData.user._id.toString()).toBe(user._id.toString());
      expect(responseData.user.email).toBe(user.email);
    });
  });
});