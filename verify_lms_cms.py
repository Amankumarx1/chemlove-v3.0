import urllib.request
import urllib.parse
import json
import http.cookiejar
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import mysql.connector
import csv

BASE_URL = "http://localhost:5000"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        return None

class ChemLoveClient:
    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.cookie_processor = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib.request.build_opener(self.cookie_processor)
        self.no_redirect_opener = urllib.request.build_opener(self.cookie_processor, NoRedirectHandler())

    def request(self, method, path, data=None, is_json=True, follow_redirects=True):
        url = f"{BASE_URL}{path}"
        req_data = None
        headers = {}

        if data is not None:
            if is_json:
                req_data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            else:
                req_data = urllib.parse.urlencode(data).encode('utf-8')
                headers['Content-Type'] = 'application/x-www-form-urlencoded'

        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        opener = self.opener if follow_redirects else self.no_redirect_opener

        try:
            with opener.open(req) as response:
                body = response.read().decode('utf-8')
                resp_json = None
                if 'application/json' in response.headers.get('Content-Type', ''):
                    try:
                        resp_json = json.loads(body)
                    except Exception:
                        pass
                return response.status, response.url, response.headers, body, resp_json
        except urllib.request.HTTPError as e:
            try:
                body = e.read().decode('utf-8')
                resp_json = None
                if 'application/json' in e.headers.get('Content-Type', ''):
                    try:
                        resp_json = json.loads(body)
                    except Exception:
                        pass
                return e.code, e.url, e.headers, body, resp_json
            finally:
                e.close()

def db_cleanup():
    print("[CLEANUP] Cleaning up CMS test database records...")
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")

    def parse_mysql_url(url):
        if not url.startswith("mysql://"):
            raise ValueError("Must start with mysql://")
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
            
        return {
            "host": host,
            "port": port,
            "user": urllib.parse.unquote(user),
            "password": urllib.parse.unquote(password),
            "database": database
        }

    if database_url and database_url.startswith("mysql://"):
        try:
            db_config = parse_mysql_url(database_url)
        except Exception as e:
            print(f"[CLEANUP] WARNING: Error parsing DATABASE_URL: {e}")
            return
    else:
        db_config = {
            "host": os.getenv("MYSQL_HOST", "localhost"),
            "port": int(os.getenv("MYSQL_PORT", 3306)),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", ""),
            "database": os.getenv("MYSQL_DATABASE", "chemlove")
        }

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Deleting specific test accounts used for CMS testing
        cursor.execute(
            "SELECT id FROM users WHERE email IN ('cms_admin@example.com', 'cms_teacher@example.com', 'cms_student@example.com')"
        )
        user_ids = [row[0] for row in cursor.fetchall()]

        if user_ids:
            placeholders = ",".join("%s" for _ in user_ids)
            cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders})", user_ids)
        
        # Clean up any orphan courses, chapters, modules containing 'CMS Test' in the title
        cursor.execute("DELETE FROM courses WHERE title LIKE '%CMS Test%'")
        cursor.execute("DELETE FROM chapters WHERE title LIKE '%CMS Test%'")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("[CLEANUP] CMS Cleanup finished.")
    except Exception as e:
        print(f"[CLEANUP] WARNING: Failed to clean up: {e}")

def run_tests():
    db_cleanup()

    # Create clients
    admin = ChemLoveClient()
    student = ChemLoveClient()

    # Step 1: Sign up accounts
    print("\n--- STEP 1: Registration ---")
    status, _, _, _, _ = admin.request(
        "POST", "/signup",
        {"name": "CMS Admin", "email": "cms_admin@example.com", "password": "pass123", "institution": "CMS High", "role": "admin"},
        is_json=False
    )
    assert status == 200, f"Admin signup failed: {status}"
    print("SUCCESS: Admin registered")

    status, _, _, _, _ = student.request(
        "POST", "/signup",
        {"name": "CMS Student", "email": "cms_student@example.com", "password": "pass123", "institution": "CMS High", "role": "student", "classLevel": "11"},
        is_json=False
    )
    assert status == 200, f"Student signup failed: {status}"
    print("SUCCESS: Student registered")

    # Logins
    status, _, _, _, _ = admin.request(
        "POST", "/login",
        {"email": "cms_admin@example.com", "password": "pass123"},
        is_json=False,
        follow_redirects=False
    )
    assert status == 302 or status == 200, f"Admin login failed: {status}"
    print("SUCCESS: Admin logged in")

    status, _, _, _, _ = student.request(
        "POST", "/login",
        {"email": "cms_student@example.com", "password": "pass123"},
        is_json=False,
        follow_redirects=False
    )
    assert status == 302 or status == 200, f"Student login failed: {status}"
    print("SUCCESS: Student logged in")

    # Step 2: Dynamic Course, Module, Chapter, Lesson CRUD
    print("\n--- STEP 2: Dynamic Content CRUD ---")
    
    # 2.1 Course CRUD
    payload = {
        "title": "CMS Test Course",
        "description": "CMS Test Course Description",
        "category": "Organic Chemistry",
        "class_level": "11",
        "status": "draft"
    }
    status, _, _, _, res = admin.request("POST", "/api/admin/courses", payload)
    assert status == 200 and res.get("ok"), f"Course creation failed: {res}"
    course_id = res["id"]
    print(f"SUCCESS: Created Course ID {course_id}")

    # Read courses
    status, _, _, _, res = admin.request("GET", "/api/admin/courses")
    assert status == 200, f"GET Courses failed: {status}"
    courses = res.get("courses", [])
    assert any(c["id"] == course_id for c in courses), "Created course not found in list"
    
    # 2.2 Module CRUD
    payload = {
        "course_id": course_id,
        "title": "CMS Test Module",
        "order_index": 1
    }
    status, _, _, _, res = admin.request("POST", "/api/admin/modules", payload)
    assert status == 200 and res.get("ok"), f"Module creation failed: {res}"
    module_id = res["id"]
    print(f"SUCCESS: Created Module ID {module_id}")

    # 2.3 Chapter CRUD
    payload = {
        "class_level": "11",
        "chapter_number": 99,
        "title": "CMS Test Chapter",
        "description": "CMS Test Chapter Description",
        "status": "draft"
    }
    status, _, _, _, res = admin.request("POST", "/api/admin/chapters", payload)
    assert status == 200 and res.get("ok"), f"Chapter creation failed: {res}"
    chapter_id = res["id"]
    print(f"SUCCESS: Created Chapter ID {chapter_id}")

    # 2.4 Lesson CRUD
    payload = {
        "chapter_id": chapter_id,
        "title": "CMS Test Lesson",
        "content": "CMS Lesson content v1",
        "order_index": 1,
        "status": "draft"
    }
    status, _, _, _, res = admin.request("POST", "/api/admin/lessons", payload)
    assert status == 200 and res.get("ok"), f"Lesson creation failed: {res}"
    lesson_id = res["id"]
    print(f"SUCCESS: Created Lesson ID {lesson_id}")

    # Step 3: Workflow Transitions and Access Boundaries
    print("\n--- STEP 3: Workflow Transitions and Access Boundaries ---")
    
    # Verify student cannot access the chapter because it is a draft
    status, url, _, body, _ = student.request("GET", f"/student/chapter/{chapter_id}", follow_redirects=True)
    assert "chapters" in url or "available yet" in body or "Unauthorized" in body, f"Draft chapter should not be accessible. URL: {url}"
    print("SUCCESS: Student access to draft chapter blocked")

    # Update chapter status to published
    payload = {
        "id": chapter_id,
        "class_level": "11",
        "chapter_number": 99,
        "title": "CMS Test Chapter",
        "description": "CMS Test Chapter Description",
        "status": "published",
        "order_index": 1
    }
    status, _, _, _, res = admin.request("PUT", "/api/admin/chapters", payload)
    assert status == 200 and res.get("ok"), f"Chapter update failed: {res}"
    print("SUCCESS: Chapter status updated to published")

    # Verify student can access it now
    status, url, _, body, _ = student.request("GET", f"/student/chapter/{chapter_id}", follow_redirects=True)
    assert f"chapter/{chapter_id}" in url, f"Student should be able to view published chapter. Redirected to: {url}"
    print("SUCCESS: Student access to published chapter allowed")

    # Step 4: Version Recovery
    print("\n--- STEP 4: Version Control and Recovery ---")
    
    # Edit the lesson twice to create history
    payload = {
        "id": lesson_id,
        "chapter_id": chapter_id,
        "title": "CMS Test Lesson",
        "content": "CMS Lesson content v2",
        "order_index": 1,
        "status": "draft"
    }
    status, _, _, _, res = admin.request("PUT", "/api/admin/lessons", payload)
    assert status == 200 and res.get("ok"), "Lesson update v2 failed"

    payload = {
        "id": lesson_id,
        "chapter_id": chapter_id,
        "title": "CMS Test Lesson",
        "content": "CMS Lesson content v3",
        "order_index": 1,
        "status": "draft"
    }
    status, _, _, _, res = admin.request("PUT", "/api/admin/lessons", payload)
    assert status == 200 and res.get("ok"), "Lesson update v3 failed"

    # Get version history
    status, _, _, _, res = admin.request("GET", f"/api/admin/versions?content_type=lesson&content_id={lesson_id}")
    assert status == 200, f"GET versions failed: {status}"
    versions = res.get("versions", [])
    assert len(versions) >= 3, f"Expected at least 3 versions, got: {len(versions)}"
    print(f"SUCCESS: Version history verified. Found {len(versions)} versions.")

    # Restore Version 1
    payload = {
        "content_type": "lesson",
        "content_id": lesson_id,
        "version_number": 1
    }
    status, _, _, _, res = admin.request("POST", "/api/admin/versions", payload)
    assert status == 200 and res.get("ok"), f"Restoration failed: {res}"

    # Verify restoration in database/API
    status, _, _, _, res = admin.request("GET", f"/api/admin/lessons?id={lesson_id}")
    lesson_data = res.get("lesson", {})
    assert lesson_data.get("content") == "CMS Lesson content v1", f"Restoration failed. Content is: {lesson_data.get('content')}"
    print("SUCCESS: Restored lesson version 1 successfully")

    # Step 5: Scheduling Release Boundaries
    print("\n--- STEP 5: Content Release Scheduling ---")
    
    # Schedule chapter to tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).isoformat()[:19]
    payload = {
        "id": chapter_id,
        "class_level": "11",
        "chapter_number": 99,
        "title": "CMS Test Chapter",
        "description": "CMS Test Chapter Description",
        "status": "published",
        "publish_at": tomorrow,
        "order_index": 1
    }
    status, _, _, _, res = admin.request("PUT", "/api/admin/chapters", payload)
    assert status == 200 and res.get("ok"), f"Scheduling update failed: {res}"

    # Verify student cannot view scheduled chapter
    status, url, _, body, _ = student.request("GET", f"/student/chapter/{chapter_id}", follow_redirects=True)
    assert "chapters" in url or "available yet" in body or "Unauthorized" in body, f"Future scheduled chapter should not be accessible. URL: {url}"
    print("SUCCESS: Future-scheduled chapter hidden from student")

    # Schedule chapter to yesterday (past release)
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()[:19]
    payload["publish_at"] = yesterday
    status, _, _, _, res = admin.request("PUT", "/api/admin/chapters", payload)
    assert status == 200 and res.get("ok"), f"Past-scheduling update failed: {res}"

    # Verify student can view past scheduled chapter
    status, url, _, body, _ = student.request("GET", f"/student/chapter/{chapter_id}", follow_redirects=True)
    assert f"chapter/{chapter_id}" in url, f"Past-scheduled chapter should be accessible. URL: {url}"
    print("SUCCESS: Past-scheduled chapter visible to student")

    # Step 6: Bulk Operations and AI Generator Stubs
    print("\n--- STEP 6: Bulk Operations & AI Generation ---")
    import bulk_exporter
    import ai_generator
    
    # 6.1 Test AI generator stubs
    outline = ai_generator.generate_course_outline("Thermodynamics", "12")
    assert outline["topic"] == "Thermodynamics"
    assert len(outline["modules"]) == 2
    mcqs = ai_generator.generate_quiz_mcqs("Some physics text", 2)
    assert len(mcqs) == 2
    assert mcqs[0]["correct_option"] == "B"
    print("SUCCESS: Mock AI outline and MCQ generation verified")
    
    # 6.2 Test Bulk CSV import functions
    # Let's write a mock courses CSV
    csv_file = "cms_test_courses.csv"
    with open(csv_file, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "description", "category", "class_level", "status"])
        writer.writeheader()
        writer.writerow({
            "title": "CMS Test Bulk Course",
            "description": "Bulk import description",
            "category": "Organic",
            "class_level": "11",
            "status": "draft"
        })
    
    try:
        count = bulk_exporter.import_courses_csv(csv_file)
        assert count == 1, f"Expected 1 course imported, got {count}"
        
        # Verify in DB
        status, _, _, _, res = admin.request("GET", "/api/admin/courses")
        assert status == 200
        courses = res.get("courses", [])
        assert any(c["title"] == "CMS Test Bulk Course" for c in courses), "Imported course not found in DB"
        print("SUCCESS: Course CSV bulk import verified")
    finally:
        if os.path.exists(csv_file):
            os.remove(csv_file)

    # Clean up and log
    db_cleanup()
    print("\n*** ALL CMS/LMS TESTS PASSED SUCCESSFULLY! ***")

if __name__ == "__main__":
    run_tests()
