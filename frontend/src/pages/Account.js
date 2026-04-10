import React, { useState, useContext, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import Modal from '../components/common/Modal';

const AccountContainer = styled.div`
  flex: 1;
  padding: 2rem;
`;

const AccountHeader = styled.div`
  margin-bottom: 2rem;
`;

const AccountTitle = styled.h1`
  margin: 0 0 1rem;
  font-size: 2rem;
`;

const AccountGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  
  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
`;

const PaymentMethodCard = styled.div`
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const CardInfo = styled.div`
  display: flex;
  align-items: center;
  
  i {
    font-size: 1.5rem;
    margin-right: 1rem;
    color: #666;
  }
`;

const CardDetails = styled.div`
  p {
    margin: 0;
    
    &:first-child {
      font-weight: 500;
    }
    
    &:last-child {
      font-size: 0.9rem;
      color: #666;
    }
  }
`;

const Account = () => {
  const { user, updateProfile, changePassword } = useContext(AuthContext);
  
  const [profileData, setProfileData] = useState({
    name: '',
    email: ''
  });
  
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(false);
  const [paymentLoading, setPaymentLoading] = useState(true);
  const [profileError, setProfileError] = useState(null);
  const [passwordError, setPasswordError] = useState(null);
  const [paymentError, setPaymentError] = useState(null);
  const [profileSuccess, setProfileSuccess] = useState(null);
  const [passwordSuccess, setPasswordSuccess] = useState(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deletePaymentId, setDeletePaymentId] = useState(null);
  
  useEffect(() => {
    if (user) {
      setProfileData({
        name: user.name,
        email: user.email
      });
    }
    
    fetchPaymentMethods();
  }, [user]);
  
  const fetchPaymentMethods = async () => {
    try {
      setPaymentLoading(true);
      const res = await axios.get('/api/payments/payment-methods');
      setPaymentMethods(res.data.paymentMethods);
      setPaymentLoading(false);
    } catch (err) {
      setPaymentError('Failed to load payment methods');
      setPaymentLoading(false);
    }
  };
  
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData({
      ...profileData,
      [name]: value
    });
  };
  
  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData({
      ...passwordData,
      [name]: value
    });
  };
  
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setProfileError(null);
    setProfileSuccess(null);
    
    const result = await updateProfile(profileData);
    
    if (result.success) {
      setProfileSuccess('Profile updated successfully');
    } else {
      setProfileError(result.error);
    }
    
    setLoading(false);
  };
  
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setPasswordError(null);
    setPasswordSuccess(null);
    
    // Validate passwords
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setPasswordError('Passwords do not match');
      setLoading(false);
      return;
    }
    
    if (passwordData.newPassword.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }
    
    const result = await changePassword({
      currentPassword: passwordData.currentPassword,
      newPassword: passwordData.newPassword
    });
    
    if (result.success) {
      setPasswordSuccess('Password changed successfully');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } else {
      setPasswordError(result.error);
    }
    
    setLoading(false);
  };
  
  const handleDeletePaymentMethod = (paymentMethodId) => {
    setDeletePaymentId(paymentMethodId);
    setIsDeleteModalOpen(true);
  };
  
  const confirmDeletePaymentMethod = async () => {
    try {
      await axios.delete(`/api/payments/payment-methods/${deletePaymentId}`);
      
      // Update payment methods list
      setPaymentMethods(paymentMethods.filter(method => method.id !== deletePaymentId));
      
      // Close modal
      setIsDeleteModalOpen(false);
      setDeletePaymentId(null);
    } catch (err) {
      setPaymentError('Failed to delete payment method');
    }
  };
  
  return (
    <AccountContainer>
      <AccountHeader>
        <AccountTitle>Account Settings</AccountTitle>
      </AccountHeader>
      
      <AccountGrid>
        <div>
          <Card title="Profile Information">
            {profileError && <Alert type="danger" message={profileError} onClose={() => setProfileError(null)} />}
            {profileSuccess && <Alert type="success" message={profileSuccess} onClose={() => setProfileSuccess(null)} />}
            
            <form onSubmit={handleProfileSubmit}>
              <FormGroup>
                <Label htmlFor="name">Full Name</Label>
                <Input
                  type="text"
                  id="name"
                  name="name"
                  value={profileData.name}
                  onChange={handleProfileChange}
                  placeholder="Your full name"
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="email">Email Address</Label>
                <Input
                  type="email"
                  id="email"
                  name="email"
                  value={profileData.email}
                  onChange={handleProfileChange}
                  placeholder="Your email address"
                  required
                />
              </FormGroup>
              
              <Button type="submit" variant="primary" disabled={loading}>
                {loading ? <Spinner size={20} /> : 'Update Profile'}
              </Button>
            </form>
          </Card>
          
          <Card title="Change Password" style={{ marginTop: '2rem' }}>
            {passwordError && <Alert type="danger" message={passwordError} onClose={() => setPasswordError(null)} />}
            {passwordSuccess && <Alert type="success" message={passwordSuccess} onClose={() => setPasswordSuccess(null)} />}
            
            <form onSubmit={handlePasswordSubmit}>
              <FormGroup>
                <Label htmlFor="currentPassword">Current Password</Label>
                <Input
                  type="password"
                  id="currentPassword"
                  name="currentPassword"
                  value={passwordData.currentPassword}
                  onChange={handlePasswordChange}
                  placeholder="Enter your current password"
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="newPassword">New Password</Label>
                <Input
                  type="password"
                  id="newPassword"
                  name="newPassword"
                  value={passwordData.newPassword}
                  onChange={handlePasswordChange}
                  placeholder="Enter your new password"
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <Input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={passwordData.confirmPassword}
                  onChange={handlePasswordChange}
                  placeholder="Confirm your new password"
                  required
                />
              </FormGroup>
              
              <Button type="submit" variant="primary" disabled={loading}>
                {loading ? <Spinner size={20} /> : 'Change Password'}
              </Button>
            </form>
          </Card>
        </div>
        
        <div>
          <Card title="Payment Methods">
            {paymentError && <Alert type="danger" message={paymentError} onClose={() => setPaymentError(null)} />}
            
            {paymentLoading ? (
              <Spinner />
            ) : paymentMethods.length === 0 ? (
              <div>
                <p>You don't have any payment methods saved.</p>
                <Button to="/subscriptions" variant="primary">
                  Add Payment Method
                </Button>
              </div>
            ) : (
              <>
                {paymentMethods.map(method => (
                  <PaymentMethodCard key={method.id}>
                    <CardInfo>
                      <i className={`fab fa-cc-${method.card.brand.toLowerCase()}`}></i>
                      <CardDetails>
                        <p>{method.card.brand} •••• {method.card.last4}</p>
                        <p>Expires {method.card.exp_month}/{method.card.exp_year}</p>
                      </CardDetails>
                    </CardInfo>
                    <Button 
                      variant="danger" 
                      size="small"
                      onClick={() => handleDeletePaymentMethod(method.id)}
                    >
                      Remove
                    </Button>
                  </PaymentMethodCard>
                ))}
                
                <Button to="/subscriptions" variant="outline">
                  Add New Payment Method
                </Button>
              </>
            )}
          </Card>
          
          <Card title="Danger Zone" style={{ marginTop: '2rem' }}>
            <p>Delete your account and all associated data.</p>
            <Button variant="danger">
              Delete Account
            </Button>
          </Card>
        </div>
      </AccountGrid>
      
      {/* Delete Payment Method Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Payment Method"
        size="small"
        footer={
          <>
            <Button variant="light" onClick={() => setIsDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={confirmDeletePaymentMethod}>
              Delete
            </Button>
          </>
        }
      >
        <p>Are you sure you want to delete this payment method?</p>
        <p>This action cannot be undone.</p>
      </Modal>
    </AccountContainer>
  );
};

export default Account;