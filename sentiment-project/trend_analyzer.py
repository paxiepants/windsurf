"""
Trend analysis module for sentiment data.
Analyzes sentiment trends over time by category, topic, and keywords.
"""

import sqlite3
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from config import get_config
from logger import get_logger

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)


class TrendAnalyzer:
    """
    Analyzes sentiment trends across categories, topics, and keywords
    """

    def __init__(self, db_path=None):
        """
        Initialize the trend analyzer

        Args:
            db_path: Database path (defaults to config)
        """
        self.db_path = db_path or config.get_db_path()
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    def generate_daily_trends(self, days_back: int = 30) -> int:
        """
        Generate daily trend data for the past N days

        Args:
            days_back: Number of days to analyze

        Returns:
            Number of trend records created
        """
        self.logger.info(f"Generating daily trends for past {days_back} days")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get the date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)

            records_created = 0

            # Generate trends for each day
            current_date = start_date
            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)

                # Generate category trends for this day
                records_created += self._generate_category_trends_for_period(
                    cursor, current_date, next_date, 'daily'
                )

                # Generate topic trends for this day
                records_created += self._generate_topic_trends_for_period(
                    cursor, current_date, next_date, 'daily'
                )

                # Generate keyword trends for this day
                records_created += self._generate_keyword_trends_for_period(
                    cursor, current_date, next_date, 'daily'
                )

                current_date = next_date

            conn.commit()
            conn.close()

            self.logger.info(f"Generated {records_created} daily trend records")
            return records_created

        except Exception as e:
            self.logger.error(f"Error generating daily trends: {e}", exc_info=True)
            return 0

    def generate_weekly_trends(self, weeks_back: int = 12) -> int:
        """
        Generate weekly trend data for the past N weeks

        Args:
            weeks_back: Number of weeks to analyze

        Returns:
            Number of trend records created
        """
        self.logger.info(f"Generating weekly trends for past {weeks_back} weeks")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get the date range
            end_date = date.today()
            start_date = end_date - timedelta(weeks=weeks_back)

            # Align to Monday (start of week)
            start_date = start_date - timedelta(days=start_date.weekday())

            records_created = 0

            # Generate trends for each week
            current_date = start_date
            while current_date <= end_date:
                next_date = current_date + timedelta(days=7)

                # Generate category trends for this week
                records_created += self._generate_category_trends_for_period(
                    cursor, current_date, next_date, 'weekly'
                )

                # Generate topic trends for this week
                records_created += self._generate_topic_trends_for_period(
                    cursor, current_date, next_date, 'weekly'
                )

                # Generate keyword trends for this week
                records_created += self._generate_keyword_trends_for_period(
                    cursor, current_date, next_date, 'weekly'
                )

                current_date = next_date

            conn.commit()
            conn.close()

            self.logger.info(f"Generated {records_created} weekly trend records")
            return records_created

        except Exception as e:
            self.logger.error(f"Error generating weekly trends: {e}", exc_info=True)
            return 0

    def _generate_category_trends_for_period(self, cursor, start_date: date, end_date: date, period_type: str) -> int:
        """Generate trend data for categories in the given period"""

        query = """
            SELECT
                c.id as category_id,
                c.name as category_name,
                COUNT(*) as article_count,
                AVG(es.polarity) as avg_polarity,
                AVG(es.subjectivity) as avg_subjectivity,
                SUM(CASE WHEN es.polarity > 0.1 THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN es.polarity < -0.1 THEN 1 ELSE 0 END) as negative_count,
                SUM(CASE WHEN es.polarity >= -0.1 AND es.polarity <= 0.1 THEN 1 ELSE 0 END) as neutral_count,
                es.emotion as dominant_emotion
            FROM enhanced_sentiment es
            JOIN categories c ON es.primary_category_id = c.id
            WHERE DATE(es.analysis_time) >= ? AND DATE(es.analysis_time) < ?
            GROUP BY c.id, c.name, es.emotion
            ORDER BY COUNT(*) DESC
        """

        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()

        records_created = 0

        # Group by category and pick the most frequent emotion as dominant
        category_data = defaultdict(lambda: {
            'article_count': 0,
            'avg_polarity': 0,
            'avg_subjectivity': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'emotions': defaultdict(int)
        })

        for row in results:
            (category_id, category_name, article_count, avg_polarity, avg_subjectivity,
             positive_count, negative_count, neutral_count, emotion) = row

            data = category_data[category_id]
            data['category_id'] = category_id
            data['article_count'] += article_count
            data['avg_polarity'] += avg_polarity * article_count
            data['avg_subjectivity'] += avg_subjectivity * article_count
            data['positive_count'] += positive_count
            data['negative_count'] += negative_count
            data['neutral_count'] += neutral_count
            data['emotions'][emotion] += article_count

        # Insert trend records
        for category_id, data in category_data.items():
            if data['article_count'] > 0:
                # Calculate weighted averages
                data['avg_polarity'] /= data['article_count']
                data['avg_subjectivity'] /= data['article_count']

                # Find dominant emotion
                dominant_emotion = max(data['emotions'].items(), key=lambda x: x[1])[0]

                cursor.execute("""
                    INSERT OR REPLACE INTO sentiment_trends
                    (category_id, period_start, period_end, period_type,
                     avg_polarity, avg_subjectivity, article_count,
                     positive_count, negative_count, neutral_count, dominant_emotion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    category_id, start_date, end_date, period_type,
                    data['avg_polarity'], data['avg_subjectivity'], data['article_count'],
                    data['positive_count'], data['negative_count'], data['neutral_count'],
                    dominant_emotion
                ))

                records_created += 1

        return records_created

    def _generate_topic_trends_for_period(self, cursor, start_date: date, end_date: date, period_type: str) -> int:
        """Generate trend data for topics in the given period"""

        query = """
            SELECT
                t.id as topic_id,
                t.name as topic_name,
                COUNT(*) as article_count,
                AVG(es.polarity) as avg_polarity,
                AVG(es.subjectivity) as avg_subjectivity,
                SUM(CASE WHEN es.polarity > 0.1 THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN es.polarity < -0.1 THEN 1 ELSE 0 END) as negative_count,
                SUM(CASE WHEN es.polarity >= -0.1 AND es.polarity <= 0.1 THEN 1 ELSE 0 END) as neutral_count,
                es.emotion as dominant_emotion
            FROM enhanced_sentiment es
            JOIN topics t ON es.primary_topic_id = t.id
            WHERE DATE(es.analysis_time) >= ? AND DATE(es.analysis_time) < ?
            GROUP BY t.id, t.name, es.emotion
            ORDER BY COUNT(*) DESC
        """

        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()

        records_created = 0

        # Similar processing as categories
        topic_data = defaultdict(lambda: {
            'article_count': 0,
            'avg_polarity': 0,
            'avg_subjectivity': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'emotions': defaultdict(int)
        })

        for row in results:
            (topic_id, topic_name, article_count, avg_polarity, avg_subjectivity,
             positive_count, negative_count, neutral_count, emotion) = row

            if topic_id:  # Only process if topic_id is not None
                data = topic_data[topic_id]
                data['topic_id'] = topic_id
                data['article_count'] += article_count
                data['avg_polarity'] += avg_polarity * article_count
                data['avg_subjectivity'] += avg_subjectivity * article_count
                data['positive_count'] += positive_count
                data['negative_count'] += negative_count
                data['neutral_count'] += neutral_count
                data['emotions'][emotion] += article_count

        # Insert trend records
        for topic_id, data in topic_data.items():
            if data['article_count'] > 0:
                data['avg_polarity'] /= data['article_count']
                data['avg_subjectivity'] /= data['article_count']

                dominant_emotion = max(data['emotions'].items(), key=lambda x: x[1])[0]

                cursor.execute("""
                    INSERT OR REPLACE INTO sentiment_trends
                    (topic_id, period_start, period_end, period_type,
                     avg_polarity, avg_subjectivity, article_count,
                     positive_count, negative_count, neutral_count, dominant_emotion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    topic_id, start_date, end_date, period_type,
                    data['avg_polarity'], data['avg_subjectivity'], data['article_count'],
                    data['positive_count'], data['negative_count'], data['neutral_count'],
                    dominant_emotion
                ))

                records_created += 1

        return records_created

    def _generate_keyword_trends_for_period(self, cursor, start_date: date, end_date: date, period_type: str) -> int:
        """Generate trend data for keywords in the given period"""

        query = """
            SELECT
                k.id as keyword_id,
                k.keyword,
                COUNT(*) as article_count,
                AVG(es.polarity) as avg_polarity,
                AVG(es.subjectivity) as avg_subjectivity,
                SUM(CASE WHEN es.polarity > 0.1 THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN es.polarity < -0.1 THEN 1 ELSE 0 END) as negative_count,
                SUM(CASE WHEN es.polarity >= -0.1 AND es.polarity <= 0.1 THEN 1 ELSE 0 END) as neutral_count,
                es.emotion as dominant_emotion
            FROM enhanced_sentiment es
            JOIN article_keywords ak ON es.id = ak.article_id
            JOIN keywords k ON ak.keyword_id = k.id
            WHERE DATE(es.analysis_time) >= ? AND DATE(es.analysis_time) < ?
            GROUP BY k.id, k.keyword, es.emotion
            HAVING COUNT(*) >= 2  -- Only keywords that appear in at least 2 articles
            ORDER BY COUNT(*) DESC
        """

        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()

        records_created = 0

        # Similar processing as categories
        keyword_data = defaultdict(lambda: {
            'article_count': 0,
            'avg_polarity': 0,
            'avg_subjectivity': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'emotions': defaultdict(int)
        })

        for row in results:
            (keyword_id, keyword, article_count, avg_polarity, avg_subjectivity,
             positive_count, negative_count, neutral_count, emotion) = row

            data = keyword_data[keyword_id]
            data['keyword_id'] = keyword_id
            data['article_count'] += article_count
            data['avg_polarity'] += avg_polarity * article_count
            data['avg_subjectivity'] += avg_subjectivity * article_count
            data['positive_count'] += positive_count
            data['negative_count'] += negative_count
            data['neutral_count'] += neutral_count
            data['emotions'][emotion] += article_count

        # Insert trend records
        for keyword_id, data in keyword_data.items():
            if data['article_count'] > 0:
                data['avg_polarity'] /= data['article_count']
                data['avg_subjectivity'] /= data['article_count']

                dominant_emotion = max(data['emotions'].items(), key=lambda x: x[1])[0]

                cursor.execute("""
                    INSERT OR REPLACE INTO sentiment_trends
                    (keyword_id, period_start, period_end, period_type,
                     avg_polarity, avg_subjectivity, article_count,
                     positive_count, negative_count, neutral_count, dominant_emotion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    keyword_id, start_date, end_date, period_type,
                    data['avg_polarity'], data['avg_subjectivity'], data['article_count'],
                    data['positive_count'], data['negative_count'], data['neutral_count'],
                    dominant_emotion
                ))

                records_created += 1

        return records_created

    def get_category_trends(self, category_name: str, period_type: str = 'daily', limit: int = 30) -> List[Dict]:
        """
        Get trend data for a specific category

        Args:
            category_name: Name of the category
            period_type: 'daily' or 'weekly'
            limit: Number of periods to return

        Returns:
            List of trend data dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = """
                SELECT
                    st.period_start,
                    st.period_end,
                    st.avg_polarity,
                    st.avg_subjectivity,
                    st.article_count,
                    st.positive_count,
                    st.negative_count,
                    st.neutral_count,
                    st.dominant_emotion
                FROM sentiment_trends st
                JOIN categories c ON st.category_id = c.id
                WHERE c.name = ? AND st.period_type = ?
                ORDER BY st.period_start DESC
                LIMIT ?
            """

            cursor.execute(query, (category_name, period_type, limit))
            results = cursor.fetchall()

            trends = []
            for row in results:
                trends.append({
                    'period_start': row[0],
                    'period_end': row[1],
                    'avg_polarity': row[2],
                    'avg_subjectivity': row[3],
                    'article_count': row[4],
                    'positive_count': row[5],
                    'negative_count': row[6],
                    'neutral_count': row[7],
                    'dominant_emotion': row[8]
                })

            conn.close()
            return trends

        except Exception as e:
            self.logger.error(f"Error getting category trends: {e}", exc_info=True)
            return []

    def get_trending_keywords(self, period_type: str = 'daily', limit: int = 20) -> List[Dict]:
        """
        Get the most trending keywords

        Args:
            period_type: 'daily' or 'weekly'
            limit: Number of keywords to return

        Returns:
            List of trending keyword data
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = """
                SELECT
                    k.keyword,
                    st.avg_polarity,
                    st.article_count,
                    st.positive_count,
                    st.negative_count,
                    st.neutral_count,
                    st.dominant_emotion,
                    st.period_start
                FROM sentiment_trends st
                JOIN keywords k ON st.keyword_id = k.id
                WHERE st.period_type = ?
                ORDER BY st.article_count DESC, st.period_start DESC
                LIMIT ?
            """

            cursor.execute(query, (period_type, limit))
            results = cursor.fetchall()

            keywords = []
            for row in results:
                keywords.append({
                    'keyword': row[0],
                    'avg_polarity': row[1],
                    'article_count': row[2],
                    'positive_count': row[3],
                    'negative_count': row[4],
                    'neutral_count': row[5],
                    'dominant_emotion': row[6],
                    'period_start': row[7]
                })

            conn.close()
            return keywords

        except Exception as e:
            self.logger.error(f"Error getting trending keywords: {e}", exc_info=True)
            return []

    def generate_trend_summary(self) -> Dict:
        """
        Generate a comprehensive trend summary

        Returns:
            Dictionary with trend summary data
        """
        try:
            self.logger.info("Generating trend summary")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            summary = {}

            # Most active categories this week
            cursor.execute("""
                SELECT c.name, SUM(st.article_count) as total_articles
                FROM sentiment_trends st
                JOIN categories c ON st.category_id = c.id
                WHERE st.period_type = 'weekly'
                AND st.period_start >= DATE('now', '-7 days')
                GROUP BY c.id, c.name
                ORDER BY total_articles DESC
                LIMIT 5
            """)
            summary['most_active_categories'] = [{'category': row[0], 'articles': row[1]} for row in cursor.fetchall()]

            # Sentiment trends by category
            cursor.execute("""
                SELECT c.name, AVG(st.avg_polarity) as avg_polarity, COUNT(*) as periods
                FROM sentiment_trends st
                JOIN categories c ON st.category_id = c.id
                WHERE st.period_type = 'daily'
                AND st.period_start >= DATE('now', '-30 days')
                GROUP BY c.id, c.name
                HAVING periods >= 5
                ORDER BY avg_polarity DESC
            """)
            summary['sentiment_by_category'] = [
                {'category': row[0], 'avg_polarity': row[1], 'periods': row[2]}
                for row in cursor.fetchall()
            ]

            # Most discussed keywords
            cursor.execute("""
                SELECT k.keyword, SUM(st.article_count) as total_mentions
                FROM sentiment_trends st
                JOIN keywords k ON st.keyword_id = k.id
                WHERE st.period_type = 'weekly'
                AND st.period_start >= DATE('now', '-30 days')
                GROUP BY k.id, k.keyword
                ORDER BY total_mentions DESC
                LIMIT 10
            """)
            summary['trending_keywords'] = [{'keyword': row[0], 'mentions': row[1]} for row in cursor.fetchall()]

            conn.close()

            self.logger.info("Trend summary generated successfully")
            return summary

        except Exception as e:
            self.logger.error(f"Error generating trend summary: {e}", exc_info=True)
            return {}


if __name__ == "__main__":
    try:
        analyzer = TrendAnalyzer()

        print("Generating trend analysis...")

        # Generate daily trends
        daily_records = analyzer.generate_daily_trends(days_back=30)
        print(f"Generated {daily_records} daily trend records")

        # Generate weekly trends
        weekly_records = analyzer.generate_weekly_trends(weeks_back=8)
        print(f"Generated {weekly_records} weekly trend records")

        # Generate summary
        summary = analyzer.generate_trend_summary()
        print("\nTrend Summary:")
        print(json.dumps(summary, indent=2))

    except Exception as e:
        print(f"Error: {e}")