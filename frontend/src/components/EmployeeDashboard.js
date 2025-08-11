import React, { useState, useEffect } from "react";
import axios from "axios";
import ProfileSetup from "./ProfileSetup";
import LearningDashboard from "./LearningDashboard";
import GoalsManager from "./GoalsManager";
import MilestonesManager from "./MilestonesManager";
import ResourceDirectory from "./ResourceDirectory";
import PeerLearning from "./PeerLearning";
import BadgeGenerator from "./BadgeGenerator";
import "../styles/EmployeeDashboard.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function EmployeeDashboard({ user }) {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setProfileLoading(true);
      const response = await axios.get(`${API}/profile`);
      setProfile(response.data);
    } catch (error) {
      if (error.response?.status === 404) {
        // Profile doesn't exist, user needs to create one
        setProfile(null);
        setActiveTab('profile');
      } else {
        console.error('Error loading profile:', error);
      }
    } finally {
      setProfileLoading(false);
    }
  };

  const handleProfileCreated = (newProfile) => {
    setProfile(newProfile);
    setActiveTab('dashboard');
  };

  const TabButton = ({ tabId, label, icon, isActive, onClick, disabled = false }) => (
    <button
      onClick={() => onClick(tabId)}
      className={`tab-button ${isActive ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
      disabled={disabled}
    >
      <span className="tab-icon">{icon}</span>
      {label}
    </button>
  );

  if (profileLoading) {
    return (
      <div className="employee-loading">
        <div className="spinner"></div>
        <p>Loading your profile...</p>
      </div>
    );
  }

  // If no profile exists, force profile setup
  if (!profile && activeTab !== 'profile') {
    return (
      <div className="employee-dashboard">
        <div className="profile-required-message">
          <h2>👋 Welcome to the Learning Platform!</h2>
          <p>Please complete your profile to get started with your learning journey.</p>
        </div>
        <ProfileSetup user={user} onProfileCreated={handleProfileCreated} />
      </div>
    );
  }

  return (
    <div className="employee-dashboard">
      <div className="dashboard-navigation">
        <div className="nav-tabs">
          <TabButton
            tabId="dashboard"
            label="Dashboard"
            icon="📊"
            isActive={activeTab === 'dashboard'}
            onClick={setActiveTab}
            disabled={!profile}
          />
          <TabButton
            tabId="profile"
            label="Profile"
            icon="👤"
            isActive={activeTab === 'profile'}
            onClick={setActiveTab}
          />
          <TabButton
            tabId="goals"
            label="Goals"
            icon="🎯"
            isActive={activeTab === 'goals'}
            onClick={setActiveTab}
            disabled={!profile}
          />
          <TabButton
            tabId="milestones"
            label="Milestones"
            icon="🏆"
            isActive={activeTab === 'milestones'}
            onClick={setActiveTab}
            disabled={!profile}
          />
          <TabButton
            tabId="badge-generator"
            label="Badge Generator"
            icon="🏅"
            isActive={activeTab === 'badge-generator'}
            onClick={setActiveTab}
            disabled={!profile}
          />
          <TabButton
            tabId="resources"
            label="Resources"
            icon="📚"
            isActive={activeTab === 'resources'}
            onClick={setActiveTab}
            disabled={!profile}
          />
          <TabButton
            tabId="peers"
            label="Peer Learning"
            icon="👥"
            isActive={activeTab === 'peers'}
            onClick={setActiveTab}
            disabled={!profile}
          />
        </div>
      </div>

      <div className="dashboard-content">
        {activeTab === 'dashboard' && profile && (
          <LearningDashboard user={user} profile={profile} />
        )}
        
        {activeTab === 'profile' && (
          <ProfileSetup 
            user={user} 
            existingProfile={profile}
            onProfileCreated={handleProfileCreated} 
          />
        )}
        
        {activeTab === 'goals' && profile && (
          <GoalsManager user={user} profile={profile} />
        )}
        
        {activeTab === 'milestones' && profile && (
          <MilestonesManager user={user} profile={profile} />
        )}
        
        {activeTab === 'badge-generator' && profile && (
          <BadgeGenerator />
        )}
        
        {activeTab === 'resources' && profile && (
          <ResourceDirectory user={user} profile={profile} />
        )}
        
        {activeTab === 'peers' && profile && (
          <PeerLearning user={user} profile={profile} />
        )}
      </div>
    </div>
  );
}

export default EmployeeDashboard;