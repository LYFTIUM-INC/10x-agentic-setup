-- Intelligent Web Search Cache Database Schema
-- Created for 10X Agentic Development Environment

CREATE TABLE IF NOT EXISTS search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    keywords TEXT NOT NULL,
    domain TEXT,
    results_file TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    relevance_score INTEGER DEFAULT 50,
    usage_count INTEGER DEFAULT 0,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
    query_hash TEXT UNIQUE,
    file_size INTEGER,
    status TEXT DEFAULT 'active',
    search_type TEXT DEFAULT 'websearch',
    api_calls_saved INTEGER DEFAULT 0
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_keywords ON search_cache(keywords);
CREATE INDEX IF NOT EXISTS idx_timestamp ON search_cache(timestamp);
CREATE INDEX IF NOT EXISTS idx_domain ON search_cache(domain);
CREATE INDEX IF NOT EXISTS idx_query_hash ON search_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_relevance ON search_cache(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_status ON search_cache(status);

-- Search metrics tracking
CREATE TABLE IF NOT EXISTS search_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE DEFAULT (date('now')),
    total_searches INTEGER DEFAULT 0,
    cache_hits INTEGER DEFAULT 0,
    cache_hit_rate REAL DEFAULT 0.0,
    time_saved_seconds INTEGER DEFAULT 0,
    api_calls_saved INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Search patterns for intelligence
CREATE TABLE IF NOT EXISTS search_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT,
    query_sequence TEXT,
    frequency INTEGER DEFAULT 1,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    effectiveness_score REAL DEFAULT 0.0
);

-- Initial metrics record
INSERT OR IGNORE INTO search_metrics (date) VALUES (date('now'));

-- Initial domains
INSERT OR IGNORE INTO search_cache (query, keywords, domain, results_file, query_hash, status) 
VALUES 
('CACHE_SYSTEM_INITIALIZED', 'initialization', 'system', 'system_init.md', 'init_hash', 'system');