import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/PeerLearning.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PeerLearning({ user, profile }) {
  const [peers, setPeers] = useState([]);
  const [filteredPeers, setFilteredPeers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [skillFilter, setSkillFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPeers();
  }, []);

  useEffect(() => {
    filterPeers();
  }, [peers, selectedDepartment, skillFilter]);

  const loadPeers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/peers`);
      setPeers(response.data.peers);
      
      // Extract unique departments
      const uniqueDepartments = [...new Set(response.data.peers.map(p => p.department))];
      setDepartments(uniqueDepartments);
    } catch (error) {
      console.error('Error loading peers:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterPeers = () => {
    let filtered = peers;
    
    if (selectedDepartment !== 'all') {
      filtered = filtered.filter(peer => peer.department === selectedDepartment);
    }
    
    if (skillFilter) {
      filtered = filtered.filter(peer => 
        peer.existing_skills.some(skill => 
          skill.toLowerCase().includes(skillFilter.toLowerCase())
        ) ||
        peer.learning_interests.some(interest => 
          interest.toLowerCase().includes(skillFilter.toLowerCase())
        )
      );
    }
    
    setFilteredPeers(filtered);
  };

  const handleBookmark = async (peerId) => {
    try {
      await axios.post(`${API}/bookmarks/${peerId}`);
      // Could add toast notification here
      console.log('Peer bookmarked successfully');
    } catch (error) {
      if (error.response?.status === 400) {
        console.log('Peer already bookmarked');
      } else {
        console.error('Error bookmarking peer:', error);
      }
    }
  };

  const PeerCard = ({ peer }) => (
    <div className="peer-card">
      <div className="peer-header">
        <div className="peer-avatar">
          {peer.profile_picture ? (
            <img src={peer.profile_picture} alt={peer.full_name} />
          ) : (
            <div className="avatar-placeholder">
              {peer.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
            </div>
          )}
        </div>
        <div className="peer-info">
          <h3 className="peer-name">{peer.full_name}</h3>
          <p className="peer-role">{peer.position}</p>
          <p className="peer-department">{peer.department}</p>
        </div>
        <button 
          onClick={() => handleBookmark(peer.id)}
          className="bookmark-btn"
          title="Bookmark this peer"
        >
          🔖
        </button>
      </div>
      
      <div className="peer-skills">
        <div className="skills-section">
          <h4>💼 Current Skills</h4>
          <div className="skills-tags">
            {peer.existing_skills.slice(0, 4).map((skill, index) => (
              <span key={index} className="skill-tag existing">{skill}</span>
            ))}
            {peer.existing_skills.length > 4 && (
              <span className="skill-tag more">+{peer.existing_skills.length - 4} more</span>
            )}
          </div>
        </div>
        
        <div className="skills-section">
          <h4>🌱 Learning Interests</h4>
          <div className="skills-tags">
            {peer.learning_interests.slice(0, 4).map((interest, index) => (
              <span key={index} className="skill-tag learning">{interest}</span>
            ))}
            {peer.learning_interests.length > 4 && (
              <span className="skill-tag more">+{peer.learning_interests.length - 4} more</span>
            )}
          </div>
        </div>
      </div>

      {peer.recent_milestones.length > 0 && (
        <div className="peer-milestones">
          <h4>🏆 Recent Learning</h4>
          {peer.recent_milestones.slice(0, 2).map((milestone, index) => (
            <div key={index} className="milestone-item">
              <div className="milestone-content">
                <p className="milestone-learning">{milestone.what_learned}</p>
                <div className="milestone-details">
                  <span className="milestone-source">📚 {milestone.source}</span>
                  <span className="milestone-hours">⏱️ {milestone.hours_invested}h</span>
                  {milestone.can_teach && (
                    <span className="can-teach">✋ Can teach this</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="peer-learning">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Finding your learning peers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="peer-learning">
      <div className="peer-header">
        <h2>👥 Peer Learning Network</h2>
        <p>Connect with colleagues, discover skills, and learn together</p>
      </div>

      <div className="peer-filters">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search by skills or learning interests..."
            value={skillFilter}
            onChange={(e) => setSkillFilter(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="department-filters">
          <button
            onClick={() => setSelectedDepartment('all')}
            className={`dept-btn ${selectedDepartment === 'all' ? 'active' : ''}`}
          >
            All Departments ({peers.length})
          </button>
          {departments.map(dept => (
            <button
              key={dept}
              onClick={() => setSelectedDepartment(dept)}
              className={`dept-btn ${selectedDepartment === dept ? 'active' : ''}`}
            >
              {dept} ({peers.filter(p => p.department === dept).length})
            </button>
          ))}
        </div>
      </div>

      <div className="peers-grid">
        {filteredPeers.length > 0 ? (
          filteredPeers.map(peer => (
            <PeerCard key={peer.id} peer={peer} />
          ))
        ) : (
          <div className="no-peers">
            <div className="no-peers-icon">👥</div>
            <h3>No peers found</h3>
            <p>
              {skillFilter || selectedDepartment !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'No peer profiles available yet'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default PeerLearning;