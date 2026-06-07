import urllib.request
import urllib.parse
import json
import http.cookiejar
import os
import mysql.connector
from dotenv import load_dotenv

BASE_URL = "http://127.0.0.1:5000"

class ChemLoveClient:
    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.cookie_processor = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib.request.build_opener(self.cookie_processor)

    def request(self, method, path, data=None, is_json=True):
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
        try:
            with self.opener.open(req) as response:
                body = response.read().decode('utf-8')
                resp_json = None
                if 'application/json' in response.headers.get('Content-Type', ''):
                    try:
                        resp_json = json.loads(body)
                    except:
                        pass
                return response.status, body, resp_json
        except urllib.request.HTTPError as e:
            body = e.read().decode('utf-8')
            return e.code, body, None

def run_verification():
    load_dotenv()
    print("Starting ChemLove CMS Persistence Verification...")
    
    admin = ChemLoveClient()
    student = ChemLoveClient()

    # Register Admin & Student
    admin.request("POST", "/signup", {
        "name": "Persist Admin", "email": "persist_admin@example.com", "password": "pass", "institution": "ChemLove High", "role": "admin"
    }, is_json=False)
    
    student.request("POST", "/signup", {
        "name": "Persist Student", "email": "persist_student@example.com", "password": "pass", "institution": "ChemLove High", "role": "student", "classLevel": "11"
    }, is_json=False)

    # Login Admin
    st, body, _ = admin.request("POST", "/login", {
        "email": "persist_admin@example.com", "password": "pass"
    }, is_json=False)
    if st != 200:
        print(f"FAILED Admin Login: {st} - {body}")
        return

    # Login Student
    st, body, _ = student.request("POST", "/login", {
        "email": "persist_student@example.com", "password": "pass"
    }, is_json=False)
    if st != 200:
        print(f"FAILED Student Login: {st} - {body}")
        return

    # Re-login Admin for creation
    admin.request("POST", "/login", {
        "email": "persist_admin@example.com", "password": "pass"
    }, is_json=False)

    # 1. Create a Course
    course_payload = {
        "title": "CMS Test Course Persistence",
        "description": "Test description.",
        "category": "Physical Chemistry",
        "class_level": "11",
        "status": "published"
    }
    st, body, res_course = admin.request("POST", "/api/admin/courses", course_payload)
    if st != 200 or not res_course or not res_course.get("ok"):
        print(f"FAILED Course Creation: {st} - {body}")
        return
    course_id = res_course["id"]
    print(f"SUCCESS: Course created (ID: {course_id})")

    # 2. Create a Chapter with multi-line, indented content
    key_points_text = "1. Types of Solutions:\n  • Gas in Gas\n  • Liquid in Gas\n  • Solid in Gas\n\n2. Concentration Expressions:\n  • Mass %\n  • Volume %"
    notes_text = "Standard line of notes.\n    Indented line of notes with spaces.\n- Bullet 1\n- Bullet 2"
    formulas_text = "Formula 1: Molarity = moles / L\nFormula 2: Molality = moles / kg"
    reactions_text = "2H₂ + O₂ → 2H₂O\nCH₄ + 2O₂ → CO₂ + 2H₂O"
    experiment_text = "Aim: To study solubility.\nProcedure:\n  1. Take water.\n  2. Add salt."

    chapter_payload = {
        "course_id": course_id,
        "class_level": "11",
        "chapter_number": 1,
        "title": "CMS Test Chapter Persistence",
        "description": "Test Chapter Description",
        "status": "published",
        "key_points": key_points_text,
        "notes": notes_text,
        "formulas": formulas_text,
        "reactions": reactions_text,
        "experiment_content": experiment_text
    }

    st, body, res_chapter = admin.request("POST", "/api/admin/chapters", chapter_payload)
    if st != 200 or not res_chapter or not res_chapter.get("ok"):
        print(f"FAILED Chapter Creation: {st} - {body}")
        return
    chapter_id = res_chapter["id"]
    print(f"SUCCESS: Chapter created (ID: {chapter_id})")

    # 3. Call Debug Endpoint to assert raw persistence in MySQL
    st, body, res_debug = admin.request("GET", f"/admin/debug/chapter/{chapter_id}")
    if st != 200 or not res_debug:
        print(f"FAILED Debug Check: {st} - {body}")
        return

    raw = res_debug["raw_mysql_values"]
    
    # Assert exact preservation of formatting (newlines, tabs, math symbols)
    assert raw["course_id"] == course_id, "course_id mismatch"
    assert raw["key_points"] == key_points_text, "key_points formatting lost!"
    assert raw["notes"] == notes_text, "notes formatting lost!"
    assert raw["formulas"] == formulas_text, "formulas formatting lost!"
    assert raw["reactions"] == reactions_text, "reactions formatting lost!"
    assert raw["experiment_content"] == experiment_text, "experiment_content formatting lost!"
    print("SUCCESS: Exact character formats matched perfectly in MySQL storage!")

    # 4. Check Student View Rendering
    st, body, _ = student.request("GET", f"/student/chapter/{chapter_id}")
    if st != 200:
        print(f"FAILED Student View Request: {st}")
        return

    # Verify formatting tags and styling classes exist in output HTML
    assert 'class="chapter-notes bg-black/20 border border-white/5 p-6 rounded-2xl text-slate-300 text-sm leading-relaxed font-medium"' in body or 'class="chapter-notes bg-black/20 border border-white/5 p-6 rounded-2xl text-slate-300 text-sm leading-relaxed font-medium"' in body or "chapter-notes" in body, "Missing class for notes styling"
    assert "chapter-keypoints" in body, "Missing class for key points styling"
    assert "chapter-formulas" in body, "Missing class for formulas styling"
    assert "Experiments" in body, "Missing Experiments tab link in student view"
    assert "Gas in Gas" in body, "Missing note data inside student view"
    assert "2H₂ + O₂" in body, "Missing reactions content inside student view"
    assert "Procedure" in body, "Missing experiment content inside student view"
    print("SUCCESS: Student view HTML contains all pre-wrap formatting classes and content!")

    # 5. Clean up DB records
    # Clean up will occur in DB directly to be clean
    db_url = os.getenv("DATABASE_URL")
    parsed = urllib.parse.urlparse(db_url)
    db_name = parsed.path.lstrip('/')
    
    conn = mysql.connector.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        database=db_name
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chapters WHERE id = %s", (chapter_id,))
    cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
    cursor.execute("DELETE FROM users WHERE email IN ('persist_admin@example.com', 'persist_student@example.com')")
    conn.commit()
    cursor.close()
    conn.close()
    print("SUCCESS: Cleanup completed.")
    print("--- ALL PERSISTENCE TESTS PASSED FLAWLESSLY ---")

if __name__ == "__main__":
    run_verification()
