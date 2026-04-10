const mongoose = require('mongoose');

const TemplateSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true
  },
  displayName: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  category: {
    type: String,
    enum: ['business', 'portfolio', 'blog', 'ecommerce', 'personal', 'landing', 'other'],
    default: 'other'
  },
  thumbnail: {
    type: String,
    default: 'default-template-thumbnail.jpg'
  },
  structure: {
    type: Object,
    required: true
  },
  pages: [{
    title: String,
    slug: String,
    content: Object
  }],
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
    }
  },
  isPublic: {
    type: Boolean,
    default: true
  },
  isPremium: {
    type: Boolean,
    default: false
  },
  creator: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  tags: [String],
  popularity: {
    type: Number,
    default: 0
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
TemplateSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Index for faster queries
TemplateSchema.index({ name: 1 });
TemplateSchema.index({ category: 1 });
TemplateSchema.index({ isPublic: 1, isPremium: 1 });
TemplateSchema.index({ tags: 1 });
TemplateSchema.index({ popularity: -1 });

module.exports = mongoose.model('Template', TemplateSchema);