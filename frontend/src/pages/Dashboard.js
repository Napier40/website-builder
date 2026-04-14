import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';

const DashboardContainer = styled.div`
  flex: 1;
  padding: 2rem;
`;

const DashboardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
`;

const DashboardTitle = styled.h1`
  margin: 0;
  font-size: 2rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const StatCard = styled(Card)`
  text-align: center;
`;

const StatValue = styled.h2`
  font-size: 2.5rem;
  margin: 0.5rem 0;
  color: var(--primary-color);
`;

const StatLabel = styled.p`
  margin: 0;
  color: #666;
  font-size: 1rem;
`;

const SectionTitle = styled.h2`
  margin: 2rem 0 1rem;
  font-size: 1.5rem;
`;

const WebsiteGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const WebsiteCard = styled(Card)`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const WebsiteCardBody = styled.div`
  flex: 1;
`;

const WebsiteTitle = styled.h3`
  margin: 0 0 0.5rem;
  font-size: 1.2rem;
`;

const WebsiteUrl = styled.p`
  margin: 0 0 1rem;
  color: var(--primary-color);
  font-size: 0.9rem;
`;

const WebsiteStatus = styled.span`
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
  background-color: ${props => props.published ? 'var(--success-color)' : '#f39c12'};
  color: #fff;
  margin-bottom: 1rem;
`;

const WebsiteActions = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-top: auto;
`;

const SubscriptionCard = styled(Card)`
  margin-bottom: 2rem;
`;

const SubscriptionInfo = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  
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

const Dashboard = () => {
  const [websites, setWebsites] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const { user } = useContext(AuthContext);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch websites
        const websitesRes = await axios.get('/api/websites');
        setWebsites(websitesRes.data.websites);
        
        // Fetch subscription
        const subscriptionRes = await axios.get('/api/subscriptions/current');
        setSubscription(subscriptionRes.data);
        
        setLoading(false);
      } catch (err) {
        setError('Failed to load dashboard data');
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  if (loading) {
    return <Spinner fullPage />;
  }
  
  const recentWebsites = websites.slice(0, 3);
  
  return (
    <DashboardContainer>
      <DashboardHeader>
        <DashboardTitle>Welcome, {user?.name}</DashboardTitle>
        <Button to="/websites/new" variant="primary">
          <i className="fas fa-plus"></i> Create New Website
        </Button>
      </DashboardHeader>
      
      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      
      <StatsGrid>
        <StatCard>
          <StatValue>{websites.length}</StatValue>
          <StatLabel>Total Websites</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>{websites.filter(website => website.isPublished).length}</StatValue>
          <StatLabel>Published Websites</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>
            {subscription?.hasSubscription
              ? (subscription.maxWebsites === -1 ? '∞' : subscription.maxWebsites - websites.length)
              : 1 - websites.length}
          </StatValue>
          <StatLabel>Remaining Websites</StatLabel>
        </StatCard>
        
        <StatCard>
          <StatValue>
            {subscription?.plan?.displayName || 'Free'}
          </StatValue>
          <StatLabel>Current Plan</StatLabel>
        </StatCard>
      </StatsGrid>
      
      <SubscriptionCard>
        <SubscriptionInfo>
          <SubscriptionDetails>
            <h3>
              Current Plan
              <SubscriptionBadge type={user?.subscriptionStatus}>
                {user?.subscriptionType === 'free' ? 'Free Plan' : `${(user?.subscriptionType || 'free').charAt(0).toUpperCase() + (user?.subscriptionType || 'free').slice(1)} Plan`}
              </SubscriptionBadge>
            </h3>
            {subscription?.hasSubscription ? (
              <p>
                {subscription.plan?.displayName} plan &mdash; {subscription.maxWebsites === -1 ? 'Unlimited' : subscription.maxWebsites} websites allowed
              </p>
            ) : (
              <p>Upgrade to create more websites and access premium features</p>
            )}
          </SubscriptionDetails>
          
          <Button to="/subscriptions" variant={subscription?.hasSubscription ? 'outline' : 'primary'}>
            {subscription?.hasSubscription ? 'Manage Subscription' : 'Upgrade Now'}
          </Button>
        </SubscriptionInfo>
      </SubscriptionCard>
      
      <SectionTitle>Recent Websites</SectionTitle>
      {recentWebsites.length > 0 ? (
        <WebsiteGrid>
          {recentWebsites.map(website => (
            <WebsiteCard key={website.id}>
              <WebsiteCardBody>
                <WebsiteTitle>{website.name}</WebsiteTitle>
                <WebsiteUrl>
                  {website.customDomain || `${website.subdomain}.example.com`}
                </WebsiteUrl>
                <WebsiteStatus published={website.isPublished}>
                  {website.isPublished ? 'Published' : 'Draft'}
                </WebsiteStatus>
              </WebsiteCardBody>
              <WebsiteActions>
                <Button to={`/builder/${website.id}`} variant="primary" block>
                  Edit
                </Button>
                <Button to={`https://${website.subdomain}.example.com`} target="_blank" variant="outline" block>
                  View
                </Button>
              </WebsiteActions>
            </WebsiteCard>
          ))}
        </WebsiteGrid>
      ) : (
        <Card>
          <p>You haven't created any websites yet.</p>
          <Button to="/websites/new" variant="primary">
            Create Your First Website
          </Button>
        </Card>
      )}
      
      {websites.length > 3 && (
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <Button to="/websites" variant="outline">
            View All Websites
          </Button>
        </div>
      )}
    </DashboardContainer>
  );
};

export default Dashboard;