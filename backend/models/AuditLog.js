const mongoose = require('mongoose');

const AuditLogSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  action: {
    type: String,
    required: true,
    enum: [
      'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 
      'PASSWORD_CHANGE', 'CONTENT_OVERRIDE', 'MODERATION',
      'SUBSCRIPTION_CHANGE', 'PAYMENT', 'ADMIN_ACTION'
    ]
  },
  resource: {
    type: String,
    required: true
  },
  resourceId: {
    type: mongoose.Schema.Types.ObjectId,
    refPath: 'resourceModel'
  },
  resourceModel: {
    type: String,
    enum: ['User', 'Website', 'Page', 'Subscription', 'Payment', null]
  },
  ipAddress: String,
  userAgent: String,
  previousState: Object,
  newState: Object,
  details: Object,
  timestamp: {
    type: Date,
    default: Date.now
  }
});

// Index for faster queries
AuditLogSchema.index({ user: 1, timestamp: -1 });
AuditLogSchema.index({ action: 1, timestamp: -1 });
AuditLogSchema.index({ resource: 1, resourceId: 1 });

// Static method to create audit log
AuditLogSchema.statics.createLog = async function(logData) {
  try {
    return await this.create(logData);
  } catch (error) {
    console.error('Error creating audit log:', error);
    // Don't throw - audit logs should never break the main application flow
    return null;
  }
};

module.exports = mongoose.model('AuditLog', AuditLogSchema);