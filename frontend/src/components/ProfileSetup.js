import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/ProfileSetup.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function ProfileSetup({ user, existingProfile, onProfileCreated }) {
  const [formData, setFormData] = useState({
    full_name: '',
    position: '',
    department: '',
    date_of_joining: '',
    existing_skills: [],
    learning_interests: [],
    profile_picture: ''
  });
  
  const [skillInput, setSkillInput] = useState('');
  const [interestInput, setInterestInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (existingProfile) {
      setFormData({
        full_name: existingProfile.full_name || '',
        position: existingProfile.position || '',
        department: existingProfile.department || '',
        date_of_joining: existingProfile.date_of_joining ? 
          new Date(existingProfile.date_of_joining).toISOString().split('T')[0] : '',
        existing_skills: existingProfile.existing_skills || [],
        learning_interests: existingProfile.learning_interests || [],
        profile_picture: existingProfile.profile_picture || ''
      });
    }
  }, [existingProfile]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addSkill = () => {
    if (skillInput.trim() && !formData.existing_skills.includes(skillInput.trim())) {
      setFormData(prev => ({
        ...prev,
        existing_skills: [...prev.existing_skills, skillInput.trim()]
      }));
      setSkillInput('');
    }
  };

  const removeSkill = (skill) => {
    setFormData(prev => ({
      ...prev,
      existing_skills: prev.existing_skills.filter(s => s !== skill)
    }));
  };

  const addInterest = () => {
    if (interestInput.trim() && !formData.learning_interests.includes(interestInput.trim())) {
      setFormData(prev => ({
        ...prev,
        learning_interests: [...prev.learning_interests, interestInput.trim()]
      }));
      setInterestInput('');
    }
  };

  const removeInterest = (interest) => {
    setFormData(prev => ({
      ...prev,
      learning_interests: prev.learning_interests.filter(i => i !== interest)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const submitData = {
        ...formData,
        date_of_joining: new Date(formData.date_of_joining).toISOString()
      };

      let response;
      if (existingProfile) {
        response = await axios.put(`${API}/profile`, submitData);
      } else {
        response = await axios.post(`${API}/profile`, submitData);
      }
      
      onProfileCreated(response.data);
    } catch (error) {
      console.error('Error saving profile:', error);
      setError(error.response?.data?.detail || 'Failed to save profile');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="profile-setup">
      <div className="profile-container">
        <div className="profile-header">
          <h2>{existingProfile ? 'Update Your Profile' : 'Complete Your Profile'}</h2>
          <p>Help us understand your learning journey and professional background</p>
        </div>

        <form onSubmit={handleSubmit} className="profile-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="full_name" className="label">Full Name *</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                required
                className="input"
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="position" className="label">Position *</label>
              <input
                type="text"
                id="position"
                name="position"
                value={formData.position}
                onChange={handleInputChange}
                required
                className="input"
                placeholder="e.g., Software Engineer, Marketing Manager"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="department" className="label">Department *</label>
              <select
                id="department"
                name="department"
                value={formData.department}
                onChange={handleInputChange}
                required
                className="select"
              >
                <option value="">Select Department</option>
                <option value="Engineering">Engineering</option>
                <option value="Marketing">Marketing</option>
                <option value="Sales">Sales</option>
                <option value="HR">Human Resources</option>
                <option value="Finance">Finance</option>
                <option value="Operations">Operations</option>
                <option value="Design">Design</option>
                <option value="Product">Product</option>
                <option value="Customer Success">Customer Success</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="date_of_joining" className="label">Date of Joining *</label>
              <input
                type="date"
                id="date_of_joining"
                name="date_of_joining"
                value={formData.date_of_joining}
                onChange={handleInputChange}
                required
                className="input"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="label">Existing Skills *</label>
            <div className="tag-input-container">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                className="tag-input"
                placeholder="Type a skill and press Enter"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addSkill();
                  }
                }}
              />
              <button type="button" onClick={addSkill} className="add-tag-btn">
                Add
              </button>
            </div>
            <div className="tags-container">
              {formData.existing_skills.map((skill, index) => (
                <span key={index} className="tag">
                  {skill}
                  <button
                    type="button"
                    onClick={() => removeSkill(skill)}
                    className="remove-tag"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="label">Learning Interests *</label>
            <div className="tag-input-container">
              <input
                type="text"
                value={interestInput}
                onChange={(e) => setInterestInput(e.target.value)}
                className="tag-input"
                placeholder="Type a learning interest and press Enter"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addInterest();
                  }
                }}
              />
              <button type="button" onClick={addInterest} className="add-tag-btn">
                Add
              </button>
            </div>
            <div className="tags-container">
              {formData.learning_interests.map((interest, index) => (
                <span key={index} className="tag">
                  {interest}
                  <button
                    type="button"
                    onClick={() => removeInterest(interest)}
                    className="remove-tag"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || formData.existing_skills.length === 0 || formData.learning_interests.length === 0}
            className="submit-button"
          >
            {isLoading ? (
              <>
                <div className="spinner"></div>
                {existingProfile ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              existingProfile ? 'Update Profile' : 'Complete Setup'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ProfileSetup;