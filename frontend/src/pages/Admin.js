import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Alert from '../components/common/Alert';

const AdminContainer = styled.div`
  flex: 1;
  padding: 2rem;
`;

const AdminTitle = styled.h1`
  margin: 0 0 2rem;
  font-size: 2rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;

  @media (max-width: 1200px) { grid-template-columns: repeat(2, 1fr); }
  @media (max-width: 600px)  { grid-template-columns: 1fr; }
`;

const StatCard = styled(Card)`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary-color);
`;

const StatLabel = styled.div`
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
`;

const SectionTitle = styled.h2`
  margin: 2rem 0 1rem;
  font-size: 1.5rem;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;

  th, td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid #eee;
    font-size: 0.95rem;
  }

  th { background: #f8f9fa; font-weight: 600; }
  tr:hover td { background: #f8f9fa; }
`;

const Badge = styled.span`
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  background-color: ${props => {
    switch (props.type) {
      case 'admin':    return '#e74c3c';
      case 'premium':  return '#2ecc71';
      case 'basic':    return '#3498db';
      case 'enterprise': return '#9b59b6';
      case 'active':   return '#2ecc71';
      case 'pending':  return '#f39c12';
      case 'approved': return '#2ecc71';
      case 'rejected': return '#e74c3c';
      default:         return '#95a5a6';
    }
  }};
  color: #fff;
`;

const Admin = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const [stats, setStats]               = useState(null);
  const [users, setUsers]               = useState([]);
  const [modQueue, setModQueue]         = useState([]);
  const [auditLogs, setAuditLogs]       = useState([]);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState(null);
  const [activeTab, setActiveTab]       = useState('dashboard');

  // Redirect non-admins
  useEffect(() => {
    if (user && user.role !== 'admin') {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const [statsRes, usersRes, modRes, logsRes] = await Promise.all([
        axios.get('/api/admin/dashboard'),
        axios.get('/api/admin/users?limit=20'),
        axios.get('/api/admin/moderation?status=pending&limit=20'),
        axios.get('/api/admin/audit-logs?limit=20'),
      ]);
      setStats(statsRes.data.stats);
      setUsers(usersRes.data.users || []);
      setModQueue(modRes.data.reports || []);
      setAuditLogs(logsRes.data.logs || []);
      setLoading(false);
    } catch (err) {
      setError('Failed to load admin data');
      setLoading(false);
    }
  };

  const handleUpdateUserRole = async (userId, newRole) => {
    try {
      await axios.put(`/api/admin/users/${userId}`, { role: newRole });
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      setError('Failed to update user role');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Delete this user and all their data?')) return;
    try {
      await axios.delete(`/api/admin/users/${userId}`);
      setUsers(users.filter(u => u.id !== userId));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete user');
    }
  };

  const handleReviewMod = async (modId, status) => {
    try {
      await axios.put(`/api/admin/moderation/${modId}`, { status, notes: `Marked ${status} by admin` });
      setModQueue(modQueue.filter(m => m.id !== modId));
    } catch (err) {
      setError('Failed to review report');
    }
  };

  if (loading) return <Spinner fullPage />;

  const tabs = ['dashboard', 'users', 'moderation', 'audit-logs'];

  return (
    <AdminContainer>
      <AdminTitle>Admin Panel</AdminTitle>

      {error && <Alert type="danger" message={error} onClose={() => setError(null)} />}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '2px solid #eee', paddingBottom: '0' }}>
        {tabs.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '0.75rem 1.5rem',
              background: 'none',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid var(--primary-color)' : '2px solid transparent',
              color: activeTab === tab ? 'var(--primary-color)' : '#666',
              fontWeight: activeTab === tab ? 600 : 400,
              cursor: 'pointer',
              fontSize: '1rem',
              marginBottom: '-2px',
            }}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1).replace('-', ' ')}
          </button>
        ))}
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && stats && (
        <>
          <StatsGrid>
            <StatCard>
              <StatValue>{stats.users?.total || 0}</StatValue>
              <StatLabel>Total Users</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{stats.websites?.total || 0}</StatValue>
              <StatLabel>Total Websites</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{stats.websites?.published || 0}</StatValue>
              <StatLabel>Published Sites</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{stats.moderation?.pending || 0}</StatValue>
              <StatLabel>Pending Reports</StatLabel>
            </StatCard>
          </StatsGrid>

          <SectionTitle>Subscriptions Breakdown</SectionTitle>
          <StatsGrid>
            {Object.entries(stats.subscriptions || {}).map(([plan, count]) => (
              <StatCard key={plan}>
                <StatValue>{count}</StatValue>
                <StatLabel>{plan.charAt(0).toUpperCase() + plan.slice(1)}</StatLabel>
              </StatCard>
            ))}
          </StatsGrid>
        </>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <Card>
          <Table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Plan</th>
                <th>Joined</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.name}</td>
                  <td>{u.email}</td>
                  <td><Badge type={u.role}>{u.role}</Badge></td>
                  <td><Badge type={u.subscriptionType}>{u.subscriptionType}</Badge></td>
                  <td>{new Date(u.createdAt).toLocaleDateString()}</td>
                  <td style={{ display: 'flex', gap: '0.5rem' }}>
                    {u.id !== user?.id && (
                      <>
                        <Button
                          variant={u.role === 'admin' ? 'outline' : 'primary'}
                          size="small"
                          onClick={() => handleUpdateUserRole(u.id, u.role === 'admin' ? 'user' : 'admin')}
                        >
                          {u.role === 'admin' ? 'Revoke Admin' : 'Make Admin'}
                        </Button>
                        <Button
                          variant="danger"
                          size="small"
                          onClick={() => handleDeleteUser(u.id)}
                        >
                          Delete
                        </Button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}

      {/* Moderation Tab */}
      {activeTab === 'moderation' && (
        <Card>
          {modQueue.length === 0 ? (
            <p style={{ padding: '1rem', color: '#666' }}>No pending moderation reports. ✅</p>
          ) : (
            <Table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Content</th>
                  <th>Type</th>
                  <th>Reason</th>
                  <th>Reported</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {modQueue.map(m => (
                  <tr key={m.id}>
                    <td>{m.id}</td>
                    <td>#{m.contentId}</td>
                    <td>{m.contentModel}</td>
                    <td>{m.reason}</td>
                    <td>{new Date(m.createdAt).toLocaleDateString()}</td>
                    <td style={{ display: 'flex', gap: '0.5rem' }}>
                      <Button variant="primary" size="small" onClick={() => handleReviewMod(m.id, 'approved')}>
                        Approve
                      </Button>
                      <Button variant="danger" size="small" onClick={() => handleReviewMod(m.id, 'rejected')}>
                        Reject
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card>
      )}

      {/* Audit Logs Tab */}
      {activeTab === 'audit-logs' && (
        <Card>
          <Table>
            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map(log => (
                <tr key={log.id}>
                  <td>{log.id}</td>
                  <td>#{log.userId}</td>
                  <td><Badge type={log.action === 'DELETE' ? 'rejected' : 'active'}>{log.action}</Badge></td>
                  <td>{log.resource}{log.resourceId ? ` #${log.resourceId}` : ''}</td>
                  <td>{new Date(log.createdAt).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </AdminContainer>
  );
};

export default Admin;