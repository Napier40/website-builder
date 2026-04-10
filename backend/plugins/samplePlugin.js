/**
 * Sample Plugin for Website Builder
 * Demonstrates the plugin system capabilities
 */

// Plugin initialization
exports.init = async (settings) => {
  console.log('Sample plugin initialized with settings:', settings);
  return true;
};

// Plugin cleanup
exports.cleanup = async () => {
  console.log('Sample plugin cleanup');
  return true;
};

// Hook: beforeWebsiteCreate
exports.beforeWebsiteCreate = async (context, settings) => {
  console.log('Before website create hook called');
  
  // Example: Add a default page to all new websites
  if (context.body && !context.body.pages) {
    context.body.pages = [];
  }
  
  if (context.body && context.body.pages) {
    context.body.pages.push({
      title: 'Created by Plugin',
      slug: 'plugin-page',
      content: {
        sections: [
          {
            type: 'text',
            heading: 'This page was created by a plugin',
            content: 'This demonstrates the plugin system capabilities.'
          }
        ]
      },
      isPublished: true
    });
  }
  
  return context.body;
};

// Hook: afterWebsiteCreate
exports.afterWebsiteCreate = async (context, settings) => {
  console.log('After website create hook called');
  console.log(`Website created: ${context.result.name} (${context.result._id})`);
  
  // Example: You could send a notification, log to analytics, etc.
  return true;
};

// Hook: beforeWebsitePublish
exports.beforeWebsitePublish = async (context, settings) => {
  console.log('Before website publish hook called');
  
  // Example: Validate website content before publishing
  const website = context.website;
  
  // Check if website has at least one page
  if (!website.pages || website.pages.length === 0) {
    throw new Error('Website must have at least one page before publishing');
  }
  
  return true;
};

// Hook: contentFilter
exports.contentFilter = async (context, settings) => {
  console.log('Content filter hook called');
  
  // Example: Filter out inappropriate content
  if (!context.content) return context.content;
  
  // Simple example - in a real plugin you would use more sophisticated filtering
  const inappropriateWords = settings.inappropriateWords || ['badword1', 'badword2'];
  
  let filteredContent = context.content;
  
  inappropriateWords.forEach(word => {
    const regex = new RegExp(word, 'gi');
    filteredContent = filteredContent.replace(regex, '***');
  });
  
  return filteredContent;
};

// Hook: dashboardWidgets
exports.dashboardWidgets = async (context, settings) => {
  console.log('Dashboard widgets hook called');
  
  // Example: Add custom widgets to the dashboard
  return [
    {
      id: 'sample-plugin-widget',
      title: 'Sample Plugin Widget',
      type: 'info',
      content: 'This widget was added by the sample plugin',
      position: 'sidebar',
      order: 1
    }
  ];
};

// Hook: extendUserMenu
exports.extendUserMenu = async (context, settings) => {
  console.log('Extend user menu hook called');
  
  // Example: Add custom menu items
  return [
    {
      id: 'sample-plugin-menu-item',
      title: 'Plugin Feature',
      icon: 'puzzle-piece',
      link: '/plugin-feature',
      order: 100
    }
  ];
};