import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

const ButtonStyles = `
  display: inline-block;
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const StyledButton = styled.button`
  ${ButtonStyles}
  background-color: ${props => {
    switch (props.variant) {
      case 'primary':
        return 'var(--primary-color)';
      case 'secondary':
        return 'var(--secondary-color)';
      case 'danger':
        return 'var(--danger-color)';
      case 'success':
        return 'var(--success-color)';
      case 'warning':
        return 'var(--warning-color)';
      case 'info':
        return 'var(--info-color)';
      case 'outline':
        return 'transparent';
      default:
        return 'var(--light-color)';
    }
  }};
  color: ${props => {
    if (props.variant === 'outline') {
      return 'var(--primary-color)';
    }
    return ['primary', 'secondary', 'danger', 'success', 'warning', 'info'].includes(props.variant)
      ? '#fff'
      : '#333';
  }};
  border: ${props => props.variant === 'outline' ? '1px solid var(--primary-color)' : 'none'};
  width: ${props => props.block ? '100%' : 'auto'};
  
  &:hover:not(:disabled) {
    opacity: 0.9;
    transform: translateY(-1px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const StyledLink = styled(Link)`
  ${ButtonStyles}
  background-color: ${props => {
    switch (props.variant) {
      case 'primary':
        return 'var(--primary-color)';
      case 'secondary':
        return 'var(--secondary-color)';
      case 'danger':
        return 'var(--danger-color)';
      case 'success':
        return 'var(--success-color)';
      case 'warning':
        return 'var(--warning-color)';
      case 'info':
        return 'var(--info-color)';
      case 'outline':
        return 'transparent';
      default:
        return 'var(--light-color)';
    }
  }};
  color: ${props => {
    if (props.variant === 'outline') {
      return 'var(--primary-color)';
    }
    return ['primary', 'secondary', 'danger', 'success', 'warning', 'info'].includes(props.variant)
      ? '#fff'
      : '#333';
  }};
  border: ${props => props.variant === 'outline' ? '1px solid var(--primary-color)' : 'none'};
  width: ${props => props.block ? '100%' : 'auto'};
  text-decoration: none;
  
  &:hover {
    opacity: 0.9;
    transform: translateY(-1px);
    color: ${props => {
      if (props.variant === 'outline') {
        return 'var(--primary-color)';
      }
      return ['primary', 'secondary', 'danger', 'success', 'warning', 'info'].includes(props.variant)
        ? '#fff'
        : '#333';
    }};
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const Button = ({ children, variant, block, to, ...rest }) => {
  if (to) {
    return (
      <StyledLink to={to} variant={variant} block={block} {...rest}>
        {children}
      </StyledLink>
    );
  }
  
  return (
    <StyledButton variant={variant} block={block} {...rest}>
      {children}
    </StyledButton>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'danger', 'success', 'warning', 'info', 'light', 'outline']),
  block: PropTypes.bool,
  to: PropTypes.string
};

Button.defaultProps = {
  variant: 'primary',
  block: false
};

export default Button;