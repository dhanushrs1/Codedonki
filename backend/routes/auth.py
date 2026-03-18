"""
Auth routes: /api/signup, /api/login, /api/forgot-password, /api/logout
"""
import os
import jwt
import datetime
import pymysql.err

from flask import Blueprint, request, jsonify
from passlib.hash import pbkdf2_sha256

from backend.db import get_db_connection
from backend.auth_helpers import get_jwt_secret, login_required

MYSQL_ERROR_DUPLICATE_KEY = 1062

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not name or not email or not password:
        return jsonify({"error": "Missing name, email, or password"}), 400
    hashed_password = pbkdf2_sha256.hash(password)
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, hashed_password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except pymysql.err.IntegrityError as e:
        conn.rollback()
        if e.args[0] == MYSQL_ERROR_DUPLICATE_KEY:
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, hashed_password, role FROM users WHERE email = %s", (email,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        if pbkdf2_sha256.verify(password, user['hashed_password']):
            token = jwt.encode(
                {
                    'user_id': user['id'],
                    'role': user['role'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                get_jwt_secret(),
                algorithm="HS256"
            )
            return jsonify({
                "message": "Login successful",
                "token": token,
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@auth_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "If the email exists, a reset link has been sent"}), 200
        reset_token = jwt.encode(
            {
                'user_id': user['id'],
                'type': 'password_reset',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            get_jwt_secret(),
            algorithm="HS256"
        )
        print(f"Password reset token for {email}: {reset_token}")
        return jsonify({"message": "If the email exists, a reset link has been sent"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@auth_bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    user_id = request.current_user['user_id']
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, email, role, xp, avatar_url FROM users WHERE id = %s", (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        avatar_url = user['avatar_url'] or "/uploads/profile.png"
        return jsonify({
            "name": user['name'],
            "email": user['email'],
            "role": user['role'],
            "xp": user['xp'],
            "avatar_url": avatar_url
        }), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@auth_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    user_id = request.current_user['user_id']
    data = request.get_json()
    new_name = data.get('name')
    if not new_name:
        return jsonify({"error": "Name is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
        conn.commit()
        return jsonify({"message": "Profile updated successfully", "name": new_name}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@auth_bp.route('/api/profile/password', methods=['PUT'])
@login_required
def change_password():
    user_id = request.current_user['user_id']
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    if not current_password or not new_password:
        return jsonify({"error": "Current password and new password are required"}), 400
    if len(new_password) < 6:
        return jsonify({"error": "New password must be at least 6 characters long"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        if not pbkdf2_sha256.verify(current_password, user['hashed_password']):
            return jsonify({"error": "Current password is incorrect"}), 400
        new_hash = pbkdf2_sha256.hash(new_password)
        cursor.execute("UPDATE users SET hashed_password = %s WHERE id = %s", (new_hash, user_id))
        conn.commit()
        return jsonify({"message": "Password changed successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@auth_bp.route('/api/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload profile picture — note: uploads are read-only on Vercel's filesystem."""
    user_id = request.current_user['user_id']
    if 'avatar' not in request.files:
        return jsonify({"error": "No avatar file provided"}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    try:
        import datetime as dt
        from werkzeug.utils import secure_filename
        from flask import current_app
        ext = os.path.splitext(file.filename)[1]
        filename = secure_filename(f"avatar_{user_id}_{int(dt.datetime.now().timestamp())}{ext}")
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        avatar_url = f"/uploads/{filename}"
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET avatar_url = %s WHERE id = %s", (avatar_url, user_id))
            conn.commit()
            return jsonify({"message": "Avatar updated successfully", "avatar_url": avatar_url}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                conn.close()
    except Exception as e:
        return jsonify({"error": f"File upload failed: {str(e)}"}), 500


@auth_bp.route('/api/user-info', methods=['GET'])
def get_user_info():
    """Returns basic user info for interactive lesson pages."""
    try:
        from backend.auth_helpers import get_jwt_identity
        identity, _ = get_jwt_identity()
        if identity and identity.get('user_id'):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM users WHERE id = %s", (identity['user_id'],))
                row = cursor.fetchone()
                conn.close()
                if row:
                    return jsonify({"name": row['name']}), 200
        return jsonify({"name": None}), 200
    except Exception as e:
        return jsonify({"name": None}), 200
