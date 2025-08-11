import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/ResourceDirectory.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function ResourceDirectory({ user, profile }) {
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadResources();
  }, []);

  useEffect(() => {
    filterResources();
  }, [resources, selectedCategory, searchTerm]);

  const loadResources = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/resources`);
      setResources(response.data.resources);
      
      // Extract unique categories
      const uniqueCategories = [...new Set(response.data.resources.map(r => r.category))];
      setCategories(uniqueCategories);
    } catch (error) {
      console.error('Error loading resources:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterResources = () => {
    let filtered = resources;
    
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(resource => resource.category === selectedCategory);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(resource => 
        resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        resource.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        resource.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    setFilteredResources(filtered);
  };

  const ResourceCard = ({ resource }) => (
    <div className="resource-card">
      <div className="resource-header">
        <h3 className="resource-title">{resource.title}</h3>
        <span className="resource-category">{resource.category}</span>
      </div>
      <p className="resource-description">{resource.description}</p>
      <div className="resource-tags">
        {resource.tags.map((tag, index) => (
          <span key={index} className="resource-tag">#{tag}</span>
        ))}
      </div>
      <div className="resource-footer">
        <a 
          href={resource.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="resource-link"
        >
          Visit Resource 🔗
        </a>
        <span className="resource-date">
          Added {new Date(resource.created_at).toLocaleDateString()}
        </span>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="resource-directory">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading resources...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="resource-directory">
      <div className="resource-header">
        <h2>📚 Learning Resources</h2>
        <p>Discover curated learning resources approved by our team</p>
      </div>

      <div className="resource-filters">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search resources, tags, or descriptions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="category-filters">
          <button
            onClick={() => setSelectedCategory('all')}
            className={`category-btn ${selectedCategory === 'all' ? 'active' : ''}`}
          >
            All ({resources.length})
          </button>
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
            >
              {category} ({resources.filter(r => r.category === category).length})
            </button>
          ))}
        </div>
      </div>

      <div className="resources-grid">
        {filteredResources.length > 0 ? (
          filteredResources.map(resource => (
            <ResourceCard key={resource.id} resource={resource} />
          ))
        ) : (
          <div className="no-resources">
            <div className="no-resources-icon">📚</div>
            <h3>No resources found</h3>
            <p>
              {searchTerm || selectedCategory !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'No approved resources available yet'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResourceDirectory;