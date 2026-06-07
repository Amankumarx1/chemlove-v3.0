"""
ChemLove V4 Migration Script
Adds section-level tracking columns to chapter_progress table
and ensures chapter_section_progress table exists.
Run once with the venv python from the project root.
"""
import os
import mysql.connector
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("mysql://"):
    parsed = urlparse(db_url)
    conn = mysql.connector.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip("/")
    )
else:
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "chemlove")
    )

cursor = conn.cursor()

# 1. Add section columns to chapter_progress
new_cols = [
    ("overview_completed",    "BOOLEAN DEFAULT FALSE"),
    ("keypoints_completed",   "BOOLEAN DEFAULT FALSE"),
    ("formulas_completed",    "BOOLEAN DEFAULT FALSE"),
    ("reactions_completed",   "BOOLEAN DEFAULT FALSE"),
    ("experiments_completed", "BOOLEAN DEFAULT FALSE"),
    ("practice_completed",    "BOOLEAN DEFAULT FALSE"),
    ("quiz_completed",        "BOOLEAN DEFAULT FALSE"),
    ("completion_percentage", "INT DEFAULT 0"),
    ("xp_earned",             "INT DEFAULT 0"),
]
for col_name, col_def in new_cols:
    try:
        cursor.execute(f"ALTER TABLE chapter_progress ADD COLUMN {col_name} {col_def}")
        print(f"[OK] Added column: {col_name}")
    except mysql.connector.Error as e:
        if e.errno == 1060:  # Duplicate column
            print(f"[SKIP] Column already exists: {col_name}")
        else:
            print(f"[WARN] {col_name}: {e}")

# 2. Ensure chapter_section_progress table exists (for intermediate tracking)
cursor.execute("""
CREATE TABLE IF NOT EXISTS chapter_section_progress (
    user_id      INT NOT NULL,
    chapter_id   INT NOT NULL,
    section_name VARCHAR(50) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, chapter_id, section_name),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
)
""")
print("[OK] chapter_section_progress table ready.")

conn.commit()
cursor.close()
conn.close()
print("\nMigration complete!")
