const express = require('express');
const router = express.Router();
const { getUsers, getUserById, updateUser, deleteUser, getUserStats } = require('../controllers/userController');
const { protect, authorize } = require('../middleware/auth');

// All routes are protected and require admin role
router.use(protect);
router.use(authorize('admin'));

router.get('/', getUsers);
router.get('/stats', getUserStats);
router.get('/:id', getUserById);
router.put('/:id', updateUser);
router.delete('/:id', deleteUser);

module.exports = router;