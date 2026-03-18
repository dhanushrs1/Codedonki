"""
Badges management routes.
"""
import os
import time

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import pymysql

from backend.db import get_db_connection
from backend.auth_helpers import login_required, admin_required, get_jwt_identity

MYSQL_ERROR_DUPLICATE_KEY = 1062

badges_bp = Blueprint('badges', __name__)


@badges_bp.route('/api/badges', methods=['GET'])
@login_required
def get_all_badges():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        identity, _ = get_jwt_identity()
        is_admin = identity and identity.get('role') == 'admin'
        cursor = conn.cursor()
        if is_admin:
            cursor.execute(
                "SELECT id, name, description, icon_url, xp_threshold, color, is_active "
                "FROM badges ORDER BY xp_threshold"
            )
        else:
            cursor.execute(
                "SELECT id, name, description, icon_url, xp_threshold, color, is_active "
                "FROM badges WHERE is_active = 1 ORDER BY xp_threshold"
            )
        badges = []
        for row in cursor.fetchall():
            b = {
                "id": row['id'], "name": row['name'], "description": row['description'],
                "icon_url": row['icon_url'], "xp_threshold": row['xp_threshold'],
                "color": row['color']
            }
            if is_admin:
                b['is_active'] = bool(row['is_active'])
            badges.append(b)
        return jsonify(badges), 200
    except Exception as e:
        print(f"❌ Error in get_all_badges: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@badges_bp.route('/api/admin/badges', methods=['POST'])
@admin_required
def create_badge():
    try:
        name = str(request.form.get('name', ''))
        description = str(request.form.get('description', ''))
        xp_threshold = request.form.get('xp_threshold')
        color = str(request.form.get('color', '#FFD700'))
        if not name or not xp_threshold:
            return jsonify({"error": "Badge name and XP threshold are required"}), 400
        try:
            xp_threshold = int(xp_threshold)
        except (ValueError, TypeError):
            return jsonify({"error": "XP threshold must be a number"}), 400

        icon_url = ''
        if 'badge_icon' in request.files and request.files['badge_icon'].filename:
            file = request.files['badge_icon']
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"badge_{name.replace(' ', '_')}_{int(time.time())}{ext}")
            badges_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'badges')
            os.makedirs(badges_folder, exist_ok=True)
            file.save(os.path.join(badges_folder, filename))
            icon_url = f"/uploads/badges/{filename}"

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO badges (name, description, icon_url, xp_threshold, color) VALUES (%s, %s, %s, %s, %s)",
                (name, description, icon_url, xp_threshold, color)
            )
            badge_id = cursor.lastrowid
            conn.commit()
            return jsonify({"message": "Badge created successfully", "badge_id": badge_id}), 201
        except pymysql.Error as e:
            conn.rollback()
            if e.args[0] == MYSQL_ERROR_DUPLICATE_KEY:
                return jsonify({"error": "Badge name already exists"}), 409
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                conn.close()
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@badges_bp.route('/api/admin/badges/<int:badge_id>', methods=['PUT'])
@admin_required
def update_badge(badge_id):
    conn = None
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        xp_threshold = request.form.get('xp_threshold')
        if xp_threshold is not None:
            try:
                xp_threshold = int(xp_threshold)
            except (ValueError, TypeError):
                return jsonify({"error": "XP threshold must be a number"}), 400
        color = request.form.get('color')
        is_active_str = request.form.get('is_active')
        is_active = None
        if is_active_str is not None:
            is_active = 1 if str(is_active_str).lower() in ['true', '1', 'yes'] else 0

        existing_icon_url = request.form.get('existing_icon_url')
        icon_url = existing_icon_url
        if 'badge_icon' in request.files and request.files['badge_icon'].filename:
            file = request.files['badge_icon']
            ext = os.path.splitext(file.filename)[1]
            badge_name = name or f"badge_{badge_id}"
            filename = secure_filename(f"badge_{badge_name.replace(' ', '_')}_{int(time.time())}{ext}")
            badges_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'badges')
            os.makedirs(badges_folder, exist_ok=True)
            file.save(os.path.join(badges_folder, filename))
            icon_url = f"/uploads/badges/{filename}"

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        update_fields = []
        update_values = []
        for field, val in [('name', name), ('description', description), ('icon_url', icon_url),
                           ('xp_threshold', xp_threshold), ('color', color), ('is_active', is_active)]:
            if val is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(val)
        if not update_fields:
            conn.close()
            return jsonify({"error": "No fields to update"}), 400
        update_values.append(badge_id)
        cursor.execute(f"UPDATE badges SET {', '.join(update_fields)} WHERE id = %s", update_values)
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Badge not found"}), 404
        conn.commit()
        conn.close()
        return jsonify({"message": "Badge updated successfully"}), 200
    except pymysql.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        if e.args[0] == MYSQL_ERROR_DUPLICATE_KEY:
            return jsonify({"error": "Badge name already exists"}), 409
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@badges_bp.route('/api/admin/badges/<int:badge_id>', methods=['DELETE'])
@admin_required
def delete_badge(badge_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM badges WHERE id = %s", (badge_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Badge not found"}), 404
        conn.commit()
        return jsonify({"message": "Badge deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
