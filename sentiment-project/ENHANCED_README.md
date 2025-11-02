# Enhanced Sentiment Analysis with Categorization and Trending

This enhanced version of the sentiment analyzer now includes sophisticated categorization, keyword extraction, and trend analysis capabilities using LLM-powered analysis.

## 🆕 New Features

### 1. **Intelligent Categorization**
- **Automatic category detection**: Technology, Business, Politics, Health, Sports, Entertainment, Science, Environment, Education, Travel
- **Topic identification**: Specific topics within categories (e.g., AI, Cryptocurrency, Mobile Technology)
- **Confidence scoring**: Measure of categorization accuracy

### 2. **Advanced Keyword Extraction**
- **Primary keywords**: Most important terms from each article
- **Entity detection**: People, organizations, locations
- **Technical terms**: Industry-specific terminology
- **Keyword trending**: Track which keywords are gaining momentum

### 3. **Comprehensive Trend Analysis**
- **Daily and weekly trends**: Sentiment patterns over time
- **Category-based trending**: How sentiment changes within specific categories
- **Keyword momentum**: Track rising and falling keywords
- **Emotion tracking**: Monitor emotional responses over time

### 4. **Enhanced LLM Prompting**
- **Structured analysis**: JSON-formatted responses for consistent data
- **Multi-dimensional scoring**: Polarity, subjectivity, emotion, confidence
- **Contextual understanding**: Better interpretation of nuanced content

### 5. **Rich Reporting and Visualization**
- **Comprehensive reports**: Multi-section analysis with actionable insights
- **Data export**: CSV exports for further analysis
- **Visualizations**: Charts and graphs (requires matplotlib, pandas, seaborn)
- **Trend summaries**: Key insights and recommendations

## 📊 Database Schema

The enhanced system uses a sophisticated database schema with the following new tables:

- **categories**: Predefined content categories
- **topics**: Specific topics within categories
- **keywords**: Extracted keywords with frequency tracking
- **enhanced_sentiment**: Full sentiment analysis with categorization
- **article_keywords**: Many-to-many keyword associations
- **article_categories**: Multiple category assignments per article
- **article_topics**: Topic associations
- **sentiment_trends**: Aggregated trend data over time

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Enhanced Schema
The enhanced schema is automatically applied when you first run the analyzer.

### 3. Run Enhanced Analysis
```bash
# Analyze all articles with categorization and keyword extraction
python enhanced_sentiment_cli.py analyze

# Generate comprehensive report
python enhanced_sentiment_cli.py report --export --visualize

# Show quick summary
python enhanced_sentiment_cli.py summary

# Analyze a single piece of text
python enhanced_sentiment_cli.py single "Breaking: New AI breakthrough announced"

# Generate trend analysis
python enhanced_sentiment_cli.py trends --days 30
```

## 📋 Available Commands

### `analyze`
Runs enhanced sentiment analysis on all unanalyzed articles, including:
- Sentiment scoring (polarity, subjectivity, emotion, confidence)
- Category and topic classification
- Keyword extraction
- Automated trend generation

### `report`
Generates a comprehensive multi-section report:
- Overall statistics
- Category analysis
- Topic breakdown
- Keyword trending
- Emotion distribution
- Recent changes
- Actionable recommendations

Options:
- `--export`: Export data to CSV files
- `--visualize`: Create charts and graphs

### `trends`
Performs trend analysis:
- Daily and weekly sentiment patterns
- Category-specific trends
- Keyword momentum tracking
- Trending summary

Options:
- `--days N`: Analyze past N days (default: 30)
- `--category NAME`: Focus on specific category

### `single TEXT`
Analyzes a single piece of text with full categorization and keyword extraction.

### `summary`
Shows a quick overview of your sentiment analysis data.

## 📈 Understanding the Analysis

### Sentiment Scoring
- **Polarity**: -1.0 (very negative) to +1.0 (very positive)
- **Subjectivity**: 0.0 (objective) to 1.0 (subjective)
- **Confidence**: 0.0 to 1.0 (analysis confidence)

### Categories
The system automatically classifies content into these categories:
- **Technology**: Software, hardware, innovation
- **Business**: Finance, economy, markets
- **Politics**: Government, policy, elections
- **Health**: Medicine, wellness, healthcare
- **Sports**: Athletic events and news
- **Entertainment**: Movies, music, celebrities
- **Science**: Research, discoveries
- **Environment**: Climate, sustainability
- **Education**: Academic, learning
- **Travel**: Tourism, destinations
- **Other**: Miscellaneous content

### Emotions
Detected emotional states:
- **Joy**: Positive, happy content
- **Sadness**: Disappointing, melancholy news
- **Anger**: Frustrating, outrageous events
- **Fear**: Worrying, threatening situations
- **Surprise**: Unexpected developments
- **Disgust**: Repelling, offensive content
- **Neutral**: Factual, balanced reporting

## 📊 Trend Analysis

### Daily Trends
- Tracks sentiment changes day-by-day
- Identifies emerging patterns
- Monitors article volume fluctuations

### Weekly Trends
- Broader pattern recognition
- Smooths out daily volatility
- Better for long-term analysis

### Category Trends
- How sentiment evolves within specific topics
- Comparative analysis across categories
- Identifies category-specific patterns

### Keyword Trends
- Rising and falling keyword momentum
- Sentiment associated with specific terms
- Early indicator of emerging topics

## 📁 File Structure

```
sentiment-project/
├── enhanced_ollama_analyzer.py    # Enhanced LLM-based analyzer
├── trend_analyzer.py              # Trend analysis engine
├── sentiment_reporter.py          # Comprehensive reporting
├── enhanced_sentiment_cli.py      # Command-line interface
├── enhanced_schema.sql            # Database schema
├── config.py                      # Configuration management
├── logger.py                      # Logging utilities
├── requirements.txt               # Dependencies
├── exports/                       # CSV data exports
├── charts/                        # Generated visualizations
└── logs/                          # Application logs
```

## 🔧 Configuration

The system uses the same configuration as the original analyzer:

```env
# API Keys
NEWS_API_KEY=your_news_api_key_here

# Ollama Configuration
OLLAMA_MODEL=mistral
OLLAMA_HOST=http://localhost:11434

# Database
DB_NAME=news.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=sentiment_analysis.log
```

## 📊 Data Export

The system can export data in multiple formats:

### CSV Exports
- `sentiment_analysis.csv`: Complete sentiment data with categories
- `trend_analysis.csv`: Aggregated trend data
- `keyword_analysis.csv`: Keyword frequency and sentiment

### Visualizations
- Category sentiment distribution
- Emotion pie charts
- Sentiment trends over time
- Article volume patterns

## 🎯 Use Cases

### 1. **Brand Monitoring**
- Track sentiment around your brand across categories
- Identify trending topics affecting brand perception
- Monitor competitor sentiment

### 2. **Market Intelligence**
- Analyze sentiment in specific business sectors
- Track emerging trends and topics
- Identify market opportunities and threats

### 3. **Content Strategy**
- Understand which content categories resonate most
- Identify high-engagement keywords
- Optimize content timing based on trends

### 4. **Crisis Management**
- Early detection of negative sentiment spikes
- Category-specific sentiment monitoring
- Rapid response planning based on trend data

### 5. **Research and Analytics**
- Academic research on sentiment patterns
- Media bias analysis across categories
- Longitudinal sentiment studies

## 🔍 Advanced Features

### LLM Prompt Engineering
The enhanced analyzer uses sophisticated prompts that extract:
- Nuanced sentiment scoring
- Detailed categorization reasoning
- Comprehensive keyword extraction
- Contextual understanding

### Confidence Scoring
Every analysis includes confidence metrics:
- Overall analysis confidence
- Category assignment confidence
- Keyword relevance scoring

### Multi-dimensional Analysis
Beyond simple positive/negative:
- Emotional depth (joy, anger, fear, etc.)
- Subjectivity vs objectivity
- Category-specific sentiment patterns
- Temporal sentiment evolution

## 🚨 Troubleshooting

### Common Issues

1. **No models available**
   - Ensure Ollama is running
   - The system will automatically use available models

2. **Visualization errors**
   - Install: `pip install matplotlib pandas seaborn`
   - Charts will be skipped if libraries unavailable

3. **Memory issues with large datasets**
   - Process articles in smaller batches
   - Increase system memory allocation

4. **Slow analysis**
   - LLM analysis takes time for quality results
   - Consider using faster models for bulk processing

## 🤝 Contributing

Enhancements welcome! Focus areas:
- Additional category definitions
- Improved prompt engineering
- Advanced visualization options
- Performance optimizations
- Integration with other data sources

## 📄 License

Same license as the original project.

---

**Enhanced by Claude Code** - Bringing AI-powered intelligence to sentiment analysis.