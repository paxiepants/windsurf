"""
Sentiment analyzer module using TextBlob.
Analyzes sentiment of news articles and stores results in the database.
"""

import sqlite3
from textblob import TextBlob

from config import get_config
from logger import get_logger

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)


def analyze_sentiment():
    """Analyze sentiment for all unanalyzed news articles"""
    db_path = config.get_db_path()
    logger.info(f"Starting sentiment analysis using database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create sentiment table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_sentiment (
                title TEXT PRIMARY KEY,
                polarity REAL,
                subjectivity REAL,
                analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Get articles that haven't been analyzed yet
        cursor.execute("""
            SELECT title FROM news
            WHERE title NOT IN (SELECT title FROM news_sentiment)
        """)
        news_items = cursor.fetchall()

        if not news_items:
            logger.info("No new articles to analyze")
            print("No new articles to analyze.")
            conn.close()
            return

        logger.info(f"Analyzing sentiment for {len(news_items)} articles")
        print(f"Analyzing sentiment for {len(news_items)} articles...")

        analyzed = 0
        errors = 0

        # Analyze sentiment for each news item
        for (title,) in news_items:
            try:
                # Get sentiment scores using TextBlob
                analysis = TextBlob(title)
                polarity = analysis.sentiment.polarity  # -1 (negative) to 1 (positive)
                subjectivity = analysis.sentiment.subjectivity  # 0 (objective) to 1 (subjective)

                # Insert the sentiment analysis results
                cursor.execute(
                    """
                    INSERT INTO news_sentiment (title, polarity, subjectivity)
                    VALUES (?, ?, ?)
                    """,
                    (title, polarity, subjectivity)
                )
                analyzed += 1
                logger.debug(f"Analyzed: {title[:60]}... (polarity: {polarity:.3f})")

            except Exception as e:
                logger.error(f"Error analyzing '{title[:60]}...': {e}")
                errors += 1
                continue

        # Commit changes
        conn.commit()
        conn.close()

        logger.info(f"Analysis complete: {analyzed} analyzed, {errors} errors")
        print(f"Sentiment analysis complete! Analyzed {analyzed} articles.")
        if errors > 0:
            print(f"Warning: {errors} articles had errors during analysis")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}", exc_info=True)
        print(f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        print(f"Error: {e}")


def get_sentiment_summary():
    """Get and display summary statistics of sentiment analysis"""
    db_path = config.get_db_path()
    logger.info("Generating sentiment summary")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get sentiment statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                AVG(polarity) as avg_polarity,
                AVG(subjectivity) as avg_subjectivity,
                SUM(CASE WHEN polarity > ? THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN polarity < ? THEN 1 ELSE 0 END) as negative,
                SUM(CASE WHEN polarity BETWEEN ? AND ? THEN 1 ELSE 0 END) as neutral
            FROM news_sentiment
            WHERE polarity IS NOT NULL
        """, (
            config.SENTIMENT_POSITIVE_THRESHOLD,
            config.SENTIMENT_NEGATIVE_THRESHOLD,
            config.SENTIMENT_NEGATIVE_THRESHOLD,
            config.SENTIMENT_POSITIVE_THRESHOLD
        ))

        stats = cursor.fetchone()

        if stats and stats[0] > 0:
            total, avg_polarity, avg_subjectivity, positive, negative, neutral = stats

            # Print summary
            print("\n" + "="*60)
            print("SENTIMENT ANALYSIS SUMMARY (TextBlob)")
            print("="*60)
            print(f"Total articles analyzed:  {total}")
            print(f"Average polarity:         {avg_polarity:.3f} (range: -1 to 1)")
            print(f"Average subjectivity:     {avg_subjectivity:.3f} (range: 0 to 1)")
            print(f"\nSentiment Distribution:")
            print(f"  Positive:  {positive:4d} ({positive/total*100:5.1f}%)")
            print(f"  Negative:  {negative:4d} ({negative/total*100:5.1f}%)")
            print(f"  Neutral:   {neutral:4d} ({neutral/total*100:5.1f}%)")
            print("="*60)

            logger.info(f"Summary: {positive} positive, {negative} negative, {neutral} neutral")

        else:
            logger.warning("No sentiment analysis data found")
            print("No articles with sentiment analysis found.")

        conn.close()

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}", exc_info=True)
        print(f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error generating summary: {e}", exc_info=True)
        print(f"Error: {e}")


def main():
    """Main function to run sentiment analysis"""
    logger.info("="*60)
    logger.info("Starting TextBlob sentiment analyzer")
    logger.info("="*60)

    try:
        # Ensure NLTK data is available
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('taggers/averaged_perceptron_tagger')
            nltk.data.find('sentiment/vader_lexicon')
        except LookupError:
            logger.info("Downloading required NLTK data...")
            print("Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('vader_lexicon', quiet=True)

        # Run analysis
        analyze_sentiment()
        get_sentiment_summary()

        logger.info("Sentiment analysis completed successfully")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\nOperation cancelled")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        from textblob import TextBlob
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
