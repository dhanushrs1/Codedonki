"""
AI routes: /api/hint, /api/dialogue
"""
import os

from flask import Blueprint, request, jsonify

ai_bp = Blueprint('ai', __name__)


def _get_model():
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        return genai.GenerativeModel('gemini-2.0-flash-exp')
    except Exception as e:
        print(f"❌ WARNING: Could not configure Gemini AI: {e}")
        return None


@ai_bp.route('/api/hint', methods=['POST'])
def ai_hint():
    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip()
    student_name = data.get('student_name', 'Student')
    challenge = data.get('challenge', 1)
    topic = data.get('topic', 'print')

    topic_hints = {
        'print': {
            1: f'Hey {student_name}! Start with print, then add parentheses ( ), and put your text in quotes like "Hi!"',
            2: f'Remember {student_name}, numbers like 20 don\'t need quotes. Just: print(20)'
        },
        'variables': {
            1: f'Hey {student_name}! Store a number: variable_name = 3 (no quotes for numbers!)',
            2: f'Remember {student_name}, text needs quotes: variable_name = "text here"',
            3: f'{student_name}, use print(variable_name) to display what\'s stored!'
        },
        'input': {
            1: f'Hey {student_name}! Use input() to ask: name = input("What is your name? ")',
            2: f'Remember {student_name}, join text with +: print("Hello " + name)',
            3: f'{student_name}, ask another question: age = input("How old are you? ")'
        },
        'loops': {
            1: f'Hey {student_name}! Start with: for i in range(5):',
            2: f'Remember {student_name}, indent your code inside the loop!'
        }
    }

    default_hint = topic_hints.get(topic, {}).get(challenge) or f'Hey {student_name}! Check your syntax and try again!'

    if not os.getenv('GEMINI_API_KEY'):
        return jsonify({"hint": default_hint}), 200

    try:
        model = _get_model()
        if not model:
            return jsonify({"hint": default_hint}), 200

        system = f'You are Donki, a friendly female Python coding assistant. Address the student as "{student_name}". Keep hints SHORT (1-2 sentences). Be encouraging. DON\'T give the full answer.'
        prompt = f'Topic: {topic.upper()}. Student {student_name} typed: "{code or "(nothing yet)"}". Give a friendly hint.'
        resp = model.generate_content([system, prompt])
        text = getattr(resp, 'text', None) or default_hint
        return jsonify({"hint": text.strip().strip('"').strip("'")}), 200
    except Exception as e:
        print(f"❌ AI Hint error: {e}")
        return jsonify({"hint": default_hint}), 200


@ai_bp.route('/api/dialogue', methods=['POST'])
def ai_dialogue():
    data = request.get_json(silent=True) or {}
    student_name = data.get('student_name', 'Student')
    stage = data.get('stage', 'greeting')
    user_input = data.get('user_input', '')

    default_responses = {
        'greeting': f'Hello {student_name}! How are you?',
        'string_response': 'I\'m doing well!',
        'age_question': f'That\'s great {student_name}! How old are you?',
        'age_response': 'I\'m 20 years old!',
        'celebration': 'Awesome! You\'ve mastered print()!'
    }

    if not os.getenv('GEMINI_API_KEY'):
        return jsonify({
            "dialogue": default_responses.get(stage, '...'),
            "should_continue": True
        }), 200

    try:
        model = _get_model()
        if not model:
            return jsonify({"dialogue": default_responses.get(stage, '...'), "should_continue": True}), 200

        system_prompt = f"You are a friendly character in a Python learning game. Respond in ONE short sentence (max 10 words). Stage: {stage}. Student name: {student_name}."
        prompt = f"User input: '{user_input}'. Generate an appropriate {stage} response."
        resp = model.generate_content([system_prompt, prompt])
        text = getattr(resp, 'text', None) or default_responses.get(stage, '...')
        return jsonify({"dialogue": text.strip().strip('"').strip("'"), "should_continue": True}), 200
    except Exception as e:
        print(f"❌ Dialogue generation error: {e}")
        return jsonify({"dialogue": default_responses.get(stage, '...'), "should_continue": True}), 200
