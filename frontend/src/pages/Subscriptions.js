import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import axios from 'axios';

import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import Modal from '../components/common/Modal';

const SubscriptionsContainer = styled.div`
  flex: 1;
  padding: 2rem;
`;

const SubscriptionsHeader = styled.div`
  margin-bottom: 2rem;
`;

const SubscriptionsTitle = styled.h1`
  margin: 0 0 1rem;
  font-size: 2rem;
`;

const SubscriptionsSubtitle = styled.p`
  margin: 0;
  color: #666;
  font-size: 1.1rem;
`;

const CurrentSubscription = styled(Card)`
  margin-bottom: 2rem;
`;

const SubscriptionInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
`;

const SubscriptionDetails = styled.div`
  h3 {
    margin: 0 0 0.5rem;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
  }
  
  p {
    margin: 0;
    color: #666;
  }
`;

const SubscriptionBadge = styled.span`
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  background-color: ${props => {
    switch (props.type) {
      case 'basic':
        return '#3498db';
      case 'premium':
        return '#2ecc71';
      case 'enterprise':
        return '#9b59b6';
      default:
        return '#95a5a6';
    }
  }};
  color: #fff;
  margin-left: 0.5rem;
`;

const SubscriptionFeatures = styled.ul`
  list-style: none;
  padding: 0;
  margin: 1rem 0;
`;

const SubscriptionFeature = styled.li`
  padding: 0.5rem 0;
  display: flex;
  align-items: center;
  
  &:before {
    content: '✓';
    color: var(--success-color);
    margin-right: 0.5rem;
    font-weight: bold;
  }
`;

const PlansGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  margin-top: 2rem;
  
  @media (max-width: 992px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const PlanCard = styled(Card)`
  border: ${props => props.popular ? '2px solid var(--primary-color)' : '1px solid #eee'};
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const PopularBadge = styled.div`
  position: absolute;
  top: -12px;
  right: 20px;
  background-color: var(--primary-color);
  color: #fff;
  padding: 0.25rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
`;

const PlanTitle = styled.h3`
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
`;

const PlanPrice = styled.div`
  font-size: 2.5rem;
  font-weight: bold;
  margin: 1.5rem 0;
  
  span {
    font-size: 1rem;
    font-weight: normal;
    color: #666;
  }
`;

const PlanFeatures = styled.ul`
  list-style: none;
  padding: 0;
  margin: 2rem 0;
  text-align: left;
  flex: 1;
`;

const PlanFeature = styled.li`
  padding: 0.5rem 0;
  display: flex;
  align-items: center;
  
  &:before {
    content: '✓';
    color: var(--success-color);
    margin-right: 0.5rem;
    font-weight: bold;
  }
`;

const PaymentHistoryTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  
  th, td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }
  
  th {
    background-color: #f8f9fa;
    font-weight: 500;
  }
  
  tr:hover {
    background-color: #f8f9fa;
  }
`;

const Subscriptions = () => {
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  
  
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchSubscriptionData();
  }, []);
  
  const fetchSubscriptionData = async () => {
    try {
      setLoading(true);
      
      // Fetch subscription plans
      const plansRes = await axios.get('/api/subscriptions');
      setSubscriptionPlans(plansRes.data.data?.plans || []);
      
      // Fetch current subscription
      const currentSubRes = await axios.get('/api/subscriptions/current');
      setCurrentSubscription(currentSubRes.data.data);
      
      // Fetch payment history (paginated: data is the array itself)
      const paymentsRes = await axios.get('/api/payments/history');
      setPaymentHistory(Array.isArray(paymentsRes.data.data) ? paymentsRes.data.data : []);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load subscription data');
      setLoading(false);
    }
  };
  
  const handleSubscribe = (subscriptionId) => {
    navigate(`/checkout/${subscriptionId}`);
  };
  
  const handleCancelSubscription = async () => {
    try {
      await axios.post('/api/subscriptions/cancel');
      
      // Update current subscription
      setCurrentSubscription({
        hasSubscription: false,
        message: 'No active subscription'
      });
      
      // Close modal
      setIsCancelModalOpen(false);
    } catch (err) {
      setError('Failed to cancel subscription');
    }
  };
  
  if (loading) {
    return <Spinner fullPage />;
  }
  
  return (
    <SubscriptionsContainer>
      <SubscriptionsHeader>
        <SubscriptionsTitle>Subscription Plans</SubscriptionsTitle>
        <SubscriptionsSubtitle>
          Choose the perfect plan for your website building needs
        </SubscriptionsSubtitle>
      </SubscriptionsHeader>
      
      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      
      {/* Current Subscription */}
      <CurrentSubscription>
        <h2>Current Plan</h2>
        
        {currentSubscription?.hasSubscription ? (
          <>
            <SubscriptionInfo>
              <SubscriptionDetails>
                <h3>
                  {currentSubscription.plan?.displayName || currentSubscription.subscriptionType} Plan
                  <SubscriptionBadge type={currentSubscription.subscriptionType}>
                    Active
                  </SubscriptionBadge>
                </h3>
                <p>
                  {currentSubscription.maxWebsites === -1 ? 'Unlimited' : currentSubscription.maxWebsites} websites allowed
                </p>
              </SubscriptionDetails>
              
              <Button 
                variant="danger" 
                onClick={() => setIsCancelModalOpen(true)}
              >
                Cancel Subscription
              </Button>
            </SubscriptionInfo>
            
            <SubscriptionFeatures>
              <SubscriptionFeature>
                {currentSubscription.maxWebsites === -1 ? 'Unlimited' : currentSubscription.maxWebsites} Website{currentSubscription.maxWebsites !== 1 ? 's' : ''}
              </SubscriptionFeature>
              {currentSubscription.plan?.features?.map((feature, i) => (
                <SubscriptionFeature key={i}>{feature}</SubscriptionFeature>
              ))}
            </SubscriptionFeatures>
          </>
        ) : (
          <SubscriptionInfo>
            <SubscriptionDetails>
              <h3>
                Free Plan
                <SubscriptionBadge type="none">
                  Active
                </SubscriptionBadge>
              </h3>
              <p>Upgrade to create more websites and access premium features</p>
            </SubscriptionDetails>
          </SubscriptionInfo>
        )}
      </CurrentSubscription>
      
      {/* Available Plans */}
      <h2>Available Plans</h2>
      <PlansGrid>
        {subscriptionPlans.map(plan => (
          <PlanCard 
            key={plan.id} 
            popular={plan.name === 'premium'}
          >
            {plan.name === 'premium' && <PopularBadge>Most Popular</PopularBadge>}
            <PlanTitle>
              {plan.name.charAt(0).toUpperCase() + plan.name.slice(1)} Plan
            </PlanTitle>
            <PlanPrice>
              ${plan.price} <span>/month</span>
            </PlanPrice>
            <PlanFeatures>
              <PlanFeature>{plan.maxWebsites === -1 ? 'Unlimited' : plan.maxWebsites} Website{plan.maxWebsites !== 1 ? 's' : ''}</PlanFeature>
              
              <PlanFeature>Free SSL Certificate</PlanFeature>
              <PlanFeature>Mobile Responsive</PlanFeature>
              {plan.features?.map((f, i) => <PlanFeature key={i}>{f}</PlanFeature>)}
              {plan.name === 'enterprise' && <PlanFeature>Priority Support</PlanFeature>}
            </PlanFeatures>
            <Button 
              variant={currentSubscription?.subscriptionType === plan.name ? 'light' : 'primary'} 
              block
              disabled={currentSubscription?.subscriptionType === plan.name}
              onClick={() => handleSubscribe(plan.id)}
            >
              {currentSubscription?.subscriptionType === plan.name ? 'Current Plan' : 'Select Plan'}
            </Button>
          </PlanCard>
        ))}
      </PlansGrid>
      
      {/* Payment History */}
      {paymentHistory.length > 0 && (
        <>
          <h2 style={{ marginTop: '3rem' }}>Payment History</h2>
          <Card>
            <PaymentHistoryTable>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Plan</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {paymentHistory.map(payment => (
                  <tr key={payment.id}>
                    <td>{new Date(payment.createdAt).toLocaleDateString()}</td>
                    <td>{payment.subscriptionType ? payment.subscriptionType.charAt(0).toUpperCase() + payment.subscriptionType.slice(1) : 'N/A'}</td>
                    <td>${payment.amount}</td>
                    <td>
                      <span style={{ 
                        color: payment.status === 'succeeded' ? 'var(--success-color)' : 
                               payment.status === 'failed' ? 'var(--danger-color)' : 
                               'var(--warning-color)'
                      }}>
                        {payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </PaymentHistoryTable>
          </Card>
        </>
      )}
      
      {/* Cancel Subscription Modal */}
      <Modal
        isOpen={isCancelModalOpen}
        onClose={() => setIsCancelModalOpen(false)}
        title="Cancel Subscription"
        size="small"
        footer={
          <>
            <Button variant="light" onClick={() => setIsCancelModalOpen(false)}>
              Keep Subscription
            </Button>
            <Button variant="danger" onClick={handleCancelSubscription}>
              Cancel Subscription
            </Button>
          </>
        }
      >
        <p>Are you sure you want to cancel your subscription?</p>
        <p>You will lose access to premium features at the end of your current billing period.</p>
      </Modal>
    </SubscriptionsContainer>
  );
};

export default Subscriptions;