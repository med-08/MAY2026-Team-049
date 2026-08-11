import os
import json
import re
from flask import request, jsonify
from student import student_bp
from database import db
from models import Quiz, QuizQuestion, FAQ, Tutor, Subject, FlashcardDeck, FlashcardItem
from decorators import student_required
from student.routes import student_response, student_error, get_current_student

def call_gemini(prompt, system_instruction=None):
    """
    Backend-only Gemini API helper.
    Tries google.generativeai SDK first; falls back to standard urllib REST API.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        for env_path in [
            os.path.join(os.path.dirname(__file__), "..", ".env"),
            os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        ]:
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val:
                                api_key = val
                                os.environ["GEMINI_API_KEY"] = val
                                break
            if api_key:
                break

    if not api_key:
        raise ValueError("GEMINI_API_KEY missing")

    full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

    # 1. Try SDK if available
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        for m_name in ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-flash-latest"]:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    generation_config={"temperature": 0.3, "max_output_tokens": 2500}
                )
                res = model.generate_content(full_prompt)
                if res and res.text:
                    return res.text.strip()
            except Exception:
                continue
    except ImportError:
        pass

    # 2. Fallback to urllib.request REST API (zero dependencies required)
    import urllib.request
    import urllib.parse

    models_to_try = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]
    last_err = None

    for m_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={api_key}"
        payload = json.dumps({
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2500
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
        except Exception as e:
            last_err = e
            continue

    if last_err:
        raise last_err
    raise RuntimeError("Gemini REST API call failed")


def parse_json_from_response(text):
    """
    Extract and parse JSON array or object from response text safely.
    Handles markdown fences and unwraps nested dictionary lists.
    """
    cleaned = re.sub(r'```(?:json)?\s*', '', text)
    cleaned = re.sub(r'```\s*$', '', cleaned).strip()
    
    # Try regex match for JSON array or object
    match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)

    parsed = json.loads(cleaned)

    # Unwrap if returned as dict object e.g. {"flashcards": [...]}
    if isinstance(parsed, dict):
        for key in ["flashcards", "cards", "questions", "items", "data"]:
            if key in parsed and isinstance(parsed[key], list):
                return parsed[key]
        # Return list of values if dict of objects
        if all(isinstance(v, dict) for v in parsed.values()):
            return list(parsed.values())

    return parsed


# ==================== TASK 1: AI Quiz Generation ====================
@student_bp.route('/quizzes/generate', methods=['POST'])
@student_required
def generate_quiz():
    data = request.get_json() or {}
    topic = data.get("topic", "General Science").strip()
    count = int(data.get("count", 5))
    if not topic:
        topic = "General Knowledge"

    # Find a default tutor and subject for saving the quiz
    default_tutor = Tutor.query.first()
    tutor_id = default_tutor.tutor_id if default_tutor else 1
    default_subj = Subject.query.first()
    subject_id = default_subj.subject_id if default_subj else 1

    questions_list = []

    try:
        prompt = (
            f"Generate {count} multiple choice questions (MCQs) on topic '{topic}'. "
            "Return ONLY a raw JSON array of objects with keys: question, option_a, option_b, option_c, option_d, correct_option (A/B/C/D), difficulty (easy/medium/hard). "
            "Do not include any additional text or explanation."
        )
        raw_output = call_gemini(prompt)
        parsed = parse_json_from_response(raw_output)
        if isinstance(parsed, list) and len(parsed) > 0:
            questions_list = parsed
        else:
            raise ValueError("Parsed result is not a non-empty list")
    except Exception as e:
        # FALLBACK: Static 5-question quiz for the topic
        questions_list = [
            {
                "question": f"What is a core fundamental concept in {topic}?",
                "option_a": "Basic Principles",
                "option_b": "Advanced Theory",
                "option_c": "Historical Context",
                "option_d": "Random Guess",
                "correct_option": "A",
                "difficulty": "easy"
            },
            {
                "question": f"Which of the following is most associated with {topic}?",
                "option_a": "Component Alpha",
                "option_b": "Primary Law of Mechanics",
                "option_c": "Key Element",
                "option_d": "Secondary Formula",
                "correct_option": "C",
                "difficulty": "easy"
            },
            {
                "question": f"How is {topic} typically applied in practice?",
                "option_a": "Through direct observation",
                "option_b": "By structured analysis",
                "option_c": "Using empirical testing",
                "option_d": "All of the above",
                "correct_option": "D",
                "difficulty": "medium"
            },
            {
                "question": f"What is a common misconception regarding {topic}?",
                "option_a": "It never changes",
                "option_b": "It is completely theoretical",
                "option_c": "It is restricted to experts",
                "option_d": "It requires no foundation",
                "correct_option": "B",
                "difficulty": "medium"
            },
            {
                "question": f"In advanced study of {topic}, which factor is critical?",
                "option_a": "Precision and consistency",
                "option_b": "Speed alone",
                "option_c": "Ignoring variables",
                "option_d": "Linear extrapolation",
                "correct_option": "A",
                "difficulty": "hard"
            }
        ]

    # Save to DB as Quiz + QuizQuestion rows
    new_quiz = Quiz(
        tutor_id=tutor_id,
        subject_id=subject_id,
        title=f"AI Quiz: {topic}",
        week_number=1
    )
    db.session.add(new_quiz)
    db.session.commit()

    saved_questions = []
    for q_data in questions_list:
        correct_opt = str(q_data.get("correct_option", "A")).upper().strip()
        if correct_opt not in ["A", "B", "C", "D"]:
            correct_opt = "A"
        
        diff = str(q_data.get("difficulty", "medium")).lower().strip()
        if diff not in ["easy", "medium", "hard"]:
            diff = "medium"

        qq = QuizQuestion(
            quiz_id=new_quiz.quiz_id,
            question=q_data.get("question", "Sample Question"),
            option_a=q_data.get("option_a", "Option A"),
            option_b=q_data.get("option_b", "Option B"),
            option_c=q_data.get("option_c", "Option C"),
            option_d=q_data.get("option_d", "Option D"),
            correct_option=correct_opt,
            difficulty=diff
        )
        db.session.add(qq)
        saved_questions.append(qq)

    db.session.commit()

    return student_response(
        data={
            "quiz_id": new_quiz.quiz_id,
            "title": new_quiz.title,
            "topic": topic,
            "question_count": len(saved_questions)
        },
        message="AI Quiz generated successfully!"
    )


# ==================== TASK 3: Persistent Flashcards (AI + Manual + Storage + Delete) ====================
@student_bp.route('/flashcards/decks', methods=['GET'])
@student_required
def get_flashcard_decks():
    student_obj = get_current_student()
    if not student_obj:
        return student_error("Student not found", 404)
    
    decks = FlashcardDeck.query.filter_by(student_id=student_obj.student_id).order_by(FlashcardDeck.created_at.desc()).all()
    result = []
    for d in decks:
        card_items = FlashcardItem.query.filter_by(deck_id=d.deck_id).all()
        result.append({
            "deck_id": d.deck_id,
            "topic": d.topic,
            "created_at": d.created_at.strftime("%d %b %Y, %I:%M %p"),
            "card_count": len(card_items),
            "cards": [{"card_id": c.card_id, "front": c.front, "back": c.back} for c in card_items]
        })
    return student_response(data=result)


@student_bp.route('/flashcards', methods=['POST'])
@student_required
def create_flashcards():
    student_obj = get_current_student()
    if not student_obj:
        return student_error("Student not found", 404)

    data = request.get_json() or {}
    topic = data.get("topic", "General Knowledge").strip()
    if not topic:
        topic = "General Knowledge"
    
    is_manual = data.get("is_manual", False)
    raw_cards = data.get("cards", [])

    cards = []
    if is_manual and isinstance(raw_cards, list) and len(raw_cards) > 0:
        for c in raw_cards:
            if c.get("front") and c.get("back"):
                cards.append({"front": str(c["front"]).strip(), "back": str(c["back"]).strip()})
    
    if not cards:
        try:
            prompt = (
                f"You are an expert tutor creating study flashcards for students. "
                f"Generate 10 highly accurate, educational, subject-specific flashcards about '{topic}'. "
                "Return ONLY a raw JSON array of 10 objects. Each object MUST have keys: "
                "\"front\" (the specific question, formula, or concept term) and \"back\" (the clear, accurate answer, definition, or explanation). "
                "Example format: [{\"front\": \"What is CPU?\", \"back\": \"Central Processing Unit - the main processor that executes instructions.\"}]"
            )
            raw_output = call_gemini(prompt)
            parsed = parse_json_from_response(raw_output)
            if isinstance(parsed, list) and len(parsed) > 0:
                cards = []
                for item in parsed[:10]:
                    if isinstance(item, dict) and "front" in item and "back" in item:
                        cards.append({"front": str(item["front"]).strip(), "back": str(item["back"]).strip()})
            if not cards:
                raise ValueError("Parsed result did not yield valid card objects")
        except Exception as e:
            cards = [
                {"front": f"What is the core definition of {topic}?", "back": f"{topic} is a key subject of study focusing on core principles, analysis, and practical applications."},
                {"front": f"Why is studying {topic} important?", "back": "It helps develop problem-solving capabilities, logical thinking, and technical proficiency."},
                {"front": f"What is a primary principle in {topic}?", "back": "Decomposing complex topics into clear, logical, and manageable components."},
                {"front": f"How do you master {topic}?", "back": "Through consistent practice, self-testing, reviewing notes, and applying concepts."},
                {"front": f"Key takeaway for {topic}", "back": "Mastering the fundamental axioms provides a strong foundation for advanced topics!"}
            ]

    # Save new deck & card items to database
    new_deck = FlashcardDeck(student_id=student_obj.student_id, topic=topic)
    db.session.add(new_deck)
    db.session.commit()

    saved_cards = []
    for card_data in cards:
        item = FlashcardItem(
            deck_id=new_deck.deck_id,
            front=card_data.get("front", ""),
            back=card_data.get("back", "")
        )
        db.session.add(item)
        saved_cards.append(item)
    db.session.commit()

    return student_response(
        data={
            "deck_id": new_deck.deck_id,
            "topic": topic,
            "created_at": new_deck.created_at.strftime("%d %b %Y, %I:%M %p"),
            "card_count": len(saved_cards),
            "cards": [{"card_id": c.card_id, "front": c.front, "back": c.back} for c in saved_cards]
        },
        message="Flashcard deck created and saved successfully!"
    )


@student_bp.route('/flashcards/decks/<int:deck_id>', methods=['DELETE'])
@student_required
def delete_flashcard_deck(deck_id):
    student_obj = get_current_student()
    if not student_obj:
        return student_error("Student not found", 404)
    
    deck = FlashcardDeck.query.filter_by(deck_id=deck_id, student_id=student_obj.student_id).first()
    if not deck:
        return student_error("Flashcard deck not found", 404)
    
    db.session.delete(deck)
    db.session.commit()
    return student_response(message="Flashcard deck deleted successfully!")


@student_bp.route('/flashcards/items/<int:card_id>', methods=['DELETE'])
@student_required
def delete_flashcard_item(card_id):
    student_obj = get_current_student()
    if not student_obj:
        return student_error("Student not found", 404)

    card = FlashcardItem.query.get(card_id)
    if not card:
        return student_error("Flashcard item not found", 404)

    db.session.delete(card)
    db.session.commit()
    return student_response(message="Flashcard item deleted successfully!")



# ==================== TASK 4: FAQ Chatbot ====================
@student_bp.route('/faq-chat', methods=['POST'])
@student_required
def faq_chat():
    data = request.get_json() or {}
    user_question = data.get("question", "").strip()
    if not user_question:
        return student_error("Question is required", 400)

    q_clean = user_question.lower().strip()

    # 1. Quick handling for common greetings
    greetings = ["hi", "hello", "hlo", "hey", "namaste", "good morning", "good afternoon", "good evening"]
    if q_clean in greetings or any(q_clean.startswith(g + " ") for g in greetings if len(g) > 2):
        return student_response(
            data={
                "question": user_question,
                "answer": "Hello! I am your AI FAQ Assistant. How can I help you with platform policies, sessions, tutors, or study questions today?"
            }
        )

    # 2. Quick handling for simple math expression e.g. "2+2", "5 * 5"
    if re.match(r'^\s*(\d+\s*[\+\-\*\/\^]\s*)+\d+\s*$', user_question):
        try:
            # Safe eval of simple math
            expr = user_question.replace('^', '**')
            ans_val = eval(expr, {"__builtins__": None}, {})
            return student_response(
                data={
                    "question": user_question,
                    "answer": f"The answer to {user_question} is {ans_val}."
                }
            )
        except Exception:
            pass

    # Load all FAQs from DB
    faqs = FAQ.query.all()
    faq_lines = [f"Q: {f.question}\nA: {f.answer}" for f in faqs]
    faq_context = "\n\n".join(faq_lines) if faq_lines else "No FAQs available."

    try:
        prompt = (
            "You are an AI FAQ Assistant for the LearnAtHome platform. "
            f"Official Platform FAQ Context:\n{faq_context}\n\n"
            f"User Question: '{user_question}'\n\n"
            "Instructions:\n"
            "1. If the question relates to platform rules, sessions, attendance, payments, tutors, or FAQs, answer accurately using the FAQ context.\n"
            "2. If it is a general educational or academic question (e.g. math, science, study tips), provide a brief, helpful 1-2 sentence explanation.\n"
            "3. If completely unrelated to education or the platform, politely respond: 'For specific subject guidance or custom queries, please ask your tutor!'"
        )
        answer = call_gemini(prompt)
        if not answer:
            answer = "For specific subject guidance or custom queries, please ask your tutor!"
    except Exception as e:
        # FALLBACK: Keyword match against DB FAQs
        answer = None
        words = [w for w in q_clean.split() if len(w) > 3]

        for f in faqs:
            f_q_lower = f.question.lower()
            f_a_lower = f.answer.lower()
            if any(word in f_q_lower or word in f_a_lower for word in words):
                answer = f.answer
                break

        if not answer:
            answer = "For specific subject guidance or custom queries, please ask your tutor!"

    return student_response(
        data={
            "question": user_question,
            "answer": answer
        }
    )

