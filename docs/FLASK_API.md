# Website Builder - Flask API Documentation

**Version:** 2.0.0 (Python Flask)  
**Base URL:** `http://localhost:5000/api`  
**Authentication:** JWT Bearer Token

---

## Table of Contents
1. [Authentication](#authentication)
2. [Websites](#websites)
3. [Subscriptions](#subscriptions)
4. [Payments](#payments)
5. [Templates](#templates)
6. [Admin](#admin)
7. [Plugins](#plugins)
8. [Error Responses](#error-responses)

---

## Authentication

All protected routes require the `Authorization: Bearer <token>` header.

### POST /api/auth/register
Register a new user account.

**Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Account created successfully",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "_id": "64f1a2b3c4d5e6f7a8b9c0d1",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "subscriptionStatus": "none",
    "isActive": true
  }
}
```

---

### POST /api/auth/login
Authenticate and receive a JWT token.

**Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { ... }
}
```

---

### GET /api/auth/me *(Private)*
Get the current authenticated user's profile.

**Response 200:**
```json
{
  "success": true,
  "user": { ... }
}
```

---

### PUT /api/auth/profile *(Private)*
Update the current user's name or email.

**Body:**
```json
{
  "name": "Updated Name",
  "email": "newemail@example.com"
}
```

---

### PUT /api/auth/change-password *(Private)*
Change the current user's password.

**Body:**
```json
{
  "currentPassword": "OldPass123",
  "newPassword": "NewPass456"
}
```

---

## Websites

### GET /api/websites *(Private)*
Get all websites for the current user.

**Response 200:**
```json
{
  "success": true,
  "count": 2,
  "websites": [
    {
      "_id": "...",
      "name": "My Site",
      "subdomain": "my-site",
      "isPublished": false,
      "pages": [...],
      "settings": {...}
    }
  ]
}
```

---

### POST /api/websites *(Private)*
Create a new website.

**Body:**
```json
{
  "name": "My Awesome Site",
  "subdomain": "my-awesome-site",
  "template": "default"
}
```

**Subdomain rules:** 3-63 chars, lowercase letters/digits/hyphens only, cannot start/end with hyphen.

---

### GET /api/websites/:id *(Private)*
Get a specific website by ID. Must be the owner or admin.

---

### PUT /api/websites/:id *(Private)*
Update website name, domain, template, or settings.

**Body:**
```json
{
  "name": "New Name",
  "customDomain": "www.mysite.com",
  "settings": {
    "theme": {
      "primaryColor": "#e74c3c"
    }
  }
}
```

> ⚠️ Custom domains require **Premium** or **Enterprise** subscription.

---

### DELETE /api/websites/:id *(Private)*
Delete a website permanently.

---

### PUT /api/websites/:id/publish *(Private)*
Publish a website (make it live).

---

### PUT /api/websites/:id/unpublish *(Private)*
Unpublish a website.

---

### POST /api/websites/:id/pages *(Private)*
Add a new page to a website.

**Body:**
```json
{
  "title": "About Us",
  "slug": "about",
  "content": {
    "sections": [
      {
        "type": "hero",
        "heading": "About Us"
      }
    ]
  },
  "meta": {
    "description": "About our company",
    "keywords": "about, company"
  }
}
```

---

### PUT /api/websites/:id/pages/:pageId *(Private)*
Update an existing page.

---

### DELETE /api/websites/:id/pages/:pageId *(Private)*
Delete a page. The **home** page cannot be deleted.

---

## Subscriptions

### GET /api/subscriptions *(Public)*
Get all available subscription plans.

**Response 200:**
```json
{
  "success": true,
  "plans": [
    {
      "name": "basic",
      "displayName": "Basic",
      "price": 9.99,
      "currency": "usd",
      "websiteLimit": 3,
      "customDomain": false,
      "features": ["Up to 3 websites", "1GB storage", ...]
    }
  ]
}
```

---

### GET /api/subscriptions/current *(Private)*
Get the current user's active subscription.

---

### POST /api/subscriptions/subscribe *(Private)*
Subscribe to a plan via Stripe.

**Body:**
```json
{
  "planName": "basic",
  "paymentMethodId": "pm_card_visa"
}
```

---

### POST /api/subscriptions/cancel *(Private)*
Cancel the current user's active subscription.

---

## Payments

### POST /api/payments/intent *(Private)*
Create a Stripe PaymentIntent.

**Body:**
```json
{
  "amount": 9.99,
  "currency": "usd",
  "description": "Website Builder Basic Plan"
}
```

**Response 200:**
```json
{
  "success": true,
  "clientSecret": "pi_..._secret_...",
  "paymentId": "...",
  "intentId": "pi_..."
}
```

---

### GET /api/payments/history *(Private)*
Get the current user's payment history with pagination.

---

### POST /api/payments/webhook
Stripe webhook endpoint. Handles:
- `payment_intent.succeeded` → marks payment completed
- `payment_intent.payment_failed` → marks payment failed
- `customer.subscription.deleted` → resets user subscription to 'none'

---

## Templates

### GET /api/templates *(Public)*
Get all public templates.

**Query params:** `category`, `isPremium`, `search`, `page`, `limit`

---

### GET /api/templates/categories *(Public)*
Get list of all template categories.

---

### GET /api/templates/tags *(Public)*
Get list of all template tags.

---

### GET /api/templates/:id *(Public)*
Get a specific template.

---

### POST /api/templates *(Admin)*
Create a new template.

---

### PUT /api/templates/:id *(Admin)*
Update a template.

---

### DELETE /api/templates/:id *(Admin)*
Delete a template.

---

### POST /api/templates/save-from-website/:websiteId *(Private)*
Save a website as a reusable template.

---

### PUT /api/templates/:templateId/apply/:websiteId *(Private)*
Apply a template to a website.

---

## Admin

> All admin routes require `role: admin`.

### GET /api/admin/dashboard *(Admin)*
Get comprehensive platform statistics.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 150,
      "new30Days": 12,
      "subscriptions": [
        {"_id": "none", "count": 80},
        {"_id": "basic", "count": 45}
      ]
    },
    "websites": {"total": 320, "published": 180},
    "revenue": {"monthly": 1250.75},
    "moderation": [{"_id": "pending", "count": 3}]
  }
}
```

---

### GET /api/admin/users *(Admin)*
Get all users with filtering and pagination.

**Query params:** `search`, `role`, `subscriptionStatus`, `page`, `limit`, `sort`

---

### GET /api/admin/users/:id *(Admin)*
Get a user with their websites, payments, and audit logs.

---

### PUT /api/admin/users/:id *(Admin)*
Update any user field (role, subscriptionStatus, isActive, name, email).

---

### DELETE /api/admin/users/:id *(Admin)*
Delete a user account permanently.

---

### GET /api/admin/moderation *(Admin)*
Get the content moderation queue.

**Query params:** `status` (pending/approved/rejected), `contentModel`, `page`, `limit`

---

### POST /api/admin/moderation *(Admin)*
Flag content for moderation.

**Body:**
```json
{
  "contentId": "website-id-here",
  "contentModel": "Website",
  "reason": "Contains inappropriate content"
}
```

---

### PUT /api/admin/moderation/:id *(Admin)*
Process a moderation item (approve or reject).

**Body:**
```json
{
  "status": "rejected",
  "reason": "Violates terms of service",
  "action": "content_removal",
  "modifiedContent": null
}
```

---

### PUT /api/admin/websites/:id/override *(Admin)*
Override a website's page content directly.

**Body:**
```json
{
  "content": [
    {
      "title": "Home",
      "slug": "home",
      "content": {"sections": [...]},
      "isPublished": true,
      "meta": {}
    }
  ],
  "reason": "Removed TOS-violating content"
}
```

---

### DELETE /api/admin/websites/:id/delete-content *(Admin)*
Delete an entire website as admin action.

---

### GET /api/admin/audit-logs *(Admin)*
Get audit logs with filtering.

**Query params:** `user`, `action`, `resource`, `startDate`, `endDate`, `page`, `limit`

---

## Plugins

### GET /api/plugins *(Admin)*
Get all registered plugins.

---

### POST /api/plugins *(Admin)*
Register a new plugin.

---

### PUT /api/plugins/:id/toggle *(Admin)*
Activate or deactivate a plugin.

---

### GET /api/plugins/hooks *(Admin)*
Get all registered hooks and loaded plugins.

---

### POST /api/plugins/hooks/:hookName/execute *(Admin)*
Execute a specific plugin hook with data.

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "message": "Human-readable error description"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request - missing/invalid fields |
| 401 | Unauthorized - missing or invalid JWT |
| 403 | Forbidden - insufficient role or subscription |
| 404 | Not Found - resource doesn't exist |
| 500 | Internal Server Error |

---

## Subscription Limits

| Feature | Free | Basic ($9.99) | Premium ($29.99) | Enterprise ($99.99) |
|---------|------|---------------|------------------|---------------------|
| Websites | 1 | 3 | 10 | Unlimited |
| Storage | - | 1 GB | 10 GB | 100 GB |
| Custom Domain | ❌ | ❌ | ✅ | ✅ |
| Analytics | ❌ | ❌ | ✅ | ✅ |
| Priority Support | ❌ | ❌ | ❌ | ✅ |