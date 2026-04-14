import React, { useState, useEffect, useContext } from 'react';

import styled from 'styled-components';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import Modal from '../components/common/Modal';

const WebsitesContainer = styled.div`
  flex: 1;
  padding: 2rem;
`;

const WebsitesHeader = styled.div`
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

const WebsitesTitle = styled.h1`
  margin: 0;
  font-size: 2rem;
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
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
`;

const WebsiteInfo = styled.div`
  margin: 1rem 0;
  
  p {
    margin: 0.5rem 0;
    font-size: 0.9rem;
    color: #666;
    
    strong {
      color: #333;
    }
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 3rem;
`;

const SearchBar = styled.div`
  margin-bottom: 1.5rem;
  display: flex;
  gap: 1rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const SearchInput = styled.input`
  flex: 1;
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

const FilterSelect = styled.select`
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  min-width: 150px;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
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

const Select = styled.select`
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

const ErrorText = styled.p`
  color: var(--danger-color);
  font-size: 0.9rem;
  margin-top: 0.5rem;
`;

const Websites = () => {
  const [websites, setWebsites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [websiteToDelete, setWebsiteToDelete] = useState(null);
  
  const [newWebsite, setNewWebsite] = useState({
    name: '',
    subdomain: '',
    template: 'default'
  });
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { user } = useContext(AuthContext);
  
  useEffect(() => {
    fetchWebsites();
  }, []);
  
  const fetchWebsites = async () => {
    try {
      setLoading(true);
      const res = await axios.get('/api/websites');
      setWebsites(res.data.websites);
      setLoading(false);
    } catch (err) {
      setError('Failed to load websites');
      setLoading(false);
    }
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    if (name === 'name' && !newWebsite.subdomain) {
      // Auto-generate subdomain from name
      const subdomain = value.toLowerCase().replace(/[^a-z0-9]/g, '-');
      setNewWebsite({
        ...newWebsite,
        [name]: value,
        subdomain
      });
    } else {
      setNewWebsite({
        ...newWebsite,
        [name]: value
      });
    }
    
    // Clear error for this field
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: null
      });
    }
  };
  
  const validateForm = () => {
    const errors = {};
    
    if (!newWebsite.name.trim()) {
      errors.name = 'Website name is required';
    }
    
    if (!newWebsite.subdomain.trim()) {
      errors.subdomain = 'Subdomain is required';
    } else if (!/^[a-z0-9-]+$/.test(newWebsite.subdomain)) {
      errors.subdomain = 'Subdomain can only contain lowercase letters, numbers, and hyphens';
    }
    
    if (!newWebsite.template) {
      errors.template = 'Template is required';
    }
    
    return errors;
  };
  
  const handleCreateWebsite = async (e) => {
    e.preventDefault();
    
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    try {
      setIsSubmitting(true);
      const res = await axios.post('/api/websites', newWebsite);
      
      // Add new website to state
      setWebsites([...websites, res.data.website]);
      
      // Reset form
      setNewWebsite({
        name: '',
        subdomain: '',
        template: 'default'
      });
      
      // Close modal
      setIsCreateModalOpen(false);
      setIsSubmitting(false);
    } catch (err) {
      setFormErrors({
        ...formErrors,
        submit: err.response?.data?.message || 'Failed to create website'
      });
      setIsSubmitting(false);
    }
  };
  
  const handleDeleteClick = (website) => {
    setWebsiteToDelete(website);
    setIsDeleteModalOpen(true);
  };
  
  const handleDeleteWebsite = async () => {
    if (!websiteToDelete) return;
    
    try {
      await axios.delete(`/api/websites/${websiteToDelete.id}`);
      
      // Remove website from state
      setWebsites(websites.filter(website => website.id !== websiteToDelete.id));
      
      // Close modal
      setIsDeleteModalOpen(false);
      setWebsiteToDelete(null);
    } catch (err) {
      setError('Failed to delete website');
    }
  };
  
  const handlePublishToggle = async (website) => {
    try {
      if (website.isPublished) {
        await axios.put(`/api/websites/${website.id}/unpublish`);
      } else {
        await axios.put(`/api/websites/${website.id}/publish`);
      }
      
      // Update website in state
      setWebsites(websites.map(w => {
        if (w.id === website.id) {
          return { ...w, isPublished: !w.isPublished };
        }
        return w;
      }));
    } catch (err) {
      setError(`Failed to ${website.isPublished ? 'unpublish' : 'publish'} website`);
    }
  };
  
  const filteredWebsites = websites.filter(website => {
    const matchesSearch = website.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         website.subdomain.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (statusFilter === 'all') {
      return matchesSearch;
    } else if (statusFilter === 'published') {
      return matchesSearch && website.isPublished;
    } else {
      return matchesSearch && !website.isPublished;
    }
  });
  
  if (loading) {
    return <Spinner fullPage />;
  }
  
  return (
    <WebsitesContainer>
      <WebsitesHeader>
        <WebsitesTitle>My Websites</WebsitesTitle>
        <Button 
          variant="primary" 
          onClick={() => setIsCreateModalOpen(true)}
          disabled={user?.subscriptionStatus === 'none' && websites.length >= 1}
        >
          <i className="fas fa-plus"></i> Create New Website
        </Button>
      </WebsitesHeader>
      
      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}
      
      {user?.subscriptionStatus === 'none' && websites.length >= 1 && (
        <Alert 
          type="warning" 
          message="You've reached the limit for the free plan. Upgrade to create more websites." 
        />
      )}
      
      <SearchBar>
        <SearchInput
          type="text"
          placeholder="Search websites..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <FilterSelect
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="all">All Websites</option>
          <option value="published">Published</option>
          <option value="draft">Draft</option>
        </FilterSelect>
      </SearchBar>
      
      {websites.length === 0 ? (
        <EmptyState>
          <h2>You haven't created any websites yet</h2>
          <p>Get started by creating your first website</p>
          <Button 
            variant="primary" 
            onClick={() => setIsCreateModalOpen(true)}
          >
            Create Website
          </Button>
        </EmptyState>
      ) : filteredWebsites.length === 0 ? (
        <Card>
          <p>No websites match your search criteria.</p>
        </Card>
      ) : (
        <WebsiteGrid>
          {filteredWebsites.map(website => (
            <WebsiteCard key={website.id}>
              <WebsiteCardBody>
                <WebsiteTitle>{website.name}</WebsiteTitle>
                <WebsiteUrl>
                  {website.customDomain || `${website.subdomain}.example.com`}
                </WebsiteUrl>
                <WebsiteStatus published={website.isPublished}>
                  {website.isPublished ? 'Published' : 'Draft'}
                </WebsiteStatus>
                
                <WebsiteInfo>
                  <p><strong>Template:</strong> {website.template}</p>
                  <p><strong>Created:</strong> {new Date(website.createdAt).toLocaleDateString()}</p>
                  <p><strong>Last Updated:</strong> {new Date(website.updatedAt).toLocaleDateString()}</p>
                </WebsiteInfo>
              </WebsiteCardBody>
              
              <WebsiteActions>
                <Button to={`/builder/${website.id}`} variant="primary">
                  Edit
                </Button>
                <Button 
                  variant={website.isPublished ? 'warning' : 'success'}
                  onClick={() => handlePublishToggle(website)}
                >
                  {website.isPublished ? 'Unpublish' : 'Publish'}
                </Button>
                <Button 
                  variant="danger"
                  onClick={() => handleDeleteClick(website)}
                >
                  Delete
                </Button>
                {website.isPublished && (
                  <Button 
                    to={`https://${website.subdomain}.example.com`} 
                    target="_blank" 
                    variant="outline"
                  >
                    Visit
                  </Button>
                )}
              </WebsiteActions>
            </WebsiteCard>
          ))}
        </WebsiteGrid>
      )}
      
      {/* Create Website Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create New Website"
        footer={
          <>
            <Button variant="light" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreateWebsite} disabled={isSubmitting}>
              {isSubmitting ? <Spinner size={20} /> : 'Create Website'}
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateWebsite}>
          <FormGroup>
            <Label htmlFor="name">Website Name</Label>
            <Input
              type="text"
              id="name"
              name="name"
              value={newWebsite.name}
              onChange={handleInputChange}
              placeholder="My Awesome Website"
            />
            {formErrors.name && <ErrorText>{formErrors.name}</ErrorText>}
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="subdomain">Subdomain</Label>
            <Input
              type="text"
              id="subdomain"
              name="subdomain"
              value={newWebsite.subdomain}
              onChange={handleInputChange}
              placeholder="my-awesome-website"
            />
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
              Your website will be available at {newWebsite.subdomain || 'your-subdomain'}.example.com
            </p>
            {formErrors.subdomain && <ErrorText>{formErrors.subdomain}</ErrorText>}
          </FormGroup>
          
          <FormGroup>
            <Label htmlFor="template">Template</Label>
            <Select
              id="template"
              name="template"
              value={newWebsite.template}
              onChange={handleInputChange}
            >
              <option value="default">Default</option>
              <option value="business">Business</option>
              <option value="portfolio">Portfolio</option>
              <option value="blog">Blog</option>
              <option value="ecommerce">E-commerce</option>
            </Select>
            {formErrors.template && <ErrorText>{formErrors.template}</ErrorText>}
          </FormGroup>
          
          {formErrors.submit && <Alert type="danger" message={formErrors.submit} />}
        </form>
      </Modal>
      
      {/* Delete Website Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Website"
        size="small"
        footer={
          <>
            <Button variant="light" onClick={() => setIsDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDeleteWebsite}>
              Delete Website
            </Button>
          </>
        }
      >
        <p>Are you sure you want to delete <strong>{websiteToDelete?.name}</strong>?</p>
        <p>This action cannot be undone.</p>
      </Modal>
    </WebsitesContainer>
  );
};

export default Websites;