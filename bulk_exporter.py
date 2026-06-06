import csv
import json
import mysql.connector
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

def get_db_connection():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("mysql://"):
        parsed = urlparse(db_url)
        return mysql.connector.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/')
        )
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "chemlove")
    )

def import_courses_csv(file_path):
    """Imports courses from a CSV file. Columns: title, description, category, class_level, status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    imported_count = 0
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title")
            description = row.get("description", "")
            category = row.get("category", "")
            class_level = row.get("class_level", "10")
            status = row.get("status", "draft")
            if title:
                cursor.execute(
                    "INSERT INTO courses (title, description, category, class_level, status) VALUES (%s, %s, %s, %s, %s)",
                    (title, description, category, class_level, status)
                )
                imported_count += 1
    conn.commit()
    cursor.close()
    conn.close()
    return imported_count

def import_questions_csv(file_path, quiz_id):
    """Imports MCQ questions for a quiz from a CSV file.
    Columns: question_text, option_a, option_b, option_c, option_d, correct_option, explanation
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    imported_count = 0
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            q_text = row.get("question_text")
            opt_a = row.get("option_a", "")
            opt_b = row.get("option_b", "")
            opt_c = row.get("option_c", "")
            opt_d = row.get("option_d", "")
            correct = row.get("correct_option", "A")
            explanation = row.get("explanation", "")
            if q_text:
                options = {"A": opt_a, "B": opt_b, "C": opt_c, "D": opt_d}
                cursor.execute(
                    """
                    INSERT INTO quiz_questions (quiz_id, question, options_json, correct_answer, explanation) 
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (quiz_id, q_text, json.dumps(options), correct, explanation)
                )
                imported_count += 1
    conn.commit()
    cursor.close()
    conn.close()
    return imported_count

def import_students_csv(file_path):
    """Imports/enrolls students from a CSV. Columns: name, email, password, class_level"""
    from werkzeug.security import generate_password_hash
    conn = get_db_connection()
    cursor = conn.cursor()
    imported_count = 0
    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name")
            email = row.get("email")
            password = row.get("password", "pass123")
            class_level = row.get("class_level", "10")
            if name and email:
                hashed_pw = generate_password_hash(password)
                try:
                    cursor.execute(
                        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'student')",
                        (name, email, hashed_pw)
                    )
                    user_id = cursor.lastrowid
                    cursor.execute(
                        "INSERT INTO student_profiles (user_id, class_level, current_xp, daily_streak) VALUES (%s, %s, 100, 0)",
                        (user_id, class_level)
                    )
                    imported_count += 1
                except mysql.connector.Error as err:
                    print(f"Skipping duplicate or error for user {email}: {err}")
    conn.commit()
    cursor.close()
    conn.close()
    return imported_count
