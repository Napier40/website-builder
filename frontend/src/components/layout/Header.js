import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { AuthContext } from '../../context/AuthContext';

const HeaderContainer = styled.header`
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
`;

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  
  span {
    color: var(--secondary-color);
  }
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
`;

const NavLink = styled(Link)`
  margin-left: 1.5rem;
  color: var(--dark-color);
  font-weight: 500;
  
  &:hover {
    color: var(--primary-color);
  }
`;

const Button = styled(Link)`
  background-color: var(--primary-color);
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-left: 1.5rem;
  font-weight: 500;
  
  &:hover {
    background-color: #2980b9;
    color: #fff;
  }
`;

const Header = () => {
  const { isAuthenticated, user, logout } = useContext(AuthContext);

  const authLinks = (
    <>
      <NavLink to="/dashboard">Dashboard</NavLink>
      <NavLink to="/websites">My Websites</NavLink>
      <NavLink to="/subscriptions">Subscriptions</NavLink>
      <NavLink to="/account">Account</NavLink>
      <NavLink to="/" onClick={logout}>Logout</NavLink>
    </>
  );

  const guestLinks = (
    <>
      <NavLink to="/#features">Features</NavLink>
      <NavLink to="/#pricing">Pricing</NavLink>
      <Button to="/register">Sign Up</Button>
      <NavLink to="/login">Login</NavLink>
    </>
  );

  return (
    <HeaderContainer>
      <Logo to="/">
        Website<span>Builder</span>
      </Logo>
      <Nav>
        {isAuthenticated ? authLinks : guestLinks}
      </Nav>
    </HeaderContainer>
  );
};

export default Header;