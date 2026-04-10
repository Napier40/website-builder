import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import Button from '../components/common/Button';

const HeroSection = styled.section`
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: #fff;
  padding: 6rem 2rem;
  text-align: center;
`;

const HeroContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const HeroTitle = styled.h1`
  font-size: 3rem;
  margin-bottom: 1.5rem;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
`;

const HeroSubtitle = styled.p`
  font-size: 1.5rem;
  margin-bottom: 2rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  
  @media (max-width: 768px) {
    font-size: 1.2rem;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  justify-content: center;
  gap: 1rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
  }
`;

const FeaturesSection = styled.section`
  padding: 5rem 2rem;
  background-color: #f8f9fa;
`;

const SectionTitle = styled.h2`
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2.5rem;
  color: #333;
`;

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 992px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FeatureCard = styled.div`
  background-color: #fff;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
`;

const FeatureIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
`;

const FeatureTitle = styled.h3`
  margin-bottom: 1rem;
  font-size: 1.5rem;
`;

const FeatureDescription = styled.p`
  color: #666;
`;

const PricingSection = styled.section`
  padding: 5rem 2rem;
  background-color: #fff;
`;

const PricingGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 992px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const PricingCard = styled.div`
  background-color: #fff;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  border: ${props => props.popular ? '2px solid var(--primary-color)' : '1px solid #eee'};
  position: relative;
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

const PricingTitle = styled.h3`
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
`;

const PricingPrice = styled.div`
  font-size: 2.5rem;
  font-weight: bold;
  margin: 1.5rem 0;
  
  span {
    font-size: 1rem;
    font-weight: normal;
    color: #666;
  }
`;

const PricingFeatures = styled.ul`
  list-style: none;
  padding: 0;
  margin: 2rem 0;
  text-align: left;
`;

const PricingFeature = styled.li`
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

const TestimonialsSection = styled.section`
  padding: 5rem 2rem;
  background-color: #f8f9fa;
`;

const TestimonialsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const TestimonialCard = styled.div`
  background-color: #fff;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const TestimonialText = styled.p`
  font-style: italic;
  margin-bottom: 1.5rem;
  color: #555;
`;

const TestimonialAuthor = styled.div`
  display: flex;
  align-items: center;
`;

const TestimonialAvatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #eee;
  margin-right: 1rem;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
`;

const TestimonialInfo = styled.div`
  h4 {
    margin: 0;
    font-size: 1.1rem;
  }
  
  p {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
  }
`;

const CtaSection = styled.section`
  padding: 5rem 2rem;
  background: linear-gradient(135deg, #3498db, #2ecc71);
  color: #fff;
  text-align: center;
`;

const CtaContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const CtaTitle = styled.h2`
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
`;

const CtaText = styled.p`
  font-size: 1.2rem;
  margin-bottom: 2rem;
`;

const Home = () => {
  return (
    <>
      <HeroSection>
        <HeroContainer>
          <HeroTitle>Create Beautiful Websites Without Coding</HeroTitle>
          <HeroSubtitle>
            Our drag-and-drop website builder makes it easy to create professional websites in minutes.
            No technical skills required.
          </HeroSubtitle>
          <ButtonGroup>
            <Button to="/register" variant="light" size="large">Get Started Free</Button>
            <Button to="/features" variant="outline" size="large">Learn More</Button>
          </ButtonGroup>
        </HeroContainer>
      </HeroSection>
      
      <FeaturesSection>
        <SectionTitle>Why Choose Our Website Builder</SectionTitle>
        <FeaturesGrid>
          <FeatureCard>
            <FeatureIcon>
              <i className="fas fa-paint-brush"></i>
            </FeatureIcon>
            <FeatureTitle>Beautiful Templates</FeatureTitle>
            <FeatureDescription>
              Choose from hundreds of professionally designed templates that look great on any device.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <i className="fas fa-mouse-pointer"></i>
            </FeatureIcon>
            <FeatureTitle>Drag & Drop Editor</FeatureTitle>
            <FeatureDescription>
              Simply drag and drop elements to create your perfect website without any coding.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <i className="fas fa-mobile-alt"></i>
            </FeatureIcon>
            <FeatureTitle>Mobile Responsive</FeatureTitle>
            <FeatureDescription>
              All websites automatically adapt to look great on any device - desktop, tablet, or mobile.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <i className="fas fa-rocket"></i>
            </FeatureIcon>
            <FeatureTitle>Fast Performance</FeatureTitle>
            <FeatureDescription>
              Optimized for speed to ensure your website loads quickly and keeps visitors engaged.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <i className="fas fa-search"></i>
            </FeatureIcon>
            <FeatureTitle>SEO Friendly</FeatureTitle>
            <FeatureDescription>
              Built-in SEO tools help your website rank higher in search engine results.
            </FeatureDescription>
          </FeatureCard>
          
          <FeatureCard>
            <FeatureIcon>
              <i className="fas fa-headset"></i>
            </FeatureIcon>
            <FeatureTitle>24/7 Support</FeatureTitle>
            <FeatureDescription>
              Our dedicated support team is always ready to help you with any questions.
            </FeatureDescription>
          </FeatureCard>
        </FeaturesGrid>
      </FeaturesSection>
      
      <PricingSection>
        <SectionTitle>Choose Your Plan</SectionTitle>
        <PricingGrid>
          <PricingCard>
            <PricingTitle>Basic</PricingTitle>
            <PricingPrice>$9.99 <span>/month</span></PricingPrice>
            <PricingFeatures>
              <PricingFeature>1 Website</PricingFeature>
              <PricingFeature>5GB Storage</PricingFeature>
              <PricingFeature>Free SSL Certificate</PricingFeature>
              <PricingFeature>Mobile Responsive</PricingFeature>
              <PricingFeature>Basic Templates</PricingFeature>
            </PricingFeatures>
            <Button to="/register" variant="primary" block>Get Started</Button>
          </PricingCard>
          
          <PricingCard popular>
            <PopularBadge>Most Popular</PopularBadge>
            <PricingTitle>Premium</PricingTitle>
            <PricingPrice>$19.99 <span>/month</span></PricingPrice>
            <PricingFeatures>
              <PricingFeature>5 Websites</PricingFeature>
              <PricingFeature>20GB Storage</PricingFeature>
              <PricingFeature>Free SSL Certificate</PricingFeature>
              <PricingFeature>Mobile Responsive</PricingFeature>
              <PricingFeature>Premium Templates</PricingFeature>
              <PricingFeature>Custom Domain</PricingFeature>
              <PricingFeature>Analytics</PricingFeature>
            </PricingFeatures>
            <Button to="/register" variant="primary" block>Get Started</Button>
          </PricingCard>
          
          <PricingCard>
            <PricingTitle>Enterprise</PricingTitle>
            <PricingPrice>$49.99 <span>/month</span></PricingPrice>
            <PricingFeatures>
              <PricingFeature>Unlimited Websites</PricingFeature>
              <PricingFeature>100GB Storage</PricingFeature>
              <PricingFeature>Free SSL Certificate</PricingFeature>
              <PricingFeature>Mobile Responsive</PricingFeature>
              <PricingFeature>All Templates</PricingFeature>
              <PricingFeature>Custom Domain</PricingFeature>
              <PricingFeature>Advanced Analytics</PricingFeature>
              <PricingFeature>E-commerce Features</PricingFeature>
              <PricingFeature>Priority Support</PricingFeature>
            </PricingFeatures>
            <Button to="/register" variant="primary" block>Get Started</Button>
          </PricingCard>
        </PricingGrid>
      </PricingSection>
      
      <TestimonialsSection>
        <SectionTitle>What Our Customers Say</SectionTitle>
        <TestimonialsGrid>
          <TestimonialCard>
            <TestimonialText>
              "I was able to create a professional website for my business in just a few hours. The drag-and-drop editor is so intuitive and easy to use. I've received so many compliments on my website!"
            </TestimonialText>
            <TestimonialAuthor>
              <TestimonialAvatar>
                <img src="https://randomuser.me/api/portraits/women/32.jpg" alt="Sarah Johnson" />
              </TestimonialAvatar>
              <TestimonialInfo>
                <h4>Sarah Johnson</h4>
                <p>Small Business Owner</p>
              </TestimonialInfo>
            </TestimonialAuthor>
          </TestimonialCard>
          
          <TestimonialCard>
            <TestimonialText>
              "As a freelance photographer, I needed a website that showcases my portfolio beautifully. This website builder exceeded my expectations with its stunning templates and customization options."
            </TestimonialText>
            <TestimonialAuthor>
              <TestimonialAvatar>
                <img src="https://randomuser.me/api/portraits/men/44.jpg" alt="Michael Chen" />
              </TestimonialAvatar>
              <TestimonialInfo>
                <h4>Michael Chen</h4>
                <p>Photographer</p>
              </TestimonialInfo>
            </TestimonialAuthor>
          </TestimonialCard>
          
          <TestimonialCard>
            <TestimonialText>
              "I've tried several website builders before, but this one is by far the best. The templates are modern and professional, and the customer support is outstanding. Highly recommended!"
            </TestimonialText>
            <TestimonialAuthor>
              <TestimonialAvatar>
                <img src="https://randomuser.me/api/portraits/women/68.jpg" alt="Emily Rodriguez" />
              </TestimonialAvatar>
              <TestimonialInfo>
                <h4>Emily Rodriguez</h4>
                <p>Marketing Consultant</p>
              </TestimonialInfo>
            </TestimonialAuthor>
          </TestimonialCard>
          
          <TestimonialCard>
            <TestimonialText>
              "Setting up an online store was a breeze with this platform. The e-commerce features are robust yet easy to use. My sales have increased significantly since launching my new website."
            </TestimonialText>
            <TestimonialAuthor>
              <TestimonialAvatar>
                <img src="https://randomuser.me/api/portraits/men/22.jpg" alt="David Wilson" />
              </TestimonialAvatar>
              <TestimonialInfo>
                <h4>David Wilson</h4>
                <p>Online Retailer</p>
              </TestimonialInfo>
            </TestimonialAuthor>
          </TestimonialCard>
        </TestimonialsGrid>
      </TestimonialsSection>
      
      <CtaSection>
        <CtaContainer>
          <CtaTitle>Ready to Build Your Website?</CtaTitle>
          <CtaText>
            Join thousands of satisfied customers who have created stunning websites with our platform.
            Get started today with our free plan - no credit card required.
          </CtaText>
          <Button to="/register" variant="light" size="large">Create Your Website Now</Button>
        </CtaContainer>
      </CtaSection>
    </>
  );
};

export default Home;