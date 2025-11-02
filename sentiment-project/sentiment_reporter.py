"""
Comprehensive sentiment analysis reporting and visualization module.
Provides detailed reports with categorization, trending, and visualizations.
"""

import sqlite3
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Visualization libraries not available. Install matplotlib, pandas, and seaborn for charts.")

from config import get_config
from logger import get_logger
from trend_analyzer import TrendAnalyzer

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)


class SentimentReporter:
    """
    Comprehensive sentiment analysis reporter with categorization and trends
    """

    def __init__(self, db_path=None):
        """
        Initialize the sentiment reporter

        Args:
            db_path: Database path (defaults to config)
        """
        self.db_path = db_path or config.get_db_path()
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.trend_analyzer = TrendAnalyzer(db_path)

    def generate_comprehensive_report(self, output_file: str = None) -> str:
        """
        Generate a comprehensive sentiment analysis report

        Args:
            output_file: Optional file path to save the report

        Returns:
            Report content as string
        """
        self.logger.info("Generating comprehensive sentiment report")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("COMPREHENSIVE SENTIMENT ANALYSIS REPORT")
            report_lines.append("=" * 80)
            report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")

            # 1. Overall Statistics
            report_lines.extend(self._generate_overall_stats(cursor))

            # 2. Category Analysis
            report_lines.extend(self._generate_category_analysis(cursor))

            # 3. Topic Analysis
            report_lines.extend(self._generate_topic_analysis(cursor))

            # 4. Keyword Analysis
            report_lines.extend(self._generate_keyword_analysis(cursor))

            # 5. Emotion Analysis
            report_lines.extend(self._generate_emotion_analysis(cursor))

            # 6. Trend Analysis
            report_lines.extend(self._generate_trend_analysis())

            # 7. Recent Sentiment Changes
            report_lines.extend(self._generate_recent_changes(cursor))

            # 8. Recommendations
            report_lines.extend(self._generate_recommendations(cursor))

            conn.close()

            report_content = "\\n".join(report_lines)

            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.logger.info(f"Report saved to: {output_file}")

            return report_content

        except Exception as e:
            self.logger.error(f"Error generating report: {e}", exc_info=True)
            return f"Error generating report: {e}"

    def _generate_overall_stats(self, cursor) -> List[str]:
        """Generate overall statistics section"""
        lines = []
        lines.append("1. OVERALL STATISTICS")
        lines.append("-" * 50)

        # Total articles analyzed
        cursor.execute("SELECT COUNT(*) FROM enhanced_sentiment")
        total_articles = cursor.fetchone()[0]
        lines.append(f"Total Articles Analyzed: {total_articles}")

        if total_articles == 0:
            lines.append("No data available for analysis.")
            lines.append("")
            return lines

        # Average sentiment metrics
        cursor.execute("""
            SELECT
                AVG(polarity) as avg_polarity,
                AVG(subjectivity) as avg_subjectivity,
                AVG(confidence) as avg_confidence
            FROM enhanced_sentiment
        """)
        avg_polarity, avg_subjectivity, avg_confidence = cursor.fetchone()

        lines.append(f"Average Polarity: {avg_polarity:.3f} (Range: -1 to 1)")
        lines.append(f"Average Subjectivity: {avg_subjectivity:.3f} (Range: 0 to 1)")
        lines.append(f"Average Confidence: {avg_confidence:.3f} (Range: 0 to 1)")

        # Sentiment distribution
        cursor.execute("""
            SELECT
                SUM(CASE WHEN polarity > 0.1 THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN polarity < -0.1 THEN 1 ELSE 0 END) as negative,
                SUM(CASE WHEN polarity >= -0.1 AND polarity <= 0.1 THEN 1 ELSE 0 END) as neutral
            FROM enhanced_sentiment
        """)
        positive, negative, neutral = cursor.fetchone()

        lines.append("")
        lines.append("Sentiment Distribution:")
        lines.append(f"  Positive: {positive} ({positive/total_articles*100:.1f}%)")
        lines.append(f"  Negative: {negative} ({negative/total_articles*100:.1f}%)")
        lines.append(f"  Neutral:  {neutral} ({neutral/total_articles*100:.1f}%)")

        # Analysis timeframe
        cursor.execute("""
            SELECT MIN(analysis_time), MAX(analysis_time)
            FROM enhanced_sentiment
        """)
        min_time, max_time = cursor.fetchone()
        lines.append("")
        lines.append(f"Analysis Timeframe: {min_time} to {max_time}")
        lines.append("")

        return lines

    def _generate_category_analysis(self, cursor) -> List[str]:
        """Generate category analysis section"""
        lines = []
        lines.append("2. CATEGORY ANALYSIS")
        lines.append("-" * 50)

        cursor.execute("""
            SELECT
                c.name,
                COUNT(*) as article_count,
                AVG(es.polarity) as avg_polarity,
                AVG(es.subjectivity) as avg_subjectivity,
                SUM(CASE WHEN es.polarity > 0.1 THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN es.polarity < -0.1 THEN 1 ELSE 0 END) as negative,
                SUM(CASE WHEN es.polarity >= -0.1 AND es.polarity <= 0.1 THEN 1 ELSE 0 END) as neutral
            FROM enhanced_sentiment es
            JOIN categories c ON es.primary_category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY article_count DESC
        """)

        results = cursor.fetchall()

        if not results:
            lines.append("No category data available.")
            lines.append("")
            return lines

        lines.append(f"{'Category':<20} {'Articles':<8} {'Avg Polarity':<12} {'Pos':<4} {'Neg':<4} {'Neu':<4}")
        lines.append("-" * 60)

        for row in results:
            name, count, polarity, subjectivity, pos, neg, neu = row
            lines.append(f"{name:<20} {count:<8} {polarity:<12.3f} {pos:<4} {neg:<4} {neu:<4}")

        lines.append("")
        return lines

    def _generate_topic_analysis(self, cursor) -> List[str]:
        """Generate topic analysis section"""
        lines = []
        lines.append("3. TOPIC ANALYSIS")
        lines.append("-" * 50)

        cursor.execute("""
            SELECT
                t.name,
                COUNT(*) as article_count,
                AVG(es.polarity) as avg_polarity,
                c.name as category_name
            FROM enhanced_sentiment es
            JOIN topics t ON es.primary_topic_id = t.id
            JOIN categories c ON t.category_id = c.id
            GROUP BY t.id, t.name, c.name
            ORDER BY article_count DESC
            LIMIT 15
        """)

        results = cursor.fetchall()

        if not results:
            lines.append("No topic data available.")
            lines.append("")
            return lines

        lines.append(f"{'Topic':<30} {'Category':<15} {'Articles':<8} {'Avg Polarity':<12}")
        lines.append("-" * 70)

        for row in results:
            topic, count, polarity, category = row
            lines.append(f"{topic:<30} {category:<15} {count:<8} {polarity:<12.3f}")

        lines.append("")
        return lines

    def _generate_keyword_analysis(self, cursor) -> List[str]:
        """Generate keyword analysis section"""
        lines = []
        lines.append("4. KEYWORD ANALYSIS")
        lines.append("-" * 50)

        cursor.execute("""
            SELECT
                k.keyword,
                COUNT(*) as mentions,
                AVG(es.polarity) as avg_polarity
            FROM enhanced_sentiment es
            JOIN article_keywords ak ON es.id = ak.article_id
            JOIN keywords k ON ak.keyword_id = k.id
            GROUP BY k.id, k.keyword
            ORDER BY mentions DESC
            LIMIT 20
        """)

        results = cursor.fetchall()

        if not results:
            lines.append("No keyword data available.")
            lines.append("")
            return lines

        lines.append("Top Keywords by Mentions:")
        lines.append(f"{'Keyword':<25} {'Mentions':<8} {'Avg Polarity':<12}")
        lines.append("-" * 50)

        for row in results:
            keyword, mentions, polarity = row
            lines.append(f"{keyword:<25} {mentions:<8} {polarity:<12.3f}")

        lines.append("")
        return lines

    def _generate_emotion_analysis(self, cursor) -> List[str]:
        """Generate emotion analysis section"""
        lines = []
        lines.append("5. EMOTION ANALYSIS")
        lines.append("-" * 50)

        cursor.execute("""
            SELECT
                emotion,
                COUNT(*) as count,
                AVG(polarity) as avg_polarity
            FROM enhanced_sentiment
            GROUP BY emotion
            ORDER BY count DESC
        """)

        results = cursor.fetchall()

        if not results:
            lines.append("No emotion data available.")
            lines.append("")
            return lines

        total_articles = sum(row[1] for row in results)

        lines.append(f"{'Emotion':<15} {'Count':<8} {'Percentage':<12} {'Avg Polarity':<12}")
        lines.append("-" * 50)

        for row in results:
            emotion, count, avg_polarity = row
            percentage = count / total_articles * 100
            lines.append(f"{emotion:<15} {count:<8} {percentage:<12.1f}% {avg_polarity:<12.3f}")

        lines.append("")
        return lines

    def _generate_trend_analysis(self) -> List[str]:
        """Generate trend analysis section"""
        lines = []
        lines.append("6. TREND ANALYSIS")
        lines.append("-" * 50)

        try:
            # Generate trends if not already done
            self.trend_analyzer.generate_daily_trends(days_back=7)

            # Get trending keywords
            trending_keywords = self.trend_analyzer.get_trending_keywords(period_type='daily', limit=10)

            if trending_keywords:
                lines.append("Trending Keywords (Past Week):")
                lines.append(f"{'Keyword':<20} {'Articles':<8} {'Sentiment':<10}")
                lines.append("-" * 40)

                for kw in trending_keywords:
                    sentiment_label = "Positive" if kw['avg_polarity'] > 0.1 else "Negative" if kw['avg_polarity'] < -0.1 else "Neutral"
                    lines.append(f"{kw['keyword']:<20} {kw['article_count']:<8} {sentiment_label:<10}")
            else:
                lines.append("No trending data available.")

            lines.append("")

            # Get category trends
            tech_trends = self.trend_analyzer.get_category_trends('Technology', period_type='daily', limit=7)
            if tech_trends:
                lines.append("Technology Category - Past Week:")
                avg_polarity = sum(t['avg_polarity'] for t in tech_trends) / len(tech_trends)
                total_articles = sum(t['article_count'] for t in tech_trends)
                lines.append(f"  Average Sentiment: {avg_polarity:.3f}")
                lines.append(f"  Total Articles: {total_articles}")

        except Exception as e:
            lines.append(f"Error generating trend analysis: {e}")

        lines.append("")
        return lines

    def _generate_recent_changes(self, cursor) -> List[str]:
        """Generate recent sentiment changes section"""
        lines = []
        lines.append("7. RECENT SENTIMENT CHANGES")
        lines.append("-" * 50)

        # Get articles from the last 24 hours
        cursor.execute("""
            SELECT
                title,
                polarity,
                emotion,
                c.name as category,
                analysis_time
            FROM enhanced_sentiment es
            JOIN categories c ON es.primary_category_id = c.id
            WHERE analysis_time >= datetime('now', '-1 day')
            ORDER BY analysis_time DESC
            LIMIT 10
        """)

        results = cursor.fetchall()

        if not results:
            lines.append("No recent articles found.")
            lines.append("")
            return lines

        lines.append("Recent Articles (Last 24 Hours):")
        lines.append("")

        for row in results:
            title, polarity, emotion, category, analysis_time = row
            sentiment_label = "Positive" if polarity > 0.1 else "Negative" if polarity < -0.1 else "Neutral"

            lines.append(f"• {title[:60]}...")
            lines.append(f"  Category: {category} | Sentiment: {sentiment_label} ({polarity:.2f}) | Emotion: {emotion}")
            lines.append(f"  Time: {analysis_time}")
            lines.append("")

        return lines

    def _generate_recommendations(self, cursor) -> List[str]:
        """Generate recommendations section"""
        lines = []
        lines.append("8. RECOMMENDATIONS")
        lines.append("-" * 50)

        # Get some statistics for recommendations
        cursor.execute("""
            SELECT
                AVG(polarity) as avg_polarity,
                COUNT(*) as total_articles,
                COUNT(DISTINCT primary_category_id) as unique_categories
            FROM enhanced_sentiment
        """)

        avg_polarity, total_articles, unique_categories = cursor.fetchone()

        if total_articles == 0:
            lines.append("No data available for recommendations.")
            lines.append("")
            return lines

        # Generate recommendations based on data
        if avg_polarity < -0.2:
            lines.append("• Overall sentiment is quite negative. Consider:")
            lines.append("  - Monitoring for crisis situations")
            lines.append("  - Identifying root causes of negative sentiment")
            lines.append("  - Developing positive messaging strategies")
        elif avg_polarity > 0.2:
            lines.append("• Overall sentiment is positive. Consider:")
            lines.append("  - Leveraging positive trends for marketing")
            lines.append("  - Amplifying successful initiatives")
            lines.append("  - Maintaining current strategies")
        else:
            lines.append("• Overall sentiment is neutral. Consider:")
            lines.append("  - Identifying opportunities for improvement")
            lines.append("  - Engaging more actively with your audience")
            lines.append("  - Monitoring for emerging trends")

        lines.append("")

        if unique_categories < 5:
            lines.append("• Limited category diversity detected. Consider:")
            lines.append("  - Expanding content sources")
            lines.append("  - Diversifying topic coverage")
            lines.append("  - Monitoring additional categories")

        lines.append("")
        lines.append("• Data Quality Recommendations:")
        lines.append("  - Ensure regular data collection")
        lines.append("  - Validate sentiment analysis accuracy")
        lines.append("  - Monitor trending topics and keywords")
        lines.append("  - Set up alerts for significant sentiment changes")

        lines.append("")
        return lines

    def create_visualizations(self, output_dir: str = "charts") -> bool:
        """
        Create visualization charts

        Args:
            output_dir: Directory to save charts

        Returns:
            True if successful, False otherwise
        """
        if not VISUALIZATION_AVAILABLE:
            self.logger.warning("Visualization libraries not available")
            return False

        try:
            import os
            os.makedirs(output_dir, exist_ok=True)

            conn = sqlite3.connect(self.db_path)

            # 1. Sentiment distribution by category
            df_categories = pd.read_sql_query("""
                SELECT
                    c.name as category,
                    AVG(es.polarity) as avg_polarity,
                    COUNT(*) as article_count
                FROM enhanced_sentiment es
                JOIN categories c ON es.primary_category_id = c.id
                GROUP BY c.id, c.name
                ORDER BY article_count DESC
            """, conn)

            if not df_categories.empty:
                plt.figure(figsize=(12, 6))
                plt.subplot(1, 2, 1)
                plt.bar(df_categories['category'], df_categories['avg_polarity'])
                plt.title('Average Sentiment by Category')
                plt.xlabel('Category')
                plt.ylabel('Average Polarity')
                plt.xticks(rotation=45)

                plt.subplot(1, 2, 2)
                plt.bar(df_categories['category'], df_categories['article_count'])
                plt.title('Article Count by Category')
                plt.xlabel('Category')
                plt.ylabel('Article Count')
                plt.xticks(rotation=45)

                plt.tight_layout()
                plt.savefig(f"{output_dir}/category_analysis.png", dpi=300, bbox_inches='tight')
                plt.close()

            # 2. Emotion distribution
            df_emotions = pd.read_sql_query("""
                SELECT emotion, COUNT(*) as count
                FROM enhanced_sentiment
                GROUP BY emotion
                ORDER BY count DESC
            """, conn)

            if not df_emotions.empty:
                plt.figure(figsize=(10, 6))
                plt.pie(df_emotions['count'], labels=df_emotions['emotion'], autopct='%1.1f%%')
                plt.title('Distribution of Emotions')
                plt.savefig(f"{output_dir}/emotion_distribution.png", dpi=300, bbox_inches='tight')
                plt.close()

            # 3. Sentiment over time (if we have trend data)
            df_trends = pd.read_sql_query("""
                SELECT
                    period_start,
                    AVG(avg_polarity) as avg_polarity,
                    SUM(article_count) as total_articles
                FROM sentiment_trends
                WHERE period_type = 'daily'
                GROUP BY period_start
                ORDER BY period_start
            """, conn)

            if not df_trends.empty:
                plt.figure(figsize=(12, 6))
                plt.subplot(2, 1, 1)
                plt.plot(pd.to_datetime(df_trends['period_start']), df_trends['avg_polarity'])
                plt.title('Sentiment Trend Over Time')
                plt.ylabel('Average Polarity')
                plt.xticks(rotation=45)

                plt.subplot(2, 1, 2)
                plt.bar(pd.to_datetime(df_trends['period_start']), df_trends['total_articles'])
                plt.title('Article Volume Over Time')
                plt.ylabel('Article Count')
                plt.xticks(rotation=45)

                plt.tight_layout()
                plt.savefig(f"{output_dir}/sentiment_trends.png", dpi=300, bbox_inches='tight')
                plt.close()

            conn.close()

            self.logger.info(f"Charts saved to {output_dir}/")
            return True

        except Exception as e:
            self.logger.error(f"Error creating visualizations: {e}", exc_info=True)
            return False

    def export_data_to_csv(self, output_dir: str = "exports") -> bool:
        """
        Export analysis data to CSV files

        Args:
            output_dir: Directory to save CSV files

        Returns:
            True if successful, False otherwise
        """
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)

            conn = sqlite3.connect(self.db_path)

            # Export enhanced sentiment data
            df_sentiment = pd.read_sql_query("""
                SELECT
                    es.*,
                    c.name as category_name,
                    t.name as topic_name
                FROM enhanced_sentiment es
                LEFT JOIN categories c ON es.primary_category_id = c.id
                LEFT JOIN topics t ON es.primary_topic_id = t.id
            """, conn)

            df_sentiment.to_csv(f"{output_dir}/sentiment_analysis.csv", index=False)

            # Export trend data
            df_trends = pd.read_sql_query("""
                SELECT
                    st.*,
                    c.name as category_name,
                    t.name as topic_name,
                    k.keyword
                FROM sentiment_trends st
                LEFT JOIN categories c ON st.category_id = c.id
                LEFT JOIN topics t ON st.topic_id = t.id
                LEFT JOIN keywords k ON st.keyword_id = k.id
            """, conn)

            df_trends.to_csv(f"{output_dir}/trend_analysis.csv", index=False)

            # Export keyword data
            df_keywords = pd.read_sql_query("""
                SELECT
                    k.keyword,
                    k.frequency,
                    COUNT(ak.article_id) as article_mentions
                FROM keywords k
                LEFT JOIN article_keywords ak ON k.id = ak.keyword_id
                GROUP BY k.id, k.keyword, k.frequency
                ORDER BY article_mentions DESC
            """, conn)

            df_keywords.to_csv(f"{output_dir}/keyword_analysis.csv", index=False)

            conn.close()

            self.logger.info(f"Data exported to {output_dir}/")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting data: {e}", exc_info=True)
            return False


if __name__ == "__main__":
    try:
        reporter = SentimentReporter()

        print("Generating comprehensive sentiment report...")

        # Generate report
        report = reporter.generate_comprehensive_report("sentiment_report.txt")
        print("Report generated and saved to sentiment_report.txt")

        # Create visualizations if possible
        if VISUALIZATION_AVAILABLE:
            if reporter.create_visualizations():
                print("Visualizations created in charts/ directory")
        else:
            print("Install matplotlib, pandas, and seaborn for visualizations")

        # Export data
        if reporter.export_data_to_csv():
            print("Data exported to exports/ directory")

        print("\\nReport preview:")
        print(report[:2000] + "..." if len(report) > 2000 else report)

    except Exception as e:
        print(f"Error: {e}")