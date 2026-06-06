import json

def generate_course_outline(topic, class_level):
    """Mocks AI generation of a course outline. Returns a structured JSON dictionary."""
    return {
        "topic": topic,
        "class_level": class_level,
        "modules": [
            {
                "title": f"Introduction to {topic}",
                "order_index": 1,
                "lessons": [
                    {"title": f"Basic concepts of {topic}", "order_index": 1},
                    {"title": f"Historical development of {topic}", "order_index": 2}
                ]
            },
            {
                "title": f"Advanced {topic} applications",
                "order_index": 2,
                "lessons": [
                    {"title": f"Practical experiments in {topic}", "order_index": 1},
                    {"title": f"Future of {topic}", "order_index": 2}
                ]
            }
        ]
    }

def generate_quiz_mcqs(text_source, num_questions=3):
    """Mocks parsing text to generate MCQs. Returns a list of structured JSON question objects."""
    questions = []
    for i in range(1, num_questions + 1):
        questions.append({
            "question_text": f"AI Generated Question {i} based on source text.",
            "option_a": f"AI Option A for Q{i}",
            "option_b": f"AI Option B for Q{i} (Correct)",
            "option_c": f"AI Option C for Q{i}",
            "option_d": f"AI Option D for Q{i}",
            "correct_option": "B",
            "explanation": f"Explanation for AI question {i} generated from context."
        })
    return questions
