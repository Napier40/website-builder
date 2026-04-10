const Website = require('../models/Website');
const User = require('../models/User');
const Subscription = require('../models/Subscription');

// @desc    Get all websites for current user
// @route   GET /api/websites
// @access  Private
exports.getMyWebsites = async (req, res) => {
  try {
    const websites = await Website.find({ user: req.user._id });
    
    res.status(200).json({
      success: true,
      count: websites.length,
      websites
    });
  } catch (error) {
    console.error('Get my websites error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Get website by ID
// @route   GET /api/websites/:id
// @access  Private
exports.getWebsiteById = async (req, res) => {
  try {
    const website = await Website.findById(req.params.id);
    
    if (!website) {
      return res.status(404).json({ success: false, message: 'Website not found' });
    }
    
    // Check if user owns the website
    if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to access this website' });
    }
    
    res.status(200).json({
      success: true,
      website
    });
  } catch (error) {
    console.error('Get website by ID error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Create new website
// @route   POST /api/websites
// @access  Private
exports.createWebsite = async (req, res) => {
  try {
    const { name, subdomain, template } = req.body;
    
    // Check if user has reached website limit
    const user = await User.findById(req.user._id);
    const userWebsites = await Website.countDocuments({ user: req.user._id });
    
    // Get subscription details
    let websiteLimit = 1; // Default limit for free users
    
    if (user.subscriptionStatus !== 'none') {
      const subscription = await Subscription.findOne({ name: user.subscriptionStatus });
      if (subscription) {
        websiteLimit = subscription.websiteLimit;
      }
    }
    
    if (userWebsites >= websiteLimit) {
      return res.status(403).json({ 
        success: false, 
        message: `You have reached your website limit (${websiteLimit}). Please upgrade your subscription to create more websites.` 
      });
    }
    
    // Check if subdomain is available
    const subdomainExists = await Website.findOne({ subdomain });
    if (subdomainExists) {
      return res.status(400).json({ success: false, message: 'Subdomain is already taken' });
    }
    
    // Create default home page
    const homePage = {
      title: 'Home',
      slug: 'home',
      content: {
        sections: [
          {
            type: 'hero',
            heading: 'Welcome to my website',
            subheading: 'This is a new website created with Website Builder',
            buttonText: 'Learn More',
            buttonLink: '#about'
          },
          {
            type: 'text',
            heading: 'About Us',
            content: 'This is the about section of your new website. You can edit this content in the website builder.'
          }
        ]
      },
      isPublished: true,
      meta: {
        description: 'Welcome to my website',
        keywords: 'website, builder'
      }
    };
    
    // Create website
    const website = await Website.create({
      name,
      subdomain,
      user: req.user._id,
      template: template || 'default',
      pages: [homePage]
    });
    
    res.status(201).json({
      success: true,
      website
    });
  } catch (error) {
    console.error('Create website error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Update website
// @route   PUT /api/websites/:id
// @access  Private
exports.updateWebsite = async (req, res) => {
  try {
    const { name, customDomain, template, settings } = req.body;
    
    // Find website
    const website = await Website.findById(req.params.id);
    
    if (!website) {
      return res.status(404).json({ success: false, message: 'Website not found' });
    }
    
    // Check if user owns the website
    if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to update this website' });
    }
    
    // Check if user can use custom domain
    if (customDomain && customDomain !== website.customDomain) {
      const user = await User.findById(req.user._id);
      
      if (user.subscriptionStatus === 'none' || user.subscriptionStatus === 'basic') {
        return res.status(403).json({ 
          success: false, 
          message: 'Custom domains are only available for Premium and Enterprise subscriptions' 
        });
      }
      
      // Check if domain is already in use
      const domainExists = await Website.findOne({ customDomain });
      if (domainExists && domainExists._id.toString() !== website._id.toString()) {
        return res.status(400).json({ success: false, message: 'Domain is already in use' });
      }
    }
    
    // Update fields
    if (name) website.name = name;
    if (customDomain !== undefined) website.customDomain = customDomain;
    if (template) website.template = template;
    if (settings) {
      website.settings = {
        ...website.settings,
        ...settings
      };
    }
    
    website.updatedAt = Date.now();
    
    // Save website
    await website.save();
    
    res.status(200).json({
      success: true,
      website
    });
  } catch (error) {
    console.error('Update website error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Delete website
// @route   DELETE /api/websites/:id
// @access  Private
exports.deleteWebsite = async (req, res) => {
  try {
    const website = await Website.findById(req.params.id);
    
    if (!website) {
      return res.status(404).json({ success: false, message: 'Website not found' });
    }
    
    // Check if user owns the website
    if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to delete this website' });
    }
    
    await website.remove();
    
    res.status(200).json({
      success: true,
      message: 'Website deleted successfully'
    });
  } catch (error) {
    console.error('Delete website error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Create new page for website
// @route   POST /api/websites/:id/pages
// @access  Private
exports.createPage = async (req, res) => {
  try {
    const { title, slug, content, meta } = req.body;
    
    // Find website
    const website = await Website.findById(req.params.id);
    
    if (!website) {
      return res.status(404).json({ success: false, message: 'Website not found' });
    }
    
    // Check if user owns the website
    if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to update this website' });
    }
    
    // Check if slug already exists
    const slugExists = website.pages.some(page => page.slug === slug);
    if (slugExists) {
      return res.status(400).json({ success: false, message: 'Page slug already exists' });
    }
    
    // Create new page
    const newPage = {
      title,
      slug,
      content: content || {},
      meta: meta || {}
    };
    
    website.pages.push(newPage);
    website.updatedAt = Date.now();
    
    // Save website
    await website.save();
    
    res.status(201).json({
      success: true,
      page: newPage
    });
  } catch (error) {
    console.error('Create page error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Update page
// @route   PUT /api/websites/:id/pages/:pageId
// @access  Private
exports.updatePage = async (req, res) => {
  try {
    const { title, content, isPublished, meta } = req.body;
    
    // Find website
    const website = await Website.findById(req.params.id);
    
    if (!website) {
      return res.status(404).json({ success: false, message: 'Website not found' });
    }
    
    // Check if user owns the website
    if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to update this website' });
    }
    
    // Find page
    const pageIndex = website.pages.findIndex(page => page._id.toString() === req.params.pageId);
    
    if (pageIndex === -1) {
      return res.status(404).json({ success: false, message: 'Page not found' });
    }
    
    // Update page fields
    if (title) website.pages[pageIndex].title = title;
    if (content) website.pages[pageIndex].content = content;
    if (isPublished !== undefined) website.pages[pageIndex].isPublished = isPublished;
    if (meta) website.pages[pageIndex].meta = meta;
    
    website.pages[pageIndex].updatedAt = Date.now();
    website.updatedAt = Date.now();
    
    // Save website
    await website.save();
    
    res.status(200).json({
      success: true,
      page: website.pages[pageIndex]
    });
  } catch (error) {
    console.error('Update page error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Delete page
// @route   DELETE /api/websites/:id/pages/:pageId
// @access  Private
exports.deletePage = async (req, res) => {
  try {
    // Find website
    const website = await Website.findById(req.params.id);
    
    if (!website) {
      return res.status(404).json({ success: false, message: 'Website not found' });
    }
    
    // Check if user owns the website
    if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to update this website' });
    }
    
    // Find page
    const pageIndex = website.pages.findIndex(page => page._id.toString() === req.params.pageId);
    
    if (pageIndex === -1) {
      return res.status(404).json({ success: false, message: 'Page not found' });
    }
    
    // Don't allow deleting the home page
    if (website.pages[pageIndex].slug === 'home') {
      return res.status(400).json({ success: false, message: 'Cannot delete the home page' });
    }
    
    // Remove page
    website.pages.splice(pageIndex, 1);
    website.updatedAt = Date.now();
    
    // Save website
    await website.save();
    
    res.status(200).json({
      success: true,
      message: 'Page deleted successfully'
    });
  } catch (error) {
    console.error('Delete page error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Publish website
// @route   PUT /api/websites/:id/publish
// @access  Private
exports.publishWebsite = async (req, res) => {
  try {
    // Find website
    const website = await Website.findById(req.params.id);
    
    if (!website) {
      return res.status(404).json({ success: false, message: 'Website not found' });
    }
    
    // Check if user owns the website
    if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to publish this website' });
    }
    
    // Update website
    website.isPublished = true;
    website.updatedAt = Date.now();
    
    // Save website
    await website.save();
    
    res.status(200).json({
      success: true,
      message: 'Website published successfully',
      website
    });
  } catch (error) {
    console.error('Publish website error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};

// @desc    Unpublish website
// @route   PUT /api/websites/:id/unpublish
// @access  Private
exports.unpublishWebsite = async (req, res) => {
  try {
    // Find website
    const website = await Website.findById(req.params.id);
    
    if (!website) {
      return res.status(404).json({ success: false, message: 'Website not found' });
    }
    
    // Check if user owns the website
    if (website.user.toString() !== req.user._id.toString() && req.user.role !== 'admin') {
      return res.status(403).json({ success: false, message: 'Not authorized to unpublish this website' });
    }
    
    // Update website
    website.isPublished = false;
    website.updatedAt = Date.now();
    
    // Save website
    await website.save();
    
    res.status(200).json({
      success: true,
      message: 'Website unpublished successfully',
      website
    });
  } catch (error) {
    console.error('Unpublish website error:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
};