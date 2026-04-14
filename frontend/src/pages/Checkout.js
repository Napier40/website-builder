import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import axios from 'axios';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';

const CheckoutContainer = styled.div`
  flex: 1;
  padding: 2rem;
`;

const CheckoutHeader = styled.div`
  margin-bottom: 2rem;
`;

const CheckoutTitle = styled.h1`
  margin: 0 0 1rem;
  font-size: 2rem;
`;

const CheckoutGrid = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  
  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
`;

const PaymentForm = styled.form`
  margin-top: 1.5rem;
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

const CardElementContainer = styled.div`
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  
  &:focus-within {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
`;

const OrderSummary = styled(Card)`
  position: sticky;
  top: 80px;
`;

const SummaryItem = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #eee;
  
  &:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }
`;

const SummaryLabel = styled.span`
  font-weight: ${props => props.bold ? 'bold' : 'normal'};
`;

const SummaryValue = styled.span`
  font-weight: ${props => props.bold ? 'bold' : 'normal'};
`;

const SubscriptionDetails = styled.div`
  margin-bottom: 1.5rem;
`;

const PlanTitle = styled.h3`
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
`;

const PlanFeatures = styled.ul`
  list-style: none;
  padding: 0;
  margin: 1rem 0;
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

const Checkout = () => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [succeeded, setSucceeded] = useState(false);
  const [clientSecret, setClientSecret] = useState('');
  const [billingDetails, setBillingDetails] = useState({
    name: '',
    email: '',
    address: {
      line1: '',
      city: '',
      state: '',
      postal_code: ''
    }
  });
  
  const stripe = useStripe();
  const elements = useElements();
  const { id } = useParams();
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchSubscriptionAndIntent = async () => {
      try {
        setLoading(true);
        
        // Fetch subscription details
        const subRes = await axios.get(`/api/subscriptions/${id}`);
        setSubscription(subRes.data.subscription);
        
        // Create payment intent
        const intentRes = await axios.post('/api/payments/intent', {
          subscriptionId: id
        });
        
        setClientSecret(intentRes.data.clientSecret);
        setLoading(false);
      } catch (err) {
        setError('Failed to load checkout data');
        setLoading(false);
      }
    };
    
    fetchSubscriptionAndIntent();
  }, [id]);
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setBillingDetails({
        ...billingDetails,
        [parent]: {
          ...billingDetails[parent],
          [child]: value
        }
      });
    } else {
      setBillingDetails({
        ...billingDetails,
        [name]: value
      });
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!stripe || !elements) {
      // Stripe.js has not loaded yet
      return;
    }
    
    // Validate form
    if (!billingDetails.name || !billingDetails.email || 
        !billingDetails.address.line1 || !billingDetails.address.city || 
        !billingDetails.address.state || !billingDetails.address.postal_code) {
      setError('Please fill in all required fields');
      return;
    }
    
    setProcessing(true);
    
    try {
      // Create payment method
      const { error: paymentMethodError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: elements.getElement(CardElement),
        billing_details: billingDetails
      });
      
      if (paymentMethodError) {
        setError(paymentMethodError.message);
        setProcessing(false);
        return;
      }
      
      // Subscribe user to plan
      const { error: confirmError } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: paymentMethod.id
      });
      
      if (confirmError) {
        setError(confirmError.message);
        setProcessing(false);
        return;
      }
      
      // Subscribe user to plan in our backend
      await axios.post('/api/subscriptions/subscribe', {
        subscriptionId: id,
        paymentMethodId: paymentMethod.id
      });
      
      setSucceeded(true);
      setProcessing(false);
      
      // Redirect to dashboard after successful payment
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.message || 'Payment failed');
      setProcessing(false);
    }
  };
  
  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4'
        }
      },
      invalid: {
        color: '#9e2146',
        iconColor: '#9e2146'
      }
    }
  };
  
  if (loading) {
    return <Spinner fullPage />;
  }
  
  if (!subscription) {
    return (
      <CheckoutContainer>
        <Alert type="danger" message="Subscription plan not found" />
        <Button to="/subscriptions" variant="primary">
          Back to Subscriptions
        </Button>
      </CheckoutContainer>
    );
  }
  
  return (
    <CheckoutContainer>
      <CheckoutHeader>
        <CheckoutTitle>Checkout</CheckoutTitle>
      </CheckoutHeader>
      
      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      {succeeded && <Alert type="success" message="Payment successful! Redirecting to dashboard..." />}
      
      <CheckoutGrid>
        <div>
          <Card>
            <SubscriptionDetails>
              <PlanTitle>
                {subscription.name.charAt(0).toUpperCase() + subscription.name.slice(1)} Plan
              </PlanTitle>
              <p>${subscription.price}/month</p>
              
              <PlanFeatures>
                <PlanFeature>{subscription.maxWebsites === -1 ? 'Unlimited' : subscription.maxWebsites} Website{subscription.maxWebsites !== 1 ? 's' : ''}</PlanFeature>
                {subscription.features?.map((f, i) => <PlanFeature key={i}>{f}</PlanFeature>)}
                <PlanFeature>Free SSL Certificate</PlanFeature>
                <PlanFeature>Mobile Responsive</PlanFeature>
                {subscription.customDomain && <PlanFeature>Custom Domain Support</PlanFeature>}
                {subscription.analytics && <PlanFeature>Advanced Analytics</PlanFeature>}
                {subscription.ecommerce && <PlanFeature>E-commerce Features</PlanFeature>}
                {subscription.name === 'enterprise' && <PlanFeature>Priority Support</PlanFeature>}
              </PlanFeatures>
            </SubscriptionDetails>
            
            <PaymentForm onSubmit={handleSubmit}>
              <h3>Billing Information</h3>
              
              <FormGroup>
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  name="name"
                  value={billingDetails.name}
                  onChange={handleInputChange}
                  placeholder="John Doe"
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={billingDetails.email}
                  onChange={handleInputChange}
                  placeholder="john@example.com"
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="address.line1">Address</Label>
                <Input
                  id="address.line1"
                  name="address.line1"
                  value={billingDetails.address.line1}
                  onChange={handleInputChange}
                  placeholder="123 Main St"
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="address.city">City</Label>
                <Input
                  id="address.city"
                  name="address.city"
                  value={billingDetails.address.city}
                  onChange={handleInputChange}
                  placeholder="San Francisco"
                  required
                />
              </FormGroup>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <FormGroup>
                  <Label htmlFor="address.state">State</Label>
                  <Input
                    id="address.state"
                    name="address.state"
                    value={billingDetails.address.state}
                    onChange={handleInputChange}
                    placeholder="CA"
                    required
                  />
                </FormGroup>
                
                <FormGroup>
                  <Label htmlFor="address.postal_code">ZIP Code</Label>
                  <Input
                    id="address.postal_code"
                    name="address.postal_code"
                    value={billingDetails.address.postal_code}
                    onChange={handleInputChange}
                    placeholder="94103"
                    required
                  />
                </FormGroup>
              </div>
              
              <h3>Payment Information</h3>
              
              <FormGroup>
                <Label htmlFor="card">Credit Card</Label>
                <CardElementContainer>
                  <CardElement id="card" options={cardElementOptions} />
                </CardElementContainer>
              </FormGroup>
              
              <Button 
                type="submit" 
                variant="primary" 
                block 
                disabled={processing || succeeded || !stripe}
              >
                {processing ? <Spinner size={20} /> : `Pay $${subscription.price}`}
              </Button>
            </PaymentForm>
          </Card>
        </div>
        
        <OrderSummary>
          <h3>Order Summary</h3>
          
          <SummaryItem>
            <SummaryLabel>Plan</SummaryLabel>
            <SummaryValue>
              {subscription.name.charAt(0).toUpperCase() + subscription.name.slice(1)}
            </SummaryValue>
          </SummaryItem>
          
          <SummaryItem>
            <SummaryLabel>Billing Cycle</SummaryLabel>
            <SummaryValue>Monthly</SummaryValue>
          </SummaryItem>
          
          <SummaryItem>
            <SummaryLabel>Subtotal</SummaryLabel>
            <SummaryValue>${subscription.price}</SummaryValue>
          </SummaryItem>
          
          <SummaryItem>
            <SummaryLabel>Tax</SummaryLabel>
            <SummaryValue>$0.00</SummaryValue>
          </SummaryItem>
          
          <SummaryItem>
            <SummaryLabel bold>Total</SummaryLabel>
            <SummaryValue bold>${subscription.price}/month</SummaryValue>
          </SummaryItem>
          
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '1rem' }}>
            You will be charged ${subscription.price} today and then ${subscription.price} monthly until you cancel.
          </p>
        </OrderSummary>
      </CheckoutGrid>
    </CheckoutContainer>
  );
};

export default Checkout;