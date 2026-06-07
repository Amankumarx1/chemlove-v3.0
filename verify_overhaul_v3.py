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
    print("Starting ChemLove V3 Guided Chapter Learning Journey Verification...")
    
    admin = ChemLoveClient()
    student = ChemLoveClient()

    # 1. Register Admin & Student
    admin.request("POST", "/signup", {
        "name": "V3 Admin", "email": "v3_admin@example.com", "password": "pass", "institution": "ChemLove High", "role": "admin"
    }, is_json=False)
    
    student.request("POST", "/signup", {
        "name": "V3 Student", "email": "v3_student@example.com", "password": "pass", "institution": "ChemLove High", "role": "student", "classLevel": "11"
    }, is_json=False)

    # Login Admin
    st, body, _ = admin.request("POST", "/login", {
        "email": "v3_admin@example.com", "password": "pass"
    }, is_json=False)
    if st != 200:
        print(f"FAILED Admin Login: {st} - {body}")
        return

    # Login Student
    st, body, _ = student.request("POST", "/login", {
        "email": "v3_student@example.com", "password": "pass"
    }, is_json=False)
    if st != 200:
        print(f"FAILED Student Login: {st} - {body}")
        return

    # Re-login Admin for creation
    admin.request("POST", "/login", {
        "email": "v3_admin@example.com", "password": "pass"
    }, is_json=False)

    # 2. Create Course
    course_payload = {
        "title": "V3 Guided Journey Course",
        "description": "LMS V3 Verification.",
        "category": "Organic Chemistry",
        "class_level": "11",
        "status": "published"
    }
    st, body, res_course = admin.request("POST", "/api/admin/courses", course_payload)
    if st != 200 or not res_course or not res_course.get("ok"):
        print(f"FAILED Course Creation: {st} - {body}")
        return
    course_id = res_course["id"]
    print(f"SUCCESS: Course created (ID: {course_id})")

    # 3. Create V3 Chapter
    chapter_payload = {
        "course_id": course_id,
        "class_level": "11",
        "chapter_number": 1,
        "title": "CHEMICAL BONDING AND MOLECULAR STRUCTURE",
        "description": "Premium guided textbook chapter.",
        "status": "published",
        "key_points": "### Key Concepts\n- Octet Rule\n- Covalent Bonding",
        "notes": "# Molecular Structure Intro\nLearn bonding properties.",
        "formulas": ":::formula\nName: Formal Charge\nEquation: FC = V - L - B/2\n:::",
        "reactions": ":::reaction\nType: Redox\nEquation: 2Na + Cl2 -> 2NaCl\n:::",
        "experiment_content": ":::experiment\nAim: Study covalent models\n:::",
        "practice_questions": [
            {"question": "Identify formal charge.", "answer": "0", "category": "Numerical", "difficulty": "Easy"}
        ]
    }

    st, body, res_chapter = admin.request("POST", "/api/admin/chapters", chapter_payload)
    if st != 200 or not res_chapter or not res_chapter.get("ok"):
        print(f"FAILED Chapter Creation: {st} - {body}")
        return
    chapter_id = res_chapter["id"]
    print(f"SUCCESS: Chapter created (ID: {chapter_id})")

    # 4. Create Quiz for Chapter
    quiz_payload = {
        "chapter_id": chapter_id,
        "title": "Bonding Evaluation",
        "duration_minutes": 15,
        "total_marks": 100,
        "questions": [
            {
                "question": "What shape is methane?",
                "option_a": "Tetrahedral",
                "option_b": "Linear",
                "option_c": "Trigonal Planar",
                "option_d": "Bent",
                "correct_answer": "A",
                "explanation": "Methane has sp3 hybridization yielding a tetrahedral shape."
            }
        ]
    }
    st, body, res_quiz = admin.request("POST", "/api/admin/quizzes", quiz_payload)
    if st != 200 or not res_quiz or not res_quiz.get("ok"):
        print(f"FAILED Quiz Creation: {st} - {body}")
        return
    quiz_id = res_quiz["id"]
    print(f"SUCCESS: Quiz created (ID: {quiz_id})")

    # 5. student loads chapter page
    st, body, _ = student.request("GET", f"/student/chapter/{chapter_id}")
    if st != 200:
        print(f"FAILED Loading Student Chapter View: {st}")
        return
    
    assert "Journey Progress" in body, "Missing Journey Progress track bar"
    assert "Guided Learning Path" in body, "Missing central roadmap timeline"
    print("SUCCESS: Chapter page UI structure verified.")

    # 6. student loads sections sequentially
    sections = ['overview', 'keypoints', 'formulas', 'reactions', 'experiments', 'practice']
    for sec in sections:
        if sec == 'experiments' or sec == 'practice':
            # Complete actions
            st, body, res_comp = student.request("POST", f"/api/chapter/{chapter_id}/section/{sec}/complete")
            if st != 200 or not res_comp or not res_comp.get("ok"):
                print(f"FAILED completing section {sec}: {st} - {body}")
                return
            print(f"SUCCESS: Completed section: {sec}. Progress Mastery: {res_comp['mastery_percent']}%")
        else:
            # View-based sections
            st, body, res_view = student.request("GET", f"/api/chapter/{chapter_id}/section/{sec}")
            if st != 200 or not res_view or not res_view.get("ok"):
                print(f"FAILED loading section {sec}: {st} - {body}")
                return
            print(f"SUCCESS: Loaded section: {sec}. Progress Mastery: {res_view['mastery_percent']}%")

    # 7. inline quiz complete
    st, body, res_quiz_comp = student.request("POST", f"/api/chapter/{chapter_id}/section/quiz/complete")
    if st != 200 or not res_quiz_comp or not res_quiz_comp.get("ok"):
        print(f"FAILED completing quiz section: {st} - {body}")
        return
    
    assert res_quiz_comp["mastery_percent"] == 100, "Mastery did not reach 100% after quiz"
    assert res_quiz_comp["newly_completed"] is True, "Chapter was not flagged as newly mastered"
    assert res_quiz_comp["xp_earned"] == 150, "Did not award 150 XP for mastery completion"
    print("SUCCESS: Quiz complete verified. Student mastery hits 100% and awards XP successfully.")

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
    cursor.execute("DELETE FROM quizzes WHERE id = %s", (quiz_id,))
    cursor.execute("DELETE FROM chapter_section_progress WHERE chapter_id = %s", (chapter_id,))
    cursor.execute("DELETE FROM chapter_progress WHERE chapter_id = %s", (chapter_id,))
    cursor.execute("DELETE FROM chapters WHERE id = %s", (chapter_id,))
    cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
    cursor.execute("DELETE FROM users WHERE email IN ('v3_admin@example.com', 'v3_student@example.com')")
    conn.commit()
    cursor.close()
    conn.close()
    print("SUCCESS: Cleanup completed.")
    print("--- ALL V3 CHAPTER JOURNEY & INLINE EVALUATIONS TESTS PASSED ---")

if __name__ == "__main__":
    run_verification()
