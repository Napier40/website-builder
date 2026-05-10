import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import axios from 'axios';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';
import Modal from '../components/common/Modal';

const BuilderContainer = styled.div`
  display: flex;
  height: calc(100vh - 60px);
`;

const Sidebar = styled.div`
  width: 300px;
  background-color: #fff;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
`;

const SidebarHeader = styled.div`
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const SidebarTitle = styled.h2`
  margin: 0;
  font-size: 1.2rem;
`;

const SidebarContent = styled.div`
  flex: 1;
  padding: 1rem;
`;

const SidebarFooter = styled.div`
  padding: 1rem;
  border-top: 1px solid #eee;
  display: flex;
  gap: 0.5rem;
`;

const TabsContainer = styled.div`
  display: flex;
  margin-bottom: 1rem;
  border-bottom: 1px solid #eee;
`;

const Tab = styled.button`
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid ${props => props.active ? 'var(--primary-color)' : 'transparent'};
  color: ${props => props.active ? 'var(--primary-color)' : '#666'};
  font-weight: ${props => props.active ? '500' : 'normal'};
  cursor: pointer;
  
  &:hover {
    color: var(--primary-color);
  }
`;

const ElementsPanel = styled.div`
  margin-bottom: 1.5rem;
`;

const ElementsTitle = styled.h3`
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: #666;
`;

const ElementsList = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
`;

const Element = styled.div`
  padding: 0.75rem;
  background-color: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
  
  &:hover {
    background-color: #f0f7ff;
    border-color: var(--primary-color);
  }
  
  i {
    display: block;
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: #666;
  }
`;

const Canvas = styled.div`
  flex: 1;
  background-color: #f8f9fa;
  overflow-y: auto;
  padding: 2rem;
`;

const PageContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100%;
  background-color: #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
`;

const EmptyCanvas = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  
  i {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  h3 {
    margin: 0 0 1rem;
  }
`;

const Toolbar = styled.div`
  height: 60px;
  background-color: #333;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  justify-content: space-between;
`;

const ToolbarLeft = styled.div`
  display: flex;
  align-items: center;
`;

const ToolbarRight = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const DeviceSelector = styled.div`
  display: flex;
  align-items: center;
  margin-right: 2rem;
`;

const DeviceButton = styled.button`
  background: none;
  border: none;
  color: ${props => props.active ? '#fff' : '#aaa'};
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  
  &:hover {
    color: #fff;
  }
`;

const PageSelector = styled.select`
  padding: 0.5rem;
  border-radius: 4px;
  border: none;
  margin-right: 1rem;
`;

const WebsiteBuilder = () => {
  const [website, setWebsite] = useState(null);
  const [currentPage, setCurrentPage] = useState(null);
  const [activeTab, setActiveTab] = useState('elements');
  const [device, setDevice] = useState('desktop');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [isExitModalOpen, setIsExitModalOpen] = useState(false);
  
  const { id } = useParams();
  const navigate = useNavigate();
  
  const fetchWebsite = useCallback(async () => {
    try {
      setLoading(true);
      const res = await axios.get(`/api/websites/${id}`);
      setWebsite(res.data.website);
      
      // Set current page to home page or first page
      const homePage = res.data.website.pages.find(page => page.slug === 'home');
      setCurrentPage(homePage || res.data.website.pages[0]);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load website');
      setLoading(false);
    }
  }, [id]);
  
  useEffect(() => {
    fetchWebsite();
  }, [fetchWebsite]);
  
  const handlePageChange = (e) => {
    const pageId = parseInt(e.target.value, 10);
    const page = website.pages.find(p => p.id === pageId);
    setCurrentPage(page);
  };
  
  const handleSave = async () => {
    try {
      setIsSaving(true);
      if (currentPage) {
        await axios.put(`/api/websites/${id}/pages/${currentPage.id}`, {
          content: currentPage.content,
          title:   currentPage.title,
          slug:    currentPage.slug,
        });
      }
      setIsSaving(false);
    } catch (err) {
      setError('Failed to save changes');
      setIsSaving(false);
    }
  };

  const handleContentChange = (newContent) => {
    setCurrentPage(prev => ({ ...prev, content: newContent }));
    setWebsite(prev => ({
      ...prev,
      pages: prev.pages.map(p => p.id === currentPage.id ? { ...p, content: newContent } : p)
    }));
  };
  
  const handlePublish = async () => {
    try {
      setIsPublishing(true);
      
      // Publish website
      await axios.put(`/api/websites/${id}/publish`);
      
      // Update website state
      setWebsite({
        ...website,
        isPublished: true
      });
      
      setIsPublishing(false);
    } catch (err) {
      setError('Failed to publish website');
      setIsPublishing(false);
    }
  };
  
  const handleExit = () => {
    // In a real implementation, we would check for unsaved changes
    // For now, we'll just show the exit modal
    setIsExitModalOpen(true);
  };
  
  const confirmExit = () => {
    navigate('/websites');
  };
  
  if (loading) {
    return <Spinner fullPage />;
  }
  
  if (error) {
    return (
      <div style={{ padding: '2rem' }}>
        <Alert type="danger" message={error} />
        <Button to="/websites" variant="primary">
          Back to Websites
        </Button>
      </div>
    );
  }
  
  return (
    <>
      <Toolbar>
        <ToolbarLeft>
          <Button variant="outline" onClick={handleExit} style={{ marginRight: '1rem' }}>
            <i className="fas fa-arrow-left"></i> Exit
          </Button>
          
          <PageSelector value={currentPage?.id} onChange={handlePageChange}>
            {website.pages.map(page => (
              <option key={page.id} value={page.id}>
                {page.title}
              </option>
            ))}
          </PageSelector>
          
          <DeviceSelector>
            <DeviceButton 
              active={device === 'desktop'} 
              onClick={() => setDevice('desktop')}
              title="Desktop View"
            >
              <i className="fas fa-desktop"></i>
            </DeviceButton>
            <DeviceButton 
              active={device === 'tablet'} 
              onClick={() => setDevice('tablet')}
              title="Tablet View"
            >
              <i className="fas fa-tablet-alt"></i>
            </DeviceButton>
            <DeviceButton 
              active={device === 'mobile'} 
              onClick={() => setDevice('mobile')}
              title="Mobile View"
            >
              <i className="fas fa-mobile-alt"></i>
            </DeviceButton>
          </DeviceSelector>
        </ToolbarLeft>
        
        <ToolbarRight>
          <Button variant="outline" onClick={handleSave} disabled={isSaving}>
            {isSaving ? <Spinner size={20} /> : 'Save'}
          </Button>
          <Button 
            variant={website.isPublished ? 'success' : 'primary'} 
            onClick={handlePublish}
            disabled={isPublishing}
          >
            {isPublishing ? <Spinner size={20} /> : website.isPublished ? 'Published' : 'Publish'}
          </Button>
        </ToolbarRight>
      </Toolbar>
      
      <BuilderContainer>
        <Sidebar>
          <SidebarHeader>
            <SidebarTitle>Builder</SidebarTitle>
          </SidebarHeader>
          
          <TabsContainer>
            <Tab 
              active={activeTab === 'elements'} 
              onClick={() => setActiveTab('elements')}
            >
              Elements
            </Tab>
            <Tab 
              active={activeTab === 'pages'} 
              onClick={() => setActiveTab('pages')}
            >
              Pages
            </Tab>
            <Tab 
              active={activeTab === 'settings'} 
              onClick={() => setActiveTab('settings')}
            >
              Settings
            </Tab>
          </TabsContainer>
          
          <SidebarContent>
            {activeTab === 'elements' && (
              <>
                <ElementsPanel>
                  <ElementsTitle>Layout</ElementsTitle>
                  <ElementsList>
                    <Element>
                      <i className="fas fa-columns"></i>
                      Section
                    </Element>
                    <Element>
                      <i className="fas fa-th-large"></i>
                      Container
                    </Element>
                    <Element>
                      <i className="fas fa-grip-horizontal"></i>
                      Row
                    </Element>
                    <Element>
                      <i className="fas fa-square"></i>
                      Column
                    </Element>
                  </ElementsList>
                </ElementsPanel>
                
                <ElementsPanel>
                  <ElementsTitle>Basic</ElementsTitle>
                  <ElementsList>
                    <Element>
                      <i className="fas fa-heading"></i>
                      Heading
                    </Element>
                    <Element>
                      <i className="fas fa-paragraph"></i>
                      Text
                    </Element>
                    <Element>
                      <i className="fas fa-image"></i>
                      Image
                    </Element>
                    <Element>
                      <i className="fas fa-play-circle"></i>
                      Video
                    </Element>
                    <Element>
                      <i className="fas fa-link"></i>
                      Button
                    </Element>
                    <Element>
                      <i className="fas fa-list"></i>
                      List
                    </Element>
                  </ElementsList>
                </ElementsPanel>
                
                <ElementsPanel>
                  <ElementsTitle>Advanced</ElementsTitle>
                  <ElementsList>
                    <Element>
                      <i className="fas fa-envelope"></i>
                      Form
                    </Element>
                    <Element>
                      <i className="fas fa-map-marker-alt"></i>
                      Map
                    </Element>
                    <Element>
                      <i className="fas fa-table"></i>
                      Table
                    </Element>
                    <Element>
                      <i className="fas fa-code"></i>
                      HTML
                    </Element>
                  </ElementsList>
                </ElementsPanel>
              </>
            )}
            
            {activeTab === 'pages' && (
              <div>
                <h3>Pages</h3>
                <p>Manage your website pages here.</p>
                {/* Page management UI would go here */}
              </div>
            )}
            
            {activeTab === 'settings' && (
              <div>
                <h3>Website Settings</h3>
                <p>Configure your website settings here.</p>
                {/* Settings UI would go here */}
              </div>
            )}
          </SidebarContent>
          
          <SidebarFooter>
            <Button variant="outline" block>
              Preview
            </Button>
            <Button variant="primary" block onClick={handleSave} disabled={isSaving}>
              {isSaving ? <Spinner size={20} /> : 'Save'}
            </Button>
          </SidebarFooter>
        </Sidebar>
        
        <Canvas>
          <PageContainer style={{
            width: device === 'desktop' ? '100%' : device === 'tablet' ? '768px' : '375px',
            margin: '0 auto'
          }}>
            {currentPage ? (
              <div>
                {/* Live HTML preview */}
                {currentPage.content ? (
                  <div
                    dangerouslySetInnerHTML={{ __html: currentPage.content }}
                    style={{ minHeight: '200px' }}
                  />
                ) : (
                  <EmptyCanvas>
                    <i className="fas fa-plus-circle"></i>
                    <h3>This page is empty</h3>
                    <p>Use the HTML editor below to add content.</p>
                  </EmptyCanvas>
                )}
                {/* HTML Editor */}
                <div style={{ marginTop: '2rem', borderTop: '1px solid #eee', paddingTop: '1rem' }}>
                  <label style={{ fontWeight: 600, display: 'block', marginBottom: '0.5rem' }}>
                    HTML Editor
                  </label>
                  <textarea
                    value={currentPage.content || ''}
                    onChange={e => handleContentChange(e.target.value)}
                    style={{
                      width: '100%',
                      minHeight: '200px',
                      fontFamily: 'monospace',
                      fontSize: '0.9rem',
                      padding: '0.75rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      resize: 'vertical',
                    }}
                    placeholder="Enter HTML content for this page..."
                  />
                </div>
              </div>
            ) : (
              <EmptyCanvas>
                <i className="fas fa-plus-circle"></i>
                <h3>No page selected</h3>
                <p>Select a page from the dropdown above.</p>
              </EmptyCanvas>
            )}
          </PageContainer>
        </Canvas>
      </BuilderContainer>
      
      {/* Exit Confirmation Modal */}
      <Modal
        isOpen={isExitModalOpen}
        onClose={() => setIsExitModalOpen(false)}
        title="Exit Builder"
        size="small"
        footer={
          <>
            <Button variant="light" onClick={() => setIsExitModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={confirmExit}>
              Exit
            </Button>
          </>
        }
      >
        <p>Are you sure you want to exit the builder?</p>
        <p>Any unsaved changes will be lost.</p>
      </Modal>
    </>
  );
};

export default WebsiteBuilder;