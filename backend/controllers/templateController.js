const Template = require('../models/Template');
const ErrorResponse = require('../utils/errorResponse');
const asyncHandler = require('../middleware/async');
const AuditLog = require('../models/AuditLog');

// @desc    Get all templates
// @route   GET /api/templates
// @access  Public
exports.getTemplates = asyncHandler(async (req, res, next) => {
  const { category, isPremium, search, tags, page = 1, limit = 10, sort = 'popularity' } = req.query;
  
  const query = { isPublic: true };
  
  // Filter by category
  if (category) {
    query.category = category;
  }
  
  // Filter by premium status
  if (isPremium !== undefined) {
    query.isPremium = isPremium === 'true';
  }
  
  // Filter by tags (comma-separated)
  if (tags) {
    const tagArray = tags.split(',').map(tag => tag.trim());
    query.tags = { $in: tagArray };
  }
  
  // Search by name or description
  if (search) {
    query.$or = [
      { name: { $regex: search, $options: 'i' } },
      { displayName: { $regex: search, $options: 'i' } },
      { description: { $regex: search, $options: 'i' } }
    ];
  }
  
  // Determine sort order
  const sortDirection = sort.startsWith('-') ? -1 : 1;
  const sortField = sort.startsWith('-') ? sort.substring(1) : sort;
  
  // Execute query with pagination
  const templates = await Template.find(query)
    .populate('creator', 'name')
    .sort({ [sortField]: sortDirection })
    .skip((page - 1) * limit)
    .limit(parseInt(limit));
    
  const total = await Template.countDocuments(query);
  
  res.status(200).json({
    success: true,
    count: templates.length,
    total,
    pages: Math.ceil(total / limit),
    data: templates
  });
});

// @desc    Get template by ID
// @route   GET /api/templates/:id
// @access  Public
exports.getTemplateById = asyncHandler(async (req, res, next) => {
  const template = await Template.findById(req.params.id).populate('creator', 'name');
  
  if (!template) {
    return next(new ErrorResponse(`Template not found with id of ${req.params.id}`, 404));
  }
  
  // Check if template is public or user is creator or admin
  if (!template.isPublic && 
      (!req.user || (template.creator && template.creator._id.toString() !== req.user._id.toString() && req.user.role !== 'admin'))) {
    return next(new ErrorResponse(`Not authorized to access this template`, 403));
  }
  
  // Increment popularity
  template.popularity += 1;
  await template.save();
  
  res.status(200).json({
    success: true,
    data: template
  });
});

// @desc    Create template
// @route   POST /api/templates
// @access  Private
exports.createTemplate = asyncHandler(async (req, res, next) => {
  // Add creator
  req.body.creator = req.user._id;
  
  // Create template
  const template = await Template.create(req.body);
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'CREATE',
    resource: `/api/templates`,
    resourceId: template._id,
    resourceModel: 'Template',
    details: { 
      templateName: template.name
    }
  });
  
  res.status(201).json({
    success: true,
    data: template
  });
});

// @desc    Update template
// @route   PUT /api/templates/:id
// @access  Private
exports.updateTemplate = asyncHandler(async (req, res, next) => {
  let template = await Template.findById(req.params.id);
  
  if (!template) {
    return next(new ErrorResponse(`Template not found with id of ${req.params.id}`, 404));
  }
  
  // Check if user is template creator or admin
  if (template.creator && template.creator.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    return next(new ErrorResponse(`Not authorized to update this template`, 403));
  }
  
  // Store original state for audit log
  const originalState = template.toObject();
  
  // Update template
  template = await Template.findByIdAndUpdate(req.params.id, req.body, {
    new: true,
    runValidators: true
  });
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'UPDATE',
    resource: `/api/templates/${template._id}`,
    resourceId: template._id,
    resourceModel: 'Template',
    previousState: originalState,
    newState: template.toObject(),
    details: { 
      templateName: template.name
    }
  });
  
  res.status(200).json({
    success: true,
    data: template
  });
});

// @desc    Delete template
// @route   DELETE /api/templates/:id
// @access  Private
exports.deleteTemplate = asyncHandler(async (req, res, next) => {
  const template = await Template.findById(req.params.id);
  
  if (!template) {
    return next(new ErrorResponse(`Template not found with id of ${req.params.id}`, 404));
  }
  
  // Check if user is template creator or admin
  if (template.creator && template.creator.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    return next(new ErrorResponse(`Not authorized to delete this template`, 403));
  }
  
  // Create audit log before deletion
  await AuditLog.createLog({
    user: req.user._id,
    action: 'DELETE',
    resource: `/api/templates/${template._id}`,
    resourceId: template._id,
    resourceModel: 'Template',
    previousState: template.toObject(),
    details: { 
      templateName: template.name
    }
  });
  
  await template.remove();
  
  res.status(200).json({
    success: true,
    data: {}
  });
});

// @desc    Save website as template
// @route   POST /api/templates/from-website/:websiteId
// @access  Private
exports.saveWebsiteAsTemplate = asyncHandler(async (req, res, next) => {
  const { websiteId } = req.params;
  const { name, displayName, description, category, isPublic, tags } = req.body;
  
  // Find the website
  const Website = require('../models/Website');
  const website = await Website.findById(websiteId);
  
  if (!website) {
    return next(new ErrorResponse(`Website not found with id of ${websiteId}`, 404));
  }
  
  // Check if user owns the website
  if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
    return next(new ErrorResponse(`Not authorized to use this website as template`, 403));
  }
  
  // Create template from website
  const template = await Template.create({
    name: name || `template-${Date.now()}`,
    displayName: displayName || website.name,
    description: description || `Template created from ${website.name}`,
    category: category || 'other',
    structure: website.settings || {},
    pages: website.pages || [],
    settings: website.settings || {},
    isPublic: isPublic !== undefined ? isPublic : false,
    isPremium: req.user.role === 'admin', // Only admins can create premium templates
    creator: req.user._id,
    tags: tags || []
  });
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'CREATE',
    resource: `/api/templates/from-website/${websiteId}`,
    resourceId: template._id,
    resourceModel: 'Template',
    details: { 
      templateName: template.name,
      websiteId,
      websiteName: website.name
    }
  });
  
  res.status(201).json({
    success: true,
    data: template
  });
});

// @desc    Get template categories
// @route   GET /api/templates/categories
// @access  Public
exports.getTemplateCategories = asyncHandler(async (req, res, next) => {
  const categories = await Template.distinct('category');
  
  res.status(200).json({
    success: true,
    count: categories.length,
    data: categories
  });
});

// @desc    Get template tags
// @route   GET /api/templates/tags
// @access  Public
exports.getTemplateTags = asyncHandler(async (req, res, next) => {
  const tags = await Template.aggregate([
    { $unwind: '$tags' },
    { $group: { _id: '$tags', count: { $sum: 1 } } },
    { $sort: { count: -1 } },
    { $limit: 50 }
  ]);
  
  res.status(200).json({
    success: true,
    count: tags.length,
    data: tags.map(tag => ({ name: tag._id, count: tag.count }))
  });
});