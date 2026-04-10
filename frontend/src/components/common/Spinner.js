import React from 'react';
import styled, { keyframes } from 'styled-components';
import PropTypes from 'prop-types';

const spin = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SpinnerContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: ${props => props.fullPage ? '100vh' : '100%'};
  width: 100%;
`;

const SpinnerElement = styled.div`
  width: ${props => props.size}px;
  height: ${props => props.size}px;
  border: ${props => props.thickness}px solid rgba(0, 0, 0, 0.1);
  border-top: ${props => props.thickness}px solid ${props => props.color};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`;

const Spinner = ({ size, thickness, color, fullPage }) => {
  return (
    <SpinnerContainer fullPage={fullPage}>
      <SpinnerElement size={size} thickness={thickness} color={color} />
    </SpinnerContainer>
  );
};

Spinner.propTypes = {
  size: PropTypes.number,
  thickness: PropTypes.number,
  color: PropTypes.string,
  fullPage: PropTypes.bool
};

Spinner.defaultProps = {
  size: 50,
  thickness: 4,
  color: 'var(--primary-color)',
  fullPage: false
};

export default Spinner;