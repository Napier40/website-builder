const mongoose = require('mongoose');

const PageSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true
  },
  slug: {
    type: String,
    required: true
  },
  content: {
    type: Object,
    default: {}
  },
  isPublished: {
    type: Boolean,
    default: false
  },
  meta: {
    description: String,
    keywords: String
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

const WebsiteSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  subdomain: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  customDomain: {
    type: String,
    default: null
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  template: {
    type: String,
    default: 'default'
  },
  pages: [PageSchema],
  settings: {
    theme: {
      type: Object,
      default: {
        primaryColor: '#3498db',
        secondaryColor: '#2ecc71',
        fontFamily: 'Arial, sans-serif',
        fontSize: '16px'
      }
    },
    seo: {
      title: String,
      description: String,
      keywords: String
    },
    analytics: {
      googleAnalyticsId: String
    }
  },
  isPublished: {
    type: Boolean,
    default: false
  },
  moderationStatus: {
    type: String,
    enum: ['pending', 'approved', 'rejected', 'flagged'],
    default: 'approved'
  },
  moderationReason: {
    type: String,
    default: null
  },
  adminOverride: {
    admin: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      default: null
    },
    date: {
      type: Date,
      default: null
    },
    reason: {
      type: String,
      default: null
    }
  },
  lastModifiedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  lastModifiedAt: {
    type: Date
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

module.exports = mongoose.model('Website', WebsiteSchema);