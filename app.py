import os
import sqlite3
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv()

import psycopg
from psycopg.rows import dict_row
from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

# ── No-cache for authentication pages ──────────────────────────────────────
_AUTH_PATHS = ('/login', '/signup', '/auth')

@app.after_request
def no_cache_html(response):
    """Prevent the browser from caching any server-rendered HTML page.
    This ensures that after login/logout the correct navbar (logged-in vs
    logged-out) is always shown without needing a manual refresh.
    Static assets (JS, CSS, images) are excluded so they remain cached.
    """
    content_type = response.headers.get('Content-Type', '')
    if 'text/html' in content_type:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

DATABASE_URL = os.getenv("DATABASE_URL")

class SQLiteCursorWrapper:
    def __init__(self, cursor, lastrowid=None):
        self.cursor = cursor
        self._lastrowid = lastrowid
        self.description = cursor.description
        self.colnames = [col[0] for col in self.description] if self.description else []

    def _to_dict(self, row):
        if row is None:
            return None
        return dict(zip(self.colnames, row))

    def fetchone(self):
        row = self.cursor.fetchone()
        if not row:
            if self._lastrowid is not None:
                return {"id": self._lastrowid}
            return None
        return self._to_dict(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [self._to_dict(r) for r in rows]


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

    def execute(self, query, params=None):
        # Translate placeholder and serial syntax to be compatible with SQLite
        query = query.replace('%s', '?')
        if "SERIAL PRIMARY KEY" in query:
            query = query.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return SQLiteCursorWrapper(cursor)
        except Exception as e:
            if "RETURNING" in query.upper() and ("near \"RETURNING\"" in str(e).lower() or "syntax error" in str(e).lower()):
                clean_query = query
                returning_idx = query.upper().rfind("RETURNING")
                if returning_idx != -1:
                    clean_query = query[:returning_idx].strip()
                if params:
                    cursor.execute(clean_query, params)
                else:
                    cursor.execute(clean_query)
                return SQLiteCursorWrapper(cursor, lastrowid=cursor.lastrowid)
            raise e


USING_SQLITE = False

def get_db():
    global USING_SQLITE
    
    if USING_SQLITE:
        conn = sqlite3.connect("chemlove.db")
        return SQLiteConnectionWrapper(conn)
        
    if not DATABASE_URL:
        print("[DATABASE] DATABASE_URL is not set. Falling back to local SQLite (chemlove.db).")
        USING_SQLITE = True
        conn = sqlite3.connect("chemlove.db")
        return SQLiteConnectionWrapper(conn)
        
    try:
        # Connect to PostgreSQL with a brief timeout so startup doesn't hang
        return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=3)
    except Exception as e:
        print(f"[DATABASE] Connection to PostgreSQL failed: {e}")
        print("[DATABASE] Falling back to local SQLite (chemlove.db).")
        USING_SQLITE = True
        conn = sqlite3.connect("chemlove.db")
        return SQLiteConnectionWrapper(conn)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def init_db():
    """Initialise the database.
    
    For SQLite: create all tables and seed default data.
    For PostgreSQL (Supabase): tables already exist — only run a quick
    connectivity check so we can confirm the connection is working.
    """
    if USING_SQLITE:
        with get_db() as connection:
            # Create users table
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    institution TEXT NOT NULL,
                    role TEXT NOT NULL,
                    class_level TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            try:
                connection.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
            except Exception:
                pass

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS student_profiles (
                    user_id INTEGER PRIMARY KEY,
                    current_xp INTEGER DEFAULT 100,
                    level INTEGER DEFAULT 1,
                    weak_topics TEXT,
                    strong_topics TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS teacher_profiles (
                    user_id INTEGER PRIMARY KEY,
                    department TEXT DEFAULT 'Chemistry',
                    qualifications TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS classrooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    section TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    classroom_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    enrolled_at TEXT NOT NULL,
                    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    class_level TEXT NOT NULL,
                    description TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS labs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    chapter_id INTEGER,
                    status TEXT DEFAULT 'published',
                    description TEXT,
                    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    classroom_id INTEGER NOT NULL,
                    chapter_id INTEGER,
                    lab_id INTEGER,
                    marks INTEGER DEFAULT 100,
                    due_date TEXT,
                    instructions TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
                    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL,
                    FOREIGN KEY (lab_id) REFERENCES labs(id) ON DELETE SET NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    submitted_at TEXT NOT NULL,
                    file_data TEXT,
                    marks_obtained REAL,
                    feedback TEXT,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    classroom_id INTEGER NOT NULL,
                    chapter_id INTEGER,
                    duration_minutes INTEGER DEFAULT 30,
                    total_marks INTEGER DEFAULT 100,
                    start_date TEXT,
                    end_date TEXT,
                    difficulty TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'scheduled',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
                    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE SET NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS test_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    options_json TEXT,
                    correct_answer TEXT NOT NULL,
                    marks INTEGER DEFAULT 1,
                    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS test_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    score REAL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT DEFAULT 'completed',
                    suspicious_alerts_count INTEGER DEFAULT 0,
                    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    classroom_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author_id INTEGER NOT NULL,
                    classroom_id INTEGER,
                    target_role TEXT,
                    is_pinned INTEGER DEFAULT 0,
                    publish_at TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (classroom_id) REFERENCES classrooms(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS badges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    icon TEXT,
                    requirements_json TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    badge_id INTEGER NOT NULL,
                    unlocked_at TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_xp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT,
                    is_read INTEGER DEFAULT 0,
                    type TEXT,
                    link TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    target_table TEXT,
                    target_id INTEGER,
                    details TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS theme_preferences (
                    user_id INTEGER PRIMARY KEY,
                    theme TEXT DEFAULT 'system',
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS leaderboard_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    xp INTEGER NOT NULL,
                    rank INTEGER,
                    week_start TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            # Seed default badges
            row = connection.execute("SELECT COUNT(*) as count FROM badges").fetchone()
            if not row or row["count"] == 0:
                default_badges = [
                    ("Lab Pioneer", "Simulated your first chemical reaction successfully.", "science", '{"reaction_count": 1}'),
                    ("Titration Master", "Completed a precise acid-base neutralization.", "opacity", '{"titration_count": 1}'),
                    ("Concept Overlord", "Unlocked 90% mastery in any syllabus chapter.", "psychology", '{"mastery": 90}'),
                    ("Safety Inspector", "Logged 10 consecutive safe simulations without volatile explosions.", "verified_user", '{"safety_count": 10}')
                ]
                for b in default_badges:
                    connection.execute("INSERT INTO badges(name, description, icon, requirements_json) VALUES (%s, %s, %s, %s)", b)

            # Seed default chapters
            row_ch = connection.execute("SELECT COUNT(*) as count FROM chapters").fetchone()
            if not row_ch or row_ch["count"] == 0:
                default_chapters = [
                    (1, "Chemical Reactions and Equations", "10", "Introduction to balancing chemical equations, combination, decomposition, displacement, and redox reactions."),
                    (2, "Acids, Bases and Salts", "10", "Understanding indicators, pH scales, chemical properties of acids and bases, and salts characteristics."),
                    (3, "Metals and Non-metals", "10", "Properties of metals/non-metals, reactivity series, ionic compound properties, and metallurgy."),
                    (4, "Carbon and its Compounds", "10", "Covalent bonding, versatile nature of carbon, homologous series, and functional groups."),
                    (5, "Hydrocarbons", "11", "Alkanes, alkenes, alkynes, isomerism, and methods of preparation (like Wurtz Reaction).")
                ]
                for ch in default_chapters:
                    connection.execute("INSERT INTO chapters(number, title, class_level, description) VALUES (%s, %s, %s, %s)", ch)

            # Sync chapter JSON files
            import glob, re, json
            chapters_dir = os.path.join('content', 'chapters')
            if os.path.exists(chapters_dir):
                for filepath in glob.glob(os.path.join(chapters_dir, 'chapter_*.json')):
                    filename = os.path.basename(filepath)
                    match = re.match(r'chapter_(\d+)\.json', filename)
                    if match:
                        ch_num = int(match.group(1))
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                ch_data = json.load(f)
                            title = ch_data.get("title", f"Chapter {ch_num}")
                            description = ch_data.get("description", "")
                            class_level = str(ch_data.get("class", ch_data.get("class_level", "11")))
                            existing = connection.execute("SELECT id FROM chapters WHERE number = %s", (ch_num,)).fetchone()
                            if existing:
                                connection.execute(
                                    "UPDATE chapters SET title = %s, class_level = %s, description = %s WHERE number = %s",
                                    (title, class_level, description, ch_num)
                                )
                            else:
                                connection.execute(
                                    "INSERT INTO chapters(id, number, title, class_level, description) VALUES (%s, %s, %s, %s, %s)",
                                    (ch_num, ch_num, title, class_level, description)
                                )
                        except Exception as e:
                            print(f"[DATABASE] Error syncing chapter JSON {filename}: {e}")

            # Seed default labs
            row_lb = connection.execute("SELECT COUNT(*) as count FROM labs").fetchone()
            if not row_lb or row_lb["count"] == 0:
                default_labs = [
                    ("Virtual Sandbox", 5, "published", "Mix any organic/inorganic reagents in a safe virtual drop-zone."),
                    ("Acid-Base Titration Workbench", 2, "published", "Drop-wise addition of titrant into an analyte to trace equivalence pH curves.")
                ]
                for lb in default_labs:
                    connection.execute("INSERT INTO labs(name, chapter_id, status, description) VALUES (%s, %s, %s, %s)", lb)

            # Ensure default admin user exists
            admin_row = connection.execute("SELECT * FROM users WHERE email = %s", ("admin@chemlove.com",)).fetchone()
            if admin_row:
                if admin_row["role"] != "admin" or admin_row["status"] != "active":
                    connection.execute(
                        "UPDATE users SET role = %s, status = %s, password_hash = %s WHERE email = %s",
                        ("admin", "active", generate_password_hash("admin123"), "admin@chemlove.com")
                    )
            else:
                created_at = now_iso()
                connection.execute(
                    """
                    INSERT INTO users(name, email, password_hash, institution, role, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    ("Admin", "admin@chemlove.com", generate_password_hash("admin123"),
                     "ChemLove", "admin", "active", created_at, created_at)
                )
            print("[DATABASE] SQLite initialised successfully.")
    else:
        # PostgreSQL / Supabase — tables already exist, just verify connectivity
        try:
            with get_db() as connection:
                connection.execute("SELECT 1").fetchone()
            print("[DATABASE] PostgreSQL connection verified successfully.")
        except Exception as e:
            print(f"[DATABASE] PostgreSQL connectivity check failed: {e}")


def user_from_row(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "institution": row["institution"],
        "role": row["role"],
        "classLevel": row["class_level"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    with get_db() as connection:
        row = connection.execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
        if not row:
            return None
        if row.get("status") == 'suspended':
            session.pop("user_id", None)
            return None
        
        user_dict = user_from_row(row)
        user_dict["status"] = row.get("status", "active")
        
        if user_dict["role"] == "student":
            sp = connection.execute("SELECT current_xp, level FROM student_profiles WHERE user_id = %s", (user_id,)).fetchone()
            if sp:
                user_dict["current_xp"] = sp["current_xp"]
                user_dict["level"] = sp["level"]
            else:
                user_dict["current_xp"] = 100
                user_dict["level"] = 1
    return user_dict


def add_history(user_id, event_type, event_data=None):
    with get_db() as connection:
        connection.execute(
            "INSERT INTO user_history(user_id, event_type, event_data, created_at) VALUES (%s, %s, %s, %s)",
            (user_id, event_type, event_data, now_iso()),
        )


init_db()


def redirect_by_role(user):
    if user['role'] == 'student':
        return redirect(url_for('student_dashboard'))
    elif user['role'] == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('landing/index.html', current_user=get_current_user())


@app.route('/features')
def features():
    return render_template('landing/features.html', current_user=get_current_user())


@app.route('/about')
def about():
    return render_template('landing/about.html', current_user=get_current_user())


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash('Please fill in Name, Email, and Message fields.', 'error')
            return redirect(url_for('contact'))

        user = get_current_user()
        if user:
            add_history(user['id'], "contact_message_sent", f"subject={subject}")

        print(f"[CONTACT FORM] Form submission received from {name} ({email}) - Role: {role}, Subject: {subject}")
        flash('Thank you for reaching out! We will get back to you shortly.', 'success')
        return redirect(url_for('contact'))

    return render_template('landing/contact.html', current_user=get_current_user())


@app.route('/index.html')
def index_html_redirect():
    return redirect(url_for('home'))


@app.route('/login.html')
def login_html_redirect():
    return redirect(url_for('login'))


@app.route('/signup.html')
def signup_html_redirect():
    return redirect(url_for('signup'))


@app.route('/auth')
def auth_page():
    """Canonical /auth URL – redirect logged-in users to their dashboard."""
    user = get_current_user()
    if user:
        return redirect_by_role(user)
    active_form = request.args.get('form', 'login')
    return render_template('landing/auth.html', active_form=active_form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    user = get_current_user()
    if user:
        return redirect_by_role(user)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        institution = request.form.get('institution', '').strip()
        role = request.form.get('role', '').strip()
        class_level = request.form.get('classLevel', '').strip()

        if not name or not email or not password or not institution or not role:
            flash('Please fill all required fields.', 'error')
            return redirect(url_for('signup'))

        if role == 'student' and not class_level:
            flash('Please select class level for student role.', 'error')
            return redirect(url_for('signup'))

        with get_db() as connection:
            existing = connection.execute("SELECT id FROM users WHERE email = %s", (email,)).fetchone()
        if existing:
            flash('Email already exists. Please login.', 'error')
            return redirect(url_for('signup'))

        created_at = now_iso()
        password_hash = generate_password_hash(password)
        with get_db() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users(name, email, password_hash, institution, role, class_level, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, 'active', %s, %s)
                RETURNING id
                """,
                (name, email, password_hash, institution, role, class_level if role == 'student' else None, created_at, created_at),
            )
            user_id = cursor.fetchone()["id"]
            
            # Create corresponding profile
            if role == 'student':
                connection.execute(
                    "INSERT INTO student_profiles(user_id, current_xp, level) VALUES (%s, 100, 1)",
                    (user_id,)
                )
            elif role == 'teacher':
                connection.execute(
                    "INSERT INTO teacher_profiles(user_id, department) VALUES (%s, 'Chemistry')",
                    (user_id,)
                )
        session['user_id'] = user_id
        add_history(user_id, "signup_success", f"role={role}")
        flash('Signup successful. Welcome!', 'success')
        
        with get_db() as connection:
            user = connection.execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
        return redirect_by_role(user)

    return render_template('landing/auth.html', active_form='signup')


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if user:
        return redirect_by_role(user)
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        with get_db() as connection:
            user = connection.execute("SELECT * FROM users WHERE email = %s", (email,)).fetchone()

        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

        if user.get('status') == 'suspended':
            flash('This account has been suspended. Please contact the administrator.', 'error')
            return redirect(url_for('login'))

        session['user_id'] = user['id']
        add_history(user['id'], "login_success")
        flash('Login successful.', 'success')
        return redirect_by_role(user)

    return render_template('landing/auth.html', active_form='login')


@app.route('/logout', methods=['POST'])
def logout():
    user_id = session.get("user_id")
    if user_id:
        add_history(user_id, "logout")
    session.pop('user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/profile')
def profile_page():
    user = get_current_user()
    if not user:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    return render_template('student/profile.html', current_user=user, active_tab='profile')


@app.route('/api/profile', methods=['GET', 'PUT'])
def profile_api():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        return jsonify({"profile": user})

    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or user["name"]).strip()
    institution = (payload.get("institution") or user["institution"]).strip()
    class_level = (payload.get("classLevel") if user["role"] == "student" else None)
    updated_at = now_iso()
    with get_db() as connection:
        connection.execute(
            "UPDATE users SET name = %s, institution = %s, class_level = %s, updated_at = %s WHERE id = %s",
            (name, institution, class_level, updated_at, user["id"]),
        )
    add_history(user["id"], "profile_updated")
    return jsonify({"ok": True})


@app.route('/api/history')
def history_api():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    with get_db() as connection:
        rows = connection.execute(
            "SELECT event_type, event_data, created_at FROM user_history WHERE user_id = %s ORDER BY id DESC LIMIT 50",
            (user["id"],),
        ).fetchall()
    return jsonify({"history": rows})


@app.route('/dashboard')
def dashboard_page():
    user = get_current_user()
    if not user:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    if user['role'] == 'student':
        return redirect(url_for('student_dashboard'))
    elif user['role'] == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('home'))


@app.route('/api/log_event', methods=['POST'])
def log_event_api():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    payload = request.get_json(silent=True) or {}
    event_type = payload.get("event_type")
    event_data = payload.get("event_data")
    
    if not event_type:
        return jsonify({"error": "Missing event_type"}), 400
        
    add_history(user["id"], event_type, event_data)
    return jsonify({"ok": True})


# ============================================================
# ROLE-BASED PORTALS DECORATORS & ROUTING
# ============================================================

from functools import wraps

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if user['role'] != 'student':
            flash('Unauthorized access.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if user['role'] != 'teacher':
            flash('Unauthorized access. Teacher role required.', 'error')
            return redirect(url_for('profile_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if user['role'] != 'admin':
            flash('Unauthorized access. Admin role required.', 'error')
            return redirect(url_for('profile_page'))
        return f(*args, **kwargs)
    return decorated_function


# Student portal endpoints
@app.route('/student/dashboard')
@student_required
def student_dashboard():
    return render_template('student/dashboard.html', current_user=get_current_user(), active_tab='dashboard')


@app.route('/student/chapters')
@student_required
def student_chapters():
    with get_db() as connection:
        rows = connection.execute("SELECT * FROM chapters").fetchall()
    return render_template('student/chapters.html', current_user=get_current_user(), chapters=rows, active_tab='chapters')


@app.route('/student/chapter/<int:chapter_id>')
@student_required
def student_chapter_view(chapter_id):
    import json
    chapter_file = os.path.join('content', 'chapters', f'chapter_{chapter_id}.json')
    if not os.path.exists(chapter_file):
        flash('Chapter content not found.', 'error')
        return redirect(url_for('student_chapters'))
    with open(chapter_file, 'r', encoding='utf-8') as f:
        chapter_data = json.load(f)
    return render_template('student/chapter_view.html', current_user=get_current_user(), chapter_data=chapter_data, active_tab='chapters')


@app.route('/student/reactions')
@student_required
def student_reactions():
    return render_template('student/reactions.html', current_user=get_current_user(), active_tab='reactions')


@app.route('/student/experiments')
@student_required
def student_experiments():
    import json
    experiments = []
    exp_dir = os.path.join('content', 'experiments')
    if os.path.exists(exp_dir):
        for filename in sorted(os.listdir(exp_dir)):
            if filename.endswith('.json'):
                with open(os.path.join(exp_dir, filename), 'r', encoding='utf-8') as f:
                    try:
                        experiments.append(json.load(f))
                    except Exception:
                        pass
    return render_template('student/experiments.html', current_user=get_current_user(), experiments=experiments, active_tab='experiments')


@app.route('/student/experiment/<int:experiment_id>')
@student_required
def student_experiment_view(experiment_id):
    import json
    exp_file = os.path.join('content', 'experiments', f'{experiment_id}.json')
    if not os.path.exists(exp_file):
        flash('Experiment content not found.', 'error')
        return redirect(url_for('student_experiments'))
    with open(exp_file, 'r', encoding='utf-8') as f:
        experiment_data = json.load(f)
    return render_template('student/experiment_view.html', current_user=get_current_user(), experiment=experiment_data, active_tab='experiments')


@app.route('/student/quizzes')
@student_required
def student_quizzes():
    import json
    quizzes = []
    quiz_dir = os.path.join('content', 'quizzes')
    if os.path.exists(quiz_dir):
        for filename in sorted(os.listdir(quiz_dir)):
            if filename.endswith('.json'):
                with open(os.path.join(quiz_dir, filename), 'r', encoding='utf-8') as f:
                    try:
                        quizzes.append(json.load(f))
                    except Exception:
                        pass
    return render_template('student/quizzes.html', current_user=get_current_user(), quizzes=quizzes, active_tab='quizzes')


@app.route('/student/quiz/<int:chapter_id>')
@student_required
def student_quiz_view(chapter_id):
    import json
    quiz_file = os.path.join('content', 'quizzes', f'{chapter_id}.json')
    if not os.path.exists(quiz_file):
        flash('Quiz not found.', 'error')
        return redirect(url_for('student_quizzes'))
    with open(quiz_file, 'r', encoding='utf-8') as f:
        quiz_data = json.load(f)
    return render_template('student/quiz_view.html', current_user=get_current_user(), quiz=quiz_data, active_tab='quizzes')


@app.route('/student/virtual-lab')
@student_required
def student_virtual_lab():
    return render_template('student/virtual_lab.html', current_user=get_current_user(), active_tab='virtual-lab')


@app.route('/student/assignments')
@student_required
def student_assignments():
    return render_template('student/assignments.html', current_user=get_current_user(), active_tab='assignments')


@app.route('/student/profile')
@student_required
def student_profile():
    return redirect(url_for('profile_page'))


# Teacher portal routes
@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    return render_template('teacher/dashboard.html', current_user=get_current_user(), active_tab='dashboard')


@app.route('/teacher/students')
@teacher_required
def teacher_students():
    return render_template('teacher/students.html', current_user=get_current_user(), active_tab='students')


@app.route('/teacher/classes')
@teacher_required
def teacher_classes():
    return render_template('teacher/classes.html', current_user=get_current_user(), active_tab='classes')


@app.route('/teacher/assignments')
@teacher_required
def teacher_assignments():
    return render_template('teacher/assignments.html', current_user=get_current_user(), active_tab='assignments')


@app.route('/teacher/quizzes')
@teacher_required
def teacher_quizzes():
    return render_template('teacher/quizzes.html', current_user=get_current_user(), active_tab='quizzes')


@app.route('/teacher/reports')
@teacher_required
def teacher_reports():
    return render_template('teacher/reports.html', current_user=get_current_user(), active_tab='reports')


# Admin portal routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html', current_user=get_current_user(), active_tab='dashboard')


@app.route('/admin/users')
@admin_required
def admin_users():
    return render_template('admin/users.html', current_user=get_current_user(), active_tab='users')


@app.route('/admin/content')
@admin_required
def admin_content():
    return render_template('admin/content.html', current_user=get_current_user(), active_tab='content')


@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    return render_template('admin/analytics.html', current_user=get_current_user(), active_tab='analytics')


# ============================================================
# API SYSTEM ENDPOINTS
# ============================================================

import json

@app.route('/api/classrooms', methods=['GET', 'POST', 'DELETE'])
def api_classrooms():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        with get_db() as connection:
            if user['role'] == 'teacher':
                rows = connection.execute(
                    "SELECT c.*, (SELECT COUNT(*) FROM enrollments WHERE classroom_id = c.id) as student_count FROM classrooms c WHERE c.teacher_id = %s",
                    (user['id'],)
                ).fetchall()
            elif user['role'] == 'admin':
                rows = connection.execute(
                    "SELECT c.*, u.name as teacher_name, (SELECT COUNT(*) FROM enrollments WHERE classroom_id = c.id) as student_count FROM classrooms c LEFT JOIN users u ON c.teacher_id = u.id"
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT c.*, u.name as teacher_name FROM classrooms c JOIN enrollments e ON c.id = e.classroom_id LEFT JOIN users u ON c.teacher_id = u.id WHERE e.student_id = %s",
                    (user['id'],)
                ).fetchall()
        return jsonify({"classrooms": rows})
        
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        grade = payload.get("grade")
        section = payload.get("section")
        teacher_id = payload.get("teacher_id") or user['id']
        
        if not name or not grade:
            return jsonify({"error": "Missing name or grade"}), 400
            
        with get_db() as connection:
            connection.execute(
                "INSERT INTO classrooms(name, teacher_id, grade, section, created_at) VALUES (%s, %s, %s, %s, %s)",
                (name, teacher_id, grade, section, now_iso())
            )
        return jsonify({"ok": True})
        
    elif request.method == 'DELETE':
        cid = request.args.get("id")
        if not cid:
            return jsonify({"error": "Missing classroom id"}), 400
        with get_db() as connection:
            if user['role'] == 'teacher':
                connection.execute("DELETE FROM classrooms WHERE id = %s AND teacher_id = %s", (cid, user['id']))
            elif user['role'] == 'admin':
                connection.execute("DELETE FROM classrooms WHERE id = %s", (cid,))
            else:
                return jsonify({"error": "Forbidden"}), 403
        return jsonify({"ok": True})


@app.route('/api/students', methods=['GET', 'POST', 'DELETE'])
def api_students():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        classroom_id = request.args.get("classroom_id")
        student_id = request.args.get("student_id")
        
        with get_db() as connection:
            if student_id:
                student_details = connection.execute(
                    "SELECT u.id, u.name, u.email, u.institution, u.class_level, sp.current_xp, sp.level, sp.weak_topics, sp.strong_topics FROM users u LEFT JOIN student_profiles sp ON u.id = sp.user_id WHERE u.id = %s AND u.role = 'student'",
                    (student_id,)
                ).fetchone()
                
                if not student_details:
                    return jsonify({"error": "Student not found"}), 404
                    
                history_rows = connection.execute(
                    "SELECT event_type, event_data, created_at FROM user_history WHERE user_id = %s ORDER BY id DESC LIMIT 20",
                    (student_id,)
                ).fetchall()
                
                attempts_rows = connection.execute(
                    "SELECT ta.*, t.title as test_title FROM test_attempts ta JOIN tests t ON ta.test_id = t.id WHERE ta.student_id = %s",
                    (student_id,)
                ).fetchall()
                
                badges_rows = connection.execute(
                    "SELECT b.name, b.description, b.icon, a.unlocked_at FROM achievements a JOIN badges b ON a.badge_id = b.id WHERE a.student_id = %s",
                    (student_id,)
                ).fetchall()
                
                sub_rows = connection.execute(
                    "SELECT s.*, a.title as assignment_title FROM submissions s JOIN assignments a ON s.assignment_id = a.id WHERE s.student_id = %s",
                    (student_id,)
                ).fetchall()
                
                return jsonify({
                    "student": student_details,
                    "history": history_rows,
                    "attempts": attempts_rows,
                    "badges": badges_rows,
                    "submissions": sub_rows
                })
                
            elif classroom_id:
                rows = connection.execute(
                    """
                    SELECT u.id, u.name, u.email, u.institution, u.class_level, u.status, sp.current_xp, sp.level 
                    FROM users u 
                    JOIN enrollments e ON u.id = e.student_id 
                    LEFT JOIN student_profiles sp ON u.id = sp.user_id 
                    WHERE e.classroom_id = %s
                    """,
                    (classroom_id,)
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT u.id, u.name, u.email, u.institution, u.class_level, u.status, sp.current_xp, sp.level FROM users u LEFT JOIN student_profiles sp ON u.id = sp.user_id WHERE u.role = 'student'"
                ).fetchall()
                
        return jsonify({"students": rows})
        
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        classroom_id = payload.get("classroom_id")
        student_id = payload.get("student_id")
        
        if not classroom_id or not student_id:
            return jsonify({"error": "Missing parameters"}), 400
            
        with get_db() as connection:
            dup = connection.execute("SELECT id FROM enrollments WHERE classroom_id = %s AND student_id = %s", (classroom_id, student_id)).fetchone()
            if not dup:
                connection.execute(
                    "INSERT INTO enrollments(classroom_id, student_id, enrolled_at) VALUES (%s, %s, %s)",
                    (classroom_id, student_id, now_iso())
                )
        return jsonify({"ok": True})
        
    elif request.method == 'DELETE':
        classroom_id = request.args.get("classroom_id")
        student_id = request.args.get("student_id")
        
        if not classroom_id or not student_id:
            return jsonify({"error": "Missing parameters"}), 400
            
        with get_db() as connection:
            connection.execute("DELETE FROM enrollments WHERE classroom_id = %s AND student_id = %s", (classroom_id, student_id))
        return jsonify({"ok": True})


@app.route('/api/assignments', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_assignments():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        classroom_id = request.args.get("classroom_id")
        with get_db() as connection:
            if classroom_id:
                rows = connection.execute(
                    """
                    SELECT a.*, c.name as classroom_name, ch.title as chapter_title, l.name as lab_name, 
                           (SELECT COUNT(*) FROM submissions WHERE assignment_id = a.id) as submission_count 
                    FROM assignments a 
                    JOIN classrooms c ON a.classroom_id = c.id 
                    LEFT JOIN chapters ch ON a.chapter_id = ch.id 
                    LEFT JOIN labs l ON a.lab_id = l.id 
                    WHERE a.classroom_id = %s
                    """,
                    (classroom_id,)
                ).fetchall()
            else:
                if user['role'] == 'teacher':
                    rows = connection.execute(
                        """
                        SELECT a.*, c.name as classroom_name, ch.title as chapter_title, l.name as lab_name,
                               (SELECT COUNT(*) FROM submissions WHERE assignment_id = a.id) as submission_count
                        FROM assignments a 
                        JOIN classrooms c ON a.classroom_id = c.id 
                        LEFT JOIN chapters ch ON a.chapter_id = ch.id 
                        LEFT JOIN labs l ON a.lab_id = l.id 
                        WHERE c.teacher_id = %s
                        """,
                        (user['id'],)
                    ).fetchall()
                elif user['role'] == 'admin':
                    rows = connection.execute(
                        """
                        SELECT a.*, c.name as classroom_name, ch.title as chapter_title, l.name as lab_name,
                               (SELECT COUNT(*) FROM submissions WHERE assignment_id = a.id) as submission_count
                        FROM assignments a 
                        JOIN classrooms c ON a.classroom_id = c.id 
                        LEFT JOIN chapters ch ON a.chapter_id = ch.id 
                        LEFT JOIN labs l ON a.lab_id = l.id
                        """
                    ).fetchall()
                else:
                    rows = connection.execute(
                        """
                        SELECT a.*, c.name as classroom_name, ch.title as chapter_title, l.name as lab_name,
                               s.status as submission_status, s.marks_obtained, s.feedback
                        FROM assignments a 
                        JOIN classrooms c ON a.classroom_id = c.id 
                        JOIN enrollments e ON c.id = e.classroom_id
                        LEFT JOIN chapters ch ON a.chapter_id = ch.id 
                        LEFT JOIN labs l ON a.lab_id = l.id 
                        LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = %s
                        WHERE e.student_id = %s AND a.status = 'published'
                        """,
                        (user['id'], user['id'])
                    ).fetchall()
        return jsonify({"assignments": rows})
        
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        title = payload.get("title")
        description = payload.get("description")
        classroom_id = payload.get("classroom_id")
        chapter_id = payload.get("chapter_id")
        lab_id = payload.get("lab_id")
        marks = payload.get("marks") or 100
        due_date = payload.get("due_date")
        instructions = payload.get("instructions")
        status = payload.get("status") or "draft"
        
        if not title or not classroom_id:
            return jsonify({"error": "Missing title or classroom_id"}), 400
            
        with get_db() as connection:
            connection.execute(
                """
                INSERT INTO assignments(title, description, classroom_id, chapter_id, lab_id, marks, due_date, instructions, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (title, description, classroom_id, chapter_id if chapter_id else None, lab_id if lab_id else None, marks, due_date, instructions, status, now_iso())
            )
        return jsonify({"ok": True})
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        aid = payload.get("id")
        status = payload.get("status")
        
        if not aid or not status:
            return jsonify({"error": "Missing parameters"}), 400
            
        with get_db() as connection:
            connection.execute("UPDATE assignments SET status = %s WHERE id = %s", (status, aid))
        return jsonify({"ok": True})
        
    elif request.method == 'DELETE':
        aid = request.args.get("id")
        if not aid:
            return jsonify({"error": "Missing assignment id"}), 400
        with get_db() as connection:
            connection.execute("DELETE FROM assignments WHERE id = %s", (aid,))
        return jsonify({"ok": True})


@app.route('/api/submissions', methods=['GET', 'POST', 'PUT'])
def api_submissions():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        assignment_id = request.args.get("assignment_id")
        with get_db() as connection:
            if user['role'] in ('teacher', 'admin'):
                if assignment_id:
                    rows = connection.execute(
                        "SELECT s.*, u.name as student_name, u.email as student_email FROM submissions s JOIN users u ON s.student_id = u.id WHERE s.assignment_id = %s",
                        (assignment_id,)
                    ).fetchall()
                else:
                    rows = connection.execute(
                        "SELECT s.*, u.name as student_name, a.title as assignment_title FROM submissions s JOIN users u ON s.student_id = u.id JOIN assignments a ON s.assignment_id = a.id"
                    ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT s.*, a.title as assignment_title FROM submissions s JOIN assignments a ON s.assignment_id = a.id WHERE s.student_id = %s",
                    (user['id'],)
                ).fetchall()
        return jsonify({"submissions": rows})
        
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        assignment_id = payload.get("assignment_id")
        file_data = payload.get("file_data") or ""
        
        if not assignment_id:
            return jsonify({"error": "Missing assignment_id"}), 400
            
        with get_db() as connection:
            existing = connection.execute("SELECT id FROM submissions WHERE assignment_id = %s AND student_id = %s", (assignment_id, user['id'])).fetchone()
            if existing:
                connection.execute(
                    "UPDATE submissions SET file_data = %s, submitted_at = %s, status = 'pending' WHERE id = %s",
                    (file_data, now_iso(), existing["id"])
                )
            else:
                connection.execute(
                    "INSERT INTO submissions(assignment_id, student_id, submitted_at, file_data, status) VALUES (%s, %s, %s, %s, 'pending')",
                    (assignment_id, user['id'], now_iso(), file_data)
                )
        add_history(user['id'], "assignment_submission", f"assignment_id={assignment_id}")
        return jsonify({"ok": True})
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        sid = payload.get("id")
        marks_obtained = payload.get("marks_obtained")
        feedback = payload.get("feedback")
        status = payload.get("status") or "graded"
        
        if not sid or marks_obtained is None:
            return jsonify({"error": "Missing parameters"}), 400
            
        student_id_to_award = None
        with get_db() as connection:
            connection.execute(
                "UPDATE submissions SET marks_obtained = %s, feedback = %s, status = %s WHERE id = %s",
                (marks_obtained, feedback, status, sid)
            )
            if status == 'approved':
                row = connection.execute("SELECT student_id FROM submissions WHERE id = %s", (sid,)).fetchone()
                if row:
                    student_id_to_award = row["student_id"]
                    connection.execute("UPDATE student_profiles SET current_xp = current_xp + 50 WHERE user_id = %s", (student_id_to_award,))
        if student_id_to_award is not None:
            add_history(student_id_to_award, "badge_unlocked", "XP Awarded for Assignment Approval")
        return jsonify({"ok": True})


@app.route('/api/tests', methods=['GET', 'POST', 'DELETE'])
def api_tests():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        test_id = request.args.get("id")
        with get_db() as connection:
            if test_id:
                test = connection.execute("SELECT * FROM tests WHERE id = %s", (test_id,)).fetchone()
                questions = connection.execute("SELECT * FROM test_questions WHERE test_id = %s", (test_id,)).fetchall()
                attempts = connection.execute(
                    "SELECT ta.*, u.name as student_name FROM test_attempts ta JOIN users u ON ta.student_id = u.id WHERE ta.test_id = %s",
                    (test_id,)
                ).fetchall()
                return jsonify({"test": test, "questions": questions, "attempts": attempts})
                
            if user['role'] == 'teacher':
                rows = connection.execute(
                    "SELECT t.*, c.name as classroom_name FROM tests t JOIN classrooms c ON t.classroom_id = c.id WHERE c.teacher_id = %s",
                    (user['id'],)
                ).fetchall()
            elif user['role'] == 'admin':
                rows = connection.execute("SELECT t.*, c.name as classroom_name FROM tests t JOIN classrooms c ON t.classroom_id = c.id").fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT t.*, c.name as classroom_name, ta.score, ta.status as attempt_status 
                    FROM tests t 
                    JOIN classrooms c ON t.classroom_id = c.id 
                    JOIN enrollments e ON c.id = e.classroom_id 
                    LEFT JOIN test_attempts ta ON t.id = ta.test_id AND ta.student_id = %s
                    WHERE e.student_id = %s
                    """,
                    (user['id'], user['id'])
                ).fetchall()
        return jsonify({"tests": rows})
        
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        title = payload.get("title")
        classroom_id = payload.get("classroom_id")
        chapter_id = payload.get("chapter_id")
        duration = payload.get("duration") or 30
        total_marks = payload.get("total_marks") or 100
        start_date = payload.get("start_date")
        end_date = payload.get("end_date")
        difficulty = payload.get("difficulty") or "medium"
        questions = payload.get("questions") or []
        
        if not title or not classroom_id:
            return jsonify({"error": "Missing title or classroom_id"}), 400
            
        with get_db() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tests (title, classroom_id, chapter_id, duration_minutes, total_marks, start_date, end_date, difficulty, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'scheduled', %s)
                RETURNING id
                """,
                (title, classroom_id, chapter_id if chapter_id else None, duration, total_marks, start_date, end_date, difficulty, now_iso())
            )
            test_id = cursor.fetchone()["id"]
            
            for q in questions:
                connection.execute(
                    """
                    INSERT INTO test_questions (test_id, type, question_text, options_json, correct_answer, marks)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (test_id, q.get("type"), q.get("question_text"), json.dumps(q.get("options")), q.get("correct_answer"), q.get("marks") or 1)
                )
        return jsonify({"ok": True, "test_id": test_id})
        
    elif request.method == 'DELETE':
        tid = request.args.get("id")
        if not tid:
            return jsonify({"error": "Missing test id"}), 400
        with get_db() as connection:
            connection.execute("DELETE FROM tests WHERE id = %s", (tid,))
        return jsonify({"ok": True})


@app.route('/api/admin/users', methods=['GET', 'PUT'])
@admin_required
def api_admin_users():
    if request.method == 'GET':
        with get_db() as connection:
            rows = connection.execute("SELECT id, name, email, role, institution, class_level, status, created_at FROM users").fetchall()
        return jsonify({"users": rows})
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        uid = payload.get("id")
        name = payload.get("name")
        role = payload.get("role")
        status = payload.get("status")
        
        if not uid:
            return jsonify({"error": "Missing user id"}), 400
            
        with get_db() as connection:
            target_user = connection.execute("SELECT role FROM users WHERE id = %s", (uid,)).fetchone()
            if not target_user:
                return jsonify({"error": "User not found"}), 404
            if target_user["role"] == "admin":
                return jsonify({"error": "Cannot promote, demote, or suspend administrator accounts"}), 403

            connection.execute(
                "UPDATE users SET name = %s, role = %s, status = %s, updated_at = %s WHERE id = %s",
                (name, role, status, now_iso(), uid)
            )
        return jsonify({"ok": True})


@app.route('/api/theme_preference', methods=['GET', 'PUT'])
def api_theme_preference():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        with get_db() as connection:
            row = connection.execute("SELECT theme FROM theme_preferences WHERE user_id = %s", (user['id'],)).fetchone()
        return jsonify({"theme": row["theme"] if row else "system"})
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        theme = payload.get("theme") or "system"
        with get_db() as connection:
            existing = connection.execute("SELECT user_id FROM theme_preferences WHERE user_id = %s", (user['id'],)).fetchone()
            if existing:
                connection.execute("UPDATE theme_preferences SET theme = %s, updated_at = %s WHERE user_id = %s", (theme, now_iso(), user['id']))
            else:
                connection.execute("INSERT INTO theme_preferences (user_id, theme, updated_at) VALUES (%s, %s, %s)", (user['id'], theme, now_iso()))
        return jsonify({"ok": True})


@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def api_admin_analytics():
    with get_db() as connection:
        total_students = connection.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'").fetchone()["count"]
        total_teachers = connection.execute("SELECT COUNT(*) as count FROM users WHERE role = 'teacher'").fetchone()["count"]
        total_classes = connection.execute("SELECT COUNT(*) as count FROM classrooms").fetchone()["count"]
        total_labs = connection.execute("SELECT COUNT(*) as count FROM labs").fetchone()["count"]
        total_tests = connection.execute("SELECT COUNT(*) as count FROM tests").fetchone()["count"]
        
        logins = connection.execute("SELECT COUNT(*) as count FROM user_history WHERE event_type = 'login_success'").fetchone()["count"]
        signups = connection.execute("SELECT COUNT(*) as count FROM user_history WHERE event_type = 'signup_success'").fetchone()["count"]
        
        lab_usage = connection.execute(
            "SELECT event_type, COUNT(*) as count FROM user_history WHERE event_type IN ('reaction_success', 'titration_complete') GROUP BY event_type"
        ).fetchall()
        
        xp_dist = connection.execute(
            "SELECT u.name, sp.current_xp FROM users u JOIN student_profiles sp ON u.id = sp.user_id ORDER BY sp.current_xp DESC LIMIT 10"
        ).fetchall()
        
    return jsonify({
        "stats": {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_classes": total_classes,
            "total_labs": total_labs,
            "total_tests": total_tests,
            "active_users": total_students + total_teachers,
            "daily_logins": logins,
            "signups": signups
        },
        "lab_usage": lab_usage,
        "leaderboard": xp_dist
    })


@app.route('/api/chapters', methods=['GET'])
def api_chapters():
    with get_db() as connection:
        rows = connection.execute("SELECT * FROM chapters").fetchall()
    return jsonify({"chapters": rows})


@app.route('/api/labs_list', methods=['GET'])
def api_labs_list():
    with get_db() as connection:
        rows = connection.execute("SELECT * FROM labs").fetchall()
    return jsonify({"labs": rows})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
