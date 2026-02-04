import { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useParams, useSearchParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { Search, Book, Moon, Sun, ChevronRight, Download, ArrowLeft, Menu, X, BookOpen, Users, Sparkles, Tag } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Theme Context
const ThemeContext = createContext();

const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

const useTheme = () => useContext(ThemeContext);

// Category Icons mapping
const getCategoryIcon = (code) => {
  const icons = {
    COMM: "💬",
    DIGI: "📱",
    FMLY: "👨‍👩‍👧‍👦",
    FOUND: "📚",
    GLOB: "🌍",
    GNDR: "⚡",
    LIFE: "🌱",
    MENT: "🧠",
    MISC: "📖",
    PRNT: "❤️",
    SPEC: "✨",
    TEEN: "🎓"
  };
  return icons[code] || "📖";
};

// Header Component
const Header = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="header" data-testid="header">
      <div className="header-container">
        <Link to="/" className="logo" data-testid="logo-link">
          <div className="logo-icon">
            <BookOpen size={24} />
          </div>
          <span className="logo-text">ParentWise</span>
          <span className="logo-subtitle">Summaries</span>
        </Link>

        <nav className="nav-desktop" data-testid="desktop-nav">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/browse" className="nav-link">Browse All</Link>
          <Link to="/categories" className="nav-link">Categories</Link>
        </nav>

        <div className="header-actions">
          <button 
            onClick={toggleTheme} 
            className="theme-toggle"
            data-testid="theme-toggle"
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          <button 
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="mobile-menu-btn"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {mobileMenuOpen && (
          <nav className="nav-mobile" data-testid="mobile-nav">
            <Link to="/" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Home</Link>
            <Link to="/browse" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Browse All</Link>
            <Link to="/categories" className="nav-link" onClick={() => setMobileMenuOpen(false)}>Categories</Link>
          </nav>
        )}
      </div>
    </header>
  );
};

// Search Component
const SearchBar = ({ onSearch, initialValue = "" }) => {
  const [query, setQuery] = useState(initialValue);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className="search-form" data-testid="search-form">
      <div className="search-input-wrapper">
        <Search size={20} className="search-icon" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search book summaries..."
          className="search-input"
          data-testid="search-input"
        />
      </div>
      <button type="submit" className="btn-primary search-btn" data-testid="search-btn">
        Search
      </button>
    </form>
  );
};

// Category Card Component
const CategoryCard = ({ category, index }) => (
  <Link 
    to={`/browse?category=${category.code}`} 
    className={`category-card card-hover animate-fade-in-up stagger-${(index % 5) + 1}`}
    data-testid={`category-card-${category.code}`}
  >
    <span className="category-icon">{getCategoryIcon(category.code)}</span>
    <div className="category-info">
      <h3 className="category-name">{category.name}</h3>
      <p className="category-description">{category.description}</p>
      <span className="category-count">{category.count} summaries</span>
    </div>
    <ChevronRight size={20} className="category-arrow" />
  </Link>
);

// Summary Card Component
const SummaryCard = ({ summary, index }) => (
  <Link 
    to={`/summary/${summary.slug}`} 
    className={`summary-card card-hover animate-fade-in-up stagger-${(index % 5) + 1}`}
    data-testid={`summary-card-${summary.slug}`}
  >
    <div className="summary-category-badge">
      <span>{getCategoryIcon(summary.category_code)}</span>
      <span>{summary.category_name}</span>
    </div>
    <h3 className="summary-title">{summary.title}</h3>
    <p className="summary-author">by {summary.author}</p>
    {summary.key_principles && summary.key_principles.length > 0 && (
      <div className="summary-principles">
        {summary.key_principles.slice(0, 2).map((principle, i) => (
          <span key={i} className="principle-tag">{principle}</span>
        ))}
        {summary.key_principles.length > 2 && (
          <span className="principle-more">+{summary.key_principles.length - 2} more</span>
        )}
      </div>
    )}
    <div className="summary-footer">
      <span className="read-more">Read Summary <ChevronRight size={16} /></span>
    </div>
  </Link>
);

// Home Page
const Home = () => {
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [featuredSummaries, setFeaturedSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [catRes, statsRes, summariesRes] = await Promise.all([
          axios.get(`${API}/categories`),
          axios.get(`${API}/stats`),
          axios.get(`${API}/summaries?limit=6`)
        ]);
        setCategories(catRes.data);
        setStats(statsRes.data);
        setFeaturedSummaries(summariesRes.data.summaries);
      } catch (e) {
        console.error("Error fetching data:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSearch = (query) => {
    if (query.trim()) {
      navigate(`/browse?search=${encodeURIComponent(query)}`);
    }
  };

  if (loading) {
    return (
      <div className="loading-container" data-testid="loading">
        <div className="loading-spinner"></div>
        <p>Loading summaries...</p>
      </div>
    );
  }

  return (
    <div className="home-page" data-testid="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content animate-fade-in-up">
          <div className="hero-badge">
            <Sparkles size={16} />
            <span>Expert-Backed Parenting Insights</span>
          </div>
          <h1 className="hero-title">Book Summaries for<br /><span className="gradient-text">Thoughtful Parents</span></h1>
          <p className="hero-subtitle">
            Access {stats?.total_summaries || 247} comprehensive book summaries covering communication, 
            mental health, teenagers, and more—all designed to help you raise confident, resilient children.
          </p>
          <SearchBar onSearch={handleSearch} />
          <div className="hero-stats">
            <div className="stat">
              <BookOpen size={20} />
              <span><strong>{stats?.total_summaries || 247}</strong> Summaries</span>
            </div>
            <div className="stat">
              <Users size={20} />
              <span><strong>{stats?.total_authors || 200}+</strong> Authors</span>
            </div>
            <div className="stat">
              <Tag size={20} />
              <span><strong>{stats?.total_categories || 12}</strong> Categories</span>
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="section categories-section">
        <div className="section-header">
          <h2 className="section-title">Browse by Category</h2>
          <Link to="/categories" className="section-link">View All <ChevronRight size={16} /></Link>
        </div>
        <div className="categories-grid">
          {categories.slice(0, 6).map((category, index) => (
            <CategoryCard key={category.code} category={category} index={index} />
          ))}
        </div>
      </section>

      {/* Featured Summaries Section */}
      <section className="section featured-section">
        <div className="section-header">
          <h2 className="section-title">Featured Summaries</h2>
          <Link to="/browse" className="section-link">Browse All <ChevronRight size={16} /></Link>
        </div>
        <div className="summaries-grid">
          {featuredSummaries.map((summary, index) => (
            <SummaryCard key={summary.id} summary={summary} index={index} />
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="footer" data-testid="footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="logo">
              <div className="logo-icon">
                <BookOpen size={24} />
              </div>
              <span className="logo-text">ParentWise</span>
            </div>
            <p className="footer-tagline">FOCUSED • EMPATHETIC • EXPERT-BACKED</p>
          </div>
          <div className="footer-links">
            <Link to="/">Home</Link>
            <Link to="/browse">Browse</Link>
            <Link to="/categories">Categories</Link>
          </div>
          <p className="footer-copyright">© {new Date().getFullYear()} ParentWise. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

// Browse Page
const Browse = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [summaries, setSummaries] = useState([]);
  const [categories, setCategories] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const category = searchParams.get('category') || '';
  const search = searchParams.get('search') || '';

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (category) params.append('category', category);
        if (search) params.append('search', search);
        params.append('limit', '100');

        const [summariesRes, categoriesRes] = await Promise.all([
          axios.get(`${API}/summaries?${params.toString()}`),
          axios.get(`${API}/categories`)
        ]);
        
        setSummaries(summariesRes.data.summaries);
        setTotal(summariesRes.data.total);
        setCategories(categoriesRes.data);
      } catch (e) {
        console.error("Error fetching summaries:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [category, search]);

  const handleSearch = (query) => {
    const params = new URLSearchParams();
    if (query) params.set('search', query);
    if (category) params.set('category', category);
    setSearchParams(params);
  };

  const handleCategoryChange = (code) => {
    const params = new URLSearchParams();
    if (code) params.set('category', code);
    if (search) params.set('search', search);
    setSearchParams(params);
  };

  const currentCategory = categories.find(c => c.code === category);

  return (
    <div className="browse-page" data-testid="browse-page">
      <div className="browse-header">
        <h1 className="page-title">
          {currentCategory ? currentCategory.name : search ? `Search: "${search}"` : 'All Book Summaries'}
        </h1>
        <p className="page-subtitle">
          {total} {total === 1 ? 'summary' : 'summaries'} found
        </p>
      </div>

      <div className="browse-content">
        <aside className="browse-sidebar" data-testid="browse-sidebar">
          <div className="sidebar-search">
            <SearchBar onSearch={handleSearch} initialValue={search} />
          </div>
          
          <div className="filter-section">
            <h3 className="filter-title">Categories</h3>
            <div className="filter-options">
              <button
                className={`filter-option ${!category ? 'active' : ''}`}
                onClick={() => handleCategoryChange('')}
                data-testid="filter-all"
              >
                All Categories
              </button>
              {categories.map(cat => (
                <button
                  key={cat.code}
                  className={`filter-option ${category === cat.code ? 'active' : ''}`}
                  onClick={() => handleCategoryChange(cat.code)}
                  data-testid={`filter-${cat.code}`}
                >
                  <span>{getCategoryIcon(cat.code)}</span>
                  <span>{cat.name}</span>
                  <span className="filter-count">{cat.count}</span>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="browse-main">
          {loading ? (
            <div className="loading-container">
              <div className="loading-spinner"></div>
              <p>Loading summaries...</p>
            </div>
          ) : summaries.length === 0 ? (
            <div className="empty-state" data-testid="empty-state">
              <Book size={48} />
              <h3>No summaries found</h3>
              <p>Try adjusting your search or filters</p>
            </div>
          ) : (
            <div className="summaries-list">
              {summaries.map((summary, index) => (
                <SummaryCard key={summary.id} summary={summary} index={index} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

// Categories Page
const Categories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await axios.get(`${API}/categories`);
        setCategories(res.data);
      } catch (e) {
        console.error("Error fetching categories:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchCategories();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading categories...</p>
      </div>
    );
  }

  return (
    <div className="categories-page" data-testid="categories-page">
      <div className="page-header">
        <h1 className="page-title">All Categories</h1>
        <p className="page-subtitle">Explore {categories.length} curated categories of parenting wisdom</p>
      </div>
      
      <div className="categories-full-grid">
        {categories.map((category, index) => (
          <CategoryCard key={category.code} category={category} index={index} />
        ))}
      </div>
    </div>
  );
};

// Summary Detail Page
const SummaryDetail = () => {
  const { slug } = useParams();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await axios.get(`${API}/summaries/${slug}`);
        setSummary(res.data);
      } catch (e) {
        console.error("Error fetching summary:", e);
        setError("Summary not found");
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [slug]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading summary...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="error-page" data-testid="error-page">
        <Book size={64} />
        <h2>Summary Not Found</h2>
        <p>The summary you're looking for doesn't exist.</p>
        <button className="btn-primary" onClick={() => navigate('/browse')}>
          Browse All Summaries
        </button>
      </div>
    );
  }

  return (
    <div className="summary-page" data-testid="summary-page">
      <div className="summary-header">
        <button className="back-btn" onClick={() => navigate(-1)} data-testid="back-btn">
          <ArrowLeft size={20} />
          <span>Back</span>
        </button>

        <div className="summary-meta animate-fade-in-up">
          <Link 
            to={`/browse?category=${summary.category_code}`} 
            className="summary-category-link"
          >
            {getCategoryIcon(summary.category_code)} {summary.category_name}
          </Link>
          <h1 className="summary-page-title">{summary.title}</h1>
          <p className="summary-page-author">by {summary.author}</p>
          
          {summary.key_principles && summary.key_principles.length > 0 && (
            <div className="summary-key-principles">
              <h4>Key Principles:</h4>
              <div className="principles-list">
                {summary.key_principles.map((principle, i) => (
                  <span key={i} className="principle-tag">{principle}</span>
                ))}
              </div>
            </div>
          )}

          {summary.tags && summary.tags.length > 0 && (
            <div className="summary-tags">
              {summary.tags.map((tag, i) => (
                <span key={i} className="tag">{tag}</span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="summary-content-wrapper animate-fade-in-up stagger-2">
        <div 
          className="markdown-content"
          dangerouslySetInnerHTML={{ __html: summary.content_html }}
          data-testid="summary-content"
        />
      </div>
    </div>
  );
};

// Main App
function App() {
  return (
    <ThemeProvider>
      <div className="app">
        <BrowserRouter>
          <Header />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/browse" element={<Browse />} />
              <Route path="/categories" element={<Categories />} />
              <Route path="/summary/:slug" element={<SummaryDetail />} />
            </Routes>
          </main>
        </BrowserRouter>
      </div>
    </ThemeProvider>
  );
}

export default App;
