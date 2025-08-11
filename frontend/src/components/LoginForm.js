import React, { useState } from "react";
import "../styles/LoginForm.css";

function LoginForm({ onLogin }) {
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await onLogin(name);
    } catch (error) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">
            <span className="brand-text">Branding Pioneers</span>
            <br />
            Learning Platform
          </h1>
          <p className="login-subtitle">
            Enter your name to access the learning badge generator
          </p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="name" className="label">Your Name</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="login-input"
              placeholder="Enter your full name"
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !name.trim()}
            className="login-button"
          >
            {isLoading ? (
              <>
                <div className="spinner"></div>
                Logging in...
              </>
            ) : (
              'Access Platform'
            )}
          </button>
        </form>

        <div className="login-footer">
          <p>Administrators and users have different access levels</p>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;