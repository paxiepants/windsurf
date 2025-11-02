"""
Enhanced Sentiment Analysis CLI
Command-line interface for the enhanced sentiment analyzer with categorization and trending.
"""

import sys
import argparse
from datetime import datetime

from enhanced_ollama_analyzer import EnhancedOllamaSentimentAnalyzer
from trend_analyzer import TrendAnalyzer
from sentiment_reporter import SentimentReporter
from config import get_config
from logger import get_logger

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Enhanced Sentiment Analysis with Categorization and Trending",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python enhanced_sentiment_cli.py analyze          # Analyze all unanalyzed articles
  python enhanced_sentiment_cli.py trends           # Generate trend analysis
  python enhanced_sentiment_cli.py report           # Generate comprehensive report
  python enhanced_sentiment_cli.py report --export  # Generate report and export data
  python enhanced_sentiment_cli.py single "Breaking: AI breakthrough announced"
        """
    )

    parser.add_argument(
        'command',
        choices=['analyze', 'trends', 'report', 'single', 'summary'],
        help='Command to execute'
    )

    parser.add_argument(
        'text',
        nargs='?',
        help='Text to analyze (for single command)'
    )

    parser.add_argument(
        '--export',
        action='store_true',
        help='Export data to CSV files (for report command)'
    )

    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Create visualization charts (for report command)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for trend analysis (default: 30)'
    )

    parser.add_argument(
        '--category',
        type=str,
        help='Specific category for analysis'
    )

    args = parser.parse_args()

    try:
        if args.command == 'analyze':
            analyze_articles()

        elif args.command == 'single':
            if not args.text:
                print("Error: Text is required for single analysis")
                return 1
            analyze_single_text(args.text)

        elif args.command == 'trends':
            generate_trends(args.days, args.category)

        elif args.command == 'report':
            generate_report(args.export, args.visualize)

        elif args.command == 'summary':
            show_summary()

        return 0

    except KeyboardInterrupt:
        print("\\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"CLI error: {e}", exc_info=True)
        return 1


def analyze_articles():
    """Analyze all unanalyzed articles"""
    print("Enhanced Sentiment Analysis")
    print("=" * 50)
    print("Initializing analyzer...")

    try:
        analyzer = EnhancedOllamaSentimentAnalyzer()
        print("Starting analysis of unanalyzed articles...")

        analyzed, errors = analyzer.analyze_all_articles()

        print(f"\\nAnalysis Complete!")
        print(f"Articles analyzed: {analyzed}")
        print(f"Errors encountered: {errors}")

        if analyzed > 0:
            print("\\nGenerating trends...")
            trend_analyzer = TrendAnalyzer()
            daily_trends = trend_analyzer.generate_daily_trends(days_back=7)
            print(f"Generated {daily_trends} daily trend records")

            print("\\nUse 'python enhanced_sentiment_cli.py report' for detailed analysis")

    except Exception as e:
        print(f"Error during analysis: {e}")


def analyze_single_text(text: str):
    """Analyze a single piece of text"""
    print("Single Text Analysis")
    print("=" * 50)
    print(f"Analyzing: {text[:60]}...")

    try:
        analyzer = EnhancedOllamaSentimentAnalyzer()
        result = analyzer.analyze_article(text, "")

        if result:
            print("\\nAnalysis Results:")
            print("-" * 30)

            sentiment = result.get('sentiment', {})
            categorization = result.get('categorization', {})
            keywords = result.get('keywords', {})

            print(f"Sentiment: {sentiment.get('polarity', 0):.3f} ({get_sentiment_label(sentiment.get('polarity', 0))})")
            print(f"Emotion: {sentiment.get('emotion', 'unknown')}")
            print(f"Confidence: {sentiment.get('confidence', 0):.3f}")
            print(f"Subjectivity: {sentiment.get('subjectivity', 0):.3f}")

            print(f"\\nCategory: {categorization.get('primary_category', 'Unknown')}")
            print(f"Topic: {categorization.get('primary_topic', 'Unknown')}")

            if keywords.get('primary_keywords'):
                print(f"\\nKeywords: {', '.join(keywords['primary_keywords'][:5])}")

            print(f"\\nSummary: {result.get('summary', 'No summary available')}")
            print(f"\\nReasoning: {result.get('reasoning', 'No reasoning available')}")

        else:
            print("Analysis failed")

    except Exception as e:
        print(f"Error during analysis: {e}")


def generate_trends(days_back: int, category: str = None):
    """Generate trend analysis"""
    print("Trend Analysis")
    print("=" * 50)

    try:
        trend_analyzer = TrendAnalyzer()

        print(f"Generating trends for past {days_back} days...")
        daily_trends = trend_analyzer.generate_daily_trends(days_back)
        weekly_trends = trend_analyzer.generate_weekly_trends(weeks_back=max(1, days_back // 7))

        print(f"Generated {daily_trends} daily trend records")
        print(f"Generated {weekly_trends} weekly trend records")

        # Show trending keywords
        print("\\nTrending Keywords:")
        print("-" * 30)
        trending_keywords = trend_analyzer.get_trending_keywords(limit=10)

        if trending_keywords:
            for kw in trending_keywords[:10]:
                sentiment_label = get_sentiment_label(kw['avg_polarity'])
                print(f"• {kw['keyword']:<20} {kw['article_count']} articles ({sentiment_label})")
        else:
            print("No trending keywords found")

        # Show category trends if specified
        if category:
            print(f"\\n{category} Category Trends:")
            print("-" * 30)
            cat_trends = trend_analyzer.get_category_trends(category, limit=7)

            if cat_trends:
                for trend in cat_trends:
                    sentiment_label = get_sentiment_label(trend['avg_polarity'])
                    print(f"{trend['period_start']}: {trend['article_count']} articles ({sentiment_label})")
            else:
                print(f"No trends found for {category} category")

        # Generate summary
        summary = trend_analyzer.generate_trend_summary()
        if summary:
            print("\\nTrend Summary:")
            print("-" * 30)

            if summary.get('most_active_categories'):
                print("Most Active Categories:")
                for cat in summary['most_active_categories'][:5]:
                    print(f"• {cat['category']}: {cat['articles']} articles")

            if summary.get('trending_keywords'):
                print("\\nTop Keywords:")
                for kw in summary['trending_keywords'][:5]:
                    print(f"• {kw['keyword']}: {kw['mentions']} mentions")

    except Exception as e:
        print(f"Error generating trends: {e}")


def generate_report(export_data: bool = False, create_visualizations: bool = False):
    """Generate comprehensive report"""
    print("Comprehensive Sentiment Report")
    print("=" * 50)

    try:
        reporter = SentimentReporter()

        print("Generating report...")
        report_file = f"sentiment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report = reporter.generate_comprehensive_report(report_file)

        print(f"Report saved to: {report_file}")

        if export_data:
            print("Exporting data to CSV...")
            if reporter.export_data_to_csv():
                print("Data exported to exports/ directory")

        if create_visualizations:
            print("Creating visualizations...")
            if reporter.create_visualizations():
                print("Charts saved to charts/ directory")
            else:
                print("Visualization libraries not available. Install matplotlib, pandas, and seaborn.")

        # Show report preview
        print("\\nReport Preview:")
        print("-" * 30)
        lines = report.split('\\n')
        for line in lines[:50]:  # Show first 50 lines
            print(line)

        if len(lines) > 50:
            print("\\n... (see full report in file)")

    except Exception as e:
        print(f"Error generating report: {e}")


def show_summary():
    """Show quick summary"""
    print("Quick Summary")
    print("=" * 50)

    try:
        import sqlite3
        conn = sqlite3.connect(config.get_db_path())
        cursor = conn.cursor()

        # Basic stats
        cursor.execute("SELECT COUNT(*) FROM enhanced_sentiment")
        total_articles = cursor.fetchone()[0]

        if total_articles == 0:
            print("No analyzed articles found.")
            print("Run 'python enhanced_sentiment_cli.py analyze' first.")
            return

        cursor.execute("SELECT AVG(polarity), AVG(confidence) FROM enhanced_sentiment")
        avg_polarity, avg_confidence = cursor.fetchone()

        cursor.execute("""
            SELECT
                SUM(CASE WHEN polarity > 0.1 THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN polarity < -0.1 THEN 1 ELSE 0 END) as negative,
                SUM(CASE WHEN polarity >= -0.1 AND polarity <= 0.1 THEN 1 ELSE 0 END) as neutral
            FROM enhanced_sentiment
        """)
        positive, negative, neutral = cursor.fetchone()

        print(f"Total Articles Analyzed: {total_articles}")
        print(f"Average Sentiment: {avg_polarity:.3f} ({get_sentiment_label(avg_polarity)})")
        print(f"Average Confidence: {avg_confidence:.3f}")
        print()
        print("Sentiment Distribution:")
        print(f"  Positive: {positive} ({positive/total_articles*100:.1f}%)")
        print(f"  Negative: {negative} ({negative/total_articles*100:.1f}%)")
        print(f"  Neutral:  {neutral} ({neutral/total_articles*100:.1f}%)")

        # Top categories
        cursor.execute("""
            SELECT c.name, COUNT(*) as count
            FROM enhanced_sentiment es
            JOIN categories c ON es.primary_category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY count DESC
            LIMIT 5
        """)

        print("\\nTop Categories:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} articles")

        # Recent analysis
        cursor.execute("""
            SELECT MAX(analysis_time), MIN(analysis_time)
            FROM enhanced_sentiment
        """)
        max_time, min_time = cursor.fetchone()
        print(f"\\nAnalysis Period: {min_time} to {max_time}")

        conn.close()

    except Exception as e:
        print(f"Error showing summary: {e}")


def get_sentiment_label(polarity: float) -> str:
    """Convert polarity to human-readable label"""
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"


if __name__ == "__main__":
    sys.exit(main())