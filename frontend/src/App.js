import React, { useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [formData, setFormData] = useState({
    employeeName: '',
    learning: '',
    difficulty: 'Easy'
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setResult(null);
    
    try {
      const response = await axios.post(`${API}/generate`, formData);
      setResult(response.data);
    } catch (error) {
      console.error('Error generating badge and post:', error);
      alert('Error generating content. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(result.linkedinPost);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">
            <span className="brand-text">Branding Pioneers</span>
            <br />
            Learning Badge Generator
          </h1>
          <p className="subtitle">
            Celebrate your learning achievements with beautiful badges and LinkedIn posts
          </p>
        </header>

        <div className="card">
          <form onSubmit={handleSubmit} className="form">
            <div className="form-group">
              <label htmlFor="employeeName" className="label">Your Name</label>
              <input
                type="text"
                id="employeeName"
                name="employeeName"
                value={formData.employeeName}
                onChange={handleInputChange}
                required
                className="input"
                placeholder="Enter your full name"
              />
            </div>

            <div className="form-group">
              <label htmlFor="learning" className="label">What did you learn?</label>
              <textarea
                id="learning"
                name="learning"
                value={formData.learning}
                onChange={handleInputChange}
                required
                className="textarea"
                placeholder="Describe what you learned today..."
                rows="4"
              />
            </div>

            <div className="form-group">
              <label htmlFor="difficulty" className="label">Difficulty Level</label>
              <select
                id="difficulty"
                name="difficulty"
                value={formData.difficulty}
                onChange={handleInputChange}
                className="select"
              >
                <option value="Easy">Easy</option>
                <option value="Moderate">Moderate</option>
                <option value="Hard">Hard</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="submit-button"
            >
              {isLoading ? (
                <>
                  <div className="spinner"></div>
                  Generating...
                </>
              ) : (
                'Generate Badge & Post'
              )}
            </button>
          </form>
        </div>

        {result && (
          <div className="results">
            <div className="success-message">
              🎉 Your badge & LinkedIn post are ready!
            </div>
            
            <div className="results-grid">
              <div className="badge-section">
                <h3 className="section-title">Your Learning Badge</h3>
                <div className="badge-container">
                  <img 
                    src={result.badgeUrl} 
                    alt="Learning Achievement Badge" 
                    className="badge-image"
                  />
                </div>
              </div>

              <div className="post-section">
                <h3 className="section-title">LinkedIn Post</h3>
                <div className="post-container">
                  <textarea
                    value={result.linkedinPost}
                    readOnly
                    className="post-textarea"
                    rows="8"
                  />
                  <button
                    onClick={copyToClipboard}
                    className="copy-button"
                  >
                    {copySuccess ? '✓ Copied!' : 'Copy to Clipboard'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <footer className="footer">
          Made with ❤️ by Branding Pioneers
        </footer>
      </div>
    </div>
  );
}

export default App;