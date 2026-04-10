const mongoose = require('mongoose');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config({ path: './.env.test' });

// Connect to test database before tests
beforeAll(async () => {
  await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/website-builder-test', {
    useNewUrlParser: true,
    useUnifiedTopology: true
  });
});

// Clear database between tests
afterEach(async () => {
  const collections = Object.keys(mongoose.connection.collections);
  for (const collectionName of collections) {
    const collection = mongoose.connection.collections[collectionName];
    await collection.deleteMany({});
  }
});

// Disconnect from database after tests
afterAll(async () => {
  await mongoose.connection.close();
});