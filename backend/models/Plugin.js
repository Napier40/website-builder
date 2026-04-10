const mongoose = require('mongoose');

const PluginSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true
  },
  description: {
    type: String,
    required: true
  },
  version: {
    type: String,
    required: true
  },
  entryPoint: {
    type: String,
    required: true
  },
  settings: {
    type: Object,
    default: {}
  },
  isActive: {
    type: Boolean,
    default: true
  },
  permissions: [String],
  author: {
    name: String,
    email: String,
    url: String
  },
  repository: String,
  installedBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  },
  installedAt: {
    type: Date,
    default: Date.now
  },
  lastUpdated: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Plugin', PluginSchema);