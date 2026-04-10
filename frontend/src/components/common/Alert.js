import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const AlertContainer = styled.div`
  padding: 0.8rem;
  margin: 1rem 0;
  opacity: 0.9;
  background: ${props => {
    switch (props.type) {
      case 'primary':
        return 'var(--primary-color)';
      case 'dark':
        return 'var(--dark-color)';
      case 'danger':
        return 'var(--danger-color)';
      case 'success':
        return 'var(--success-color)';
      case 'warning':
        return 'var(--warning-color)';
      case 'info':
        return 'var(--info-color)';
      default:
        return 'var(--light-color)';
    }
  }};
  color: ${props => {
    return ['primary', 'dark', 'danger', 'success', 'warning', 'info'].includes(props.type)
      ? '#fff'
      : '#333';
  }};
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  opacity: 0.7;
  
  &:hover {
    opacity: 1;
  }
`;

const Alert = ({ type, message, onClose }) => {
  return (
    <AlertContainer type={type}>
      <div>{message}</div>
      {onClose && (
        <CloseButton onClick={onClose}>
          &times;
        </CloseButton>
      )}
    </AlertContainer>
  );
};

Alert.propTypes = {
  type: PropTypes.oneOf(['primary', 'dark', 'light', 'danger', 'success', 'warning', 'info']),
  message: PropTypes.string.isRequired,
  onClose: PropTypes.func
};

Alert.defaultProps = {
  type: 'light'
};

export default Alert;