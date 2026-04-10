# Website Builder - Administrator Guide

This guide provides instructions for administrators on how to manage the Website Builder platform, moderate content, and handle user issues.

## Table of Contents

1. [Accessing Admin Features](#accessing-admin-features)
2. [User Management](#user-management)
3. [Content Moderation](#content-moderation)
4. [Subscription Management](#subscription-management)
5. [Plugin Management](#plugin-management)
6. [Template Management](#template-management)
7. [System Monitoring](#system-monitoring)
8. [Audit Logs](#audit-logs)
9. [Common Administrative Tasks](#common-administrative-tasks)
10. [Troubleshooting](#troubleshooting)

## Accessing Admin Features

### Admin Dashboard

The admin dashboard is accessible only to users with the "admin" role. To access the admin dashboard:

1. Log in with an admin account
2. Navigate to `/admin` in the application
3. You will see the admin dashboard with various sections

### Creating Admin Accounts

To create an admin account:

1. Register a regular user account
2. Access the MongoDB database directly
3. Update the user's role to "admin":

```javascript
// In MongoDB shell or MongoDB Compass
db.users.updateOne(
  { email: "admin@example.com" },
  { $set: { role: "admin" } }
)
```

## User Management

### Viewing Users

1. In the admin dashboard, navigate to the "Users" section
2. You will see a list of all users with search and filter options
3. Click on a user to view their details

### Editing User Information

1. Click on a user in the user list
2. Click the "Edit" button
3. Update the user's information
4. Click "Save" to apply changes

### Managing User Roles

1. Click on a user in the user list
2. In the user details, change the "Role" dropdown
3. Select "user" or "admin"
4. Click "Save" to apply changes

### Managing User Subscriptions

1. Click on a user in the user list
2. In the user details, change the "Subscription" dropdown
3. Select the appropriate subscription level
4. Click "Save" to apply changes

### Suspending or Deleting Users

1. Click on a user in the user list
2. Click "Suspend" to temporarily disable the account, or
3. Click "Delete" to permanently remove the account
4. Confirm your action in the confirmation dialog

## Content Moderation

### Moderation Queue

1. Navigate to the "Moderation" section in the admin dashboard
2. You will see a list of content flagged for moderation
3. Filter by status: pending, approved, rejected, flagged

### Reviewing Content

1. Click on an item in the moderation queue
2. Review the content details
3. Choose an action:
   - Approve: Content is acceptable
   - Reject: Content violates terms
   - Edit: Modify the content to make it acceptable
   - Flag: Mark for further review

### Content Override

For immediate action on any content:

1. Navigate to the content directly (website, page, etc.)
2. Click the "Admin Override" button
3. Make necessary changes to the content
4. Provide a reason for the override
5. Click "Save" to apply changes

### Setting Up Automatic Content Filtering

1. Navigate to "Settings" > "Content Moderation"
2. Configure automatic filtering rules:
   - Keyword blacklist
   - Content categories to flag
   - User reputation thresholds
3. Click "Save" to apply changes

## Subscription Management

### Managing Subscription Plans

1. Navigate to "Subscriptions" > "Plans"
2. View existing subscription plans
3. To edit a plan, click on it and update details
4. To create a new plan, click "Add Plan"

### Viewing Subscription Analytics

1. Navigate to "Subscriptions" > "Analytics"
2. View subscription metrics:
   - Active subscriptions by plan
   - Conversion rates
   - Churn rates
   - Revenue

### Managing Payment Issues

1. Navigate to "Subscriptions" > "Payments"
2. View payment history and issues
3. Filter by status: completed, failed, refunded
4. Click on a payment to view details and take action

## Plugin Management

### Installing Plugins

1. Navigate to "Plugins" > "Browse"
2. Browse available plugins
3. Click "Install" on the plugin you want to add
4. Configure plugin settings if required

### Managing Plugins

1. Navigate to "Plugins" > "Installed"
2. View all installed plugins
3. Actions:
   - Activate/Deactivate: Toggle plugin status
   - Configure: Adjust plugin settings
   - Uninstall: Remove the plugin

### Creating Custom Plugins

1. Develop a plugin following the plugin API documentation
2. Navigate to "Plugins" > "Upload"
3. Upload your plugin file
4. Configure and activate the plugin

## Template Management

### Managing Templates

1. Navigate to "Templates" > "All Templates"
2. View all available templates
3. Filter by category, tags, or popularity
4. Click on a template to view details

### Creating Featured Templates

1. Navigate to "Templates" > "All Templates"
2. Click on a template
3. Toggle the "Featured" switch
4. Adjust the display order if needed

### Approving User Templates

1. Navigate to "Templates" > "Pending"
2. Review templates submitted by users
3. Click "Approve" or "Reject"
4. Provide feedback if rejecting

## System Monitoring

### Dashboard Overview

The admin dashboard provides key metrics:

- User statistics (total, new, active)
- Website statistics (total, published)
- Subscription statistics
- Revenue metrics
- System health indicators

### Performance Monitoring

1. Navigate to "System" > "Performance"
2. View system performance metrics:
   - Server load
   - Database performance
   - API response times
   - Error rates

### Error Logs

1. Navigate to "System" > "Logs"
2. View system error logs
3. Filter by severity, date, or component
4. Click on an error for details

## Audit Logs

### Viewing Audit Logs

1. Navigate to "System" > "Audit Logs"
2. View all system actions
3. Filter by:
   - User
   - Action type
   - Date range
   - Resource type

### Exporting Audit Logs

1. Navigate to "System" > "Audit Logs"
2. Apply desired filters
3. Click "Export" and choose format (CSV, JSON)

## Common Administrative Tasks

### Handling User Complaints

1. Navigate to "Support" > "Tickets"
2. Review user complaints
3. Investigate the issue using audit logs and content history
4. Take appropriate action
5. Respond to the user

### Managing Inappropriate Content

1. Review flagged content in the moderation queue
2. If content violates terms:
   - Remove the content
   - Notify the user
   - Apply appropriate sanctions if necessary
3. Document the action in the admin notes

### Resolving Payment Disputes

1. Navigate to "Subscriptions" > "Payments"
2. Locate the disputed payment
3. Review transaction details and user history
4. Process refund if appropriate
5. Contact the user with the resolution

## Troubleshooting

### Common Issues and Solutions

#### User Cannot Access Their Account
1. Check if the account is suspended
2. Verify email confirmation status
3. Check for payment issues if premium features are inaccessible

#### Content Not Publishing
1. Check moderation status
2. Verify user subscription allows publishing
3. Check for technical errors in the content

#### Payment Processing Failures
1. Check Stripe dashboard for detailed error
2. Verify payment method validity
3. Check for account restrictions

### Getting Support

For issues you cannot resolve:

1. Check the administrator documentation
2. Contact technical support with:
   - Detailed description of the issue
   - Relevant user IDs or content IDs
   - Steps to reproduce
   - Error messages or logs

---

This guide covers the basic administrative tasks for the Website Builder platform. For more detailed information, refer to the technical documentation or contact the development team.