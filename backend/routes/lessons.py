"""
Lessons & Categories routes.
"""
import os
import time

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from backend.db import get_db_connection, create_slug
from backend.auth_helpers import login_required, admin_required

lessons_bp = Blueprint('lessons', __name__)


@lessons_bp.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, description, color, icon, slug, meta_description, created_at "
            "FROM categories ORDER BY name"
        )
        categories = []
        for cat in cursor.fetchall():
            categories.append({
                "id": cat['id'], "name": cat['name'],
                "description": cat['description'], "color": cat['color'],
                "icon": cat['icon'], "slug": cat['slug'],
                "meta_description": cat['meta_description'],
                "created_at": str(cat['created_at']) if cat['created_at'] else None
            })
        return jsonify(categories), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@lessons_bp.route('/api/lessons', methods=['GET'])
@login_required
def get_lessons():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT l.id, l.title, l.description, c.name as category_name,
                   l.xp_min, l.xp_max, l.ar_model_url, l.category_id,
                   l.order_in_category, l.pass_threshold, l.slug
            FROM lessons l
            LEFT JOIN categories c ON l.category_id = c.id
            ORDER BY l.category_id, l.order_in_category
            """
        )
        lessons_list = [
            {
                "id": row['id'], "title": row['title'], "description": row['description'],
                "category": row['category_name'] if row['category_name'] else 'General',
                "category_id": row['category_id'],
                "xp_min": row['xp_min'], "xp_max": row['xp_max'],
                "ar_model_url": row['ar_model_url'],
                "order_in_category": row['order_in_category'],
                "pass_threshold": row['pass_threshold'],
                "slug": row['slug'] if row['slug'] else create_slug(row['title'])
            } for row in cursor.fetchall()
        ]
        return jsonify(lessons_list), 200
    except Exception as e:
        print(f"❌ ERROR in get_lessons: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


def _get_lesson_by_field(field, value):
    sql_query = "SELECT title, description, ar_model_url, xp_min, xp_max, id, slug FROM lessons WHERE "
    if field == 'id':
        sql_query += "id = %s"
    elif field == 'slug':
        sql_query += "slug = %s"
    else:
        return None
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query, (value,))
        lesson = cursor.fetchone()
        if not lesson:
            return None
        return {
            "title": lesson['title'], "description": lesson['description'],
            "ar_model_url": lesson['ar_model_url'], "xp_min": lesson['xp_min'],
            "xp_max": lesson['xp_max'], "id": lesson['id'], "slug": lesson['slug']
        }
    except Exception as e:
        print(f"❌ ERROR in _get_lesson_by_field: {e}")
        return None
    finally:
        if conn:
            conn.close()


@lessons_bp.route('/api/lessons/<int:lesson_id>', methods=['GET'])
@login_required
def get_lesson_by_id(lesson_id):
    lesson = _get_lesson_by_field('id', lesson_id)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404
    return jsonify(lesson), 200


@lessons_bp.route('/api/lessons/slug/<lesson_slug>', methods=['GET'])
@login_required
def get_lesson_by_slug(lesson_slug):
    lesson = _get_lesson_by_field('slug', lesson_slug)
    if not lesson:
        return jsonify({"error": "Lesson not found"}), 404
    return jsonify(lesson), 200


@lessons_bp.route('/api/lessons/complete', methods=['POST'])
@login_required
def complete_lesson():
    user_id = request.current_user['user_id']
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    xp_to_award = data.get('xp', 20)
    if not lesson_id:
        return jsonify({"error": "Missing lesson_id"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM completed_lessons WHERE user_id = %s AND lesson_id = %s",
            (user_id, lesson_id)
        )
        if cursor.fetchone():
            return jsonify({"message": "Lesson already completed"}), 200
        cursor.execute(
            "INSERT IGNORE INTO completed_lessons (user_id, lesson_id) VALUES (%s, %s)",
            (user_id, lesson_id)
        )
        cursor.execute("UPDATE users SET xp = xp + %s WHERE id = %s", (xp_to_award, user_id))
        cursor.execute("SELECT xp FROM users WHERE id = %s", (user_id,))
        new_xp = cursor.fetchone()['xp']
        conn.commit()
        return jsonify({"message": "Lesson completed!", "new_xp": new_xp}), 201
    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR in complete_lesson: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@lessons_bp.route('/api/lessons/unlocked', methods=['GET'])
@login_required
def get_unlocked_lessons():
    user_id = request.current_user['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT l.id, l.title, l.description, c.name as category_name, l.xp_min, l.xp_max,
                   l.ar_model_url, l.order_in_category, l.slug,
                   COALESCE(lp.is_completed, false) as is_completed,
                   COALESCE(lp.is_unlocked,
                       CASE WHEN l.order_in_category = 1 THEN true ELSE false END
                   ) as is_unlocked
            FROM lessons l
            LEFT JOIN categories c ON l.category_id = c.id
            LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.user_id = %s
            WHERE COALESCE(lp.is_unlocked,
                CASE WHEN l.order_in_category = 1 THEN true ELSE false END
            ) = true
            ORDER BY c.name, l.order_in_category
            """, (user_id,)
        )
        lessons = []
        for row in cursor.fetchall():
            lessons.append({
                "id": row['id'], "title": row['title'], "description": row['description'],
                "category": row['category_name'], "xp_min": row['xp_min'],
                "xp_max": row['xp_max'], "ar_model_url": row['ar_model_url'],
                "order_in_category": row['order_in_category'],
                "is_completed": row['is_completed'], "is_unlocked": row['is_unlocked'],
                "slug": row['slug'] if row['slug'] else create_slug(row['title'])
            })
        return jsonify(lessons), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@lessons_bp.route('/api/lessons/all-status', methods=['GET'])
@login_required
def get_all_lessons_with_status():
    user_id = request.current_user['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT l.id, l.title, l.description, c.name as category_name, l.xp_min, l.xp_max,
                   l.ar_model_url, l.category_id, l.order_in_category, l.slug,
                   COALESCE(lp.is_completed, false) as is_completed,
                   COALESCE(lp.is_unlocked,
                       CASE WHEN l.order_in_category = 1 THEN true ELSE false END
                   ) as is_unlocked
            FROM lessons l
            LEFT JOIN categories c ON l.category_id = c.id
            LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.user_id = %s
            ORDER BY c.name, l.order_in_category
            """, (user_id,)
        )
        lessons = []
        for row in cursor.fetchall():
            lessons.append({
                "id": row['id'], "title": row['title'], "description": row['description'],
                "category": row['category_name'], "xp_min": row['xp_min'],
                "xp_max": row['xp_max'], "ar_model_url": row['ar_model_url'],
                "category_id": row['category_id'], "order_in_category": row['order_in_category'],
                "is_completed": row['is_completed'], "is_unlocked": row['is_unlocked'],
                "slug": row['slug'] if row['slug'] else create_slug(row['title'])
            })
        return jsonify(lessons), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@lessons_bp.route('/api/leaderboard', methods=['GET'])
@login_required
def get_leaderboard():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, xp, avatar_url FROM users ORDER BY xp DESC LIMIT 50")
        leaderboard = []
        for row in cursor.fetchall():
            leaderboard.append({
                "name": row['name'], "xp": row['xp'],
                "avatar_url": row['avatar_url'] or "/uploads/profile.png"
            })
        return jsonify(leaderboard), 200
    except Exception as e:
        print(f"❌ ERROR in get_leaderboard: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@lessons_bp.route('/api/profile/badges', methods=['GET'])
@login_required
def get_user_badges():
    user_id = request.current_user['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.id, b.name, b.description, b.icon_url, b.xp_threshold, b.color, ub.earned_at
            FROM badges b
            INNER JOIN user_badges ub ON b.id = ub.badge_id
            WHERE ub.user_id = %s AND b.is_active = 1
            ORDER BY ub.earned_at DESC
            """, (user_id,)
        )
        badges = []
        for row in cursor.fetchall():
            badges.append({
                "id": row['id'], "name": row['name'], "description": row['description'],
                "icon_url": row['icon_url'], "xp_threshold": row['xp_threshold'],
                "color": row['color'],
                "earned_at": str(row['earned_at']) if row['earned_at'] else None
            })
        return jsonify(badges), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
