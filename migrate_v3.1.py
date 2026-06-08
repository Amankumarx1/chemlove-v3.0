import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def parse_mysql_url(url):
    if not url.startswith("mysql://"):
        raise ValueError("Invalid MySQL URL format.")
    rem = url[8:]
    auth, host_port_db = rem.split("@", 1)
    user, password = auth.split(":", 1)
    if "/" in host_port_db:
        host_port, database = host_port_db.split("/", 1)
    else:
        host_port = host_port_db
        database = ""
    if "?" in database:
        database = database.split("?", 1)[0]
    if ":" in host_port:
        host, port = host_port.split(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 3306
    import urllib.parse
    return {
        "host": host,
        "port": port,
        "user": urllib.parse.unquote(user),
        "password": urllib.parse.unquote(password),
        "database": database
    }

config = parse_mysql_url(DATABASE_URL)

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("Successfully connected to MySQL database.")

    # 1. Update check constraint on users role
    # First, let's find existing check constraints on the users table.
    cursor.execute("""
        SELECT CONSTRAINT_NAME 
        FROM information_schema.TABLE_CONSTRAINTS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND CONSTRAINT_TYPE = 'CHECK'
    """, (config["database"],))
    check_constraints = cursor.fetchall()
    
    for (c_name,) in check_constraints:
        try:
            cursor.execute(f"ALTER TABLE users DROP CHECK {c_name}")
            print(f"Dropped check constraint {c_name}")
        except Exception as e:
            print(f"Skipping dropping {c_name}: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD CONSTRAINT chk_role CHECK (role IN ('student', 'teacher', 'admin', 'content_manager'))")
        print("Added updated chk_role check constraint.")
    except Exception as e:
        print(f"Error adding updated check constraint: {e}")

    # 2. Subjects Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE
        )
    """)
    print("Subjects table verified.")
    
    subjects_seed = ['Chemistry', 'Physics', 'Biology', 'Mathematics']
    for sub in subjects_seed:
        cursor.execute("INSERT IGNORE INTO subjects (name) VALUES (%s)", (sub,))
    print("Seeded subjects table.")

    # 3. Add subject_id column to courses if not exists
    cursor.execute("SHOW COLUMNS FROM courses LIKE 'subject_id'")
    column_exists = cursor.fetchone()
    if not column_exists:
        cursor.execute("ALTER TABLE courses ADD COLUMN subject_id INT NULL")
        cursor.execute("ALTER TABLE courses ADD CONSTRAINT fk_course_subject FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL")
        print("Added subject_id column and foreign key constraint to courses table.")
    else:
        print("subject_id column already exists in courses.")

    # 4. Dashboard Widgets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dashboard_widgets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            widget_key VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
            sort_order INT NOT NULL DEFAULT 0
        )
    """)
    print("Dashboard widgets table verified.")

    widgets_seed = [
        ('telemetry', 'Platform Telemetry Status', True, 1),
        ('user_stats', 'User Registration Metrics', True, 2),
        ('recent_activity', 'Live System Activity Logs', True, 3),
        ('course_distribution', 'Active Course Distributions', True, 4)
    ]
    for key, name, enabled, order in widgets_seed:
        cursor.execute("""
            INSERT INTO dashboard_widgets (widget_key, name, is_enabled, sort_order) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE name=%s, is_enabled=%s, sort_order=%s
        """, (key, name, enabled, order, name, enabled, order))
    print("Seeded dashboard widgets.")

    # 5. Library Settings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS library_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(100) UNIQUE NOT NULL,
            access_mode VARCHAR(50) NOT NULL DEFAULT 'OPEN'
        )
    """)
    print("Library settings table verified.")

    library_seed = [
        ('Class 9', 'OPEN'),
        ('Class 10', 'OPEN'),
        ('Class 11', 'OPEN'),
        ('Class 12', 'OPEN'),
        ('Advanced Topics', 'OPEN'),
        ('Skill Tracks', 'OPEN')
    ]
    for cat, mode in library_seed:
        cursor.execute("""
            INSERT INTO library_settings (category_name, access_mode)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE access_mode=%s
        """, (cat, mode, mode))
    print("Seeded library settings.")

    # 6. Activity Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            event_type VARCHAR(255) NOT NULL,
            event_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    print("Activity logs table verified.")

    conn.commit()
    print("All migrations committed successfully!")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Migration failed: {e}")
