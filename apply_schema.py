import os
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url or not db_url.startswith("mysql://"):
    print("Invalid or missing DATABASE_URL in .env")
    exit(1)

parsed = urlparse(db_url)
db_name = parsed.path.lstrip('/')

try:
    conn = mysql.connector.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password
    )
    cursor = conn.cursor()
    
    # Create database if not exists
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    cursor.execute(f"USE `{db_name}`")
    
    print(f"Applying schema.sql to database '{db_name}'...")
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    for result in cursor.execute(schema_sql, multi=True):
        if result.with_rows:
            result.fetchall()
            
    conn.commit()
    print("Database schema applied successfully!")
except Exception as e:
    print(f"Failed to apply database schema: {e}")
    exit(1)
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
