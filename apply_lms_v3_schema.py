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
    print("Connected to MySQL database. Applying LMS v3 updates...")

    # 1. Create schools table
    print("Creating schools table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schools (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        domain VARCHAR(255) UNIQUE,
        access_mode VARCHAR(50) DEFAULT 'STRICT',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Create batches table
    print("Creating batches table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batches (
        id INT AUTO_INCREMENT PRIMARY KEY,
        classroom_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        start_date DATE,
        end_date DATE,
        FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE
    )
    """)

    # 3. Alter courses table
    print("Altering courses table for CMS support...")
    course_alters = [
        "ALTER TABLE courses ADD COLUMN thumbnail VARCHAR(500) NULL",
        "ALTER TABLE courses ADD COLUMN version INT DEFAULT 1",
        "ALTER TABLE courses ADD COLUMN published_at TIMESTAMP NULL",
        "ALTER TABLE courses MODIFY COLUMN status VARCHAR(50) NOT NULL DEFAULT 'draft'"
    ]
    for sql in course_alters:
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"  Note: course alter failed or column already exists: {e}")

    try:
        cursor.execute("UPDATE courses SET status = 'published' WHERE status = 'active'")
        print("  Updated status of existing courses to 'published'.")
    except Exception as e:
        print(f"  Note: Failed to update existing course status: {e}")

    try:
        cursor.execute("ALTER TABLE courses DROP CHECK chk_course_status")
    except Exception as e:
        pass
    try:
        cursor.execute("ALTER TABLE courses DROP CONSTRAINT chk_course_status")
    except Exception as e:
        pass
    try:
        cursor.execute("ALTER TABLE courses ADD CONSTRAINT chk_course_status CHECK (status IN ('draft', 'review', 'published', 'archived'))")
        print("  Added chk_course_status check constraint to courses table.")
    except Exception as e:
        print(f"  Note: Failed to add course status check: {e}")

    # 4. Alter chapters table
    print("Altering chapters table for CMS and Versioning support...")
    chapter_alters = [
        "ALTER TABLE chapters ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'draft'",
        "ALTER TABLE chapters ADD COLUMN version INT DEFAULT 1",
        "ALTER TABLE chapters ADD COLUMN order_index INT DEFAULT 0",
        "ALTER TABLE chapters ADD COLUMN publish_at TIMESTAMP NULL"
    ]
    for sql in chapter_alters:
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"  Note: chapter alter failed or column already exists: {e}")

    # 5. Create content_versions table
    print("Creating content_versions table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS content_versions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        content_type VARCHAR(50) NOT NULL,
        content_id INT NOT NULL,
        version_number INT NOT NULL,
        title VARCHAR(255) NOT NULL,
        content_data LONGTEXT NOT NULL,
        created_by INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE (content_type, content_id, version_number)
    )
    """)

    # 6. Create progress tables
    print("Creating student progress and telemetry tables...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS course_progress (
        user_id INT NOT NULL,
        course_id INT NOT NULL,
        percent_completed DECIMAL(5,2) DEFAULT 0.00,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, course_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapter_progress (
        user_id INT NOT NULL,
        chapter_id INT NOT NULL,
        is_completed BOOLEAN DEFAULT FALSE,
        completed_at TIMESTAMP NULL,
        PRIMARY KEY (user_id, chapter_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lesson_progress (
        user_id INT NOT NULL,
        lesson_id INT NOT NULL,
        is_completed BOOLEAN DEFAULT FALSE,
        time_spent_seconds INT DEFAULT 0,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, lesson_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_progress (
        user_id INT NOT NULL,
        assessment_type VARCHAR(50) NOT NULL,
        assessment_id INT NOT NULL,
        score_percentage DECIMAL(5,2) DEFAULT 0.00,
        attempts_count INT DEFAULT 1,
        is_passed BOOLEAN DEFAULT FALSE,
        last_attempt_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, assessment_type, assessment_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 7. Create certificate_templates table
    print("Creating certificate templates table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS certificate_templates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        html_layout LONGTEXT NOT NULL,
        css_styles LONGTEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Alter certificates to add template_id
    print("Altering certificates table for template association...")
    try:
        cursor.execute("ALTER TABLE certificates ADD COLUMN template_id INT NULL")
    except Exception as e:
        print(f"  Note: template_id already exists in certificates: {e}")

    try:
        cursor.execute("ALTER TABLE certificates ADD CONSTRAINT fk_cert_template FOREIGN KEY (template_id) REFERENCES certificate_templates(id) ON DELETE SET NULL")
    except Exception as e:
        print(f"  Note: fk_cert_template already exists in certificates: {e}")

    # Seed default school configuration
    print("Seeding default school configuration...")
    try:
        cursor.execute("SELECT id FROM schools WHERE domain = 'chemlove.com'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO schools (name, domain, access_mode) VALUES ('ChemLove Academy', 'chemlove.com', 'STRICT')")
            print("  Created default school ChemLove Academy.")
    except Exception as e:
        print(f"  Warning: Failed to seed default school: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("LMS v3 database updates applied successfully.")

if __name__ == "__main__":
    main()
