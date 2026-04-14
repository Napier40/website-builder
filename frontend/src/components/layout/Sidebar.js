import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { AuthContext } from '../../context/AuthContext';

const SidebarContainer = styled.div`
  width: 250px;
  background-color: #fff;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  height: 100%;
  padding: 2rem 0;
  position: fixed;
  left: 0;
  top: 60px;
  z-index: 900;
  
  @media (max-width: 768px) {
    width: 100%;
    position: relative;
    top: 0;
    height: auto;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }
`;

const SidebarNav = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const SidebarItem = styled.li`
  margin-bottom: 0.5rem;
`;

const SidebarLink = styled(Link)`
  display: block;
  padding: 0.8rem 1.5rem;
  color: var(--dark-color);
  font-weight: 500;
  border-left: 4px solid transparent;
  
  &:hover {
    background-color: #f8f9fa;
    color: var(--primary-color);
    border-left-color: var(--primary-color);
  }
  
  &.active {
    background-color: #f0f7ff;
    color: var(--primary-color);
    border-left-color: var(--primary-color);
  }
`;

const UserInfo = styled.div`
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  margin-bottom: 1rem;
`;

const UserName = styled.h3`
  margin: 0;
  font-size: 1.2rem;
  color: var(--dark-color);
`;

const UserEmail = styled.p`
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
  color: #888;
`;

const SubscriptionBadge = styled.div`
  display: inline-block;
  padding: 0.25rem 0.5rem;
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
  border-radius: 4px;
  font-size: 0.8rem;
  margin-top: 0.5rem;
`;

const Sidebar = () => {
  const { user } = useContext(AuthContext);
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <SidebarContainer>
      {user && (
        <UserInfo>
          <UserName>{user.name}</UserName>
          <UserEmail>{user.email}</UserEmail>
          <SubscriptionBadge type={user.subscriptionType}>
            {(user.subscriptionType === 'free' || !user.subscriptionType) ? 'Free Plan' : `${user.subscriptionType.charAt(0).toUpperCase() + user.subscriptionType.slice(1)} Plan`}
          </SubscriptionBadge>
        </UserInfo>
      )}
      
      <SidebarNav>
        <SidebarItem>
          <SidebarLink to="/dashboard" className={isActive('/dashboard')}>
            Dashboard
          </SidebarLink>
        </SidebarItem>
        <SidebarItem>
          <SidebarLink to="/websites" className={isActive('/websites')}>
            My Websites
          </SidebarLink>
        </SidebarItem>
        <SidebarItem>
          <SidebarLink to="/subscriptions" className={isActive('/subscriptions')}>
            Subscriptions
          </SidebarLink>
        </SidebarItem>
        <SidebarItem>
          <SidebarLink to="/account" className={isActive('/account')}>
            Account Settings
          </SidebarLink>
        </SidebarItem>
        {user?.role === 'admin' && (
          <SidebarItem>
            <SidebarLink to="/admin" className={isActive('/admin')}>
              Admin Panel
            </SidebarLink>
          </SidebarItem>
        )}
      </SidebarNav>
    </SidebarContainer>
  );
};

export default Sidebar;