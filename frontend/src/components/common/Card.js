import React from 'react';
import styled from 'styled-components';
import PropTypes from 'prop-types';

const CardContainer = styled.div`
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: ${props => props.noMargin ? '0' : '1.5rem'};
  height: ${props => props.fullHeight ? '100%' : 'auto'};
  display: flex;
  flex-direction: column;
`;

const CardHeader = styled.div`
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #eee;
  background-color: ${props => props.background || 'transparent'};
  
  h2, h3, h4, h5, h6 {
    margin: 0;
    color: ${props => props.color || 'inherit'};
  }
`;

const CardBody = styled.div`
  padding: 1.5rem;
  flex: 1;
`;

const CardFooter = styled.div`
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  background-color: ${props => props.background || '#f8f9fa'};
`;

const Card = ({ 
  children, 
  title, 
  headerBackground, 
  headerColor, 
  footer, 
  footerBackground,
  noMargin,
  fullHeight
}) => {
  return (
    <CardContainer noMargin={noMargin} fullHeight={fullHeight}>
      {title && (
        <CardHeader background={headerBackground} color={headerColor}>
          {typeof title === 'string' ? <h3>{title}</h3> : title}
        </CardHeader>
      )}
      <CardBody>
        {children}
      </CardBody>
      {footer && (
        <CardFooter background={footerBackground}>
          {footer}
        </CardFooter>
      )}
    </CardContainer>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  headerBackground: PropTypes.string,
  headerColor: PropTypes.string,
  footer: PropTypes.node,
  footerBackground: PropTypes.string,
  noMargin: PropTypes.bool,
  fullHeight: PropTypes.bool
};

Card.defaultProps = {
  noMargin: false,
  fullHeight: false
};

export default Card;