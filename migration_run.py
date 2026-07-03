import os
import uuid
import urllib.parse
from dotenv import load_dotenv

# Load environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found in environment!")

# Parse database configuration
parsed = urllib.parse.urlparse(DATABASE_URL)
database = parsed.path.lstrip('/')
port = parsed.port if parsed.port is not None else 3306
db_config = {
    "host": parsed.hostname or "localhost",
    "port": port,
    "user": urllib.parse.unquote(parsed.username or "root"),
    "password": urllib.parse.unquote(parsed.password or ""),
    "database": database,
    "autocommit": True
}
if parsed.query:
    query_params = urllib.parse.parse_qs(parsed.query)
    # Enable SSL connection dynamically if ssl parameters are in config
    if any('ssl' in k.lower() for k in query_params.keys()) or 'ssl-mode' in query_params:
        db_config["ssl"] = {}

# Import connection library
try:
    import pymysql
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    print("Successfully connected using PyMySQL.")
except Exception as e:
    print(f"PyMySQL failed: {e}. Trying mysql.connector...")
    import mysql.connector
    # Filter config for mysql.connector
    valid_keys = {
        'host', 'port', 'user', 'password', 'database',
        'ssl_ca', 'ssl_cert', 'ssl_key', 'ssl_capath', 'ssl_cipher',
        'charset', 'collation', 'connection_timeout', 'autocommit'
    }
    conn_config = {k: v for k, v in db_config.items() if k in valid_keys}
    if "ssl" in db_config:
        conn_config["ssl_disabled"] = False
    conn = mysql.connector.connect(**conn_config)
    cursor = conn.cursor(dictionary=True)
    print("Successfully connected using mysql.connector.")

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

for table in tables:
    print(f"\nProcessing table: {table}")
    
    # 1. Check if table exists
    cursor.execute(f"SHOW TABLES LIKE '{table}'")
    if not cursor.fetchone():
        print(f"Table '{table}' does not exist. Skipping.")
        continue
        
    # 2. Check if public_id column exists
    cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE 'public_id'")
    col_exists = cursor.fetchone()
    
    if not col_exists:
        print(f"Adding public_id column to '{table}'...")
        cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN public_id VARCHAR(36) DEFAULT NULL")
    else:
        print(f"public_id column already exists in '{table}'.")

    # 3. Generate UUIDs for all rows
    cursor.execute(f"SELECT * FROM `{table}`")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} records in '{table}'.")
    
    updated_count = 0
    for row in rows:
        # Check if record already has a public_id (idempotency check)
        if not row.get("public_id"):
            new_uuid = str(uuid.uuid4())
            # Note: reactions table has a string id, but WHERE id = %s still works perfectly
            cursor.execute(
                f"UPDATE `{table}` SET public_id = %s WHERE id = %s",
                (new_uuid, row["id"])
            )
            updated_count += 1
            
    if updated_count > 0:
        print(f"Generated UUIDs for {updated_count} records.")
    else:
        print("All records already have UUIDs.")
        
    # 4. Make column NOT NULL UNIQUE
    # First drop constraints or unique index if they already exist to avoid duplicates
    try:
        cursor.execute(f"ALTER TABLE `{table}` DROP INDEX `idx_{table}_public_id`")
    except Exception:
        pass
    try:
        cursor.execute(f"ALTER TABLE `{table}` DROP INDEX `public_id`")
    except Exception:
        pass
        
    # Enforce constraints
    print(f"Enforcing NOT NULL UNIQUE constraints on '{table}'.public_id...")
    cursor.execute(f"ALTER TABLE `{table}` MODIFY COLUMN public_id VARCHAR(36) NOT NULL")
    cursor.execute(f"ALTER TABLE `{table}` ADD UNIQUE KEY `idx_{table}_public_id` (public_id)")
    print(f"Constraints and unique index successfully created on '{table}'.")

print("\nDatabase migration completed successfully!")
cursor.close()
conn.close()
