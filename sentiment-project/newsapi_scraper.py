"""
NewsAPI scraper module.
Fetches news articles from NewsAPI and stores them in the database.
"""

import sqlite3
import requests
from datetime import datetime, timedelta

from config import get_config
from logger import get_logger

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)


def get_news_from_api(api_key=None, query=None, page_size=None, days_back=None):
    """
    Fetch news from News API

    Args:
        api_key: NewsAPI key (defaults to config)
        query: Search query (defaults to config)
        page_size: Number of articles to fetch (defaults to config)
        days_back: Number of days to look back (defaults to config)

    Returns:
        list: List of article dictionaries
    """
    # Use config values as defaults
    api_key = api_key or config.NEWSAPI_KEY
    query = query or config.NEWS_QUERY
    page_size = page_size or config.NEWS_PAGE_SIZE
    days_back = days_back or config.NEWS_DAYS_BACK

    # Calculate date range
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    logger.info(f"Fetching news: query='{query}', page_size={page_size}, from={from_date}")

    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': query,
        'from': from_date,
        'sortBy': 'publishedAt',
        'apiKey': api_key,
        'pageSize': page_size
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        logger.info(f"Successfully fetched {len(articles)} articles from NewsAPI")
        return articles
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news from API: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return []


def store_articles(articles, db_path=None):
    """
    Store articles in the SQLite database

    Args:
        articles: List of articles to store
        db_path: Database path (defaults to config)

    Returns:
        tuple: (inserted_count, skipped_count)
    """
    if not articles:
        logger.warning("No articles to store")
        return 0, 0

    db_path = db_path or config.get_db_path()
    logger.info(f"Storing articles in database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                link TEXT UNIQUE,
                polarity REAL,
                subjectivity REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_sentiment (
                title TEXT PRIMARY KEY,
                polarity REAL,
                subjectivity REAL,
                analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        inserted = 0
        skipped = 0

        for article in articles:
            try:
                title = article.get('title', '')
                url = article.get('url', '')

                if not title or not url:
                    logger.debug(f"Skipping article with missing title or URL")
                    skipped += 1
                    continue

                cursor.execute(
                    "INSERT OR IGNORE INTO news (title, link) VALUES (?, ?)",
                    (title, url)
                )

                if cursor.rowcount > 0:
                    inserted += 1
                    logger.debug(f"Inserted: {title[:60]}...")
                else:
                    skipped += 1
                    logger.debug(f"Skipped duplicate: {title[:60]}...")

            except sqlite3.IntegrityError:
                skipped += 1
            except Exception as e:
                logger.error(f"Error storing article: {e}")
                skipped += 1

        conn.commit()
        conn.close()

        logger.info(f"Storage complete: {inserted} inserted, {skipped} skipped")
        return inserted, skipped

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}", exc_info=True)
        return 0, 0
    except Exception as e:
        logger.error(f"Unexpected error during storage: {e}", exc_info=True)
        return 0, 0


def main():
    """Main function to fetch and store news articles"""
    logger.info("="*60)
    logger.info("Starting NewsAPI scraper")
    logger.info("="*60)

    try:
        # Validate API key is configured
        api_key = config.require_newsapi_key()
        logger.info("NewsAPI key found")

        # Fetch articles
        logger.info("Fetching news from NewsAPI...")
        articles = get_news_from_api(api_key)

        if not articles:
            logger.warning("No articles found. Check your API key and internet connection.")
            return

        logger.info(f"Found {len(articles)} articles")

        # Store articles
        logger.info("Storing articles in database...")
        inserted, skipped = store_articles(articles)

        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Inserted:  {inserted} new articles")
        print(f"Skipped:   {skipped} duplicate articles")
        print(f"Total:     {inserted + skipped} articles")
        print("="*60)

        logger.info("NewsAPI scraper completed successfully")

    except ValueError as e:
        logger.error(str(e))
        print(f"\nERROR: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"\nERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import requests
        from config import get_config
        from logger import get_logger
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Please run the script again.")
        exit(0)

    exit(main())
