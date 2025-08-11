import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/Recommendations.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function Recommendations({ user, profile }) {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/recommendations`);
      setRecommendations(response.data);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshRecommendations = async () => {
    try {
      setRefreshing(true);
      await axios.post(`${API}/recommendations/refresh`);
      await loadRecommendations();
    } catch (error) {
      console.error('Error refreshing recommendations:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const filterRecommendations = (recommendations) => {
    if (!recommendations) return [];
    
    return recommendations.filter(rec => {
      if (selectedDifficulty !== 'all' && rec.difficulty_level !== selectedDifficulty) {
        return false;
      }
      return true;
    });
  };

  const getDisplayRecommendations = () => {
    if (!recommendations) return { paid: [], unpaid: [] };
    
    switch (activeTab) {
      case 'paid':
        return { paid: filterRecommendations(recommendations.paid_recommendations), unpaid: [] };
      case 'unpaid':
        return { paid: [], unpaid: filterRecommendations(recommendations.unpaid_recommendations) };
      default:
        return {
          paid: filterRecommendations(recommendations.paid_recommendations),
          unpaid: filterRecommendations(recommendations.unpaid_recommendations)
        };
    }
  };

  const RecommendationCard = ({ recommendation, isPaid }) => (
    <div className={`recommendation-card ${isPaid ? 'paid' : 'unpaid'}`}>
      <div className="recommendation-header">
        <div className="recommendation-title-section">
          <h3 className="recommendation-title">{recommendation.title}</h3>
          <div className="recommendation-meta">
            <span className="platform-badge">{recommendation.platform}</span>
            <span className={`difficulty-badge ${recommendation.difficulty_level}`}>
              {recommendation.difficulty_level}
            </span>
            <span className="hours-badge">
              {recommendation.estimated_hours}h
            </span>
            {isPaid && recommendation.price && (
              <span className="price-badge">{recommendation.price}</span>
            )}
          </div>
        </div>
        <div className={`category-indicator ${isPaid ? 'paid' : 'free'}`}>
          {isPaid ? '💳 Paid' : '🆓 Free'}
        </div>
      </div>
      
      <div className="recommendation-content">
        <p className="recommendation-description">{recommendation.description}</p>
        
        {recommendation.skill_tags && recommendation.skill_tags.length > 0 && (
          <div className="skill-tags">
            {recommendation.skill_tags.map((skill, index) => (
              <span key={index} className="skill-tag">{skill}</span>
            ))}
          </div>
        )}
        
        <div className="recommendation-reason">
          <div className="reason-icon">💡</div>
          <div className="reason-text">
            <strong>Why this is perfect for you:</strong> {recommendation.reason}
          </div>
        </div>
      </div>
      
      <div className="recommendation-footer">
        <a 
          href={recommendation.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="learn-now-btn"
        >
          <span>Start Learning</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </a>
        <div className="recommendation-stats">
          <span className="relevance-score">
            Match: {Math.round(recommendation.relevance_score * 100)}%
          </span>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="recommendations">
        <div className="loading-container">
          <div className="ai-spinner">
            <div className="spinner-ring"></div>
            <div className="spinner-text">AI is analyzing your learning profile...</div>
          </div>
        </div>
      </div>
    );
  }

  const displayRecs = getDisplayRecommendations();
  const totalCount = displayRecs.paid.length + displayRecs.unpaid.length;

  return (
    <div className="recommendations">
      <div className="recommendations-header">
        <div className="header-content">
          <h2>🚀 AI-Powered Learning Recommendations</h2>
          <p>Personalized suggestions based on your learning journey, goals, and interests</p>
          
          {recommendations && recommendations.personalization_factors && (
            <div className="personalization-info">
              <span className="info-label">Personalized using:</span>
              {recommendations.personalization_factors.map((factor, index) => (
                <span key={index} className="factor-badge">{factor}</span>
              ))}
            </div>
          )}
        </div>
        
        <div className="header-actions">
          <button 
            onClick={refreshRecommendations}
            disabled={refreshing}
            className="refresh-btn"
          >
            {refreshing ? (
              <>
                <div className="mini-spinner"></div>
                Refreshing...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C9.5 21 7.26392 19.9056 5.73392 18.1056" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M3 16V12H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                Refresh AI Recommendations
              </>
            )}
          </button>
        </div>
      </div>

      <div className="recommendations-filters">
        <div className="tab-filters">
          <button
            onClick={() => setActiveTab('all')}
            className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
          >
            All ({recommendations ? recommendations.total_count : 0})
          </button>
          <button
            onClick={() => setActiveTab('unpaid')}
            className={`tab-btn ${activeTab === 'unpaid' ? 'active' : ''}`}
          >
            🆓 Free ({recommendations ? recommendations.unpaid_recommendations.length : 0})
          </button>
          <button
            onClick={() => setActiveTab('paid')}
            className={`tab-btn ${activeTab === 'paid' ? 'active' : ''}`}
          >
            💳 Paid ({recommendations ? recommendations.paid_recommendations.length : 0})
          </button>
        </div>
        
        <div className="difficulty-filter">
          <select 
            value={selectedDifficulty} 
            onChange={(e) => setSelectedDifficulty(e.target.value)}
            className="difficulty-select"
          >
            <option value="all">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
      </div>

      <div className="recommendations-content">
        {totalCount === 0 ? (
          <div className="no-recommendations">
            <div className="no-rec-icon">🤖</div>
            <h3>No recommendations found</h3>
            <p>Try adjusting your filters or refresh to get new AI recommendations</p>
          </div>
        ) : (
          <div className="recommendations-grid">
            {/* Free Resources Section */}
            {displayRecs.unpaid.length > 0 && (
              <div className="recommendations-section">
                {activeTab === 'all' && (
                  <div className="section-header">
                    <h3>🆓 Free Learning Resources</h3>
                    <p>{displayRecs.unpaid.length} personalized recommendations</p>
                  </div>
                )}
                <div className="cards-grid">
                  {displayRecs.unpaid.map(rec => (
                    <RecommendationCard key={rec.id} recommendation={rec} isPaid={false} />
                  ))}
                </div>
              </div>
            )}

            {/* Paid Resources Section */}
            {displayRecs.paid.length > 0 && (
              <div className="recommendations-section">
                {activeTab === 'all' && (
                  <div className="section-header">
                    <h3>💳 Premium Learning Resources</h3>
                    <p>{displayRecs.paid.length} curated premium courses</p>
                  </div>
                )}
                <div className="cards-grid">
                  {displayRecs.paid.map(rec => (
                    <RecommendationCard key={rec.id} recommendation={rec} isPaid={true} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Recommendations;