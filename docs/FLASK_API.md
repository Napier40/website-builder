# Website Builder - Flask API Documentation

**Version:** 3.0.0 (Python Flask + SQLite)  
**Base URL:** `http://localhost:5000/api`  
**Authentication:** JWT Bearer Token  
**Database:** SQLite (via SQLAlchemy 2.0)

---

## Table of Contents
1. [Authentication](#authentication)
2. [Users](#users)
3. [Websites](#websites)
4. [Subscriptions](#subscriptions)
5. [Payments](#payments)
6. [Templates](#templates)
7. [Admin](#admin)
8. [Plugins](#plugins)
9. [Error Responses](#error-responses)

---

## Authentication

All protected routes require the `Authorization: Bearer <token>` header.

> **Note:** IDs are integers (SQLite auto-increment), not MongoDB ObjectIds.

---

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
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "subscriptionType": "free",
    "subscriptionStatus": "active",
    "createdAt": "2025-01-15T10:30:00"
  }
}
```

**Errors:**
- `400` — Missing required fields, invalid email, password too short (<8 chars)
- `409` — Email already registered

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
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "subscriptionType": "free",
    "subscriptionStatus": "active"
  }
}
```

**Errors:**
- `400` — Missing fields
- `401` — Invalid email or password

---

### GET /api/auth/me *(Private)*
Get the current authenticated user's profile.

**Response 200:**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "subscriptionType": "free",
    "subscriptionStatus": "active",
    "stripeCustomerId": null,
    "createdAt": "2025-01-15T10:30:00",
    "updatedAt": "2025-01-15T10:30:00"
  }
}
```

---

### PUT /api/auth/me *(Private)*
Update the current user's profile.

**Body (all fields optional):**
```json
{
  "name": "Jane Doe"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Profile updated",
  "user": { ... }
}
```

---

### PUT /api/auth/me/password *(Private)*
Change the current user's password.

**Body:**
```json
{
  "currentPassword": "OldPass123",
  "newPassword": "NewPass456"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

**Errors:**
- `400` — New password too short, missing fields
- `401` — Current password incorrect

---

## Users

### GET /api/users/profile *(Private)*
Alias for `GET /api/auth/me`.

### PUT /api/users/profile *(Private)*
Alias for `PUT /api/auth/me`.

---

## Websites

### GET /api/websites *(Private)*
List the current user's websites (paginated).

**Query params:** `page` (default 1), `limit` (default 10)

**Response 200:**
```json
{
  "success": true,
  "websites": [
    {
      "id": 1,
      "name": "My Portfolio",
      "subdomain": "my-portfolio",
      "customDomain": null,
      "userId": 1,
      "template": "blank",
      "isPublished": false,
      "moderationStatus": "pending",
      "description": null,
      "pages": [
        {
          "id": 1,
          "title": "Home",
          "slug": "home",
          "content": "<h1>Welcome to my website</h1>",
          "order": 0,
          "createdAt": "2025-01-15T10:30:00",
          "updatedAt": "2025-01-15T10:30:00"
        }
      ],
      "adminOverride": null,
      "createdAt": "2025-01-15T10:30:00",
      "updatedAt": "2025-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

---

### POST /api/websites *(Private)*
Create a new website. Free plan users are limited to 1 website.

**Body:**
```json
{
  "name": "My Portfolio",
  "subdomain": "my-portfolio",
  "template": "blank"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Website created successfully",
  "website": { ... }
}
```

**Errors:**
- `400` — Missing name/subdomain, invalid subdomain format
- `409` — Subdomain already taken
- `403` — Website limit reached for current plan

**Subdomain rules:** 3–50 characters, lowercase letters, digits, hyphens only. No leading/trailing hyphens.

---

### GET /api/websites/:id *(Private)*
Get a single website by integer ID.

**Response 200:**
```json
{
  "success": true,
  "website": { ... }
}
```

**Errors:**
- `404` — Website not found
- `403` — Not the owner (non-admins)

---

### PUT /api/websites/:id *(Private)*
Update website metadata.

**Body (all optional):**
```json
{
  "name": "Updated Name",
  "description": "My updated description",
  "customDomain": "www.mysite.com"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Website updated",
  "website": { ... }
}
```

---

### DELETE /api/websites/:id *(Private)*
Delete a website and all its pages.

**Response 200:**
```json
{
  "success": true,
  "message": "Website deleted"
}
```

---

### PUT /api/websites/:id/publish *(Private)*
Publish a website.

**Response 200:**
```json
{
  "success": true,
  "message": "Website published",
  "website": { ... }
}
```

---

### PUT /api/websites/:id/unpublish *(Private)*
Unpublish a website.

**Response 200:**
```json
{
  "success": true,
  "message": "Website unpublished",
  "website": { ... }
}
```

---

### POST /api/websites/:id/pages *(Private)*
Add a new page to a website.

**Body:**
```json
{
  "title": "About",
  "slug": "about",
  "content": "<h1>About Me</h1>"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Page added",
  "page": {
    "id": 2,
    "title": "About",
    "slug": "about",
    "content": "<h1>About Me</h1>",
    "order": 1,
    "createdAt": "2025-01-15T11:00:00",
    "updatedAt": "2025-01-15T11:00:00"
  }
}
```

---

### PUT /api/websites/:id/pages/:page_id *(Private)*
Update an existing page.

**Body (all optional):**
```json
{
  "title": "About Us",
  "slug": "about-us",
  "content": "<h1>About Us</h1>",
  "order": 2
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Page updated",
  "page": { ... }
}
```

---

### DELETE /api/websites/:id/pages/:page_id *(Private)*
Delete a page from a website.

**Response 200:**
```json
{
  "success": true,
  "message": "Page deleted"
}
```

---

## Subscriptions

### GET /api/subscriptions
List all available subscription plans (public).

**Response 200:**
```json
{
  "success": true,
  "subscriptions": [
    {
      "id": 1,
      "name": "free",
      "displayName": "Free",
      "price": 0.0,
      "currency": "usd",
      "interval": "month",
      "features": ["1 website", "Basic templates", "Subdomain hosting"],
      "maxWebsites": 1,
      "hasCustomDomain": false,
      "isActive": true
    },
    {
      "id": 2,
      "name": "basic",
      "displayName": "Basic",
      "price": 9.99,
      "currency": "usd",
      "interval": "month",
      "features": ["3 websites", "All templates", "Subdomain hosting", "Email support"],
      "maxWebsites": 3,
      "hasCustomDomain": false,
      "isActive": true
    },
    {
      "id": 3,
      "name": "premium",
      "displayName": "Premium",
      "price": 29.99,
      "currency": "usd",
      "interval": "month",
      "features": ["10 websites", "All templates", "Custom domains", "Priority support", "Analytics"],
      "maxWebsites": 10,
      "hasCustomDomain": true,
      "isActive": true
    },
    {
      "id": 4,
      "name": "enterprise",
      "displayName": "Enterprise",
      "price": 99.99,
      "currency": "usd",
      "interval": "month",
      "features": ["Unlimited websites", "All templates", "Custom domains", "Dedicated support", "Advanced analytics", "White labeling"],
      "maxWebsites": -1,
      "hasCustomDomain": true,
      "isActive": true
    }
  ]
}
```

---

### POST /api/subscriptions/subscribe *(Private)*
Subscribe the current user to a plan.

**Body:**
```json
{
  "plan": "premium",
  "paymentMethodId": "pm_card_visa"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Subscribed to premium plan",
  "subscription": {
    "type": "premium",
    "status": "active"
  }
}
```

---

### POST /api/subscriptions/cancel *(Private)*
Cancel the current user's subscription (reverts to free).

**Response 200:**
```json
{
  "success": true,
  "message": "Subscription cancelled"
}
```

---

## Payments

### POST /api/payments/intent *(Private)*
Create a Stripe PaymentIntent.

**Body:**
```json
{
  "amount": 2999,
  "currency": "usd"
}
```

**Response 200:**
```json
{
  "success": true,
  "clientSecret": "pi_3N...._secret_...",
  "paymentIntentId": "pi_3N...."
}
```

---

### GET /api/payments/history *(Private)*
Get the current user's payment history.

**Response 200:**
```json
{
  "success": true,
  "payments": [
    {
      "id": 1,
      "amount": 2999,
      "currency": "usd",
      "status": "succeeded",
      "stripePaymentIntentId": "pi_3N....",
      "description": "Premium plan subscription",
      "createdAt": "2025-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

---

### POST /api/payments/webhook
Stripe webhook endpoint (public, validated by Stripe signature).

**Headers:** `Stripe-Signature: ...`

---

## Templates

### GET /api/templates
List all available templates (public).

**Query params:** `category` (optional filter)

**Response 200:**
```json
{
  "success": true,
  "templates": [
    {
      "id": 1,
      "name": "blank",
      "displayName": "Blank",
      "description": "Start with a clean slate",
      "category": "basic",
      "thumbnail": null,
      "tags": ["minimal", "blank"],
      "isPremium": false,
      "isActive": true
    }
  ]
}
```

---

### GET /api/templates/:id
Get a single template by integer ID.

**Response 200:**
```json
{
  "success": true,
  "template": { ... }
}
```

---

## Admin

> All admin routes require `role: admin`.

### GET /api/admin/dashboard *(Admin)*
Get platform statistics.

**Response 200:**
```json
{
  "success": true,
  "stats": {
    "users": {
      "total": 150,
      "admins": 2
    },
    "websites": {
      "total": 320,
      "published": 180
    },
    "moderation": {
      "pending": 5
    },
    "subscriptions": {
      "free": 100,
      "basic": 30,
      "premium": 15,
      "enterprise": 5
    }
  }
}
```

---

### GET /api/admin/users *(Admin)*
List all users with search and pagination.

**Query params:** `page`, `limit`, `search`, `role`, `sort_by`, `sort_dir`

**Response 200:**
```json
{
  "success": true,
  "users": [ { ... }, { ... } ],
  "total": 150,
  "page": 1,
  "pages": 15
}
```

---

### GET /api/admin/users/:id *(Admin)*
Get a single user by integer ID.

**Response 200:**
```json
{
  "success": true,
  "user": { ... }
}
```

---

### PUT /api/admin/users/:id *(Admin)*
Update a user's role or subscription.

**Body (all optional):**
```json
{
  "role": "admin",
  "subscriptionType": "premium",
  "subscriptionStatus": "active"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "User updated",
  "user": { ... }
}
```

---

### DELETE /api/admin/users/:id *(Admin)*
Delete a user and all their data.

**Errors:**
- `400` — Cannot delete your own account

**Response 200:**
```json
{
  "success": true,
  "message": "User deleted"
}
```

---

### GET /api/admin/moderation *(Admin)*
Get the moderation queue.

**Query params:** `page`, `limit`, `status` (`pending` | `approved` | `rejected`)

**Response 200:**
```json
{
  "success": true,
  "reports": [
    {
      "id": 1,
      "contentId": "42",
      "contentModel": "website",
      "reporterId": 7,
      "reason": "Inappropriate content",
      "status": "pending",
      "reviewedBy": null,
      "reviewedAt": null,
      "reviewNotes": null,
      "createdAt": "2025-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

---

### POST /api/admin/moderation *(Private)*
Submit a moderation report (any authenticated user).

**Body:**
```json
{
  "contentId": 42,
  "contentModel": "website",
  "reason": "Spam or inappropriate content"
}
```

**Response 201:**
```json
{
  "success": true,
  "message": "Report submitted",
  "report": { ... }
}
```

---

### PUT /api/admin/moderation/:id *(Admin)*
Review a moderation report.

**Body:**
```json
{
  "status": "approved",
  "notes": "Content reviewed and approved"
}
```

**Valid statuses:** `approved`, `rejected`

**Response 200:**
```json
{
  "success": true,
  "message": "Moderation report reviewed",
  "report": { ... }
}
```

---

### PUT /api/admin/websites/:id/override *(Admin)*
Admin override on a website (approve and optionally update content).

**Body:**
```json
{
  "reason": "Content reviewed and approved by admin",
  "moderationStatus": "approved"
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Admin override applied",
  "website": { ... }
}
```

---

### DELETE /api/admin/websites/:id/content *(Admin)*
Remove a website's page content (content moderation action).

**Response 200:**
```json
{
  "success": true,
  "message": "Website content removed"
}
```

---

### GET /api/admin/audit-logs *(Admin)*
Get the audit log trail.

**Query params:** `page`, `limit`, `user_id`, `action`, `resource`

**Response 200:**
```json
{
  "success": true,
  "logs": [
    {
      "id": 1,
      "userId": 1,
      "action": "login",
      "resource": "auth",
      "resourceId": null,
      "details": {},
      "ipAddress": "127.0.0.1",
      "userAgent": "Mozilla/5.0 ...",
      "createdAt": "2025-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "pages": 1
}
```

---

## Plugins

### GET /api/plugins
List all available plugins (public).

**Response 200:**
```json
{
  "success": true,
  "plugins": [
    {
      "id": 1,
      "name": "seo-optimizer",
      "displayName": "SEO Optimizer",
      "description": "Optimize your website for search engines",
      "version": "1.0.0",
      "author": "Website Builder Team",
      "isActive": true,
      "isPremium": false
    }
  ]
}
```

---

### GET /api/plugins/:id
Get a single plugin by integer ID.

---

### POST /api/plugins *(Admin)*
Create a new plugin.

**Body:**
```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "description": "A custom plugin",
  "version": "1.0.0"
}
```

---

## Health Check

### GET /api/health
Public health check endpoint.

**Response 200:**
```json
{
  "status": "healthy",
  "database": {
    "engine": "SQLite",
    "status": "connected"
  },
  "version": "3.0.0"
}
```

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | OK |
| `201` | Created |
| `400` | Bad Request — validation error or missing fields |
| `401` | Unauthorized — missing or invalid JWT token |
| `403` | Forbidden — insufficient role or subscription |
| `404` | Not Found |
| `409` | Conflict — duplicate entry (email, subdomain) |
| `500` | Internal Server Error |

---

## Data Types

| Field | Type | Notes |
|-------|------|-------|
| `id` | integer | SQLite auto-increment primary key |
| `createdAt` / `updatedAt` | ISO 8601 string | UTC datetime, e.g. `"2025-01-15T10:30:00"` |
| `isPublished` | boolean | `true` / `false` |
| `price` | float | Subscription price in USD |
| `amount` | integer | Stripe amount in cents (e.g. `2999` = $29.99) |

---

## Database

The backend uses **SQLite** via **SQLAlchemy 2.0** and **Flask-SQLAlchemy 3.1**.

- **Development / Production:** `flask-backend/website_builder.db` (file-based, created automatically)
- **Testing:** In-memory SQLite (`sqlite:///:memory:`) — no file created, wiped after each test
- **No installation required** — SQLite is built into Python

Tables: `users`, `websites`, `pages`, `subscriptions`, `payments`, `audit_logs`, `moderation`, `plugins`, `templates`