import os
import subprocess
import shutil
import dotenv

# Load environment
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
dotenv.load_dotenv(dotenv_path)

# Parse database configuration
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

def run_mysqldump(config, output_path):
    print("[BACKUP] Attempting backup using system mysqldump...")
    
    # Construct mysqldump command
    # Avoid exposing password on command line using environment variables for safety
    env = os.environ.copy()
    env["MYSQL_PWD"] = config["password"]
    
    cmd = [
        "mysqldump",
        f"-h{config['host']}",
        f"-P{config['port']}",
        f"-u{config['user']}",
        "--no-tablespaces",
        config["database"]
    ]
    
    try:
        # Run and capture stdout
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        print(f"[BACKUP] Success! Exported database to {output_path} via mysqldump.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[BACKUP] System mysqldump failed or not found: {e}")
        return False

def run_python_fallback_dump(config, output_path):
    print("[BACKUP] Falling back to pure Python database serialization...")
    try:
        import mysql.connector
        from datetime import datetime, date
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        sql_content = []
        sql_content.append("SET FOREIGN_KEY_CHECKS = 0;\n")
        
        cursor.execute("SHOW TABLES")
        tables = [list(r.values())[0] if isinstance(r, dict) else r[0] for r in cursor.fetchall()]
        
        for t in tables:
            sql_content.append(f"DROP TABLE IF EXISTS `{t}`;")
        sql_content.append("")
        
        for t in tables:
            cursor.execute(f"SHOW CREATE TABLE `{t}`")
            res = cursor.fetchone()
            create_stmt = list(res.values())[1]
            sql_content.append(create_stmt + ";\n")
            
            # Export data
            cursor.execute(f"SELECT * FROM `{t}`")
            rows = cursor.fetchall()
            if rows:
                sql_content.append(f"-- Seeding data for table `{t}`")
                for row in rows:
                    cols = []
                    vals = []
                    for k, v in row.items():
                        cols.append(f"`{k}`")
                        if v is None:
                            vals.append("NULL")
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        elif isinstance(v, bool):
                            vals.append("1" if v else "0")
                        elif isinstance(v, (datetime, date)):
                            vals.append(f"'{v.strftime('%Y-%m-%d %H:%M:%S')}'")
                        else:
                            escaped = str(v).replace("\\", "\\\\").replace("'", "\\'")
                            vals.append(f"'{escaped}'")
                    
                    cols_str = ", ".join(cols)
                    vals_str = ", ".join(vals)
                    sql_content.append(f"INSERT INTO `{t}` ({cols_str}) VALUES ({vals_str});")
                sql_content.append("")
                
        sql_content.append("SET FOREIGN_KEY_CHECKS = 1;\n")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sql_content))
            
        print(f"[BACKUP] Success! Exported database to {output_path} via Python serialization.")
        cursor.close()
        conn.close()
        return True
    except Exception as ex:
        print(f"[BACKUP] ERROR: Python fallback backup failed: {ex}")
        return False

def main():
    config = get_db_config()
    
    # Ensure backups folder exists
    backups_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
    os.makedirs(backups_dir, exist_ok=True)
    
    output_path = os.path.join(backups_dir, "latest_seed.sql")
    
    # Attempt mysqldump, fallback if it fails
    if not run_mysqldump(config, output_path):
        run_python_fallback_dump(config, output_path)

if __name__ == "__main__":
    main()
