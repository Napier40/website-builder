const mongoose = require('mongoose');

const ModerationSchema = new mongoose.Schema({
  content: {
    type: mongoose.Schema.Types.ObjectId,
    refPath: 'contentModel',
    required: true
  },
  contentModel: {
    type: String,
    enum: ['Website', 'Page'],
    required: true
  },
  moderator: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'approved', 'rejected', 'flagged'],
    default: 'pending'
  },
  reason: {
    type: String,
    required: function() {
      return this.status === 'rejected' || this.status === 'flagged';
    }
  },
  action: {
    type: String,
    enum: ['none', 'warning', 'temporary_ban', 'permanent_ban', 'content_removal'],
    default: 'none'
  },
  originalContent: Object,
  modifiedContent: Object,
  userNotified: {
    type: Boolean,
    default: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Update the updatedAt field on save
ModerationSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Index for faster queries
ModerationSchema.index({ status: 1, createdAt: -1 });
ModerationSchema.index({ contentModel: 1, content: 1 });
ModerationSchema.index({ moderator: 1 });

module.exports = mongoose.model('Moderation', ModerationSchema);