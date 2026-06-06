import os
import json
import glob
import re
from datetime import datetime, timezone, date
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
def safe_json_loads(val):
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return val
    try:
        return json.loads(val)
    except Exception:
        return val


def parse_chapter_json_fields(ch):
    if not ch:
        return None
    ch = dict(ch)
    json_fields = [
        'learning_objectives', 'key_points', 'important_laws', 'formulas',
        'constants', 'important_reactions', 'notes', 'real_life_applications',
        'virtual_labs', 'practice_questions', 'common_mistakes',
        'chapter_weightage', 'next_chapter'
    ]
    for field in json_fields:
        if field in ch:
            ch[field] = safe_json_loads(ch[field])
    return ch


def parse_experiment_json_fields(exp):
    if not exp:
        return None
    exp = dict(exp)
    json_fields = ['apparatus', 'procedure', 'observations', 'viva_questions']
    for field in json_fields:
        if field in exp:
            exp[field] = safe_json_loads(exp[field])
    return exp


def parse_reaction_json_fields(rxn):
    if not rxn:
        return None
    rxn = dict(rxn)
    json_fields = ['reactants', 'products', 'mechanism']
    for field in json_fields:
        if field in rxn:
            rxn[field] = safe_json_loads(rxn[field])
    return rxn


def all_chapters():
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM chapters ORDER BY chapter_number ASC").fetchall()
        return [parse_chapter_json_fields(row) for row in rows]
    except Exception as e:
        print(f"Error fetching chapters: {e}")
        return []


def get_chapter(chapter_id):
    try:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM chapters WHERE id = %s", (chapter_id,)).fetchone()
        return parse_chapter_json_fields(row) if row else None
    except Exception as e:
        print(f"Error fetching chapter {chapter_id}: {e}")
        return None


def all_labs():
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM labs ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Error fetching labs: {e}")
        return []


def all_badges():
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM badges ORDER BY id ASC").fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Error fetching badges: {e}")
        return []


def get_badge(badge_id):
    try:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM badges WHERE id = %s", (badge_id,)).fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error fetching badge {badge_id}: {e}")
        return None


def all_experiments():
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM experiments ORDER BY id ASC").fetchall()
        return [parse_experiment_json_fields(row) for row in rows]
    except Exception as e:
        print(f"Error fetching experiments: {e}")
        return []


def get_experiment(experiment_id):
    try:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM experiments WHERE id = %s", (experiment_id,)).fetchone()
        return parse_experiment_json_fields(row) if row else None
    except Exception as e:
        print(f"Error fetching experiment {experiment_id}: {e}")
        return None


def all_quizzes():
    try:
        with get_db() as conn:
            quiz_rows = conn.execute("SELECT * FROM quizzes ORDER BY id ASC").fetchall()
        quizzes = []
        for q_row in quiz_rows:
            q_dict = dict(q_row)
            with get_db() as conn:
                questions = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = %s ORDER BY id ASC", (q_dict['id'],)).fetchall()
            enriched_questions = []
            for ques in questions:
                q_info = dict(ques)
                opts = [q_info['option_a'], q_info['option_b'], q_info['option_c'], q_info['option_d']]
                q_info['options'] = [o for o in opts if o]
                letter_idx = ord(q_info['correct_answer'].upper()) - 65
                if 0 <= letter_idx < len(q_info['options']):
                    q_info['answer'] = q_info['options'][letter_idx]
                else:
                    q_info['answer'] = q_info['option_a']
                enriched_questions.append(q_info)
            q_dict['questions'] = enriched_questions
            quizzes.append(q_dict)
        return quizzes
    except Exception as e:
        print(f"Error fetching quizzes: {e}")
        return []


def get_quiz(chapter_id):
    try:
        with get_db() as conn:
            quiz_row = conn.execute("SELECT * FROM quizzes WHERE chapter_id = %s", (chapter_id,)).fetchone()
        if not quiz_row:
            return None
        q_dict = dict(quiz_row)
        with get_db() as conn:
            questions = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = %s ORDER BY id ASC", (q_dict['id'],)).fetchall()
        
        enriched_questions = []
        for ques in questions:
            q_info = dict(ques)
            opts = [q_info['option_a'], q_info['option_b'], q_info['option_c'], q_info['option_d']]
            q_info['options'] = [o for o in opts if o]
            letter_idx = ord(q_info['correct_answer'].upper()) - 65
            if 0 <= letter_idx < len(q_info['options']):
                q_info['answer'] = q_info['options'][letter_idx]
            else:
                q_info['answer'] = q_info['option_a']
            enriched_questions.append(q_info)
        
        with get_db() as conn:
            ch_row = conn.execute("SELECT title FROM chapters WHERE id = %s", (chapter_id,)).fetchone()
        q_dict['chapter'] = ch_row['title'] if ch_row else "Chemistry"
        q_dict['questions'] = enriched_questions
        return q_dict
    except Exception as e:
        print(f"Error fetching quiz for chapter {chapter_id}: {e}")
        return None



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
            session.pop("impersonator_user_id", None)
            return None

        user_dict = user_from_row(row)

        if user_dict["role"] == "student":
            sp = conn.execute(
                "SELECT current_xp, level FROM student_profiles WHERE user_id = %s",
                (user_id,)
            ).fetchone()
            user_dict["current_xp"] = sp["current_xp"] if sp else 100
            user_dict["level"]      = sp["level"]      if sp else 1

        # Check for active impersonation session
        impersonator_id = session.get("impersonator_user_id")
        if impersonator_id:
            imp_row = conn.execute("SELECT name, role FROM users WHERE id = %s", (impersonator_id,)).fetchone()
            if imp_row:
                user_dict["is_impersonating"] = True
                user_dict["impersonator_name"] = imp_row["name"]
                user_dict["impersonator_role"] = imp_row["role"]

    return user_dict


def add_history(user_id, event_type, event_data=None):
    """Record only meaningful events — not every click."""
    TRACKED_EVENTS = {
        'login_success', 'logout', 'signup_success',
        'assignment_submission', 'test_submitted',
        'badge_unlocked', 'contact_message_sent',
        'profile_updated',
        'quiz_passed', 'titration_complete', 'reaction_success',
    }
    if event_type not in TRACKED_EVENTS:
        return
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO user_history(user_id, event_type, event_data, created_at) VALUES (%s, %s, %s, NOW())",
                (user_id, event_type, event_data),
            )
    except Exception as e:
        print(f"Error writing user history for user_id {user_id}: {e}")


# ── Audit Logging Helper ──────────────────────────────────────────────────
def log_audit(action, details=None):
    """Log system actions to audit_logs."""
    user = get_current_user()
    user_id = user["id"] if user else session.get("user_id")
    if not user_id:
        # Fallback to system / unauthenticated action
        return
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO audit_logs (user_id, action, details) VALUES (%s, %s, %s)",
                (user_id, action, details)
            )
    except Exception as e:
        print(f"Error logging audit: {e}")


# ── Role & Permission check helpers ────────────────────────────────────────
def check_permission(permission_key):
    user = get_current_user()
    if not user:
        return False
    # Combined Admin has unrestricted access to everything
    if user['role'] == 'admin':
        return True
    return False

app.jinja_env.globals.update(check_permission=check_permission)


# ── Role decorators ────────────────────────────────────────────────────────


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if user['role'] not in ('student', 'admin'):
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
        if user['role'] not in ('teacher', 'admin'):
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
    if user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif user['role'] == 'student':
        return redirect(url_for('student_dashboard'))
    elif user['role'] == 'teacher':
        return redirect(url_for('teacher_dashboard'))
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
    session.pop('impersonator_user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/admin/impersonate/<int:target_uid>')
@admin_required
def admin_impersonate(target_uid):
    with get_db() as conn:
        target_user = conn.execute("SELECT * FROM users WHERE id = %s", (target_uid,)).fetchone()
    
    if not target_user:
        flash("Target user not found.", "error")
        return redirect(url_for('admin_dashboard'))
    
    if target_user["role"] == "admin":
        flash("Cannot impersonate another Admin account.", "error")
        return redirect(url_for('admin_dashboard'))

    admin_id = session.get("user_id")
    session["impersonator_user_id"] = admin_id
    session["user_id"] = target_uid

    log_audit("impersonate_user", f"Admin impersonating {target_user['name']} (ID: {target_uid})")
    flash(f"Now impersonating {target_user['name']} ({target_user['role']})", "success")
    return redirect_by_role(target_user)


@app.route('/auth/stop-impersonation')
def stop_impersonation():
    impersonator_id = session.get("impersonator_user_id")
    if not impersonator_id:
        flash("No active impersonation session found.", "error")
        return redirect(url_for('home'))

    session["user_id"] = impersonator_id
    session.pop("impersonator_user_id", None)

    log_audit("stop_impersonate_user", "Stopped impersonation")
    flash("Stopped impersonation. Returned to Admin.", "success")
    return redirect(url_for('admin_dashboard'))


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
    user = get_current_user()
    class_level = request.args.get('class_level', user.get('classLevel') or '11')
    with get_db() as conn:
        if class_level == 'all':
            rows = conn.execute("SELECT * FROM chapters ORDER BY class_level ASC, chapter_number ASC").fetchall()
        else:
            rows = conn.execute("SELECT * FROM chapters WHERE class_level = %s ORDER BY chapter_number ASC", (class_level,)).fetchall()
    chapters = [parse_chapter_json_fields(row) for row in rows]
    return render_template('student/chapters.html', current_user=user, chapters=chapters, selected_class=class_level, active_tab='chapters')


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
    user = get_current_user()
    class_level = request.args.get('class_level', user.get('classLevel') or '11')
    return render_template('student/reactions.html', current_user=user, selected_class=class_level, active_tab='reactions')


@app.route('/student/experiments')
@student_required
def student_experiments():
    user = get_current_user()
    class_level = request.args.get('class_level', user.get('classLevel') or '11')
    with get_db() as conn:
        if class_level == 'all':
            rows = conn.execute("SELECT e.*, c.class_level FROM experiments e LEFT JOIN chapters c ON e.chapter_id = c.id ORDER BY e.id ASC").fetchall()
        else:
            rows = conn.execute("""
                SELECT e.*, c.class_level FROM experiments e
                LEFT JOIN chapters c ON e.chapter_id = c.id
                WHERE c.class_level = %s OR (c.class_level IS NULL AND %s = '11')
                ORDER BY e.id ASC
            """, (class_level, class_level)).fetchall()
    experiments = [parse_experiment_json_fields(row) for row in rows]
    return render_template('student/experiments.html', current_user=user, experiments=experiments, selected_class=class_level, active_tab='experiments')


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
    user = get_current_user()
    class_level = request.args.get('class_level', user.get('classLevel') or '11')
    quizzes = []
    with get_db() as conn:
        if class_level == 'all':
            quiz_rows = conn.execute("SELECT q.*, c.class_level FROM quizzes q LEFT JOIN chapters c ON q.chapter_id = c.id ORDER BY q.id ASC").fetchall()
        else:
            quiz_rows = conn.execute("""
                SELECT q.*, c.class_level FROM quizzes q
                LEFT JOIN chapters c ON q.chapter_id = c.id
                WHERE c.class_level = %s
                ORDER BY q.id ASC
            """, (class_level,)).fetchall()
    for q_row in quiz_rows:
        q_dict = dict(q_row)
        with get_db() as conn:
            questions = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = %s ORDER BY id ASC", (q_dict['id'],)).fetchall()
        enriched_questions = []
        for ques in questions:
            q_info = dict(ques)
            opts = [q_info['option_a'], q_info['option_b'], q_info['option_c'], q_info['option_d']]
            q_info['options'] = [o for o in opts if o]
            letter_idx = ord(q_info['correct_answer'].upper()) - 65
            if 0 <= letter_idx < len(q_info['options']):
                q_info['answer'] = q_info['options'][letter_idx]
            else:
                q_info['answer'] = q_info['option_a']
            enriched_questions.append(q_info)
        q_dict['questions'] = enriched_questions
        quizzes.append(q_dict)
    return render_template('student/quizzes.html', current_user=user, quizzes=quizzes, selected_class=class_level, active_tab='quizzes')


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


@app.route('/teacher/content')
@teacher_required
def teacher_content():
    return render_template('admin/content.html', current_user=get_current_user(), active_tab='content')


# ============================================================
# ADMIN PORTAL & MONITORING
# ============================================================

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = {}
    try:
        with get_db() as conn:
            stats['total_users'] = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
            stats['total_students'] = conn.execute("SELECT COUNT(*) as c FROM users WHERE role = 'student'").fetchone()['c']
            stats['total_teachers'] = conn.execute("SELECT COUNT(*) as c FROM users WHERE role = 'teacher'").fetchone()['c']
            stats['total_courses'] = conn.execute("SELECT COUNT(*) as c FROM courses").fetchone()['c']
            stats['total_chapters'] = conn.execute("SELECT COUNT(*) as c FROM chapters").fetchone()['c']
            stats['total_certificates'] = conn.execute("SELECT COUNT(*) as c FROM certificates").fetchone()['c']
            
            # DAU / MAU: count unique user_id in user_history in last 1 day vs 30 days
            dau_row = conn.execute("SELECT COUNT(DISTINCT user_id) as c FROM user_history WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)").fetchone()
            stats['dau'] = dau_row['c'] if dau_row['c'] else 1
            
            mau_row = conn.execute("SELECT COUNT(DISTINCT user_id) as c FROM user_history WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)").fetchone()
            stats['mau'] = mau_row['c'] if mau_row['c'] else 1
            
            # DB Size
            db_size_row = conn.execute("""
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size 
                FROM information_schema.TABLES 
                WHERE table_schema = %s
            """, (db_config.get('database'),)).fetchone()
            stats['db_size'] = db_size_row['size'] if db_size_row and db_size_row['size'] else 1.24
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        stats = {
            'total_users': 0, 'total_students': 0, 'total_teachers': 0,
            'total_courses': 0, 'total_chapters': 0, 'total_certificates': 0,
            'dau': 1, 'mau': 1, 'db_size': 1.24
        }

    audit_logs = []
    try:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT a.*, u.name as operator_name, u.role
                FROM audit_logs a
                LEFT JOIN users u ON a.user_id = u.id
                ORDER BY a.created_at DESC
                LIMIT 50
            """).fetchall()
            for r in rows:
                audit_logs.append(dict(r))
    except Exception as e:
        print(f"Error getting audit logs: {e}")

    chart_data = []
    try:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT DATE(created_at) as d, COUNT(*) as c 
                FROM users 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY d ASC
            """).fetchall()
            for r in rows:
                chart_data.append({
                    'date': r['d'].strftime('%b %d') if hasattr(r['d'], 'strftime') else str(r['d']),
                    'count': r['c']
                })
    except Exception as e:
        print(f"Error getting chart data: {e}")

    if not chart_data:
        chart_data = [
            {'date': 'June 1', 'count': 1},
            {'date': 'June 2', 'count': 2},
            {'date': 'June 3', 'count': 3},
            {'date': 'June 4', 'count': 5},
            {'date': 'June 5', 'count': 8}
        ]

    return render_template('admin/dashboard.html', current_user=get_current_user(), stats=stats, audit_logs=audit_logs, chart_data=chart_data, active_tab='dashboard')


@app.route('/admin/erp-stub')
@admin_required
def admin_erp_stub():
    module = request.args.get('module', 'System Administration')
    metrics = {
        'Academies': [
            {'title': 'Partner Schools', 'val': '12 Active', 'desc': 'Colleges & Institutions linked'},
            {'title': 'Branches', 'val': '34 Nodes', 'desc': 'Physical labs synchronization status'},
            {'title': 'Coordinators', 'val': '15 Registered', 'desc': 'Active institution operators'}
        ],
        'Assessments': [
            {'title': 'Quiz Bank Entries', 'val': '1,420 Items', 'desc': 'Physics, Biology & Chemistry'},
            {'title': 'Coding Challenges', 'val': '84 Challenges', 'desc': 'Syntax compilation validators'},
            {'title': 'Avg Class Rank', 'val': 'Top 10%', 'desc': 'Across all connected academies'}
        ],
        'Certifications': [
            {'title': 'Certificate Templates', 'val': '5 Premium', 'desc': 'SVG Custom vector layouts'},
            {'title': 'Revocation Keys', 'val': '0 Active', 'desc': 'Security keys validation status'},
            {'title': 'Achievements Badges', 'val': '12 Unlocked', 'desc': 'Live gamification statistics'}
        ],
        'Communications': [
            {'title': 'Send Grid SMTP Status', 'val': 'Connected', 'desc': 'Email relay server validation'},
            {'title': 'Scheduled Broadcasts', 'val': '2 Pending', 'desc': 'System notifications queue'},
            {'title': 'Relay Latency', 'val': '1.2s', 'desc': 'Websocket messaging broker'}
        ],
        'Settings': [
            {'title': 'Branding Override', 'val': 'ChemLove Premium', 'desc': 'Global brand title'},
            {'title': 'Multi-Factor Auth (MFA)', 'val': 'Enforced', 'desc': 'Security authentication keys'},
            {'title': 'SMTP Relay Server', 'val': 'smtp.gmail.com', 'desc': 'Mail system transport configurations'}
        ],
        'AI': [
            {'title': 'LLM Gateway', 'val': 'DeepSeek / Gemini', 'desc': 'Active inference nodes status'},
            {'title': 'AI Generation Queue', 'val': '0 In-Queue', 'desc': 'Auto-quiz compilation request log'},
            {'title': 'Token Budget Utilisation', 'val': '14.2%', 'desc': 'Platform-wide consumption telemetry'}
        ],
        'System': [
            {'title': 'Database Backup', 'val': 'Daily Autocommit', 'desc': 'Automated SQL binary backups'},
            {'title': 'Intrusion Detection System', 'val': 'Shield Active', 'desc': 'Threat monitoring terminal logs'},
            {'title': 'Backup History', 'val': '14 Backups', 'desc': 'Available restore snapshots'}
        ]
    }
    selected_metrics = metrics.get(module, [
        {'title': 'ERP Component', 'val': 'Scalable Node', 'desc': 'Under Supervision'},
        {'title': 'System Integration', 'val': 'Connected', 'desc': 'Operational'},
        {'title': 'Status', 'val': 'Optimal', 'desc': 'All services live'}
    ])
    return render_template('admin/erp_stub.html', current_user=get_current_user(), module=module, metrics=selected_metrics, active_tab=module.lower())


@app.route('/admin/control-center', methods=['GET', 'POST'])
@admin_required
def admin_control_center():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            name = request.form.get('name')
            email = request.form.get('email')
            institution = request.form.get('institution')
            role = request.form.get('role')
            class_level = request.form.get('class_level') if role == 'student' else None
            password = request.form.get('password')
            
            if not (name and email and password and institution and role):
                flash("Missing required fields for user creation.", "error")
                return redirect(url_for('admin_control_center'))
            
            pwd_hash = generate_password_hash(password)
            try:
                with get_db() as conn:
                    existing = conn.execute("SELECT id FROM users WHERE email = %s", (email,)).fetchone()
                    if existing:
                        flash("A user with this email registry already exists.", "error")
                        return redirect(url_for('admin_control_center'))
                    
                    cursor = conn.execute(
                        "INSERT INTO users (name, email, password_hash, institution, role, class_level, status) VALUES (%s, %s, %s, %s, %s, %s, 'active')",
                        (name, email, pwd_hash, institution, role, class_level)
                    )
                    new_uid = cursor.lastrowid
                    
                    if role == 'student':
                        conn.execute("INSERT IGNORE INTO student_profiles (user_id, current_xp, level) VALUES (%s, 100, 1)", (new_uid,))
                        if class_level:
                            matching_courses = conn.execute("SELECT id FROM courses WHERE class_level = %s AND status = 'active'", (class_level,)).fetchall()
                            for c in matching_courses:
                                conn.execute("INSERT IGNORE INTO course_enrollments (course_id, student_id, progress, status) VALUES (%s, %s, 0, 'active')", (c['id'], new_uid))
                    elif role == 'teacher':
                        conn.execute("INSERT IGNORE INTO teacher_profiles (user_id, department) VALUES (%s, 'Chemistry')", (new_uid,))
                        
                log_audit("create_user", f"Created user {name} ({role}) - Email: {email}")
                flash(f"Successfully registered user {name}.", "success")
            except Exception as e:
                flash(f"Error creating user: {e}", "error")
                
        elif action == 'edit':
            uid = request.form.get('id')
            name = request.form.get('name')
            institution = request.form.get('institution')
            role = request.form.get('role')
            class_level = request.form.get('class_level') if role == 'student' else None
            status = request.form.get('status')
            
            if not (uid and name and institution and role and status):
                flash("Missing required fields for user edit.", "error")
                return redirect(url_for('admin_control_center'))
            
            try:
                with get_db() as conn:
                    conn.execute(
                        "UPDATE users SET name = %s, institution = %s, role = %s, class_level = %s, status = %s WHERE id = %s",
                        (name, institution, role, class_level, status, uid)
                    )
                    if role == 'student':
                        conn.execute("INSERT IGNORE INTO student_profiles (user_id, current_xp, level) VALUES (%s, 100, 1)", (uid,))
                    elif role == 'teacher':
                        conn.execute("INSERT IGNORE INTO teacher_profiles (user_id, department) VALUES (%s, 'Chemistry')", (uid,))
                log_audit("edit_user", f"Updated user parameters for ID {uid}: {name} ({role}), status: {status}")
                flash("User parameters successfully updated.", "success")
            except Exception as e:
                flash(f"Error updating user: {e}", "error")
                
        elif action == 'delete':
            uid = request.form.get('id')
            if not uid:
                flash("User ID missing for deletion.", "error")
                return redirect(url_for('admin_control_center'))
            try:
                with get_db() as conn:
                    target = conn.execute("SELECT name, email, role FROM users WHERE id = %s", (uid,)).fetchone()
                    if target:
                        conn.execute("DELETE FROM users WHERE id = %s", (uid,))
                        log_audit("delete_user", f"Purged user {target['name']} ({target['role']}) - Email: {target['email']} - ID: {uid}")
                        flash(f"User {target['name']} permanently deleted.", "success")
                    else:
                        flash("User not found.", "error")
            except Exception as e:
                flash(f"Error deleting user: {e}", "error")
                
        elif action == 'reset_password':
            uid = request.form.get('id')
            password = request.form.get('password')
            if not (uid and password):
                flash("Missing ID or new password.", "error")
                return redirect(url_for('admin_control_center'))
            pwd_hash = generate_password_hash(password)
            try:
                with get_db() as conn:
                    target = conn.execute("SELECT name, email FROM users WHERE id = %s", (uid,)).fetchone()
                    if target:
                        conn.execute("UPDATE users SET password_hash = %s WHERE id = %s", (pwd_hash, uid))
                        log_audit("reset_password", f"Reset password credentials for {target['name']} (ID: {uid})")
                        flash(f"Credentials successfully reset for {target['name']}.", "success")
                    else:
                        flash("User not found.", "error")
            except Exception as e:
                flash(f"Error resetting credentials: {e}", "error")

        return redirect(url_for('admin_control_center'))

    search_query = request.args.get('search', '').strip()
    selected_role = request.args.get('role', 'all').strip()
    
    users = []
    try:
        with get_db() as conn:
            query = "SELECT * FROM users"
            params = []
            conditions = []
            
            if search_query:
                conditions.append("(name LIKE %s OR email LIKE %s OR institution LIKE %s)")
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term, like_term])
                
            if selected_role != 'all':
                conditions.append("role = %s")
                params.append(selected_role)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY id DESC"
            rows = conn.execute(query, tuple(params)).fetchall()
            
            for row in rows:
                u_dict = dict(row)
                u_dict["classLevel"] = row["class_level"]
                u_dict["class_level"] = row["class_level"]
                users.append(u_dict)
    except Exception as e:
        print(f"Error fetching users: {e}")
        
    return render_template(
        'admin/control_center.html', 
        current_user=user, 
        users=users, 
        search_query=search_query, 
        selected_role=selected_role,
        active_tab='users'
    )


@app.route('/admin/student-monitoring/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_student_monitoring(user_id):
    with get_db() as conn:
        student_row = conn.execute("SELECT * FROM users WHERE id = %s AND role = 'student'", (user_id,)).fetchone()
        
    if not student_row:
        flash("Student profile not found.", "error")
        return redirect(url_for('admin_control_center'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'issue_certificate':
            course_id = request.form.get('course_id')
            if course_id:
                import uuid
                verification_id = f"CERT-CHEM-{uuid.uuid4().hex[:8].upper()}"
                try:
                    with get_db() as conn:
                        conn.execute(
                            "INSERT INTO certificates (student_id, course_id, verification_id, status) VALUES (%s, %s, %s, 'issued')",
                            (user_id, course_id, verification_id)
                        )
                    log_audit("issue_certificate", f"Manually issued certificate {verification_id} for course ID {course_id} to student ID {user_id}")
                    flash(f"Manually issued verified certificate: {verification_id}", "success")
                except Exception as e:
                    flash(f"Error issuing certificate: {e}", "error")
                    
        elif action == 'move_batch':
            class_level = request.form.get('class_level')
            if class_level:
                try:
                    with get_db() as conn:
                        conn.execute("UPDATE users SET class_level = %s WHERE id = %s", (class_level, user_id))
                        matching_courses = conn.execute("SELECT id FROM courses WHERE class_level = %s AND status = 'active'", (class_level,)).fetchall()
                        for c in matching_courses:
                            conn.execute("INSERT IGNORE INTO course_enrollments (course_id, student_id, progress, status) VALUES (%s, %s, 0, 'active')", (c['id'], user_id))
                    log_audit("move_batch", f"Moved student ID {user_id} to batch Class {class_level}")
                    flash(f"Moved student to Class {class_level} batch.", "success")
                except Exception as e:
                    flash(f"Error moving batch: {e}", "error")
                    
        elif action == 'toggle_access':
            new_status = 'suspended' if student_row['status'] == 'active' else 'active'
            try:
                with get_db() as conn:
                    conn.execute("UPDATE users SET status = %s WHERE id = %s", (new_status, user_id))
                log_audit("toggle_access", f"Toggled student ID {user_id} status to {new_status}")
                flash(f"Student status successfully updated to {new_status}.", "success")
            except Exception as e:
                flash(f"Error toggling status: {e}", "error")
                
        return redirect(url_for('admin_student_monitoring', user_id=user_id))

    student = dict(student_row)
    student["classLevel"] = student_row["class_level"]
    student["class_level"] = student_row["class_level"]
    
    courses = []
    enrollments = []
    quiz_attempts = []
    history = []
    attendance_stats = {'present': 0, 'absent': 0, 'late': 0, 'percentage': 100}
    
    try:
        with get_db() as conn:
            sp = conn.execute("SELECT current_xp, level FROM student_profiles WHERE user_id = %s", (user_id,)).fetchone()
            student["current_xp"] = sp["current_xp"] if sp else 100
            student["level"] = sp["level"] if sp else 1
            
            courses_rows = conn.execute("SELECT id, title FROM courses WHERE status = 'active' ORDER BY title ASC").fetchall()
            courses = [dict(c) for c in courses_rows]
            
            enroll_rows = conn.execute("""
                SELECT ce.*, c.title as course_title
                FROM course_enrollments ce
                JOIN courses c ON ce.course_id = c.id
                WHERE ce.student_id = %s
            """, (user_id,)).fetchall()
            for r in enroll_rows:
                e_dict = dict(r)
                if isinstance(e_dict.get('enrolled_at'), datetime):
                    e_dict['enrolled_at'] = e_dict['enrolled_at'].strftime('%Y-%m-%d')
                enrollments.append(e_dict)
                
            qa_rows = conn.execute("""
                SELECT ta.*, t.title as test_title
                FROM test_attempts ta
                JOIN tests t ON ta.test_id = t.id
                WHERE ta.student_id = %s
                ORDER BY ta.completed_at DESC
            """, (user_id,)).fetchall()
            for r in qa_rows:
                ta_dict = dict(r)
                if isinstance(ta_dict.get('completed_at'), datetime):
                    ta_dict['completed_at'] = ta_dict['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
                quiz_attempts.append(ta_dict)
                
            hist_rows = conn.execute("SELECT * FROM user_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 50", (user_id,)).fetchall()
            for r in hist_rows:
                h_dict = dict(r)
                if isinstance(h_dict.get('created_at'), datetime):
                    h_dict['created_at'] = h_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                history.append(h_dict)
                
            att_rows = conn.execute("SELECT status, COUNT(*) as count FROM attendance WHERE student_id = %s GROUP BY status", (user_id,)).fetchall()
            total_days = 0
            present_days = 0
            for r in att_rows:
                st = r['status'].lower()
                c = r['count']
                total_days += c
                if st in attendance_stats:
                    attendance_stats[st] = c
                if st == 'present' or st == 'late':
                    present_days += c
            if total_days > 0:
                attendance_stats['percentage'] = round((present_days / total_days) * 100)
    except Exception as e:
        print(f"Error fetching student monitoring telemetry: {e}")

    return render_template(
        'admin/student_monitoring.html', 
        current_user=get_current_user(), 
        student=student, 
        courses=courses,
        enrollments=enrollments,
        quiz_attempts=quiz_attempts,
        history=history,
        attendance_stats=attendance_stats,
        active_tab='users'
    )


@app.route('/admin/teacher-monitoring/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def admin_teacher_monitoring(user_id):
    with get_db() as conn:
        teacher_row = conn.execute("SELECT * FROM users WHERE id = %s AND role = 'teacher'", (user_id,)).fetchone()
        
    if not teacher_row:
        flash("Teacher profile not found.", "error")
        return redirect(url_for('admin_control_center'))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'assign_course':
            course_id = request.form.get('course_id')
            if course_id:
                try:
                    with get_db() as conn:
                        conn.execute("INSERT IGNORE INTO teacher_courses (teacher_id, course_id) VALUES (%s, %s)", (user_id, course_id))
                    log_audit("assign_course", f"Assigned course ID {course_id} management to teacher ID {user_id}")
                    flash("Course assigned to teacher successfully.", "success")
                except Exception as e:
                    flash(f"Error assigning course: {e}", "error")
                    
        elif action == 'remove_course':
            course_id = request.form.get('course_id')
            if course_id:
                try:
                    with get_db() as conn:
                        conn.execute("DELETE FROM teacher_courses WHERE teacher_id = %s AND course_id = %s", (user_id, course_id))
                    log_audit("remove_course", f"Removed course ID {course_id} assignment from teacher ID {user_id}")
                    flash("Course assignment removed successfully.", "success")
                except Exception as e:
                    flash(f"Error removing course assignment: {e}", "error")
                    
        elif action == 'update_department':
            dept = request.form.get('department')
            if dept:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO teacher_profiles (user_id, department) 
                            VALUES (%s, %s) 
                            ON DUPLICATE KEY UPDATE department = %s
                        """, (user_id, dept, dept))
                    log_audit("update_department", f"Updated department to {dept} for teacher ID {user_id}")
                    flash(f"Department adjusted to {dept}.", "success")
                except Exception as e:
                    flash(f"Error updating department: {e}", "error")
                    
        elif action == 'toggle_access':
            new_status = 'suspended' if teacher_row['status'] == 'active' else 'active'
            try:
                with get_db() as conn:
                    conn.execute("UPDATE users SET status = %s WHERE id = %s", (new_status, user_id))
                log_audit("toggle_access", f"Toggled teacher ID {user_id} status to {new_status}")
                flash(f"Teacher status successfully updated to {new_status}.", "success")
            except Exception as e:
                flash(f"Error toggling status: {e}", "error")
                
        return redirect(url_for('admin_teacher_monitoring', user_id=user_id))

    teacher = dict(teacher_row)
    
    all_courses = []
    assigned_courses = []
    classrooms = []
    history = []
    
    try:
        with get_db() as conn:
            tp = conn.execute("SELECT department FROM teacher_profiles WHERE user_id = %s", (user_id,)).fetchone()
            teacher["department"] = tp["department"] if tp else 'Chemistry'
            
            courses_rows = conn.execute("SELECT id, title FROM courses WHERE status = 'active' ORDER BY title ASC").fetchall()
            all_courses = [dict(c) for c in courses_rows]
            
            assigned_rows = conn.execute("""
                SELECT tc.*, c.title as course_title
                FROM teacher_courses tc
                JOIN courses c ON tc.course_id = c.id
                WHERE tc.teacher_id = %s
            """, (user_id,)).fetchall()
            for r in assigned_rows:
                tc_dict = dict(r)
                if isinstance(tc_dict.get('assigned_at'), datetime):
                    tc_dict['assigned_at'] = tc_dict['assigned_at'].strftime('%Y-%m-%d')
                assigned_courses.append(tc_dict)
                
            room_rows = conn.execute("SELECT * FROM classrooms WHERE teacher_id = %s ORDER BY name ASC", (user_id,)).fetchall()
            classrooms = [dict(r) for r in room_rows]
                
            hist_rows = conn.execute("SELECT * FROM user_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 50", (user_id,)).fetchall()
            for r in hist_rows:
                h_dict = dict(r)
                if isinstance(h_dict.get('created_at'), datetime):
                    h_dict['created_at'] = h_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                history.append(h_dict)
    except Exception as e:
        print(f"Error fetching teacher monitoring telemetry: {e}")

    return render_template(
        'admin/teacher_monitoring.html', 
        current_user=get_current_user(), 
        teacher=teacher, 
        all_courses=all_courses,
        assigned_courses=assigned_courses,
        classrooms=classrooms,
        history=history,
        active_tab='users'
    )


# ============================================================
# RBAC PERMISSIONS MATRIX & CAPABILITIES
# ============================================================

@app.route('/admin/permissions', methods=['GET', 'POST'])
@admin_required
def admin_permissions():
    user = get_current_user()
    if user['role'] != 'admin' and not check_permission('manage_users'):
        flash("Unauthorized. You do not have permission to manage permissions.", "error")
        return redirect(url_for('profile_page'))
        
    permission_keys = [
        'manage_users', 'manage_content', 'manage_assessments', 
        'manage_certificates', 'send_notifications', 'view_reports'
    ]
    
    if request.method == 'POST':
        try:
            with get_db() as conn:
                for pk in permission_keys:
                    val = 1 if request.form.get(pk) else 0
                    conn.execute("""
                        INSERT INTO permissions (role, permission_key, is_granted)
                        VALUES ('admin', %s, %s)
                        ON DUPLICATE KEY UPDATE is_granted = %s
                    """, (pk, val, val))
            log_audit("update_permissions", "Updated Admin RBAC permission switches matrix")
            flash("Admin capability matrix updated successfully.", "success")
        except Exception as e:
            flash(f"Error updating permissions: {e}", "error")
        return redirect(url_for('admin_permissions'))
        
    perms = {pk: False for pk in permission_keys}
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT permission_key, is_granted FROM permissions WHERE role = 'admin'").fetchall()
            for r in rows:
                perms[r['permission_key']] = bool(r['is_granted'])
    except Exception as e:
        print(f"Error loading admin permissions: {e}")
        
    return render_template('admin/permissions.html', current_user=user, perms=perms, active_tab='permissions')


# ============================================================
# STUDENT LMS CATALOG
# ============================================================

@app.route('/student/courses')
@student_required
def student_courses():
    user = get_current_user()
    
    # Auto-enroll student in courses matching their class level if they are not enrolled
    if user.get("classLevel"):
        try:
            with get_db() as conn:
                matching_courses = conn.execute("SELECT id FROM courses WHERE class_level = %s AND status = 'active'", (user["classLevel"],)).fetchall()
                for c in matching_courses:
                    conn.execute("INSERT IGNORE INTO course_enrollments (course_id, student_id, progress, status) VALUES (%s, %s, 0, 'active')", (c['id'], user['id']))
        except Exception as e:
            print(f"Error auto-enrolling student: {e}")

    enrollments = []
    try:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT ce.*, c.title as course_title, c.description, c.category
                FROM course_enrollments ce
                JOIN courses c ON ce.course_id = c.id
                WHERE ce.student_id = %s
            """, (user["id"],)).fetchall()
            enrollments = [dict(r) for r in rows]
    except Exception as e:
        print(f"Error fetching enrollments: {e}")
    return render_template('student/courses.html', current_user=user, enrollments=enrollments, active_tab='courses')


@app.route('/student/course/<int:course_id>')
@student_required
def student_course_view(course_id):
    user = get_current_user()
    try:
        with get_db() as conn:
            course = conn.execute("SELECT * FROM courses WHERE id = %s", (course_id,)).fetchone()
            if not course:
                flash("Course not found.", "error")
                return redirect(url_for('student_courses'))
                
            enrollment = conn.execute("SELECT * FROM course_enrollments WHERE course_id = %s AND student_id = %s", (course_id, user["id"])).fetchone()
            
            # Fetch hierarchy: modules -> chapters -> lessons -> resources
            modules_rows = conn.execute("SELECT * FROM modules WHERE course_id = %s ORDER BY order_index ASC", (course_id,)).fetchall()
            modules = []
            for m in modules_rows:
                m_dict = dict(m)
                ch_rows = conn.execute("SELECT * FROM chapters WHERE module_id = %s ORDER BY chapter_number ASC", (m_dict["id"],)).fetchall()
                chapters = []
                for ch in ch_rows:
                    ch_dict = parse_chapter_json_fields(ch)
                    lesson_rows = conn.execute("SELECT * FROM lessons WHERE chapter_id = %s AND status = 'published' ORDER BY order_index ASC", (ch_dict["id"],)).fetchall()
                    lessons = []
                    for l in lesson_rows:
                        l_dict = dict(l)
                        res_rows = conn.execute("SELECT * FROM resources WHERE lesson_id = %s AND status = 'published' ORDER BY id ASC", (l_dict["id"],)).fetchall()
                        l_dict["resources"] = [dict(r) for r in res_rows]
                        lessons.append(l_dict)
                    ch_dict["lessons"] = lessons
                    chapters.append(ch_dict)
                m_dict["chapters"] = chapters
                modules.append(m_dict)
    except Exception as e:
        print(f"Error loading course view: {e}")
        flash("Error loading course content.", "error")
        return redirect(url_for('student_courses'))
        
    return render_template(
        'student/course_view.html', 
        current_user=user, 
        course=course, 
        modules=modules, 
        enrollment=enrollment,
        active_tab='courses'
    )


@app.route('/student/certificates')
@student_required
def student_certificates():
    user = get_current_user()
    certs = []
    try:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT c.*, cr.title as course_title, cr.description
                FROM certificates c
                JOIN courses cr ON c.course_id = cr.id
                WHERE c.student_id = %s AND c.status = 'issued'
                ORDER BY c.issued_at DESC
            """, (user["id"],)).fetchall()
            for r in rows:
                c_dict = dict(r)
                if isinstance(c_dict.get('issued_at'), datetime):
                    c_dict['issued_at'] = c_dict['issued_at'].strftime('%B %d, %Y')
                certs.append(c_dict)
    except Exception as e:
        print(f"Error fetching student certificates: {e}")
    return render_template('student/certificates.html', current_user=user, certificates=certs, active_tab='certificates')


# ============================================================
# API — LMS CORE REST CRUD
# ============================================================

@app.route('/api/categories', methods=['GET', 'POST', 'DELETE'])
def api_categories():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'GET':
        try:
            with get_db() as conn:
                rows = conn.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()
            return jsonify({"categories": [dict(r) for r in rows]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        name = payload.get("name")
        if not name:
            return jsonify({"error": "Missing category name"}), 400
        try:
            with get_db() as conn:
                cursor = conn.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
                cat_id = cursor.lastrowid
            log_audit("create_category", f"Created content category: {name}")
            return jsonify({"ok": True, "id": cat_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'DELETE':
        cat_id = request.args.get("id")
        if not cat_id:
            return jsonify({"error": "Missing category id"}), 400
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM categories WHERE id = %s", (cat_id,))
            log_audit("delete_category", f"Deleted category ID: {cat_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/admin/courses', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_admin_courses():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'GET':
        course_id = request.args.get("id")
        try:
            with get_db() as conn:
                if course_id:
                    course = conn.execute("SELECT * FROM courses WHERE id = %s", (course_id,)).fetchone()
                    return jsonify({"course": dict(course) if course else None})
                else:
                    rows = conn.execute("SELECT * FROM courses ORDER BY class_level ASC, title ASC").fetchall()
                    return jsonify({"courses": [dict(r) for r in rows]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        title = payload.get("title")
        description = payload.get("description")
        category = payload.get("category")
        class_level = payload.get("class_level")
        status = payload.get("status", "active")
        
        if not title:
            return jsonify({"error": "Missing course title"}), 400
            
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO courses (title, description, category, class_level, status) VALUES (%s, %s, %s, %s, %s)",
                    (title, description, category, class_level, status)
                )
                course_id = cursor.lastrowid
                
                if class_level and status == 'active':
                    students = conn.execute("SELECT id FROM users WHERE role = 'student' AND class_level = %s", (class_level,)).fetchall()
                    for s in students:
                        conn.execute("INSERT IGNORE INTO course_enrollments (course_id, student_id, progress, status) VALUES (%s, %s, 0, 'active')", (course_id, s['id']))
                        
            log_audit("create_course", f"Created course {title} for Class {class_level}")
            return jsonify({"ok": True, "id": course_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        course_id = payload.get("id")
        if not course_id:
            return jsonify({"error": "Missing course id"}), 400
            
        title = payload.get("title")
        description = payload.get("description")
        category = payload.get("category")
        class_level = payload.get("class_level")
        status = payload.get("status")
        
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        if category is not None:
            update_fields.append("category = %s")
            params.append(category)
        if class_level is not None:
            update_fields.append("class_level = %s")
            params.append(class_level)
        if status is not None:
            update_fields.append("status = %s")
            params.append(status)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(course_id)
        query = f"UPDATE courses SET {', '.join(update_fields)} WHERE id = %s"
        try:
            with get_db() as conn:
                conn.execute(query, tuple(params))
            log_audit("update_course", f"Updated parameters for course ID {course_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'DELETE':
        course_id = request.args.get("id")
        if not course_id:
            return jsonify({"error": "Missing course id"}), 400
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM courses WHERE id = %s", (course_id,))
            log_audit("delete_course", f"Deleted course ID {course_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/admin/modules', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_admin_modules():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'GET':
        module_id = request.args.get("id")
        course_id = request.args.get("course_id")
        try:
            with get_db() as conn:
                if module_id:
                    module = conn.execute("SELECT * FROM modules WHERE id = %s", (module_id,)).fetchone()
                    return jsonify({"module": dict(module) if module else None})
                elif course_id:
                    rows = conn.execute("SELECT * FROM modules WHERE course_id = %s ORDER BY order_index ASC", (course_id,)).fetchall()
                    return jsonify({"modules": [dict(r) for r in rows]})
                else:
                    rows = conn.execute("SELECT * FROM modules ORDER BY course_id ASC, order_index ASC").fetchall()
                    return jsonify({"modules": [dict(r) for r in rows]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        course_id = payload.get("course_id")
        title = payload.get("title")
        description = payload.get("description")
        order_index = payload.get("order_index", 0)
        
        if not course_id or not title:
            return jsonify({"error": "Missing course_id or title"}), 400
            
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO modules (course_id, title, description, order_index) VALUES (%s, %s, %s, %s)",
                    (course_id, title, description, order_index)
                )
                module_id = cursor.lastrowid
            log_audit("create_module", f"Created module {title} for course ID {course_id}")
            return jsonify({"ok": True, "id": module_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        module_id = payload.get("id")
        if not module_id:
            return jsonify({"error": "Missing module id"}), 400
            
        title = payload.get("title")
        description = payload.get("description")
        order_index = payload.get("order_index")
        
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        if order_index is not None:
            update_fields.append("order_index = %s")
            params.append(order_index)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(module_id)
        query = f"UPDATE modules SET {', '.join(update_fields)} WHERE id = %s"
        try:
            with get_db() as conn:
                conn.execute(query, tuple(params))
            log_audit("update_module", f"Updated module ID {module_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'DELETE':
        module_id = request.args.get("id")
        if not module_id:
            return jsonify({"error": "Missing module id"}), 400
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM modules WHERE id = %s", (module_id,))
            log_audit("delete_module", f"Deleted module ID {module_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/admin/lessons', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_admin_lessons():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'GET':
        lesson_id = request.args.get("id")
        chapter_id = request.args.get("chapter_id")
        try:
            with get_db() as conn:
                if lesson_id:
                    lesson = conn.execute("SELECT * FROM lessons WHERE id = %s", (lesson_id,)).fetchone()
                    return jsonify({"lesson": dict(lesson) if lesson else None})
                elif chapter_id:
                    rows = conn.execute("SELECT * FROM lessons WHERE chapter_id = %s ORDER BY order_index ASC", (chapter_id,)).fetchall()
                    return jsonify({"lessons": [dict(r) for r in rows]})
                else:
                    rows = conn.execute("SELECT * FROM lessons ORDER BY chapter_id ASC, order_index ASC").fetchall()
                    return jsonify({"lessons": [dict(r) for r in rows]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        chapter_id = payload.get("chapter_id")
        title = payload.get("title")
        content = payload.get("content")
        order_index = payload.get("order_index", 0)
        status = payload.get("status", "published")
        
        if not chapter_id or not title:
            return jsonify({"error": "Missing chapter_id or title"}), 400
            
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO lessons (chapter_id, title, content, order_index, status) VALUES (%s, %s, %s, %s, %s)",
                    (chapter_id, title, content, order_index, status)
                )
                lesson_id = cursor.lastrowid
            log_audit("create_lesson", f"Created lesson {title} for chapter ID {chapter_id}")
            return jsonify({"ok": True, "id": lesson_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        lesson_id = payload.get("id")
        if not lesson_id:
            return jsonify({"error": "Missing lesson id"}), 400
            
        title = payload.get("title")
        content = payload.get("content")
        order_index = payload.get("order_index")
        status = payload.get("status")
        
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        if content is not None:
            update_fields.append("content = %s")
            params.append(content)
        if order_index is not None:
            update_fields.append("order_index = %s")
            params.append(order_index)
        if status is not None:
            update_fields.append("status = %s")
            params.append(status)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(lesson_id)
        query = f"UPDATE lessons SET {', '.join(update_fields)} WHERE id = %s"
        try:
            with get_db() as conn:
                conn.execute(query, tuple(params))
            log_audit("update_lesson", f"Updated lesson ID {lesson_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'DELETE':
        lesson_id = request.args.get("id")
        if not lesson_id:
            return jsonify({"error": "Missing lesson id"}), 400
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM lessons WHERE id = %s", (lesson_id,))
            log_audit("delete_lesson", f"Deleted lesson ID {lesson_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/admin/resources', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_admin_resources():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'GET':
        resource_id = request.args.get("id")
        lesson_id = request.args.get("lesson_id")
        try:
            with get_db() as conn:
                if resource_id:
                    res = conn.execute("SELECT * FROM resources WHERE id = %s", (resource_id,)).fetchone()
                    return jsonify({"resource": dict(res) if res else None})
                elif lesson_id:
                    rows = conn.execute("SELECT * FROM resources WHERE lesson_id = %s ORDER BY id ASC", (lesson_id,)).fetchall()
                    return jsonify({"resources": [dict(r) for r in rows]})
                else:
                    rows = conn.execute("SELECT * FROM resources ORDER BY id ASC").fetchall()
                    return jsonify({"resources": [dict(r) for r in rows]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        lesson_id = payload.get("lesson_id")
        title = payload.get("title")
        file_path = payload.get("file_path")
        file_type = payload.get("file_type", "link")
        status = payload.get("status", "published")
        
        if not title or not file_path:
            return jsonify({"error": "Missing title or file_path"}), 400
            
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO resources (lesson_id, title, file_path, file_type, status) VALUES (%s, %s, %s, %s, %s)",
                    (lesson_id, title, file_path, file_type, status)
                )
                res_id = cursor.lastrowid
            log_audit("create_resource", f"Created resource {title} of type {file_type}")
            return jsonify({"ok": True, "id": res_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        resource_id = payload.get("id")
        if not resource_id:
            return jsonify({"error": "Missing resource id"}), 400
            
        title = payload.get("title")
        file_path = payload.get("file_path")
        file_type = payload.get("file_type")
        status = payload.get("status")
        
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        if file_path is not None:
            update_fields.append("file_path = %s")
            params.append(file_path)
        if file_type is not None:
            update_fields.append("file_type = %s")
            params.append(file_type)
        if status is not None:
            update_fields.append("status = %s")
            params.append(status)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(resource_id)
        query = f"UPDATE resources SET {', '.join(update_fields)} WHERE id = %s"
        try:
            with get_db() as conn:
                conn.execute(query, tuple(params))
            log_audit("update_resource", f"Updated resource ID {resource_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'DELETE':
        resource_id = request.args.get("id")
        if not resource_id:
            return jsonify({"error": "Missing resource id"}), 400
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM resources WHERE id = %s", (resource_id,))
            log_audit("delete_resource", f"Deleted resource ID {resource_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/admin/certificates', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_admin_certificates():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'GET':
        cert_id = request.args.get("id")
        try:
            with get_db() as conn:
                if cert_id:
                    cert = conn.execute("""
                        SELECT c.*, u.name as student_name, u.email as student_email, cr.title as course_title
                        FROM certificates c
                        JOIN users u ON c.student_id = u.id
                        JOIN courses cr ON c.course_id = cr.id
                        WHERE c.id = %s
                    """, (cert_id,)).fetchone()
                    return jsonify({"certificate": dict(cert) if cert else None})
                else:
                    rows = conn.execute("""
                        SELECT c.*, u.name as student_name, u.email as student_email, cr.title as course_title
                        FROM certificates c
                        JOIN users u ON c.student_id = u.id
                        JOIN courses cr ON c.course_id = cr.id
                        ORDER BY c.issued_at DESC
                    """).fetchall()
                    certs = []
                    for r in rows:
                        c_dict = dict(r)
                        if isinstance(c_dict.get('issued_at'), datetime):
                            c_dict['issued_at'] = c_dict['issued_at'].strftime('%Y-%m-%d %H:%M:%S')
                        certs.append(c_dict)
                    return jsonify({"certificates": certs})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        student_id = payload.get("student_id")
        course_id = payload.get("course_id")
        status = payload.get("status", "issued")
        
        if not student_id or not course_id:
            return jsonify({"error": "Missing student_id or course_id"}), 400
            
        import uuid
        verification_id = f"CERT-CHEM-{uuid.uuid4().hex[:8].upper()}"
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO certificates (student_id, course_id, verification_id, status) VALUES (%s, %s, %s, %s)",
                    (student_id, course_id, verification_id, status)
                )
                cert_id = cursor.lastrowid
            log_audit("issue_certificate", f"Issued certificate {verification_id} to student ID {student_id}")
            return jsonify({"ok": True, "id": cert_id, "verification_id": verification_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        cert_id = payload.get("id")
        status = payload.get("status")
        
        if not cert_id or status is None:
            return jsonify({"error": "Missing id or status"}), 400
            
        try:
            with get_db() as conn:
                conn.execute("UPDATE certificates SET status = %s WHERE id = %s", (status, cert_id))
            log_audit("update_certificate", f"Updated certificate ID {cert_id} status to {status}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'DELETE':
        cert_id = request.args.get("id")
        if not cert_id:
            return jsonify({"error": "Missing cert id"}), 400
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM certificates WHERE id = %s", (cert_id,))
            log_audit("delete_certificate", f"Deleted certificate ID {cert_id}")
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route('/api/student/update_progress', methods=['POST'])
@student_required
def api_student_update_progress():
    user = get_current_user()
    course_id = request.args.get("course_id")
    if not course_id:
        return jsonify({"error": "Missing course_id"}), 400
        
    try:
        with get_db() as conn:
            lessons = conn.execute("""
                SELECT l.id
                FROM lessons l
                JOIN chapters ch ON l.chapter_id = ch.id
                JOIN modules m ON ch.module_id = m.id
                WHERE m.course_id = %s AND l.status = 'published'
            """, (course_id,)).fetchall()
            
            total_lessons = len(lessons)
            if total_lessons == 0:
                conn.execute(
                    "UPDATE course_enrollments SET progress = 100, status = 'completed', completed_at = NOW() WHERE course_id = %s AND student_id = %s",
                    (course_id, user["id"])
                )
                return jsonify({"ok": True, "progress": 100})
                
            lesson_ids = [l["id"] for l in lessons]
            
            completed_events = conn.execute(
                "SELECT event_data FROM user_history WHERE user_id = %s AND event_type = 'read_notes'",
                (user["id"],)
            ).fetchall()
            
            completed_set = set()
            for ev in completed_events:
                data_str = ev["event_data"] or ""
                match = re.search(r"lesson_id=(\d+)", data_str)
                if match:
                    lid = int(match.group(1))
                    if lid in lesson_ids:
                        completed_set.add(lid)
                        
            progress = min(100, round((len(completed_set) / total_lessons) * 100))
            
            status = 'completed' if progress == 100 else 'active'
            completed_at_clause = ", completed_at = NOW()" if progress == 100 else ""
            conn.execute(
                f"UPDATE course_enrollments SET progress = %s, status = %s{completed_at_clause} WHERE course_id = %s AND student_id = %s",
                (progress, status, course_id, user["id"])
            )
            
            if progress == 100:
                existing = conn.execute("SELECT id FROM certificates WHERE student_id = %s AND course_id = %s", (user["id"], course_id)).fetchone()
                if not existing:
                    import uuid
                    verification_id = f"CERT-CHEM-{uuid.uuid4().hex[:8].upper()}"
                    conn.execute(
                        "INSERT INTO certificates (student_id, course_id, verification_id, status) VALUES (%s, %s, %s, 'issued')",
                        (user["id"], course_id, verification_id)
                    )
                    log_audit("issue_certificate", f"Auto-issued certificate {verification_id} to student ID {user['id']} on course 100% completion")
                    
        return jsonify({"ok": True, "progress": progress})
    except Exception as e:
        print(f"Error updating course progress: {e}")
        return jsonify({"error": str(e)}), 500


@teacher_required
def teacher_content():
    return render_template('admin/content.html', current_user=get_current_user(), active_tab='content')


# ============================================================
# ADMIN PORTAL
# ============================================================

@app.route('/admin/content')
@admin_required
def admin_content():
    return render_template('admin/content.html', current_user=get_current_user(), active_tab='content')


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


@app.route('/api/reactions')
def api_reactions():
    class_level = request.args.get('class_level')
    try:
        with get_db() as conn:
            if class_level and class_level != 'all':
                rows = conn.execute("SELECT * FROM reactions WHERE class_level = %s ORDER BY id ASC", (class_level,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM reactions ORDER BY id ASC").fetchall()
        reactions = []
        for r in rows:
            parsed = parse_reaction_json_fields(r)
            reactants_list = parsed.get('reactants', []) or []
            products_list = parsed.get('products', []) or []
            parsed['reactants'] = ','.join(reactants_list)
            parsed['products'] = ','.join(products_list)
            reactions.append(parsed)
        return jsonify({"reactions": reactions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/log_event', methods=['POST'])
def api_log_event():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    payload = request.get_json(silent=True) or {}
    event_type = payload.get("event_type")
    event_data = payload.get("event_data")
    
    if not event_type:
        return jsonify({"error": "Missing event_type"}), 400
        
    add_history(user["id"], event_type, event_data)
    
    xp_to_add = 0
    if event_type == 'quiz_passed':
        xp_to_add = 30
    elif event_type == 'titration_complete':
        xp_to_add = 25
    elif event_type == 'reaction_success':
        xp_to_add = 15
        
    if xp_to_add > 0:
        try:
            with get_db() as conn:
                conn.execute(
                    "UPDATE student_profiles SET current_xp = current_xp + %s WHERE user_id = %s",
                    (xp_to_add, user["id"])
                )
        except Exception as e:
            print(f"Error updating XP: {e}")
            
    return jsonify({"ok": True})


# ============================================================
# API — CONTENT MANAGEMENT (Admin/Teacher)
# ============================================================

@app.route('/api/admin/chapters', methods=['POST', 'PUT', 'DELETE'])
def api_admin_chapters():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        class_level = payload.get("class_level")
        chapter_number = payload.get("chapter_number")
        title = payload.get("title")
        description = payload.get("description")
        
        if not title:
            return jsonify({"error": "Missing title"}), 400
            
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO chapters (
                    class_level, chapter_number, title, description,
                    learning_objectives, key_points, important_laws, formulas,
                    constants, important_reactions, notes, real_life_applications,
                    virtual_labs, practice_questions, common_mistakes, difficulty,
                    estimated_study_time, chapter_weightage, next_chapter
                ) VALUES (%s, %s, %s, %s, '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', 'Beginner', '4 Hours', '{}', '{}')
                """,
                (class_level, chapter_number, title, description)
            )
            chapter_id = cursor.lastrowid
        return jsonify({"ok": True, "id": chapter_id})
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        ch_id = payload.get("id")
        if not ch_id:
            return jsonify({"error": "Missing chapter id"}), 400
            
        title = payload.get("title")
        description = payload.get("description")
        class_level = payload.get("class_level")
        chapter_number = payload.get("chapter_number")
        
        learning_objectives = json.dumps(payload.get("learning_objectives", [])) if "learning_objectives" in payload else None
        key_points = json.dumps(payload.get("key_points", [])) if "key_points" in payload else None
        formulas = json.dumps(payload.get("formulas", [])) if "formulas" in payload else None
        notes = json.dumps(payload.get("notes", [])) if "notes" in payload else None
        
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        if class_level is not None:
            update_fields.append("class_level = %s")
            params.append(class_level)
        if chapter_number is not None:
            update_fields.append("chapter_number = %s")
            params.append(chapter_number)
        if learning_objectives is not None:
            update_fields.append("learning_objectives = %s")
            params.append(learning_objectives)
        if key_points is not None:
            update_fields.append("key_points = %s")
            params.append(key_points)
        if formulas is not None:
            update_fields.append("formulas = %s")
            params.append(formulas)
        if notes is not None:
            update_fields.append("notes = %s")
            params.append(notes)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(ch_id)
        query = f"UPDATE chapters SET {', '.join(update_fields)} WHERE id = %s"
        with get_db() as conn:
            conn.execute(query, tuple(params))
        return jsonify({"ok": True})
        
    elif request.method == 'DELETE':
        ch_id = request.args.get("id")
        if not ch_id:
            return jsonify({"error": "Missing chapter id"}), 400
        with get_db() as conn:
            conn.execute("DELETE FROM chapters WHERE id = %s", (ch_id,))
        return jsonify({"ok": True})


@app.route('/api/admin/reactions', methods=['POST', 'PUT', 'DELETE'])
def api_admin_reactions():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        rxn_id = payload.get("id")
        name = payload.get("name")
        equation = payload.get("equation")
        reaction_type = payload.get("reaction_type") or "organic"
        class_level = payload.get("class_level")
        reactants = payload.get("reactants", "")
        products = payload.get("products", "")
        conditions = payload.get("conditions")
        explanation = payload.get("explanation")
        
        if not rxn_id or not name:
            return jsonify({"error": "Missing id or name"}), 400
            
        if isinstance(reactants, str):
            reactants = [r.strip() for r in reactants.split(',') if r.strip()]
        if isinstance(products, str):
            products = [p.strip() for p in products.split(',') if p.strip()]
            
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO reactions (
                    id, name, equation, reaction_type, class_level,
                    reactants, products, conditions, explanation, mechanism
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, '[]')
                """,
                (rxn_id, name, equation, reaction_type, class_level,
                 json.dumps(reactants), json.dumps(products), conditions, explanation)
            )
        return jsonify({"ok": True})
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        rxn_id = payload.get("id")
        if not rxn_id:
            return jsonify({"error": "Missing reaction id"}), 400
            
        name = payload.get("name")
        equation = payload.get("equation")
        reaction_type = payload.get("reaction_type")
        class_level = payload.get("class_level")
        reactants = payload.get("reactants")
        products = payload.get("products")
        conditions = payload.get("conditions")
        explanation = payload.get("explanation")
        
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = %s")
            params.append(name)
        if equation is not None:
            update_fields.append("equation = %s")
            params.append(equation)
        if reaction_type is not None:
            update_fields.append("reaction_type = %s")
            params.append(reaction_type)
        if class_level is not None:
            update_fields.append("class_level = %s")
            params.append(class_level)
        if reactants is not None:
            if isinstance(reactants, str):
                reactants = [r.strip() for r in reactants.split(',') if r.strip()]
            update_fields.append("reactants = %s")
            params.append(json.dumps(reactants))
        if products is not None:
            if isinstance(products, str):
                products = [p.strip() for p in products.split(',') if p.strip()]
            update_fields.append("products = %s")
            params.append(json.dumps(products))
        if conditions is not None:
            update_fields.append("conditions = %s")
            params.append(conditions)
        if explanation is not None:
            update_fields.append("explanation = %s")
            params.append(explanation)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(rxn_id)
        query = f"UPDATE reactions SET {', '.join(update_fields)} WHERE id = %s"
        with get_db() as conn:
            conn.execute(query, tuple(params))
        return jsonify({"ok": True})
        
    elif request.method == 'DELETE':
        rxn_id = request.args.get("id")
        if not rxn_id:
            return jsonify({"error": "Missing reaction id"}), 400
        with get_db() as conn:
            conn.execute("DELETE FROM reactions WHERE id = %s", (rxn_id,))
        return jsonify({"ok": True})


@app.route('/api/admin/quizzes', methods=['POST', 'PUT', 'DELETE'])
def api_admin_quizzes():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        chapter_id = payload.get("chapter_id")
        title = payload.get("title")
        duration_minutes = payload.get("duration_minutes") or 10
        total_marks = payload.get("total_marks") or 10
        
        if not chapter_id or not title:
            return jsonify({"error": "Missing chapter_id or title"}), 400
            
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO quizzes (chapter_id, title, duration_minutes, total_marks) VALUES (%s, %s, %s, %s)",
                (chapter_id, title, duration_minutes, total_marks)
            )
            quiz_id = cursor.lastrowid
            
            questions = payload.get("questions", [])
            for q in questions:
                conn.execute(
                    """
                    INSERT INTO quiz_questions (
                        quiz_id, question, option_a, option_b, option_c, option_d, correct_answer, explanation
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (quiz_id, q.get("question"), q.get("option_a"), q.get("option_b"),
                     q.get("option_c"), q.get("option_d"), q.get("correct_answer", "A"), q.get("explanation", ""))
                )
        return jsonify({"ok": True, "id": quiz_id})
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        quiz_id = payload.get("id")
        if not quiz_id:
            return jsonify({"error": "Missing quiz id"}), 400
            
        title = payload.get("title")
        duration_minutes = payload.get("duration_minutes")
        total_marks = payload.get("total_marks")
        
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        if duration_minutes is not None:
            update_fields.append("duration_minutes = %s")
            params.append(duration_minutes)
        if total_marks is not None:
            update_fields.append("total_marks = %s")
            params.append(total_marks)
            
        if update_fields:
            params.append(quiz_id)
            query = f"UPDATE quizzes SET {', '.join(update_fields)} WHERE id = %s"
            with get_db() as conn:
                conn.execute(query, tuple(params))
                
        if "questions" in payload:
            questions = payload.get("questions", [])
            with get_db() as conn:
                conn.execute("DELETE FROM quiz_questions WHERE quiz_id = %s", (quiz_id,))
                for q in questions:
                    conn.execute(
                        """
                        INSERT INTO quiz_questions (
                            quiz_id, question, option_a, option_b, option_c, option_d, correct_answer, explanation
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (quiz_id, q.get("question"), q.get("option_a"), q.get("option_b"),
                         q.get("option_c"), q.get("option_d"), q.get("correct_answer"), q.get("explanation", ""))
                    )
        return jsonify({"ok": True})
        
    elif request.method == 'DELETE':
        quiz_id = request.args.get("id")
        if not quiz_id:
            return jsonify({"error": "Missing quiz id"}), 400
        with get_db() as conn:
            conn.execute("DELETE FROM quizzes WHERE id = %s", (quiz_id,))
        return jsonify({"ok": True})


@app.route('/api/admin/experiments', methods=['POST', 'PUT', 'DELETE'])
def api_admin_experiments():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        chapter_id = payload.get("chapter_id")
        title = payload.get("title")
        aim = payload.get("aim")
        theory = payload.get("theory")
        procedure = payload.get("procedure", [])
        observations = payload.get("observations", [])
        result = payload.get("result")
        
        if not title:
            return jsonify({"error": "Missing title"}), 400
            
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO experiments (
                    chapter_id, title, aim, apparatus, theory, `procedure`, observations, result, viva_questions, simulation_url
                ) VALUES (%s, %s, %s, '[]', %s, %s, %s, %s, '[]', %s)
                """,
                (chapter_id, title, aim, theory, json.dumps(procedure),
                 json.dumps(observations), result, payload.get("simulation_url"))
            )
            exp_id = cursor.lastrowid
        return jsonify({"ok": True, "id": exp_id})
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        exp_id = payload.get("id")
        if not exp_id:
            return jsonify({"error": "Missing experiment id"}), 400
            
        title = payload.get("title")
        chapter_id = payload.get("chapter_id")
        aim = payload.get("aim")
        theory = payload.get("theory")
        procedure = payload.get("procedure")
        observations = payload.get("observations")
        result = payload.get("result")
        simulation_url = payload.get("simulation_url")
        
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        if chapter_id is not None:
            update_fields.append("chapter_id = %s")
            params.append(chapter_id)
        if aim is not None:
            update_fields.append("aim = %s")
            params.append(aim)
        if theory is not None:
            update_fields.append("theory = %s")
            params.append(theory)
        if procedure is not None:
            update_fields.append("`procedure` = %s")
            params.append(json.dumps(procedure))
        if observations is not None:
            update_fields.append("observations = %s")
            params.append(json.dumps(observations))
        if result is not None:
            update_fields.append("result = %s")
            params.append(result)
        if simulation_url is not None:
            update_fields.append("simulation_url = %s")
            params.append(simulation_url)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(exp_id)
        query = f"UPDATE experiments SET {', '.join(update_fields)} WHERE id = %s"
        with get_db() as conn:
            conn.execute(query, tuple(params))
        return jsonify({"ok": True})
        
    elif request.method == 'DELETE':
        exp_id = request.args.get("id")
        if not exp_id:
            return jsonify({"error": "Missing experiment id"}), 400
        with get_db() as conn:
            conn.execute("DELETE FROM experiments WHERE id = %s", (exp_id,))
        return jsonify({"ok": True})



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
