"""
Enhanced Ollama-based sentiment analyzer with categorization and trending.
Uses LLM for sentiment analysis, category detection, keyword extraction, and trend analysis.
"""

import sqlite3
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

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


class EnhancedOllamaSentimentAnalyzer:
    """
    Enhanced sentiment analyzer with categorization, keyword extraction, and trend analysis
    """

    def __init__(self, model=None, db_path=None):
        """
        Initialize the enhanced analyzer

        Args:
            model: Ollama model to use (defaults to config)
            db_path: Database path (defaults to config)
        """
        self.model = model or config.OLLAMA_MODEL
        self.db_path = db_path or config.get_db_path()
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

        self.logger.info(f"Initializing enhanced analyzer with model: {self.model}")
        self._verify_ollama_connection()
        self._initialize_database()

    def _verify_ollama_connection(self):
        """Verify that Ollama is running and the model is available"""
        try:
            models_response = ollama.list()
            if hasattr(models_response, 'models'):
                available_models = [model.model for model in models_response.models]
            else:
                available_models = [model['name'] for model in models_response.get('models', [])]

            if not available_models:
                self.logger.warning("No models found locally")
                self.logger.error("No models available in Ollama")
                raise Exception("No models available")
            elif self.model not in available_models:
                self.logger.warning(f"Model '{self.model}' not found locally")
                available_str = ', '.join(available_models[:5])
                self.logger.info(f"Available models: {available_str}")

                # Use the first available model instead of asking for user input
                if available_models:
                    self.model = available_models[0]
                    self.logger.info(f"Using available model: {self.model}")
                else:
                    self.logger.error("No models available")
                    raise Exception("No models available")
            else:
                self.logger.info(f"Model {self.model} is available")
                self.logger.info(f"Available models: {', '.join(available_models)}")

        except Exception as e:
            self.logger.error(f"Error connecting to Ollama: {e}", exc_info=True)
            raise

    def _initialize_database(self):
        """Initialize the enhanced database schema"""
        try:
            with open('enhanced_schema.sql', 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Execute schema creation
            cursor.executescript(schema_sql)
            conn.commit()
            conn.close()

            self.logger.info("Enhanced database schema initialized")

        except Exception as e:
            self.logger.error(f"Error initializing database: {e}", exc_info=True)
            raise

    def _create_enhanced_prompt(self, title: str, content: str = "") -> str:
        """Create enhanced prompt for categorization and sentiment analysis"""

        prompt = f"""Analyze the following news article and provide a comprehensive analysis in JSON format.

Title: {title}
Content: {content if content else "No additional content provided"}

Please analyze and return a JSON object with the following structure:
{{
    "sentiment": {{
        "polarity": <float between -1 and 1, where -1 is very negative, 0 is neutral, 1 is very positive>,
        "subjectivity": <float between 0 and 1, where 0 is objective, 1 is subjective>,
        "emotion": "<primary emotion: joy, sadness, anger, fear, surprise, disgust, neutral>",
        "confidence": <float between 0 and 1 indicating confidence in analysis>
    }},
    "categorization": {{
        "primary_category": "<most relevant category from: Technology, Business, Politics, Health, Sports, Entertainment, Science, Environment, Education, Travel, Other>",
        "category_confidence": <float between 0 and 1>,
        "all_categories": ["<list of all relevant categories>"],
        "primary_topic": "<specific topic or field within the category>",
        "all_topics": ["<list of all relevant topics>"]
    }},
    "keywords": {{
        "primary_keywords": ["<5-10 most important keywords/phrases>"],
        "entities": ["<people, organizations, locations mentioned>"],
        "technical_terms": ["<industry-specific or technical terms>"]
    }},
    "summary": "<brief 1-2 sentence summary of the article>",
    "reasoning": "<explanation of the sentiment and categorization decisions>"
}}

Be precise with the polarity score:
- Very positive news (great achievements, breakthroughs): 0.7 to 1.0
- Moderately positive (good news, improvements): 0.3 to 0.7
- Slightly positive (minor good news): 0.1 to 0.3
- Neutral (factual reporting, no clear sentiment): -0.1 to 0.1
- Slightly negative (minor concerns, delays): -0.3 to -0.1
- Moderately negative (problems, failures): -0.7 to -0.3
- Very negative (disasters, major failures): -1.0 to -0.7

Focus on extracting relevant keywords that would be useful for trend analysis and categorization."""

        return prompt

    def analyze_article(self, title: str, link: str = "", content: str = "") -> Optional[Dict]:
        """
        Perform enhanced sentiment analysis with categorization

        Args:
            title: Article title
            link: Article URL
            content: Article content (optional)

        Returns:
            Dictionary with analysis results or None if error
        """
        try:
            self.logger.debug(f"Analyzing: {title[:60]}...")

            prompt = self._create_enhanced_prompt(title, content)

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Low temperature for consistent results
                    'top_p': 0.9,
                    'num_predict': 800   # Allow longer responses
                }
            )

            response_text = response['response'].strip()

            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    result = json.loads(json_str)

                    # Validate and normalize the result
                    result = self._validate_analysis_result(result, title, link)

                    self.logger.debug(f"Analysis result: polarity={result.get('sentiment', {}).get('polarity')}, "
                                    f"category={result.get('categorization', {}).get('primary_category')}")
                    return result

                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON parsing error: {e}, Raw response: {response_text}")

            # If JSON parsing fails, create a basic result
            return self._create_fallback_result(title, link, response_text)

        except Exception as e:
            self.logger.error(f"Error analyzing article: {e}", exc_info=True)
            return None

    def _validate_analysis_result(self, result: Dict, title: str, link: str) -> Dict:
        """Validate and normalize analysis result"""

        # Ensure required structure exists
        if 'sentiment' not in result:
            result['sentiment'] = {}
        if 'categorization' not in result:
            result['categorization'] = {}
        if 'keywords' not in result:
            result['keywords'] = {}

        # Validate sentiment values
        sentiment = result['sentiment']
        sentiment['polarity'] = max(-1, min(1, float(sentiment.get('polarity', 0))))
        sentiment['subjectivity'] = max(0, min(1, float(sentiment.get('subjectivity', 0.5))))
        sentiment['confidence'] = max(0, min(1, float(sentiment.get('confidence', 0.5))))

        if sentiment.get('emotion') not in ['joy', 'sadness', 'anger', 'fear', 'surprise', 'disgust', 'neutral']:
            sentiment['emotion'] = 'neutral'

        # Validate categorization
        categorization = result['categorization']
        valid_categories = ['Technology', 'Business', 'Politics', 'Health', 'Sports',
                          'Entertainment', 'Science', 'Environment', 'Education', 'Travel', 'Other']

        if categorization.get('primary_category') not in valid_categories:
            categorization['primary_category'] = 'Other'

        categorization['category_confidence'] = max(0, min(1, float(categorization.get('category_confidence', 0.5))))

        # Ensure all_categories is a list
        if not isinstance(categorization.get('all_categories'), list):
            categorization['all_categories'] = [categorization['primary_category']]

        # Ensure keywords are lists
        keywords = result['keywords']
        for key in ['primary_keywords', 'entities', 'technical_terms']:
            if not isinstance(keywords.get(key), list):
                keywords[key] = []

        # Add metadata
        result['title'] = title
        result['link'] = link
        result['analysis_time'] = datetime.now().isoformat()

        return result

    def _create_fallback_result(self, title: str, link: str, response_text: str) -> Dict:
        """Create a basic result when JSON parsing fails"""

        return {
            'sentiment': {
                'polarity': 0.0,
                'subjectivity': 0.5,
                'emotion': 'neutral',
                'confidence': 0.3
            },
            'categorization': {
                'primary_category': 'Other',
                'category_confidence': 0.3,
                'all_categories': ['Other'],
                'primary_topic': 'Unknown',
                'all_topics': ['Unknown']
            },
            'keywords': {
                'primary_keywords': [],
                'entities': [],
                'technical_terms': []
            },
            'summary': f"Analysis of: {title[:100]}...",
            'reasoning': f"Fallback analysis due to parsing error: {response_text[:200]}...",
            'title': title,
            'link': link,
            'analysis_time': datetime.now().isoformat()
        }

    def store_enhanced_analysis(self, analysis_result: Dict) -> bool:
        """Store the enhanced analysis result in the database"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert or update enhanced_sentiment table
            cursor.execute("""
                INSERT OR REPLACE INTO enhanced_sentiment
                (title, link, polarity, subjectivity, emotion, confidence, reasoning,
                 primary_category_id, category_confidence, extracted_keywords,
                 llm_categories, llm_topics, llm_summary, analysis_time)
                VALUES (?, ?, ?, ?, ?, ?, ?,
                       (SELECT id FROM categories WHERE name = ?),
                       ?, ?, ?, ?, ?, ?)
            """, (
                analysis_result['title'],
                analysis_result['link'],
                analysis_result['sentiment']['polarity'],
                analysis_result['sentiment']['subjectivity'],
                analysis_result['sentiment']['emotion'],
                analysis_result['sentiment']['confidence'],
                analysis_result['reasoning'],
                analysis_result['categorization']['primary_category'],
                analysis_result['categorization']['category_confidence'],
                json.dumps(analysis_result['keywords']),
                json.dumps(analysis_result['categorization']['all_categories']),
                json.dumps(analysis_result['categorization']['all_topics']),
                analysis_result['summary'],
                analysis_result['analysis_time']
            ))

            article_id = cursor.lastrowid

            # Store keywords
            for keyword in analysis_result['keywords']['primary_keywords']:
                if keyword:
                    cursor.execute("""
                        INSERT OR IGNORE INTO keywords (keyword) VALUES (?)
                    """, (keyword,))

                    cursor.execute("""
                        INSERT OR REPLACE INTO article_keywords (article_id, keyword_id)
                        VALUES (?, (SELECT id FROM keywords WHERE keyword = ?))
                    """, (article_id, keyword))

            # Store category mappings
            for category in analysis_result['categorization']['all_categories']:
                cursor.execute("""
                    INSERT OR REPLACE INTO article_categories (article_id, category_id)
                    VALUES (?, (SELECT id FROM categories WHERE name = ?))
                """, (article_id, category))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            self.logger.error(f"Error storing analysis: {e}", exc_info=True)
            return False

    def analyze_all_articles(self) -> Tuple[int, int]:
        """Analyze all unanalyzed articles from the news table"""

        self.logger.info("Starting enhanced analysis of all unanalyzed articles")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get articles that haven't been analyzed yet
            cursor.execute("""
                SELECT DISTINCT n.title, n.link
                FROM news n
                LEFT JOIN enhanced_sentiment es ON n.title = es.title
                WHERE es.title IS NULL
                ORDER BY n.id
            """)

            articles = cursor.fetchall()
            conn.close()

            if not articles:
                self.logger.info("No new articles to analyze")
                return 0, 0

            self.logger.info(f"Analyzing {len(articles)} articles using {self.model}")

            analyzed = 0
            errors = 0

            for title, link in articles:
                try:
                    self.logger.info(f"Analyzing: {title[:60]}...")

                    result = self.analyze_article(title, link)

                    if result:
                        if self.store_enhanced_analysis(result):
                            analyzed += 1
                            self.logger.debug(f"✓ Stored analysis for: {title[:50]}...")
                        else:
                            errors += 1
                            self.logger.error(f"✗ Failed to store: {title[:50]}...")
                    else:
                        errors += 1
                        self.logger.error(f"✗ Failed to analyze: {title[:50]}...")

                except Exception as e:
                    errors += 1
                    self.logger.error(f"Error processing article '{title}': {e}")

            self.logger.info(f"Enhanced analysis complete: {analyzed} analyzed, {errors} errors")
            return analyzed, errors

        except Exception as e:
            self.logger.error(f"Database error: {e}", exc_info=True)
            return 0, 0

if __name__ == "__main__":
    try:
        analyzer = EnhancedOllamaSentimentAnalyzer()
        analyzed, errors = analyzer.analyze_all_articles()
        print(f"Analysis complete: {analyzed} articles analyzed, {errors} errors")

    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"Error: {e}")