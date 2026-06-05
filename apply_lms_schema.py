import os
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

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
    cursor = conn.cursor(dictionary=True)
    print("Connected to MySQL database. Applying alterations...")

    # 1. Update user role check constraint
    print("Altering user role constraint...")
    try:
        cursor.execute("ALTER TABLE users DROP CHECK chk_role")
    except Exception as e:
        print(f"  Note: Failed to DROP CHECK chk_role (might not exist as CHECK): {e}")
    try:
        cursor.execute("ALTER TABLE users DROP CONSTRAINT chk_role")
    except Exception as e:
        print(f"  Note: Failed to DROP CONSTRAINT chk_role: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD CONSTRAINT chk_role CHECK (role IN ('student', 'teacher', 'admin', 'superadmin'))")
        print("  Successfully updated users check constraint.")
    except Exception as e:
        print(f"  Warning: Failed to add updated users check constraint: {e}")

    # 2. Create categories and courses tables
    print("Creating LMS core tables...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        category VARCHAR(100),
        class_level VARCHAR(50),
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        CONSTRAINT chk_course_status CHECK (status IN ('active', 'archived'))
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modules (
        id INT AUTO_INCREMENT PRIMARY KEY,
        course_id INT NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        order_index INT DEFAULT 0,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    )
    """)

    # 3. Alter chapters table
    print("Altering chapters table...")
    try:
        cursor.execute("ALTER TABLE chapters ADD COLUMN module_id INT NULL")
    except Exception as e:
        print(f"  Note: module_id column already exists or failed: {e}")
    try:
        cursor.execute("ALTER TABLE chapters ADD CONSTRAINT fk_chapter_module FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE SET NULL")
    except Exception as e:
        print(f"  Note: fk_chapter_module constraint already exists or failed: {e}")

    # 4. Create lessons and resources tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        chapter_id INT NOT NULL,
        title VARCHAR(255) NOT NULL,
        content TEXT,
        order_index INT DEFAULT 0,
        status VARCHAR(50) NOT NULL DEFAULT 'published',
        publish_at TIMESTAMP NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        CONSTRAINT chk_lesson_status CHECK (status IN ('draft', 'published', 'scheduled')),
        FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        id INT AUTO_INCREMENT PRIMARY KEY,
        lesson_id INT,
        title VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_type VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'published',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT chk_resource_status CHECK (status IN ('draft', 'published', 'archived')),
        FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
    )
    """)

    # 5. Create enrollments and teacher mappings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS course_enrollments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        course_id INT NOT NULL,
        student_id INT NOT NULL,
        progress INT DEFAULT 0,
        status VARCHAR(50) NOT NULL DEFAULT 'active',
        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP NULL,
        UNIQUE(course_id, student_id),
        CONSTRAINT chk_enrollment_status CHECK (status IN ('active', 'completed')),
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher_courses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        course_id INT NOT NULL,
        teacher_id INT NOT NULL,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(course_id, teacher_id),
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
        FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # 6. Create certificates, notifications, audit logs, and permissions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS certificates (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        course_id INT NOT NULL,
        verification_id VARCHAR(100) NOT NULL UNIQUE,
        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) NOT NULL DEFAULT 'issued',
        CONSTRAINT chk_certificate_status CHECK (status IN ('issued', 'revoked')),
        FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sender_id INT NOT NULL,
        recipient_id INT NULL,
        target_group VARCHAR(100) NULL,
        title VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        action VARCHAR(255) NOT NULL,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS permissions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        role VARCHAR(50) NOT NULL,
        permission_key VARCHAR(100) NOT NULL,
        is_granted BOOLEAN DEFAULT TRUE,
        UNIQUE(role, permission_key)
    )
    """)

    # Seed default permissions for Admin role
    admin_perms = [
        ('admin', 'manage_users'),
        ('admin', 'manage_content'),
        ('admin', 'manage_assessments'),
        ('admin', 'manage_certificates'),
        ('admin', 'send_notifications'),
        ('admin', 'view_reports')
    ]
    for role, key in admin_perms:
        try:
            cursor.execute(
                "INSERT IGNORE INTO permissions (role, permission_key, is_granted) VALUES (%s, %s, TRUE)",
                (role, key)
            )
        except Exception as e:
            print(f"  Note: Failed to seed admin permission {key}: {e}")

    # Seed default Super Admin user
    print("Seeding Super Admin user...")
    try:
        cursor.execute("SELECT id FROM users WHERE email = 'superadmin@chemlove.com'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, institution, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
                ("Super Admin", "superadmin@chemlove.com", generate_password_hash("superadmin123"), "ChemLove HQ", "superadmin", "active")
            )
            print("  Created superadmin@chemlove.com with password 'superadmin123'")
        else:
            print("  Super Admin user already exists.")
    except Exception as e:
        print(f"  Warning: Failed to seed Super Admin user: {e}")

    # Seed default courses for each grade level
    print("Seeding default courses and modules...")
    courses_seed = [
        ("9", "Matter & Physical Science", "Introduction to particulate study, melting points of ice, and fundamental properties of matter.", "Science"),
        ("10", "Acids, Bases & Salinity", "Comprehensive study of acidic structures, indicator determination, and neutralization reactions.", "Chemistry"),
        ("11", "Organic Synthesis & Fundamentals", "Advanced study of hydrocarbons, laboratory synthesis (Wurtz, Kolbe), and titration simulation.", "Chemistry"),
        ("12", "Chemical Kinetics & Reaction Rates", "Analysis of reaction speed, thiosulphate concentration effect, and mathematical expressions.", "Chemistry")
    ]
    for class_level, title, desc, cat in courses_seed:
        cursor.execute("SELECT id FROM courses WHERE class_level = %s", (class_level,))
        course = cursor.fetchone()
        if not course:
            cursor.execute(
                "INSERT INTO courses (title, description, category, class_level, status) VALUES (%s, %s, %s, %s, 'active')",
                (title, desc, cat, class_level)
            )
            course_id = cursor.lastrowid
            print(f"  Created Course: {title} (ID: {course_id})")
        else:
            course_id = course["id"]
            print(f"  Course '{title}' already exists (ID: {course_id})")

        # Create a default module in this course
        cursor.execute("SELECT id FROM modules WHERE course_id = %s", (course_id,))
        module = cursor.fetchone()
        if not module:
            cursor.execute(
                "INSERT INTO modules (course_id, title, description) VALUES (%s, %s, %s)",
                (course_id, "Core Syllabus Modules", f"Fundamental curriculum modules for Class {class_level}")
            )
            module_id = cursor.lastrowid
            print(f"    Created default Module (ID: {module_id})")
        else:
            module_id = module["id"]

        # Map existing chapters to this module
        # Class 9 -> Chapter 4
        # Class 10 -> Chapter 5
        # Class 11 -> Chapter 1, 2, 3
        # Class 12 -> Chapter 6
        if class_level == "9":
            cursor.execute("UPDATE chapters SET module_id = %s WHERE id = 4", (module_id,))
        elif class_level == "10":
            cursor.execute("UPDATE chapters SET module_id = %s WHERE id = 5", (module_id,))
        elif class_level == "11":
            cursor.execute("UPDATE chapters SET module_id = %s WHERE id IN (1, 2, 3)", (module_id,))
        elif class_level == "12":
            cursor.execute("UPDATE chapters SET module_id = %s WHERE id = 6", (module_id,))

    conn.commit()
    cursor.close()
    conn.close()
    print("Database alterations and default seeding completed successfully.")

if __name__ == "__main__":
    main()
