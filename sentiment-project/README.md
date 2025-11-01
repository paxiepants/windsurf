# News Sentiment Analysis Project

A comprehensive, production-ready news sentiment analysis system that uses both traditional NLP (TextBlob) and advanced LLM-based analysis (Ollama) to analyze news articles.

## Features

- **Multiple Data Sources**: Fetch news from NewsAPI or scrape from Google News
- **Dual Analysis Methods**:
  - TextBlob for fast, traditional sentiment analysis
  - Ollama LLM for advanced, nuanced sentiment analysis with emotion detection
- **Interactive Chat**: Query and discuss news sentiment using natural language
- **SQLite Database**: Store articles and sentiment analysis results
- **Centralized Configuration**: Environment-based configuration with validation
- **Professional Logging**: File and console logging with rotation and colored output
- **Secure**: No hardcoded credentials, proper error handling
- **Modular Architecture**: Clean, maintainable code structure

## Project Structure

```
sentiment-project/
├── config.py                   # Centralized configuration management
├── logger.py                   # Logging utilities and setup
├── newsapi_scraper.py          # Fetch news from NewsAPI
├── updated_news_scraper.py     # Scrape news from Google News
├── sentiment_analyzer.py       # TextBlob-based sentiment analysis
├── ollama_chat.py              # Ollama LLM-based analysis & chat
├── check_db.py                 # Database inspection utility
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── news.db                     # SQLite database (auto-generated)
└── logs/                       # Log files directory (auto-generated)
    └── sentiment_analysis.log  # Main log file with rotation
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd sentiment-project
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your NewsAPI key:

```env
NEWSAPI_KEY=your_actual_api_key_here
```

Get a free API key from: https://newsapi.org/

### 3. Install Ollama (for Advanced Analysis)

If you want to use the advanced LLM-based sentiment analysis:

1. Download and install Ollama from: https://ollama.com
2. Start Ollama service:
   ```bash
   ollama serve
   ```
3. Pull a model (recommended: llama3.2):
   ```bash
   ollama pull llama3.2
   ```

## Usage

### Method 1: Fetch News from NewsAPI

```bash
python newsapi_scraper.py
```

This will:
- Fetch the latest news articles based on your configuration
- Store them in the SQLite database
- Show summary statistics
- Log all operations to file and console

### Method 2: Scrape News from Google News

```bash
python updated_news_scraper.py
```

This will:
- Scrape headlines from Google News
- Store them in the database
- Log scraping activity

### Analyze Sentiment (TextBlob)

```bash
python sentiment_analyzer.py
```

This provides:
- Fast sentiment analysis using TextBlob
- Polarity scores (-1 to 1)
- Subjectivity scores (0 to 1)
- Summary statistics
- Detailed logging

### Advanced Analysis with Ollama

```bash
python ollama_chat.py
```

This provides an interactive menu with options to:

1. **Analyze all new articles** - Run LLM-based sentiment analysis
2. **Show sentiment summary** - View statistics and distributions
3. **Show detailed analysis** - See individual article breakdowns
4. **Chat about news sentiment** - Ask questions in natural language
5. **Exit**

#### Example Chat Queries

```
> What are the main themes in today's news?
> Which articles are the most negative?
> Summarize the overall sentiment about technology
> What emotions are most common in the news?
```

### Check Database Contents

```bash
python check_db.py
```

View:
- All tables in the database
- Column structures
- Row counts
- Sample data

## Configuration Options

Edit `.env` to customize all aspects of the application:

```env
# NewsAPI Settings
NEWSAPI_KEY=your_key_here
NEWS_QUERY=technology          # Search topic
NEWS_PAGE_SIZE=20              # Articles per request
NEWS_DAYS_BACK=1               # How many days back to search

# Ollama Settings
OLLAMA_MODEL=llama3.2          # Model to use
OLLAMA_HOST=http://localhost:11434
OLLAMA_TEMPERATURE=0.3         # LLM temperature (0.0-2.0)

# Database
DB_NAME=news.db                # Database filename

# Logging Configuration
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=sentiment_analysis.log
LOG_MAX_BYTES=10485760         # 10MB log file size
LOG_BACKUP_COUNT=5             # Keep 5 backup log files

# Sentiment Thresholds
SENTIMENT_POSITIVE_THRESHOLD=0.1
SENTIMENT_NEGATIVE_THRESHOLD=-0.1
```

## Logging

The application includes comprehensive logging:

- **Console Output**: Colored, INFO level and above
- **File Output**: All levels, with automatic rotation
- **Log Rotation**: When log file reaches 10MB, keeps 5 backups
- **Structured Logs**: Timestamp, module name, level, and message

Log levels:
- `DEBUG`: Detailed information for diagnosing problems
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

Change log level in `.env`:
```env
LOG_LEVEL=DEBUG  # For more detailed logging
```

## Database Schema

### `news` Table
- `id`: Auto-increment primary key
- `title`: Article title
- `link`: Article URL (unique)
- `polarity`: Sentiment score (optional)
- `subjectivity`: Subjectivity score (optional)

### `news_sentiment` Table (TextBlob)
- `title`: Article title (primary key)
- `polarity`: Sentiment polarity (-1 to 1)
- `subjectivity`: Subjectivity score (0 to 1)
- `analysis_time`: When analysis was performed

### `ollama_sentiment` Table (LLM-based)
- `title`: Article title (primary key)
- `polarity`: Sentiment polarity (-1 to 1)
- `subjectivity`: Subjectivity score (0 to 1)
- `emotion`: Detected emotion (joy, anger, fear, etc.)
- `confidence`: Analysis confidence (0 to 1)
- `reasoning`: Explanation of the sentiment
- `analysis_time`: When analysis was performed

## Comparison: TextBlob vs Ollama

| Feature | TextBlob | Ollama LLM |
|---------|----------|------------|
| Speed | Fast | Slower |
| Accuracy | Good for simple cases | Excellent for nuanced text |
| Emotion Detection | No | Yes |
| Reasoning | No | Yes (explains decisions) |
| Sarcasm Detection | Poor | Good |
| Context Understanding | Limited | Excellent |
| Offline | Yes | Yes (after model download) |
| Resource Usage | Low | High (requires GPU/CPU) |

## Architecture

### Configuration Management (`config.py`)
- Centralized environment variable loading
- Configuration validation
- Type conversion and default values
- Secure credential handling

### Logging System (`logger.py`)
- Colored console output
- File rotation
- Multiple log levels
- Exception logging with traceback
- Module-specific loggers

### Modular Design
All scripts follow a consistent pattern:
1. Import configuration and logger
2. Define functions with docstrings
3. Comprehensive error handling
4. Logging at appropriate levels
5. Clean separation of concerns

## Security Best Practices

✅ **DO:**
- Use `.env` file for API keys
- Keep `.env` in `.gitignore`
- Use environment variables for sensitive data
- Regularly rotate API keys
- Review log files for sensitive information

❌ **DON'T:**
- Commit API keys to version control
- Share `.env` files
- Hardcode credentials in source code
- Store passwords in plain text

## Troubleshooting

### "NEWSAPI_KEY not found"
- Make sure you created a `.env` file
- Verify the file is in the same directory as the scripts
- Check that the variable name is exactly `NEWSAPI_KEY`
- Check the logs: `tail logs/sentiment_analysis.log`

### "Error connecting to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check that the model is downloaded: `ollama list`
- Verify the model name in `.env` matches an installed model
- Check logs for detailed error messages

### "No articles found"
- Check your internet connection
- Verify your NewsAPI key is valid
- Try a different search query
- Review logs for API response errors

### Database errors
- Delete the `.db` file and let it regenerate
- Check file permissions
- Ensure sufficient disk space
- Check logs for detailed error messages

### Configuration Errors
```bash
python config.py  # Test configuration loading
```

### View Logs
```bash
# View recent logs
tail -n 50 logs/sentiment_analysis.log

# Follow logs in real-time
tail -f logs/sentiment_analysis.log

# Search logs for errors
grep ERROR logs/sentiment_analysis.log

# View all log files (including rotated)
ls -lh logs/
```

## Development

### Running Tests
```bash
# Test configuration
python config.py

# Test logging
python logger.py

# Test database
python check_db.py
```

### Adding New Features
1. Add configuration options to `config.py`
2. Update `.env.example`
3. Use centralized logger
4. Follow existing error handling patterns
5. Update this README

## Performance Tips

- Use TextBlob for batch processing (faster)
- Use Ollama for quality analysis (slower but better)
- Adjust `NEWS_PAGE_SIZE` based on API limits
- Set `LOG_LEVEL=WARNING` in production for better performance
- Use database indexes for large datasets

## Contributing

Feel free to submit issues or pull requests to improve this project.

## License

This project is for educational purposes.

## Credits

- NewsAPI: https://newsapi.org/
- Ollama: https://ollama.com/
- TextBlob: https://textblob.readthedocs.io/
- Beautiful Soup: https://www.crummy.com/software/BeautifulSoup/
