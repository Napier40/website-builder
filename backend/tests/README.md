# Website Builder Test System

This directory contains the test suite for the Website Builder application. The tests are organized into different categories to ensure comprehensive coverage of the application's functionality.

## Test Structure

- **Unit Tests**: Test individual components in isolation
  - `tests/unit/models`: Test database models
  - `tests/unit/controllers`: Test controller functions
  - `tests/unit/middleware`: Test middleware functions
  - `tests/unit/services`: Test service functions

- **Integration Tests**: Test the interaction between components
  - `tests/integration`: Test API endpoints and their interactions with the database

- **End-to-End Tests**: Test the complete application flow
  - `tests/e2e`: Test full user journeys through the application

## Running Tests

You can run the tests using the following npm scripts:

```bash
# Run all tests
npm test

# Run tests in watch mode (useful during development)
npm run test:watch

# Run tests with coverage report
npm run test:coverage

# Run only unit tests
npm run test:unit

# Run only integration tests
npm run test:integration

# Run only end-to-end tests
npm run test:e2e
```

## Test Configuration

- **Jest**: The test runner and assertion library
- **Supertest**: For testing HTTP endpoints
- **MongoDB Memory Server**: For running tests against an in-memory MongoDB instance

## Writing Tests

### Unit Tests

Unit tests should focus on testing a single function or component in isolation. Dependencies should be mocked.

Example:

```javascript
describe('User Model', () => {
  it('should hash the password before saving', async () => {
    const user = new User({
      name: 'Test User',
      email: 'test@example.com',
      password: 'password123'
    });
    
    await user.save();
    
    expect(user.password).not.toBe('password123');
    expect(user.password).toHaveLength(60); // bcrypt hash length
  });
});
```

### Integration Tests

Integration tests should focus on testing the interaction between components, such as API endpoints and the database.

Example:

```javascript
describe('Auth API', () => {
  it('should register a new user', async () => {
    const res = await request(app)
      .post('/api/auth/register')
      .send({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
    
    expect(res.statusCode).toBe(201);
    expect(res.body.success).toBe(true);
    expect(res.body.token).toBeDefined();
  });
});
```

### End-to-End Tests

End-to-end tests should focus on testing complete user journeys through the application.

Example:

```javascript
describe('User Journey', () => {
  it('should allow a user to register, create a website, and publish it', async () => {
    // Register user
    const registerRes = await request(app)
      .post('/api/auth/register')
      .send({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
    
    const token = registerRes.body.token;
    
    // Create website
    const websiteRes = await request(app)
      .post('/api/websites')
      .set('Authorization', `Bearer ${token}`)
      .send({
        name: 'My Website',
        subdomain: 'my-website',
        template: 'default'
      });
    
    const websiteId = websiteRes.body.website._id;
    
    // Publish website
    const publishRes = await request(app)
      .put(`/api/websites/${websiteId}/publish`)
      .set('Authorization', `Bearer ${token}`);
    
    expect(publishRes.statusCode).toBe(200);
    expect(publishRes.body.website.isPublished).toBe(true);
  });
});
```

## Test Coverage

The test coverage report can be generated using the `npm run test:coverage` command. This will create a coverage report in the `coverage` directory.

## API Testing with REST Client

You can also test the API endpoints manually using the REST Client extension for VS Code. The `api-tests.http` file contains sample requests for testing the API endpoints.

## Continuous Integration

The tests are automatically run in the CI/CD pipeline to ensure that all changes pass the tests before being deployed to production.