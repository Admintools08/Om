import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/MilestonesManager.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function MilestonesManager({ user, profile }) {
  const [milestones, setMilestones] = useState([]);
  const [goals, setGoals] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    goal_id: '',
    what_learned: '',
    source: '',
    can_teach: false,
    hours_invested: '',
    project_certificate_link: ''
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [milestonesRes, goalsRes] = await Promise.all([
        axios.get(`${API}/milestones`),
        axios.get(`${API}/goals`)
      ]);
      setMilestones(milestonesRes.data.milestones);
      setGoals(goalsRes.data.goals);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const submitData = {
        ...formData,
        hours_invested: parseFloat(formData.hours_invested),
        goal_id: formData.goal_id || null
      };

      await axios.post(`${API}/milestones`, submitData);
      await loadData();
      resetForm();
      alert('Milestone added successfully! 🎉');
    } catch (error) {
      console.error('Error saving milestone:', error);
      alert('Failed to save milestone. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      goal_id: '',
      what_learned: '',
      source: '',
      can_teach: false,
      hours_invested: '',
      project_certificate_link: ''
    });
    setShowForm(false);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const groupMilestonesByMonth = (milestones) => {
    const grouped = milestones.reduce((acc, milestone) => {
      const monthYear = milestone.month_year;
      if (!acc[monthYear]) {
        acc[monthYear] = [];
      }
      acc[monthYear].push(milestone);
      return acc;
    }, {});

    return Object.entries(grouped).sort((a, b) => b[0].localeCompare(a[0]));
  };

  const calculateMonthlyStats = (monthMilestones) => {
    const totalHours = monthMilestones.reduce((sum, m) => sum + m.hours_invested, 0);
    const canTeachCount = monthMilestones.filter(m => m.can_teach).length;
    
    return {
      totalHours,
      canTeachCount,
      milestonesCount: monthMilestones.length,
      targetProgress: Math.min((totalHours / 6) * 100, 100)
    };
  };

  if (loading) {
    return (
      <div className="milestones-loading">
        <div className="spinner"></div>
        <p>Loading your milestones...</p>
      </div>
    );
  }

  const groupedMilestones = groupMilestonesByMonth(milestones);

  return (
    <div className="milestones-manager">
      <div className="milestones-header">
        <div className="header-content">
          <h2>Learning Milestones</h2>
          <p>Track your monthly learning achievements</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="add-milestone-btn"
        >
          {showForm ? 'Cancel' : '+ Add Milestone'}
        </button>
      </div>

      {showForm && (
        <div className="milestone-form-container">
          <form onSubmit={handleSubmit} className="milestone-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="goal_id" className="label">Related Goal (Optional)</label>
                <select
                  id="goal_id"
                  name="goal_id"
                  value={formData.goal_id}
                  onChange={handleInputChange}
                  className="select"
                >
                  <option value="">Select a goal...</option>
                  {goals.filter(g => g.status === 'active').map(goal => (
                    <option key={goal.id} value={goal.id}>
                      {goal.title}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="hours_invested" className="label">Hours Invested *</label>
                <input
                  type="number"
                  id="hours_invested"
                  name="hours_invested"
                  value={formData.hours_invested}
                  onChange={handleInputChange}
                  required
                  min="0.1"
                  step="0.1"
                  className="input"
                  placeholder="e.g., 2.5"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="what_learned" className="label">What have you learnt? *</label>
              <textarea
                id="what_learned"
                name="what_learned"
                value={formData.what_learned}
                onChange={handleInputChange}
                required
                className="textarea"
                placeholder="Describe what you learned in detail..."
                rows="3"
              />
            </div>

            <div className="form-group">
              <label htmlFor="source" className="label">From where have you learnt? *</label>
              <input
                type="text"
                id="source"
                name="source"
                value={formData.source}
                onChange={handleInputChange}
                required
                className="input"
                placeholder="e.g., YouTube, Coursera, Udemy, Books, Mentorship..."
              />
            </div>

            <div className="form-group">
              <label htmlFor="project_certificate_link" className="label">Project/Certificate Link</label>
              <input
                type="url"
                id="project_certificate_link"
                name="project_certificate_link"
                value={formData.project_certificate_link}
                onChange={handleInputChange}
                className="input"
                placeholder="https://..."
              />
            </div>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_teach"
                  checked={formData.can_teach}
                  onChange={handleInputChange}
                  className="checkbox"
                />
                <span className="checkmark"></span>
                Can you teach it to others?
              </label>
            </div>

            <div className="form-actions">
              <button type="button" onClick={resetForm} className="cancel-btn">
                Cancel
              </button>
              <button type="submit" disabled={submitting} className="submit-btn">
                {submitting ? (
                  <>
                    <div className="spinner small"></div>
                    Adding...
                  </>
                ) : (
                  'Add Milestone'
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="milestones-content">
        {milestones.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🏆</div>
            <h3>No Milestones Yet</h3>
            <p>Start tracking your learning journey by adding your first milestone!</p>
            <button onClick={() => setShowForm(true)} className="cta-button">
              Add Your First Milestone
            </button>
          </div>
        ) : (
          <div className="milestones-timeline">
            {groupedMilestones.map(([monthYear, monthMilestones]) => {
              const stats = calculateMonthlyStats(monthMilestones);
              const monthName = new Date(monthYear + '-01').toLocaleDateString('en-US', { 
                month: 'long', 
                year: 'numeric' 
              });

              return (
                <div key={monthYear} className="month-section">
                  <div className="month-header">
                    <h3>{monthName}</h3>
                    <div className="month-stats">
                      <div className="stat">
                        <span className="stat-value">{stats.totalHours}h</span>
                        <span className="stat-label">Total Hours</span>
                      </div>
                      <div className="stat">
                        <span className="stat-value">{stats.milestonesCount}</span>
                        <span className="stat-label">Milestones</span>
                      </div>
                      <div className="stat">
                        <span className="stat-value">{stats.canTeachCount}</span>
                        <span className="stat-label">Can Teach</span>
                      </div>
                      <div className="progress-indicator">
                        <div 
                          className="progress-circle-small"
                          style={{
                            background: `conic-gradient(
                              ${stats.targetProgress >= 100 ? '#00C851' : '#ff8800'} ${stats.targetProgress * 3.6}deg, 
                              #e0e0e0 0deg
                            )`
                          }}
                        >
                          <span>{Math.round(stats.targetProgress)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="milestones-list">
                    {monthMilestones.map((milestone) => (
                      <div key={milestone.id} className="milestone-card">
                        <div className="milestone-content">
                          <div className="milestone-main">
                            <h4>{milestone.what_learned}</h4>
                            <div className="milestone-meta">
                              <span className="milestone-source">
                                📚 {milestone.source}
                              </span>
                              <span className="milestone-hours">
                                ⏰ {milestone.hours_invested}h
                              </span>
                              {milestone.can_teach && (
                                <span className="teach-badge">
                                  👨‍🏫 Can teach
                                </span>
                              )}
                            </div>
                          </div>
                          
                          {milestone.project_certificate_link && (
                            <div className="milestone-link">
                              <a 
                                href={milestone.project_certificate_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="project-link"
                              >
                                🔗 View Project/Certificate
                              </a>
                            </div>
                          )}
                          
                          <div className="milestone-date">
                            Added on {formatDate(milestone.created_at)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default MilestonesManager;