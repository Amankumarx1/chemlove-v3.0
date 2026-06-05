import os
import json
import glob
import re
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

conn = mysql.connector.connect(
    host=parsed.hostname,
    port=parsed.port or 3306,
    user=parsed.username,
    password=parsed.password,
    database=db_name
)
cursor = conn.cursor(dictionary=True)

# Disable foreign key checks during migration to prevent ordering errors
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("TRUNCATE TABLE quiz_questions")
cursor.execute("TRUNCATE TABLE quizzes")
cursor.execute("TRUNCATE TABLE experiments")
cursor.execute("TRUNCATE TABLE reactions")
cursor.execute("TRUNCATE TABLE badges")
cursor.execute("TRUNCATE TABLE labs")
cursor.execute("TRUNCATE TABLE chapters")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

content_dir = os.path.join(os.path.dirname(__file__), 'content')

# 1. Migrate Chapters
print("Migrating chapters...")
chapters_pattern = os.path.join(content_dir, 'chapters', 'chapter_*.json')
chapters_map = {} # to keep track of loaded chapters
for filepath in sorted(glob.glob(chapters_pattern)):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            ch = json.load(f)
            ch_id = ch.get('id')
            
            # Map number -> chapter_number, class -> class_level
            chapter_number = ch.get('number')
            class_level = str(ch.get('class', ''))
            
            cursor.execute(
                """
                INSERT INTO chapters (
                    id, class_level, chapter_number, title, description,
                    learning_objectives, key_points, important_laws, formulas,
                    constants, important_reactions, notes, real_life_applications,
                    virtual_labs, practice_questions, common_mistakes, difficulty,
                    estimated_study_time, chapter_weightage, next_chapter, quiz_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    ch_id,
                    class_level,
                    chapter_number,
                    ch.get('title'),
                    ch.get('description'),
                    json.dumps(ch.get('learning_objectives', [])),
                    json.dumps(ch.get('key_points', [])),
                    json.dumps(ch.get('important_laws', [])),
                    json.dumps(ch.get('formulas', [])),
                    json.dumps(ch.get('constants', [])),
                    json.dumps(ch.get('important_reactions', [])),
                    json.dumps(ch.get('notes', []) if isinstance(ch.get('notes'), list) else [ch.get('notes', '')]),
                    json.dumps(ch.get('real_life_applications', [])),
                    json.dumps(ch.get('virtual_labs', [])),
                    json.dumps(ch.get('practice_questions', [])),
                    json.dumps(ch.get('common_mistakes', [])),
                    ch.get('difficulty'),
                    ch.get('estimated_study_time'),
                    json.dumps(ch.get('chapter_weightage', {})),
                    json.dumps(ch.get('next_chapter', {})),
                    ch.get('quiz_id')
                )
            )
            chapters_map[ch_id] = ch
            print(f"  Inserted Chapter {ch_id}: {ch.get('title')}")
        except Exception as e:
            print(f"  Failed to insert chapter {filepath}: {e}")

# 2. Migrate Labs
print("Migrating labs...")
labs_path = os.path.join(content_dir, 'labs.json')
lab_to_chapter_map = {}
if os.path.exists(labs_path):
    with open(labs_path, 'r', encoding='utf-8') as f:
        labs = json.load(f)
        for lab in labs:
            lab_id = lab.get('id')
            chapter_id = lab.get('chapter_id')
            lab_to_chapter_map[lab_id] = chapter_id
            cursor.execute(
                """
                INSERT INTO labs (id, title, chapter_id, description, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    lab_id,
                    lab.get('title'),
                    chapter_id,
                    lab.get('description'),
                    lab.get('status', 'published')
                )
            )
            print(f"  Inserted Lab {lab_id}: {lab.get('title')}")

# 3. Migrate Badges
print("Migrating badges...")
badges_path = os.path.join(content_dir, 'badges.json')
if os.path.exists(badges_path):
    with open(badges_path, 'r', encoding='utf-8') as f:
        badges = json.load(f)
        for b in badges:
            cursor.execute(
                """
                INSERT INTO badges (id, name, description, icon, xp_reward)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    b.get('id'),
                    b.get('name'),
                    b.get('description'),
                    b.get('icon'),
                    b.get('xp_reward', 0)
                )
            )
            print(f"  Inserted Badge {b.get('id')}: {b.get('name')}")

# 4. Migrate Experiments
print("Migrating experiments...")
exp_pattern = os.path.join(content_dir, 'experiments', '*.json')
for filepath in glob.glob(exp_pattern):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            exp = json.load(f)
            exp_id = exp.get('id')
            
            # Match experiment to chapter using lab_to_chapter_map
            chapter_id = lab_to_chapter_map.get(exp_id)
            
            cursor.execute(
                """
                INSERT INTO experiments (
                    id, chapter_id, title, aim, apparatus, theory,
                    `procedure`, observations, result, viva_questions, simulation_url
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    exp_id,
                    chapter_id,
                    exp.get('title'),
                    exp.get('aim'),
                    json.dumps(exp.get('apparatus', [])),
                    exp.get('theory'),
                    json.dumps(exp.get('procedure', [])),
                    json.dumps(exp.get('observations', [])),
                    exp.get('result'),
                    json.dumps(exp.get('viva_questions', [])),
                    exp.get('simulation_url')
                )
            )
            print(f"  Inserted Experiment {exp_id}: {exp.get('title')}")
        except Exception as e:
            print(f"  Failed to insert experiment {filepath}: {e}")

# 5. Migrate Quizzes & Quiz Questions
print("Migrating quizzes...")
quizzes_pattern = os.path.join(content_dir, 'quizzes', '*.json')
for filepath in glob.glob(quizzes_pattern):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            quiz = json.load(f)
            chapter_id = quiz.get('chapter_id')
            
            cursor.execute(
                """
                INSERT INTO quizzes (chapter_id, title, total_marks, duration_minutes)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    chapter_id,
                    quiz.get('title'),
                    quiz.get('total_marks', 100),
                    quiz.get('time_limit_minutes', 30)
                )
            )
            quiz_id = cursor.lastrowid
            
            # Migrate questions
            for q in quiz.get('questions', []):
                options = q.get('options', [])
                ans_str = q.get('answer')
                
                # Determine correct option letter A, B, C, or D
                correct_letter = 'A'
                try:
                    idx = options.index(ans_str)
                    correct_letter = chr(65 + idx) # 0->A, 1->B, ...
                except ValueError:
                    # If not exact match, check substring
                    found = False
                    for i, opt in enumerate(options):
                        if ans_str in opt or opt in ans_str:
                            correct_letter = chr(65 + i)
                            found = True
                            break
                    if not found:
                        print(f"    Warning: correct answer '{ans_str}' not in options {options} for question '{q.get('question')}'")
                
                cursor.execute(
                    """
                    INSERT INTO quiz_questions (
                        quiz_id, question, option_a, option_b, option_c, option_d,
                        correct_answer, explanation
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        quiz_id,
                        q.get('question'),
                        options[0] if len(options) > 0 else '',
                        options[1] if len(options) > 1 else '',
                        options[2] if len(options) > 2 else '',
                        options[3] if len(options) > 3 else '',
                        correct_letter,
                        q.get('explanation', '')
                    )
                )
            print(f"  Inserted Quiz for chapter {chapter_id}: {quiz.get('title')} with {len(quiz.get('questions', []))} questions")
        except Exception as e:
            print(f"  Failed to insert quiz {filepath}: {e}")

# 6. Migrate Reactions
print("Migrating reactions...")
reactions_path = os.path.join(os.path.dirname(__file__), 'reactions_extracted.json')
if os.path.exists(reactions_path):
    with open(reactions_path, 'r', encoding='utf-8') as f:
        reactions = json.load(f)
        for rxn in reactions:
            # Map class_level to string
            class_level = str(rxn.get('class_level', ''))
            
            # Map reactants/products (which are comma-separated strings in script.js reactions)
            # We will split them and store as a JSON array of strings
            reactants = [r.strip() for r in rxn.get('reactants', '').split(',') if r.strip()]
            products = [p.strip() for p in rxn.get('products', '').split(',') if p.strip()]
            
            cursor.execute(
                """
                INSERT INTO reactions (
                    id, chapter_id, class_level, name, equation, reaction_type,
                    reactants, products, conditions, explanation, mechanism, applications, not_occur
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    rxn.get('id'),
                    None, # chapter_id initially null
                    class_level,
                    rxn.get('name'),
                    rxn.get('equation'),
                    rxn.get('type', 'organic'),
                    json.dumps(reactants),
                    json.dumps(products),
                    rxn.get('conditions'),
                    rxn.get('explanation'),
                    json.dumps(rxn.get('mechanism', [])),
                    rxn.get('applications'),
                    rxn.get('not_occur')
                )
            )
        print(f"  Inserted {len(reactions)} reactions from reactions_extracted.json")
else:
    print("  reactions_extracted.json not found, skipping reactions seeding.")

conn.commit()
cursor.close()
conn.close()
print("Migration completed successfully!")
