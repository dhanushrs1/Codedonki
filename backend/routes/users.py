"""
User management routes (admin only).
"""
from flask import Blueprint, request, jsonify

from backend.db import get_db_connection
from backend.auth_helpers import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.name, u.email, u.xp, u.avatar_url, u.created_at, u.role,
                   COUNT(lp.lesson_id) as completed_lessons,
                   COUNT(ub.badge_id) as badges_earned
            FROM users u
            LEFT JOIN lesson_progress lp ON u.id = lp.user_id AND lp.is_completed = 1
            LEFT JOIN user_badges ub ON u.id = ub.user_id
            GROUP BY u.id, u.name, u.email, u.xp, u.avatar_url, u.created_at, u.role
            ORDER BY u.xp DESC
            """
        )
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row['id'], "name": row['name'], "email": row['email'],
                "xp": row['xp'], "avatar_url": row['avatar_url'],
                "created_at": str(row['created_at']) if row['created_at'] else None,
                "role": row['role'] or "user",
                "completed_lessons": row['completed_lessons'],
                "badges_earned": row['badges_earned']
            })
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@users_bp.route('/api/admin/users/<int:user_id>/reset-progress', methods=['PUT'])
@admin_required
def reset_user_progress(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET xp = 0 WHERE id = %s", (user_id,))
        cursor.execute("DELETE FROM lesson_progress WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_badges WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM user_quiz_attempts WHERE user_id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": "User progress reset successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@users_bp.route('/api/admin/users/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        for table in ['user_quiz_attempts', 'user_badges', 'lesson_progress']:
            cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": f"User {user['name']} deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@users_bp.route('/api/admin/users/<int:user_id>/promote', methods=['PUT'])
@admin_required
def promote_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        if user['role'] == 'admin':
            return jsonify({"error": "User is already an admin"}), 400
        cursor.execute("UPDATE users SET role = 'admin' WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": f"User {user['name']} promoted to admin successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@users_bp.route('/api/admin/users/<int:user_id>/award-badges', methods=['POST'])
@admin_required
def award_missing_badges(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, xp FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        cursor.execute(
            """
            SELECT b.id, b.name, b.xp_threshold FROM badges b
            WHERE b.xp_threshold <= %s AND b.is_active = 1
            AND b.id NOT IN (SELECT ub.badge_id FROM user_badges ub WHERE ub.user_id = %s)
            ORDER BY b.xp_threshold
            """, (user['xp'], user_id)
        )
        missing_badges = cursor.fetchall()
        if not missing_badges:
            return jsonify({"message": f"User {user['name']} already has all eligible badges"}), 200
        awarded_badges = []
        for badge in missing_badges:
            cursor.execute(
                "INSERT IGNORE INTO user_badges (user_id, badge_id, earned_at) VALUES (%s, %s, CURRENT_TIMESTAMP)",
                (user_id, badge['id'])
            )
            awarded_badges.append({"name": badge['name'], "xp_threshold": badge['xp_threshold']})
        conn.commit()
        return jsonify({
            "message": f"Awarded {len(awarded_badges)} badges to {user['name']}",
            "awarded_badges": awarded_badges
        }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@users_bp.route('/api/admin/users/<int:user_id>/activity', methods=['GET'])
@admin_required
def get_user_recent_activity(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        activities = []
        try:
            cursor.execute("SELECT name, created_at FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            if row and row['created_at']:
                activities.append({
                    "type": "registration", "title": "Joined the platform",
                    "details": row['name'], "timestamp": str(row['created_at'])
                })
        except Exception:
            pass
        try:
            cursor.execute(
                """
                SELECT l.title as lesson_title, lp.completed_at, lp.xp_earned
                FROM lesson_progress lp JOIN lessons l ON l.id = lp.lesson_id
                WHERE lp.user_id = %s AND lp.is_completed = 1 AND lp.completed_at IS NOT NULL
                ORDER BY lp.completed_at DESC LIMIT 20
                """, (user_id,)
            )
            for r in cursor.fetchall():
                activities.append({
                    "type": "completion", "title": "Completed lesson",
                    "details": r['lesson_title'], "xp": r['xp_earned'] or 0,
                    "timestamp": str(r['completed_at'])
                })
        except Exception:
            pass
        try:
            cursor.execute(
                """
                SELECT l.title as lesson_title, uqa.score, uqa.passed, uqa.attempted_at
                FROM user_quiz_attempts uqa JOIN lessons l ON l.id = uqa.lesson_id
                WHERE uqa.user_id = %s ORDER BY uqa.attempted_at DESC LIMIT 20
                """, (user_id,)
            )
            for r in cursor.fetchall():
                activities.append({
                    "type": "quiz", "title": "Quiz attempted",
                    "details": r['lesson_title'], "score": r['score'],
                    "passed": bool(r['passed']), "timestamp": str(r['attempted_at'])
                })
        except Exception:
            pass

        activities.sort(key=lambda x: str(x.get('timestamp', '')), reverse=True)
        return jsonify(activities[:30]), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
