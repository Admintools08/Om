import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/AdminDashboard.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [badges, setBadges] = useState([]);
  const [adminActions, setAdminActions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadStats(),
        loadUsers(),
        loadBadges(),
        loadAdminActions()
      ]);
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`);
      setUsers(response.data.users);
    } catch (error) {
      console.error('Error loading users:', error);
    }
  };

  const loadBadges = async () => {
    try {
      const response = await axios.get(`${API}/admin/badges`);
      setBadges(response.data.badges);
    } catch (error) {
      console.error('Error loading badges:', error);
    }
  };

  const loadAdminActions = async () => {
    try {
      const response = await axios.get(`${API}/admin/actions`);
      setAdminActions(response.data.actions);
    } catch (error) {
      console.error('Error loading admin actions:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const TabButton = ({ tabId, label, isActive, onClick }) => (
    <button
      onClick={() => onClick(tabId)}
      className={`tab-button ${isActive ? 'active' : ''}`}
    >
      {label}
    </button>
  );

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Loading admin dashboard...</p>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="dashboard-tabs">
        <TabButton
          tabId="overview"
          label="📊 Overview"
          isActive={activeTab === 'overview'}
          onClick={setActiveTab}
        />
        <TabButton
          tabId="users"
          label="👥 Users"
          isActive={activeTab === 'users'}
          onClick={setActiveTab}
        />
        <TabButton
          tabId="badges"
          label="🏆 All Badges"
          isActive={activeTab === 'badges'}
          onClick={setActiveTab}
        />
        <TabButton
          tabId="actions"
          label="📝 Admin Actions"
          isActive={activeTab === 'actions'}
          onClick={setActiveTab}
        />
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && stats && (
          <div className="overview-tab">
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Users</h3>
                <div className="stat-number">{stats.total_users}</div>
              </div>
              <div className="stat-card">
                <h3>Total Admins</h3>
                <div className="stat-number">{stats.total_admins}</div>
              </div>
              <div className="stat-card">
                <h3>Total Badges Generated</h3>
                <div className="stat-number">{stats.total_badges_generated}</div>
              </div>
            </div>

            <div className="overview-sections">
              <div className="section">
                <h3>🏆 Top Learners</h3>
                <div className="top-learners">
                  {stats.top_learners.map((learner, index) => (
                    <div key={index} className="learner-item">
                      <span className="learner-rank">#{index + 1}</span>
                      <span className="learner-name">{learner.name}</span>
                      <span className="learner-count">{learner.badge_count} badges</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="section">
                <h3>📈 Recent Activities</h3>
                <div className="recent-activities">
                  {stats.recent_activities.slice(0, 10).map((activity, index) => (
                    <div key={index} className="activity-item">
                      <div className="activity-main">
                        <strong>{activity.user_name}</strong> generated a badge for{' '}
                        <strong>{activity.employee_name}</strong>
                      </div>
                      <div className="activity-details">
                        {activity.learning.substring(0, 100)}...
                      </div>
                      <div className="activity-meta">
                        <span className="difficulty-badge difficulty-{activity.difficulty.toLowerCase()}">
                          {activity.difficulty}
                        </span>
                        <span className="activity-time">{formatDate(activity.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="users-tab">
            <h3>👥 All Users ({users.length})</h3>
            <div className="users-grid">
              {users.map((user) => (
                <div key={user.id} className="user-card">
                  <div className="user-header">
                    <h4>{user.name}</h4>
                    <span className={`role-badge role-${user.role}`}>
                      {user.role}
                    </span>
                  </div>
                  <div className="user-stats">
                    <div className="user-stat">
                      <span className="stat-label">Badges Generated:</span>
                      <span className="stat-value">{user.total_badges_generated}</span>
                    </div>
                    <div className="user-stat">
                      <span className="stat-label">Joined:</span>
                      <span className="stat-value">{formatDate(user.created_at)}</span>
                    </div>
                    <div className="user-stat">
                      <span className="stat-label">Last Active:</span>
                      <span className="stat-value">{formatDate(user.last_active)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'badges' && (
          <div className="badges-tab">
            <h3>🏆 All Generated Badges ({badges.length})</h3>
            <div className="badges-grid">
              {badges.map((badge) => (
                <div key={badge.id} className="badge-card">
                  <div className="badge-image-container">
                    <img
                      src={badge.badge_url}
                      alt="Badge"
                      className="badge-thumbnail"
                    />
                  </div>
                  <div className="badge-info">
                    <h4>{badge.employee_name}</h4>
                    <p className="badge-text">{badge.badge_text}</p>
                    <div className="badge-meta">
                      <span className="badge-user">By: {badge.user_name}</span>
                      <span className={`difficulty-badge difficulty-${badge.difficulty.toLowerCase()}`}>
                        {badge.difficulty}
                      </span>
                      <span className="badge-date">{formatDate(badge.created_at)}</span>
                    </div>
                    <div className="badge-learning">
                      <strong>Learning:</strong> {badge.learning.substring(0, 150)}...
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="actions-tab">
            <h3>📝 Admin Actions ({adminActions.length})</h3>
            <div className="actions-list">
              {adminActions.map((action) => (
                <div key={action.id} className="action-item">
                  <div className="action-header">
                    <strong>{action.admin_name}</strong>
                    <span className="action-type">{action.action}</span>
                    <span className="action-time">{formatDate(action.timestamp)}</span>
                  </div>
                  <div className="action-details">
                    {action.details}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;