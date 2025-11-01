"""
Database inspection utility.
Displays all tables, columns, and sample data from the database.
"""

import sqlite3

from config import get_config
from logger import get_logger

# Initialize configuration and logger
config = get_config()
logger = get_logger(__name__)


def check_database():
    """Check and display database contents"""
    db_path = config.get_db_path()
    logger.info(f"Inspecting database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print("\n" + "="*60)
        print(f"DATABASE INSPECTION: {db_path}")
        print("="*60)

        if not tables:
            logger.warning("No tables found in database")
            print("No tables found in the database.")
            conn.close()
            return

        print(f"\nTables in the database: {len(tables)}")

        for table in tables:
            table_name = table[0]
            print(f"\n{'-'*60}")
            print(f"TABLE: {table_name}")
            print(f"{'-'*60}")

            # Show columns for each table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                pk_marker = " (PRIMARY KEY)" if pk else ""
                null_marker = " NOT NULL" if not_null else ""
                print(f"  - {col_name} ({col_type}){pk_marker}{null_marker}")

            # Show row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nRow count: {count}")

            # Show first few rows
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print("\nSample data (first 3 rows):")
                for idx, row in enumerate(rows, 1):
                    print(f"  Row {idx}:")
                    for col_idx, (col_info, value) in enumerate(zip(columns, row)):
                        col_name = col_info[1]
                        # Truncate long values
                        value_str = str(value)
                        if len(value_str) > 60:
                            value_str = value_str[:57] + "..."
                        print(f"    {col_name}: {value_str}")
            else:
                print("  (No data)")

        print("\n" + "="*60)
        logger.info(f"Database inspection complete: {len(tables)} tables found")

        conn.close()

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}", exc_info=True)
        print(f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error: {e}")


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

    check_database()
