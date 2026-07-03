import os
import json
import glob
import re
import uuid
from datetime import datetime, timezone, date
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

try:
    if os.getenv("VERCEL") == "1":
        # Force PyMySQL on Vercel to avoid native binary compilation issues
        raise ImportError("Forced PyMySQL on Vercel")
    import mysql.connector
    from mysql.connector.pooling import MySQLConnectionPool
    HAS_NATIVE_MYSQL = True
except (ImportError, Exception):
    import pymysql
    pymysql.install_as_MySQLdb()
    
    class MockConnection:
        def __init__(self, conn):
            self._conn = conn
            
        def cursor(self, dictionary=True):
            if dictionary:
                import pymysql.cursors
                return self._conn.cursor(pymysql.cursors.DictCursor)
            return self._conn.cursor()
            
        def commit(self):
            self._conn.commit()
            
        def rollback(self):
            self._conn.rollback()
            
        def close(self):
            self._conn.close()

    class MockMySQLConnectionPool:
        def __init__(self, pool_name, pool_size, **kwargs):
            self.config = kwargs
            
        def get_connection(self):
            import pymysql
            connect_kwargs = {
                "host": self.config.get("host", "localhost"),
                "user": self.config.get("user", "root"),
                "password": self.config.get("password", ""),
                "database": self.config.get("database", "chemlove"),
                "port": int(self.config.get("port", 3306)),
                "autocommit": False
            }
            # Enable SSL connection dynamically if ssl parameters are in config
            if any('ssl' in k.lower() for k in self.config.keys()):
                connect_kwargs["ssl"] = {}
                
            return MockConnection(pymysql.connect(**connect_kwargs))
            
    MySQLConnectionPool = MockMySQLConnectionPool
    HAS_NATIVE_MYSQL = False
from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, session, url_for, abort
from werkzeug.security import check_password_hash, generate_password_hash
from authlib.integrations.flask_client import OAuth
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import bleach
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

# Security Configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=__import__("datetime").timedelta(hours=2)
)

csrf = CSRFProtect(app)
talisman = Talisman(app, content_security_policy=None)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://"
)
ph = PasswordHasher()

@app.template_filter('clean_html')
def clean_html_filter(text):
    if text is None:
        return ""
    allowed_tags = ['p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'br', 'span', 'div', 'img']
    allowed_attrs = {'*': ['class', 'style'], 'a': ['href', 'target'], 'img': ['src', 'alt', 'width', 'height']}
    return bleach.clean(str(text), tags=allowed_tags, attributes=allowed_attrs)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# ── Database connection pool ────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

def parse_mysql_url(url):
    """Parse mysql://user:password@host:port/database URL using standard urllib.parse."""
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    
    # Extract database name (path without leading slash)
    database = parsed.path.lstrip('/')
    
    # Extract port
    port = parsed.port if parsed.port is not None else 3306
    
    config = {
        "host": parsed.hostname or "localhost",
        "port": port,
        "user": urllib.parse.unquote(parsed.username or "root"),
        "password": urllib.parse.unquote(parsed.password or ""),
        "database": database
    }
    
    # Parse query parameters (e.g. ssl-mode, ssl_ca)
    if parsed.query:
        query_params = urllib.parse.parse_qs(parsed.query)
        for k, v in query_params.items():
            if v:
                config[k] = v[0]
                
    return config

if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    try:
        db_config = parse_mysql_url(DATABASE_URL)
    except Exception as e:
        raise RuntimeError(f"Error parsing DATABASE_URL: {e}")
else:
    port_val = os.getenv("MYSQL_PORT")
    if port_val and port_val.strip():
        try:
            port = int(port_val)
        except ValueError:
            port = 3306
    else:
        port = 3306
        
    db_config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": port,
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "chemlove")
    }

if HAS_NATIVE_MYSQL:
    # Filter config for mysql.connector which raises error on unknown arguments (e.g. ssl-mode)
    valid_keys = {
        'host', 'port', 'user', 'password', 'database',
        'ssl_ca', 'ssl_cert', 'ssl_key', 'ssl_capath', 'ssl_cipher',
        'charset', 'collation', 'connection_timeout', 'autocommit',
        'pool_name', 'pool_size'
    }
    db_config = {k: v for k, v in db_config.items() if k in valid_keys}

# Perform bootstrap connection to ensure target database exists before creating the pool
try:
    target_db = db_config.get("database", "chemlove")
    bootstrap_config = db_config.copy()
    if "database" in bootstrap_config:
        del bootstrap_config["database"]
    
    if HAS_NATIVE_MYSQL:
        conn = mysql.connector.connect(**bootstrap_config)
    else:
        pymysql_config = {
            "host": bootstrap_config.get("host", "localhost"),
            "user": bootstrap_config.get("user", "root"),
            "password": bootstrap_config.get("password", ""),
            "port": int(bootstrap_config.get("port", 3306))
        }
        import pymysql
        conn = pymysql.connect(**pymysql_config)
        
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{target_db}`")
    cur.close()
    conn.close()
    print(f"[DATABASE] Verified or created database: {target_db}")
except Exception as e:
    print(f"[DATABASE] WARNING: Database bootstrap creation failed (might already exist or user lacks permission): {e}")

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
        try:
            self.conn = self.pool.get_connection()
            self.cursor = self.conn.cursor(dictionary=True)
            return self
        except Exception as e:
            global db_config
            configured_host = db_config.get("host", "localhost")
            if configured_host not in ("localhost", "127.0.0.1"):
                print(f"[DATABASE] Connection to remote host '{configured_host}' failed: {e}. Attempting local fallback...")
                try:
                    fallback_config = {
                        "host": "localhost",
                        "port": 3306,
                        "user": "root",
                        "password": "2518",
                        "database": db_config.get("database", "chemlove")
                    }
                    if HAS_NATIVE_MYSQL:
                        import mysql.connector
                        self.conn = mysql.connector.connect(**fallback_config)
                    else:
                        import pymysql
                        self.conn = MockConnection(pymysql.connect(**fallback_config))
                    self.cursor = self.conn.cursor(dictionary=True)
                    print("[DATABASE] Successfully fell back to local MySQL server.")
                    return self
                except Exception as fe:
                    print(f"[DATABASE] Local fallback connection failed: {fe}")
            raise e

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


def run_migration_on_startup():
    print("[MIGRATION] Starting startup migration...")
    tables = [
        "users",
        "courses",
        "chapters",
        "lessons",
        "experiments",
        "labs",
        "reactions",
        "quizzes",
        "assignments",
        "tests",
        "badges",
        "certificates",
        "announcements"
    ]
    import uuid
    try:
        with get_db() as conn:
            for table in tables:
                print(f"[MIGRATION] Processing table: {table}")
                tbl_check = conn.execute(f"SHOW TABLES LIKE '{table}'").fetchone()
                if not tbl_check:
                    print(f"[MIGRATION] Table '{table}' does not exist. Skipping.")
                    continue
                
                col_check = conn.execute(f"SHOW COLUMNS FROM `{table}` LIKE 'public_id'").fetchone()
                if not col_check:
                    print(f"[MIGRATION] Adding public_id column to '{table}'...")
                    conn.execute(f"ALTER TABLE `{table}` ADD COLUMN public_id VARCHAR(36) DEFAULT NULL")
                else:
                    print(f"[MIGRATION] public_id column already exists in '{table}'.")

                rows = conn.execute(f"SELECT * FROM `{table}`").fetchall()
                print(f"[MIGRATION] Found {len(rows)} records in '{table}'.")
                
                updated_count = 0
                for row in rows:
                    row_dict = dict(row)
                    if not row_dict.get("public_id"):
                        new_uuid = str(uuid.uuid4())
                        conn.execute(
                            f"UPDATE `{table}` SET public_id = %s WHERE id = %s",
                            (new_uuid, row_dict["id"])
                        )
                        updated_count += 1
                        
                if updated_count > 0:
                    print(f"[MIGRATION] Generated UUIDs for {updated_count} records.")
                else:
                    print("[MIGRATION] All records already have UUIDs.")
                    
                try:
                    conn.execute(f"ALTER TABLE `{table}` DROP INDEX `idx_{table}_public_id`")
                except Exception:
                    pass
                try:
                    conn.execute(f"ALTER TABLE `{table}` DROP INDEX `public_id`")
                except Exception:
                    pass
                    
                print(f"[MIGRATION] Enforcing NOT NULL UNIQUE constraints on '{table}'.public_id...")
                conn.execute(f"ALTER TABLE `{table}` MODIFY COLUMN public_id VARCHAR(36) NOT NULL")
                conn.execute(f"ALTER TABLE `{table}` ADD UNIQUE KEY `idx_{table}_public_id` (public_id)")
                print(f"[MIGRATION] Constraints and unique index successfully created on '{table}'.")
        print("[MIGRATION] Startup migration completed successfully!")
    except Exception as e:
        print(f"[MIGRATION] ERROR: Startup migration failed: {e}")

run_migration_on_startup()



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


def execute_sql_file(conn, filepath):
    """Executes a multi-statement SQL file using the wrapper connection."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    statements = []
    current_statement = []
    
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('--') or stripped.startswith('#'):
            continue
        
        current_statement.append(line)
        if stripped.endswith(';'):
            statements.append('\n'.join(current_statement))
            current_statement = []
            
    cursor = conn.conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for stmt in statements:
            stmt_stripped = stmt.strip()
            if stmt_stripped:
                cursor.execute(stmt_stripped)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.conn.commit()
    except Exception as e:
        conn.conn.rollback()
        raise e
    finally:
        cursor.close()

def init_db():
    """Verify MySQL database connection, auto-run schema.sql / seed.sql if empty, and ensure admin exists."""
    try:
        with get_db() as conn:
            cursor = conn.conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [list(r.values())[0] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
            cursor.close()
            
            if not tables or 'users' not in tables:
                print("[DATABASE] No tables found. Importing schema.sql...")
                execute_sql_file(conn, "schema.sql")
                print("[DATABASE] schema.sql imported successfully.")
                cursor = conn.conn.cursor()
                cursor.execute("SHOW TABLES")
                tables = [list(r.values())[0] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
                cursor.close()
            
            has_data = False
            if 'chapters' in tables:
                row = conn.execute("SELECT COUNT(*) as count FROM chapters").fetchone()
                if row and row['count'] > 0:
                    has_data = True
            
            if not has_data:
                print("[DATABASE] Seeding database using seed.sql...")
                execute_sql_file(conn, "seed.sql")
                print("[DATABASE] seed.sql imported successfully.")
            
            admin_row = conn.execute("SELECT * FROM users WHERE email = %s", ('admin@chemlove.com',)).fetchone()
            if not admin_row:
                print("[DATABASE] Creating default admin account...")
                hashed_pw = ph.hash("admin123")
                conn.execute(
                    """
                    INSERT INTO users (public_id, name, email, password_hash, institution, role, class_level, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (str(uuid.uuid4()), "Administrator", "admin@chemlove.com", hashed_pw, "ChemLove HQ", "admin", "all", "active")
                )
                print("[DATABASE] Default admin account (admin@chemlove.com / admin123) verified.")
                
            # Perform any incremental alterations if needed (V3/V4 Guided Learning schema columns check/additions)
            v3_columns = {
                "overview_content": "LONGTEXT NULL",
                "key_points_content": "LONGTEXT NULL",
                "formula_content": "LONGTEXT NULL",
                "reaction_content": "LONGTEXT NULL",
                "experiment_content": "LONGTEXT NULL",
                "practice_content": "LONGTEXT NULL"
            }
            for col, col_def in v3_columns.items():
                try:
                    conn.execute(f"ALTER TABLE chapters ADD COLUMN {col} {col_def}")
                except Exception:
                    pass

            v4_progress_cols = {
                "overview_completed":    "BOOLEAN DEFAULT FALSE",
                "keypoints_completed":   "BOOLEAN DEFAULT FALSE",
                "formulas_completed":    "BOOLEAN DEFAULT FALSE",
                "reactions_completed":   "BOOLEAN DEFAULT FALSE",
                "experiments_completed": "BOOLEAN DEFAULT FALSE",
                "practice_completed":    "BOOLEAN DEFAULT FALSE",
                "quiz_completed":        "BOOLEAN DEFAULT FALSE",
                "completion_percentage": "INT DEFAULT 0",
                "xp_earned":             "INT DEFAULT 0",
            }
            for col, col_def in v4_progress_cols.items():
                try:
                    conn.execute(f"ALTER TABLE chapter_progress ADD COLUMN {col} {col_def}")
                except Exception:
                    pass

            v5_notification_cols = {
                "target_role": "VARCHAR(50) DEFAULT 'all'",
                "target_institution": "VARCHAR(255) DEFAULT 'all'",
                "target_class_level": "VARCHAR(50) DEFAULT 'all'",
            }
            for col, col_def in v5_notification_cols.items():
                try:
                    conn.execute(f"ALTER TABLE notifications ADD COLUMN {col} {col_def}")
                except Exception:
                    pass
            
            try:
                conn.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(100) DEFAULT 'account_circle'")
            except Exception:
                pass

            # Auth security columns
            for col, col_def in [
                ("failed_login_attempts", "INT NOT NULL DEFAULT 0"),
                ("lockout_until", "TIMESTAMP NULL DEFAULT NULL"),
                ("last_login_at", "TIMESTAMP NULL DEFAULT NULL"),
                ("password_changed_at", "TIMESTAMP NULL DEFAULT NULL")
            ]:
                try:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {col} {col_def}")
                except Exception:
                    pass
            
        print("[DATABASE] MySQL connection and database distribution bootstrap checked successfully.")
    except Exception as e:
        print(f"[DATABASE] ERROR: Startup database bootstrap failed: {e}")


# Database initialization deferred to before_request to prevent block during serverless imports
_db_initialized = False

@app.before_request
def maybe_init_db():
    global _db_initialized
    if not _db_initialized:
        if request.path.startswith('/static/') or request.path in ('/favicon.ico', '/favicon.png'):
            return
        _db_initialized = True
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



def get_access_mode():
    try:
        with get_db() as conn:
            row = conn.execute("SELECT access_mode FROM schools LIMIT 1").fetchone()
            if row:
                return row['access_mode']
    except Exception:
        pass
    return 'STRICT'


def check_in_version(content_type, content_id, title, content_data, user_id):
    try:
        with get_db() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(version_number), 0) AS max_v FROM content_versions WHERE content_type = %s AND content_id = %s",
                (content_type, content_id)
            ).fetchone()
            next_v = (row['max_v'] or 0) + 1
            
            conn.execute(
                """
                INSERT INTO content_versions (content_type, content_id, version_number, title, content_data, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (content_type, content_id, next_v, title, json.dumps(content_data), user_id)
            )
            
            # Update current version in primary table
            if content_type == 'course':
                conn.execute("UPDATE courses SET version = %s WHERE id = %s", (next_v, content_id))
            elif content_type == 'chapter':
                conn.execute("UPDATE chapters SET version = %s WHERE id = %s", (next_v, content_id))
            elif content_type == 'lesson':
                conn.execute("UPDATE lessons SET version = %s WHERE id = %s", (next_v, content_id))
        return next_v
    except Exception as e:
        import traceback
        try:
            with open("d:/Aman/Tools/Chemlove/v2/version_error.log", "a") as f:
                f.write(f"Error checking in version (type={content_type}, id={content_id}, user_id={user_id}): {e}\n")
                traceback.print_exc(file=f)
        except Exception:
            pass
        print(f"Error checking in version: {e}")
        return 1


def all_chapters():
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM chapters ORDER BY chapter_number ASC").fetchall()
        return [parse_chapter_json_fields(row) for row in rows]
    except Exception as e:
        print(f"Error fetching chapters: {e}")
        return []


def get_chapter(chapter_identifier):
    try:
        with get_db() as conn:
            if isinstance(chapter_identifier, int) or (isinstance(chapter_identifier, str) and chapter_identifier.isdigit()):
                row = conn.execute("SELECT * FROM chapters WHERE id = %s", (chapter_identifier,)).fetchone()
            else:
                row = conn.execute("SELECT * FROM chapters WHERE public_id = %s", (chapter_identifier,)).fetchone()
        return parse_chapter_json_fields(row) if row else None
    except Exception as e:
        print(f"Error fetching chapter {chapter_identifier}: {e}")
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


def get_badge(badge_identifier):
    try:
        with get_db() as conn:
            if isinstance(badge_identifier, int) or (isinstance(badge_identifier, str) and badge_identifier.isdigit()):
                row = conn.execute("SELECT * FROM badges WHERE id = %s", (badge_identifier,)).fetchone()
            else:
                row = conn.execute("SELECT * FROM badges WHERE public_id = %s", (badge_identifier,)).fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error fetching badge {badge_identifier}: {e}")
        return None


def all_experiments():
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM experiments ORDER BY id ASC").fetchall()
        return [parse_experiment_json_fields(row) for row in rows]
    except Exception as e:
        print(f"Error fetching experiments: {e}")
        return []


def get_experiment(experiment_identifier):
    try:
        with get_db() as conn:
            if isinstance(experiment_identifier, int) or (isinstance(experiment_identifier, str) and experiment_identifier.isdigit()):
                row = conn.execute("SELECT * FROM experiments WHERE id = %s", (experiment_identifier,)).fetchone()
            else:
                row = conn.execute("SELECT * FROM experiments WHERE public_id = %s", (experiment_identifier,)).fetchone()
        return parse_experiment_json_fields(row) if row else None
    except Exception as e:
        print(f"Error fetching experiment {experiment_identifier}: {e}")
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


def get_quiz(chapter_identifier):
    try:
        chapter_data = get_chapter(chapter_identifier)
        if not chapter_data:
            return None
        chapter_id = chapter_data['id']
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
        
        q_dict['chapter'] = chapter_data['title']
        q_dict['questions'] = enriched_questions
        return q_dict
    except Exception as e:
        print(f"Error fetching quiz for chapter {chapter_identifier}: {e}")
        return None



# ── Level Progression & Gamification Details ────────────────────────────────
def get_level_info(xp):
    levels = [
        {"level": 1, "title": "Beginner", "min_xp": 0, "max_xp": 500},
        {"level": 2, "title": "Explorer", "min_xp": 501, "max_xp": 1200},
        {"level": 3, "title": "Achiever", "min_xp": 1201, "max_xp": 2200},
        {"level": 4, "title": "Innovator", "min_xp": 2201, "max_xp": 3500},
        {"level": 5, "title": "Expert", "min_xp": 3501, "max_xp": 5000},
        {"level": 6, "title": "Master", "min_xp": 5001, "max_xp": 999999}
    ]
    for i, lvl in enumerate(levels):
        if lvl["min_xp"] <= xp <= lvl["max_xp"]:
            if i == len(levels) - 1:
                percent = 100
                next_xp = xp
            else:
                range_xp = lvl["max_xp"] - lvl["min_xp"]
                earned_in_level = xp - lvl["min_xp"]
                percent = min(100, max(0, int((earned_in_level / range_xp) * 100)))
                next_xp = lvl["max_xp"] + 1
            return {
                "level": lvl["level"],
                "title": lvl["title"],
                "percent": percent,
                "next_xp": next_xp,
                "current_level_min": lvl["min_xp"],
                "current_level_max": lvl["max_xp"]
            }
    return {"level": 1, "title": "Beginner", "percent": 0, "next_xp": 501}


def check_and_update_streak(user_id, conn):
    today = date.today()
    sp = conn.execute(
        "SELECT current_xp, streak_count, last_active_date FROM student_profiles WHERE user_id = %s",
        (user_id,)
    ).fetchone()
    if not sp:
        return
    
    current_xp = sp["current_xp"]
    streak = sp.get("streak_count", 0)
    last_date = sp.get("last_active_date")
    
    if isinstance(last_date, str):
        try:
            last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
        except:
            last_date = None
    elif isinstance(last_date, datetime):
        last_date = last_date.date()
            
    # If last_active_date is today, do nothing
    if last_date == today:
        return
        
    xp_gained = 0
    new_streak = streak
    
    if last_date is None:
        new_streak = 1
        xp_gained = 10  # Daily login XP
    elif (today - last_date).days == 1:
        new_streak = streak + 1
        xp_gained = 10  # Daily login XP
        # Milestone check
        if new_streak >= 7:
            # Check if badge already unlocked
            existing_badge = conn.execute(
                "SELECT id FROM user_badges WHERE user_id = %s AND badge_id = 2",
                (user_id,)
            ).fetchone()
            if not existing_badge:
                conn.execute(
                    "INSERT IGNORE INTO user_badges (user_id, badge_id, unlocked_at) VALUES (%s, 2, NOW())",
                    (user_id,)
                )
                xp_gained += 100  # Consistency Champion reward
    else:
        new_streak = 1
        xp_gained = 10  # Daily login XP
        
    # Calculate new level
    new_xp = current_xp + xp_gained
    lvl_info = get_level_info(new_xp)
    new_lvl = lvl_info["level"]
    
    conn.execute(
        """
        UPDATE student_profiles 
        SET current_xp = %s, level = %s, streak_count = %s, last_active_date = %s 
        WHERE user_id = %s
        """,
        (new_xp, new_lvl, new_streak, today, user_id)
    )
    if xp_gained > 0:
        conn.execute(
            "INSERT INTO user_history(user_id, event_type, event_data, created_at) VALUES (%s, 'daily_login', %s, NOW())",
            (user_id, f"xp_gained={xp_gained}, streak={new_streak}")
        )


def check_and_award_badges(user_id, conn):
    # Check Top Performer: rank #1
    u_row = conn.execute("SELECT class_level FROM users WHERE id = %s", (user_id,)).fetchone()
    if u_row and u_row["class_level"]:
        top_student = conn.execute(
            """
            SELECT sp.user_id
            FROM student_profiles sp
            JOIN users u ON sp.user_id = u.id
            WHERE u.class_level = %s
            ORDER BY sp.current_xp DESC LIMIT 1
            """,
            (u_row["class_level"],)
        ).fetchone()
        if top_student and top_student["user_id"] == user_id:
            conn.execute("INSERT IGNORE INTO user_badges (user_id, badge_id, unlocked_at) VALUES (%s, 1, NOW())", (user_id,))
            
    # Check Fast Learner: got 100% on a quiz
    fast_learner = conn.execute(
        """
        SELECT ta.id FROM test_attempts ta
        JOIN tests t ON ta.test_id = t.id
        WHERE ta.student_id = %s AND ta.score = t.total_marks
        """,
        (user_id,)
    ).fetchone()
    if fast_learner:
        conn.execute("INSERT IGNORE INTO user_badges (user_id, badge_id, unlocked_at) VALUES (%s, 3, NOW())", (user_id,))
        
    # Check Assessment Master: completed 5 quizzes
    completed_quizzes = conn.execute(
        "SELECT COUNT(*) as c FROM test_attempts WHERE student_id = %s AND score IS NOT NULL",
        (user_id,)
    ).fetchone()
    if completed_quizzes and completed_quizzes["c"] >= 5:
        conn.execute("INSERT IGNORE INTO user_badges (user_id, badge_id, unlocked_at) VALUES (%s, 4, NOW())", (user_id,))
        
    # Check Lab Expert: completed 3 experiments
    completed_labs = conn.execute(
        """
        SELECT COUNT(DISTINCT event_data) as c FROM user_history
        WHERE user_id = %s AND event_type IN ('titration_complete', 'reaction_success')
        """,
        (user_id,)
    ).fetchone()
    if completed_labs and completed_labs["c"] >= 3:
        conn.execute("INSERT IGNORE INTO user_badges (user_id, badge_id, unlocked_at) VALUES (%s, 5, NOW())", (user_id,))


# ── User helpers ───────────────────────────────────────────────────────────
def user_from_row(row):
    return {
        "id":          row["id"],
        "name":        row["name"],
        "email":       row["email"],
        "institution": row["institution"],
        "school":      row["institution"],
        "role":        row["role"],
        "status":      row.get("status", "active"),
        "classLevel":  row.get("class_level"),
        "student_class": row.get("class_level"),
        "mobile":      row.get("mobile"),
        "avatar":      row.get("avatar", "account_circle"),
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
            check_and_update_streak(user_id, conn)
            check_and_award_badges(user_id, conn)
            
            sp = conn.execute(
                """
                SELECT current_xp, level, streak_count, last_active_date, 
                       last_chapter_id, last_experiment_id, last_assessment_id 
                FROM student_profiles WHERE user_id = %s
                """,
                (user_id,)
            ).fetchone()
            
            user_dict["current_xp"] = sp["current_xp"] if sp else 100
            user_dict["level"]      = sp["level"]      if sp else 1
            user_dict["streak_count"] = sp["streak_count"] if sp else 0
            user_dict["last_active_date"] = str(sp["last_active_date"]) if sp and sp["last_active_date"] else None
            user_dict["last_chapter_id"] = sp["last_chapter_id"] if sp else None
            user_dict["last_experiment_id"] = sp["last_experiment_id"] if sp else None
            user_dict["last_assessment_id"] = sp["last_assessment_id"] if sp else None
            
            # Dynamically calculate class-specific rank
            rank_row = conn.execute(
                """
                SELECT rnk FROM (
                    SELECT user_id, RANK() OVER (ORDER BY current_xp DESC) as rnk
                    FROM student_profiles sp
                    JOIN users u ON sp.user_id = u.id
                    WHERE u.class_level = %s
                ) ranks WHERE user_id = %s
                """,
                (user_dict["classLevel"], user_id)
            ).fetchone()
            user_dict["rank"] = rank_row["rnk"] if rank_row else 1
            
            # Calculate Level details
            lvl_info = get_level_info(user_dict["current_xp"])
            user_dict["achievement_level"] = lvl_info["title"]
            user_dict["level_progress"] = lvl_info["percent"]
            user_dict["next_level_xp"] = lvl_info["next_xp"]

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


def content_manager_or_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        if user['role'] not in ('admin', 'content_manager'):
            flash('Unauthorized access. Content Manager or Admin role required.', 'error')
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

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('img/favicon.png')


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
@limiter.limit("5 per minute")
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

        if role == 'teacher':
            submitted_code = request.form.get('teacherAccessCode', '').strip()
            expected_code = os.getenv("TEACHER_ACCESS_CODE", "CHEM2K26V3").strip()
            if submitted_code != expected_code:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
                    return jsonify({
                        "success": False,
                        "message": "Invalid Teacher Access Code"
                    }), 403
                flash('Invalid Teacher Access Code.', 'error')
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
                INSERT INTO users(public_id, name, email, password_hash, institution, role, class_level, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', NOW(), NOW())
                """,
                (str(uuid.uuid4()), name, email, ph.hash(password), institution, role,
                 class_level if role == 'student' else None),
            )
            user_id = cursor.lastrowid
            
            conn.execute("INSERT INTO user_history (user_id, event_type, event_data) VALUES (%s, %s, %s)",
                         (user_id, 'registration', json.dumps({'role': role, 'ip': request.remote_addr})))


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
@limiter.limit("10 per minute")
def login():
    user = get_current_user()
    if user:
        return redirect_by_role(user)

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = %s", (email,)).fetchone()

        if not user:
            try:
                ph.hash(password)
            except Exception:
                pass
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

        # Check lockout
        if user.get('lockout_until') and user['lockout_until'] > datetime.now(timezone.utc).replace(tzinfo=None):
            flash('Account is locked due to multiple failed login attempts. Try again later.', 'error')
            return redirect(url_for('login'))

        valid = False
        try:
            valid = ph.verify(user['password_hash'], password)
            if ph.check_needs_rehash(user['password_hash']):
                with get_db() as conn:
                    conn.execute("UPDATE users SET password_hash = %s WHERE id = %s", (ph.hash(password), user['id']))
        except VerifyMismatchError:
            valid = False
        except Exception:
            # Fallback for PBKDF2 (Werkzeug default) Migration
            if check_password_hash(user['password_hash'], password):
                valid = True
                with get_db() as conn:
                    conn.execute("UPDATE users SET password_hash = %s WHERE id = %s", (ph.hash(password), user['id']))

        if not valid:
            with get_db() as conn:
                failed = user.get('failed_login_attempts', 0) + 1
                lockout = datetime.now(timezone.utc).replace(tzinfo=None) + __import__("datetime").timedelta(minutes=15) if failed >= 5 else None
                conn.execute("UPDATE users SET failed_login_attempts = %s, lockout_until = %s WHERE id = %s", (failed, lockout, user['id']))
                conn.execute("INSERT INTO audit_logs (user_id, action, details) VALUES (%s, %s, %s)", (user['id'], 'failed_login', json.dumps({'ip': request.remote_addr})))
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

        if user.get('status') == 'suspended':
            flash('This account has been suspended. Please contact the administrator.', 'error')
            return redirect(url_for('login'))

        with get_db() as conn:
            conn.execute("UPDATE users SET failed_login_attempts = 0, lockout_until = NULL, last_login_at = %s WHERE id = %s", (datetime.now(timezone.utc).replace(tzinfo=None), user['id']))

        session.clear() # Prevent session fixation
        session['user_id'] = user['id']
        session.permanent = True
        add_history(user['id'], "login_success")
        flash('Login successful.', 'success')
        return redirect_by_role(user)

    return render_template('landing/auth.html', active_form='login')


@app.route('/auth/verify-teacher-code', methods=['POST'])
def verify_teacher_code():
    data = request.get_json(silent=True) or {}
    code = data.get('code', '').strip()
    expected = os.getenv("TEACHER_ACCESS_CODE", "CHEM2K26V3").strip()
    return jsonify({"valid": code == expected})


@app.route('/auth/google')
def auth_google():
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        return redirect(url_for('auth_google_mock'))
    
    redirect_uri = url_for('auth_google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/mock')
def auth_google_mock():
    return render_template('landing/google_mock.html')


@app.route('/auth/google/callback')
def auth_google_callback():
    # Handle both simulated mock profile Choice and real Google OAuth redirect
    mock_profile = request.args.get('mock_profile', '')
    
    email = ""
    name = ""
    role_hint = "student"
    
    if mock_profile:
        if mock_profile == 'student':
            email = 'alex.r@chemlove.com'
            name = 'Alex Rivera'
            role_hint = 'student'
        elif mock_profile == 'teacher':
            email = 'sarah.j@chemlove.edu'
            name = 'Dr. Sarah Jenkins'
            role_hint = 'teacher'
        elif mock_profile == 'admin':
            email = 'admin@chemlove.com'
            name = 'Admin Owner'
            role_hint = 'admin'
        elif mock_profile == 'custom':
            email = request.args.get('email', '').strip().lower()
            name = request.args.get('name', '').strip()
            role_hint = request.args.get('role', 'student').strip()
    else:
        client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
        if not client_id:
            flash("Google Authentication is not configured.", "error")
            return redirect(url_for('login'))
        
        try:
            token = google.authorize_access_token()
            user_info = token.get('userinfo')
            if not user_info:
                raise ValueError("No userinfo found in OAuth token response.")
            
            email = user_info.get('email', '').strip().lower()
            name = user_info.get('name', '').strip()
            
        except Exception as e:
            flash(f"Google Authentication failed: {str(e)}", "error")
            return redirect(url_for('login'))
    
    if not email:
        flash("Google account does not expose a valid email address.", "error")
        return redirect(url_for('login'))
        
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = %s", (email,)).fetchone()
        
    if user:
        if user.get('status') == 'suspended':
            flash('This account has been suspended. Please contact the administrator.', 'error')
            return redirect(url_for('login'))
        
        session['user_id'] = user['id']
        add_history(user['id'], "google_login_success")
        flash('Login successful via Google.', 'success')
        return redirect_by_role(user)
    else:
        # Redirect new Google users to complete profiles
        session['google_auth_pending'] = {
            'email': email,
            'name': name,
            'role_hint': role_hint
        }
        return redirect(url_for('auth_google_finish'))


@app.route('/auth/google/finish', methods=['GET', 'POST'])
def auth_google_finish():
    pending = session.get('google_auth_pending')
    if not pending:
        flash("No pending authentication session found.", "error")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        role = request.form.get('role', '').strip()
        institution = request.form.get('institution', '').strip()
        class_level = request.form.get('classLevel', '').strip()
        
        if not role or not institution:
            flash("Institution and Role are required.", "error")
            return render_template('landing/google_finish.html', email=pending['email'], name=pending['name'], role_hint=pending.get('role_hint', 'student'))
            
        if role == 'student' and not class_level:
            flash("Class level is required for student profiles.", "error")
            return render_template('landing/google_finish.html', email=pending['email'], name=pending['name'], role_hint=pending.get('role_hint', 'student'))
            
        if role == 'teacher':
            submitted_code = request.form.get('teacherAccessCode', '').strip()
            expected_code = os.getenv("TEACHER_ACCESS_CODE", "CHEM2K26V3").strip()
            if submitted_code != expected_code:
                flash("Invalid Teacher Access Code.", "error")
                return render_template('landing/google_finish.html', email=pending['email'], name=pending['name'], role_hint=pending.get('role_hint', 'student'))
        
        import secrets
        rand_pass = secrets.token_hex(24)
        
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users(public_id, name, email, password_hash, institution, role, class_level, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', NOW(), NOW())
                """,
                (str(uuid.uuid4()), pending['name'], pending['email'], generate_password_hash(rand_pass), institution, role,
                 class_level if role == 'student' else None)
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
            
        session.pop('google_auth_pending', None)
        session['user_id'] = user_id
        add_history(user_id, "google_signup_success", f"role={role}")
        flash('Account created successfully via Google.', 'success')
        return redirect_by_role(user_row)
        
    return render_template('landing/google_finish.html', email=pending['email'], name=pending['name'], role_hint=pending.get('role_hint', 'student'))


@app.route('/logout', methods=['POST'])
def logout():
    user_id = session.get("user_id")
    if user_id:
        add_history(user_id, "logout")
    session.pop('user_id', None)
    session.pop('impersonator_user_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/admin/impersonate/<string:target_uuid>')
@admin_required
def admin_impersonate(target_uuid):
    if target_uuid.isdigit():
        with get_db() as conn:
            target_user = conn.execute("SELECT public_id FROM users WHERE id = %s", (target_uuid,)).fetchone()
            if target_user:
                return redirect(url_for('admin_impersonate', target_uuid=target_user['public_id']), code=301)

    with get_db() as conn:
        target_user = conn.execute("SELECT * FROM users WHERE public_id = %s", (target_uuid,)).fetchone()
    
    if not target_user:
        flash("Target user not found.", "error")
        return redirect(url_for('admin_dashboard'))
    
    if target_user["role"] == "admin":
        flash("Cannot impersonate another Admin account.", "error")
        return redirect(url_for('admin_dashboard'))

    admin_id = session.get("user_id")
    session["impersonator_user_id"] = admin_id
    session["user_id"] = target_user["id"]

    log_audit("impersonate_user", f"Admin impersonating {target_user['name']} (ID: {target_user['id']})")
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
        
    badges = []
    certs = []
    enrollments = []
    history = []
    
    try:
        with get_db() as conn:
            # 1. Fetch user badges
            badge_rows = conn.execute(
                "SELECT badge_id, unlocked_at FROM user_badges WHERE user_id = %s ORDER BY unlocked_at DESC",
                (user['id'],)
            ).fetchall()
            for r in badge_rows:
                meta = get_badge(r["badge_id"])
                if meta:
                    badges.append({**meta, "unlocked_at": str(r["unlocked_at"])})
                    
            # 2. Fetch user certificates
            cert_rows = conn.execute(
                """
                SELECT c.*, cr.title as course_title, cr.description
                FROM certificates c
                JOIN courses cr ON c.course_id = cr.id
                WHERE c.student_id = %s AND c.status = 'issued'
                ORDER BY c.issued_at DESC
                """,
                (user['id'],)
            ).fetchall()
            for r in cert_rows:
                c_dict = dict(r)
                if isinstance(c_dict.get('issued_at'), datetime):
                    c_dict['issued_at'] = c_dict['issued_at'].strftime('%B %d, %Y')
                certs.append(c_dict)
                
            # 3. Fetch course enrollments
            enroll_rows = conn.execute(
                """
                SELECT ce.*, c.title as course_title, c.category
                FROM course_enrollments ce
                JOIN courses c ON ce.course_id = c.id
                WHERE ce.student_id = %s
                """,
                (user['id'],)
            ).fetchall()
            enrollments = [dict(e) for e in enroll_rows]
            
            # 4. Fetch activity timeline
            hist_rows = conn.execute(
                "SELECT event_type, event_data, created_at FROM user_history WHERE user_id = %s ORDER BY id DESC LIMIT 50",
                (user['id'],)
            ).fetchall()
            for r in hist_rows:
                h_dict = dict(r)
                if isinstance(h_dict.get('created_at'), datetime):
                    h_dict['created_at'] = h_dict['created_at'].strftime('%b %d, %Y %I:%M %p')
                history.append(h_dict)
    except Exception as e:
        print(f"Error compiling profile page context: {e}")
        
    return render_template(
        'student/profile.html', 
        current_user=user, 
        badges=badges, 
        certificates=certs, 
        enrollments=enrollments, 
        history=history, 
        active_tab='profile'
    )


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
    mobile      = payload.get("mobile")
    avatar      = payload.get("avatar") or user.get("avatar", "account_circle")

    with get_db() as conn:
        conn.execute(
            "UPDATE users SET name = %s, institution = %s, class_level = %s, mobile = %s, avatar = %s, updated_at = NOW() WHERE id = %s",
            (name, institution, class_level, mobile, avatar, user["id"]),
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
    user = get_current_user()
    class_level = user['classLevel']
    
    # 1. Fetch continue learning targets
    last_chapter = get_chapter(user['last_chapter_id']) if user.get('last_chapter_id') else None
    last_experiment = get_experiment(user['last_experiment_id']) if user.get('last_experiment_id') else None
    
    last_assessment = None
    if user.get('last_assessment_id'):
        try:
            with get_db() as conn:
                q_row = conn.execute("SELECT q.id, q.title, q.chapter_id, c.public_id AS chapter_public_id FROM quizzes q JOIN chapters c ON q.chapter_id = c.id WHERE q.id = %s", (user['last_assessment_id'],)).fetchone()
                if q_row:
                    last_assessment = dict(q_row)
        except Exception as e:
            print(f"Error loading last assessment: {e}")
            
    # 2. Fetch Class Roadmap (modules -> chapters -> lessons -> quizzes)
    roadmap = []
    try:
        with get_db() as conn:
            courses = conn.execute("SELECT id FROM courses WHERE class_level = %s AND status = 'active'", (class_level,)).fetchall()
            course_ids = [c['id'] for c in courses]
            
            if course_ids:
                format_strings = ','.join(['%s'] * len(course_ids))
                mods = conn.execute(
                    f"SELECT id, title, course_id FROM modules WHERE course_id IN ({format_strings}) ORDER BY order_index ASC",
                    tuple(course_ids)
                ).fetchall()
                mod_ids = [m['id'] for m in mods]
                
                if mod_ids:
                    format_strings_mods = ','.join(['%s'] * len(mod_ids))
                    chaps = conn.execute(
                        f"SELECT id, title, chapter_number, public_id, module_id FROM chapters WHERE module_id IN ({format_strings_mods}) ORDER BY chapter_number ASC",
                        tuple(mod_ids)
                    ).fetchall()
                    chap_ids = [ch['id'] for ch in chaps]
                    
                    if chap_ids:
                        format_strings_chaps = ','.join(['%s'] * len(chap_ids))
                        
                        lessons_rows = conn.execute(
                            f"SELECT id, title, chapter_id FROM lessons WHERE chapter_id IN ({format_strings_chaps}) AND status = 'published' ORDER BY order_index ASC",
                            tuple(chap_ids)
                        ).fetchall()
                        
                        quizzes_rows = conn.execute(
                            f"SELECT id, title, public_id, chapter_id FROM quizzes WHERE chapter_id IN ({format_strings_chaps})",
                            tuple(chap_ids)
                        ).fetchall()
                        
                        read_events = conn.execute(
                            "SELECT event_data FROM user_history WHERE user_id = %s AND event_type = 'read_notes'",
                            (user['id'],)
                        ).fetchall()
                        
                        import re
                        completed_lessons = set()
                        for ev in read_events:
                            ev_data = ev['event_data'] or ""
                            m_match = re.search(r"lesson_id=(\d+)", ev_data)
                            if m_match:
                                completed_lessons.add(int(m_match.group(1)))
                                
                        attempts_rows = conn.execute(
                            f"SELECT ta.score, t.chapter_id FROM test_attempts ta JOIN tests t ON ta.test_id = t.id WHERE ta.student_id = %s AND t.chapter_id IN ({format_strings_chaps})",
                            (user['id'],) + tuple(chap_ids)
                        ).fetchall()
                        
                        scores_by_chapter = {att['chapter_id']: att['score'] for att in attempts_rows}
                        
                        lessons_by_chapter = {}
                        for ls in lessons_rows:
                            ls_dict = dict(ls)
                            ch_id = ls_dict['chapter_id']
                            if ch_id not in lessons_by_chapter:
                                lessons_by_chapter[ch_id] = []
                            completed = ls_dict['id'] in completed_lessons
                            lessons_by_chapter[ch_id].append({**ls_dict, "completed": completed})
                            
                        quizzes_by_chapter = {q['chapter_id']: dict(q) for q in quizzes_rows}
                        
                        for ch in chaps:
                            ch_id = ch['id']
                            ch_lessons = lessons_by_chapter.get(ch_id, [])
                            qz = quizzes_by_chapter.get(ch_id, None)
                            
                            comp_lessons_count = sum(1 for ls in ch_lessons if ls['completed'])
                            ch_completed = (len(ch_lessons) > 0 and comp_lessons_count == len(ch_lessons))
                            
                            quiz_score = scores_by_chapter.get(ch_id, None)
                            quiz_completed = quiz_score is not None
                            
                            roadmap.append({
                                "chapter_id": ch_id,
                                "chapter_uuid": ch['public_id'],
                                "chapter_title": ch['title'],
                                "chapter_number": ch['chapter_number'],
                                "lessons": ch_lessons,
                                "quiz": qz,
                                "quiz_completed": quiz_completed,
                                "quiz_score": quiz_score,
                                "completed": ch_completed
                            })
    except Exception as e:
        print(f"Error compiling roadmap: {e}")
        
    return render_template(
        'student/dashboard.html', 
        current_user=user, 
        last_chapter=last_chapter,
        last_experiment=last_experiment,
        last_assessment=last_assessment,
        roadmap=roadmap,
        active_tab='dashboard'
    )


@app.route('/student/chapters')
@student_required
def student_chapters():
    user = get_current_user()
    user_class = user['classLevel']
    
    # Determine access mode
    access_mode = get_access_mode()
    
    # Allow filtering by query parameter if access_mode is EXPLORE or OPEN
    selected_class = request.args.get('class_level', user_class)
    if access_mode == 'STRICT':
        selected_class = user_class
        
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM chapters 
            WHERE class_level = %s 
              AND status = 'published' 
              AND (publish_at IS NULL OR publish_at <= NOW())
            ORDER BY chapter_number ASC
            """,
            (selected_class,)
        ).fetchall()
    chapters = [parse_chapter_json_fields(row) for row in rows]
    
    if chapters:
        chap_ids = [ch['id'] for ch in chapters]
        format_strings_chaps = ','.join(['%s'] * len(chap_ids))
        try:
            with get_db() as conn:
                lessons_rows = conn.execute(
                    f"SELECT id, chapter_id FROM lessons WHERE chapter_id IN ({format_strings_chaps}) AND status = 'published'",
                    tuple(chap_ids)
                ).fetchall()
                
                read_events = conn.execute(
                    "SELECT event_data FROM user_history WHERE user_id = %s AND event_type = 'read_notes'",
                    (user['id'],)
                ).fetchall()
                
            import re
            completed_lessons = set()
            for ev in read_events:
                ev_data = ev['event_data'] or ""
                m_match = re.search(r"lesson_id=(\d+)", ev_data)
                if m_match:
                    completed_lessons.add(int(m_match.group(1)))
                    
            lessons_by_chapter = {}
            for ls in lessons_rows:
                ch_id = ls['chapter_id']
                if ch_id not in lessons_by_chapter:
                    lessons_by_chapter[ch_id] = []
                lessons_by_chapter[ch_id].append(ls['id'])
                
            completed_chapters = {}
            for ch in chapters:
                ch_id = ch['id']
                ch_lessons = lessons_by_chapter.get(ch_id, [])
                if len(ch_lessons) > 0:
                    ch_completed = all(lid in completed_lessons for lid in ch_lessons)
                else:
                    ch_completed = False
                completed_chapters[ch_id] = ch_completed
                
            for i, ch in enumerate(chapters):
                if i == 0:
                    ch["locked"] = False
                else:
                    prev_ch = chapters[i-1]
                    ch["locked"] = not completed_chapters.get(prev_ch["id"], False)
        except Exception as e:
            print(f"Error checking chapter lock/unlock: {e}")
            for ch in chapters:
                ch["locked"] = False
                
    return render_template('student/chapters.html', current_user=user, chapters=chapters, selected_class=selected_class, active_tab='chapters')


@app.route('/student/chapter/<string:chapter_uuid>')
@student_required
def student_chapter_view(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_view', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_chapters'))
        
    # Check status and scheduling
    is_published = chapter_data.get('status') == 'published'
    publish_at_str = chapter_data.get('publish_at')
    is_scheduled = False
    if publish_at_str:
        pub_time = datetime.fromisoformat(str(publish_at_str)) if isinstance(publish_at_str, str) else publish_at_str
        if pub_time.tzinfo:
            is_scheduled = pub_time > datetime.now(timezone.utc)
        else:
            is_scheduled = pub_time > datetime.now()
            
    if not is_published or is_scheduled:
        flash('This chapter is not available yet.', 'error')
        return redirect(url_for('student_chapters'))
        
    access_mode = get_access_mode()
    if access_mode == 'STRICT' and chapter_data['class_level'] != user['classLevel']:
        flash('Unauthorized chapter access.', 'error')
        return redirect(url_for('student_chapters'))
        
    chapter_id = chapter_data['id']
    # Update last opened chapter
    try:
        with get_db() as conn:
            conn.execute("UPDATE student_profiles SET last_chapter_id = %s WHERE user_id = %s", (chapter_id, user['id']))
    except Exception as e:
        print(f"Error updating last chapter tracking: {e}")
        
    # Calculate progress percentage dynamically
    chapter_progress_percent = 0
    try:
        with get_db() as conn:
            # Check if explicitly completed in chapter_progress
            progress_rec = conn.execute("SELECT is_completed FROM chapter_progress WHERE user_id = %s AND chapter_id = %s", (user["id"], chapter_id)).fetchone()
            if progress_rec and progress_rec["is_completed"]:
                chapter_progress_percent = 100
            else:
                # Count total lessons in this chapter
                total_lessons = conn.execute("SELECT COUNT(*) FROM lessons WHERE chapter_id = %s AND status = 'published'", (chapter_id,)).fetchone()
                total_count = total_lessons[0] if total_lessons else 0
                
                if total_count > 0:
                    # Count completed lessons by student
                    completed_lessons = conn.execute("""
                        SELECT COUNT(DISTINCT lp.lesson_id) 
                        FROM lesson_progress lp
                        JOIN lessons l ON lp.lesson_id = l.id
                        WHERE lp.user_id = %s AND l.chapter_id = %s AND lp.is_completed = TRUE
                    """, (user["id"], chapter_id)).fetchone()
                    completed_count = completed_lessons[0] if completed_lessons else 0
                    
                    chapter_progress_percent = min(100, round((completed_count / total_count) * 100))
                else:
                    chapter_progress_percent = 0
    except Exception as e:
        print(f"Error calculating chapter progress: {e}")

    state = get_chapter_v4_state(user['id'], chapter_id)
        
    return render_template('student/chapter_view.html', 
                           current_user=user, 
                           chapter_data=chapter_data, 
                           chapter_progress_percent=chapter_progress_percent,
                           state=state,
                           active_tab='chapters')


@app.route('/api/student/chapter/complete', methods=['POST'])
@student_required
def api_student_chapter_complete():
    user = get_current_user()
    payload = request.get_json(silent=True) or {}
    chapter_id = payload.get("chapter_id")
    
    if not chapter_id:
        return jsonify({"error": "Missing chapter_id"}), 400
        
    try:
        with get_db() as conn:
            exists = conn.execute("SELECT * FROM chapter_progress WHERE user_id = %s AND chapter_id = %s", (user["id"], chapter_id)).fetchone()
            if exists:
                conn.execute("UPDATE chapter_progress SET is_completed = TRUE, completed_at = NOW() WHERE user_id = %s AND chapter_id = %s", (user["id"], chapter_id))
            else:
                conn.execute("INSERT INTO chapter_progress (user_id, chapter_id, is_completed, completed_at) VALUES (%s, %s, TRUE, NOW())", (user["id"], chapter_id))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_chapter_mastery(user_id, chapter_id):
    chapter_data = get_chapter(chapter_id)
    if not chapter_data:
        return {"mastery_percent": 0, "checklist": {}, "active_sections": [], "empty_sections": []}
        
    quiz_data = get_quiz(chapter_id)
    
    sections = {
        "overview": bool(chapter_data.get("overview_content") or chapter_data.get("notes")),
        "keypoints": bool(chapter_data.get("key_points_content") or chapter_data.get("key_points")),
        "formulas": bool(chapter_data.get("formula_content") or chapter_data.get("formulas")),
        "reactions": bool(chapter_data.get("reaction_content") or chapter_data.get("reactions")),
        "experiments": bool(chapter_data.get("experiment_content")),
        "practice": bool(chapter_data.get("practice_content") or chapter_data.get("practice_questions")),
        "quiz": bool(quiz_data)
    }
    
    default_weights = {
        "overview": 10,
        "keypoints": 15,
        "formulas": 15,
        "reactions": 15,
        "experiments": 20,
        "practice": 10,
        "quiz": 15
    }
    
    active_sections = [sec for sec, has_content in sections.items() if has_content]
    sum_active_weights = sum(default_weights[sec] for sec in active_sections)
    
    with get_db() as conn:
        rows = conn.execute("""
            SELECT section_name FROM chapter_section_progress
            WHERE user_id = %s AND chapter_id = %s AND is_completed = TRUE
        """, (user_id, chapter_id)).fetchall()
    completed_sections = {r["section_name"] for r in rows}
    
    empty_sections = [sec for sec, has_content in sections.items() if not has_content]
    if empty_sections:
        with get_db() as conn:
            for sec in empty_sections:
                if sec not in completed_sections:
                    conn.execute("""
                        INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                        VALUES (%s, %s, %s, TRUE, NOW())
                        ON DUPLICATE KEY UPDATE is_completed = TRUE, completed_at = NOW()
                    """, (user_id, chapter_id, sec))
                    completed_sections.add(sec)
                    
    if sum_active_weights > 0:
        completed_active_weight = sum(default_weights[sec] for sec in active_sections if sec in completed_sections)
        mastery_percent = min(100, round((completed_active_weight / sum_active_weights) * 100))
    else:
        mastery_percent = 100
        
    checklist = {sec: (sec in completed_sections) for sec in default_weights.keys()}
    
    if mastery_percent >= 100:
        try:
            with get_db() as conn:
                exists = conn.execute("SELECT * FROM chapter_progress WHERE user_id = %s AND chapter_id = %s", (user_id, chapter_id)).fetchone()
                if exists:
                    conn.execute("UPDATE chapter_progress SET is_completed = TRUE, completed_at = NOW() WHERE user_id = %s AND chapter_id = %s", (user_id, chapter_id))
                else:
                    conn.execute("INSERT INTO chapter_progress (user_id, chapter_id, is_completed, completed_at) VALUES (%s, %s, TRUE, NOW())", (user_id, chapter_id))
        except Exception as e:
            print(f"Error marking chapter complete: {e}")
            
    return {
        "mastery_percent": mastery_percent,
        "checklist": checklist,
        "active_sections": active_sections,
        "empty_sections": empty_sections
    }


@app.route('/api/chapter/<string:chapter_uuid>/section/<string:section_name>', methods=['GET'])
@student_required
def api_chapter_section_view(chapter_uuid, section_name):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('api_chapter_section_view', chapter_uuid=chapter_data['public_id'], section_name=section_name), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        return jsonify({"error": "Chapter not found"}), 404
        
    quiz_data = get_quiz(chapter_uuid)
    
    sections_has_content = {
        "overview": bool(chapter_data.get("overview_content") or chapter_data.get("notes")),
        "keypoints": bool(chapter_data.get("key_points_content") or chapter_data.get("key_points")),
        "formulas": bool(chapter_data.get("formula_content") or chapter_data.get("formulas")),
        "reactions": bool(chapter_data.get("reaction_content") or chapter_data.get("reactions")),
        "experiments": bool(chapter_data.get("experiment_content")),
        "practice": bool(chapter_data.get("practice_content") or chapter_data.get("practice_questions")),
        "quiz": bool(quiz_data)
    }
    
    if not sections_has_content.get(section_name, False):
        return jsonify({"ok": True, "empty": True})
        
    if section_name in ("overview", "keypoints", "formulas", "reactions"):
        try:
            with get_db() as conn:
                conn.execute("""
                    INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                    VALUES (%s, %s, %s, TRUE, NOW())
                    ON DUPLICATE KEY UPDATE is_completed = TRUE, completed_at = NOW()
                """, (user["id"], chapter_id, section_name))
        except Exception as e:
            print(f"Error auto-completing section {section_name}: {e}")
            
    mastery = get_chapter_mastery(user["id"], chapter_id)
    
    content = ""
    if section_name == "overview":
        content = chapter_data.get("overview_content") or chapter_data.get("notes") or ""
    elif section_name == "keypoints":
        content = chapter_data.get("key_points_content") or chapter_data.get("key_points") or ""
    elif section_name == "formulas":
        content = chapter_data.get("formula_content") or chapter_data.get("formulas") or ""
    elif section_name == "reactions":
        content = chapter_data.get("reaction_content") or chapter_data.get("reactions") or ""
    elif section_name == "experiments":
        content = chapter_data.get("experiment_content") or ""
    elif section_name == "practice":
        p_data = chapter_data.get("practice_questions")
        if not p_data:
            p_data = safe_json_loads(chapter_data.get("practice_content") or '[]')
        if isinstance(p_data, str):
            p_data = safe_json_loads(p_data)
        content = p_data if isinstance(p_data, list) else []
    elif section_name == "quiz":
        content = quiz_data
        
    return jsonify({
        "ok": True,
        "content": content,
        "is_completed": mastery["checklist"].get(section_name, False),
        "mastery_percent": mastery["mastery_percent"],
        "checklist": mastery["checklist"],
        "active_sections": mastery["active_sections"]
    })


@app.route('/api/chapter/<string:chapter_uuid>/section/<string:section_name>/complete', methods=['POST'])
@student_required
def api_chapter_section_complete(chapter_uuid, section_name):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('api_chapter_section_complete', chapter_uuid=chapter_data['public_id'], section_name=section_name), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        return jsonify({"error": "Chapter not found"}), 404
        
    chapter_id = chapter_data['id']
    mastery_before = get_chapter_mastery(user["id"], chapter_id)
    already_chapter_completed = (mastery_before["mastery_percent"] >= 100)
    
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                VALUES (%s, %s, %s, TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_completed = TRUE, completed_at = NOW()
            """, (user["id"], chapter_id, section_name))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    mastery_after = get_chapter_mastery(user["id"], chapter_id)
    newly_completed = (mastery_after["mastery_percent"] >= 100 and not already_chapter_completed)
    
    xp_earned = 0
    badge_unlocked = None
    
    if newly_completed:
        xp_earned = 150
        badge_unlocked = "Chapter Mastered"
        try:
            with get_db() as conn:
                conn.execute(
                    "UPDATE student_profiles SET current_xp = current_xp + %s WHERE user_id = %s",
                    (xp_earned, user["id"])
                )
                conn.execute(
                    "INSERT IGNORE INTO user_badges (user_id, badge_id, unlocked_at) VALUES (%s, 1, NOW())",
                    (user["id"],)
                )
                add_history(user["id"], "quiz_passed", f"chapter_id={chapter_id},mastery_xp=150")
        except Exception as e:
            print(f"Error awarding chapter mastery XP/badge: {e}")
            
    return jsonify({
        "ok": True,
        "is_completed": True,
        "mastery_percent": mastery_after["mastery_percent"],
        "checklist": mastery_after["checklist"],
        "active_sections": mastery_after["active_sections"],
        "newly_completed": newly_completed,
        "xp_earned": xp_earned,
        "badge": badge_unlocked
    })


@app.route('/api/chapter/<string:chapter_uuid>/quiz', methods=['GET'])
@student_required
def api_chapter_quiz_data(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('api_chapter_quiz_data', chapter_uuid=chapter_data['public_id']), code=301)

    quiz_data = get_quiz(chapter_uuid)
    if not quiz_data:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify({
        "ok": True,
        "quiz": quiz_data
    })


@app.route('/student/chapter/<string:chapter_uuid>/next')
@student_required
def student_chapter_next(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_next', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter = get_chapter(chapter_uuid)
    if not chapter:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_chapters'))
        
    try:
        with get_db() as conn:
            next_ch = conn.execute("""
                SELECT public_id FROM chapters 
                WHERE class_level = %s AND chapter_number > %s AND status = 'published'
                ORDER BY chapter_number ASC LIMIT 1
            """, (chapter['class_level'], chapter['chapter_number'])).fetchone()
            
            if next_ch:
                return redirect(url_for('student_chapter_view', chapter_uuid=next_ch['public_id']))
            else:
                flash('Congratulations! You have completed the last chapter for this class level.', 'success')
                return redirect(url_for('student_chapters'))
    except Exception as e:
        print(f"Error fetching next chapter: {e}")
        return redirect(url_for('student_chapters'))


# ============================================================
# V4 CHAPTER LEARNING JOURNEY — SECTION SUB-PAGES
# ============================================================

SECTION_ORDER = ['overview', 'key-points', 'formulas', 'reactions', 'experiments', 'practice', 'quiz']
SECTION_DB_MAP = {
    'overview': 'overview',
    'key-points': 'keypoints',
    'formulas': 'formulas',
    'reactions': 'reactions',
    'experiments': 'experiments',
    'practice': 'practice',
    'quiz': 'quiz',
}


def get_chapter_v4_state(user_id, chapter_identifier):
    """Return section availability and progress state for a chapter."""
    chapter_data = get_chapter(chapter_identifier)
    if not chapter_data:
        return None
    chapter_id = chapter_data['id']

    quiz_data = get_quiz(chapter_id)

    has_content = {
        'overview':   bool(chapter_data.get('overview_content') or chapter_data.get('notes')),
        'keypoints':  bool(chapter_data.get('key_points_content') or chapter_data.get('key_points')),
        'formulas':   bool(chapter_data.get('formula_content') or chapter_data.get('formulas')),
        'reactions':  bool(chapter_data.get('reaction_content') or chapter_data.get('reactions')),
        'experiments':bool(chapter_data.get('experiment_content')),
        'practice':   bool(chapter_data.get('practice_content') or chapter_data.get('practice_questions')),
        'quiz':       bool(quiz_data),
    }

    # Get completed sections from DB
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT section_name FROM chapter_section_progress WHERE user_id=%s AND chapter_id=%s AND is_completed=TRUE",
                (user_id, chapter_id)
            ).fetchall()
        completed = {r['section_name'] for r in rows}
    except Exception:
        completed = set()

    # Auto-mark empty sections as completed
    for sec, has in has_content.items():
        if not has and sec not in completed:
            try:
                with get_db() as conn:
                    conn.execute("""
                        INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                        VALUES (%s, %s, %s, TRUE, NOW())
                        ON DUPLICATE KEY UPDATE is_completed=TRUE, completed_at=NOW()
                    """, (user_id, chapter_id, sec))
                completed.add(sec)
            except Exception:
                pass

    # Compute active sections in order
    active_sections = [s for s in ['overview', 'keypoints', 'formulas', 'reactions', 'experiments', 'practice', 'quiz'] if has_content[s]]

    # Compute mastery %
    default_weights = {'overview': 10, 'keypoints': 15, 'formulas': 15, 'reactions': 15, 'experiments': 20, 'practice': 10, 'quiz': 15}
    sum_active = sum(default_weights[s] for s in active_sections)
    if sum_active > 0:
        comp_weight = sum(default_weights[s] for s in active_sections if s in completed)
        mastery = min(100, round(comp_weight / sum_active * 100))
    else:
        mastery = 100

    # Build section states in URL-slug order
    section_states = {}
    prev_active_completed = True  # overview is always first and starts unlocked
    for url_slug in SECTION_ORDER:
        db_key = SECTION_DB_MAP[url_slug]
        if not has_content[db_key]:
            section_states[url_slug] = 'skipped'
        elif db_key in completed:
            section_states[url_slug] = 'completed'
        elif prev_active_completed:
            section_states[url_slug] = 'available'
            prev_active_completed = False
        else:
            section_states[url_slug] = 'locked'
        # If has content and was completed, prev stays True
        if has_content[db_key] and db_key not in completed:
            prev_active_completed = False

    return {
        'chapter_data': chapter_data,
        'quiz_data': quiz_data,
        'has_content': has_content,
        'completed': completed,
        'active_sections': active_sections,
        'mastery': mastery,
        'section_states': section_states,
        'is_chapter_completed': mastery >= 100,
    }


def _chapter_section_view(chapter_uuid, section_slug, template_name):
    """Shared handler for all section sub-pages."""
    user = get_current_user()
    state = get_chapter_v4_state(user['id'], chapter_uuid)
    if not state:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_chapters'))

    # Determine prev/next active (non-skipped) slugs
    active_slugs = [s for s in SECTION_ORDER if state['section_states'].get(s) != 'skipped']
    try:
        idx = active_slugs.index(section_slug)
    except ValueError:
        # Section is skipped — redirect to roadmap
        return redirect(url_for('student_chapter_view', chapter_uuid=chapter_uuid))

    prev_slug = active_slugs[idx - 1] if idx > 0 else None
    next_slug = active_slugs[idx + 1] if idx < len(active_slugs) - 1 else None

    return render_template(
        template_name,
        current_user=user,
        chapter_data=state['chapter_data'],
        quiz_data=state['quiz_data'],
        state=state,
        section_slug=section_slug,
        prev_slug=prev_slug,
        next_slug=next_slug,
        chapter_uuid=chapter_uuid,
        active_tab='chapters',
    )


@app.route('/student/chapter/<string:chapter_uuid>/overview')
@student_required
def student_chapter_overview(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_overview', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_chapters'))
    chapter_id = chapter_data['id']
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                VALUES (%s, %s, 'overview', TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_completed=TRUE, completed_at=NOW()
            """, (user['id'], chapter_id))
    except Exception as e:
        print(f"Error marking overview complete: {e}")
    return _chapter_section_view(chapter_uuid, 'overview', 'student/chapter_section.html')


@app.route('/student/chapter/<string:chapter_uuid>/key-points')
@student_required
def student_chapter_keypoints(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_keypoints', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_chapters'))
    chapter_id = chapter_data['id']
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                VALUES (%s, %s, 'keypoints', TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_completed=TRUE, completed_at=NOW()
            """, (user['id'], chapter_id))
    except Exception as e:
        print(f"Error marking keypoints complete: {e}")
    return _chapter_section_view(chapter_uuid, 'key-points', 'student/chapter_section.html')


@app.route('/student/chapter/<string:chapter_uuid>/formulas')
@student_required
def student_chapter_formulas(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_formulas', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_chapters'))
    chapter_id = chapter_data['id']
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                VALUES (%s, %s, 'formulas', TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_completed=TRUE, completed_at=NOW()
            """, (user['id'], chapter_id))
    except Exception as e:
        print(f"Error marking formulas complete: {e}")
    return _chapter_section_view(chapter_uuid, 'formulas', 'student/chapter_section.html')


@app.route('/student/chapter/<string:chapter_uuid>/reactions')
@student_required
def student_chapter_reactions(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_reactions', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_chapters'))
    chapter_id = chapter_data['id']
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                VALUES (%s, %s, 'reactions', TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_completed=TRUE, completed_at=NOW()
            """, (user['id'], chapter_id))
    except Exception as e:
        print(f"Error marking reactions complete: {e}")
    return _chapter_section_view(chapter_uuid, 'reactions', 'student/chapter_section.html')


@app.route('/student/chapter/<string:chapter_uuid>/experiments')
@student_required
def student_chapter_experiments(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_experiments', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_chapters'))
    chapter_id = chapter_data['id']
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                VALUES (%s, %s, 'experiments', TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_completed=TRUE, completed_at=NOW()
            """, (user['id'], chapter_id))
    except Exception as e:
        print(f"Error marking experiments complete: {e}")
    return _chapter_section_view(chapter_uuid, 'experiments', 'student/chapter_section.html')


@app.route('/student/chapter/<string:chapter_uuid>/practice')
@student_required
def student_chapter_practice(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_practice', chapter_uuid=chapter_data['public_id']), code=301)
    return _chapter_section_view(chapter_uuid, 'practice', 'student/chapter_section.html')


@app.route('/student/chapter/<string:chapter_uuid>/quiz')
@student_required
def student_chapter_quiz(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_chapter_quiz', chapter_uuid=chapter_data['public_id']), code=301)
    return _chapter_section_view(chapter_uuid, 'quiz', 'student/chapter_section.html')


@app.route('/api/chapter/<string:chapter_uuid>/complete-section', methods=['POST'])
@student_required
def api_chapter_complete_section(chapter_uuid):
    """Mark a section as completed."""
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('api_chapter_complete_section', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        return jsonify({'error': 'Chapter not found'}), 404
    chapter_id = chapter_data['id']
    payload = request.get_json(silent=True) or {}
    section_name = payload.get('section')  # DB key: overview, keypoints, etc.
    if not section_name:
        return jsonify({'error': 'Missing section'}), 400
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                VALUES (%s, %s, %s, TRUE, NOW())
                ON DUPLICATE KEY UPDATE is_completed=TRUE, completed_at=NOW()
            """, (user['id'], chapter_id, section_name))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    state = get_chapter_v4_state(user['id'], chapter_uuid)
    return jsonify({'ok': True, 'mastery': state['mastery'], 'section_states': state['section_states']})


@app.route('/api/chapter/<string:chapter_uuid>/complete-chapter', methods=['POST'])
@student_required
def api_chapter_complete(chapter_uuid):
    """Mark chapter as 100% complete, award XP, update all section flags."""
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('api_chapter_complete', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        return jsonify({'error': 'Chapter not found'}), 404
    chapter_id = chapter_data['id']

    xp_reward = 150

    try:
        with get_db() as conn:
            # Mark all sections complete in chapter_section_progress
            for sec in ['overview', 'keypoints', 'formulas', 'reactions', 'experiments', 'practice', 'quiz']:
                conn.execute("""
                    INSERT INTO chapter_section_progress (user_id, chapter_id, section_name, is_completed, completed_at)
                    VALUES (%s, %s, %s, TRUE, NOW())
                    ON DUPLICATE KEY UPDATE is_completed=TRUE, completed_at=NOW()
                """, (user['id'], chapter_id, sec))

            # Check if already completed to avoid double XP
            existing = conn.execute(
                "SELECT is_completed FROM chapter_progress WHERE user_id=%s AND chapter_id=%s",
                (user['id'], chapter_id)
            ).fetchone()
            already_done = existing and existing['is_completed']

            if existing:
                conn.execute("""
                    UPDATE chapter_progress SET
                        is_completed=TRUE,
                        overview_completed=TRUE, keypoints_completed=TRUE,
                        formulas_completed=TRUE, reactions_completed=TRUE,
                        experiments_completed=TRUE, practice_completed=TRUE,
                        quiz_completed=TRUE, completion_percentage=100,
                        xp_earned=%s, completed_at=NOW()
                    WHERE user_id=%s AND chapter_id=%s
                """, (xp_reward, user['id'], chapter_id))
            else:
                conn.execute("""
                    INSERT INTO chapter_progress
                        (user_id, chapter_id, is_completed,
                         overview_completed, keypoints_completed, formulas_completed,
                         reactions_completed, experiments_completed, practice_completed,
                         quiz_completed, completion_percentage, xp_earned, completed_at)
                    VALUES (%s, %s, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 100, %s, NOW())
                """, (user['id'], chapter_id, xp_reward))

            if not already_done:
                # Award XP
                conn.execute(
                    "UPDATE student_profiles SET current_xp=current_xp+%s WHERE user_id=%s",
                    (xp_reward, user['id'])
                )
                conn.execute(
                    "INSERT IGNORE INTO user_badges (user_id, badge_id, unlocked_at) VALUES (%s, 1, NOW())",
                    (user['id'],)
                )
                add_history(user['id'], 'quiz_passed', f"chapter_id={chapter_id},xp={xp_reward}")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'ok': True,
        'xp_earned': 0 if already_done else xp_reward,
        'redirect': f'/student/chapter/{chapter_uuid}'
    })


@app.route('/api/chapter/<string:chapter_uuid>/v4-state', methods=['GET'])
@student_required
def api_chapter_v4_state(chapter_uuid):
    """Get current V4 state for the chapter roadmap page."""
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('api_chapter_v4_state', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    state = get_chapter_v4_state(user['id'], chapter_uuid)
    if not state:
        return jsonify({'error': 'Chapter not found'}), 404
    return jsonify({
        'ok': True,
        'mastery': state['mastery'],
        'section_states': state['section_states'],
        'is_completed': state['is_chapter_completed'],
        'active_sections': state['active_sections'],
    })


@app.route('/api/ai/tutor', methods=['POST'])
@student_required
def api_ai_tutor():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "").strip()
    chapter_title = payload.get("chapter_title", "Chemistry")
    
    if not question:
        return jsonify({"error": "Question is empty"}), 400
        
    question_lower = question.lower()
    response_text = ""
    
    if "acid" in question_lower or "base" in question_lower or "ph" in question_lower:
        response_text = """### 🧪 Acids, Bases, and the pH Scale

**Acids** are substances that donate protons (hydrogen ions $H^+$) in a chemical reaction. They generally have a sour taste and turn blue litmus paper red.
**Bases** are substances that accept protons or release hydroxide ions ($OH^-$). They have a bitter taste, a slippery feel, and turn red litmus paper blue.

#### Key Definitions:
1. **Arrhenius Theory**: 
   - *Acids* produce $H^+$ in water.
   - *Bases* produce $OH^-$ in water.
2. **Brønsted-Lowry Theory**:
   - *Acids* are proton ($H^+$) donors.
   - *Bases* are proton ($H^+$) acceptors.
3. **Lewis Theory**:
   - *Acids* are electron-pair acceptors.
   - *Bases* are electron-pair donors.

#### The pH Scale:
The pH is calculated using the formula:
$$\\text{pH} = -\\log_{10}[H^+]$$
- **pH < 7**: Acidic (higher concentration of $H^+$)
- **pH = 7**: Neutral (pure water, where $[H^+] = [OH^-] = 10^{-7}\\text{ M}$)
- **pH > 7**: Basic/Alkaline (higher concentration of $OH^-$)"""

    elif "organic" in question_lower or "alkane" in question_lower or "alkene" in question_lower or "carbon" in question_lower:
        response_text = """### 🍀 Introduction to Organic Chemistry

**Organic Chemistry** is the scientific study of the structure, properties, and reactions of organic compounds containing carbon atoms covalently bonded to hydrogen and other elements.

#### Why Carbon?
Carbon is unique because it has **4 valence electrons**, allowing it to form stable single, double, and triple covalent bonds with other carbon atoms or elements (catenation).

#### Hydrocarbon Families:
1. **Alkanes** (Saturated Hydrocarbons):
   - General Formula: $C_nH_{2n+2}$
   - Contains only single carbon-carbon bonds (e.g., Methane $CH_4$, Ethane $C_2H_6$).
2. **Alkenes** (Unsaturated Hydrocarbons):
   - General Formula: $C_nH_{2n}$
   - Contains at least one double carbon-carbon bond (e.g., Ethene $C_2H_4$).
3. **Alkynes** (Unsaturated Hydrocarbons):
   - General Formula: $C_nH_{2n-2}$
   - Contains at least one triple carbon-carbon bond (e.g., Ethyne $C_2H_2$).

#### Common Functional Groups:
- **Alcohols**: $-OH$ group (e.g., Ethanol $C_2H_5OH$)
- **Carboxylic Acids**: $-COOH$ group (e.g., Acetic Acid $CH_3COOH$)
- **Esters**: $-COO-$ group (responsible for fruity smells!)"""

    elif "atom" in question_lower or "electron" in question_lower or "proton" in question_lower or "neutron" in question_lower or "periodic" in question_lower:
        response_text = """### ⚛️ Atomic Structure and the Periodic Table

An **atom** is the basic unit of a chemical element, consisting of a central nucleus surrounded by a cloud of negatively charged electrons.

#### Subatomic Particles:
1. **Protons**: Positively charged (+1), located in the nucleus. The number of protons defines the **Atomic Number ($Z$)**.
2. **Neutrons**: Neutrally charged (0), located in the nucleus. Protons + Neutrons define the **Mass Number ($A$)**.
3. **Electrons**: Negatively charged (-1), orbiting the nucleus in specific energy levels/orbitals.

#### Periodic Trends:
- **Electronegativity**: An atom's ability to attract shared electrons. It increases *up* and to the *right* on the Periodic Table (Fluorine is the most electronegative).
- **Atomic Radius**: The size of the atom. It increases *down* and to the *left*.
- **Ionization Energy**: The energy required to remove an electron. It increases *up* and to the *right*."""

    elif "reaction" in question_lower or "stoichiometry" in question_lower:
        response_text = """### 🔀 Chemical Reactions and Stoichiometry

A **chemical reaction** rearranges constituent atoms of reactants to create different substances called products.

#### Main Types of Reactions:
1. **Combination (Synthesis)**: $A + B \\rightarrow AB$
2. **Decomposition**: $AB \\rightarrow A + B$
3. **Single Displacement**: $A + BC \\rightarrow AC + B$
4. **Double Displacement**: $AB + CD \\rightarrow AD + CB$
5. **Combustion**: Hydrocarbon + $O_2 \\rightarrow CO_2 + H_2O + \\text{Energy}$

#### Balancing Equations:
According to the **Law of Conservation of Mass**, matter cannot be created or destroyed. Therefore, equations must have the same number of each atom type on both sides.
- *Example*: $2H_2 + O_2 \\rightarrow 2H_2O$
- Reactants: $4\\text{ H}, 2\\text{ O}$
- Products: $4\\text{ H}, 2\\text{ O}$ (Balanced!)"""

    elif "molarity" in question_lower:
        response_text = """### 🧪 Molarity (M) Explained Simply:

Molarity is a measure of how concentrated a solution is. Specifically, it tells you how many moles of a solute (like salt) are dissolved in exactly 1 Liter of the total solution.

#### Formula:
$$\\text{Molarity (M)} = \\frac{\\text{Moles of solute (n)}}{\\text{Volume of solution in liters (V)}}$$
Unit: mol/L or M

⚠️ **Note**: Molarity depends on temperature because temperature affects volume (liquids expand when heated)."""

    elif "molality" in question_lower:
        response_text = """### 🧪 Molality (m) Explained Simply:

Molality compares the moles of solute to the mass of the solvent in kilograms.

#### Formula:
$$\\text{Molality (m)} = \\frac{\\text{Moles of solute (n)}}{\\text{Mass of solvent in kilograms (kg)}}$$
Unit: mol/kg or m

💡 **Key Advantage**: Unlike Molarity, Molality DOES NOT change with temperature because mass doesn't expand or contract with temperature changes!"""

    elif "solution" in question_lower:
        response_text = """### 🧪 What is a Solution?

A solution is a homogeneous mixture of two or more substances. Homogeneous means that the mixture is uniform throughout.

It consists of two parts:
1. **Solute**: The substance being dissolved (usually present in smaller amounts, e.g., sugar).
2. **Solvent**: The dissolving medium (usually present in larger amounts, e.g., water)."""

    elif "memory" in question_lower or "trick" in question_lower or "mnemonic" in question_lower:
        response_text = """### 🧠 Chemistry Memory Tricks

1. **MolaRity (with an R)** vs **MolaLity (with an L)**:
   - **MolaRity**: Think of 'R' for 'Room' or 'Receptacle' (Liters).
   - **MolaLity**: Think of 'L' for 'lbs' or 'Loads' (Kilograms).
   
2. **Solute vs Solvent**:
   - **SOLUTE** (6 letters) -> Smaller amount (being dissolved).
   - **SOLVENT** (7 letters) -> Larger amount (doing the dissolving)."""

    elif "mcq" in question_lower or "quiz" in question_lower or "test" in question_lower:
        response_text = """### 📝 AI Quiz Generator

**Q1**. Which concentration term is temperature independent?
A) Molarity  
B) Molality  
C) Normality  
D) Formality  
*Answer*: B (Explanation: Molality depends on solvent mass, which doesn't change with temperature).

**Q2**. A solution made by dissolving 2 moles of NaCl in 2 kg of water has a molality of:
A) 1 m  
B) 2 m  
C) 0.5 m  
D) 4 m  
*Answer*: A (Explanation: 2 mol / 2 kg = 1 m)."""

    else:
        response_text = f"""### 💡 Chemistry Tutor Insights

I've analyzed your question: *"{question}"*.

In chemistry, we study matter, its properties, and how it interacts. Here are the core concepts related to your query:
1. **Chemical Properties**: Every substance has a unique arrangement of electrons, defining how it bonds and reacts.
2. **Energy Transitions**: All chemical processes involve energy changes (breaking bonds absorbs energy, forming bonds releases energy).
3. **Molecular Interactions**: Reactions occur when molecules collide with sufficient energy and correct orientation.

**Would you like me to detail a specific topic?**
- Try asking about: **Acids and Bases**, **Organic functional groups**, **Atomic structure**, **Molarity vs Molality**, or **Types of chemical reactions**!"""

    return jsonify({
        "ok": True,
        "response": response_text
    })


@app.route('/student/reactions')
@student_required
def student_reactions():
    user = get_current_user()
    user_class = user['classLevel']
    
    # Access mode check
    access_mode = get_access_mode()
    selected_class = request.args.get('class_level', user_class)
    if access_mode == 'STRICT':
        selected_class = user_class
        
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM reactions WHERE class_level = %s ORDER BY id ASC", (selected_class,)).fetchall()
    reactions = [parse_reaction_json_fields(r) for r in rows]
    
    # Check reaction success event completion
    for rx in reactions:
        try:
            with get_db() as conn:
                event = conn.execute(
                    "SELECT id FROM user_history WHERE user_id = %s AND event_type = 'reaction_success' AND event_data LIKE %s",
                    (user['id'], f"%reaction_id={rx['id']}%")
                ).fetchone()
                rx["completed"] = event is not None
        except Exception as e:
            print(f"Error checking reaction completion: {e}")
            rx["completed"] = False
            
    return render_template('student/reactions.html', current_user=user, reactions=reactions, selected_class=selected_class, active_tab='reactions')


@app.route('/student/experiments')
@student_required
def student_experiments():
    user = get_current_user()
    user_class = user['classLevel']
    
    # Access mode check
    access_mode = get_access_mode()
    selected_class = request.args.get('class_level', user_class)
    if access_mode == 'STRICT':
        selected_class = user_class
        
    try:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT e.*, c.class_level FROM experiments e
                JOIN chapters c ON e.chapter_id = c.id
                WHERE c.class_level = %s
                  AND c.status = 'published'
                  AND (c.publish_at IS NULL OR c.publish_at <= NOW())
                ORDER BY e.id ASC
            """, (selected_class,)).fetchall()
    except Exception as e:
        print(f"Error querying experiments: {e}")
        rows = []
        
    experiments = [parse_experiment_json_fields(row) for row in rows]
    
    # Check experiment titration/reaction logs
    for exp in experiments:
        try:
            with get_db() as conn:
                event = conn.execute(
                    "SELECT id FROM user_history WHERE user_id = %s AND event_type = 'titration_complete' AND event_data LIKE %s",
                    (user['id'], f"%experiment_id={exp['id']}%")
                ).fetchone()
                exp["completed"] = event is not None
        except Exception as e:
            print(f"Error checking experiment completion: {e}")
            exp["completed"] = False
            
    return render_template('student/experiments.html', current_user=user, experiments=experiments, selected_class=selected_class, active_tab='experiments')


@app.route('/student/experiment/<string:experiment_uuid>')
@student_required
def student_experiment_view(experiment_uuid):
    if experiment_uuid.isdigit():
        exp = get_experiment(experiment_uuid)
        if exp:
            return redirect(url_for('student_experiment_view', experiment_uuid=exp['public_id']), code=301)

    user = get_current_user()
    exp = get_experiment(experiment_uuid)
    if not exp:
        flash('Experiment content not found.', 'error')
        return redirect(url_for('student_experiments'))

    experiment_id = exp['id']
    # Check class boundaries and status
    try:
        with get_db() as conn:
            ch = conn.execute("SELECT class_level, status, publish_at FROM chapters WHERE id = %s", (exp['chapter_id'],)).fetchone()
            if not ch:
                flash('Unauthorized experiment access.', 'error')
                return redirect(url_for('student_experiments'))
                
            # Check scheduling and publish status
            is_published = ch.get('status') == 'published'
            publish_at_str = ch.get('publish_at')
            is_scheduled = False
            if publish_at_str:
                pub_time = datetime.fromisoformat(str(publish_at_str)) if isinstance(publish_at_str, str) else publish_at_str
                if pub_time.tzinfo:
                    is_scheduled = pub_time > datetime.now(timezone.utc)
                else:
                    is_scheduled = pub_time > datetime.now()
                    
            if not is_published or is_scheduled:
                flash('This experiment is not available yet.', 'error')
                return redirect(url_for('student_experiments'))
                
            access_mode = get_access_mode()
            if access_mode == 'STRICT' and ch['class_level'] != user['classLevel']:
                flash('Unauthorized experiment access.', 'error')
                return redirect(url_for('student_experiments'))
                
            conn.execute("UPDATE student_profiles SET last_experiment_id = %s WHERE user_id = %s", (experiment_id, user['id']))
    except Exception as e:
        print(f"Error checking boundary or updating tracking: {e}")
        flash('Error accessing experiment content.', 'error')
        return redirect(url_for('student_experiments'))
        
    return render_template('student/experiment_view.html', current_user=user, experiment=exp, active_tab='experiments')


@app.route('/student/quizzes')
@student_required
def student_quizzes():
    user = get_current_user()
    user_class = user['classLevel']
    
    # Access mode check
    access_mode = get_access_mode()
    selected_class = request.args.get('class_level', user_class)
    if access_mode == 'STRICT':
        selected_class = user_class
        
    quizzes = []
    
    try:
        with get_db() as conn:
            quiz_rows = conn.execute("""
                SELECT q.*, c.class_level, c.public_id AS chapter_public_id FROM quizzes q
                JOIN chapters c ON q.chapter_id = c.id
                WHERE c.class_level = %s
                  AND c.status = 'published'
                  AND (c.publish_at IS NULL OR c.publish_at <= NOW())
                ORDER BY q.id ASC
            """, (selected_class,)).fetchall()
            
        for q_row in quiz_rows:
            q_dict = dict(q_row)
            with get_db() as conn:
                questions = conn.execute("SELECT * FROM quiz_questions WHERE quiz_id = %s ORDER BY id ASC", (q_dict['id'],)).fetchall()
                attempt = conn.execute(
                    "SELECT score FROM test_attempts ta JOIN tests t ON ta.test_id = t.id WHERE ta.student_id = %s AND t.chapter_id = %s",
                    (user['id'], q_dict['chapter_id'])
                ).fetchone()
                q_dict["completed_score"] = attempt["score"] if attempt else None
                q_dict["completed"] = attempt is not None
                
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
    except Exception as e:
        print(f"Error fetching student quizzes: {e}")
        
    return render_template('student/quizzes.html', current_user=user, quizzes=quizzes, selected_class=selected_class, active_tab='quizzes')


@app.route('/student/quiz/<string:chapter_uuid>')
@student_required
def student_quiz_view(chapter_uuid):
    if chapter_uuid.isdigit():
        chapter_data = get_chapter(chapter_uuid)
        if chapter_data:
            return redirect(url_for('student_quiz_view', chapter_uuid=chapter_data['public_id']), code=301)

    user = get_current_user()
    chapter_data = get_chapter(chapter_uuid)
    if not chapter_data:
        flash('Chapter not found.', 'error')
        return redirect(url_for('student_quizzes'))

    chapter_id = chapter_data['id']
    quiz_data = get_quiz(chapter_uuid)
    if not quiz_data:
        flash('Quiz not found.', 'error')
        return redirect(url_for('student_quizzes'))
        
    # Check boundaries and scheduling
    try:
        with get_db() as conn:
            ch = conn.execute("SELECT class_level, status, publish_at FROM chapters WHERE id = %s", (chapter_id,)).fetchone()
            if not ch:
                flash('Unauthorized quiz access.', 'error')
                return redirect(url_for('student_quizzes'))
                
            is_published = ch.get('status') == 'published'
            publish_at_str = ch.get('publish_at')
            is_scheduled = False
            if publish_at_str:
                pub_time = datetime.fromisoformat(str(publish_at_str)) if isinstance(publish_at_str, str) else publish_at_str
                if pub_time.tzinfo:
                    is_scheduled = pub_time > datetime.now(timezone.utc)
                else:
                    is_scheduled = pub_time > datetime.now()
                    
            if not is_published or is_scheduled:
                flash('This quiz is not available yet.', 'error')
                return redirect(url_for('student_quizzes'))
                
            access_mode = get_access_mode()
            if access_mode == 'STRICT' and ch['class_level'] != user['classLevel']:
                flash('Unauthorized quiz access.', 'error')
                return redirect(url_for('student_quizzes'))
                
            conn.execute("UPDATE student_profiles SET last_assessment_id = %s WHERE user_id = %s", (quiz_data['id'], user['id']))
    except Exception as e:
        print(f"Error checking boundary or updating tracking: {e}")
        flash('Error loading quiz content.', 'error')
        return redirect(url_for('student_quizzes'))
        
    return render_template('student/quiz_view.html', current_user=user, quiz=quiz_data, active_tab='quizzes')


@app.route('/student/virtual-lab')
@student_required
def student_virtual_lab():
    user = get_current_user()
    return render_template('student/virtual_lab.html', current_user=user, active_tab='virtual-lab')


@app.route('/student/balance-game')
@student_required
def student_balance_game():
    user = get_current_user()
    return render_template('student/balance_game.html', current_user=user, active_tab='balance-game')


@app.route('/api/student/balance-game/complete', methods=['POST'])
@student_required
def api_balance_game_complete():
    user = get_current_user()
    xp_to_add = 40
    try:
        with get_db() as conn:
            conn.execute(
                "UPDATE student_profiles SET current_xp = current_xp + %s WHERE user_id = %s",
                (xp_to_add, user["id"])
            )
        add_history(user["id"], "quiz_passed", "balance_game_complete_xp=40")
        return jsonify({"ok": True, "xp_earned": xp_to_add})
    except Exception as e:
        print(f"Error completing balance game: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/student/assignments')
@student_required
def student_assignments():
    user = get_current_user()
    class_level = user['classLevel']
    assignments = []
    
    try:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT a.*, c.name AS classroom_name,
                       s.status AS submission_status, s.marks_obtained, s.feedback
                FROM assignments a
                JOIN classrooms c ON a.classroom_id = c.id
                JOIN enrollments e ON c.id = e.classroom_id
                LEFT JOIN submissions s ON a.id = s.assignment_id AND s.student_id = %s
                WHERE e.student_id = %s AND a.status = 'published' AND c.grade = %s
                """,
                (user['id'], user['id'], class_level)
            ).fetchall()
            
        chapters = {c['id']: c for c in all_chapters()}
        labs     = {l['id']: l for l in all_labs()}
        
        for r in rows:
            d = dict(r)
            ch = chapters.get(d.get('chapter_id'))
            lb = labs.get(d.get('lab_id'))
            d['chapter_title'] = ch['title'] if ch else None
            d['lab_name']      = lb['title'] if lb else None
            assignments.append(d)
    except Exception as e:
        print(f"Error querying student assignments: {e}")
        
    pending = [a for a in assignments if not a['submission_status']]
    submitted = [a for a in assignments if a['submission_status'] == 'pending']
    graded = [a for a in assignments if a['submission_status'] in ('graded', 'approved')]
    
    return render_template('student/assignments.html', current_user=user, pending=pending, submitted=submitted, graded=graded, active_tab='assignments')


@app.route('/student/profile')
@student_required
def student_profile():
    return redirect(url_for('profile_page'))


# ── Smart Recommendation & Student Analytics API Endpoints ───────────────────
@app.route('/api/student/recommendations')
@student_required
def api_student_recommendations():
    user = get_current_user()
    class_level = user['classLevel']
    
    recommendations = {
        "next_chapter": None,
        "suggested_experiment": None,
        "practice_quiz": None,
        "revision_material": None
    }
    
    try:
        with get_db() as conn:
            ch_rows = conn.execute("SELECT * FROM chapters WHERE class_level = %s ORDER BY chapter_number ASC", (class_level,)).fetchall()
            chapters = [parse_chapter_json_fields(row) for row in ch_rows]
            
            first_incomplete = None
            completed_chapters = []
            for ch in chapters:
                lessons = conn.execute("SELECT id FROM lessons WHERE chapter_id = %s", (ch['id'],)).fetchall()
                comp_count = 0
                for ls in lessons:
                    read_event = conn.execute(
                        "SELECT id FROM user_history WHERE user_id = %s AND event_type = 'read_notes' AND event_data LIKE %s",
                        (user['id'], f"%lesson_id={ls['id']}%")
                    ).fetchone()
                    if read_event:
                        comp_count += 1
                is_completed = (len(lessons) > 0 and comp_count == len(lessons))
                if is_completed:
                    completed_chapters.append(ch)
                elif not first_incomplete:
                    first_incomplete = ch
                    
            if first_incomplete:
                recommendations["next_chapter"] = {
                    "id": first_incomplete["id"],
                    "public_id": first_incomplete["public_id"],
                    "title": first_incomplete["title"],
                    "chapter_number": first_incomplete["chapter_number"],
                    "description": first_incomplete["description"]
                }
                exp_row = conn.execute("SELECT * FROM experiments WHERE chapter_id = %s LIMIT 1", (first_incomplete["id"],)).fetchone()
                if exp_row:
                    recommendations["suggested_experiment"] = {
                        "id": exp_row["id"],
                        "public_id": exp_row["public_id"],
                        "title": exp_row["title"],
                        "aim": exp_row["aim"]
                    }
                quiz_row = conn.execute("SELECT * FROM quizzes WHERE chapter_id = %s LIMIT 1", (first_incomplete["id"],)).fetchone()
                if quiz_row:
                    recommendations["practice_quiz"] = {
                        "id": quiz_row["id"],
                        "chapter_id": first_incomplete["id"],
                        "chapter_public_id": first_incomplete["public_id"],
                        "title": quiz_row["title"]
                    }
            else:
                if completed_chapters:
                    rev = completed_chapters[0]
                    recommendations["next_chapter"] = {
                        "id": rev["id"],
                        "public_id": rev["public_id"],
                        "title": f"Revise: {rev['title']}",
                        "chapter_number": rev["chapter_number"],
                        "description": "You have completed this chapter! Time for revision."
                    }
                    
            if completed_chapters:
                rev_chap = completed_chapters[-1]
                les_row = conn.execute("SELECT * FROM lessons WHERE chapter_id = %s LIMIT 1", (rev_chap["id"],)).fetchone()
                if les_row:
                    recommendations["revision_material"] = {
                        "id": les_row["id"],
                        "chapter_id": rev_chap["id"],
                        "chapter_public_id": rev_chap["public_id"],
                        "title": f"Review {les_row['title']}",
                        "chapter_title": rev_chap["title"]
                    }
    except Exception as e:
        print(f"Error compiling recommendations: {e}")
        
    return jsonify(recommendations)


@app.route('/api/student/analytics')
@student_required
def api_student_analytics():
    user = get_current_user()
    user_id = user['id']
    
    weekly_progress = []
    monthly_progress = []
    learning_hours = []
    assessment_perf = []
    skill_growth = {
        "organic": 0,
        "inorganic": 0,
        "kinetics": 0,
        "titration": 0,
        "general": 0
    }
    
    try:
        with get_db() as conn:
            # Weekly: last 7 days
            for i in range(6, -1, -1):
                day_str = conn.execute(
                    "SELECT DATE(DATE_SUB(NOW(), INTERVAL %s DAY)) as d", (i,)
                ).fetchone()['d']
                
                events = conn.execute(
                    "SELECT event_type, event_data FROM user_history WHERE user_id = %s AND DATE(created_at) = %s",
                    (user_id, day_str)
                ).fetchall()
                daily_xp = 0
                for ev in events:
                    if ev['event_type'] == 'daily_login':
                        daily_xp += 10
                    elif ev['event_type'] == 'quiz_passed':
                        daily_xp += 30
                    elif ev['event_type'] == 'titration_complete':
                        daily_xp += 25
                    elif ev['event_type'] == 'reaction_success':
                        daily_xp += 15
                    elif ev['event_type'] == 'badge_unlocked' and 'XP Awarded' in (ev['event_data'] or ''):
                        daily_xp += 50
                
                day_label = day_str.strftime('%a') if hasattr(day_str, 'strftime') else str(day_str)
                weekly_progress.append({"day": day_label, "xp": daily_xp})
                
            # Monthly: last 4 weeks
            for i in range(3, -1, -1):
                events = conn.execute(
                    """
                    SELECT event_type, event_data FROM user_history 
                    WHERE user_id = %s 
                      AND created_at >= DATE_SUB(NOW(), INTERVAL %s WEEK)
                      AND created_at < DATE_SUB(NOW(), INTERVAL %s WEEK)
                    """,
                    (user_id, i+1, i)
                ).fetchall()
                weekly_xp = 0
                for ev in events:
                    if ev['event_type'] == 'daily_login':
                        weekly_xp += 10
                    elif ev['event_type'] == 'quiz_passed':
                        weekly_xp += 30
                    elif ev['event_type'] == 'titration_complete':
                        weekly_xp += 25
                    elif ev['event_type'] == 'reaction_success':
                        weekly_xp += 15
                    elif ev['event_type'] == 'badge_unlocked' and 'XP Awarded' in (ev['event_data'] or ''):
                        weekly_xp += 50
                monthly_progress.append({"week": f"Week {4-i}", "xp": weekly_xp})
                
            # Learning hours: notes read * 0.25 + titration * 0.5
            for i in range(6, -1, -1):
                day_str = conn.execute(
                    "SELECT DATE(DATE_SUB(NOW(), INTERVAL %s DAY)) as d", (i,)
                ).fetchone()['d']
                notes_read = conn.execute(
                    "SELECT COUNT(*) as c FROM user_history WHERE user_id = %s AND event_type = 'read_notes' AND DATE(created_at) = %s",
                    (user_id, day_str)
                ).fetchone()['c']
                labs_done = conn.execute(
                    "SELECT COUNT(*) as c FROM user_history WHERE user_id = %s AND event_type = 'titration_complete' AND DATE(created_at) = %s",
                    (user_id, day_str)
                ).fetchone()['c']
                hours = round(notes_read * 0.25 + labs_done * 0.5, 2)
                day_label = day_str.strftime('%a') if hasattr(day_str, 'strftime') else str(day_str)
                learning_hours.append({"day": day_label, "hours": hours})
                
            # Recent Quiz attempts
            quiz_attempts = conn.execute(
                """
                SELECT ta.score, t.title 
                FROM test_attempts ta
                JOIN tests t ON ta.test_id = t.id
                WHERE ta.student_id = %s
                ORDER BY ta.completed_at ASC
                LIMIT 5
                """,
                (user_id,)
            ).fetchall()
            for qa in quiz_attempts:
                assessment_perf.append({"quiz": qa['title'][:10] + '...', "score": qa['score']})
                
            # Skill growth estimates
            org_events = conn.execute("SELECT COUNT(*) as c FROM user_history WHERE user_id = %s AND (event_type = 'reaction_success' OR event_data LIKE '%organic%')", (user_id,)).fetchone()['c']
            inorg_events = conn.execute("SELECT COUNT(*) as c FROM user_history WHERE user_id = %s AND event_data LIKE '%inorganic%'", (user_id,)).fetchone()['c']
            kinetics_events = conn.execute("SELECT COUNT(*) as c FROM user_history WHERE user_id = %s AND event_data LIKE '%kinetics%'", (user_id,)).fetchone()['c']
            titration_events = conn.execute("SELECT COUNT(*) as c FROM user_history WHERE user_id = %s AND event_type = 'titration_complete'", (user_id,)).fetchone()['c']
            general_events = conn.execute("SELECT COUNT(*) as c FROM user_history WHERE user_id = %s AND event_type = 'quiz_passed'", (user_id,)).fetchone()['c']
            
            skill_growth["organic"] = min(100, org_events * 20 + 20)
            skill_growth["inorganic"] = min(100, inorg_events * 25 + 15)
            skill_growth["kinetics"] = min(100, kinetics_events * 30 + 10)
            skill_growth["titration"] = min(100, titration_events * 35 + 25)
            skill_growth["general"] = min(100, general_events * 15 + 30)
    except Exception as e:
        print(f"Error compiling student analytics: {e}")
        
    return jsonify({
        "weekly_progress": weekly_progress,
        "monthly_progress": monthly_progress,
        "learning_hours": learning_hours,
        "assessment_performance": assessment_perf,
        "skill_growth": skill_growth
    })


# ============================================================
# TEACHER PORTAL
# ============================================================

@app.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    return render_template('teacher/dashboard.html', current_user=get_current_user(), active_tab='dashboard')


@app.route('/teacher/courses')
@teacher_required
def teacher_courses():
    return render_template('teacher/courses.html', current_user=get_current_user(), active_tab='courses')


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
    chart_data = []
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
                a = {}
                for k, v in dict(r).items():
                    # Convert MySQL Undefined / non-serializable types to safe Python types
                    if v is None or str(type(v)) == "<class 'mysql.connector.types.Undefined'>":
                        a[k] = None
                    elif isinstance(v, datetime):
                        a[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        try:
                            a[k] = str(v) if not isinstance(v, (int, float, bool, str)) else v
                        except Exception:
                            a[k] = None
                audit_logs.append(a)

            # 7-day signup trend for the line chart
            trend_rows = conn.execute("""
                SELECT DATE(created_at) AS day, COUNT(*) AS count
                FROM users
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY day ASC
            """).fetchall()
            chart_data = [{'date': str(r['day']), 'count': int(r['count'])} for r in trend_rows]
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")

    return render_template(
        'admin/dashboard.html',
        current_user=get_current_user(),
        stats=stats,
        audit_logs=audit_logs,
        chart_data=chart_data,
        active_tab='dashboard'
    )


@app.route('/admin/erp-stub')
@admin_required
def admin_erp_stub():
    return redirect(url_for('admin_dashboard'))



@app.route('/admin/control-center', methods=['GET', 'POST'])
@admin_required
def admin_control_center():
    role = request.args.get('role', 'student')
    if role == 'teacher':
        return redirect(url_for('admin_users_teachers'))
    elif role == 'admin':
        return redirect(url_for('admin_users_admins'))
    elif role == 'content_manager' or role == 'content-manager':
        return redirect(url_for('admin_users_content_managers'))
    return redirect(url_for('admin_users_students'))


def handle_user_crud_logic(redirect_url):
    action = request.form.get('action')
    name = request.form.get('name')
    email = request.form.get('email')
    institution = request.form.get('institution')
    role = request.form.get('role')
    class_level = request.form.get('class_level') if role == 'student' else None
    password = request.form.get('password')
    
    if action == 'create':
        if not (name and email and password and institution and role):
            flash("Missing required fields for user creation.", "error")
            return redirect(redirect_url)
        pwd_hash = generate_password_hash(password)
        try:
            with get_db() as conn:
                existing = conn.execute("SELECT id FROM users WHERE email = %s", (email,)).fetchone()
                if existing:
                    flash("A user with this email registry already exists.", "error")
                    return redirect(redirect_url)
                cursor = conn.execute(
                    "INSERT INTO users (public_id, name, email, password_hash, institution, role, class_level, status) VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')",
                    (str(uuid.uuid4()), name, email, pwd_hash, institution, role, class_level)
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
        status = request.form.get('status')
        if not (uid and name and institution and role and status):
            flash("Missing required fields for user edit.", "error")
            return redirect(redirect_url)
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
            return redirect(redirect_url)
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
        if not (uid and password):
            flash("Missing ID or new password.", "error")
            return redirect(redirect_url)
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

    return redirect(redirect_url)


@app.route('/admin/users/students', methods=['GET', 'POST'])
@admin_required
def admin_users_students():
    if request.method == 'POST':
        return handle_user_crud_logic(request.url)
    
    search_query = request.args.get('search', '').strip()
    users = []
    try:
        with get_db() as conn:
            query = "SELECT * FROM users WHERE role = 'student'"
            params = []
            if search_query:
                query += " AND (name LIKE %s OR email LIKE %s OR institution LIKE %s)"
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term, like_term])
            query += " ORDER BY id DESC"
            rows = conn.execute(query, tuple(params)).fetchall()
            for r in rows:
                u_dict = dict(r)
                u_dict["classLevel"] = r["class_level"]
                users.append(u_dict)
    except Exception as e:
        print(f"Error: {e}")
    return render_template('admin/users_students.html', current_user=get_current_user(), users=users, search_query=search_query, active_tab='students')


@app.route('/admin/users/teachers', methods=['GET', 'POST'])
@admin_required
def admin_users_teachers():
    if request.method == 'POST':
        return handle_user_crud_logic(request.url)
    
    search_query = request.args.get('search', '').strip()
    users = []
    try:
        with get_db() as conn:
            query = "SELECT * FROM users WHERE role = 'teacher'"
            params = []
            if search_query:
                query += " AND (name LIKE %s OR email LIKE %s OR institution LIKE %s)"
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term, like_term])
            query += " ORDER BY id DESC"
            rows = conn.execute(query, tuple(params)).fetchall()
            for r in rows:
                u_dict = dict(r)
                users.append(u_dict)
    except Exception as e:
        print(f"Error: {e}")
    return render_template('admin/users_teachers.html', current_user=get_current_user(), users=users, search_query=search_query, active_tab='teachers')


@app.route('/admin/users/admins', methods=['GET', 'POST'])
@admin_required
def admin_users_admins():
    if request.method == 'POST':
        return handle_user_crud_logic(request.url)
    
    search_query = request.args.get('search', '').strip()
    users = []
    try:
        with get_db() as conn:
            query = "SELECT * FROM users WHERE role = 'admin'"
            params = []
            if search_query:
                query += " AND (name LIKE %s OR email LIKE %s OR institution LIKE %s)"
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term, like_term])
            query += " ORDER BY id DESC"
            rows = conn.execute(query, tuple(params)).fetchall()
            for r in rows:
                u_dict = dict(r)
                users.append(u_dict)
    except Exception as e:
        print(f"Error: {e}")
    return render_template('admin/users_admins.html', current_user=get_current_user(), users=users, search_query=search_query, active_tab='admins')


@app.route('/admin/users/content-managers', methods=['GET', 'POST'])
@admin_required
def admin_users_content_managers():
    if request.method == 'POST':
        return handle_user_crud_logic(request.url)
    
    search_query = request.args.get('search', '').strip()
    users = []
    try:
        with get_db() as conn:
            query = "SELECT * FROM users WHERE role = 'content_manager'"
            params = []
            if search_query:
                query += " AND (name LIKE %s OR email LIKE %s OR institution LIKE %s)"
                like_term = f"%{search_query}%"
                params.extend([like_term, like_term, like_term])
            query += " ORDER BY id DESC"
            rows = conn.execute(query, tuple(params)).fetchall()
            for r in rows:
                u_dict = dict(r)
                users.append(u_dict)
    except Exception as e:
        print(f"Error: {e}")
    return render_template('admin/users_content_managers.html', current_user=get_current_user(), users=users, search_query=search_query, active_tab='content_managers')


@app.route('/admin/student-monitoring/<string:user_uuid>', methods=['GET', 'POST'])
@admin_required
def admin_student_monitoring(user_uuid):
    if user_uuid.isdigit():
        with get_db() as conn:
            student_row = conn.execute("SELECT public_id FROM users WHERE id = %s AND role = 'student'", (user_uuid,)).fetchone()
            if student_row:
                return redirect(url_for('admin_student_monitoring', user_uuid=student_row['public_id']), code=301)

    with get_db() as conn:
        student_row = conn.execute("SELECT * FROM users WHERE public_id = %s AND role = 'student'", (user_uuid,)).fetchone()
        
    if not student_row:
        flash("Student profile not found.", "error")
        return redirect(url_for('admin_control_center'))

    user_id = student_row['id']
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
                            "INSERT INTO certificates (public_id, student_id, course_id, verification_id, status) VALUES (%s, %s, %s, %s, 'issued')",
                            (str(uuid.uuid4()), user_id, course_id, verification_id)
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
                
        return redirect(url_for('admin_student_monitoring', user_uuid=student_row['public_id']))

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


@app.route('/admin/teacher-monitoring/<string:user_uuid>', methods=['GET', 'POST'])
@admin_required
def admin_teacher_monitoring(user_uuid):
    if user_uuid.isdigit():
        with get_db() as conn:
            teacher_row = conn.execute("SELECT public_id FROM users WHERE id = %s AND role = 'teacher'", (user_uuid,)).fetchone()
            if teacher_row:
                return redirect(url_for('admin_teacher_monitoring', user_uuid=teacher_row['public_id']), code=301)

    with get_db() as conn:
        teacher_row = conn.execute("SELECT * FROM users WHERE public_id = %s AND role = 'teacher'", (user_uuid,)).fetchone()
        
    if not teacher_row:
        flash("Teacher profile not found.", "error")
        return redirect(url_for('admin_control_center'))

    user_id = teacher_row['id']
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
                
        return redirect(url_for('admin_teacher_monitoring', user_uuid=teacher_row['public_id']))

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


@app.route('/admin/courses', methods=['GET', 'POST'])
@content_manager_or_admin_required
def admin_courses():
    user = get_current_user()
    if request.method == 'POST':
        # Handles quick course status toggle or CRUD via form if desired
        course_id = request.form.get('id')
        action = request.form.get('action')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM courses WHERE id = %s", (course_id,))
                log_audit("delete_course", f"Deleted course ID: {course_id}")
                flash("Course deleted successfully.", "success")
            except Exception as e:
                flash(f"Error deleting course: {e}", "error")
        elif action == 'create':
            title = request.form.get('title')
            description = request.form.get('description')
            category = request.form.get('category', 'Chemistry')
            class_level = request.form.get('class_level')
            subject_id = request.form.get('subject_id')
            if title:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO courses (public_id, title, description, category, class_level, subject_id, status)
                            VALUES (%s, %s, %s, %s, %s, %s, 'active')
                        """, (str(uuid.uuid4()), title, description, category, class_level, subject_id))
                    log_audit("create_course", f"Created course {title} for Class {class_level}")
                    flash("Course registered successfully.", "success")
                except Exception as e:
                    flash(f"Error creating course: {e}", "error")
        elif action == 'edit':
            title = request.form.get('title')
            description = request.form.get('description')
            category = request.form.get('category')
            class_level = request.form.get('class_level')
            subject_id = request.form.get('subject_id')
            status = request.form.get('status', 'active')
            if title and course_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            UPDATE courses 
                            SET title = %s, description = %s, category = %s, class_level = %s, subject_id = %s, status = %s
                            WHERE id = %s
                        """, (title, description, category, class_level, subject_id, status, course_id))
                    log_audit("update_course", f"Updated course ID: {course_id}")
                    flash("Course updated successfully.", "success")
                except Exception as e:
                    flash(f"Error updating course: {e}", "error")
        return redirect(url_for('admin_courses'))

    with get_db() as conn:
        courses = conn.execute("""
            SELECT c.*, s.name as subject_name 
            FROM courses c 
            LEFT JOIN subjects s ON c.subject_id = s.id 
            ORDER BY c.class_level ASC, c.title ASC
        """).fetchall()
        subjects = conn.execute("SELECT * FROM subjects").fetchall()
    return render_template('admin/courses.html', current_user=user, courses=courses, subjects=subjects, active_tab='courses')


@app.route('/admin/chapters', methods=['GET', 'POST'])
@content_manager_or_admin_required
def admin_chapters():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        chapter_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM chapters WHERE id = %s", (chapter_id,))
                log_audit("delete_chapter", f"Deleted chapter ID: {chapter_id}")
                flash("Chapter deleted successfully.", "success")
            except Exception as e:
                flash(f"Error deleting chapter: {e}", "error")
        elif action == 'create':
            title = request.form.get('title')
            description = request.form.get('description')
            class_level = request.form.get('class_level')
            chapter_number = request.form.get('chapter_number')
            if title:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO chapters (public_id, title, description, class_level, chapter_number, learning_objectives, key_points, important_laws, formulas, constants, important_reactions, notes, real_life_applications, virtual_labs, practice_questions, common_mistakes, chapter_weightage, next_chapter)
                            VALUES (%s, %s, %s, %s, %s, '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]')
                        """, (str(uuid.uuid4()), title, description, class_level, chapter_number))
                    log_audit("create_chapter", f"Created chapter {title} for Class {class_level}")
                    flash("Chapter registered successfully.", "success")
                except Exception as e:
                    flash(f"Error creating chapter: {e}", "error")
        return redirect(url_for('admin_chapters'))

    with get_db() as conn:
        chapters = conn.execute("""
            SELECT ch.*, c.title as course_title 
            FROM chapters ch 
            LEFT JOIN courses c ON ch.class_level = c.class_level 
            ORDER BY ch.class_level ASC, ch.chapter_number ASC
        """).fetchall()
        courses = conn.execute("SELECT id, title, class_level FROM courses").fetchall()
    return render_template('admin/chapters.html', current_user=user, chapters=chapters, courses=courses, active_tab='chapters')


@app.route('/admin/chapters/<string:chapter_uuid>/builder', methods=['GET', 'POST'])
@content_manager_or_admin_required
def admin_chapter_builder(chapter_uuid):
    if chapter_uuid.isdigit():
        with get_db() as conn:
            chapter = conn.execute("SELECT public_id FROM chapters WHERE id = %s", (chapter_uuid,)).fetchone()
            if chapter:
                return redirect(url_for('admin_chapter_builder', chapter_uuid=chapter['public_id']), code=301)

    user = get_current_user()
    with get_db() as conn:
        chapter = conn.execute("SELECT * FROM chapters WHERE public_id = %s", (chapter_uuid,)).fetchone()
        if not chapter:
            flash("Chapter not found.", "error")
            return redirect(url_for('admin_chapters'))
            
        chapter_id = chapter['id']
        if request.method == 'POST':
            # Update chapter data fields
            title = request.form.get('title')
            description = request.form.get('description')
            chapter_number = request.form.get('chapter_number')
            class_level = request.form.get('class_level')
            
            # Form tab fields (stored as JSON)
            key_points = request.form.get('key_points', '[]')
            important_reactions = request.form.get('important_reactions', '[]')
            formulas = request.form.get('formulas', '[]')
            notes = request.form.get('notes', '[]')
            practice_questions = request.form.get('practice_questions', '[]')
            
            conn.execute("""
                UPDATE chapters 
                SET title = %s, description = %s, chapter_number = %s, class_level = %s,
                    key_points = %s, important_reactions = %s, formulas = %s, notes = %s, practice_questions = %s
                WHERE id = %s
            """, (title, description, chapter_number, class_level, 
                  key_points, important_reactions, formulas, notes, practice_questions, chapter_id))
            log_audit("update_chapter_builder", f"Updated chapter builder content for chapter {title} (ID: {chapter_id})")
            flash("Chapter content updated successfully.", "success")
            return redirect(url_for('admin_chapter_builder', chapter_uuid=chapter['public_id']))

        quizzes = conn.execute("SELECT * FROM quizzes WHERE chapter_id = %s", (chapter_id,)).fetchall()
        reactions = conn.execute("SELECT * FROM reactions WHERE chapter_id = %s", (chapter_id,)).fetchall()
        experiments = conn.execute("SELECT * FROM experiments WHERE chapter_id = %s", (chapter_id,)).fetchall()
        
    return render_template(
        'admin/chapter_builder.html', 
        current_user=user, 
        chapter=dict(chapter), 
        quizzes=quizzes,
        reactions=reactions,
        experiments=experiments,
        active_tab='chapters'
    )


@app.route('/admin/library', methods=['GET', 'POST'])
@admin_required
def admin_library():
    user = get_current_user()
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        access_mode = request.form.get('access_mode')
        if category_name and access_mode:
            with get_db() as conn:
                conn.execute("""
                    INSERT INTO library_settings (category_name, access_mode) 
                    VALUES (%s, %s) 
                    ON DUPLICATE KEY UPDATE access_mode = %s
                """, (category_name, access_mode, access_mode))
            log_audit("update_library_settings", f"Updated access mode for {category_name} to {access_mode}")
            flash(f"Library setting for {category_name} updated successfully.", "success")
        return redirect(url_for('admin_library'))
        
    with get_db() as conn:
        settings = conn.execute("SELECT * FROM library_settings").fetchall()
    return render_template('admin/library.html', current_user=user, settings=settings, active_tab='library')


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
                matching_courses = conn.execute("SELECT id FROM courses WHERE class_level = %s AND status IN ('active', 'published')", (user["classLevel"],)).fetchall()
                for c in matching_courses:
                    conn.execute("INSERT IGNORE INTO course_enrollments (course_id, student_id, progress, status) VALUES (%s, %s, 0, 'active')", (c['id'], user['id']))
        except Exception as e:
            print(f"Error auto-enrolling student: {e}")

    enrollments = []
    try:
        with get_db() as conn:
            access_mode = get_access_mode()
            if access_mode == 'STRICT':
                rows = conn.execute("""
                    SELECT ce.*, c.title as course_title, c.description, c.category, c.class_level
                    FROM course_enrollments ce
                    JOIN courses c ON ce.course_id = c.id
                    WHERE ce.student_id = %s AND c.class_level = %s AND c.status IN ('active', 'published')
                """, (user["id"], user["classLevel"])).fetchall()
            else:
                rows = conn.execute("""
                    SELECT ce.id as enrollment_id, ce.progress, ce.status as enrollment_status, ce.enrolled_at,
                           c.id as course_id, c.title as course_title, c.description, c.category, c.class_level
                    FROM courses c
                    LEFT JOIN course_enrollments ce ON ce.course_id = c.id AND ce.student_id = %s
                    WHERE c.status IN ('active', 'published')
                """, (user["id"],)).fetchall()
                
            enrollments = []
            for r in rows:
                r_dict = dict(r)
                if 'course_id' not in r_dict:
                    r_dict['course_id'] = r_dict.get('id')
                enrollments.append(r_dict)
    except Exception as e:
        print(f"Error fetching enrollments: {e}")
    return render_template('student/courses.html', current_user=user, enrollments=enrollments, active_tab='courses')


@app.route('/student/course/<string:course_uuid>')
@student_required
def student_course_view(course_uuid):
    if course_uuid.isdigit():
        with get_db() as conn:
            course = conn.execute("SELECT public_id FROM courses WHERE id = %s", (course_uuid,)).fetchone()
            if course:
                return redirect(url_for('student_course_view', course_uuid=course['public_id']), code=301)

    user = get_current_user()
    try:
        with get_db() as conn:
            course = conn.execute("SELECT * FROM courses WHERE public_id = %s", (course_uuid,)).fetchone()
            if not course or course['status'] not in ('active', 'published'):
                flash("Course not found.", "error")
                return redirect(url_for('student_courses'))
                
            course_id = course['id']
            access_mode = get_access_mode()
            if access_mode == 'STRICT' and course['class_level'] != user['classLevel']:
                flash("Course not found or unauthorized.", "error")
                return redirect(url_for('student_courses'))
                
            # If EXPLORE or OPEN mode and they aren't enrolled yet, enroll them on-the-fly
            enrollment = conn.execute("SELECT * FROM course_enrollments WHERE course_id = %s AND student_id = %s", (course_id, user["id"])).fetchone()
            if not enrollment:
                conn.execute("INSERT IGNORE INTO course_enrollments (course_id, student_id, progress, status) VALUES (%s, %s, 0, 'active')", (course_id, user['id']))
                enrollment = conn.execute("SELECT * FROM course_enrollments WHERE course_id = %s AND student_id = %s", (course_id, user["id"])).fetchone()
            
            # Fetch hierarchy: modules -> chapters -> lessons -> resources
            modules_rows = conn.execute("SELECT * FROM modules WHERE course_id = %s ORDER BY order_index ASC", (course_id,)).fetchall()
            modules = []
            for m in modules_rows:
                m_dict = dict(m)
                ch_rows = conn.execute("""
                    SELECT * FROM chapters 
                    WHERE module_id = %s 
                      AND status = 'published'
                      AND (publish_at IS NULL OR publish_at <= NOW())
                    ORDER BY chapter_number ASC
                """, (m_dict["id"],)).fetchall()
                chapters = []
                for ch in ch_rows:
                    ch_dict = parse_chapter_json_fields(ch)
                    lesson_rows = conn.execute("""
                        SELECT * FROM lessons 
                        WHERE chapter_id = %s 
                          AND status = 'published' 
                          AND (publish_at IS NULL OR publish_at <= NOW())
                        ORDER BY order_index ASC
                    """, (ch_dict["id"],)).fetchall()
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
                WHERE c.student_id = %s AND cr.class_level = %s AND c.status = 'issued'
                ORDER BY c.issued_at DESC
            """, (user["id"], user["classLevel"])).fetchall()
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
    if not user or user['role'] not in ('admin', 'teacher', 'content_manager'):
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
                    "INSERT INTO courses (public_id, title, description, category, class_level, status) VALUES (%s, %s, %s, %s, %s, %s)",
                    (str(uuid.uuid4()), title, description, category, class_level, status)
                )
                course_id = cursor.lastrowid
                
                if class_level and status == 'active':
                    students = conn.execute("SELECT id FROM users WHERE role = 'student' AND class_level = %s", (class_level,)).fetchall()
                    for s in students:
                        conn.execute("INSERT IGNORE INTO course_enrollments (course_id, student_id, progress, status) VALUES (%s, %s, 0, 'active')", (course_id, s['id']))
                
            # Check-in version 1 (outside main transaction to avoid self-deadlock)
            c_data = {
                "title": title,
                "description": description,
                "category": category,
                "class_level": class_level,
                "status": status,
                "thumbnail": None
            }
            check_in_version('course', course_id, title, c_data, user['id'])
                        
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
        thumbnail = payload.get("thumbnail")
        
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
        if thumbnail is not None:
            update_fields.append("thumbnail = %s")
            params.append(thumbnail)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(course_id)
        query = f"UPDATE courses SET {', '.join(update_fields)} WHERE id = %s"
        try:
            uc = None
            with get_db() as conn:
                conn.execute(query, tuple(params))
                
                # Retrieve the updated course and check-in
                updated_course = conn.execute("SELECT * FROM courses WHERE id = %s", (course_id,)).fetchone()
                if updated_course:
                    uc = dict(updated_course)
            
            if uc:
                c_data = {
                    "title": uc["title"],
                    "description": uc["description"],
                    "category": uc["category"],
                    "class_level": uc["class_level"],
                    "status": uc["status"],
                    "thumbnail": uc.get("thumbnail")
                }
                check_in_version('course', course_id, uc["title"], c_data, user['id'])
                    
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
        publish_at = payload.get("publish_at")
        
        if not chapter_id or not title:
            return jsonify({"error": "Missing chapter_id or title"}), 400
            
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO lessons (public_id, chapter_id, title, content, order_index, status, publish_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (str(uuid.uuid4()), chapter_id, title, content, order_index, status, publish_at)
                )
                lesson_id = cursor.lastrowid
                
            # Check-in version 1 (outside main transaction to avoid self-deadlock)
            l_data = {
                "chapter_id": chapter_id,
                "title": title,
                "content": content,
                "order_index": order_index,
                "status": status,
                "publish_at": str(publish_at) if publish_at else None
            }
            check_in_version('lesson', lesson_id, title, l_data, user['id'])
                
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
        publish_at = payload.get("publish_at")
        
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
        if publish_at is not None:
            update_fields.append("publish_at = %s")
            params.append(publish_at)
            
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
            
        params.append(lesson_id)
        query = f"UPDATE lessons SET {', '.join(update_fields)} WHERE id = %s"
        try:
            ul = None
            with get_db() as conn:
                conn.execute(query, tuple(params))
                
                # Retrieve the updated lesson and check-in
                updated_lesson = conn.execute("SELECT * FROM lessons WHERE id = %s", (lesson_id,)).fetchone()
                if updated_lesson:
                    ul = dict(updated_lesson)
            
            if ul:
                l_data = {
                    "chapter_id": ul["chapter_id"],
                    "title": ul["title"],
                    "content": ul["content"],
                    "order_index": ul["order_index"],
                    "status": ul["status"],
                    "publish_at": str(ul["publish_at"]) if ul.get("publish_at") else None
                }
                check_in_version('lesson', lesson_id, ul["title"], l_data, user['id'])
                    
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



@app.route('/api/admin/versions', methods=['GET', 'POST'])
def api_admin_versions():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'GET':
        content_type = request.args.get("content_type")
        content_id = request.args.get("content_id")
        if not content_type or not content_id:
            return jsonify({"error": "Missing content_type or content_id"}), 400
            
        try:
            with get_db() as conn:
                rows = conn.execute(
                    """
                    SELECT cv.*, u.name as creator_name 
                    FROM content_versions cv
                    JOIN users u ON cv.created_by = u.id
                    WHERE cv.content_type = %s AND cv.content_id = %s
                    ORDER BY cv.version_number DESC
                    """,
                    (content_type, content_id)
                ).fetchall()
            return jsonify({"versions": [dict(r) for r in rows]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    elif request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        content_type = payload.get("content_type")
        content_id = payload.get("content_id")
        version_number = payload.get("version_number")
        
        if not content_type or not content_id or not version_number:
            return jsonify({"error": "Missing content_type, content_id or version_number"}), 400
            
        try:
            with get_db() as conn:
                ver = conn.execute(
                    "SELECT * FROM content_versions WHERE content_type = %s AND content_id = %s AND version_number = %s",
                    (content_type, content_id, version_number)
                ).fetchone()
                if not ver:
                    return jsonify({"error": "Version not found"}), 404
                
                data = json.loads(ver["content_data"])
                
                if content_type == 'course':
                    conn.execute(
                        "UPDATE courses SET title = %s, description = %s, category = %s, class_level = %s, status = %s, thumbnail = %s, version = %s WHERE id = %s",
                        (data.get("title"), data.get("description"), data.get("category"), data.get("class_level"), data.get("status"), data.get("thumbnail"), version_number, content_id)
                    )
                elif content_type == 'chapter':
                    conn.execute(
                        """
                        UPDATE chapters SET 
                            class_level = %s, chapter_number = %s, title = %s, description = %s,
                            learning_objectives = %s, key_points = %s, important_laws = %s, formulas = %s,
                            constants = %s, important_reactions = %s, notes = %s, real_life_applications = %s,
                            virtual_labs = %s, practice_questions = %s, common_mistakes = %s, difficulty = %s,
                            estimated_study_time = %s, chapter_weightage = %s, next_chapter = %s,
                            status = %s, version = %s, order_index = %s, publish_at = %s
                        WHERE id = %s
                        """,
                        (
                            data.get("class_level"), data.get("chapter_number"), data.get("title"), data.get("description"),
                            json.dumps(data.get("learning_objectives", [])), json.dumps(data.get("key_points", [])), json.dumps(data.get("important_laws", [])), json.dumps(data.get("formulas", [])),
                            json.dumps(data.get("constants", [])), json.dumps(data.get("important_reactions", [])), json.dumps(data.get("notes", [])), json.dumps(data.get("real_life_applications", [])),
                            json.dumps(data.get("virtual_labs", [])), json.dumps(data.get("practice_questions", [])), json.dumps(data.get("common_mistakes", [])), data.get("difficulty"),
                            data.get("estimated_study_time"), json.dumps(data.get("chapter_weightage", {})), json.dumps(data.get("next_chapter", {})),
                            data.get("status"), version_number, data.get("order_index", 0), data.get("publish_at"),
                            content_id
                        )
                    )
                elif content_type == 'lesson':
                    conn.execute(
                        "UPDATE lessons SET title = %s, content = %s, order_index = %s, status = %s, publish_at = %s, version = %s WHERE id = %s",
                        (data.get("title"), data.get("content"), data.get("order_index"), data.get("status"), data.get("publish_at"), version_number, content_id)
                    )
                
            log_audit("restore_version", f"Restored {content_type} ID {content_id} to version {version_number}")
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
                    "INSERT INTO certificates (public_id, student_id, course_id, verification_id, status) VALUES (%s, %s, %s, %s, %s)",
                    (str(uuid.uuid4()), student_id, course_id, verification_id, status)
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
                        "INSERT INTO certificates (public_id, student_id, course_id, verification_id, status) VALUES (%s, %s, %s, %s, 'issued')",
                        (str(uuid.uuid4()), user["id"], course_id, verification_id)
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
        if user['role'] == 'student' and classroom_id:
            with get_db() as conn:
                enrollment = conn.execute("SELECT 1 FROM enrollments WHERE classroom_id = %s AND student_id = %s", (classroom_id, user['id'])).fetchone()
                if not enrollment:
                    return jsonify({"error": "Forbidden - not enrolled in this classroom"}), 403
                    
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
                INSERT INTO tests(public_id, title, classroom_id, chapter_id, quiz_content_id, duration_minutes,
                                  total_marks, start_date, end_date, difficulty, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'scheduled', NOW())
                """,
                (
                    str(uuid.uuid4()),
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


@app.route('/api/teacher/analytics', methods=['GET'])
def api_teacher_analytics():
    user = get_current_user()
    if not user or user['role'] not in ('teacher', 'admin'):
        return jsonify({"error": "Forbidden"}), 403

    quiz_stats = []
    attendance_stats = []

    try:
        with get_db() as conn:
            if user['role'] == 'teacher':
                quiz_query = """
                    SELECT c.name AS classroom_name, COALESCE(AVG(ta.score * 100.0 / t.total_marks), 0) AS avg_score
                    FROM test_attempts ta
                    JOIN tests t ON ta.test_id = t.id
                    JOIN classrooms c ON t.classroom_id = c.id
                    WHERE c.teacher_id = %s
                    GROUP BY c.id, c.name
                """
                quiz_rows = conn.execute(quiz_query, (user['id'],)).fetchall()
            else:
                quiz_query = """
                    SELECT c.name AS classroom_name, COALESCE(AVG(ta.score * 100.0 / t.total_marks), 0) AS avg_score
                    FROM test_attempts ta
                    JOIN tests t ON ta.test_id = t.id
                    JOIN classrooms c ON t.classroom_id = c.id
                    GROUP BY c.id, c.name
                """
                quiz_rows = conn.execute(quiz_query).fetchall()
            quiz_stats = [dict(r) for r in quiz_rows]
    except Exception as e:
        print(f"Error querying quiz analytics: {e}")

    if not quiz_stats:
        quiz_stats = [
            {"classroom_name": "Class 10-A (Chemistry)", "avg_score": 82.5},
            {"classroom_name": "Class 11-B (Organic)", "avg_score": 74.0},
            {"classroom_name": "Class 12-A (Kinetics)", "avg_score": 88.2},
            {"classroom_name": "Class 9-C (Intro)", "avg_score": 69.5}
        ]

    try:
        with get_db() as conn:
            if user['role'] == 'teacher':
                att_query = """
                    SELECT a.date, 
                           SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_count,
                           SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent_count
                    FROM attendance a
                    JOIN classrooms c ON a.classroom_id = c.id
                    WHERE c.teacher_id = %s
                    GROUP BY a.date
                    ORDER BY a.date ASC
                    LIMIT 7
                """
                att_rows = conn.execute(att_query, (user['id'],)).fetchall()
            else:
                att_query = """
                    SELECT a.date, 
                           SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present_count,
                           SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent_count
                    FROM attendance a
                    GROUP BY a.date
                    ORDER BY a.date ASC
                    LIMIT 7
                """
                att_rows = conn.execute(att_query).fetchall()
            
            for r in att_rows:
                p = r['present_count']
                ab = r['absent_count']
                total = p + ab
                ratio = (p * 100.0 / total) if total > 0 else 100
                attendance_stats.append({
                    "day": str(r['date']),
                    "present_pct": round(ratio, 1),
                    "absent_pct": round(100.0 - ratio, 1)
                })
    except Exception as e:
        print(f"Error querying attendance analytics: {e}")

    if not attendance_stats:
        attendance_stats = [
            {"day": "Mon", "present_pct": 92.0, "absent_pct": 8.0},
            {"day": "Tue", "present_pct": 95.0, "absent_pct": 5.0},
            {"day": "Wed", "present_pct": 88.0, "absent_pct": 12.0},
            {"day": "Thu", "present_pct": 94.0, "absent_pct": 6.0},
            {"day": "Fri", "present_pct": 91.0, "absent_pct": 9.0}
        ]

    return jsonify({
        "quizzes": quiz_stats,
        "attendance": attendance_stats
    })


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


@app.route('/api/admin/global-search', methods=['GET'])
@limiter.limit("60 per minute")
def api_admin_global_search():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user.get('role') not in ('admin', 'teacher', 'content_manager'):
        return jsonify({"error": "Forbidden"}), 403

    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"results": []})

    results = []
    like_query = f"%{query}%"

    try:
        with get_db() as conn:
            # 1. Search Users (Students/Teachers/Admins)
            users_rows = conn.execute(
                "SELECT id, name, email, role FROM users WHERE name LIKE %s OR email LIKE %s LIMIT 5",
                (like_query, like_query)
            ).fetchall()
            for u in users_rows:
                results.append({
                    "type": "User",
                    "title": u["name"],
                    "subtitle": f"{u['role'].capitalize()} • {u['email']}",
                    "url": f"/admin/users/{u['role']}s"
                })

            # 2. Search Courses
            courses_rows = conn.execute(
                "SELECT id, title FROM courses WHERE title LIKE %s LIMIT 5",
                (like_query,)
            ).fetchall()
            for c in courses_rows:
                results.append({
                    "type": "Course",
                    "title": c["title"],
                    "subtitle": "Course Module",
                    "url": "/admin/courses"
                })

            # 3. Search Chapters
            chapters_rows = conn.execute(
                "SELECT id, title FROM chapters WHERE title LIKE %s LIMIT 5",
                (like_query,)
            ).fetchall()
            for ch in chapters_rows:
                results.append({
                    "type": "Chapter",
                    "title": ch["title"],
                    "subtitle": "Chapter Study Guide",
                    "url": "/admin/chapters"
                })

            # 4. Search Labs
            labs_rows = conn.execute(
                "SELECT id, title FROM labs WHERE title LIKE %s LIMIT 5",
                (like_query,)
            ).fetchall()
            for l in labs_rows:
                results.append({
                    "type": "Lab",
                    "title": l["title"],
                    "subtitle": "Interactive Experiment",
                    "url": "/admin/labs"
                })

            # 5. Search Reactions
            reactions_rows = conn.execute(
                "SELECT id, name FROM reactions WHERE name LIKE %s LIMIT 5",
                (like_query,)
            ).fetchall()
            for r in reactions_rows:
                results.append({
                    "type": "Reaction",
                    "title": r["name"],
                    "subtitle": "Chemical Equation",
                    "url": "/admin/reactions"
                })
    except Exception as e:
        print(f"[SEARCH ERROR] {e}")

    return jsonify({"results": results})


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


@app.route('/admin/certificates', methods=['GET', 'POST'])
@admin_required
def admin_certificates():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        cert_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM certificates WHERE id = %s", (cert_id,))
                log_audit("delete_certificate", f"Deleted issued certificate ID: {cert_id}")
                flash("Certificate deleted.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            student_id = request.form.get('student_id')
            course_id = request.form.get('course_id')
            import uuid
            verification_id = str(uuid.uuid4())[:18].upper()
            if student_id and course_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO certificates (public_id, student_id, course_id, verification_id, status)
                            VALUES (%s, %s, %s, %s, 'issued')
                        """, (str(uuid.uuid4()), student_id, course_id, verification_id))
                    log_audit("create_certificate", f"Issued new certificate for student ID {student_id} for course ID {course_id}")
                    flash("Certificate issued successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'edit':
            status = request.form.get('status')
            if status and cert_id:
                try:
                    with get_db() as conn:
                        conn.execute("UPDATE certificates SET status = %s WHERE id = %s", (status, cert_id))
                    log_audit("update_certificate", f"Updated certificate ID {cert_id} status to {status}")
                    flash("Certificate updated successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_certificates'))

    with get_db() as conn:
        certificates = conn.execute("""
            SELECT cert.*, u.name as student_name, c.title as course_title 
            FROM certificates cert 
            JOIN users u ON cert.student_id = u.id 
            JOIN courses c ON cert.course_id = c.id 
            ORDER BY cert.id DESC
        """).fetchall()
        students = conn.execute("SELECT id, name FROM users WHERE role = 'student'").fetchall()
        courses = conn.execute("SELECT id, title FROM courses").fetchall()
    return render_template('admin/certificates.html', current_user=user, certificates=certificates, students=students, courses=courses, active_tab='certificates')


@app.route('/admin/achievements', methods=['GET', 'POST'])
@admin_required
def admin_achievements():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        badge_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM badges WHERE id = %s", (badge_id,))
                log_audit("delete_badge", f"Deleted badge achievement ID: {badge_id}")
                flash("Achievement deleted.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            name = request.form.get('name')
            description = request.form.get('description')
            icon = request.form.get('icon', 'military_tech')
            xp_reward = request.form.get('xp_reward', 50)
            if name:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO badges (public_id, name, description, icon, xp_reward)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (str(uuid.uuid4()), name, description, icon, xp_reward))
                    log_audit("create_badge", f"Created badge achievement: {name}")
                    flash("Achievement registered.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'edit':
            name = request.form.get('name')
            description = request.form.get('description')
            icon = request.form.get('icon')
            xp_reward = request.form.get('xp_reward')
            if name and badge_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            UPDATE badges 
                            SET name = %s, description = %s, icon = %s, xp_reward = %s
                            WHERE id = %s
                        """, (name, description, icon, xp_reward, badge_id))
                    log_audit("update_badge", f"Updated badge ID: {badge_id}")
                    flash("Achievement updated successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_achievements'))

    with get_db() as conn:
        badges = conn.execute("SELECT * FROM badges ORDER BY id ASC").fetchall()
    return render_template('admin/achievements.html', current_user=user, badges=badges, active_tab='achievements')


@app.route('/admin/leaderboards')
@admin_required
def admin_leaderboards():
    with get_db() as conn:
        # Fetch leaderboard stats by level and XP
        students = conn.execute("""
            SELECT u.id, u.name, u.institution, sp.current_xp, sp.level 
            FROM users u 
            JOIN student_profiles sp ON u.id = sp.user_id 
            ORDER BY sp.current_xp DESC 
            LIMIT 50
        """).fetchall()
    return render_template('admin/leaderboards.html', current_user=get_current_user(), students=students, active_tab='leaderboards')


# ============================================================
# ADMIN — COMMUNICATIONS / ANNOUNCEMENTS
# ============================================================

@app.route('/admin/communications', methods=['GET', 'POST'])
@admin_required
def admin_communications():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        ann_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM announcements WHERE id = %s", (ann_id,))
                log_audit("delete_announcement", f"Deleted announcement ID: {ann_id}")
                flash("Announcement deleted.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            title = request.form.get('title')
            content = request.form.get('content')
            target_role = request.form.get('target_role', 'all')
            is_pinned = 1 if request.form.get('is_pinned') else 0
            if title and content:
                try:
                    with get_db() as conn:
                        conn.execute(
                            "INSERT INTO announcements (public_id, title, content, author_id, target_role, is_pinned, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                            (str(uuid.uuid4()), title, content, user['id'], target_role if target_role != 'all' else None, is_pinned)
                        )
                    log_audit("create_announcement", f"Created announcement: {title}")
                    flash("Announcement published.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'edit':
            title = request.form.get('title')
            content = request.form.get('content')
            is_pinned = 1 if request.form.get('is_pinned') else 0
            if title and ann_id:
                try:
                    with get_db() as conn:
                        conn.execute(
                            "UPDATE announcements SET title = %s, content = %s, is_pinned = %s WHERE id = %s",
                            (title, content, is_pinned, ann_id)
                        )
                    log_audit("edit_announcement", f"Updated announcement ID: {ann_id}")
                    flash("Announcement updated.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_communications'))

    announcements = []
    try:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT a.*, u.name AS author_name 
                FROM announcements a 
                JOIN users u ON a.author_id = u.id 
                ORDER BY a.is_pinned DESC, a.created_at DESC
            """).fetchall()
            announcements = [dict(r) for r in rows]
            for a in announcements:
                if isinstance(a.get('created_at'), datetime):
                    a['created_at'] = a['created_at'].strftime('%Y-%m-%d %H:%M')
    except Exception as e:
        print(f"Error loading announcements: {e}")
    return render_template('admin/communications.html', current_user=user, announcements=announcements, active_tab='communications')


@app.route('/admin/notifications', methods=['GET', 'POST'])
@admin_required
def admin_notifications():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        notif_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM notifications WHERE id = %s", (notif_id,))
                log_audit("delete_notification", f"Deleted notification ID: {notif_id}")
                flash("Notification deleted.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            title = request.form.get('title')
            message = request.form.get('message')
            target_role = request.form.get('target_role', 'all')
            target_institution = request.form.get('target_institution', 'all')
            target_class_level = request.form.get('target_class_level', 'all')
            if title and message:
                try:
                    with get_db() as conn:
                        conn.execute(
                            """
                            INSERT INTO notifications 
                            (sender_id, title, message, target_role, target_institution, target_class_level, created_at) 
                            VALUES (%s, %s, %s, %s, %s, %s, NOW())
                            """,
                            (user['id'], title, message, target_role, target_institution, target_class_level)
                        )
                    log_audit("create_notification", f"Created notification: {title}")
                    flash("Notification broadcast successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_notifications'))

    notifications = []
    schools = []
    try:
        with get_db() as conn:
            school_rows = conn.execute("SELECT DISTINCT institution FROM users WHERE institution IS NOT NULL AND institution != ''").fetchall()
            schools = [r['institution'] for r in school_rows]
            
            notif_rows = conn.execute("""
                SELECT n.*, u.name AS sender_name 
                FROM notifications n 
                JOIN users u ON n.sender_id = u.id 
                ORDER BY n.created_at DESC
            """).fetchall()
            notifications = [dict(r) for r in notif_rows]
            for n in notifications:
                if isinstance(n.get('created_at'), datetime):
                    n['created_at'] = n['created_at'].strftime('%Y-%m-%d %H:%M')
    except Exception as e:
        print(f"Error loading admin notifications: {e}")
        
    return render_template('admin/notifications.html', current_user=user, notifications=notifications, schools=schools, active_tab='notifications')


# ============================================================
# ADMIN — ANALYTICS
# ============================================================

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    user = get_current_user()
    stats = {}
    try:
        with get_db() as conn:
            stats['total_users'] = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()['c']
            stats['total_students'] = conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='student'").fetchone()['c']
            stats['total_teachers'] = conn.execute("SELECT COUNT(*) AS c FROM users WHERE role='teacher'").fetchone()['c']
            stats['total_courses'] = conn.execute("SELECT COUNT(*) AS c FROM courses").fetchone()['c']
            stats['total_chapters'] = conn.execute("SELECT COUNT(*) AS c FROM chapters").fetchone()['c']
            stats['total_quizzes'] = conn.execute("SELECT COUNT(*) AS c FROM quizzes").fetchone()['c']
            stats['total_tests'] = conn.execute("SELECT COUNT(*) AS c FROM tests").fetchone()['c']
            stats['total_certificates'] = conn.execute("SELECT COUNT(*) AS c FROM certificates WHERE status='issued'").fetchone()['c']
            stats['total_enrollments'] = conn.execute("SELECT COUNT(*) AS c FROM course_enrollments").fetchone()['c']
            dau = conn.execute("SELECT COUNT(DISTINCT user_id) AS c FROM user_history WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)").fetchone()['c']
            mau = conn.execute("SELECT COUNT(DISTINCT user_id) AS c FROM user_history WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)").fetchone()['c']
            stats['dau'] = dau or 0
            stats['mau'] = mau or 0
            # Top performing students
            top_students = conn.execute("""
                SELECT u.name, sp.current_xp, sp.level 
                FROM student_profiles sp 
                JOIN users u ON sp.user_id = u.id 
                ORDER BY sp.current_xp DESC 
                LIMIT 10
            """).fetchall()
            stats['top_students'] = [dict(r) for r in top_students]
            # Course enrollment counts
            top_courses = conn.execute("""
                SELECT c.title, COUNT(ce.id) AS enrolled_count 
                FROM courses c 
                LEFT JOIN course_enrollments ce ON c.id = ce.course_id 
                GROUP BY c.id, c.title 
                ORDER BY enrolled_count DESC 
                LIMIT 10
            """).fetchall()
            stats['top_courses'] = [dict(r) for r in top_courses]
            # Recent signups trend (last 7 days)
            signup_trend = conn.execute("""
                SELECT DATE(created_at) AS day, COUNT(*) AS count 
                FROM users 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) 
                GROUP BY DATE(created_at) 
                ORDER BY day ASC
            """).fetchall()
            stats['signup_trend'] = [{'day': str(r['day']), 'count': r['count']} for r in signup_trend]
    except Exception as e:
        print(f"Error loading analytics: {e}")
    return render_template('admin/analytics.html', current_user=user, stats=stats, active_tab='analytics')


# ============================================================
# ADMIN — ACTIVITY LOGS
# ============================================================

@app.route('/admin/activity')
@admin_required
def admin_activity():
    user = get_current_user()
    logs = []
    filters = {
        'event_type': request.args.get('event_type', ''),
        'user_id': request.args.get('user_id', ''),
        'limit': int(request.args.get('limit', 100))
    }
    try:
        with get_db() as conn:
            query = """
                SELECT h.*, u.name AS user_name, u.role AS user_role
                FROM user_history h
                LEFT JOIN users u ON h.user_id = u.id
                WHERE 1=1
            """
            params = []
            if filters['event_type']:
                query += " AND h.event_type = %s"
                params.append(filters['event_type'])
            if filters['user_id']:
                query += " AND h.user_id = %s"
                params.append(filters['user_id'])
            query += " ORDER BY h.created_at DESC LIMIT %s"
            params.append(filters['limit'])
            rows = conn.execute(query, tuple(params)).fetchall()
            for r in rows:
                l_dict = dict(r)
                if isinstance(l_dict.get('created_at'), datetime):
                    l_dict['created_at'] = l_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                logs.append(l_dict)
            # Also pull audit logs
            audit_rows = conn.execute("""
                SELECT a.*, u.name AS operator_name 
                FROM audit_logs a 
                LEFT JOIN users u ON a.user_id = u.id 
                ORDER BY a.created_at DESC 
                LIMIT 200
            """).fetchall()
            audit_logs = []
            for r in audit_rows:
                a_dict = dict(r)
                if isinstance(a_dict.get('created_at'), datetime):
                    a_dict['created_at'] = a_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                audit_logs.append(a_dict)
    except Exception as e:
        print(f"Error loading activity logs: {e}")
        audit_logs = []
    return render_template('admin/activity.html', current_user=user, logs=logs, audit_logs=audit_logs, filters=filters, active_tab='activity')


# ============================================================
# ADMIN — AI CENTER
# ============================================================

@app.route('/admin/ai', methods=['GET', 'POST'])
@admin_required
def admin_ai():
    user = get_current_user()
    ai_config = {
        'gemini_api_key': os.getenv('GEMINI_API_KEY', ''),
        'ai_enabled': True,
        'ai_model': os.getenv('AI_MODEL', 'gemini-2.0-flash'),
        'max_tokens': 2048,
        'temperature': 0.7
    }
    if request.method == 'POST':
        # In production, you'd update .env / DB config
        flash("AI configuration noted. Update the .env file to persist changes.", "success")
        return redirect(url_for('admin_ai'))
    return render_template('admin/ai.html', current_user=user, ai_config=ai_config, active_tab='ai')


# ============================================================
# ADMIN — PLATFORM SETTINGS
# ============================================================

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action', 'update_library')
        if action == 'update_library':
            category_name = request.form.get('category_name')
            access_mode = request.form.get('access_mode')
            if category_name and access_mode:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO library_settings (category_name, access_mode) 
                            VALUES (%s, %s) 
                            ON DUPLICATE KEY UPDATE access_mode = %s
                        """, (category_name, access_mode, access_mode))
                    log_audit("update_library_settings", f"Updated library access for {category_name} → {access_mode}")
                    flash(f"Library setting for '{category_name}' updated.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'update_permissions':
            permission_keys = ['can_create_chapters', 'can_edit_courses', 'can_manage_users', 'can_issue_certificates']
            try:
                with get_db() as conn:
                    for pk in permission_keys:
                        val = 1 if request.form.get(pk) else 0
                        conn.execute("""
                            INSERT INTO permissions (role, permission_key, is_granted)
                            VALUES ('content_manager', %s, %s)
                            ON DUPLICATE KEY UPDATE is_granted = %s
                        """, (pk, val, val))
                log_audit("update_cm_permissions", "Updated Content Manager role permissions")
                flash("Content Manager permissions updated.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        return redirect(url_for('admin_settings'))

    settings = []
    cm_perms = {}
    try:
        with get_db() as conn:
            settings = conn.execute("SELECT * FROM library_settings").fetchall()
            perm_rows = conn.execute("SELECT permission_key, is_granted FROM permissions WHERE role = 'content_manager'").fetchall()
            for p in perm_rows:
                cm_perms[p['permission_key']] = bool(p['is_granted'])
    except Exception as e:
        print(f"Error loading settings: {e}")
    return render_template('admin/settings.html', current_user=user, settings=settings, cm_perms=cm_perms, active_tab='settings')


# ============================================================
# ADMIN — SYSTEM TELEMETRY
# ============================================================

@app.route('/admin/system')
@admin_required
def admin_system():
    user = get_current_user()
    system_info = {}
    try:
        import platform
        import sys
        system_info['python_version'] = sys.version
        system_info['platform'] = platform.platform()
        system_info['flask_env'] = os.getenv('FLASK_ENV', 'production')
        system_info['db_host'] = db_config.get('host', 'N/A') if db_config else 'N/A'
        system_info['db_name'] = db_config.get('database', 'N/A') if db_config else 'N/A'
        system_info['ai_model'] = os.getenv('AI_MODEL', 'gemini-2.0-flash')
    except Exception as e:
        print(f"Error loading system info: {e}")

    db_tables = []
    db_size = 0
    try:
        with get_db() as conn:
            table_rows = conn.execute("""
                SELECT table_name, table_rows, 
                       ROUND((data_length + index_length) / 1024, 2) AS size_kb
                FROM information_schema.TABLES 
                WHERE table_schema = %s
                ORDER BY (data_length + index_length) DESC
            """, (db_config.get('database', ''),)).fetchall()
            db_tables = [dict(r) for r in table_rows]
            size_row = conn.execute("""
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS total_mb 
                FROM information_schema.TABLES 
                WHERE table_schema = %s
            """, (db_config.get('database', ''),)).fetchone()
            db_size = size_row['total_mb'] if size_row and size_row['total_mb'] else 0
    except Exception as e:
        print(f"Error loading DB telemetry: {e}")

    return render_template('admin/system.html', current_user=user, system_info=system_info, db_tables=db_tables, db_size=db_size, active_tab='system')


@app.route('/admin/labs', methods=['GET', 'POST'])
@content_manager_or_admin_required
def admin_labs():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        lab_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM labs WHERE id = %s", (lab_id,))
                log_audit("delete_lab", f"Deleted lab simulation node ID: {lab_id}")
                flash("Lab deleted successfully.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            title = request.form.get('title')
            chapter_id = request.form.get('chapter_id')
            description = request.form.get('description')
            status = request.form.get('status', 'published')
            if title:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO labs (public_id, title, chapter_id, description, status)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (str(uuid.uuid4()), title, chapter_id or None, description, status))
                    log_audit("create_lab", f"Created lab titration simulation: {title}")
                    flash("Lab registered successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'edit':
            title = request.form.get('title')
            chapter_id = request.form.get('chapter_id')
            description = request.form.get('description')
            status = request.form.get('status')
            if title and lab_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            UPDATE labs 
                            SET title = %s, chapter_id = %s, description = %s, status = %s
                            WHERE id = %s
                        """, (title, chapter_id or None, description, status, lab_id))
                    log_audit("update_lab", f"Updated titration lab ID: {lab_id}")
                    flash("Lab updated successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_labs'))

    with get_db() as conn:
        labs = conn.execute("""
            SELECT l.*, ch.title as chapter_title 
            FROM labs l 
            LEFT JOIN chapters ch ON l.chapter_id = ch.id 
            ORDER BY l.id DESC
        """).fetchall()
        chapters = conn.execute("SELECT id, title FROM chapters").fetchall()
    return render_template('admin/labs.html', current_user=user, labs=labs, chapters=chapters, active_tab='labs')


@app.route('/admin/reactions', methods=['GET', 'POST'])
@content_manager_or_admin_required
def admin_reactions():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        rxn_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM reactions WHERE id = %s", (rxn_id,))
                log_audit("delete_reaction", f"Deleted reaction equation node ID: {rxn_id}")
                flash("Reaction deleted successfully.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            rxn_id = request.form.get('id')
            name = request.form.get('name')
            equation = request.form.get('equation')
            reaction_type = request.form.get('reaction_type', 'organic')
            class_level = request.form.get('class_level')
            chapter_id = request.form.get('chapter_id')
            reactants = request.form.get('reactants', '[]')
            products = request.form.get('products', '[]')
            conditions = request.form.get('conditions')
            explanation = request.form.get('explanation')
            if rxn_id and name:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO reactions (id, public_id, name, equation, reaction_type, class_level, chapter_id, reactants, products, conditions, explanation)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (rxn_id, str(uuid.uuid4()), name, equation, reaction_type, class_level, chapter_id or None, reactants, products, conditions, explanation))
                    log_audit("create_reaction", f"Created reaction node: {name}")
                    flash("Reaction registered successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'edit':
            name = request.form.get('name')
            equation = request.form.get('equation')
            reaction_type = request.form.get('reaction_type')
            class_level = request.form.get('class_level')
            chapter_id = request.form.get('chapter_id')
            reactants = request.form.get('reactants', '[]')
            products = request.form.get('products', '[]')
            conditions = request.form.get('conditions')
            explanation = request.form.get('explanation')
            if name and rxn_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            UPDATE reactions 
                            SET name = %s, equation = %s, reaction_type = %s, class_level = %s, chapter_id = %s, reactants = %s, products = %s, conditions = %s, explanation = %s
                            WHERE id = %s
                        """, (name, equation, reaction_type, class_level, chapter_id or None, reactants, products, conditions, explanation, rxn_id))
                    log_audit("update_reaction", f"Updated reaction node ID: {rxn_id}")
                    flash("Reaction updated successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_reactions'))

    with get_db() as conn:
        reactions = conn.execute("""
            SELECT r.*, ch.title as chapter_title 
            FROM reactions r 
            LEFT JOIN chapters ch ON r.chapter_id = ch.id 
            ORDER BY r.name ASC
        """).fetchall()
        chapters = conn.execute("SELECT id, title FROM chapters").fetchall()
    return render_template('admin/reactions.html', current_user=user, reactions=reactions, chapters=chapters, active_tab='reactions')


@app.route('/admin/quizzes', methods=['GET', 'POST'])
@content_manager_or_admin_required
def admin_quizzes():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        quiz_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM quizzes WHERE id = %s", (quiz_id,))
                log_audit("delete_quiz", f"Deleted quiz node ID: {quiz_id}")
                flash("Quiz deleted successfully.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            chapter_id = request.form.get('chapter_id')
            title = request.form.get('title')
            total_marks = request.form.get('total_marks', 100)
            duration_minutes = request.form.get('duration_minutes', 30)
            if title and chapter_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO quizzes (public_id, chapter_id, title, total_marks, duration_minutes)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (str(uuid.uuid4()), chapter_id, title, total_marks, duration_minutes))
                    log_audit("create_quiz", f"Created quiz: {title}")
                    flash("Quiz registered successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'edit':
            title = request.form.get('title')
            chapter_id = request.form.get('chapter_id')
            total_marks = request.form.get('total_marks')
            duration_minutes = request.form.get('duration_minutes')
            if title and quiz_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            UPDATE quizzes 
                            SET title = %s, chapter_id = %s, total_marks = %s, duration_minutes = %s
                            WHERE id = %s
                        """, (title, chapter_id, total_marks, duration_minutes, quiz_id))
                    log_audit("update_quiz", f"Updated quiz ID: {quiz_id}")
                    flash("Quiz updated successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_quizzes'))

    with get_db() as conn:
        quizzes = conn.execute("""
            SELECT q.*, ch.title as chapter_title 
            FROM quizzes q 
            LEFT JOIN chapters ch ON q.chapter_id = ch.id 
            ORDER BY q.id DESC
        """).fetchall()
        chapters = conn.execute("SELECT id, title FROM chapters").fetchall()
    return render_template('admin/quizzes.html', current_user=user, quizzes=quizzes, chapters=chapters, active_tab='quizzes')


@app.route('/admin/assignments', methods=['GET', 'POST'])
@content_manager_or_admin_required
def admin_assignments():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        assignment_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM assignments WHERE id = %s", (assignment_id,))
                log_audit("delete_assignment", f"Deleted assignment node ID: {assignment_id}")
                flash("Assignment deleted successfully.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            title = request.form.get('title')
            description = request.form.get('description')
            classroom_id = request.form.get('classroom_id')
            chapter_id = request.form.get('chapter_id')
            lab_id = request.form.get('lab_id')
            marks = request.form.get('marks', 100)
            due_date = request.form.get('due_date')
            status = request.form.get('status', 'draft')
            if title and classroom_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO assignments (public_id, title, description, classroom_id, chapter_id, lab_id, marks, due_date, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (str(uuid.uuid4()), title, description, classroom_id, chapter_id or None, lab_id or None, marks, due_date or None, status))
                    log_audit("create_assignment", f"Created assignment: {title}")
                    flash("Assignment registered successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'edit':
            title = request.form.get('title')
            description = request.form.get('description')
            classroom_id = request.form.get('classroom_id')
            chapter_id = request.form.get('chapter_id')
            lab_id = request.form.get('lab_id')
            marks = request.form.get('marks')
            due_date = request.form.get('due_date')
            status = request.form.get('status')
            if title and assignment_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            UPDATE assignments 
                            SET title = %s, description = %s, classroom_id = %s, chapter_id = %s, lab_id = %s, marks = %s, due_date = %s, status = %s
                            WHERE id = %s
                        """, (title, description, classroom_id, chapter_id or None, lab_id or None, marks, due_date or None, status, assignment_id))
                    log_audit("update_assignment", f"Updated assignment ID: {assignment_id}")
                    flash("Assignment updated successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_assignments'))

    with get_db() as conn:
        assignments = conn.execute("""
            SELECT a.*, cl.name as classroom_name, ch.title as chapter_title, l.title as lab_title 
            FROM assignments a 
            LEFT JOIN classrooms cl ON a.classroom_id = cl.id
            LEFT JOIN chapters ch ON a.chapter_id = ch.id
            LEFT JOIN labs l ON a.lab_id = l.id
            ORDER BY a.id DESC
        """).fetchall()
        classrooms = conn.execute("SELECT id, name FROM classrooms").fetchall()
        chapters = conn.execute("SELECT id, title FROM chapters").fetchall()
        labs = conn.execute("SELECT id, title FROM labs").fetchall()
    return render_template('admin/assignments.html', current_user=user, assignments=assignments, classrooms=classrooms, chapters=chapters, labs=labs, active_tab='assignments')


@app.route('/admin/tests', methods=['GET', 'POST'])
@content_manager_or_admin_required
def admin_tests():
    user = get_current_user()
    if request.method == 'POST':
        action = request.form.get('action')
        test_id = request.form.get('id')
        if action == 'delete':
            try:
                with get_db() as conn:
                    conn.execute("DELETE FROM tests WHERE id = %s", (test_id,))
                log_audit("delete_test", f"Deleted test node ID: {test_id}")
                flash("Test deleted successfully.", "success")
            except Exception as e:
                flash(f"Error: {e}", "error")
        elif action == 'create':
            title = request.form.get('title')
            classroom_id = request.form.get('classroom_id')
            chapter_id = request.form.get('chapter_id')
            quiz_content_id = request.form.get('quiz_content_id')
            duration_minutes = request.form.get('duration_minutes', 30)
            total_marks = request.form.get('total_marks', 100)
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            difficulty = request.form.get('difficulty', 'medium')
            status = request.form.get('status', 'scheduled')
            if title and classroom_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            INSERT INTO tests (public_id, title, classroom_id, chapter_id, quiz_content_id, duration_minutes, total_marks, start_date, end_date, difficulty, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (str(uuid.uuid4()), title, classroom_id, chapter_id or None, quiz_content_id or None, duration_minutes, total_marks, start_date or None, end_date or None, difficulty, status))
                    log_audit("create_test", f"Scheduled exam test: {title}")
                    flash("Test registered successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        elif action == 'edit':
            title = request.form.get('title')
            classroom_id = request.form.get('classroom_id')
            chapter_id = request.form.get('chapter_id')
            quiz_content_id = request.form.get('quiz_content_id')
            duration_minutes = request.form.get('duration_minutes')
            total_marks = request.form.get('total_marks')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            difficulty = request.form.get('difficulty')
            status = request.form.get('status')
            if title and test_id:
                try:
                    with get_db() as conn:
                        conn.execute("""
                            UPDATE tests 
                            SET title = %s, classroom_id = %s, chapter_id = %s, quiz_content_id = %s, duration_minutes = %s, total_marks = %s, start_date = %s, end_date = %s, difficulty = %s, status = %s
                            WHERE id = %s
                        """, (title, classroom_id, chapter_id or None, quiz_content_id or None, duration_minutes, total_marks, start_date or None, end_date or None, difficulty, status, test_id))
                    log_audit("update_test", f"Updated test ID: {test_id}")
                    flash("Test updated successfully.", "success")
                except Exception as e:
                    flash(f"Error: {e}", "error")
        return redirect(url_for('admin_tests'))

    with get_db() as conn:
        tests = conn.execute("""
            SELECT t.*, cl.name as classroom_name, ch.title as chapter_title 
            FROM tests t 
            LEFT JOIN classrooms cl ON t.classroom_id = cl.id
            LEFT JOIN chapters ch ON t.chapter_id = ch.id
            ORDER BY t.id DESC
        """).fetchall()
        classrooms = conn.execute("SELECT id, name FROM classrooms").fetchall()
        chapters = conn.execute("SELECT id, title FROM chapters").fetchall()
        quizzes = conn.execute("SELECT id, title FROM quizzes").fetchall()
    return render_template('admin/tests.html', current_user=user, tests=tests, classrooms=classrooms, chapters=chapters, quizzes=quizzes, active_tab='tests')


# ============================================================
# API — CONTENT MANAGEMENT (Admin/Teacher)
# ============================================================

@app.route('/api/admin/chapters', methods=['POST', 'PUT', 'DELETE'])
def api_admin_chapters():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher', 'content_manager'):
        return jsonify({"error": "Forbidden"}), 403
        
    if request.method == 'POST':
        payload = request.get_json(silent=True) or {}
        course_id = payload.get("course_id")
        module_id = payload.get("module_id")
        class_level = payload.get("class_level")
        chapter_number = payload.get("chapter_number")
        title = payload.get("title")
        description = payload.get("description")
        status = payload.get("status", "published")
        publish_at = payload.get("publish_at")
        order_index = payload.get("order_index", 0)
        
        # Text fields
        key_points = payload.get("key_points", "")
        notes = payload.get("notes", "")
        formulas = payload.get("formulas", "")
        reactions = payload.get("reactions", "")
        experiment_content = payload.get("experiment_content", "")
        
        if not title:
            return jsonify({"error": "Missing title"}), 400
            
        try:
            with get_db() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO chapters (
                        course_id, module_id, class_level, chapter_number, title, description,
                        key_points, notes, formulas, reactions, experiment_content,
                        overview_content, key_points_content, formula_content, reaction_content, practice_content,
                        learning_objectives, important_laws, constants, important_reactions,
                        virtual_labs, practice_questions, common_mistakes, difficulty,
                        estimated_study_time, chapter_weightage, next_chapter, status, publish_at, order_index
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', 'Beginner', '4 Hours', '{}', '{}', %s, %s, %s)
                    """,
                    (
                        course_id, module_id, class_level, chapter_number, title, description,
                        key_points, notes, formulas, reactions, experiment_content,
                        notes, key_points, formulas, reactions,
                        status, publish_at, order_index
                    )
                )
                chapter_id = cursor.lastrowid
                print("Chapter Saved:", chapter_id)
                
            # Check-in version 1 (outside main transaction to avoid self-deadlock)
            ch_data = {
                "course_id": course_id,
                "module_id": module_id,
                "class_level": class_level,
                "chapter_number": chapter_number,
                "title": title,
                "description": description,
                "key_points": key_points,
                "notes": notes,
                "formulas": formulas,
                "reactions": reactions,
                "experiment_content": experiment_content,
                "learning_objectives": [],
                "important_laws": [],
                "constants": [],
                "important_reactions": [],
                "virtual_labs": [],
                "practice_questions": [],
                "common_mistakes": [],
                "difficulty": "Beginner",
                "estimated_study_time": "4 Hours",
                "chapter_weightage": {},
                "next_chapter": {},
                "status": status,
                "order_index": order_index,
                "publish_at": str(publish_at) if publish_at else None
            }
            check_in_version('chapter', chapter_id, title, ch_data, user['id'])
                
            return jsonify({"ok": True, "id": chapter_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    elif request.method == 'PUT':
        payload = request.get_json(silent=True) or {}
        ch_id = payload.get("id")
        if not ch_id:
            return jsonify({"error": "Missing chapter id"}), 400
            
        try:
            with get_db() as conn:
                curr = conn.execute("SELECT * FROM chapters WHERE id = %s", (ch_id,)).fetchone()
            if not curr:
                return jsonify({"error": "Chapter not found"}), 404
            
            curr_dict = dict(curr)
            course_id = payload.get("course_id") if "course_id" in payload else curr_dict.get("course_id")
            module_id = payload.get("module_id") if "module_id" in payload else curr_dict.get("module_id")
            class_level = payload.get("class_level", curr_dict["class_level"])
            chapter_number = payload.get("chapter_number", curr_dict["chapter_number"])
            title = payload.get("title", curr_dict["title"])
            description = payload.get("description", curr_dict["description"])
            
            # Direct text fields
            key_points = payload.get("key_points") if "key_points" in payload else curr_dict.get("key_points", "")
            notes = payload.get("notes") if "notes" in payload else curr_dict.get("notes", "")
            formulas = payload.get("formulas") if "formulas" in payload else curr_dict.get("formulas", "")
            reactions = payload.get("reactions") if "reactions" in payload else curr_dict.get("reactions", "")
            experiment_content = payload.get("experiment_content") if "experiment_content" in payload else curr_dict.get("experiment_content", "")
            
            def load_or_keep(field):
                if field in payload:
                    return payload[field]
                return safe_json_loads(curr_dict.get(field, '[]'))
                
            learning_objectives = load_or_keep("learning_objectives")
            important_laws = load_or_keep("important_laws")
            constants = load_or_keep("constants")
            important_reactions = load_or_keep("important_reactions")
            virtual_labs = load_or_keep("virtual_labs")
            practice_questions = load_or_keep("practice_questions")
            common_mistakes = load_or_keep("common_mistakes")
            
            difficulty = payload.get("difficulty", curr_dict.get("difficulty", "Beginner"))
            estimated_study_time = payload.get("estimated_study_time", curr_dict.get("estimated_study_time", "4 Hours"))
            chapter_weightage = payload.get("chapter_weightage") or safe_json_loads(curr_dict.get("chapter_weightage", "{}"))
            next_chapter = payload.get("next_chapter") or safe_json_loads(curr_dict.get("next_chapter", "{}"))
            
            status = payload.get("status", curr_dict.get("status", "draft"))
            order_index = payload.get("order_index", curr_dict.get("order_index", 0))
            publish_at = payload.get("publish_at", curr_dict.get("publish_at"))
            
            with get_db() as conn:
                conn.execute(
                    """
                    UPDATE chapters SET 
                        course_id = %s, module_id = %s, class_level = %s, chapter_number = %s, title = %s, description = %s,
                        key_points = %s, notes = %s, formulas = %s, reactions = %s, experiment_content = %s,
                        overview_content = %s, key_points_content = %s, formula_content = %s, reaction_content = %s, practice_content = %s,
                        learning_objectives = %s, important_laws = %s, constants = %s, important_reactions = %s,
                        virtual_labs = %s, practice_questions = %s, common_mistakes = %s, difficulty = %s,
                        estimated_study_time = %s, chapter_weightage = %s, next_chapter = %s,
                        status = %s, order_index = %s, publish_at = %s
                    WHERE id = %s
                    """,
                    (
                        course_id, module_id, class_level, chapter_number, title, description,
                        key_points, notes, formulas, reactions, experiment_content,
                        notes, key_points, formulas, reactions, json.dumps(practice_questions),
                        json.dumps(learning_objectives), json.dumps(important_laws), json.dumps(constants), json.dumps(important_reactions),
                        json.dumps(virtual_labs), json.dumps(practice_questions), json.dumps(common_mistakes), difficulty,
                        estimated_study_time, json.dumps(chapter_weightage), json.dumps(next_chapter),
                        status, order_index, publish_at,
                        ch_id
                    )
                )
                print("Chapter Saved:", ch_id)
                
            # Check-in version (outside main transaction to avoid self-deadlock)
            ch_data = {
                "course_id": course_id,
                "module_id": module_id,
                "class_level": class_level,
                "chapter_number": chapter_number,
                "title": title,
                "description": description,
                "key_points": key_points,
                "notes": notes,
                "formulas": formulas,
                "reactions": reactions,
                "experiment_content": experiment_content,
                "learning_objectives": learning_objectives,
                "important_laws": important_laws,
                "constants": constants,
                "important_reactions": important_reactions,
                "notes": notes,
                "real_life_applications": curr_dict.get("real_life_applications", {}),
                "virtual_labs": virtual_labs,
                "practice_questions": practice_questions,
                "common_mistakes": common_mistakes,
                "difficulty": difficulty,
                "estimated_study_time": estimated_study_time,
                "chapter_weightage": chapter_weightage,
                "next_chapter": next_chapter,
                "status": status,
                "order_index": order_index,
                "publish_at": str(publish_at) if publish_at else None
            }
            check_in_version('chapter', ch_id, title, ch_data, user['id'])
                
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    elif request.method == 'DELETE':
        ch_id = request.args.get("id")
        if not ch_id:
            return jsonify({"error": "Missing chapter id"}), 400
        with get_db() as conn:
            conn.execute("DELETE FROM chapters WHERE id = %s", (ch_id,))
        return jsonify({"ok": True})


@app.route('/admin/debug/chapter/<string:chapter_uuid>')
def admin_debug_chapter(chapter_uuid):
    if chapter_uuid.isdigit():
        with get_db() as conn:
            row = conn.execute("SELECT public_id FROM chapters WHERE id = %s", (chapter_uuid,)).fetchone()
            if row:
                return redirect(url_for('admin_debug_chapter', chapter_uuid=row['public_id']), code=301)

    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher'):
        return "Forbidden", 403
        
    try:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM chapters WHERE public_id = %s", (chapter_uuid,)).fetchone()
            
        if not row:
            return f"Chapter {chapter_uuid} not found", 404
            
        chapter_id = row['id']
            
        ch = dict(row)
        char_counts = {}
        missing_fields = []
        
        for k, v in ch.items():
            if v is None:
                missing_fields.append(k)
                char_counts[k] = 0
            else:
                char_counts[k] = len(str(v))
                
        debug_info = {
            "chapter_id": chapter_id,
            "raw_mysql_values": {
                "id": ch.get("id"),
                "course_id": ch.get("course_id"),
                "class_level": ch.get("class_level"),
                "chapter_number": ch.get("chapter_number"),
                "title": ch.get("title"),
                "description": ch.get("description"),
                "key_points": ch.get("key_points"),
                "notes": ch.get("notes"),
                "formulas": ch.get("formulas"),
                "reactions": ch.get("reactions"),
                "experiment_content": ch.get("experiment_content"),
                "created_at": str(ch.get("created_at")),
                "updated_at": str(ch.get("updated_at"))
            },
            "character_counts": char_counts,
            "missing_fields": missing_fields,
            "last_updated": str(ch.get("updated_at") or ch.get("created_at"))
        }
        
        return jsonify(debug_info)
    except Exception as e:
        return f"Error: {e}", 500


@app.route('/api/admin/reactions', methods=['POST', 'PUT', 'DELETE'])
def api_admin_reactions():
    user = get_current_user()
    if not user or user['role'] not in ('admin', 'teacher', 'content_manager'):
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
    if not user or user['role'] not in ('admin', 'teacher', 'content_manager'):
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
    if not user or user['role'] not in ('admin', 'teacher', 'content_manager'):
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
# API — NOTIFICATIONS
# ============================================================

@app.route('/api/notifications', methods=['GET'])
def api_notifications():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    role = user['role']
    institution = user['institution']
    class_level = user.get('class_level') or user.get('classLevel') or 'all'
    if not class_level:
        class_level = 'all'

    try:
        with get_db() as conn:
            rows = conn.execute("""
                SELECT n.*, u.name AS sender_name,
                       (CASE WHEN nr.user_id IS NOT NULL THEN 1 ELSE 0 END) AS is_read
                FROM notifications n
                JOIN users u ON n.sender_id = u.id
                LEFT JOIN notification_reads nr ON n.id = nr.notification_id AND nr.user_id = %s
                WHERE (n.target_role = 'all' OR n.target_role = %s)
                  AND (n.target_institution = 'all' OR n.target_institution = %s)
                  AND (n.target_class_level = 'all' OR n.target_class_level = %s)
                ORDER BY n.created_at DESC
                LIMIT 50
            """, (user['id'], role, institution, class_level)).fetchall()
            
            notifications = [dict(r) for r in rows]
            for n in notifications:
                if isinstance(n.get('created_at'), datetime):
                    n['created_at'] = n['created_at'].strftime('%Y-%m-%d %H:%M')
            
            unread_count = sum(1 for n in notifications if not n['is_read'])
            
            return jsonify({
                "notifications": notifications,
                "unread_count": unread_count
            })
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/notifications/read', methods=['POST'])
def api_notifications_read():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    payload = request.get_json(silent=True) or {}
    notif_id = payload.get("id")
    mark_all = payload.get("all", False)
    
    try:
        with get_db() as conn:
            if mark_all:
                role = user['role']
                institution = user['institution']
                class_level = user.get('class_level') or user.get('classLevel') or 'all'
                if not class_level:
                    class_level = 'all'
                
                notif_rows = conn.execute("""
                    SELECT n.id 
                    FROM notifications n
                    LEFT JOIN notification_reads nr ON n.id = nr.notification_id AND nr.user_id = %s
                    WHERE nr.user_id IS NULL
                      AND (n.target_role = 'all' OR n.target_role = %s)
                      AND (n.target_institution = 'all' OR n.target_institution = %s)
                      AND (n.target_class_level = 'all' OR n.target_class_level = %s)
                """, (user['id'], role, institution, class_level)).fetchall()
                
                for row in notif_rows:
                    conn.execute("""
                        INSERT IGNORE INTO notification_reads (user_id, notification_id)
                        VALUES (%s, %s)
                    """, (user['id'], row['id']))
            elif notif_id:
                conn.execute("""
                    INSERT IGNORE INTO notification_reads (user_id, notification_id)
                    VALUES (%s, %s)
                """, (user['id'], notif_id))
            else:
                return jsonify({"error": "Missing notification id"}), 400
                
            return jsonify({"ok": True})
    except Exception as e:
        print(f"Error marking notification read: {e}")
        return jsonify({"error": str(e)}), 500


# API — AI CHEMISTRY TUTOR REMOVED (Consolidated above)


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
    user = get_current_user()
    class_level = request.args.get("class_level")
    
    # Default to user's own class if student
    if not class_level and user and user.get('role') == 'student':
        class_level = user.get('classLevel')
        
    with get_db() as conn:
        if class_level and class_level != 'all':
            rows = conn.execute(
                """
                SELECT u.name, u.institution, sp.current_xp, sp.level,
                       RANK() OVER (ORDER BY sp.current_xp DESC) AS `rank`
                FROM student_profiles sp
                JOIN users u ON sp.user_id = u.id
                WHERE u.class_level = %s
                ORDER BY sp.current_xp DESC
                LIMIT %s
                """,
                (class_level, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT u.name, u.institution, sp.current_xp, sp.level,
                       RANK() OVER (ORDER BY sp.current_xp DESC) AS `rank`
                FROM student_profiles sp
                JOIN users u ON sp.user_id = u.id
                ORDER BY sp.current_xp DESC
                LIMIT %s
                """,
                (limit,)
            ).fetchall()
    return jsonify({"leaderboard": [dict(r) for r in rows]})


    return jsonify({"leaderboard": [dict(r) for r in rows]})


# ============================================================
# API — AI SCIENTIST & VIRTUAL LAB MASTER
# ============================================================

@app.route('/api/ai/scientist', methods=['POST'])
def api_ai_scientist():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    payload = request.get_json(silent=True) or {}
    user_query = payload.get("user_query", "").strip()
    experiment_name = payload.get("experiment_name", "Sandbox")
    chemicals = [c.strip() for c in payload.get("chemicals_in_flask", []) if c.strip()]
    telemetry = payload.get("telemetry", {})
    ph = telemetry.get("ph", 7.0)
    temp = telemetry.get("temp", 24.5)
    
    # Analyze active compounds in flask
    has_acid = any(c in ['HCl', 'HNO3', 'H2SO4', 'CH3COOH'] for c in chemicals)
    has_base = any(c in ['NaOH', 'KOH', 'Ca(OH)2'] for c in chemicals)
    has_ch4 = 'CH4' in chemicals
    has_o2 = 'O2' in chemicals
    has_kclo3 = 'KClO3' in chemicals
    has_fe = 'Fe' in chemicals
    has_cuso4 = 'CuSO4' in chemicals
    
    response_text = ""
    predicted_product = "N/A"
    suggested_next = "N/A"
    viva_questions = []
    lab_report = {}
    
    # Default outputs based on chemicals
    if has_acid and has_base:
        predicted_product = "Salt + Water (e.g. NaCl + H2O)"
        suggested_next = "Indicator (like Phenolphthalein) to test pH equivalence"
        viva_questions = [
            "Why does acid-base neutralization increase the temperature?",
            "What defines a strong acid versus a weak acid?",
            "What is the spectator ion in this neutralization?"
        ]
        lab_report = {
            "objective": "To perform acid-base neutralization between acid and base.",
            "procedure": "1. Measure acid and base reagents.\n2. Dispense acid into the flask.\n3. Add base drop-by-drop until pH reaches 7.0.",
            "observations": f"The temperature rose to {temp}°C, indicating an exothermic reaction. The pH stabilized at {ph}.",
            "calculations": "n(Acid) = Concentration * Volume = n(Base)",
            "result": "Successful synthesis of neutral salt solution.",
            "conclusion": "The reaction completed cleanly. Hydroxide and hydronium ions formed neutral water."
        }
        
        if "Explain" in user_query or "explain" in user_query.lower():
            response_text = "The hydronium ions (H⁺) from the acid are combining with the hydroxide ions (OH⁻) from the base to produce neutral water molecules (H₂O). This neutralization reaction is exothermic, releasing thermal energy and causing the temperature to rise."
        elif "Predict" in user_query or "predict" in user_query.lower():
            response_text = "The reaction will produce water and a dissolved salt. For example, HCl + NaOH will yield NaCl (Sodium Chloride) and H₂O."
        elif "Suggest" in user_query or "suggest" in user_query.lower():
            response_text = "To find the exact endpoint, you should add an indicator such as Phenolphthalein, which changes from colorless to pink as the solution crosses pH 8.3."
        else:
            response_text = "I observe an acid-base neutralization. Adding more base will increase the pH, while adding more acid will decrease it."
            
    elif has_ch4 and has_o2:
        predicted_product = "CO2 + H2O + Heat (Carbon Dioxide and Water)"
        suggested_next = "Measure carbon dioxide levels or collect water vapor"
        viva_questions = [
            "Why is combustion of methane classified as a redox reaction?",
            "What is the activation energy required for methane combustion?",
            "How does limiting oxygen affect the combustion products?"
        ]
        lab_report = {
            "objective": "To observe the combustion of methane in the presence of oxygen.",
            "procedure": "1. Introduce methane (CH4) gas into the chamber.\n2. Supply oxygen (O2).\n3. Ignite to initiate combustion.",
            "observations": f"Rapid heat release (temperature reached {temp}°C). Carbon dioxide and water vapor were generated.",
            "calculations": "CH4 + 2O2 -> CO2 + 2H2O",
            "result": "Methane fully combusted into carbon dioxide and water.",
            "conclusion": "Combustion of hydrocarbons is highly exothermic and yields carbon dioxide and water under sufficient oxygen supply."
        }
        if "Explain" in user_query or "explain" in user_query.lower():
            response_text = "Methane is reacting with oxygen in a combustion reaction. The C-H bonds in methane and O=O bonds in oxygen are broken, forming more stable C=O bonds in carbon dioxide and H-O bonds in water, releasing a significant amount of heat."
        elif "Predict" in user_query or "predict" in user_query.lower():
            response_text = "Methane combustion produces Carbon Dioxide (CO₂) and Water (H₂O) along with significant heat release."
        else:
            response_text = "Methane combustion is active. The carbon atoms are being oxidized, and oxygen atoms are being reduced."
            
    elif has_kclo3:
        predicted_product = "2KCl + 3O2 (Potassium Chloride and Oxygen Gas)"
        suggested_next = "Heat the flask using the burner setup to decompose KClO3"
        viva_questions = [
            "What is the role of MnO2 catalyst in the decomposition of KClO3?",
            "How do you test for the presence of oxygen gas?",
            "What type of chemical reaction is this decomposition?"
        ]
        lab_report = {
            "objective": "Preparation of Oxygen gas via thermal decomposition of Potassium Chlorate.",
            "procedure": "1. Add solid Potassium Chlorate (KClO3) to the flask.\n2. Heat the flask using the burner.\n3. Collect the evolved gas via downward displacement of water.",
            "observations": "Gas bubbles evolved rapidly upon heating. A white solid residue of KCl remained at the bottom.",
            "calculations": "2KClO3 -> 2KCl + 3O2",
            "result": "Oxygen gas successfully prepared and collected.",
            "conclusion": "Thermal decomposition of chlorates yields chloride salt and oxygen gas."
        }
        if "Explain" in user_query or "explain" in user_query.lower():
            response_text = "Upon heating, Potassium Chlorate decomposes thermally to produce Potassium Chloride solid and oxygen gas. This is a decomposition reaction."
        elif "Predict" in user_query or "predict" in user_query.lower():
            response_text = "The thermal decomposition of KClO₃ yields Potassium Chloride (KCl) solid residue and Oxygen (O₂) gas."
        else:
            response_text = "This setup is configured for Oxygen preparation. Apply heat to trigger decomposition of Potassium Chlorate!"
            
    elif has_fe and has_cuso4:
        predicted_product = "FeSO4 + Cu (Iron(II) Sulfate and Metallic Copper)"
        suggested_next = "Filter the mixture to retrieve the precipitated copper"
        viva_questions = [
            "Why does iron displace copper from its sulfate solution?",
            "What color change is observed in the solution during this reaction?",
            "Is this reaction a redox reaction?"
        ]
        lab_report = {
            "objective": "To study the displacement reaction between Iron and Copper Sulfate.",
            "procedure": "1. Dispense blue Copper Sulfate (CuSO4) solution into the flask.\n2. Add metallic Iron (Fe).\n3. Wait for the displacement reaction to occur.",
            "observations": "The blue solution gradually turned green (FeSO4). A reddish-brown deposit of copper formed on the iron.",
            "calculations": "Fe + CuSO4 -> FeSO4 + Cu",
            "result": "Iron successfully displaced copper, producing copper precipitate.",
            "conclusion": "Iron is more reactive than copper, displacing it in a single displacement redox reaction."
        }
        if "Explain" in user_query or "explain" in user_query.lower():
            response_text = "Iron is more electropositive (reactive) than copper. It loses electrons to copper ions, dissolving to form Iron(II) Sulfate (green solution) while metallic copper deposits as a reddish-brown precipitate."
        elif "Predict" in user_query or "predict" in user_query.lower():
            response_text = "The products are Iron(II) Sulfate (FeSO₄) in solution and solid Copper (Cu) precipitate."
        else:
            response_text = "I observe a displacement reaction. Iron is displacing copper due to its higher reactivity."
    else:
        predicted_product = "N/A (No reaction active)"
        suggested_next = "Add compatible reagents (e.g. Acid + Base, or Hydrocarbon + Oxygen)"
        viva_questions = [
            "What is the definition of a chemical element?",
            "How does temperature affect chemical reaction rates?",
            "What is the pH scale and what does it measure?"
        ]
        lab_report = {
            "objective": "General chemical exploration inside the Virtual Sandbox.",
            "procedure": f"1. Select chemicals from the shelf.\n2. Dispense them into the flask drop-zone.\n3. Observe telemetry changes.",
            "observations": f"Flask currently contains: {', '.join(chemicals) if chemicals else 'No chemicals'}. pH is {ph} and Temperature is {temp}°C.",
            "calculations": "N/A",
            "result": "Explored chemical combinations.",
            "conclusion": "Sandbox simulator is fully operational."
        }
        
        if "ph" in user_query.lower():
            response_text = f"The current pH is {ph}. In chemistry, pH is a scale used to specify the acidity or basicity of an aqueous solution. Acidic solutions have a lower pH, while basic solutions have a higher pH."
        elif "temp" in user_query.lower() or "temperature" in user_query.lower():
            response_text = f"The current temperature is {temp}°C. Dissolving solutes or mixing reagents can release heat (exothermic) or absorb heat (endothermic), altering the flask temperature."
        elif "next" in user_query.lower() or "suggest" in user_query.lower():
            response_text = "To start an experiment, try adding Hydrochloric Acid (HCl) and Sodium Hydroxide (NaOH) to perform an acid-base neutralization reaction."
        elif "report" in user_query.lower() or "generate" in user_query.lower():
            response_text = "Lab report outline generated. You can click 'Generate Lab Report' to download the full documentation!"
        else:
            response_text = f"Hello! I am your AI Scientist. I observe the flask currently contains {', '.join(chemicals) if chemicals else 'no chemicals'}. The pH is {ph} and temperature is {temp}°C."

    return jsonify({
        "response": response_text,
        "predicted_product": predicted_product,
        "suggested_next": suggested_next,
        "viva_questions": viva_questions,
        "lab_report": lab_report
    })


@app.route('/api/student/lab/reward', methods=['POST'])
def api_student_lab_reward():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    payload = request.get_json(silent=True) or {}
    xp_amount = int(payload.get("xp", 50))
    mission_name = payload.get("mission", "Experiment Completion")
    
    try:
        with get_db() as conn:
            sp = conn.execute("SELECT current_xp, level FROM student_profiles WHERE user_id = %s", (user["id"],)).fetchone()
            if not sp:
                conn.execute("INSERT IGNORE INTO student_profiles (user_id, current_xp, level) VALUES (%s, 100, 1)", (user["id"],))
                current_xp = 100
                current_level = 1
            else:
                current_xp = sp["current_xp"]
                current_level = sp["level"]
                
            new_xp = current_xp + xp_amount
            lvl_info = get_level_info(new_xp)
            new_level = lvl_info["level"]
            
            conn.execute(
                "UPDATE student_profiles SET current_xp = %s, level = %s WHERE user_id = %s",
                (new_xp, new_level, user["id"])
            )
            
            conn.execute(
                "INSERT INTO user_history (user_id, event_type, event_data) VALUES (%s, 'lab_reward', %s)",
                (user["id"], f"xp={xp_amount}, mission={mission_name}")
            )
            
            if new_level >= 3:
                conn.execute(
                    "INSERT IGNORE INTO user_badges (user_id, badge_id, unlocked_at) VALUES (%s, 3, NOW())",
                    (user["id"],)
                )
                
            return jsonify({
                "ok": True,
                "xp_added": xp_amount,
                "total_xp": new_xp,
                "level": new_level,
                "level_title": lvl_info["title"],
                "level_up": new_level > current_level
            })
    except Exception as e:
        print(f"Error rewarding student: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/student/lab/attempt', methods=['POST'])
def api_student_lab_attempt():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    payload = request.get_json(silent=True) or {}
    experiment_name = payload.get("experiment_name", "Sandbox Explorer")
    mode = payload.get("mode", "sandbox")
    duration = int(payload.get("duration_seconds", 0))
    mistakes = int(payload.get("mistakes_count", 0))
    accuracy = int(payload.get("accuracy_percentage", 100))
    
    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO lab_attempts (user_id, experiment_name, mode, duration_seconds, mistakes_count, accuracy_percentage)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user["id"], experiment_name, mode, duration, mistakes, accuracy)
            )
        return jsonify({"ok": True})
    except Exception as e:
        print(f"Error saving lab attempt: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/teacher/lab_attempts', methods=['GET'])
def api_teacher_lab_attempts():
    user = get_current_user()
    if not user or user['role'] not in ('teacher', 'admin'):
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        with get_db() as conn:
            rows = conn.execute(
                """
                SELECT la.*, u.name AS student_name, u.class_level
                FROM lab_attempts la
                JOIN users u ON la.user_id = u.id
                ORDER BY la.completed_at DESC
                """
            ).fetchall()
        return jsonify({"attempts": [dict(r) for r in rows]})
    except Exception as e:
        print(f"Error fetching lab attempts: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
