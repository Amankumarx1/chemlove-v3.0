import urllib.request
import urllib.parse
import json
import http.cookiejar
import os
import sys
from dotenv import load_dotenv
import mysql.connector

BASE_URL = "http://localhost:5000"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, hdrs, newurl):
        # Returning None stops the redirection process and returns the 302 response normally.
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
    print("[CLEANUP] Cleaning up test database records...")
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
            
        import urllib.parse
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
        # Get user IDs of test users to be extra thorough, though cascades handle most
        cursor.execute(
            "SELECT id FROM users WHERE email IN ('student_test@example.com', 'teacher_test@example.com', 'admin_test@example.com')"
        )
        user_ids = [row[0] for row in cursor.fetchall()]

        if user_ids:
            placeholders = ",".join("%s" for _ in user_ids)
            cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders})", user_ids)
        conn.commit()
        cursor.close()
        conn.close()
        print("[CLEANUP] Cleanup finished.")
    except Exception as e:
        print(f"[CLEANUP] WARNING: Failed to clean up: {e}")

def run_tests():
    # 1. Start clean
    db_cleanup()

    # Create clients
    student = ChemLoveClient()
    teacher = ChemLoveClient()
    admin = ChemLoveClient()

    print("\n--- STEP 1: Registration ---")
    
    # Register Admin
    status, _, _, _, _ = admin.request(
        "POST", "/signup",
        {"name": "Admin Test", "email": "admin_test@example.com", "password": "pass123", "institution": "Test High", "role": "admin"},
        is_json=False
    )
    assert status == 200, f"Admin signup failed: {status}"
    print("SUCCESS: Admin registered successfully")

    # Register Teacher
    status, _, _, _, _ = teacher.request(
        "POST", "/signup",
        {"name": "Teacher Test", "email": "teacher_test@example.com", "password": "pass123", "institution": "Test High", "role": "teacher"},
        is_json=False
    )
    assert status == 200, f"Teacher signup failed: {status}"
    print("SUCCESS: Teacher registered successfully")

    # Register Student
    status, _, _, _, _ = student.request(
        "POST", "/signup",
        {"name": "Student Test", "email": "student_test@example.com", "password": "pass123", "institution": "Test High", "role": "student", "classLevel": "10"},
        is_json=False
    )
    assert status == 200, f"Student signup failed: {status}"
    print("SUCCESS: Student registered successfully")


    print("\n--- STEP 2: Login and Session Sync ---")
    
    # Log out student to start fresh logins
    student.request("POST", "/logout", {}, is_json=False)
    teacher.request("POST", "/logout", {}, is_json=False)
    admin.request("POST", "/logout", {}, is_json=False)

    # Login Student
    status, url, _, _, _ = student.request(
        "POST", "/login",
        {"email": "student_test@example.com", "password": "pass123"},
        is_json=False,
        follow_redirects=False
    )
    assert status == 302 or status == 200, f"Student login failed: {status}"
    print("SUCCESS: Student login successful")

    # Login Teacher
    status, url, _, _, _ = teacher.request(
        "POST", "/login",
        {"email": "teacher_test@example.com", "password": "pass123"},
        is_json=False,
        follow_redirects=False
    )
    assert status == 302 or status == 200, f"Teacher login failed: {status}"
    print("SUCCESS: Teacher login successful")

    # Login Admin
    status, url, _, _, _ = admin.request(
        "POST", "/login",
        {"email": "admin_test@example.com", "password": "pass123"},
        is_json=False,
        follow_redirects=False
    )
    assert status == 302 or status == 200, f"Admin login failed: {status}"
    print("SUCCESS: Admin login successful")


    print("\n--- STEP 3: Role-Based Authorization Guard Checks ---")
    
    # 3.1 Student trying to access teacher dashboard or admin dashboard
    # Access /teacher/dashboard
    status, _, headers, _, _ = student.request("GET", "/teacher/dashboard", follow_redirects=False)
    assert status == 302, f"Student accessed /teacher/dashboard with code {status}"
    assert "/profile" in headers.get("Location", ""), f"Redirect Location mismatch: {headers.get('Location')}"
    print("SUCCESS: Guard: Student redirected to /profile trying to access /teacher/dashboard")

    # Access /admin/dashboard
    status, _, headers, _, _ = student.request("GET", "/admin/dashboard", follow_redirects=False)
    assert status == 302, f"Student accessed /admin/dashboard with code {status}"
    assert "/profile" in headers.get("Location", ""), f"Redirect Location mismatch: {headers.get('Location')}"
    print("SUCCESS: Guard: Student redirected to /profile trying to access /admin/dashboard")

    # 3.2 Teacher trying to access admin dashboard
    status, _, headers, _, _ = teacher.request("GET", "/admin/dashboard", follow_redirects=False)
    assert status == 302, f"Teacher accessed /admin/dashboard with code {status}"
    assert "/profile" in headers.get("Location", ""), f"Redirect Location mismatch: {headers.get('Location')}"
    print("SUCCESS: Guard: Teacher redirected to /profile trying to access /admin/dashboard")

    # 3.3 Teacher accessing teacher dashboard
    status, _, _, _, _ = teacher.request("GET", "/teacher/dashboard", follow_redirects=False)
    assert status == 200, f"Teacher failed to access /teacher/dashboard: {status}"
    print("SUCCESS: Guard: Teacher allowed to access /teacher/dashboard")

    # 3.4 Admin accessing admin dashboard
    status, _, _, _, _ = admin.request("GET", "/admin/dashboard", follow_redirects=False)
    assert status == 200, f"Admin failed to access /admin/dashboard: {status}"
    print("SUCCESS: Guard: Admin allowed to access /admin/dashboard")


    print("\n--- STEP 4: Classroom Management ---")
    
    # Teacher creates classroom
    status, _, _, _, resp_json = teacher.request(
        "POST", "/api/classrooms",
        {"name": "Class 10-A", "grade": "10", "section": "A"}
    )
    assert status == 200 and resp_json.get("ok"), "Failed to create classroom"
    print("SUCCESS: Classroom created successfully")

    # Get classroom list & extract ID
    status, _, _, _, resp_json = teacher.request("GET", "/api/classrooms")
    assert status == 200, "Failed to get classrooms"
    classrooms = resp_json.get("classrooms", [])
    classroom = next((c for c in classrooms if c["name"] == "Class 10-A"), None)
    assert classroom is not None, "Classroom not found in list"
    classroom_id = classroom["id"]
    print(f"SUCCESS: Retrieved classroom ID: {classroom_id}")


    print("\n--- STEP 5: Student Enrollment ---")
    
    # Get student profile ID
    status, _, _, _, resp_json = student.request("GET", "/api/profile")
    assert status == 200, "Failed to get student profile"
    student_id = resp_json["profile"]["id"]
    print(f"Student User ID: {student_id}")

    # Student enrolls
    status, _, _, _, resp_json = student.request(
        "POST", "/api/students",
        {"classroom_id": classroom_id, "student_id": student_id}
    )
    assert status == 200 and resp_json.get("ok"), "Failed to enroll student"
    print("SUCCESS: Student enrolled in Class 10-A successfully")

    # Verify student exists in classroom list for teacher
    status, _, _, _, resp_json = teacher.request("GET", f"/api/students?classroom_id={classroom_id}")
    assert status == 200, "Failed to get classroom students"
    students = resp_json.get("students", [])
    assert any(s["id"] == student_id for s in students), "Enrolled student not in classroom directory"
    print("SUCCESS: Enrolled student verified in teacher's classroom directory")


    print("\n--- STEP 6: Assignment Center ---")
    
    # Teacher creates assignment
    status, _, _, _, resp_json = teacher.request(
        "POST", "/api/assignments",
        {
            "title": "Acid-Base Titration Report",
            "description": "Please submit your notes on acid-base titration",
            "classroom_id": classroom_id,
            "chapter_id": 1,
            "lab_id": 1,
            "marks": 100,
            "due_date": "2026-06-10",
            "instructions": "Submit link or report text",
            "status": "published"
        }
    )
    assert status == 200 and resp_json.get("ok"), "Failed to create assignment"
    print("SUCCESS: Assignment created successfully")

    # Get assignment list & extract ID
    status, _, _, _, resp_json = teacher.request("GET", f"/api/assignments?classroom_id={classroom_id}")
    assert status == 200, "Failed to get assignments"
    assignments = resp_json.get("assignments", [])
    assignment = next((a for a in assignments if a["title"] == "Acid-Base Titration Report"), None)
    assert assignment is not None, "Assignment not found in list"
    assignment_id = assignment["id"]
    print(f"SUCCESS: Retrieved assignment ID: {assignment_id}")


    print("\n--- STEP 7: Student Submission ---")
    
    # Student submits assignment
    status, _, _, _, resp_json = student.request(
        "POST", "/api/submissions",
        {
            "assignment_id": assignment_id,
            "file_data": "https://example.com/acid-base-report.pdf"
        }
    )
    assert status == 200 and resp_json.get("ok"), "Failed to submit assignment"
    print("SUCCESS: Student submitted assignment successfully")


    print("\n--- STEP 8: Teacher Review & Grading ---")
    
    # Teacher fetches submissions
    status, _, _, _, resp_json = teacher.request("GET", f"/api/submissions?assignment_id={assignment_id}")
    assert status == 200, "Failed to get submissions"
    submissions = resp_json.get("submissions", [])
    submission = next((s for s in submissions if s["student_id"] == student_id), None)
    assert submission is not None, "Student submission not found"
    submission_id = submission["id"]
    print(f"SUCCESS: Retrieved student submission ID: {submission_id}")

    # Teacher grades assignment (Status = approved, which awards XP)
    status, _, _, _, resp_json = teacher.request(
        "PUT", "/api/submissions",
        {
            "id": submission_id,
            "marks_obtained": 98,
            "feedback": "Outstanding chemical equation details!",
            "status": "approved"
        }
    )
    assert status == 200 and resp_json.get("ok"), "Failed to grade submission"
    print("SUCCESS: Submission graded and approved by teacher successfully")


    print("\n--- STEP 9: Verify Student XP Increase ---")
    
    # Student retrieves profile to check XP
    status, _, _, _, resp_json = student.request("GET", "/api/profile")
    assert status == 200, "Failed to fetch student profile"
    profile = resp_json.get("profile", {})
    xp = profile.get("current_xp", 0)
    print(f"Student Current XP: {xp}")
    # Default is 100, plus 50 on approval = 150
    assert xp == 150, f"Expected 150 XP, got {xp}"
    print("SUCCESS: Student XP successfully increased by 50 points upon approval")


    print("\n--- STEP 10: Admin Platform Analytics ---")
    
    # Admin gets analytics
    status, _, _, _, resp_json = admin.request("GET", "/api/admin/analytics")
    assert status == 200, "Failed to fetch admin analytics"
    stats = resp_json.get("stats", {})
    print(f"Admin Analytics: {stats}")
    assert stats.get("total_students", 0) > 0, "No students registered in stats"
    print("SUCCESS: Admin successfully accessed school-wide telemetry and stats")


    print("\n--- STEP 11: Admin Suspension Control ---")
    
    # Admin suspends Student
    status, _, _, _, resp_json = admin.request(
        "PUT", "/api/admin/users",
        {
            "id": student_id,
            "name": "Student Test",
            "role": "student",
            "status": "suspended"
        }
    )
    assert status == 200 and resp_json.get("ok"), "Failed to suspend student"
    print("SUCCESS: Student account suspended by Admin")

    # Admin attempts to modify admin accounts (should be blocked with 403)
    status, _, _, _, resp_json = admin.request("GET", "/api/admin/users")
    assert status == 200, "Failed to get users"
    users_list = resp_json.get("users", [])
    admin_user = next((u for u in users_list if u["role"] == "admin"), None)
    if admin_user:
        admin_uid = admin_user["id"]
        status, _, _, _, resp_json = admin.request(
            "PUT", "/api/admin/users",
            {
                "id": admin_uid,
                "name": admin_user["name"],
                "role": "admin",
                "status": "suspended"
            }
        )
        assert status == 403, f"Expected 403 when modifying admin, got {status}"
        print("SUCCESS: Admin suspension attempt blocked with 403 Forbidden")


    print("\n--- STEP 12: Verify Suspended User Access ---")
    
    # Attempt to log in again as suspended student
    status, _, headers, body, _ = student.request(
        "POST", "/login",
        {"email": "student_test@example.com", "password": "pass123"},
        is_json=False,
        follow_redirects=False
    )
    # login() redirects back to /login on suspension
    assert status == 302, f"Expected redirect on login attempt, got {status}"
    assert "/login" in headers.get("Location", ""), f"Redirect Location mismatch: {headers.get('Location')}"
    print("SUCCESS: Suspended user login blocked and redirected back to login")

    print("\n--- STEP 13: Verify New Split Landing Pages ---")
    
    # 13.1 Verify features page returns 200
    status, _, _, body, _ = student.request("GET", "/features")
    assert status == 200, f"Features page returned {status}"
    assert "Everything You Need" in body, "Expected features page content not found"
    print("SUCCESS: Features page verified")

    # 13.2 Verify about page returns 200
    status, _, _, body, _ = student.request("GET", "/about")
    assert status == 200, f"About page returned {status}"
    assert "Our Mission" in body, "Expected about page content not found"
    print("SUCCESS: About page verified")

    # 13.3 Verify contact page GET returns 200
    status, _, _, body, _ = student.request("GET", "/contact")
    assert status == 200, f"Contact page GET returned {status}"
    assert "Send Us A Message" in body, "Expected contact page content not found"
    print("SUCCESS: Contact page GET verified")

    # 13.4 Verify contact page POST returns 302 redirect
    status, _, headers, body, _ = student.request(
        "POST", "/contact",
        {"name": "FAQ Asker", "email": "asker@example.com", "role": "student", "subject": "Test", "message": "Hello ChemLove!"},
        is_json=False,
        follow_redirects=False
    )
    assert status == 302, f"Contact page POST returned {status}"
    assert "/contact" in headers.get("Location", ""), f"Redirect Location mismatch: {headers.get('Location')}"
    print("SUCCESS: Contact page POST verified redirect")

    # Final DB cleanup
    db_cleanup()
    print("\n*** ALL TESTS PASSED SUCCESSFULLY! ***")

if __name__ == "__main__":
    try:
        run_tests()
        sys.exit(0)
    except AssertionError as e:
        print(f"\nAssertionError: {e}")
        db_cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        db_cleanup()
        sys.exit(1)
