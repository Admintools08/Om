import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/GoalsManager.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function GoalsManager({ user, profile }) {
  const [goals, setGoals] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    target_completion_date: ''
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadGoals();
  }, []);

  const loadGoals = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/goals`);
      setGoals(response.data.goals);
    } catch (error) {
      console.error('Error loading goals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const submitData = {
        ...formData,
        target_completion_date: new Date(formData.target_completion_date).toISOString()
      };

      if (editingGoal) {
        await axios.put(`${API}/goals/${editingGoal.id}`, submitData);
      } else {
        await axios.post(`${API}/goals`, submitData);
      }

      await loadGoals();
      resetForm();
    } catch (error) {
      console.error('Error saving goal:', error);
      alert('Failed to save goal. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      target_completion_date: ''
    });
    setShowForm(false);
    setEditingGoal(null);
  };

  const startEdit = (goal) => {
    setEditingGoal(goal);
    setFormData({
      title: goal.title,
      description: goal.description,
      target_completion_date: new Date(goal.target_completion_date).toISOString().split('T')[0]
    });
    setShowForm(true);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#00C851';
      case 'completed': return '#007bff';
      case 'paused': return '#ffbb33';
      default: return '#666';
    }
  };

  const getDaysUntilDeadline = (dateString) => {
    const deadline = new Date(dateString);
    const today = new Date();
    const diffTime = deadline - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return (
      <div className="goals-loading">
        <div className="spinner"></div>
        <p>Loading your learning goals...</p>
      </div>
    );
  }

  return (
    <div className="goals-manager">
      <div className="goals-header">
        <div className="header-content">
          <h2>Learning Goals</h2>
          <p>Set and track your learning objectives</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="add-goal-btn"
        >
          {showForm ? 'Cancel' : '+ Add Goal'}
        </button>
      </div>

      {showForm && (
        <div className="goal-form-container">
          <form onSubmit={handleSubmit} className="goal-form">
            <div className="form-group">
              <label htmlFor="title" className="label">Goal Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
                className="input"
                placeholder="e.g., Learn React Development"
              />
            </div>

            <div className="form-group">
              <label htmlFor="description" className="label">Description *</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                required
                className="textarea"
                placeholder="Describe what you want to achieve and why it's important..."
                rows="4"
              />
            </div>

            <div className="form-group">
              <label htmlFor="target_completion_date" className="label">Target Completion Date *</label>
              <input
                type="date"
                id="target_completion_date"
                name="target_completion_date"
                value={formData.target_completion_date}
                onChange={handleInputChange}
                required
                className="input"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>

            <div className="form-actions">
              <button type="button" onClick={resetForm} className="cancel-btn">
                Cancel
              </button>
              <button type="submit" disabled={submitting} className="submit-btn">
                {submitting ? (
                  <>
                    <div className="spinner small"></div>
                    {editingGoal ? 'Updating...' : 'Creating...'}
                  </>
                ) : (
                  editingGoal ? 'Update Goal' : 'Create Goal'
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="goals-list">
        {goals.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🎯</div>
            <h3>No Learning Goals Yet</h3>
            <p>Start your learning journey by setting your first goal!</p>
            <button onClick={() => setShowForm(true)} className="cta-button">
              Create Your First Goal
            </button>
          </div>
        ) : (
          <div className="goals-grid">
            {goals.map((goal) => {
              const daysLeft = getDaysUntilDeadline(goal.target_completion_date);
              
              return (
                <div key={goal.id} className="goal-card">
                  <div className="goal-header">
                    <h3>{goal.title}</h3>
                    <div className="goal-actions">
                      <span 
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(goal.status) }}
                      >
                        {goal.status}
                      </span>
                      <button
                        onClick={() => startEdit(goal)}
                        className="edit-btn"
                      >
                        ✏️
                      </button>
                    </div>
                  </div>
                  
                  <div className="goal-content">
                    <p className="goal-description">{goal.description}</p>
                    
                    <div className="goal-meta">
                      <div className="deadline-info">
                        <span className="meta-label">Target Date:</span>
                        <span className="meta-value">{formatDate(goal.target_completion_date)}</span>
                      </div>
                      
                      <div className="days-left">
                        {daysLeft > 0 ? (
                          <span className="days-remaining">{daysLeft} days left</span>
                        ) : daysLeft === 0 ? (
                          <span className="due-today">Due today!</span>
                        ) : (
                          <span className="overdue">{Math.abs(daysLeft)} days overdue</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="goal-progress">
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ 
                            width: goal.status === 'completed' ? '100%' : 
                                  goal.status === 'active' ? '50%' : '25%'
                          }}
                        ></div>
                      </div>
                      <span className="progress-text">
                        {goal.status === 'completed' ? 'Completed' : 'In Progress'}
                      </span>
                    </div>
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

export default GoalsManager;