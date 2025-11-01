"""
Ollama-based sentiment analyzer module.
Uses LLM for advanced, nuanced sentiment analysis with emotion detection.
"""

import sqlite3
import sys
import json

try:
    import ollama
except ImportError:
    print("Installing ollama package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    import ollama

from config import get_config
from logger import get_logger

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)


class OllamaSentimentAnalyzer:
    """
    Advanced sentiment analyzer using Ollama LLM for nuanced analysis
    """

    def __init__(self, model=None, db_path=None):
        """
        Initialize the Ollama sentiment analyzer

        Args:
            model: Ollama model to use (defaults to config)
            db_path: Database path (defaults to config)
        """
        self.model = model or config.OLLAMA_MODEL
        self.db_path = db_path or config.get_db_path()
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

        self.logger.info(f"Initializing Ollama analyzer with model: {self.model}")
        self._verify_ollama_connection()

    def _verify_ollama_connection(self):
        """Verify that Ollama is running and the model is available"""
        try:
            # List available models - handle both old and new API
            models_response = ollama.list()

            # Extract model names - API returns Model objects, not dicts
            available_models = []
            if hasattr(models_response, 'models'):
                for model in models_response.models:
                    # Handle Model object attributes
                    if hasattr(model, 'model'):
                        available_models.append(model.model)
                    elif hasattr(model, 'name'):
                        available_models.append(model.name)

            if not available_models:
                self.logger.warning("No models found locally")
                print(f"Warning: No Ollama models found locally.")
                print(f"\nTo pull {self.model}, run: ollama pull {self.model}")
                response = input(f"\nWould you like to try pulling {self.model}? (y/n): ")
                if response.lower() == 'y':
                    self.logger.info(f"Pulling model {self.model}")
                    print(f"Pulling {self.model}... This may take a while.")
                    ollama.pull(self.model)
                    self.logger.info("Model pulled successfully")
                else:
                    self.logger.error("User declined to pull model")
                    print("Exiting. Please pull the model manually.")
                    sys.exit(1)
            elif not any(self.model in m for m in available_models):
                self.logger.warning(f"Model '{self.model}' not found locally")
                print(f"Warning: Model '{self.model}' not found locally.")
                print(f"Available models: {', '.join(available_models)}")
                print(f"\nTo pull the model, run: ollama pull {self.model}")
                response = input(f"\nWould you like to try pulling {self.model}? (y/n): ")
                if response.lower() == 'y':
                    self.logger.info(f"Pulling model {self.model}")
                    print(f"Pulling {self.model}... This may take a while.")
                    ollama.pull(self.model)
                    self.logger.info("Model pulled successfully")
                else:
                    self.logger.error("User declined to pull model")
                    print("Exiting. Please pull the model manually or choose an available model.")
                    sys.exit(1)
            else:
                self.logger.info(f"Model {self.model} is available")
                self.logger.info(f"Available models: {', '.join(available_models)}")

        except Exception as e:
            self.logger.error(f"Error connecting to Ollama: {e}", exc_info=True)
            print(f"Error connecting to Ollama: {e}")
            print("\nMake sure Ollama is running. You can start it with: ollama serve")
            sys.exit(1)

    def analyze_article_sentiment(self, title, description=""):
        """
        Analyze sentiment of a news article using Ollama

        Args:
            title: Article title
            description: Article description (optional)

        Returns:
            dict: Sentiment analysis results with polarity, subjectivity, emotion, and reasoning
        """
        text = f"{title}. {description}" if description else title

        prompt = f"""Analyze the sentiment of the following news headline/article.

Article: "{text}"

Provide a JSON response with the following fields:
1. polarity: A score from -1.0 (very negative) to 1.0 (very positive)
2. subjectivity: A score from 0.0 (very objective) to 1.0 (very subjective)
3. emotion: The primary emotion (e.g., joy, anger, fear, sadness, surprise, neutral)
4. confidence: How confident you are in this analysis (0.0 to 1.0)
5. reasoning: Brief explanation of your analysis (1-2 sentences)

Return ONLY valid JSON, no additional text."""

        try:
            self.logger.debug(f"Analyzing: {title[:60]}...")
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': config.OLLAMA_TEMPERATURE,
                }
            )

            # Parse the response
            response_text = response['response'].strip()

            # Try to extract JSON from the response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()

            result = json.loads(response_text)

            # Validate the response has required fields
            required_fields = ['polarity', 'subjectivity', 'emotion', 'confidence', 'reasoning']
            for field in required_fields:
                if field not in result:
                    result[field] = None

            self.logger.debug(f"Analysis result: polarity={result.get('polarity')}, emotion={result.get('emotion')}")
            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}, Raw response: {response_text}")
            return {
                'polarity': 0.0,
                'subjectivity': 0.5,
                'emotion': 'unknown',
                'confidence': 0.0,
                'reasoning': f'Error parsing response: {str(e)}'
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
            return {
                'polarity': 0.0,
                'subjectivity': 0.5,
                'emotion': 'unknown',
                'confidence': 0.0,
                'reasoning': f'Error: {str(e)}'
            }

    def analyze_all_articles(self):
        """Analyze sentiment for all articles in the database"""
        self.logger.info("Starting analysis of all unanalyzed articles")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create enhanced sentiment table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ollama_sentiment (
                    title TEXT PRIMARY KEY,
                    polarity REAL,
                    subjectivity REAL,
                    emotion TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

            # Get articles that haven't been analyzed yet
            cursor.execute("""
                SELECT title FROM news
                WHERE title NOT IN (SELECT title FROM ollama_sentiment)
            """)
            articles = cursor.fetchall()

            if not articles:
                self.logger.info("No new articles to analyze")
                print("No new articles to analyze.")
                conn.close()
                return

            self.logger.info(f"Analyzing {len(articles)} articles using {self.model}")
            print(f"\nAnalyzing {len(articles)} articles using {self.model}...")
            print("This may take a while...\n")

            analyzed = 0
            errors = 0

            for idx, (title,) in enumerate(articles, 1):
                print(f"[{idx}/{len(articles)}] Analyzing: {title[:60]}...")

                result = self.analyze_article_sentiment(title)

                try:
                    cursor.execute("""
                        INSERT INTO ollama_sentiment
                        (title, polarity, subjectivity, emotion, confidence, reasoning)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        title,
                        result.get('polarity'),
                        result.get('subjectivity'),
                        result.get('emotion'),
                        result.get('confidence'),
                        result.get('reasoning')
                    ))
                    conn.commit()
                    analyzed += 1
                except Exception as e:
                    self.logger.error(f"Error storing analysis: {e}")
                    errors += 1

            conn.close()

            self.logger.info(f"Analysis complete: {analyzed} analyzed, {errors} errors")
            print(f"\nAnalysis complete! Analyzed {analyzed} articles.")
            if errors > 0:
                print(f"Warning: {errors} articles had errors during storage")

        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}", exc_info=True)
            print(f"Database error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            print(f"Error: {e}")

    def get_sentiment_summary(self):
        """Get summary statistics of sentiment analysis"""
        self.logger.info("Generating sentiment summary")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    AVG(polarity) as avg_polarity,
                    AVG(subjectivity) as avg_subjectivity,
                    AVG(confidence) as avg_confidence,
                    SUM(CASE WHEN polarity > ? THEN 1 ELSE 0 END) as positive,
                    SUM(CASE WHEN polarity < ? THEN 1 ELSE 0 END) as negative,
                    SUM(CASE WHEN polarity BETWEEN ? AND ? THEN 1 ELSE 0 END) as neutral
                FROM ollama_sentiment
            """, (
                config.SENTIMENT_POSITIVE_THRESHOLD,
                config.SENTIMENT_NEGATIVE_THRESHOLD,
                config.SENTIMENT_NEGATIVE_THRESHOLD,
                config.SENTIMENT_POSITIVE_THRESHOLD
            ))

            stats = cursor.fetchone()

            if stats and stats[0] > 0:
                total, avg_pol, avg_subj, avg_conf, positive, negative, neutral = stats
                print("\n" + "="*60)
                print("SENTIMENT ANALYSIS SUMMARY (Ollama)")
                print("="*60)
                print(f"Total articles analyzed: {total}")
                print(f"Average polarity:        {avg_pol:.3f} (range: -1 to 1)")
                print(f"Average subjectivity:    {avg_subj:.3f} (range: 0 to 1)")
                print(f"Average confidence:      {avg_conf:.3f}")
                print(f"\nSentiment Distribution:")
                print(f"  Positive: {positive:3d} ({positive/total*100:5.1f}%)")
                print(f"  Negative: {negative:3d} ({negative/total*100:5.1f}%)")
                print(f"  Neutral:  {neutral:3d} ({neutral/total*100:5.1f}%)")

                # Get emotion distribution
                cursor.execute("""
                    SELECT emotion, COUNT(*) as count
                    FROM ollama_sentiment
                    GROUP BY emotion
                    ORDER BY count DESC
                    LIMIT 5
                """)
                emotions = cursor.fetchall()

                if emotions:
                    print(f"\nTop Emotions:")
                    for emotion, count in emotions:
                        print(f"  {emotion}: {count} ({count/total*100:.1f}%)")

                print("="*60)

                self.logger.info(f"Summary: {positive} positive, {negative} negative, {neutral} neutral")
            else:
                self.logger.warning("No sentiment analysis data found")
                print("No sentiment analysis data found.")

            conn.close()

        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}", exc_info=True)
            print(f"Database error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error generating summary: {e}", exc_info=True)
            print(f"Error: {e}")

    def chat_about_news(self, query):
        """
        Chat with Ollama about the news sentiment data

        Args:
            query: User's question about the news

        Returns:
            str: Ollama's response
        """
        self.logger.info(f"Processing chat query: {query[:100]}...")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get recent sentiment data
            cursor.execute("""
                SELECT
                    n.title,
                    os.polarity,
                    os.emotion,
                    os.reasoning
                FROM news n
                JOIN ollama_sentiment os ON n.title = os.title
                ORDER BY os.analysis_time DESC
                LIMIT 20
            """)

            recent_articles = cursor.fetchall()
            conn.close()

            # Build context from recent articles
            context = "Recent news articles and their sentiment:\n\n"
            for idx, (title, polarity, emotion, reasoning) in enumerate(recent_articles, 1):
                sentiment = "positive" if polarity > config.SENTIMENT_POSITIVE_THRESHOLD else "negative" if polarity < config.SENTIMENT_NEGATIVE_THRESHOLD else "neutral"
                context += f"{idx}. {title}\n"
                context += f"   Sentiment: {sentiment} (polarity: {polarity:.2f}), Emotion: {emotion}\n"
                context += f"   Analysis: {reasoning}\n\n"

            prompt = f"""{context}

User question: {query}

Based on the sentiment analysis of the news articles above, please provide a helpful and informative response to the user's question."""

            self.logger.debug("Generating chat response")
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                }
            )

            self.logger.info("Chat response generated successfully")
            return response['response']

        except Exception as e:
            self.logger.error(f"Error generating chat response: {e}", exc_info=True)
            return f"Error generating response: {e}"

    def show_detailed_analysis(self, limit=10):
        """Show detailed analysis of recent articles"""
        self.logger.info(f"Showing detailed analysis for {limit} articles")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    title,
                    polarity,
                    subjectivity,
                    emotion,
                    confidence,
                    reasoning
                FROM ollama_sentiment
                ORDER BY analysis_time DESC
                LIMIT ?
            """, (limit,))

            articles = cursor.fetchall()
            conn.close()

            if not articles:
                print("No analyzed articles found.")
                return

            print(f"\n{'='*80}")
            print(f"DETAILED SENTIMENT ANALYSIS (Most Recent {limit} Articles)")
            print(f"{'='*80}\n")

            for idx, (title, pol, subj, emotion, conf, reasoning) in enumerate(articles, 1):
                sentiment = "POSITIVE" if pol > config.SENTIMENT_POSITIVE_THRESHOLD else "NEGATIVE" if pol < config.SENTIMENT_NEGATIVE_THRESHOLD else "NEUTRAL"

                print(f"{idx}. {title}")
                print(f"   Sentiment: {sentiment} | Polarity: {pol:.3f} | Subjectivity: {subj:.3f}")
                print(f"   Emotion: {emotion.upper()} | Confidence: {conf:.3f}")
                print(f"   Analysis: {reasoning}")
                print(f"{'-'*80}\n")

        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}", exc_info=True)
            print(f"Database error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error showing analysis: {e}", exc_info=True)
            print(f"Error: {e}")


def interactive_menu():
    """Interactive menu for the Ollama sentiment analyzer"""
    # Force stdout/stderr to be unbuffered for better Windows compatibility
    import sys
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)

    print("\n" + "="*60)
    print("OLLAMA NEWS SENTIMENT ANALYZER")
    print("="*60)
    print("Interactive Mode - Type your choice and press Enter")
    print("="*60)

    logger.info("Starting interactive menu")

    # Initialize analyzer
    try:
        analyzer = OllamaSentimentAnalyzer()
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {e}", exc_info=True)
        print(f"Error: {e}")
        input("\nPress Enter to exit...")
        return 1

    while True:
        print("\n" + "-"*60)
        print("OPTIONS:")
        print("-"*60)
        print("1. Analyze all new articles")
        print("2. Show sentiment summary")
        print("3. Show detailed analysis")
        print("4. Chat about news sentiment")
        print("5. Exit")
        print("-"*60)

        try:
            choice = input("\nEnter your choice (1-5): ").strip()
        except EOFError:
            print("\n\nError: Cannot read input. Please run this script directly in:")
            print("  - Command Prompt (cmd)")
            print("  - PowerShell")
            print("  - Windows Terminal")
            print("\nDo NOT run through automated systems or IDEs without proper terminal.")
            input("\nPress Enter to exit...")
            return 1

        if choice == "1":
            logger.info("User selected: Analyze all new articles")
            print("\n" + "="*60)
            print("ANALYZING ARTICLES...")
            print("="*60)
            sys.stdout.flush()
            analyzer.analyze_all_articles()
            sys.stdout.flush()
            print("\nPress Enter to continue...")
            input()
        elif choice == "2":
            logger.info("User selected: Show sentiment summary")
            print("\n" + "="*60)
            print("GENERATING SUMMARY...")
            print("="*60)
            sys.stdout.flush()
            analyzer.get_sentiment_summary()
            sys.stdout.flush()
            print("\nPress Enter to continue...")
            input()
        elif choice == "3":
            logger.info("User selected: Show detailed analysis")
            print("\n" + "="*60)
            print("DETAILED ANALYSIS")
            print("="*60)
            sys.stdout.flush()
            limit = input("How many articles to show? (default: 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            analyzer.show_detailed_analysis(limit)
            sys.stdout.flush()
            print("\nPress Enter to continue...")
            input()
        elif choice == "4":
            logger.info("User selected: Chat about news sentiment")
            print("\n" + "="*60)
            print("CHAT MODE")
            print("="*60)
            sys.stdout.flush()
            print("\nEnter your question (or 'back' to return to menu):")
            query = input("> ").strip()
            if query.lower() != 'back':
                print("\nThinking...")
                sys.stdout.flush()
                response = analyzer.chat_about_news(query)
                print(f"\nResponse:\n{response}\n")
                sys.stdout.flush()
                print("\nPress Enter to continue...")
                input()
        elif choice == "5":
            logger.info("User exited")
            print("\n" + "="*60)
            print("Goodbye!")
            print("="*60)
            sys.stdout.flush()
            break
        else:
            print("\n*** Invalid choice. Please enter a number from 1 to 5. ***")
            sys.stdout.flush()

    return 0


if __name__ == "__main__":
    try:
        from config import get_config
        from logger import get_logger
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Please run the script again.")
        exit(0)

    exit(interactive_menu())
