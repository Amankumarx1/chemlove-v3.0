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
    print("Connected to MySQL database. Patching chapters table...")

    # 1. Add course_id column
    try:
        cursor.execute("ALTER TABLE chapters ADD COLUMN course_id INT NULL")
        print("  Added course_id column to chapters table.")
    except Exception as e:
        print(f"  Note: course_id column already exists or failed to add: {e}")

    # 2. Add foreign key constraint for course_id
    try:
        cursor.execute("ALTER TABLE chapters ADD CONSTRAINT fk_chapters_course FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL")
        print("  Added fk_chapters_course foreign key constraint.")
    except Exception as e:
        print(f"  Note: fk_chapters_course already exists or failed to add: {e}")

    # 3. Add reactions column
    try:
        cursor.execute("ALTER TABLE chapters ADD COLUMN reactions LONGTEXT NULL")
        print("  Added reactions column to chapters table.")
    except Exception as e:
        print(f"  Note: reactions column already exists or failed to add: {e}")

    # 4. Add experiment_content column
    try:
        cursor.execute("ALTER TABLE chapters ADD COLUMN experiment_content LONGTEXT NULL")
        print("  Added experiment_content column to chapters table.")
    except Exception as e:
        print(f"  Note: experiment_content column already exists or failed to add: {e}")

    # 5. Add updated_at column
    try:
        cursor.execute("ALTER TABLE chapters ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        print("  Added updated_at column to chapters table.")
    except Exception as e:
        print(f"  Note: updated_at column already exists or failed to add: {e}")

    # 6. Convert key_points, notes, formulas from JSON to LONGTEXT
    columns_to_convert = ['key_points', 'notes', 'formulas']
    for col in columns_to_convert:
        try:
            cursor.execute(f"ALTER TABLE chapters MODIFY COLUMN {col} LONGTEXT NULL")
            print(f"  Converted {col} column to LONGTEXT.")
        except Exception as e:
            print(f"  Warning: Failed to convert {col} column to LONGTEXT: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Patching complete.")

if __name__ == "__main__":
    main()
