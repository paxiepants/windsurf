-- Enhanced database schema for categorized sentiment analysis with trending

-- Categories table - predefined categories for articles
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Topics/Fields table - more specific topics within categories
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category_id INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Keywords table - extracted keywords from articles
CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced sentiment analysis table with categorization
CREATE TABLE IF NOT EXISTS enhanced_sentiment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    link TEXT,
    content TEXT,

    -- Sentiment analysis
    polarity REAL,
    subjectivity REAL,
    emotion TEXT,
    confidence REAL,
    reasoning TEXT,

    -- Categorization
    primary_category_id INTEGER,
    primary_topic_id INTEGER,
    extracted_keywords TEXT, -- JSON array of keywords
    category_confidence REAL,

    -- LLM extracted data
    llm_categories TEXT, -- JSON array of detected categories
    llm_topics TEXT,     -- JSON array of detected topics
    llm_summary TEXT,    -- Brief summary from LLM

    -- Timestamps
    published_date DATE,
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (primary_category_id) REFERENCES categories(id),
    FOREIGN KEY (primary_topic_id) REFERENCES topics(id)
);

-- Article-keyword mapping (many-to-many)
CREATE TABLE IF NOT EXISTS article_keywords (
    article_id INTEGER,
    keyword_id INTEGER,
    relevance_score REAL DEFAULT 1.0,
    PRIMARY KEY (article_id, keyword_id),
    FOREIGN KEY (article_id) REFERENCES enhanced_sentiment(id),
    FOREIGN KEY (keyword_id) REFERENCES keywords(id)
);

-- Article-category mapping (many-to-many for multiple categories)
CREATE TABLE IF NOT EXISTS article_categories (
    article_id INTEGER,
    category_id INTEGER,
    confidence REAL DEFAULT 1.0,
    PRIMARY KEY (article_id, category_id),
    FOREIGN KEY (article_id) REFERENCES enhanced_sentiment(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Article-topic mapping (many-to-many for multiple topics)
CREATE TABLE IF NOT EXISTS article_topics (
    article_id INTEGER,
    topic_id INTEGER,
    confidence REAL DEFAULT 1.0,
    PRIMARY KEY (article_id, topic_id),
    FOREIGN KEY (article_id) REFERENCES enhanced_sentiment(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);

-- Trend analysis table for tracking sentiment over time
CREATE TABLE IF NOT EXISTS sentiment_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    topic_id INTEGER,
    keyword_id INTEGER,

    -- Time period
    period_start DATE,
    period_end DATE,
    period_type TEXT, -- 'daily', 'weekly', 'monthly'

    -- Aggregated metrics
    avg_polarity REAL,
    avg_subjectivity REAL,
    article_count INTEGER,
    positive_count INTEGER,
    negative_count INTEGER,
    neutral_count INTEGER,

    -- Most common emotion in this period
    dominant_emotion TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id),
    FOREIGN KEY (keyword_id) REFERENCES keywords(id)
);

-- Insert default categories
INSERT OR IGNORE INTO categories (name, description) VALUES
    ('Technology', 'Technology, software, hardware, and innovation news'),
    ('Business', 'Business, finance, economy, and market news'),
    ('Politics', 'Political news, government, and policy'),
    ('Health', 'Health, medicine, and wellness news'),
    ('Sports', 'Sports and athletic news'),
    ('Entertainment', 'Entertainment, movies, music, and celebrity news'),
    ('Science', 'Scientific research and discoveries'),
    ('Environment', 'Environmental and climate news'),
    ('Education', 'Education and academic news'),
    ('Travel', 'Travel and tourism news'),
    ('Other', 'Uncategorized or mixed content');

-- Insert some common technology topics
INSERT OR IGNORE INTO topics (name, category_id, description) VALUES
    ('Artificial Intelligence', 1, 'AI, machine learning, and neural networks'),
    ('Cryptocurrency', 1, 'Digital currencies and blockchain technology'),
    ('Mobile Technology', 1, 'Smartphones, tablets, and mobile apps'),
    ('Software Development', 1, 'Programming, software engineering, and development tools'),
    ('Hardware', 1, 'Computer hardware, processors, and components'),
    ('Cybersecurity', 1, 'Security, privacy, and data protection'),
    ('Social Media', 1, 'Social networking platforms and digital communication'),
    ('Gaming', 1, 'Video games and gaming industry'),
    ('Cloud Computing', 1, 'Cloud services and infrastructure'),
    ('Internet of Things', 1, 'Connected devices and smart technology');

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_enhanced_sentiment_category ON enhanced_sentiment(primary_category_id);
CREATE INDEX IF NOT EXISTS idx_enhanced_sentiment_topic ON enhanced_sentiment(primary_topic_id);
CREATE INDEX IF NOT EXISTS idx_enhanced_sentiment_analysis_time ON enhanced_sentiment(analysis_time);
CREATE INDEX IF NOT EXISTS idx_enhanced_sentiment_published_date ON enhanced_sentiment(published_date);
CREATE INDEX IF NOT EXISTS idx_sentiment_trends_period ON sentiment_trends(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_sentiment_trends_category ON sentiment_trends(category_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_trends_topic ON sentiment_trends(topic_id);