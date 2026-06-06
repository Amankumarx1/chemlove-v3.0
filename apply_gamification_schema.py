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
    print("Connected to MySQL database. Applying gamification alterations...")

    alters = [
        # 1. Add mobile to users
        ("ALTER TABLE users ADD COLUMN mobile VARCHAR(20) NULL", "mobile in users"),
        # 2. Add streak_count to student_profiles
        ("ALTER TABLE student_profiles ADD COLUMN streak_count INT NOT NULL DEFAULT 0", "streak_count in student_profiles"),
        # 3. Add last_active_date to student_profiles
        ("ALTER TABLE student_profiles ADD COLUMN last_active_date DATE NULL", "last_active_date in student_profiles"),
        # 4. Add last_chapter_id to student_profiles
        ("ALTER TABLE student_profiles ADD COLUMN last_chapter_id INT NULL", "last_chapter_id in student_profiles"),
        # 5. Add last_experiment_id to student_profiles
        ("ALTER TABLE student_profiles ADD COLUMN last_experiment_id INT NULL", "last_experiment_id in student_profiles"),
        # 6. Add last_assessment_id to student_profiles
        ("ALTER TABLE student_profiles ADD COLUMN last_assessment_id INT NULL", "last_assessment_id in student_profiles"),
    ]

    for sql, desc in alters:
        try:
            cursor.execute(sql)
            print(f"  Successfully applied: {desc}")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower() or "1060" in str(e):
                print(f"  Column already exists (skipping): {desc}")
            else:
                print(f"  Error applying {desc}: {e}")

    constraints = [
        ("ALTER TABLE student_profiles ADD CONSTRAINT fk_sp_last_chapter FOREIGN KEY (last_chapter_id) REFERENCES chapters(id) ON DELETE SET NULL", "fk_sp_last_chapter"),
        ("ALTER TABLE student_profiles ADD CONSTRAINT fk_sp_last_experiment FOREIGN KEY (last_experiment_id) REFERENCES experiments(id) ON DELETE SET NULL", "fk_sp_last_experiment"),
        ("ALTER TABLE student_profiles ADD CONSTRAINT fk_sp_last_assessment FOREIGN KEY (last_assessment_id) REFERENCES quizzes(id) ON DELETE SET NULL", "fk_sp_last_assessment")
    ]

    for sql, desc in constraints:
        try:
            cursor.execute(sql)
            print(f"  Successfully applied: {desc}")
        except Exception as e:
            if "duplicate key" in str(e).lower() or "already exists" in str(e).lower() or "1061" in str(e) or "1826" in str(e):
                print(f"  Constraint already exists (skipping): {desc}")
            else:
                print(f"  Error applying constraint {desc}: {e}")

    # Seed some default badges if they don't exist
    print("Verifying badge definitions...")
    badges = [
        (1, "Top Performer", "Awarded for achieving Rank #1 on your class leaderboard", "trophy", 100),
        (2, "Consistency Champion", "Awarded for maintaining a learning streak of 7 days or more", "fire", 100),
        (3, "Fast Learner", "Awarded for scoring 100% on a quiz on the first attempt", "zap", 100),
        (4, "Assessment Master", "Awarded for completing 5 quizzes with high marks", "target", 150),
        (5, "Lab Expert", "Awarded for completing 3 virtual chemistry experiments", "flask", 150)
    ]
    
    for bid, name, desc, icon, xp in badges:
        try:
            cursor.execute("SELECT id FROM badges WHERE id = %s", (bid,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO badges (id, name, description, icon, xp_reward) VALUES (%s, %s, %s, %s, %s)",
                    (bid, name, desc, icon, xp)
                )
                print(f"  Seeded badge: {name}")
            else:
                cursor.execute(
                    "UPDATE badges SET name = %s, description = %s, icon = %s, xp_reward = %s WHERE id = %s",
                    (name, desc, icon, xp, bid)
                )
        except Exception as e:
            print(f"  Error seeding/updating badge {name}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Database alterations completed successfully.")

if __name__ == "__main__":
    main()
