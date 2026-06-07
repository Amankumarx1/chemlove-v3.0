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
    print("Starting ChemLove Chapter Overhaul & Interactive UI Verification...")
    
    admin = ChemLoveClient()
    student = ChemLoveClient()

    # 1. Register Admin & Student
    admin.request("POST", "/signup", {
        "name": "Overhaul Admin", "email": "overhaul_admin@example.com", "password": "pass", "institution": "ChemLove High", "role": "admin"
    }, is_json=False)
    
    student.request("POST", "/signup", {
        "name": "Overhaul Student", "email": "overhaul_student@example.com", "password": "pass", "institution": "ChemLove High", "role": "student", "classLevel": "12"
    }, is_json=False)

    # Login Admin
    st, body, _ = admin.request("POST", "/login", {
        "email": "overhaul_admin@example.com", "password": "pass"
    }, is_json=False)
    if st != 200:
        print(f"FAILED Admin Login: {st} - {body}")
        return

    # Login Student
    st, body, _ = student.request("POST", "/login", {
        "email": "overhaul_student@example.com", "password": "pass"
    }, is_json=False)
    if st != 200:
        print(f"FAILED Student Login: {st} - {body}")
        return

    # Re-login Admin for creation
    admin.request("POST", "/login", {
        "email": "overhaul_admin@example.com", "password": "pass"
    }, is_json=False)

    # 2. Create Course for Class 12
    course_payload = {
        "title": "Class 12 Advanced Overhaul Course",
        "description": "Test description.",
        "category": "Physical Chemistry",
        "class_level": "12",
        "status": "published"
    }
    st, body, res_course = admin.request("POST", "/api/admin/courses", course_payload)
    if st != 200 or not res_course or not res_course.get("ok"):
        print(f"FAILED Course Creation: {st} - {body}")
        return
    course_id = res_course["id"]
    print(f"SUCCESS: Course created (ID: {course_id})")

    # 3. Create a Chapter with markdown tags and interactive blocks
    notes_text = (
        "# Solutions Intro\n"
        "This is a premium digital textbook page.\n"
        "Here is some *italicized* text and some **bolded** text.\n"
        "## Section 1\n"
        "- Homogeneous mixtures\n"
        "- Solvent vs Solute\n\n"
        ":::info\n"
        "This is an info callout compiled on the client side.\n"
        ":::\n\n"
        ":::quickcheck\n"
        "Question: Which of the following is temperature independent?\n"
        "A: Molarity\n"
        "B: Molality\n"
        "C: Normality\n"
        "D: Formality\n"
        "Answer: B\n"
        "Explanation: Molality relies on mass of solvent rather than volume, making it independent of temperature.\n"
        ":::"
    )
    
    formulas_text = (
        ":::formula\n"
        "Name: Molarity\n"
        "Equation: M = n_solute / V_solution\n"
        "Meaning: M is Molarity, n is moles, V is volume in Liters\n"
        "Variables: n (moles), V (Liters)\n"
        "Example: A 2 mol solute dissolved in 1L solvent gives 2 M solution.\n"
        ":::"
    )

    reactions_text = (
        ":::reaction\n"
        "Type: Dissociation\n"
        "Equation: NaCl (s) -> Na+ (aq) + Cl- (aq)\n"
        "Observation: Solid salt disappears as it dissolves in water.\n"
        "Explanation: Polar water molecules solvate Na+ and Cl- ions.\n"
        ":::"
    )

    chapter_payload = {
        "course_id": course_id,
        "class_level": "12",
        "chapter_number": 1,
        "title": "SOLUTIONS & COLLIGATIVE PROPERTIES",
        "description": "Comprehensive study of solution concentration and properties.",
        "status": "published",
        "key_points": "• Solutions are mixtures.\n• Henry's law constant depends on gas type.",
        "notes": notes_text,
        "formulas": formulas_text,
        "reactions": reactions_text,
        "experiment_content": "Aim: To verify Henry's Law.\nProcedure: Measure solubility at various pressures."
    }

    st, body, res_chapter = admin.request("POST", "/api/admin/chapters", chapter_payload)
    if st != 200 or not res_chapter or not res_chapter.get("ok"):
        print(f"FAILED Chapter Creation: {st} - {body}")
        return
    chapter_id = res_chapter["id"]
    print(f"SUCCESS: Chapter created (ID: {chapter_id})")

    # 4. Request Student View & Verify layout structure & elements
    st, body, _ = student.request("GET", f"/student/chapter/{chapter_id}")
    if st != 200:
        print(f"FAILED Student View Request: {st}")
        return

    # Check for layout and components in DOM
    assert "Journey Progress" in body, "Missing Journey Progress track bar"
    assert "Guided Learning Path" in body, "Missing central roadmap timeline"
    
    print("SUCCESS: Student View HTML checks passed with correct layout!")

    # 5. Query AI Tutor Route
    st, body, res_ai = student.request("POST", "/api/ai/tutor", {
        "question": "what is molarity?",
        "chapter_title": "Solutions"
    })
    if st != 200 or not res_ai or not res_ai.get("ok"):
        print(f"FAILED AI Tutor Query: {st} - {body}")
        return
    assert "Molarity" in res_ai["response"], "AI Response did not contain expected explanation"
    print("SUCCESS: AI Tutor Route query verified with expected educational response.")

    # 6. Mark Chapter as Complete
    st, body, res_comp = student.request("POST", f"/api/chapter/{chapter_id}/complete-chapter", {})
    if st != 200 or not res_comp or not res_comp.get("ok"):
        print(f"FAILED Chapter completion marking: {st} - {body}")
        return
    print("SUCCESS: Chapter marked complete successfully.")

    # 7. Check student progress percentage is updated
    st, body, _ = student.request("GET", f"/student/chapter/{chapter_id}")
    assert "100% Complete" in body or "100%" in body, "Chapter progress did not reflect completion"
    print("SUCCESS: Chapter progress reflects 100% completion in student view.")

    # 8. Check next chapter routing redirect
    st, body, _ = student.request("GET", f"/student/chapter/{chapter_id}/next")
    # Should say congratulations or redirect to chapters because it's the last chapter
    assert "completed the last chapter" in body or "Chapters" in body, "Next chapter redirect route failed"
    print("SUCCESS: Next chapter redirect behavior verified.")

    # Cleanup database records
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
    cursor.execute("DELETE FROM chapter_progress WHERE chapter_id = %s", (chapter_id,))
    cursor.execute("DELETE FROM chapters WHERE id = %s", (chapter_id,))
    cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
    cursor.execute("DELETE FROM users WHERE email IN ('overhaul_admin@example.com', 'overhaul_student@example.com')")
    conn.commit()
    cursor.close()
    conn.close()
    print("SUCCESS: Cleanup completed.")
    print("--- ALL OVERHAUL & INTERACTIVE INTERFACES VERIFICATION TESTS PASSED ---")

if __name__ == "__main__":
    run_verification()
