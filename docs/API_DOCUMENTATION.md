# Website Builder API Documentation

This document provides information about the API endpoints available in the Website Builder application.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:5000/api
```

## Authentication

Most endpoints require authentication. To authenticate, include a JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

You can obtain a token by registering or logging in.

## Endpoints

### Authentication

#### Register a new user

- **URL**: `/auth/register`
- **Method**: `POST`
- **Auth required**: No
- **Request body**:
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "success": true,
    "user": {
      "_id": "user_id",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "subscriptionStatus": "none"
    },
    "token": "jwt_token"
  }
  ```

#### Login

- **URL**: `/auth/login`
- **Method**: `POST`
- **Auth required**: No
- **Request body**:
  ```json
  {
    "email": "john@example.com",
    "password": "password123"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "user": {
      "_id": "user_id",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "subscriptionStatus": "none"
    },
    "token": "jwt_token"
  }
  ```

#### Get current user

- **URL**: `/auth/me`
- **Method**: `GET`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "user": {
      "_id": "user_id",
      "name": "John Doe",
      "email": "john@example.com",
      "role": "user",
      "subscriptionStatus": "none"
    }
  }
  ```

#### Update profile

- **URL**: `/auth/profile`
- **Method**: `PUT`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "name": "John Smith",
    "email": "john.smith@example.com"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "user": {
      "_id": "user_id",
      "name": "John Smith",
      "email": "john.smith@example.com",
      "role": "user",
      "subscriptionStatus": "none"
    }
  }
  ```

#### Change password

- **URL**: `/auth/change-password`
- **Method**: `PUT`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "currentPassword": "password123",
    "newPassword": "newpassword123"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "message": "Password updated successfully"
  }
  ```

### Subscriptions

#### Get all subscription plans

- **URL**: `/subscriptions`
- **Method**: `GET`
- **Auth required**: No
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "count": 3,
    "subscriptions": [
      {
        "_id": "subscription_id",
        "name": "basic",
        "price": 9.99,
        "features": ["Feature 1", "Feature 2"],
        "websiteLimit": 1,
        "storageLimit": 5000,
        "customDomain": false,
        "analytics": false,
        "ecommerce": false
      },
      // More subscription plans...
    ]
  }
  ```

#### Get subscription by ID

- **URL**: `/subscriptions/:id`
- **Method**: `GET`
- **Auth required**: No
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "subscription": {
      "_id": "subscription_id",
      "name": "basic",
      "price": 9.99,
      "features": ["Feature 1", "Feature 2"],
      "websiteLimit": 1,
      "storageLimit": 5000,
      "customDomain": false,
      "analytics": false,
      "ecommerce": false
    }
  }
  ```

#### Subscribe to a plan

- **URL**: `/subscriptions/subscribe`
- **Method**: `POST`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "subscriptionId": "subscription_id",
    "paymentMethodId": "payment_method_id"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "clientSecret": "client_secret",
    "subscriptionId": "stripe_subscription_id"
  }
  ```

#### Cancel subscription

- **URL**: `/subscriptions/cancel`
- **Method**: `POST`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "message": "Subscription cancelled successfully"
  }
  ```

#### Get user subscription

- **URL**: `/subscriptions/my-subscription`
- **Method**: `GET`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "hasSubscription": true,
    "subscription": {
      "id": "subscription_id",
      "name": "basic",
      "price": 9.99,
      "features": ["Feature 1", "Feature 2"],
      "websiteLimit": 1,
      "storageLimit": 5000,
      "customDomain": false,
      "analytics": false,
      "ecommerce": false
    },
    "stripeDetails": {
      "status": "active",
      "currentPeriodEnd": "2023-12-31T23:59:59.000Z",
      "cancelAtPeriodEnd": false
    }
  }
  ```

### Websites

#### Get all user websites

- **URL**: `/websites`
- **Method**: `GET`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "count": 2,
    "websites": [
      {
        "_id": "website_id",
        "name": "My Website",
        "subdomain": "my-website",
        "customDomain": null,
        "user": "user_id",
        "template": "default",
        "pages": [
          {
            "_id": "page_id",
            "title": "Home",
            "slug": "home",
            "content": {},
            "isPublished": true
          }
        ],
        "isPublished": true,
        "createdAt": "2023-01-01T00:00:00.000Z",
        "updatedAt": "2023-01-01T00:00:00.000Z"
      },
      // More websites...
    ]
  }
  ```

#### Get website by ID

- **URL**: `/websites/:id`
- **Method**: `GET`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "website": {
      "_id": "website_id",
      "name": "My Website",
      "subdomain": "my-website",
      "customDomain": null,
      "user": "user_id",
      "template": "default",
      "pages": [
        {
          "_id": "page_id",
          "title": "Home",
          "slug": "home",
          "content": {},
          "isPublished": true
        }
      ],
      "isPublished": true,
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Create website

- **URL**: `/websites`
- **Method**: `POST`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "name": "My New Website",
    "subdomain": "my-new-website",
    "template": "default"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "success": true,
    "website": {
      "_id": "website_id",
      "name": "My New Website",
      "subdomain": "my-new-website",
      "customDomain": null,
      "user": "user_id",
      "template": "default",
      "pages": [
        {
          "_id": "page_id",
          "title": "Home",
          "slug": "home",
          "content": {},
          "isPublished": true
        }
      ],
      "isPublished": false,
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Update website

- **URL**: `/websites/:id`
- **Method**: `PUT`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "name": "Updated Website Name",
    "customDomain": "example.com",
    "template": "business",
    "settings": {
      "theme": {
        "primaryColor": "#ff0000",
        "secondaryColor": "#00ff00"
      }
    }
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "website": {
      "_id": "website_id",
      "name": "Updated Website Name",
      "subdomain": "my-new-website",
      "customDomain": "example.com",
      "user": "user_id",
      "template": "business",
      "pages": [
        {
          "_id": "page_id",
          "title": "Home",
          "slug": "home",
          "content": {},
          "isPublished": true
        }
      ],
      "settings": {
        "theme": {
          "primaryColor": "#ff0000",
          "secondaryColor": "#00ff00",
          "fontFamily": "Arial, sans-serif",
          "fontSize": "16px"
        }
      },
      "isPublished": false,
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Delete website

- **URL**: `/websites/:id`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "message": "Website deleted successfully"
  }
  ```

#### Create page

- **URL**: `/websites/:id/pages`
- **Method**: `POST`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "title": "About Us",
    "slug": "about",
    "content": {
      "sections": [
        {
          "type": "text",
          "heading": "About Our Company",
          "content": "This is the about page content."
        }
      ]
    },
    "meta": {
      "description": "About our company",
      "keywords": "about, company"
    }
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "success": true,
    "page": {
      "_id": "page_id",
      "title": "About Us",
      "slug": "about",
      "content": {
        "sections": [
          {
            "type": "text",
            "heading": "About Our Company",
            "content": "This is the about page content."
          }
        ]
      },
      "meta": {
        "description": "About our company",
        "keywords": "about, company"
      },
      "isPublished": false,
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Update page

- **URL**: `/websites/:id/pages/:pageId`
- **Method**: `PUT`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "title": "Updated About Us",
    "content": {
      "sections": [
        {
          "type": "text",
          "heading": "About Our Company",
          "content": "This is the updated about page content."
        }
      ]
    },
    "isPublished": true,
    "meta": {
      "description": "Updated about our company",
      "keywords": "about, company, updated"
    }
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "page": {
      "_id": "page_id",
      "title": "Updated About Us",
      "slug": "about",
      "content": {
        "sections": [
          {
            "type": "text",
            "heading": "About Our Company",
            "content": "This is the updated about page content."
          }
        ]
      },
      "meta": {
        "description": "Updated about our company",
        "keywords": "about, company, updated"
      },
      "isPublished": true,
      "createdAt": "2023-01-01T00:00:00.000Z",
      "updatedAt": "2023-01-01T00:00:00.000Z"
    }
  }
  ```

#### Delete page

- **URL**: `/websites/:id/pages/:pageId`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "message": "Page deleted successfully"
  }
  ```

#### Publish website

- **URL**: `/websites/:id/publish`
- **Method**: `PUT`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "message": "Website published successfully",
    "website": {
      "_id": "website_id",
      "name": "My Website",
      "isPublished": true,
      // Other website properties...
    }
  }
  ```

#### Unpublish website

- **URL**: `/websites/:id/unpublish`
- **Method**: `PUT`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "message": "Website unpublished successfully",
    "website": {
      "_id": "website_id",
      "name": "My Website",
      "isPublished": false,
      // Other website properties...
    }
  }
  ```

### Payments

#### Create payment intent

- **URL**: `/payments/create-payment-intent`
- **Method**: `POST`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "subscriptionId": "subscription_id"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "clientSecret": "client_secret"
  }
  ```

#### Get payment methods

- **URL**: `/payments/payment-methods`
- **Method**: `GET`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "paymentMethods": [
      {
        "id": "payment_method_id",
        "card": {
          "brand": "visa",
          "last4": "4242",
          "exp_month": 12,
          "exp_year": 2025
        }
      },
      // More payment methods...
    ]
  }
  ```

#### Add payment method

- **URL**: `/payments/payment-methods`
- **Method**: `POST`
- **Auth required**: Yes
- **Request body**:
  ```json
  {
    "paymentMethodId": "payment_method_id"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "message": "Payment method added successfully"
  }
  ```

#### Delete payment method

- **URL**: `/payments/payment-methods/:id`
- **Method**: `DELETE`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "message": "Payment method deleted successfully"
  }
  ```

#### Get payment history

- **URL**: `/payments/history`
- **Method**: `GET`
- **Auth required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "success": true,
    "count": 2,
    "payments": [
      {
        "_id": "payment_id",
        "user": "user_id",
        "subscription": {
          "_id": "subscription_id",
          "name": "basic",
          "price": 9.99
        },
        "amount": 9.99,
        "currency": "usd",
        "status": "completed",
        "paymentMethod": "card",
        "createdAt": "2023-01-01T00:00:00.000Z"
      },
      // More payments...
    ]
  }
  ```

## Error Responses

All endpoints can return the following error responses:

- **400 Bad Request**: Invalid request parameters
  ```json
  {
    "success": false,
    "message": "Error message describing the issue"
  }
  ```

- **401 Unauthorized**: Authentication required or invalid token
  ```json
  {
    "success": false,
    "message": "Not authorized to access this route"
  }
  ```

- **403 Forbidden**: Insufficient permissions
  ```json
  {
    "success": false,
    "message": "User role not authorized to access this route"
  }
  ```

- **404 Not Found**: Resource not found
  ```json
  {
    "success": false,
    "message": "Resource not found"
  }
  ```

- **500 Server Error**: Internal server error
  ```json
  {
    "success": false,
    "message": "Server error"
  }
  ```