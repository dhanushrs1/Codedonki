"""
Quiz management routes.
"""
import random

from flask import Blueprint, request, jsonify

from backend.db import get_db_connection
from backend.auth_helpers import login_required, admin_required

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/api/admin/quiz', methods=['GET', 'POST'])
@admin_required
def manage_quiz_questions():
    if request.method == 'GET':
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, lesson_id, question_text, option_a, option_b, option_c,
                       option_d, correct_answer, explanation
                FROM quiz_questions ORDER BY lesson_id, id
                """
            )
            return jsonify(list(cursor.fetchall())), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if conn:
                conn.close()

    # POST
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    question_text = data.get('question_text')
    option_a = data.get('option_a')
    option_b = data.get('option_b')
    option_c = data.get('option_c')
    option_d = data.get('option_d')
    correct_answer = data.get('correct_answer')
    explanation = data.get('explanation', '')

    if not all([lesson_id, question_text, option_a, option_b, option_c, option_d, correct_answer]):
        return jsonify({"error": "Missing required fields"}), 400
    if correct_answer not in ['A', 'B', 'C', 'D']:
        return jsonify({"error": "Correct answer must be A, B, C, or D"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_questions (lesson_id, question_text, option_a, option_b,
                                      option_c, option_d, correct_answer, explanation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (lesson_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
        )
        question_id = cursor.lastrowid
        conn.commit()
        return jsonify({"message": "Quiz question created successfully", "question_id": question_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@quiz_bp.route('/api/admin/quiz/<int:question_id>', methods=['PUT'])
@admin_required
def update_quiz_question(question_id):
    data = request.get_json()
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        update_fields = []
        update_values = []
        for field in ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation']:
            val = data.get(field)
            if val is not None:
                if field == 'correct_answer' and val not in ['A', 'B', 'C', 'D']:
                    return jsonify({"error": "Correct answer must be A, B, C, or D"}), 400
                update_fields.append(f"{field} = %s")
                update_values.append(val)
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        update_values.append(question_id)
        cursor.execute(f"UPDATE quiz_questions SET {', '.join(update_fields)} WHERE id = %s", update_values)
        if cursor.rowcount == 0:
            return jsonify({"error": "Quiz question not found"}), 404
        conn.commit()
        return jsonify({"message": "Quiz question updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@quiz_bp.route('/api/admin/quiz/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_quiz_question(question_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz_questions WHERE id = %s", (question_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Quiz question not found"}), 404
        conn.commit()
        return jsonify({"message": "Quiz question deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@quiz_bp.route('/api/admin/lessons/<int:lesson_id>/quiz', methods=['GET'])
@admin_required
def get_lesson_quiz_questions(lesson_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation "
            "FROM quiz_questions WHERE lesson_id = %s ORDER BY id",
            (lesson_id,)
        )
        return jsonify(list(cursor.fetchall())), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@quiz_bp.route('/api/quiz/<int:lesson_id>', methods=['GET'])
@login_required
def get_quiz_for_user(lesson_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, question_text, option_a, option_b, option_c, option_d "
            "FROM quiz_questions WHERE lesson_id = %s ORDER BY id",
            (lesson_id,)
        )
        return jsonify(list(cursor.fetchall())), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@quiz_bp.route('/api/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    user_id = request.current_user['user_id']
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    answers = data.get('answers')
    time_taken = data.get('time_taken', 0)

    if not lesson_id or not answers:
        return jsonify({"error": "Missing lesson_id or answers"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, correct_answer FROM quiz_questions WHERE lesson_id = %s", (lesson_id,)
        )
        questions = cursor.fetchall()
        if not questions:
            return jsonify({"error": "No quiz questions found for this lesson"}), 404

        correct_count = sum(
            1 for q in questions if answers.get(str(q['id'])) == q['correct_answer']
        )
        total_questions = len(questions)
        score = int((correct_count / total_questions) * 100)

        cursor.execute(
            "SELECT pass_threshold, xp_min, xp_max, category_id, order_in_category "
            "FROM lessons WHERE id = %s", (lesson_id,)
        )
        lesson_details = cursor.fetchone()
        if not lesson_details:
            return jsonify({"error": "Lesson not found"}), 404

        pass_threshold = lesson_details['pass_threshold']
        xp_min = lesson_details['xp_min']
        xp_max = lesson_details['xp_max']
        category_id = lesson_details['category_id']
        order_in_category = lesson_details['order_in_category']
        passed = score >= pass_threshold

        base_xp = random.randint(xp_min, xp_max) if passed else 0
        time_bonus = 0
        if passed and time_taken > 0:
            expected_time = total_questions * 30
            if time_taken < expected_time:
                time_saved = expected_time - time_taken
                max_bonus = base_xp * 0.5
                time_bonus = min(int(max_bonus * (time_saved / expected_time)), int(max_bonus))
            elif time_taken > expected_time * 2:
                time_bonus = -int(base_xp * 0.2)
        xp_awarded = max(base_xp + time_bonus, 0)

        cursor.execute(
            """
            INSERT INTO user_quiz_attempts (user_id, lesson_id, quiz_questions, user_answers, score, passed, xp_awarded)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, lesson_id, str(questions), str(answers), score, passed, xp_awarded)
        )

        if passed:
            cursor.execute("UPDATE users SET xp = xp + %s WHERE id = %s", (xp_awarded, user_id))
            cursor.execute("SELECT xp FROM users WHERE id = %s", (user_id,))
            new_total_xp = cursor.fetchone()['xp']

            cursor.execute(
                """
                INSERT INTO lesson_progress (user_id, lesson_id, is_completed, is_unlocked, xp_earned, completed_at)
                VALUES (%s, %s, 1, 1, %s, CURRENT_TIMESTAMP)
                ON DUPLICATE KEY UPDATE is_completed=1, is_unlocked=1, xp_earned=%s, completed_at=CURRENT_TIMESTAMP
                """,
                (user_id, lesson_id, xp_awarded, xp_awarded)
            )

            cursor.execute(
                """
                SELECT b.id, b.name, b.description, b.icon_url
                FROM badges b
                WHERE b.xp_threshold <= %s
                AND b.id NOT IN (SELECT ub.badge_id FROM user_badges ub WHERE ub.user_id = %s)
                AND b.is_active = 1
                """,
                (new_total_xp, user_id)
            )
            new_badges = cursor.fetchall()
            for badge in new_badges:
                cursor.execute(
                    "INSERT IGNORE INTO user_badges (user_id, badge_id) VALUES (%s, %s)",
                    (user_id, badge['id'])
                )

            cursor.execute(
                "SELECT id FROM lessons WHERE category_id = %s AND order_in_category = %s + 1 LIMIT 1",
                (category_id, order_in_category)
            )
            next_row = cursor.fetchone()
            if next_row:
                cursor.execute(
                    "INSERT INTO lesson_progress (user_id, lesson_id, is_unlocked) VALUES (%s, %s, 1) "
                    "ON DUPLICATE KEY UPDATE is_unlocked=1",
                    (user_id, next_row['id'])
                )

            conn.commit()
            return jsonify({
                "message": "Quiz submitted successfully", "score": score,
                "passed": passed, "xp_awarded": xp_awarded,
                "base_xp": base_xp, "time_bonus": time_bonus,
                "new_total_xp": new_total_xp,
                "new_badges": [{"id": b['id'], "name": b['name'], "description": b['description'], "icon_url": b['icon_url']} for b in new_badges]
            }), 200
        else:
            conn.commit()
            return jsonify({
                "message": "Quiz submitted successfully", "score": score,
                "passed": passed, "xp_awarded": 0,
                "retry_message": "You need to score at least 70% to pass. You can retry the quiz."
            }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
