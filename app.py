import os
import json
import glob
import re
from datetime import datetime, timezone
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

# ── Database connection pool ────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

def parse_mysql_url(url):
    """Parse mysql://user:password@host:port/database URL."""
    if not url.startswith("mysql://"):
        raise ValueError("Invalid MySQL URL format. Must start with mysql://")
    
    rem = url[8:]
    if "@" in rem:
        auth, host_port_db = rem.split("@", 1)
        if ":" in auth:
            user, password = auth.split(":", 1)
        else:
            user = auth
            password = ""
    else:
        user = "root"
        password = ""
        host_port_db = rem
        
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

if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    try:
        db_config = parse_mysql_url(DATABASE_URL)
    except Exception as e:
        raise RuntimeError(f"Error parsing DATABASE_URL: {e}")
else:
    db_config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", 3306)),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "chemlove")
    }

try:
    pool = MySQLConnectionPool(
        pool_name="chemlove_pool",
        pool_size=10,
        **db_config
    )
except Exception as e:
    print(f"[DATABASE] CRITICAL ERROR: Could not create MySQL pool: {e}")
    pool = None


class MySQLCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def __iter__(self):
        return iter(self.cursor)


class MySQLConnectionWrapper:
    def __init__(self, pool):
        self.pool = pool
        self.conn = None
        self.cursor = None

    def __enter__(self):
        if not self.pool:
            raise RuntimeError("Database connection pool is not initialized.")
        self.conn = self.pool.get_connection()
        self.cursor = self.conn.cursor(dictionary=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()

    def execute(self, query, params=None):
        self.cursor.execute(query, params or ())
        return MySQLCursorWrapper(self.cursor)


def get_db():
    """Return a wrapper around a pooled MySQL connection (used as a context manager)."""
    return MySQLConnectionWrapper(pool)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ── No-cache for server-rendered HTML ──────────────────────────────────────
@app.after_request
def no_cache_html(response):
    if 'text/html' in response.headers.get('Content-Type', ''):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


# ── Startup connectivity check ─────────────────────────────────────────────
def init_db():
    """Verify MySQL database is reachable. Tables are managed via schema.sql."""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1").fetchone()
        print("[DATABASE] MySQL connection verified successfully.")
    except Exception as e:
        print(f"[DATABASE] WARNING: Could not reach MySQL database: {e}")


init_db()


# ── Static content helpers ─────────────────────────────────────────────────
_CONTENT_DIR = os.path.join(os.path.dirname(__file__), 'content')


def load_json(path):
    """Load a JSON file relative to the content directory."""
    full_path = os.path.join(_CONTENT_DIR, path)
    if not os.path.exists(full_path):
        return None
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def all_chapters():
    """Return a list of all chapter metadata dicts, sorted by number."""
    chapters = []
    pattern = os.path.join(_CONTENT_DIR, 'chapters', 'chapter_*.json')
    for filepath in sorted(glob.glob(pattern)):
        filename = os.path.basename(filepath)
        m = re.match(r'chapter_(\d+)\.json', filename)
        if m:
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    chapters.append(json.load(f))
                except Exception:
                    pass
    return chapters


def get_chapter(chapter_id):
    return load_json(f'chapters/chapter_{chapter_id}.json')


def all_labs():
    return load_json('labs.json') or []


def all_badges():
    return load_json('badges.json') or []


def get_badge(badge_id):
    for b in all_badges():
        if b['id'] == badge_id:
            return b
    return None


def all_experiments():
    experiments = []
    exp_dir = os.path.join(_CONTENT_DIR, 'experiments')
    if os.path.exists(exp_dir):
        for filename in sorted(os.listdir(exp_dir)):
            if filename.endswith('.json'):
                with open(os.path.join(exp_dir, filename), 'r', encoding='utf-8') as f:
                    try:
                        experiments.append(json.load(f))
                    except Exception:
                        pass
    return experiments


def get_experiment(experiment_id):
    return load_json(f'experiments/{experiment_id}.json')


def all_quizzes():
    quizzes = []
    quiz_dir = os.path.join(_CONTENT_DIR, 'quizzes')
    if os.path.exists(quiz_dir):
        for filename in sorted(os.listdir(quiz_dir)):
            if filename.endswith('.json'):
                with open(os.path.join(quiz_dir, filename), 'r', encoding='utf-8') as f:
                    try:
                        quizzes.append(json.load(f))
                    except Exception:
                        pass
    return quizzes


def get_quiz(chapter_id):
    return load_json(f'quizzes/{chapter_id}.json')


# ── User helpers ───────────────────────────────────────────────────────────
def user_from_row(row):
    return {
        "id":          row["id"],
        "name":        row["name"],
        "email":       row["email"],
        "institution": row["institution"],
        "role":        row["role"],
        "status":      row.get("status", "active"),
        "classLevel":  row.get("class_level"),
        "createdAt":   str(row["created_at"]),
        "updatedAt":   str(row["updated_at"]),
    }


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
        if not row:
            return None
        if row.get("status") == 'suspended':
            session.pop("user_id", None)
            return None

        user_dict = user_from_row(row)

        if user_dict["role"] == "student":
            sp = conn.execute(
                "SELECT current_xp, level FROM student_profiles WHERE user_id = %s",
                (user_id,)
            ).fetchone()
            user_dict["current_xp"] = sp["current_xp"] if sp else 100
            user_dict["level"]      = sp["level"]      if sp else 1

    return user_dict


def add_history(user_id, event_type, event_data=None):
    """Record only meaningful events — not every click."""
    TRACKED_EVENTS = {
        'login_success', 'logout', 'signup_success',
        'assignment_submission', 'test_submitted',
        'badge_unlocked', 'contact_message_sent',
        'profile_updated',
    }
    if event_type not in TRACKED_EVENTS:
        return
    with get_db() as conn:
        conn.execute(
            "INSERT INTO user_history(user_id, event_type, event_data, created_at) VALUES (%s, %s, %s, NOW())",
            (user_id, event_type, event_data),
        )


# ── Role decorators ────────────────────────────────────────────────────────
def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if user['role'] != 'student':
            flash('Unauthorized access.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated


def teacher_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if user['role'] != 'teacher':
            flash('Unauthorized access. Teacher role required.', 'error')
            return redirect(url_for('profile_page'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if user['role'] != 'admin':
            flash('Unauthorized access. Admin role required.', 'error')
            return redirect(url_for('profile_page'))
        return f(*args, **kwargs)
    return decorated


def redirect_by_role(user):
    if user['role'] == 'student':
        return redirect(url_for('student_dashboard'))
    elif user['role'] == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('home'))


# ============================================================
# PUBLIC ROUTES
# ============================================================

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
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        subject = request.form.get('subject', '').strip()

        if not name or not email or not message:
            flash('Please fill in Name, Email, and Message fields.', 'error')
            return redirect(url_for('contact'))

        user = get_current_user()
        if user:
            add_history(user['id'], "contact_message_sent", f"subject={subject}")

        flash('Thank you for reaching out! We will get back to you shortly.', 'success')
        return redirect(url_for('contact'))

    return render_template('landing/contact.html', current_user=get_current_user())


# Redirect aliases
@app.route('/index.html')
def index_html_redirect():
    return redirect(url_for('home'))

@app.route('/login.html')
def login_html_redirect():
    return redirect(url_for('login'))

@app.route('/signup.html')
def signup_html_redirect():
    return redirect(url_for('signup'))


# ── Auth ───────────────────────────────────────────────────────────────────

@app.route('/auth')
def auth_page():
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
        name        = request.form.get('name', '').strip()
        email       = request.form.get('email', '').strip().lower()
        password    = request.form.get('password', '')
        institution = request.form.get('institution', '').strip()
        role        = request.form.get('role', '').strip()
        class_level = request.form.get('classLevel', '').strip()

        if not name or not email or not password or not institution or not role:
            flash('Please fill all required fields.', 'error')
            return redirect(url_for('signup'))

        if role == 'student' and not class_level:
            flash('Please select class level for student role.', 'error')
            return redirect(url_for('signup'))

        with get_db() as conn:
            existing = conn.execute("SELECT id FROM users WHERE email = %s", (email,)).fetchone()
            if existing:
                flash('Email already exists. Please login.', 'error')
                return redirect(url_for('signup'))

            cursor = conn.execute(
                """
                INSERT INTO users(name, email, password_hash, institution, role, class_level, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, 'active', NOW(), NOW())
                """,
                (name, email, generate_password_hash(password), institution, role,
                 class_level if role == 'student' else None),
            )
            user_id = cursor.lastrowid

            if role == 'student':
                conn.execute(
                    "INSERT INTO student_profiles(user_id, current_xp, level) VALUES (%s, 100, 1)",
                    (user_id,)
                )
            elif role == 'teacher':
                conn.execute(
                    "INSERT INTO teacher_profiles(user_id, department) VALUES (%s, 'Chemistry')",
                    (user_id,)
                )

            user_row = conn.execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()

        session['user_id'] = user_id
        add_history(user_id, "signup_success", f"role={role}")
        flash('Signup successful. Welcome!', 'success')
        return redirect_by_role(user_row)

    return render_template('landing/auth.html', active_form='signup')


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if user:
        return redirect_by_role(user)

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = %s", (email,)).fetchone()

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


# ── Profile ────────────────────────────────────────────────────────────────

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

    payload     = request.get_json(silent=True) or {}
    name        = (payload.get("name") or user["name"]).strip()
    institution = (payload.get("institution") or user["institution"]).strip()
    class_level = payload.get("classLevel") if user["role"] == "student" else None

    with get_db() as conn:
        conn.execute(
            "UPDATE users SET name = %s, institution = %s, class_level = %s, updated_at = NOW() WHERE id = %s",
            (name, institution, class_level, user["id"]),
        )
    add_history(user["id"], "profile_updated")
    return jsonify({"ok": True})


@app.route('/api/history')
def history_api():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    with get_db() as conn:
        rows = conn.execute(
            "SELECT event_type, event_data, created_at FROM user_history WHERE user_id = %s ORDER BY id DESC LIMIT 50",
            (user["id"],),
        ).fetchall()
    return jsonify({"history": [dict(r) for r in rows]})


@app.route('/dashboard')
def dashboard_page():
    user = get_current_user()
    if not user:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    return redirect_by_role(user)


# ============================================================
# STUDENT PORTAL
# ============================================================

@app.route('/student/dashboard')
@student_required
def student_dashboard():
    return render_template('student/dashboard.html', current_user=get_current_user(), active_tab='dashboard')


@app.route('/student/chapters')
@student_required
def student_chapters():
    chapters = all_chapters()
    return render_template('student/chapters.html', current_user=get_current_user(), chapters=chapters, active_tab='chapters')


@app.route('/student/chapter/<int:chapter_id>')
@student_required
def student_chapter_view(chapter_id):
    chapter_data = get_chapter(chapter_id)
    if not chapter_data:
        flash('Chapter content not found.', 'error')
        return redirect(url_for('student_chapters'))
    return render_template('student/chapter_view.html', current_user=get_current_user(), chapter_data=chapter_data, active_tab='chapters')


@app.route('/student/reactions')
@student_required
def student_reactions():
    return render_template('student/reactions.html', current_user=get_current_user(), active_tab='reactions')


@app.route('/student/experiments')
@student_required
def student_experiments():
    return render_template('student/experiments.html', current_user=get_current_user(), experiments=all_experiments(), active_tab='experiments')


@app.route('/student/experiment/<int:experiment_id>')
@student_required
def student_experiment_view(experiment_id):
    exp = get_experiment(experiment_id)
    if not exp:
        flash('Experiment content not found.', 'error')
        return redirect(url_for('student_experiments'))
    return render_template('student/experiment_view.html', current_user=get_current_user(), experiment=exp, active_tab='experiments')


@app.route('/student/quizzes')
@student_required
def student_quizzes():
    return render_template('student/quizzes.html', current_user=get_current_user(), quizzes=all_quizzes(), active_tab='quizzes')


@app.route('/student/quiz/<int:chapter_id>')
@student_required
def student_quiz_view(chapter_id):
    quiz_data = get_quiz(chapter_id)
    if not quiz_data:
        flash('Quiz not found.', 'error')
        return redirect(url_for('student_quizzes'))
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


# ============================================================
# TEACHER PORTAL
# ============================================================

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


# ============================================================
# ADMIN PORTAL
# ============================================================

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
# API — CLASSROOMS
# ============================================================

@app.route('/api/classrooms', methods=['GET', 'POST', 'DELETE'])
def api_classrooms():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        with get_db() as conn:
            if user['role'] == 'teacher':
                rows = conn.execute(
                    """
                    SELECT c.*, (SELECT COUNT(*) FROM enrollments WHERE classroom_id = c.id) AS student_count
                    FROM classrooms c WHERE c.teacher_id = %s
                    """,
                    (user['id'],)
                ).fetchall()
            elif user['role'] == 'admin':
                rows = conn.execute(
                    """
                    SELECT c.*, u.name AS teacher_name,
                           (SELECT COUNT(*) FROM enrollments WHERE classroom_id = c.id) AS student_count
                    FROM classrooms c LEFT JOIN users u ON c.teacher_id = u.id
                    """
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT c.*, u.name AS teacher_name
                    FROM classrooms c
                    JOIN enrollments e ON c.id = e.classroom_id
                    LEFT JOIN users u ON c.teacher_id = u.id
                    WHERE e.student_id = %s
                    """,
                    (user['id'],)
                ).fetchall()
        return jsonify({"classrooms": [dict(r) for r in rows]})

    elif request.method == 'POST':
        payload    = request.get_json(silent=True) or {}
        name       = payload.get("name")
        grade      = payload.get("grade")
        section    = payload.get("section")
        teacher_id = payload.get("teacher_id") or user['id']

        if not name or not grade:
            return jsonify({"error": "Missing name or grade"}), 400

        with get_db() as conn:
            conn.execute(
                "INSERT INTO classrooms(name, teacher_id, grade, section, created_at) VALUES (%s, %s, %s, %s, NOW())",
                (name, teacher_id, grade, section)
            )
        return jsonify({"ok": True})

    elif request.method == 'DELETE':
        cid = request.args.get("id")
        if not cid:
            return jsonify({"error": "Missing classroom id"}), 400
        with get_db() as conn:
            if user['role'] == 'teacher':
                conn.execute("DELETE FROM classrooms WHERE id = %s AND teacher_id = %s", (cid, user['id']))
            elif user['role'] == 'admin':
                conn.execute("DELETE FROM classrooms WHERE id = %s", (cid,))
            else:
                return jsonify({"error": "Forbidden"}), 403
        return jsonify({"ok": True})


# ============================================================
# API — STUDENTS / ENROLLMENTS
# ============================================================

@app.route('/api/students', methods=['GET', 'POST', 'DELETE'])
def api_students():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        classroom_id = request.args.get("classroom_id")
        student_id   = request.args.get("student_id")

        with get_db() as conn:
            if student_id:
                student = conn.execute(
                    """
                    SELECT u.id, u.name, u.email, u.institution, u.class_level,
                           sp.current_xp, sp.level
                    FROM users u
                    LEFT JOIN student_profiles sp ON u.id = sp.user_id
                    WHERE u.id = %s AND u.role = 'student'
                    """,
                    (student_id,)
                ).fetchone()
                if not student:
                    return jsonify({"error": "Student not found"}), 404

                history = conn.execute(
                    "SELECT event_type, event_data, created_at FROM user_history WHERE user_id = %s ORDER BY id DESC LIMIT 20",
                    (student_id,)
                ).fetchall()
                attempts = conn.execute(
                    "SELECT ta.*, t.title AS test_title FROM test_attempts ta JOIN tests t ON ta.test_id = t.id WHERE ta.student_id = %s",
                    (student_id,)
                ).fetchall()
                badges_rows = conn.execute(
                    "SELECT badge_id, unlocked_at FROM user_badges WHERE user_id = %s",
                    (student_id,)
                ).fetchall()
                submissions = conn.execute(
                    "SELECT s.*, a.title AS assignment_title FROM submissions s JOIN assignments a ON s.assignment_id = a.id WHERE s.student_id = %s",
                    (student_id,)
                ).fetchall()

                # Enrich badges with static metadata
                badges = []
                for b in badges_rows:
                    meta = get_badge(b["badge_id"])
                    if meta:
                        badges.append({**meta, "unlocked_at": str(b["unlocked_at"])})

                return jsonify({
                    "student":     dict(student),
                    "history":     [dict(r) for r in history],
                    "attempts":    [dict(r) for r in attempts],
                    "badges":      badges,
                    "submissions": [dict(r) for r in submissions],
                })

            elif classroom_id:
                rows = conn.execute(
                    """
                    SELECT u.id, u.name, u.email, u.institution, u.class_level, u.status,
                           sp.current_xp, sp.level
                    FROM users u
                    JOIN enrollments e ON u.id = e.student_id
                    LEFT JOIN student_profiles sp ON u.id = sp.user_id
                    WHERE e.classroom_id = %s
                    """,
                    (classroom_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT u.id, u.name, u.email, u.institution, u.class_level, u.status,
                           sp.current_xp, sp.level
                    FROM users u
                    LEFT JOIN student_profiles sp ON u.id = sp.user_id
                    WHERE u.role = 'student'
                    """
                ).fetchall()

        return jsonify({"students": [dict(r) for r in rows]})

    elif request.method == 'POST':
        payload      = request.get_json(silent=True) or {}
        classroom_id = payload.get("classroom_id")
        student_id   = payload.get("student_id")

        if not classroom_id or not student_id:
            return jsonify({"error": "Missing parameters"}), 400

        with get_db() as conn:
            conn.execute(
                "INSERT IGNORE INTO enrollments(classroom_id, student_id, enrolled_at) VALUES (%s, %s, NOW())",
                (classroom_id, student_id)
            )
        return jsonify({"ok": True})

    elif request.method == 'DELETE':
        classroom_id = request.args.get("classroom_id")
        student_id   = request.args.get("student_id")

        if not classroom_id or not student_id:
            return jsonify({"error": "Missing parameters"}), 400

        with get_db() as conn:
            conn.execute(
                "DELETE FROM enrollments WHERE classroom_id = %s AND student_id = %s",
                (classroom_id, student_id)
            )
        return jsonify({"ok": True})


# ============================================================
# API — ASSIGNMENTS
# ============================================================

@app.route('/api/assignments', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_assignments():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        classroom_id = request.args.get("classroom_id")
        with get_db() as conn:
            if classroom_id:
                rows = conn.execute(
                    """
                    SELECT a.*,
                           c.name AS classroom_name,
                           (SELECT COUNT(*) FROM submissions WHERE assignment_id = a.id) AS submission_count
                    FROM assignments a
                    JOIN classrooms c ON a.classroom_id = c.id
                    WHERE a.classroom_id = %s
                    """,
                    (classroom_id,)
                ).fetchall()
            elif user['role'] == 'teacher':
                rows = conn.execute(
                    """
                    SELECT a.*, c.name AS classroom_name,
                           (SELECT COUNT(*) FROM submissions WHERE assignment_id = a.id) AS submission_count
                    FROM assignments a
                    JOIN classrooms c ON a.classroom_id = c.id
                    WHERE c.teacher_id = %s
                    """,
                    (user['id'],)
                ).fetchall()
            elif user['role'] == 'admin':
                rows = conn.execute(
                    """
                    SELECT a.*, c.name AS classroom_name,
                           (SELECT COUNT(*) FROM submissions WHERE assignment_id = a.id) AS submission_count
                    FROM assignments a
                    JOIN classrooms c ON a.classroom_id = c.id
                    """
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT a.*, c.name AS classroom_name,
                           s.status AS submission_status, s.marks_obtained, s.feedback
                    FROM assignments a
                    JOIN classrooms c ON a.classroom_id = c.id
                    JOIN enrollments e ON c.id = e.classroom_id
                    LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = %s
                    WHERE e.student_id = %s AND a.status = 'published'
                    """,
                    (user['id'], user['id'])
                ).fetchall()

        # Enrich chapter/lab names from static content
        chapters = {c['id']: c for c in all_chapters()}
        labs     = {l['id']: l for l in all_labs()}
        result   = []
        for r in rows:
            d = dict(r)
            ch = chapters.get(d.get('chapter_id'))
            lb = labs.get(d.get('lab_id'))
            d['chapter_title'] = ch['title'] if ch else None
            d['lab_name']      = lb['title'] if lb else None
            result.append(d)

        return jsonify({"assignments": result})

    elif request.method == 'POST':
        payload      = request.get_json(silent=True) or {}
        title        = payload.get("title")
        classroom_id = payload.get("classroom_id")

        if not title or not classroom_id:
            return jsonify({"error": "Missing title or classroom_id"}), 400

        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO assignments(title, description, classroom_id, chapter_id, lab_id, marks, due_date, instructions, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    title,
                    payload.get("description"),
                    classroom_id,
                    payload.get("chapter_id") or None,
                    payload.get("lab_id")     or None,
                    payload.get("marks") or 100,
                    payload.get("due_date"),
                    payload.get("instructions"),
                    payload.get("status") or "draft",
                )
            )
        return jsonify({"ok": True})

    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        aid     = payload.get("id")
        status  = payload.get("status")

        if not aid or not status:
            return jsonify({"error": "Missing parameters"}), 400

        with get_db() as conn:
            conn.execute("UPDATE assignments SET status = %s WHERE id = %s", (status, aid))
        return jsonify({"ok": True})

    elif request.method == 'DELETE':
        aid = request.args.get("id")
        if not aid:
            return jsonify({"error": "Missing assignment id"}), 400
        with get_db() as conn:
            conn.execute("DELETE FROM assignments WHERE id = %s", (aid,))
        return jsonify({"ok": True})


# ============================================================
# API — SUBMISSIONS
# ============================================================

@app.route('/api/submissions', methods=['GET', 'POST', 'PUT'])
def api_submissions():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        assignment_id = request.args.get("assignment_id")
        with get_db() as conn:
            if user['role'] in ('teacher', 'admin'):
                if assignment_id:
                    rows = conn.execute(
                        "SELECT s.*, u.name AS student_name, u.email AS student_email FROM submissions s JOIN users u ON s.student_id = u.id WHERE s.assignment_id = %s",
                        (assignment_id,)
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT s.*, u.name AS student_name, a.title AS assignment_title FROM submissions s JOIN users u ON s.student_id = u.id JOIN assignments a ON s.assignment_id = a.id"
                    ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT s.*, a.title AS assignment_title FROM submissions s JOIN assignments a ON s.assignment_id = a.id WHERE s.student_id = %s",
                    (user['id'],)
                ).fetchall()
        return jsonify({"submissions": [dict(r) for r in rows]})

    elif request.method == 'POST':
        payload       = request.get_json(silent=True) or {}
        assignment_id = payload.get("assignment_id")
        file_data     = payload.get("file_data") or ""

        if not assignment_id:
            return jsonify({"error": "Missing assignment_id"}), 400

        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO submissions(assignment_id, student_id, submitted_at, file_data, status)
                VALUES (%s, %s, NOW(), %s, 'pending')
                ON DUPLICATE KEY UPDATE file_data = %s, submitted_at = NOW(), status = 'pending'
                """,
                (assignment_id, user['id'], file_data, file_data)
            )
        add_history(user['id'], "assignment_submission", f"assignment_id={assignment_id}")
        return jsonify({"ok": True})

    elif request.method == 'PUT':
        payload        = request.get_json(silent=True) or {}
        sid            = payload.get("id")
        marks_obtained = payload.get("marks_obtained")
        feedback       = payload.get("feedback")
        status         = payload.get("status") or "graded"

        if not sid or marks_obtained is None:
            return jsonify({"error": "Missing parameters"}), 400

        with get_db() as conn:
            conn.execute(
                "UPDATE submissions SET marks_obtained = %s, feedback = %s, status = %s WHERE id = %s",
                (marks_obtained, feedback, status, sid)
            )
            if status == 'approved':
                row = conn.execute("SELECT student_id FROM submissions WHERE id = %s", (sid,)).fetchone()
                if row:
                    conn.execute(
                        "UPDATE student_profiles SET current_xp = current_xp + 50 WHERE user_id = %s",
                        (row["student_id"],)
                    )
                    add_history(row["student_id"], "badge_unlocked", "XP Awarded for Assignment Approval")

        return jsonify({"ok": True})


# ============================================================
# API — TESTS
# ============================================================

@app.route('/api/tests', methods=['GET', 'POST', 'DELETE'])
def api_tests():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        test_id = request.args.get("id")
        with get_db() as conn:
            if test_id:
                test     = conn.execute("SELECT * FROM tests WHERE id = %s", (test_id,)).fetchone()
                attempts = conn.execute(
                    "SELECT ta.*, u.name AS student_name FROM test_attempts ta JOIN users u ON ta.student_id = u.id WHERE ta.test_id = %s",
                    (test_id,)
                ).fetchall()
                # Questions come from the JSON file
                quiz_data = get_quiz(test.get("chapter_id")) if test else None
                return jsonify({
                    "test":      dict(test) if test else None,
                    "questions": quiz_data.get("questions", []) if quiz_data else [],
                    "attempts":  [dict(r) for r in attempts],
                })

            if user['role'] == 'teacher':
                rows = conn.execute(
                    "SELECT t.*, c.name AS classroom_name FROM tests t JOIN classrooms c ON t.classroom_id = c.id WHERE c.teacher_id = %s",
                    (user['id'],)
                ).fetchall()
            elif user['role'] == 'admin':
                rows = conn.execute(
                    "SELECT t.*, c.name AS classroom_name FROM tests t JOIN classrooms c ON t.classroom_id = c.id"
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT t.*, c.name AS classroom_name, ta.score, ta.status AS attempt_status
                    FROM tests t
                    JOIN classrooms c ON t.classroom_id = c.id
                    JOIN enrollments e ON c.id = e.classroom_id
                    LEFT JOIN test_attempts ta ON t.id = ta.test_id AND ta.student_id = %s
                    WHERE e.student_id = %s
                    """,
                    (user['id'], user['id'])
                ).fetchall()

        return jsonify({"tests": [dict(r) for r in rows]})

    elif request.method == 'POST':
        payload      = request.get_json(silent=True) or {}
        title        = payload.get("title")
        classroom_id = payload.get("classroom_id")

        if not title or not classroom_id:
            return jsonify({"error": "Missing title or classroom_id"}), 400

        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tests(title, classroom_id, chapter_id, quiz_content_id, duration_minutes,
                                  total_marks, start_date, end_date, difficulty, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'scheduled', NOW())
                """,
                (
                    title,
                    classroom_id,
                    payload.get("chapter_id")    or None,
                    payload.get("chapter_id")    or None,  # quiz_content_id mirrors chapter_id
                    payload.get("duration") or 30,
                    payload.get("total_marks") or 100,
                    payload.get("start_date"),
                    payload.get("end_date"),
                    payload.get("difficulty") or "medium",
                )
            )
            test_id = cursor.lastrowid
        return jsonify({"ok": True, "test_id": test_id})

    elif request.method == 'DELETE':
        tid = request.args.get("id")
        if not tid:
            return jsonify({"error": "Missing test id"}), 400
        with get_db() as conn:
            conn.execute("DELETE FROM tests WHERE id = %s", (tid,))
        return jsonify({"ok": True})


# ============================================================
# API — ADMIN
# ============================================================

@app.route('/api/admin/users', methods=['GET', 'PUT'])
@admin_required
def api_admin_users():
    if request.method == 'GET':
        with get_db() as conn:
            rows = conn.execute(
                "SELECT id, name, email, role, institution, class_level, status, created_at FROM users ORDER BY created_at DESC"
            ).fetchall()
        return jsonify({"users": [dict(r) for r in rows]})

    payload = request.get_json(silent=True) or {}
    uid     = payload.get("id")
    name    = payload.get("name")
    role    = payload.get("role")
    status  = payload.get("status")

    if not uid:
        return jsonify({"error": "Missing user id"}), 400

    with get_db() as conn:
        target = conn.execute("SELECT role FROM users WHERE id = %s", (uid,)).fetchone()
        if not target:
            return jsonify({"error": "User not found"}), 404
        if target["role"] == "admin":
            return jsonify({"error": "Cannot modify administrator accounts"}), 403

        conn.execute(
            "UPDATE users SET name = %s, role = %s, status = %s, updated_at = NOW() WHERE id = %s",
            (name, role, status, uid)
        )
    return jsonify({"ok": True})


@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def api_admin_analytics():
    with get_db() as conn:
        total_students = conn.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'student'").fetchone()["count"]
        total_teachers = conn.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'teacher'").fetchone()["count"]
        total_classes  = conn.execute("SELECT COUNT(*) AS count FROM classrooms").fetchone()["count"]
        total_tests    = conn.execute("SELECT COUNT(*) AS count FROM tests").fetchone()["count"]

        logins  = conn.execute("SELECT COUNT(*) AS count FROM user_history WHERE event_type = 'login_success'").fetchone()["count"]
        signups = conn.execute("SELECT COUNT(*) AS count FROM user_history WHERE event_type = 'signup_success'").fetchone()["count"]

        # Live leaderboard — no separate table needed
        leaderboard = conn.execute(
            """
            SELECT u.name, sp.current_xp
            FROM student_profiles sp
            JOIN users u ON sp.user_id = u.id
            ORDER BY sp.current_xp DESC
            LIMIT 10
            """
        ).fetchall()

    return jsonify({
        "stats": {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_classes":  total_classes,
            "total_labs":     len(all_labs()),
            "total_tests":    total_tests,
            "active_users":   total_students + total_teachers,
            "daily_logins":   logins,
            "signups":        signups,
        },
        "leaderboard": [dict(r) for r in leaderboard],
    })


# ============================================================
# API — STATIC CONTENT (served from JSON files)
# ============================================================

@app.route('/api/chapters')
def api_chapters():
    return jsonify({"chapters": all_chapters()})


@app.route('/api/labs_list')
def api_labs_list():
    return jsonify({"labs": all_labs()})


@app.route('/api/badges')
def api_badges():
    return jsonify({"badges": all_badges()})


@app.route('/api/quizzes')
def api_quizzes():
    return jsonify({"quizzes": all_quizzes()})


# ============================================================
# API — USER BADGES
# ============================================================

@app.route('/api/user_badges', methods=['GET', 'POST'])
def api_user_badges():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        target_id = request.args.get("user_id") or user["id"]
        with get_db() as conn:
            rows = conn.execute(
                "SELECT badge_id, unlocked_at FROM user_badges WHERE user_id = %s ORDER BY unlocked_at DESC",
                (target_id,)
            ).fetchall()
        badges = []
        for r in rows:
            meta = get_badge(r["badge_id"])
            if meta:
                badges.append({**meta, "unlocked_at": str(r["unlocked_at"])})
        return jsonify({"badges": badges})

    # POST — award a badge
    payload  = request.get_json(silent=True) or {}
    badge_id = payload.get("badge_id")
    user_id  = payload.get("user_id") or user["id"]

    if not badge_id:
        return jsonify({"error": "Missing badge_id"}), 400

    badge = get_badge(badge_id)
    if not badge:
        return jsonify({"error": "Badge not found in content/badges.json"}), 404

    with get_db() as conn:
        conn.execute(
            "INSERT IGNORE INTO user_badges(user_id, badge_id, unlocked_at) VALUES (%s, %s, NOW())",
            (user_id, badge_id)
        )
        # Award XP from badge definition
        xp = badge.get("xp_reward", 0)
        if xp > 0:
            conn.execute(
                "UPDATE student_profiles SET current_xp = current_xp + %s WHERE user_id = %s",
                (xp, user_id)
            )
    add_history(user_id, "badge_unlocked", f"badge_id={badge_id}")
    return jsonify({"ok": True})


# ============================================================
# API — ANNOUNCEMENTS
# ============================================================

@app.route('/api/announcements', methods=['GET', 'POST', 'DELETE'])
def api_announcements():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        classroom_id = request.args.get("classroom_id")
        with get_db() as conn:
            if classroom_id:
                rows = conn.execute(
                    "SELECT a.*, u.name AS author_name FROM announcements a JOIN users u ON a.author_id = u.id WHERE a.classroom_id = %s ORDER BY a.is_pinned DESC, a.created_at DESC",
                    (classroom_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT a.*, u.name AS author_name FROM announcements a JOIN users u ON a.author_id = u.id ORDER BY a.is_pinned DESC, a.created_at DESC LIMIT 50"
                ).fetchall()
        return jsonify({"announcements": [dict(r) for r in rows]})

    elif request.method == 'POST':
        if user['role'] not in ('teacher', 'admin'):
            return jsonify({"error": "Forbidden"}), 403

        payload      = request.get_json(silent=True) or {}
        title        = payload.get("title")
        content      = payload.get("content")
        classroom_id = payload.get("classroom_id")
        target_role  = payload.get("target_role")
        is_pinned    = payload.get("is_pinned", False)

        if not title or not content:
            return jsonify({"error": "Missing title or content"}), 400

        with get_db() as conn:
            conn.execute(
                "INSERT INTO announcements(title, content, author_id, classroom_id, target_role, is_pinned, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                (title, content, user["id"], classroom_id, target_role, is_pinned)
            )
        return jsonify({"ok": True})

    elif request.method == 'DELETE':
        aid = request.args.get("id")
        if not aid:
            return jsonify({"error": "Missing announcement id"}), 400
        with get_db() as conn:
            conn.execute("DELETE FROM announcements WHERE id = %s", (aid,))
        return jsonify({"ok": True})


# ============================================================
# API — ATTENDANCE
# ============================================================

@app.route('/api/attendance', methods=['GET', 'POST'])
def api_attendance():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        classroom_id = request.args.get("classroom_id")
        date         = request.args.get("date")
        if not classroom_id:
            return jsonify({"error": "Missing classroom_id"}), 400

        with get_db() as conn:
            if date:
                rows = conn.execute(
                    "SELECT a.*, u.name AS student_name FROM attendance a JOIN users u ON a.student_id = u.id WHERE a.classroom_id = %s AND a.date = %s",
                    (classroom_id, date)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT a.*, u.name AS student_name FROM attendance a JOIN users u ON a.student_id = u.id WHERE a.classroom_id = %s ORDER BY a.date DESC",
                    (classroom_id,)
                ).fetchall()
        return jsonify({"attendance": [dict(r) for r in rows]})

    elif request.method == 'POST':
        if user['role'] not in ('teacher', 'admin'):
            return jsonify({"error": "Forbidden"}), 403

        payload  = request.get_json(silent=True) or {}
        records  = payload.get("records", [])  # list of {classroom_id, student_id, date, status}

        if not records:
            return jsonify({"error": "No records provided"}), 400

        with get_db() as conn:
            for rec in records:
                conn.execute(
                    """
                    INSERT INTO attendance(classroom_id, student_id, date, status)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = %s
                    """,
                    (rec.get("classroom_id"), rec.get("student_id"), rec.get("date"), rec.get("status"), rec.get("status"))
                )
        return jsonify({"ok": True})


# ============================================================
# API — LEADERBOARD (live query, no table)
# ============================================================

@app.route('/api/leaderboard')
def api_leaderboard():
    limit = min(int(request.args.get("limit", 100)), 200)
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT u.name, u.institution, sp.current_xp, sp.level,
                   RANK() OVER (ORDER BY sp.current_xp DESC) AS rank
            FROM student_profiles sp
            JOIN users u ON sp.user_id = u.id
            ORDER BY sp.current_xp DESC
            LIMIT %s
            """,
            (limit,)
        ).fetchall()
    return jsonify({"leaderboard": [dict(r) for r in rows]})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
