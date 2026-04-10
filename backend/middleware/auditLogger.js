const AuditLog = require('../models/AuditLog');

/**
 * Middleware to log API requests for auditing purposes
 * @param {string} action - The action being performed (CREATE, UPDATE, DELETE, etc.)
 * @param {string} resourceModel - The model name for the resource (User, Website, etc.)
 */
const auditLogger = (action, resourceModel = null) => {
  return async (req, res, next) => {
    // Store original response methods
    const originalJson = res.json;
    const originalSend = res.send;
    
    // Override response methods to capture response data
    res.json = function(body) {
      res.body = body;
      return originalJson.call(this, body);
    };
    
    res.send = function(body) {
      res.body = body;
      return originalSend.call(this, body);
    };
    
    // Continue with request
    next();
    
    try {
      // Only log if user is authenticated
      if (!req.user) return;
      
      // Extract resource ID from params or body
      let resourceId = null;
      if (req.params.id) {
        resourceId = req.params.id;
      } else if (req.body._id) {
        resourceId = req.body._id;
      }
      
      // Create audit log entry
      await AuditLog.createLog({
        user: req.user._id,
        action,
        resource: req.originalUrl,
        resourceId: resourceId,
        resourceModel,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'],
        details: {
          method: req.method,
          query: req.query,
          body: req.method !== 'GET' ? req.body : undefined,
          params: req.params,
          statusCode: res.statusCode,
          response: res.body
        }
      });
    } catch (error) {
      // Don't block the request flow if logging fails
      console.error('Audit logging error:', error);
    }
  };
};

module.exports = auditLogger;