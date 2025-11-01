"""
Google News scraper module.
Scrapes news headlines from Google News and stores them in the database.
"""

import requests
from bs4 import BeautifulSoup
import sqlite3

from config import get_config
from logger import get_logger

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)


def scrape_google_news():
    """Scrape news headlines from Google News"""
    url = "https://news.google.com/home?hl=en-US&gl=US&ceid=US:en"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    logger.info(f"Scraping Google News from: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully fetched page ({len(response.text)} bytes)")
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news: {e}")
        return None


def parse_news(html_content):
    """Parse news articles from HTML content"""
    logger.info("Parsing HTML content")

    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []

    # Look for article elements
    for article in soup.select('article'):
        try:
            title_elem = article.find('h3')
            link_elem = article.find('a')

            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href', '')

                # Clean up the link
                if link.startswith('./'):
                    link = f"https://news.google.com{link[1:]}"

                if title and link:
                    articles.append({
                        'title': title,
                        'link': link
                    })
                    logger.debug(f"Parsed article: {title[:60]}...")

        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            continue

    logger.info(f"Parsed {len(articles)} articles from HTML")
    return articles


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
    logger.info(f"Storing {len(articles)} articles in database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                link TEXT UNIQUE,
                polarity REAL,
                subjectivity REAL
            )
        """)

        inserted = 0
        skipped = 0

        for article in articles:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO news (title, link) VALUES (?, ?)",
                    (article['title'], article['link'])
                )
                if cursor.rowcount > 0:
                    inserted += 1
                    logger.debug(f"Inserted: {article['title'][:60]}...")
                else:
                    skipped += 1
                    logger.debug(f"Skipped duplicate: {article['title'][:60]}...")
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
    """Main function to scrape and store Google News"""
    logger.info("="*60)
    logger.info("Starting Google News scraper")
    logger.info("="*60)

    try:
        print("Fetching news from Google...")
        html_content = scrape_google_news()

        if not html_content:
            logger.error("Failed to fetch news content")
            print("Failed to fetch news content.")
            return 1

        print("Parsing news articles...")
        articles = parse_news(html_content)

        if not articles:
            logger.warning("No articles found on the page")
            print("No articles found on the page. The website structure might have changed.")
            return 1

        print(f"Found {len(articles)} articles. Storing in database...")
        inserted, skipped = store_articles(articles)

        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Inserted:  {inserted} new articles")
        print(f"Skipped:   {skipped} duplicate articles")
        print(f"Total:     {inserted + skipped} articles")
        print("="*60)

        logger.info("Google News scraper completed successfully")
        return 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    try:
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
