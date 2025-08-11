import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/LearningDashboard.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function LearningDashboard({ user, profile }) {
  const [goals, setGoals] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [monthlyStats, setMonthlyStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [goalsRes, milestonesRes] = await Promise.all([
        axios.get(`${API}/goals`),
        axios.get(`${API}/milestones`)
      ]);
      
      setGoals(goalsRes.data.goals);
      setMilestones(milestonesRes.data.milestones);
      
      // Calculate monthly stats
      const currentMonth = new Date().toISOString().slice(0, 7);
      const currentMonthMilestones = milestonesRes.data.milestones.filter(
        m => m.month_year === currentMonth
      );
      
      const monthlyHours = currentMonthMilestones.reduce(
        (sum, m) => sum + m.hours_invested, 0
      );
      
      setMonthlyStats({
        currentMonthHours: monthlyHours,
        milestonesThisMonth: currentMonthMilestones.length,
        targetProgress: Math.min((monthlyHours / 6) * 100, 100)
      });
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getProgressColor = (progress) => {
    if (progress >= 100) return '#00C851';
    if (progress >= 75) return '#ffbb33';
    if (progress >= 50) return '#ff8800';
    return '#ff4444';
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading your learning dashboard...</p>
      </div>
    );
  }

  return (
    <div className="learning-dashboard">
      <div className="dashboard-header">
        <h2>Welcome back, {profile.full_name}!</h2>
        <p>Here's your learning progress overview</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card monthly-progress">
          <div className="stat-header">
            <h3>Monthly Learning Progress</h3>
            <span className="stat-icon">📊</span>
          </div>
          <div className="progress-container">
            <div className="progress-circle">
              <div 
                className="progress-fill"
                style={{
                  background: `conic-gradient(${getProgressColor(monthlyStats.targetProgress)} ${monthlyStats.targetProgress * 3.6}deg, #e0e0e0 0deg)`
                }}
              >
                <div className="progress-center">
                  <span className="progress-percentage">
                    {Math.round(monthlyStats.targetProgress)}%
                  </span>
                </div>
              </div>
            </div>
            <div className="progress-details">
              <div className="progress-stat">
                <span className="stat-value">{monthlyStats.currentMonthHours}h</span>
                <span className="stat-label">of 6h target</span>
              </div>
              <div className="progress-stat">
                <span className="stat-value">{monthlyStats.milestonesThisMonth}</span>
                <span className="stat-label">milestones</span>
              </div>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3>Learning Goals</h3>
            <span className="stat-icon">🎯</span>
          </div>
          <div className="stat-content">
            <div className="stat-number">{goals.length}</div>
            <div className="stat-detail">
              {goals.filter(g => g.status === 'active').length} active goals
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3>Total Milestones</h3>
            <span className="stat-icon">🏆</span>
          </div>
          <div className="stat-content">
            <div className="stat-number">{milestones.length}</div>
            <div className="stat-detail">
              All time achievements
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3>Teaching Opportunities</h3>
            <span className="stat-icon">👨‍🏫</span>
          </div>
          <div className="stat-content">
            <div className="stat-number">
              {milestones.filter(m => m.can_teach).length}
            </div>
            <div className="stat-detail">
              Skills you can teach
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-sections">
        <div className="section recent-milestones">
          <div className="section-header">
            <h3>Recent Milestones</h3>
            <span className="section-icon">🏅</span>
          </div>
          <div className="milestones-list">
            {milestones.slice(0, 5).map((milestone) => (
              <div key={milestone.id} className="milestone-item">
                <div className="milestone-main">
                  <h4>{milestone.what_learned}</h4>
                  <p>{milestone.source}</p>
                </div>
                <div className="milestone-meta">
                  <span className="milestone-hours">{milestone.hours_invested}h</span>
                  {milestone.can_teach && (
                    <span className="teach-badge">Can teach</span>
                  )}
                  <span className="milestone-date">
                    {formatDate(milestone.created_at)}
                  </span>
                </div>
              </div>
            ))}
            
            {milestones.length === 0 && (
              <div className="empty-state">
                <p>No milestones yet. Start your learning journey!</p>
                <button className="cta-button">Add Your First Milestone</button>
              </div>
            )}
          </div>
        </div>

        <div className="section active-goals">
          <div className="section-header">
            <h3>Active Goals</h3>
            <span className="section-icon">🎯</span>
          </div>
          <div className="goals-list">
            {goals.filter(g => g.status === 'active').slice(0, 3).map((goal) => (
              <div key={goal.id} className="goal-item">
                <h4>{goal.title}</h4>
                <p>{goal.description}</p>
                <div className="goal-meta">
                  <span className="goal-deadline">
                    Due: {formatDate(goal.target_completion_date)}
                  </span>
                </div>
              </div>
            ))}
            
            {goals.filter(g => g.status === 'active').length === 0 && (
              <div className="empty-state">
                <p>No active goals. Set your learning objectives!</p>
                <button className="cta-button">Create Your First Goal</button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="learning-suggestions">
        <div className="section-header">
          <h3>Suggested for You</h3>
          <span className="section-icon">💡</span>
        </div>
        <div className="suggestions-grid">
          <div className="suggestion-card">
            <h4>Complete Your Monthly Target</h4>
            <p>You're {Math.round(monthlyStats.targetProgress)}% towards your 6-hour learning goal this month.</p>
            <span className="suggestion-action">Add Milestone →</span>
          </div>
          <div className="suggestion-card">
            <h4>Explore Badge Generation</h4>
            <p>Create beautiful learning badges and LinkedIn posts to showcase your achievements.</p>
            <span className="suggestion-action">Generate Badge →</span>
          </div>
          <div className="suggestion-card">
            <h4>Connect with Peers</h4>
            <p>Discover what your colleagues are learning and get inspired by their journey.</p>
            <span className="suggestion-action">View Peers →</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LearningDashboard;