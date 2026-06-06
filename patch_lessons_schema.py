import os
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse

def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url or not db_url.startswith("mysql://"):
        print("Invalid or missing DATABASE_URL in .env")
        return

    parsed = urlparse(db_url)
    db_name = parsed.path.lstrip('/')

    conn = mysql.connector.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        database=db_name
    )
    cursor = conn.cursor()
    print("Connected to MySQL. Patching lessons table schema...")

    # 1. Add version column to lessons if not exists
    try:
        cursor.execute("ALTER TABLE lessons ADD COLUMN version INT DEFAULT 1")
        print("  Added version column to lessons table.")
    except Exception as e:
        print(f"  Note: version column already exists or failed to add: {e}")

    # 2. Drop existing constraint
    try:
        cursor.execute("ALTER TABLE lessons DROP CHECK chk_lesson_status")
        print("  Dropped chk_lesson_status check constraint.")
    except Exception as e:
        pass
    try:
        cursor.execute("ALTER TABLE lessons DROP CONSTRAINT chk_lesson_status")
        print("  Dropped chk_lesson_status constraint (alternative syntax).")
    except Exception as e:
        pass

    # 3. Add new check constraint
    try:
        cursor.execute("ALTER TABLE lessons ADD CONSTRAINT chk_lesson_status CHECK (status IN ('draft', 'review', 'published', 'archived'))")
        print("  Added new chk_lesson_status constraint successfully.")
    except Exception as e:
        print(f"  Warning: Failed to add chk_lesson_status constraint: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Patching complete.")

if __name__ == "__main__":
    main()
