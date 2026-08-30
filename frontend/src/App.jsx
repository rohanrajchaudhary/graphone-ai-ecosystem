import React, { useEffect, useState } from "react";
import "./App.css";

const API = "https://graphone-ai-ecosystem.onrender.com";

const PAPERS_PER_PAGE = 50;
const ENTITY_PAGE_SIZE = 50;

function App() {
  const [stats, setStats] = useState(null);
  const [activeTab, setActiveTab] = useState("Dashboard");

  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("graphone-theme") === "dark";
  });

  const [search, setSearch] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.body.className = darkMode ? "dark-mode" : "";
    localStorage.setItem("graphone-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  const loadStats = async () => {
    try {
      const response = await fetch(`${API}/api/stats`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Failed to load stats:", error);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!search.trim()) {
      setSearchResults(null);
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        `${API}/api/search?q=${encodeURIComponent(search.trim())}&limit=20`
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setSearchResults(data);
    } catch (error) {
      console.error("Search failed:", error);
      setSearchResults(null);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    try {
      setLoading(true);

      const response = await fetch(`${API}/api/reload`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await loadStats();
    } catch (error) {
      console.error("Reload failed:", error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    "Dashboard",
    "Startups",
    "Products",
    "Research",
    "Entities",
    "Fresh Intelligence",
  ];

  const cards = [
    {
      title: "Research Papers",
      value: stats?.researchPapers ?? 0,
      icon: "▤",
      description: "Indexed research records",
    },
    {
      title: "AI Entities",
      value: stats?.aiEntities ?? 0,
      icon: "◇",
      description: "Classified AI ecosystem entities",
    },
    {
      title: "Startups",
      value: stats?.startups ?? 0,
      icon: "◈",
      description: "AI startup records",
    },
    {
      title: "Products",
      value: stats?.products ?? 0,
      icon: "▣",
      description: "AI products and projects",
    },
    {
      title: "Fresh News",
      value: stats?.freshNews ?? 0,
      icon: "◉",
      description: "Recently collected AI news",
    },
    {
      title: "Job Sources",
      value: stats?.jobSources ?? 0,
      icon: "▤",
      description: "Monitored job sources",
    },
  ];

  return (
    <div className="app">
      {/* HEADER */}
      <header className="top-header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-mark">G</div>
            <div>
              <div className="brand-name">GRAPHONE</div>
              <div className="brand-subtitle">AI Ecosystem Intelligence</div>
            </div>
          </div>

          <div className="header-actions">
            <div className="system-status">
              <span className="status-dot"></span>
              System Online
            </div>

            <button
              className="theme-button"
              onClick={() => setDarkMode(!darkMode)}
            >
              {darkMode ? "☀ Light" : "☾ Night"}
            </button>

            <button className="refresh-button" onClick={refreshData}>
              ↻ Refresh
            </button>

            <a
              href={`${API}/docs`}
              target="_blank"
              rel="noreferrer"
              className="docs-link"
            >
              API Docs ↗
            </a>
          </div>
        </div>
      </header>

      {/* NAVIGATION */}
      <nav className="main-nav">
        <div className="nav-inner">
          {tabs.map((tab) => (
            <button
              key={tab}
              className={activeTab === tab ? "nav-item active" : "nav-item"}
              onClick={() => {
                setActiveTab(tab);
                setSearchResults(null);
              }}
            >
              {tab}
            </button>
          ))}
        </div>
      </nav>

      {/* GLOBAL SEARCH RESULTS */}
      {searchResults && (
        <main className="container">
          <section className="page-heading">
            <div>
              <div className="breadcrumb">Home / Search</div>
              <h1>Search Results</h1>
              <p>
                Results for <strong>"{searchResults.query}"</strong>
              </p>
            </div>

            <div className="dataset-status">
              <span className="status-dot"></span>
              {(
                (searchResults.paperCount || 0) +
                (searchResults.entityCount || 0)
              ).toLocaleString()}{" "}
              Results
            </div>
          </section>

          <SearchResults
            data={searchResults}
            onClear={() => setSearchResults(null)}
          />
        </main>
      )}

      {/* TABS */}
      {!searchResults && activeTab === "Dashboard" && (
        <Dashboard
          stats={stats}
          cards={cards}
          search={search}
          setSearch={setSearch}
          handleSearch={handleSearch}
          loading={loading}
          setActiveTab={setActiveTab}
        />
      )}

      {!searchResults && activeTab === "Research" && <ResearchTab />}

      {!searchResults && activeTab === "Startups" && (
        <EntityCollectionTab
          title="AI Startups"
          subtitle="Discover AI startups and organizations collected by the GraphOne pipeline."
          endpoint="/api/startups"
          emptyText="No startup records found."
        />
      )}

      {!searchResults && activeTab === "Products" && (
        <EntityCollectionTab
          title="AI Products"
          subtitle="Explore AI products, tools and ecosystem projects."
          endpoint="/api/products"
          emptyText="No product records found."
        />
      )}

      {!searchResults && activeTab === "Entities" && <EntitiesTab />}

      {!searchResults && activeTab === "Fresh Intelligence" && (
        <FreshIntelligenceTab />
      )}

      {/* FOOTER */}
      <footer className="footer">
        <div>GRAPHONE AI Ecosystem Intelligence</div>
        <div>Dataset-driven intelligence platform</div>
      </footer>
    </div>
  );
}

/* ============================================================
   DASHBOARD
============================================================ */

function Dashboard({
  stats,
  cards,
  search,
  setSearch,
  handleSearch,
  loading,
  setActiveTab,
}) {
  return (
    <main className="container">
      <section className="page-heading">
        <div>
          <div className="breadcrumb">Home / Dashboard</div>
          <h1>AI Ecosystem Intelligence Dashboard</h1>
          <p>
            Explore structured intelligence collected and processed through the
            GraphOne data pipeline.
          </p>
        </div>

        <div className="dataset-status">
          <span className="status-dot"></span>
          Dataset Operational
        </div>
      </section>

      {/* SEARCH */}
      <section className="search-panel">
        <form onSubmit={handleSearch}>
          <div className="search-box">
            <span className="search-icon">⌕</span>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search startups, products, papers or AI entities..."
            />
            <button type="submit">
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
        </form>
      </section>

      {/* STATS */}
      <section className="stats-grid">
        {cards.map((card) => (
          <div className="stat-card" key={card.title}>
            <div className="stat-top">
              <div className="stat-icon">{card.icon}</div>
              <span className="live-label">LIVE</span>
            </div>
            <div className="stat-value">
              {Number(card.value).toLocaleString()}
            </div>
            <div className="stat-title">{card.title}</div>
            <div className="stat-description">{card.description}</div>
          </div>
        ))}
      </section>

      {/* EXPLORE */}
      <section className="content-section">
        <div className="section-header">
          <div>
            <div className="section-kicker">DATA EXPLORATION</div>
            <h2>Explore Dataset</h2>
            <p>Navigate through the processed AI ecosystem intelligence.</p>
          </div>
        </div>

        <div className="explore-grid">
          <ExploreCard
            title="Startups"
            description="Discover AI startups and organizations."
            value={stats?.startups}
            onClick={() => setActiveTab("Startups")}
          />
          <ExploreCard
            title="Products"
            description="Explore AI products and projects."
            value={stats?.products}
            onClick={() => setActiveTab("Products")}
          />
          <ExploreCard
            title="Research Papers"
            description="Browse indexed AI research papers."
            value={stats?.researchPapers}
            onClick={() => setActiveTab("Research")}
          />
          <ExploreCard
            title="AI Entities"
            description="Explore classified ecosystem entities."
            value={stats?.aiEntities}
            onClick={() => setActiveTab("Entities")}
          />
          <ExploreCard
            title="Fresh Intelligence"
            description="View recently collected AI intelligence."
            value={stats?.freshNews}
            onClick={() => setActiveTab("Fresh Intelligence")}
          />
        </div>
      </section>

      {/* PIPELINE */}
      <section className="pipeline-panel">
        <div className="pipeline-header">
          <div>
            <div className="section-kicker">PIPELINE STATUS</div>
            <h2>GraphOne Data Pipeline</h2>
          </div>
          <div className="online-badge">
            <span className="status-dot"></span>
            Operational
          </div>
        </div>

        <div className="pipeline-grid">
          <PipelineItem
            title="Research Acquisition"
            value={`${stats?.researchPapers ?? 0} records`}
          />
          <PipelineItem
            title="Entity Classification"
            value={`${stats?.aiEntities ?? 0} entities`}
          />
          <PipelineItem
            title="Entity Resolution"
            value={`${stats?.paperEntityLinks ?? 0} links`}
          />
          <PipelineItem
            title="Fresh Intelligence"
            value={`${stats?.freshNews ?? 0} news items`}
          />
        </div>
      </section>
    </main>
  );
}

/* ============================================================
   RESEARCH TAB
============================================================ */

function ResearchTab() {
  const [papers, setPapers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const totalPages = Math.max(1, Math.ceil(total / PAPERS_PER_PAGE));

  const loadPapers = async () => {
    try {
      setLoading(true);
      setError("");

      const offset = (page - 1) * PAPERS_PER_PAGE;
      let url = `${API}/api/papers?limit=${PAPERS_PER_PAGE}&offset=${offset}`;

      if (search.trim()) {
        url += `&q=${encodeURIComponent(search.trim())}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setPapers(Array.isArray(data.items) ? data.items : []);
      setTotal(Number(data.total) || 0);
    } catch (err) {
      console.error("Research loading failed:", err);
      setError("Unable to load research papers.");
      setPapers([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPapers();
  }, [page]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadPapers();
  };

  const formatDate = (paper) => {
    const date =
      paper.published_date ||
      paper.publishedDate ||
      paper.published ||
      null;

    if (!date) {
      return "Publication date unavailable";
    }

    try {
      return new Date(date).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
    } catch {
      return String(date);
    }
  };

  const getAuthors = (paper) => {
    if (Array.isArray(paper.authors) && paper.authors.length > 0) {
      if (paper.authors.length <= 3) {
        return paper.authors.join(", ");
      }
      return `${paper.authors.slice(0, 3).join(", ")} +${
        paper.authors.length - 3
      } more`;
    }
    return "Authors unavailable";
  };

  const getSourceUrl = (paper) => {
    return (
      paper.sourceUrl ||
      paper.source_url ||
      paper.arxiv_url ||
      paper.arxivUrl ||
      null
    );
  };

  const getAbstract = (paper) => {
    return paper.abstract || "Abstract unavailable for this record.";
  };

  return (
    <main className="container research-page">
      <section className="page-heading">
        <div>
          <div className="breadcrumb">Home / Research</div>
          <h1>Research Papers</h1>
          <p>
            Browse indexed AI research papers collected through the GraphOne
            research pipeline.
          </p>
        </div>

        <div className="dataset-status">
          <span className="status-dot"></span>
          {total.toLocaleString()} Papers Indexed
        </div>
      </section>

      <section className="research-search-panel">
        <form onSubmit={handleSearch}>
          <div className="research-search">
            <span>⌕</span>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search research papers by title or abstract..."
            />
            <button type="submit">Search</button>
          </div>
        </form>
      </section>

      <div className="research-toolbar">
        <div>
          <strong>Research Database</strong>
          <span>
            {" "}• Showing{" "}
            {total === 0 ? 0 : (page - 1) * PAPERS_PER_PAGE + 1} -{" "}
            {Math.min(page * PAPERS_PER_PAGE, total)} of{" "}
            {total.toLocaleString()}
          </span>
        </div>

        <div className="page-indicator">
          Page {page} of {totalPages}
        </div>
      </div>

      {error && <div className="research-error">{error}</div>}

      {loading ? (
        <div className="research-loading">
          <div className="loading-spinner"></div>
          <div>Loading research papers...</div>
        </div>
      ) : papers.length === 0 ? (
        <div className="research-empty">
          <div className="empty-icon">▤</div>
          <h3>No research papers found</h3>
          <p>Try another search term.</p>
        </div>
      ) : (
        <section className="papers-list">
          {papers.map((paper, index) => {
            const sourceUrl = getSourceUrl(paper);

            return (
              <article
                className="paper-card"
                key={
                  paper.id ||
                  paper.arxiv_url ||
                  paper.sourceUrl ||
                  index
                }
              >
                <div className="paper-card-header">
                  <div className="paper-number">
                    #{(page - 1) * PAPERS_PER_PAGE + index + 1}
                  </div>
                  <div className="paper-type">RESEARCH PAPER</div>
                </div>

                <h2 className="paper-title">
                  {paper.title || "Untitled Research Paper"}
                </h2>

                <div className="paper-meta">
                  <div className="paper-authors">
                    <span className="meta-label">AUTHORS</span>
                    <span>{getAuthors(paper)}</span>
                  </div>

                  <div className="paper-date">
                    <span className="meta-label">PUBLISHED</span>
                    <span>{formatDate(paper)}</span>
                  </div>
                </div>

                <div className="paper-abstract">
                  <span className="meta-label">ABSTRACT</span>
                  <p>{getAbstract(paper)}</p>
                </div>

                <div className="paper-footer">
                  <div className="paper-source">
                    <span className="source-dot"></span>
                    {sourceUrl ? "Source available" : "Source unavailable"}
                  </div>

                  {sourceUrl && (
                    <a
                      href={sourceUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="paper-link"
                    >
                      View Paper ↗
                    </a>
                  )}
                </div>
              </article>
            );
          })}
        </section>
      )}

      {!loading && total > 0 && (
        <div className="pagination">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ← Previous
          </button>

          <div className="pagination-pages">
            {getPageNumbers(page, totalPages).map((pageNumber, index) => {
              if (pageNumber === "...") {
                return (
                  <span key={`dots-${index}`} className="pagination-dots">
                    ...
                  </span>
                );
              }

              return (
                <button
                  key={pageNumber}
                  className={
                    pageNumber === page
                      ? "page-number active"
                      : "page-number"
                  }
                  onClick={() => setPage(pageNumber)}
                >
                  {pageNumber}
                </button>
              );
            })}
          </div>

          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </main>
  );
}

/* ============================================================
   STARTUPS / PRODUCTS
============================================================ */

function EntityCollectionTab({ title, subtitle, endpoint, emptyText }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadItems = async () => {
    try {
      setLoading(true);
      setError("");

      let url = `${API}${endpoint}?limit=500`;

      if (search.trim()) {
        url += `&q=${encodeURIComponent(search.trim())}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setItems(Array.isArray(data.items) ? data.items : []);
      setTotal(Number(data.total) || 0);
    } catch (err) {
      console.error(err);
      setError(`Unable to load ${title.toLowerCase()}.`);
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    loadItems();
  };

  return (
    <main className="container">
      <section className="page-heading">
        <div>
          <div className="breadcrumb">Home / {title}</div>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>

        <div className="dataset-status">
          <span className="status-dot"></span>
          {total.toLocaleString()} Records
        </div>
      </section>

      <section className="research-search-panel">
        <form onSubmit={handleSubmit}>
          <div className="research-search">
            <span>⌕</span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={`Search ${title.toLowerCase()}...`}
            />
            <button type="submit">Search</button>
          </div>
        </form>
      </section>

      {error && <div className="research-error">{error}</div>}

      {loading ? (
        <div className="research-loading">
          <div className="loading-spinner"></div>
          Loading records...
        </div>
      ) : items.length === 0 ? (
        <div className="research-empty">
          <div className="empty-icon">◇</div>
          <h3>{emptyText}</h3>
          <p>Try another search term.</p>
        </div>
      ) : (
        <section className="entity-grid">
          {items.map((item, index) => (
            <EntityCard
              key={
                item.id ||
                item.entityId ||
                item.entityName ||
                index
              }
              item={item}
            />
          ))}
        </section>
      )}
    </main>
  );
}

/* ============================================================
   ENTITIES
============================================================ */

function EntitiesTab() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [type, setType] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const totalPages = Math.max(1, Math.ceil(total / ENTITY_PAGE_SIZE));

  const loadEntities = async () => {
    try {
      setLoading(true);
      setError("");

      const offset = (page - 1) * ENTITY_PAGE_SIZE;
      let url = `${API}/api/entities?limit=${ENTITY_PAGE_SIZE}&offset=${offset}`;

      if (search.trim()) {
        url += `&q=${encodeURIComponent(search.trim())}`;
      }

      if (type) {
        url += `&type=${encodeURIComponent(type)}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setItems(Array.isArray(data.items) ? data.items : []);
      setTotal(Number(data.total) || 0);
    } catch (err) {
      console.error(err);
      setError("Unable to load AI entities.");
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEntities();
  }, [page, type]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    loadEntities();
  };

  return (
    <main className="container">
      <section className="page-heading">
        <div>
          <div className="breadcrumb">Home / Entities</div>
          <h1>AI Entities</h1>
          <p>
            Explore classified entities across the GraphOne AI ecosystem dataset.
          </p>
        </div>

        <div className="dataset-status">
          <span className="status-dot"></span>
          {total.toLocaleString()} Entities
        </div>
      </section>

      <section className="research-search-panel">
        <form onSubmit={handleSearch}>
          <div className="research-search">
            <span>⌕</span>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search entities..."
            />
            <select
              value={type}
              onChange={(e) => {
                setType(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Types</option>
              <option value="STARTUP">Startups</option>
              <option value="PRODUCT">Products</option>
              <option value="ORGANIZATION">Organizations</option>
              <option value="OPEN_SOURCE_PROJECT">Open Source</option>
            </select>
            <button type="submit">Search</button>
          </div>
        </form>
      </section>

      <div className="research-toolbar">
        <div>
          <strong>Entity Database</strong>
          <span>
            {" "}• Showing{" "}
            {total === 0 ? 0 : (page - 1) * ENTITY_PAGE_SIZE + 1} -{" "}
            {Math.min(page * ENTITY_PAGE_SIZE, total)} of{" "}
            {total.toLocaleString()}
          </span>
        </div>

        <div className="page-indicator">
          Page {page} of {totalPages}
        </div>
      </div>

      {error && <div className="research-error">{error}</div>}

      {loading ? (
        <div className="research-loading">
          <div className="loading-spinner"></div>
          Loading entities...
        </div>
      ) : items.length === 0 ? (
        <div className="research-empty">
          <div className="empty-icon">◇</div>
          <h3>No entities found</h3>
          <p>Try another filter or search term.</p>
        </div>
      ) : (
        <section className="entity-grid">
          {items.map((item, index) => (
            <EntityCard
              key={
                item.id ||
                item.entityId ||
                item.entityName ||
                index
              }
              item={item}
            />
          ))}
        </section>
      )}

      {!loading && total > 0 && (
        <div className="pagination">
          <button
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            ← Previous
          </button>

          <div className="pagination-pages">
            {getPageNumbers(page, totalPages).map((number, index) => {
              if (number === "...") {
                return (
                  <span key={`dots-${index}`} className="pagination-dots">
                    ...
                  </span>
                );
              }

              return (
                <button
                  key={number}
                  className={
                    number === page
                      ? "page-number active"
                      : "page-number"
                  }
                  onClick={() => setPage(number)}
                >
                  {number}
                </button>
              );
            })}
          </div>

          <button
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next →
          </button>
        </div>
      )}
    </main>
  );
}

/* ============================================================
   ENTITY CARD
============================================================ */

function EntityCard({ item }) {
  const name =
    item.entityName ||
    item.name ||
    item.title ||
    "Unnamed Entity";

  const type =
    item.entityType ||
    item.type ||
    "UNKNOWN";

  const description =
    item.description ||
    item.summary ||
    item.about ||
    "No description available for this entity.";

  const website =
    item.website ||
    item.url ||
    item.sourceUrl ||
    null;

  return (
    <article className="entity-card">
      <div className="entity-card-top">
        <div className="entity-icon">◈</div>
        <span className="entity-type">
          {String(type).replaceAll("_", " ")}
        </span>
      </div>

      <h2>{name}</h2>
      <p>{description}</p>

      <div className="entity-footer">
        <span>GraphOne Entity</span>
        {website && (
          <a href={website} target="_blank" rel="noreferrer">
            Visit ↗
          </a>
        )}
      </div>
    </article>
  );
}

/* ============================================================
   FRESH INTELLIGENCE
============================================================ */

function FreshIntelligenceTab() {
  const [data, setData] = useState({
    news: [],
    jobs: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadFresh = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API}/api/fresh`);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const result = await response.json();
        setData({
          news: Array.isArray(result.news) ? result.news : [],
          jobs: Array.isArray(result.jobs) ? result.jobs : [],
        });
      } catch (err) {
        console.error(err);
        setError("Unable to load fresh intelligence.");
      } finally {
        setLoading(false);
      }
    };

    loadFresh();
  }, []);

  if (loading) {
    return (
      <main className="container">
        <div className="research-loading">
          <div className="loading-spinner"></div>
          Loading fresh intelligence...
        </div>
      </main>
    );
  }

  return (
    <main className="container">
      <section className="page-heading">
        <div>
          <div className="breadcrumb">Home / Fresh Intelligence</div>
          <h1>Fresh AI Intelligence</h1>
          <p>
            Recently collected AI news and job intelligence from monitored
            sources.
          </p>
        </div>

        <div className="dataset-status">
          <span className="status-dot"></span>
          Live Dataset
        </div>
      </section>

      {error && <div className="research-error">{error}</div>}

      {/* NEWS */}
      <section className="content-section">
        <div className="section-header">
          <div>
            <div className="section-kicker">FRESH NEWS</div>
            <h2>AI News</h2>
            <p>Recently collected AI ecosystem news.</p>
          </div>
          <div className="dataset-status">{data.news.length} items</div>
        </div>

        {data.news.length === 0 ? (
          <div className="research-empty">No fresh news available.</div>
        ) : (
          <div className="fresh-grid">
            {data.news.map((item, index) => (
              <FreshCard key={index} item={item} type="NEWS" />
            ))}
          </div>
        )}
      </section>

      {/* JOBS */}
      <section className="content-section">
        <div className="section-header">
          <div>
            <div className="section-kicker">JOB INTELLIGENCE</div>
            <h2>AI Jobs</h2>
            <p>Recently monitored AI job sources.</p>
          </div>
          <div className="dataset-status">{data.jobs.length} sources</div>
        </div>

        {data.jobs.length === 0 ? (
          <div className="research-empty">No fresh job data available.</div>
        ) : (
          <div className="fresh-grid">
            {data.jobs.map((item, index) => (
              <FreshCard key={index} item={item} type="JOB" />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

/* ============================================================
   FRESH CARD
============================================================ */

function FreshCard({ item, type }) {
  const title =
    item.title ||
    item.name ||
    item.position ||
    item.jobTitle ||
    "Untitled";

  const description =
    item.description ||
    item.summary ||
    item.snippet ||
    item.company ||
    "No additional information available.";

  const url =
    item.url ||
    item.link ||
    item.sourceUrl ||
    null;

  return (
    <article className="fresh-card">
      <div className="fresh-card-top">
        <span className="entity-type">{type}</span>
        <span className="source-dot"></span>
      </div>

      <h3>{title}</h3>
      <p>{description}</p>

      {url && (
        <a
          href={url}
          target="_blank"
          rel="noreferrer"
          className="paper-link"
        >
          Open Source ↗
        </a>
      )}
    </article>
  );
}

/* ============================================================
   GLOBAL SEARCH RESULTS
============================================================ */

function SearchResults({ data, onClear }) {
  const papers = Array.isArray(data.papers) ? data.papers : [];
  const entities = Array.isArray(data.entities) ? data.entities : [];

  return (
    <section className="content-section">
      <div className="section-header">
        <div>
          <div className="section-kicker">SEARCH</div>
          <h2>Matching Intelligence</h2>
          <p>
            {data.paperCount || 0} papers and {data.entityCount || 0} entities
            matched.
          </p>
        </div>

        <button className="refresh-button" onClick={onClear}>
          Clear Search
        </button>
      </div>

      {/* PAPERS */}
      {papers.length > 0 && (
        <>
          <div className="section-kicker">RESEARCH PAPERS</div>
          <div className="search-result-grid">
            {papers.map((paper, index) => (
              <article className="search-result-card" key={index}>
                <span className="entity-type">RESEARCH</span>
                <h3>{paper.title || "Untitled Paper"}</h3>
                <p>{paper.abstract || "No abstract available."}</p>
                {(paper.sourceUrl ||
                  paper.source_url ||
                  paper.arxiv_url) && (
                  <a
                    href={
                      paper.sourceUrl ||
                      paper.source_url ||
                      paper.arxiv_url
                    }
                    target="_blank"
                    rel="noreferrer"
                  >
                    View Paper ↗
                  </a>
                )}
              </article>
            ))}
          </div>
        </>
      )}

      {/* ENTITIES */}
      {entities.length > 0 && (
        <>
          <div className="section-kicker search-section-gap">AI ENTITIES</div>
          <div className="search-result-grid">
            {entities.map((entity, index) => (
              <EntityCard key={index} item={entity} />
            ))}
          </div>
        </>
      )}

      {papers.length === 0 && entities.length === 0 && (
        <div className="research-empty">
          <div className="empty-icon">⌕</div>
          <h3>No results found</h3>
          <p>Try a different search term.</p>
        </div>
      )}
    </section>
  );
}

/* ============================================================
   HELPERS
============================================================ */

function getPageNumbers(current, total) {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages = [];
  pages.push(1);

  if (current > 4) {
    pages.push("...");
  }

  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  if (current < total - 3) {
    pages.push("...");
  }

  pages.push(total);
  return pages;
}

/* ============================================================
   EXPLORE CARD
============================================================ */

function ExploreCard({ title, description, value, onClick }) {
  return (
    <button className="explore-card" onClick={onClick}>
      <div className="explore-card-top">
        <div className="explore-icon">▣</div>
        <span className="arrow">→</span>
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      <div className="explore-count">
        {Number(value || 0).toLocaleString()} records
      </div>
    </button>
  );
}

/* ============================================================
   PIPELINE ITEM
============================================================ */

function PipelineItem({ title, value }) {
  return (
    <div className="pipeline-item">
      <div className="pipeline-icon">✓</div>
      <div>
        <div className="pipeline-title">{title}</div>
        <div className="pipeline-value">{value}</div>
      </div>
    </div>
  );
}

export default App;