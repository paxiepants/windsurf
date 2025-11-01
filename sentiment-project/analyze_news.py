"""
Non-interactive script to analyze news articles with Ollama.
Run this to analyze all unanalyzed articles automatically.
"""

import sys
from ollama_chat import OllamaSentimentAnalyzer
from logger import get_logger

logger = get_logger(__name__)

def main():
    """Analyze all news articles and show summary"""
    print("="*60)
    print("OLLAMA NEWS SENTIMENT ANALYSIS")
    print("="*60)

    try:
        # Initialize analyzer
        print("\nInitializing Ollama analyzer...")
        analyzer = OllamaSentimentAnalyzer()

        # Analyze all articles
        print("\nAnalyzing all unanalyzed articles...")
        analyzer.analyze_all_articles()

        # Show summary
        print("\nGenerating summary...")
        analyzer.get_sentiment_summary()

        # Show detailed analysis
        print("\nShowing detailed analysis (last 5 articles)...")
        analyzer.show_detailed_analysis(limit=5)

        print("\n" + "="*60)
        print("Analysis complete!")
        print("="*60)

        logger.info("Automated analysis completed successfully")
        return 0

    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
        logger.info("Analysis cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
