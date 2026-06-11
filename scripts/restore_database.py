import os
import dotenv

# Load environment
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
dotenv.load_dotenv(dotenv_path)

def get_db_config():
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("mysql://"):
        import urllib.parse
        parsed = urllib.parse.urlparse(db_url)
        database = parsed.path.lstrip('/')
        port = parsed.port if parsed.port is not None else 3306
        return {
            "host": parsed.hostname or "localhost",
            "port": port,
            "user": urllib.parse.unquote(parsed.username or "root"),
            "password": urllib.parse.unquote(parsed.password or ""),
            "database": database
        }
    else:
        return {
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": int(os.getenv("MYSQL_PORT", 3306)),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", ""),
            "database": os.getenv("MYSQL_DATABASE", "chemlove")
        }

def execute_sql_file(cursor, conn, filepath):
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
            
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for stmt in statements:
        stmt_stripped = stmt.strip()
        if stmt_stripped:
            cursor.execute(stmt_stripped)
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()

def main():
    config = get_db_config()
    target_db = config["database"]
    
    # Check if backup file exists
    backup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups", "latest_seed.sql")
    if not os.path.exists(backup_path):
        print(f"[RESTORE] ERROR: Backup file not found at {backup_path}")
        return
        
    print(f"[RESTORE] Restoring database to: {target_db}...")
    try:
        import mysql.connector
        
        # Connect to server to verify DB exists
        bootstrap_config = config.copy()
        if "database" in bootstrap_config:
            del bootstrap_config["database"]
            
        conn = mysql.connector.connect(**bootstrap_config)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{target_db}`")
        cur.execute(f"USE `{target_db}`")
        
        print(f"[RESTORE] Database `{target_db}` ready. Executing SQL restore...")
        execute_sql_file(cur, conn, backup_path)
        
        print("[RESTORE] Success! Database fully restored from latest_seed.sql.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[RESTORE] ERROR: Database restore failed: {e}")

if __name__ == "__main__":
    main()
