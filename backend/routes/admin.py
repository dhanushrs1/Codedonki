"""
Admin lesson and category management routes.
"""
import os
import time

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import pymysql

from backend.db import get_db_connection, create_slug
from backend.auth_helpers import admin_required

MYSQL_ERROR_DUPLICATE_KEY = 1062

admin_bp = Blueprint('admin', __name__)


# ─── Lessons ──────────────────────────────────────────────────────────────────

@admin_bp.route('/api/admin/lessons', methods=['POST'])
@admin_required
def create_lesson():
    data = request.get_json() if request.is_json else request.form.to_dict()
    title = data.get('title')
    description = data.get('description')
    category_id = data.get('category_id')
    xp_min = data.get('xp_min', 50)
    xp_max = data.get('xp_max', 100)
    order_in_category = data.get('order_in_category', 1)
    pass_threshold = data.get('pass_threshold', 70)
    ar_code = data.get('ar_code')
    if not title or not category_id:
        return jsonify({"error": "Missing title or category"}), 400

    model_url = None
    if ar_code:
        filename = f"lesson_{int(time.time())}.html"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(ar_code)
        model_url = f"/uploads/{filename}"
    elif 'ar_model' in request.files and request.files['ar_model'].filename:
        file = request.files['ar_model']
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        model_url = f"/uploads/{filename}"

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        lesson_slug = create_slug(title)
        cursor.execute(
            """
            INSERT INTO lessons (title, description, category_id, xp_min, xp_max,
                               order_in_category, pass_threshold, ar_model_url, slug)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (title, description, category_id, xp_min, xp_max, order_in_category, pass_threshold, model_url, lesson_slug)
        )
        lesson_id = cursor.lastrowid
        conn.commit()
        return jsonify({"message": "Lesson created successfully", "lesson_id": lesson_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/admin/lessons/<int:lesson_id>', methods=['GET'])
@admin_required
def get_lesson_details(lesson_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT l.*, c.name as category_name
            FROM lessons l
            LEFT JOIN categories c ON l.category_id = c.id
            WHERE l.id = %s
            """, (lesson_id,)
        )
        lesson = cursor.fetchone()
        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404
        return jsonify({
            'id': lesson['id'], 'title': lesson['title'],
            'description': lesson['description'], 'category_id': lesson['category_id'],
            'category': lesson.get('category_name'), 'ar_model_url': lesson['ar_model_url'],
            'xp_min': lesson['xp_min'], 'xp_max': lesson['xp_max'],
            'order_in_category': lesson['order_in_category'],
            'pass_threshold': lesson['pass_threshold'],
            'is_locked_by_default': lesson['is_locked_by_default']
        }), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/admin/lessons/<int:lesson_id>', methods=['PUT'])
@admin_required
def update_lesson(lesson_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    category_id = data.get('category_id')
    xp_min = data.get('xp_min')
    xp_max = data.get('xp_max')
    order_in_category = data.get('order_in_category')
    pass_threshold = data.get('pass_threshold')
    ar_code = data.get('ar_code')

    if not title and not ar_code:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        model_url = None
        if ar_code:
            filename = f"lesson_{lesson_id}_{int(time.time())}.html"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(ar_code)
            model_url = f"/uploads/{filename}"

        update_fields = []
        update_values = []
        if title:
            update_fields.extend(["title = %s", "slug = %s"])
            update_values.extend([title, create_slug(title)])
        if description is not None:
            update_fields.append("description = %s")
            update_values.append(description)
        if category_id:
            update_fields.append("category_id = %s")
            update_values.append(category_id)
        if xp_min is not None:
            update_fields.append("xp_min = %s")
            update_values.append(xp_min)
        if xp_max is not None:
            update_fields.append("xp_max = %s")
            update_values.append(xp_max)
        if order_in_category:
            update_fields.append("order_in_category = %s")
            update_values.append(order_in_category)
        if pass_threshold is not None:
            update_fields.append("pass_threshold = %s")
            update_values.append(pass_threshold)
        if model_url:
            update_fields.append("ar_model_url = %s")
            update_values.append(model_url)

        update_values.append(lesson_id)
        cursor.execute(f"UPDATE lessons SET {', '.join(update_fields)} WHERE id = %s", update_values)
        if cursor.rowcount == 0:
            return jsonify({"error": "Lesson not found"}), 404
        conn.commit()
        return jsonify({"message": "Lesson updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/admin/lessons/<int:lesson_id>', methods=['DELETE'])
@admin_required
def delete_lesson(lesson_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT category_id, order_in_category FROM lessons WHERE id = %s", (lesson_id,)
        )
        lesson_data = cursor.fetchone()
        if not lesson_data:
            return jsonify({"error": "Lesson not found"}), 404
        category_id = lesson_data['category_id']
        deleted_order = lesson_data['order_in_category']
        cursor.execute("DELETE FROM lessons WHERE id = %s", (lesson_id,))
        cursor.execute(
            "UPDATE lessons SET order_in_category = order_in_category - 1 "
            "WHERE category_id = %s AND order_in_category > %s",
            (category_id, deleted_order)
        )
        conn.commit()
        return jsonify({"message": "Lesson deleted successfully and remaining lessons reordered"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/admin/lessons/next-level', methods=['GET'])
@admin_required
def get_next_level():
    category_id = request.args.get('category_id')
    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(MAX(order_in_category), 0) + 1 AS next_level FROM lessons WHERE category_id = %s",
            (category_id,)
        )
        next_level = cursor.fetchone()['next_level']
        return jsonify({"next_level": next_level}), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


# ─── Categories ───────────────────────────────────────────────────────────────

@admin_bp.route('/api/admin/categories', methods=['POST'])
@admin_required
def create_category():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    color = data.get('color', '#3498db')
    icon = data.get('icon', 'fas fa-tag')
    slug = data.get('slug', '') or create_slug(name or '')
    meta_description = data.get('meta_description', '')
    if not name:
        return jsonify({"error": "Category name is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categories (name, description, color, icon, slug, meta_description) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, description, color, icon, slug, meta_description)
        )
        category_id = cursor.lastrowid
        conn.commit()
        return jsonify({"message": "Category created successfully", "category_id": category_id}), 201
    except pymysql.Error as e:
        conn.rollback()
        if e.args[0] == MYSQL_ERROR_DUPLICATE_KEY:
            return jsonify({"error": "Category name or slug already exists"}), 409
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"error": "Category name is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        update_fields = []
        update_values = []
        for field, val in [
            ('name', name), ('description', data.get('description')),
            ('color', data.get('color')), ('icon', data.get('icon')),
            ('slug', data.get('slug')), ('meta_description', data.get('meta_description'))
        ]:
            if val is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(val)
        update_values.append(category_id)
        cursor.execute(f"UPDATE categories SET {', '.join(update_fields)} WHERE id = %s", update_values)
        if cursor.rowcount == 0:
            return jsonify({"error": "Category not found"}), 404
        conn.commit()
        return jsonify({"message": "Category updated successfully"}), 200
    except pymysql.Error as e:
        conn.rollback()
        if e.args[0] == MYSQL_ERROR_DUPLICATE_KEY:
            return jsonify({"error": "Category name or slug already exists"}), 409
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@admin_bp.route('/api/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Category not found"}), 404
        conn.commit()
        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


# ─── AI Suggestion ────────────────────────────────────────────────────────────

@admin_bp.route('/api/ai-suggestion', methods=['POST'])
@admin_required
def get_ai_suggestion():
    import google.generativeai as genai
    data = request.get_json()
    lesson_title = data.get('title')
    if not lesson_title:
        return jsonify({"error": "Missing lesson title"}), 400
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""I am a student learning programming on a gamified AR/VR platform called Codedonki.
I just finished a lesson called "{lesson_title}".
Give me one short, helpful tip (about 1-2 sentences) related to this topic
to help me remember it. Start the tip directly, e.g., "Remember that..."
or "A great way to practice...". Do not use markdown."""
        response = model.generate_content(prompt)
        return jsonify({"suggestion": response.text}), 200
    except Exception as e:
        print(f"❌ ERROR in get_ai_suggestion: {e}")
        return jsonify({"suggestion": "Great job on finishing the lesson! Make sure to practice what you've learned."}), 200


# ─── Setup Database Route ─────────────────────────────────────────────────────

@admin_bp.route('/setup-database')
def setup_database_route():
    from backend.db import setup_database
    if setup_database():
        return jsonify({"message": "Database setup completed successfully!", "status": "success"})
    else:
        return jsonify({"message": "Database setup failed!", "status": "error"}), 500
