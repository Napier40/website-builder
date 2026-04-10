const User = require('../models/User');
const Website = require('../models/Website');
const Subscription = require('../models/Subscription');
const Payment = require('../models/Payment');
const AuditLog = require('../models/AuditLog');
const Moderation = require('../models/Moderation');
const ErrorResponse = require('../utils/errorResponse');
const asyncHandler = require('../middleware/async');

// @desc    Get all users with filtering and pagination
// @route   GET /api/admin/users
// @access  Private/Admin
exports.getUsers = asyncHandler(async (req, res, next) => {
  const { search, role, subscriptionStatus, page = 1, limit = 10, sort = 'createdAt' } = req.query;
  
  const query = {};
  
  // Search by name or email
  if (search) {
    query.$or = [
      { name: { $regex: search, $options: 'i' } },
      { email: { $regex: search, $options: 'i' } }
    ];
  }
  
  if (role) query.role = role;
  if (subscriptionStatus) query.subscriptionStatus = subscriptionStatus;
  
  const sortDirection = sort.startsWith('-') ? -1 : 1;
  const sortField = sort.startsWith('-') ? sort.substring(1) : sort;
  
  const users = await User.find(query)
    .select('-password')
    .sort({ [sortField]: sortDirection })
    .skip((page - 1) * limit)
    .limit(parseInt(limit));
    
  const total = await User.countDocuments(query);
  
  res.status(200).json({
    success: true,
    count: users.length,
    total,
    pages: Math.ceil(total / limit),
    users
  });
});

// @desc    Get user by ID
// @route   GET /api/admin/users/:id
// @access  Private/Admin
exports.getUserById = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.params.id).select('-password');
  
  if (!user) {
    return next(new ErrorResponse(`User not found with id of ${req.params.id}`, 404));
  }
  
  // Get user's websites
  const websites = await Website.find({ user: req.params.id });
  
  // Get user's payment history
  const payments = await Payment.find({ user: req.params.id })
    .sort({ createdAt: -1 })
    .limit(5);
  
  // Get user's audit logs
  const auditLogs = await AuditLog.find({ user: req.params.id })
    .sort({ timestamp: -1 })
    .limit(10);
  
  res.status(200).json({
    success: true,
    data: {
      user,
      websites: {
        count: websites.length,
        items: websites
      },
      payments: {
        count: payments.length,
        items: payments
      },
      auditLogs: {
        count: auditLogs.length,
        items: auditLogs
      }
    }
  });
});

// @desc    Update user
// @route   PUT /api/admin/users/:id
// @access  Private/Admin
exports.updateUser = asyncHandler(async (req, res, next) => {
  const { name, email, role, subscriptionStatus, isActive } = req.body;
  
  const user = await User.findById(req.params.id);
  
  if (!user) {
    return next(new ErrorResponse(`User not found with id of ${req.params.id}`, 404));
  }
  
  // Store original state for audit log
  const originalState = {
    name: user.name,
    email: user.email,
    role: user.role,
    subscriptionStatus: user.subscriptionStatus,
    isActive: user.isActive
  };
  
  // Update fields
  if (name) user.name = name;
  if (email) user.email = email;
  if (role) user.role = role;
  if (subscriptionStatus) user.subscriptionStatus = subscriptionStatus;
  if (isActive !== undefined) user.isActive = isActive;
  
  await user.save();
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'ADMIN_ACTION',
    resource: `/api/admin/users/${user._id}`,
    resourceId: user._id,
    resourceModel: 'User',
    previousState: originalState,
    newState: {
      name: user.name,
      email: user.email,
      role: user.role,
      subscriptionStatus: user.subscriptionStatus,
      isActive: user.isActive
    },
    details: { 
      action: 'UPDATE_USER',
      updatedFields: req.body
    }
  });
  
  res.status(200).json({
    success: true,
    data: user
  });
});

// @desc    Delete user
// @route   DELETE /api/admin/users/:id
// @access  Private/Admin
exports.deleteUser = asyncHandler(async (req, res, next) => {
  const user = await User.findById(req.params.id);
  
  if (!user) {
    return next(new ErrorResponse(`User not found with id of ${req.params.id}`, 404));
  }
  
  // Create audit log before deletion
  await AuditLog.createLog({
    user: req.user._id,
    action: 'ADMIN_ACTION',
    resource: `/api/admin/users/${user._id}`,
    resourceId: user._id,
    resourceModel: 'User',
    previousState: user.toObject(),
    details: { 
      action: 'DELETE_USER'
    }
  });
  
  await user.remove();
  
  res.status(200).json({
    success: true,
    data: {}
  });
});

// @desc    Get content moderation queue
// @route   GET /api/admin/moderation
// @access  Private/Admin
exports.getModerationQueue = asyncHandler(async (req, res, next) => {
  const { status = 'pending', contentModel, page = 1, limit = 10 } = req.query;
  
  const query = {};
  if (status) query.status = status;
  if (contentModel) query.contentModel = contentModel;
  
  const moderations = await Moderation.find(query)
    .populate({
      path: 'content',
      select: 'name subdomain isPublished user',
      populate: {
        path: 'user',
        select: 'name email'
      }
    })
    .populate('moderator', 'name email')
    .sort({ createdAt: -1 })
    .skip((page - 1) * limit)
    .limit(parseInt(limit));
    
  const total = await Moderation.countDocuments(query);
  
  res.status(200).json({
    success: true,
    count: moderations.length,
    total,
    pages: Math.ceil(total / limit),
    data: moderations
  });
});

// @desc    Process moderation item
// @route   PUT /api/admin/moderation/:id
// @access  Private/Admin
exports.processModeration = asyncHandler(async (req, res, next) => {
  const { status, reason, action, modifiedContent } = req.body;
  
  const moderation = await Moderation.findById(req.params.id);
  
  if (!moderation) {
    return next(new ErrorResponse(`Moderation item not found with id of ${req.params.id}`, 404));
  }
  
  // Update moderation record
  moderation.status = status;
  moderation.reason = reason;
  moderation.action = action;
  moderation.moderator = req.user._id;
  
  if (modifiedContent) {
    moderation.modifiedContent = modifiedContent;
  }
  
  await moderation.save();
  
  // If approved or rejected, update the content
  if (status === 'approved' || status === 'rejected') {
    let contentModel;
    
    if (moderation.contentModel === 'Website') {
      contentModel = Website;
    } else if (moderation.contentModel === 'Page') {
      // Handle Page model if needed
    }
    
    if (contentModel) {
      const content = await contentModel.findById(moderation.content);
      
      if (content) {
        if (status === 'approved') {
          // If approved, no changes needed
          content.moderationStatus = 'approved';
        } else if (status === 'rejected') {
          // If rejected and we have modified content, apply it
          if (moderation.modifiedContent) {
            // Apply modified content (implementation depends on content structure)
            Object.assign(content, moderation.modifiedContent);
          }
          
          content.moderationStatus = 'rejected';
          content.moderationReason = reason;
        }
        
        await content.save();
      }
    }
  }
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'MODERATION',
    resource: `/api/admin/moderation/${moderation._id}`,
    resourceId: moderation._id,
    resourceModel: 'Moderation',
    details: { 
      status,
      reason,
      action,
      contentId: moderation.content,
      contentModel: moderation.contentModel
    }
  });
  
  res.status(200).json({
    success: true,
    data: moderation
  });
});

// @desc    Override website content
// @route   PUT /api/admin/websites/:id/override
// @access  Private/Admin
exports.overrideWebsiteContent = asyncHandler(async (req, res, next) => {
  const { content, reason } = req.body;
  
  const website = await Website.findById(req.params.id);
  
  if (!website) {
    return next(new ErrorResponse(`Website not found with id of ${req.params.id}`, 404));
  }
  
  // Store original content for audit trail
  const originalContent = JSON.parse(JSON.stringify(website.pages));
  
  // Update content
  if (content) {
    website.pages = content;
  }
  
  website.lastModifiedBy = req.user._id;
  website.lastModifiedAt = Date.now();
  
  // Add admin override flag
  website.adminOverride = {
    admin: req.user._id,
    date: Date.now(),
    reason
  };
  
  await website.save();
  
  // Create audit log
  await AuditLog.createLog({
    user: req.user._id,
    action: 'CONTENT_OVERRIDE',
    resource: `/api/admin/websites/${website._id}/override`,
    resourceId: website._id,
    resourceModel: 'Website',
    previousState: { pages: originalContent },
    newState: { pages: website.pages },
    details: { 
      reason,
      websiteName: website.name,
      websiteOwner: website.user
    }
  });
  
  // Create moderation record
  await Moderation.create({
    content: website._id,
    contentModel: 'Website',
    moderator: req.user._id,
    status: 'approved', // Auto-approved since admin did the override
    reason,
    action: 'content_removal',
    originalContent: { pages: originalContent },
    modifiedContent: { pages: website.pages }
  });
  
  res.status(200).json({
    success: true,
    message: 'Website content overridden successfully',
    data: website
  });
});

// @desc    Get audit logs
// @route   GET /api/admin/audit-logs
// @access  Private/Admin
exports.getAuditLogs = asyncHandler(async (req, res, next) => {
  const { user, action, resource, startDate, endDate, page = 1, limit = 20 } = req.query;
  
  const query = {};
  
  if (user) query.user = user;
  if (action) query.action = action;
  if (resource) query.resource = { $regex: resource, $options: 'i' };
  
  // Date range filter
  if (startDate || endDate) {
    query.timestamp = {};
    if (startDate) query.timestamp.$gte = new Date(startDate);
    if (endDate) query.timestamp.$lte = new Date(endDate);
  }
  
  const logs = await AuditLog.find(query)
    .populate('user', 'name email')
    .sort({ timestamp: -1 })
    .skip((page - 1) * limit)
    .limit(parseInt(limit));
    
  const total = await AuditLog.countDocuments(query);
  
  res.status(200).json({
    success: true,
    count: logs.length,
    total,
    pages: Math.ceil(total / limit),
    data: logs
  });
});

// @desc    Get admin dashboard statistics
// @route   GET /api/admin/dashboard
// @access  Private/Admin
exports.getDashboardStats = asyncHandler(async (req, res, next) => {
  // Get user statistics
  const totalUsers = await User.countDocuments();
  const newUsers = await User.countDocuments({
    createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
  });
  
  // Get subscription statistics
  const subscriptionStats = await User.aggregate([
    {
      $group: {
        _id: '$subscriptionStatus',
        count: { $sum: 1 }
      }
    }
  ]);
  
  // Get website statistics
  const totalWebsites = await Website.countDocuments();
  const publishedWebsites = await Website.countDocuments({ isPublished: true });
  
  // Get payment statistics
  const monthlyRevenue = await Payment.aggregate([
    {
      $match: {
        status: 'completed',
        createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
      }
    },
    {
      $group: {
        _id: null,
        total: { $sum: '$amount' }
      }
    }
  ]);
  
  // Get moderation statistics
  const moderationStats = await Moderation.aggregate([
    {
      $group: {
        _id: '$status',
        count: { $sum: 1 }
      }
    }
  ]);
  
  res.status(200).json({
    success: true,
    data: {
      users: {
        total: totalUsers,
        new: newUsers,
        subscriptions: subscriptionStats
      },
      websites: {
        total: totalWebsites,
        published: publishedWebsites
      },
      revenue: {
        monthly: monthlyRevenue.length > 0 ? monthlyRevenue[0].total : 0
      },
      moderation: moderationStats
    }
  });
});