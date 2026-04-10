const mongoose = require('mongoose');
const User = require('../../../models/User');
const bcrypt = require('bcryptjs');

describe('User Model', () => {
  describe('User Schema', () => {
    it('should create a new user successfully', async () => {
      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };
      
      const user = await User.create(userData);
      
      // Check if user was created successfully
      expect(user._id).toBeDefined();
      expect(user.name).toBe(userData.name);
      expect(user.email).toBe(userData.email);
      expect(user.role).toBe('user'); // Default role
      expect(user.subscriptionStatus).toBe('none'); // Default subscription
      
      // Password should be hashed
      expect(user.password).not.toBe(userData.password);
    });
    
    it('should require name, email, and password', async () => {
      const userData = {};
      
      let err;
      try {
        await User.create(userData);
      } catch (error) {
        err = error;
      }
      
      expect(err).toBeDefined();
      expect(err.errors.name).toBeDefined();
      expect(err.errors.email).toBeDefined();
      expect(err.errors.password).toBeDefined();
    });
    
    it('should not allow duplicate emails', async () => {
      const userData = {
        name: 'Test User',
        email: 'duplicate@example.com',
        password: 'password123'
      };
      
      await User.create(userData);
      
      let err;
      try {
        await User.create(userData);
      } catch (error) {
        err = error;
      }
      
      expect(err).toBeDefined();
      expect(err.code).toBe(11000); // Duplicate key error
    });
  });
  
  describe('User Methods', () => {
    it('should compare passwords correctly', async () => {
      const password = 'password123';
      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password
      };
      
      const user = await User.create(userData);
      
      // Test correct password
      const isMatch = await user.comparePassword(password);
      expect(isMatch).toBe(true);
      
      // Test incorrect password
      const isMatchWrong = await user.comparePassword('wrongpassword');
      expect(isMatchWrong).toBe(false);
    });
  });
  
  describe('Password Hashing', () => {
    it('should hash password before saving', async () => {
      const password = 'password123';
      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password
      };
      
      const user = await User.create(userData);
      
      // Password should be hashed
      expect(user.password).not.toBe(password);
      
      // Should be a valid bcrypt hash
      expect(user.password.startsWith('$2a$')).toBe(true);
      
      // Should be able to verify the password
      const isMatch = await bcrypt.compare(password, user.password);
      expect(isMatch).toBe(true);
    });
    
    it('should not rehash password if not modified', async () => {
      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };
      
      const user = await User.create(userData);
      const originalPassword = user.password;
      
      // Update user without changing password
      user.name = 'Updated Name';
      await user.save();
      
      // Password should remain the same
      expect(user.password).toBe(originalPassword);
    });
  });
});