import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Container = styled.div`
  min-height: 100vh;
  background: #0a0a0a;
  color: white;
  padding: 2rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  background: linear-gradient(135deg, #00ff88, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const LogoutButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
`;

const StatLabel = styled.div`
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: bold;
  color: #00ff88;
`;

const Section = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
`;

const SectionTitle = styled.h2`
  font-size: 1.25rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SearchBar = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const SearchInput = styled.input`
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;

  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  &:focus {
    outline: none;
    border-color: #00ff88;
  }
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const Th = styled.th`
  text-align: left;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
`;

const Td = styled.td`
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
`;

const StatusBadge = styled.span`
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  background: ${props => {
    switch (props.status) {
      case 'active': return 'rgba(0, 255, 136, 0.2)';
      case 'published': return 'rgba(0, 255, 136, 0.2)';
      case 'draft': return 'rgba(255, 193, 7, 0.2)';
      case 'suspended': return 'rgba(255, 107, 107, 0.2)';
      case 'pending': return 'rgba(255, 193, 7, 0.2)';
      case 'approved': return 'rgba(0, 255, 136, 0.2)';
      case 'rejected': return 'rgba(255, 107, 107, 0.2)';
      default: return 'rgba(255, 255, 255, 0.1)';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'active': return '#00ff88';
      case 'published': return '#00ff88';
      case 'draft': return '#ffc107';
      case 'suspended': return '#ff6b6b';
      case 'pending': return '#ffc107';
      case 'approved': return '#00ff88';
      case 'rejected': return '#ff6b6b';
      default: return 'white';
    }
  }};
`;

const ActionButton = styled.button`
  background: ${props => props.danger ? 'rgba(255, 107, 107, 0.2)' : 'rgba(0, 255, 136, 0.2)'};
  border: none;
  color: ${props => props.danger ? '#ff6b6b' : '#00ff88'};
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  margin-right: 0.5rem;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.danger ? 'rgba(255, 107, 107, 0.3)' : 'rgba(0, 255, 136, 0.3)'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
`;

const PageButton = styled.button`
  background: ${props => props.active ? 'rgba(0, 255, 136, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
  border: 1px solid ${props => props.active ? '#00ff88' : 'rgba(255, 255, 255, 0.2)'};
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover:not(:disabled) {
    background: rgba(0, 255, 136, 0.2);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const PageInfo = styled.span`
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
`;

const TabContainer = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
`;

const Tab = styled.button`
  background: ${props => props.active ? 'rgba(0, 255, 136, 0.2)' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.active ? '#00ff88' : 'rgba(255, 255, 255, 0.1)'};
  color: ${props => props.active ? '#00ff88' : 'white'};
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(0, 255, 136, 0.15);
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  color: rgba(255, 255, 255, 0.6);
`;

const ErrorMessage = styled.div`
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  color: #ff6b6b;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
`;

const ITEMS_PER_PAGE = 10;

function Admin() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalWebsites: 0,
    publishedWebsites: 0,
    pendingModeration: 0
  });
  const [users, setUsers] = useState([]);
  const [websites, setWebsites] = useState([]);
  const [moderation, setModeration] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Pagination state
  const [userPage, setUserPage] = useState(1);
  const [websitePage, setWebsitePage] = useState(1);
  const [moderationPage, setModerationPage] = useState(1);
  
  // Search state
  const [userSearch, setUserSearch] = useState('');
  const [websiteSearch, setWebsiteSearch] = useState('');
  
  // Active tab
  const [activeTab, setActiveTab] = useState('users');

  useEffect(() => {
    if (!user || user.role !== 'admin') {
      navigate('/');
      return;
    }
    
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Fetch stats
      const statsRes = await fetch('/api/admin/dashboard', { headers });
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        const s = statsData.data?.stats || statsData.stats || statsData || {};
        setStats({
          totalUsers:        s.totalUsers        || s.total_users        || 0,
          totalWebsites:     s.totalWebsites     || s.total_websites     || 0,
          publishedWebsites: s.publishedWebsites || s.published_websites || 0,
          pendingModeration: s.pendingModeration || s.pending_moderation || 0
        });
      }

      // Fetch users (paginated_response: array in data)
      const usersRes = await fetch('/api/admin/users', { headers });
      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(Array.isArray(usersData.data) ? usersData.data
               : usersData.users || []);
      }

      // Note: there is no /api/admin/websites endpoint yet — skip silently
      setWebsites([]);

      // Fetch moderation queue (paginated_response: array in data)
      const modRes = await fetch('/api/admin/moderation', { headers });
      if (modRes.ok) {
        const modData = await modRes.json();
        setModeration(Array.isArray(modData.data) ? modData.data
                    : modData.items || []);
      }
    } catch (err) {
      console.error('Error fetching admin data:', err);
      setError('Failed to load admin data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (res.ok) {
        setUsers(users.filter(u => u.id !== userId));
        setStats(prev => ({
          ...prev,
          totalUsers: prev.totalUsers - 1
        }));
      } else {
        alert('Failed to delete user');
      }
    } catch (err) {
      console.error('Error deleting user:', err);
      alert('Error deleting user');
    }
  };

  const handleDeleteWebsite = async (websiteId) => {
    if (!window.confirm('Are you sure you want to delete this website? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/admin/websites/${websiteId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (res.ok) {
        setWebsites(websites.filter(w => w.id !== websiteId));
        setStats(prev => ({
          ...prev,
          totalWebsites: prev.totalWebsites - 1
        }));
      } else {
        alert('Failed to delete website');
      }
    } catch (err) {
      console.error('Error deleting website:', err);
      alert('Error deleting website');
    }
  };

  const handleModeration = async (itemId, action) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/admin/moderation/${itemId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      });

      if (res.ok) {
        setModeration(moderation.filter(m => m.id !== itemId));
        setStats(prev => ({
          ...prev,
          pendingModeration: prev.pendingModeration - 1
        }));
      } else {
        alert('Failed to update moderation status');
      }
    } catch (err) {
      console.error('Error updating moderation:', err);
      alert('Error updating moderation status');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Filter users based on search
  const filteredUsers = users.filter(user => 
    user.email?.toLowerCase().includes(userSearch.toLowerCase()) ||
    user.name?.toLowerCase().includes(userSearch.toLowerCase())
  );

  // Filter websites based on search
  const filteredWebsites = websites.filter(website =>
    website.name?.toLowerCase().includes(websiteSearch.toLowerCase()) ||
    website.subdomain?.toLowerCase().includes(websiteSearch.toLowerCase())
  );

  // Pagination calculations
  const totalUserPages = Math.ceil(filteredUsers.length / ITEMS_PER_PAGE);
  const totalWebsitePages = Math.ceil(filteredWebsites.length / ITEMS_PER_PAGE);
  const totalModerationPages = Math.ceil(moderation.length / ITEMS_PER_PAGE);

  const paginatedUsers = filteredUsers.slice(
    (userPage - 1) * ITEMS_PER_PAGE,
    userPage * ITEMS_PER_PAGE
  );

  const paginatedWebsites = filteredWebsites.slice(
    (websitePage - 1) * ITEMS_PER_PAGE,
    websitePage * ITEMS_PER_PAGE
  );

  const paginatedModeration = moderation.slice(
    (moderationPage - 1) * ITEMS_PER_PAGE,
    moderationPage * ITEMS_PER_PAGE
  );

  // Reset page when search changes
  useEffect(() => {
    setUserPage(1);
  }, [userSearch]);

  useEffect(() => {
    setWebsitePage(1);
  }, [websiteSearch]);

  if (loading) {
    return (
      <Container>
        <LoadingSpinner>Loading admin dashboard...</LoadingSpinner>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>Admin Dashboard</Title>
        <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
      </Header>

      {error && <ErrorMessage>{error}</ErrorMessage>}

      {/* Stats Grid */}
      <StatsGrid>
        <StatCard>
          <StatLabel>Total Users</StatLabel>
          <StatValue>{stats.totalUsers || 0}</StatValue>
        </StatCard>
        <StatCard>
          <StatLabel>Total Websites</StatLabel>
          <StatValue>{stats.totalWebsites || 0}</StatValue>
        </StatCard>
        <StatCard>
          <StatLabel>Published Websites</StatLabel>
          <StatValue>{stats.publishedWebsites || 0}</StatValue>
        </StatCard>
        <StatCard>
          <StatLabel>Pending Moderation</StatLabel>
          <StatValue>{stats.pendingModeration || 0}</StatValue>
        </StatCard>
      </StatsGrid>

      {/* Tabs */}
      <TabContainer>
        <Tab active={activeTab === 'users'} onClick={() => setActiveTab('users')}>
          Users
        </Tab>
        <Tab active={activeTab === 'websites'} onClick={() => setActiveTab('websites')}>
          Websites
        </Tab>
        <Tab active={activeTab === 'moderation'} onClick={() => setActiveTab('moderation')}>
          Moderation Queue
        </Tab>
      </TabContainer>

      {/* Users Section */}
      {activeTab === 'users' && (
        <Section>
          <SectionTitle>
            User Management
          </SectionTitle>
          <SearchBar>
            <SearchInput
              type="text"
              placeholder="Search users by email or name..."
              value={userSearch}
              onChange={(e) => setUserSearch(e.target.value)}
            />
          </SearchBar>
          <Table>
            <thead>
              <tr>
                <Th>Email</Th>
                <Th>Name</Th>
                <Th>Role</Th>
                <Th>Subscription</Th>
                <Th>Created</Th>
                <Th>Actions</Th>
              </tr>
            </thead>
            <tbody>
              {paginatedUsers.map(user => (
                <tr key={user.id}>
                  <Td>{user.email}</Td>
                  <Td>{user.name || '-'}</Td>
                  <Td>
                    <StatusBadge status={user.role}>
                      {user.role || 'user'}
                    </StatusBadge>
                  </Td>
                  <Td>
                    <StatusBadge status={user.subscription_status || 'inactive'}>
                      {user.subscription_status || 'free'}
                    </StatusBadge>
                  </Td>
                  <Td>{user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</Td>
                  <Td>
                    <ActionButton danger onClick={() => handleDeleteUser(user.id)}>
                      Delete
                    </ActionButton>
                  </Td>
                </tr>
              ))}
              {paginatedUsers.length === 0 && (
                <tr>
                  <Td colSpan="6" style={{ textAlign: 'center', color: 'rgba(255,255,255,0.5)' }}>
                    {userSearch ? 'No users match your search' : 'No users found'}
                  </Td>
                </tr>
              )}
            </tbody>
          </Table>
          {totalUserPages > 1 && (
            <Pagination>
              <PageButton 
                onClick={() => setUserPage(p => Math.max(1, p - 1))}
                disabled={userPage === 1}
              >
                Previous
              </PageButton>
              <PageInfo>
                Page {userPage} of {totalUserPages}
              </PageInfo>
              <PageButton 
                onClick={() => setUserPage(p => Math.min(totalUserPages, p + 1))}
                disabled={userPage === totalUserPages}
              >
                Next
              </PageButton>
            </Pagination>
          )}
        </Section>
      )}

      {/* Websites Section */}
      {activeTab === 'websites' && (
        <Section>
          <SectionTitle>
            Website Management
          </SectionTitle>
          <SearchBar>
            <SearchInput
              type="text"
              placeholder="Search websites by name or subdomain..."
              value={websiteSearch}
              onChange={(e) => setWebsiteSearch(e.target.value)}
            />
          </SearchBar>
          <Table>
            <thead>
              <tr>
                <Th>Name</Th>
                <Th>Subdomain</Th>
                <Th>Owner</Th>
                <Th>Status</Th>
                <Th>Created</Th>
                <Th>Actions</Th>
              </tr>
            </thead>
            <tbody>
              {paginatedWebsites.map(website => (
                <tr key={website.id}>
                  <Td>{website.name}</Td>
                  <Td>{website.subdomain}.websitebuilder.com</Td>
                  <Td>{website.owner_email || website.user_id}</Td>
                  <Td>
                    <StatusBadge status={website.status}>
                      {website.status || 'draft'}
                    </StatusBadge>
                  </Td>
                  <Td>{website.created_at ? new Date(website.created_at).toLocaleDateString() : '-'}</Td>
                  <Td>
                    <ActionButton onClick={() => window.open(`http://${website.subdomain}.localhost:5000`, '_blank')}>
                      View
                    </ActionButton>
                    <ActionButton danger onClick={() => handleDeleteWebsite(website.id)}>
                      Delete
                    </ActionButton>
                  </Td>
                </tr>
              ))}
              {paginatedWebsites.length === 0 && (
                <tr>
                  <Td colSpan="6" style={{ textAlign: 'center', color: 'rgba(255,255,255,0.5)' }}>
                    {websiteSearch ? 'No websites match your search' : 'No websites found'}
                  </Td>
                </tr>
              )}
            </tbody>
          </Table>
          {totalWebsitePages > 1 && (
            <Pagination>
              <PageButton 
                onClick={() => setWebsitePage(p => Math.max(1, p - 1))}
                disabled={websitePage === 1}
              >
                Previous
              </PageButton>
              <PageInfo>
                Page {websitePage} of {totalWebsitePages}
              </PageInfo>
              <PageButton 
                onClick={() => setWebsitePage(p => Math.min(totalWebsitePages, p + 1))}
                disabled={websitePage === totalWebsitePages}
              >
                Next
              </PageButton>
            </Pagination>
          )}
        </Section>
      )}

      {/* Moderation Section */}
      {activeTab === 'moderation' && (
        <Section>
          <SectionTitle>
            Moderation Queue
          </SectionTitle>
          <Table>
            <thead>
              <tr>
                <Th>Type</Th>
                <Th>Content</Th>
                <Th>Reported By</Th>
                <Th>Date</Th>
                <Th>Actions</Th>
              </tr>
            </thead>
            <tbody>
              {paginatedModeration.map(item => (
                <tr key={item.id}>
                  <Td>{item.type || 'Content'}</Td>
                  <Td>{item.content_preview || item.reason || '-'}</Td>
                  <Td>{item.reported_by || 'System'}</Td>
                  <Td>{item.created_at ? new Date(item.created_at).toLocaleDateString() : '-'}</Td>
                  <Td>
                    <ActionButton onClick={() => handleModeration(item.id, 'approve')}>
                      Approve
                    </ActionButton>
                    <ActionButton danger onClick={() => handleModeration(item.id, 'reject')}>
                      Reject
                    </ActionButton>
                  </Td>
                </tr>
              ))}
              {paginatedModeration.length === 0 && (
                <tr>
                  <Td colSpan="5" style={{ textAlign: 'center', color: 'rgba(255,255,255,0.5)' }}>
                    No items pending moderation
                  </Td>
                </tr>
              )}
            </tbody>
          </Table>
          {totalModerationPages > 1 && (
            <Pagination>
              <PageButton 
                onClick={() => setModerationPage(p => Math.max(1, p - 1))}
                disabled={moderationPage === 1}
              >
                Previous
              </PageButton>
              <PageInfo>
                Page {moderationPage} of {totalModerationPages}
              </PageInfo>
              <PageButton 
                onClick={() => setModerationPage(p => Math.min(totalModerationPages, p + 1))}
                disabled={moderationPage === totalModerationPages}
              >
                Next
              </PageButton>
            </Pagination>
          )}
        </Section>
      )}
    </Container>
  );
}

export default Admin;