import os
import mimetypes
import re 
import sqlite3
import jwt
import datetime, time
import functools 
import google.generativeai as genai 
from flask import Flask, request, jsonify, send_from_directory, render_template, g, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash 


# Load environment variables
load_dotenv()

# --- NEW: Configure Gemini API ---
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"❌ WARNING: Could not configure Gemini AI. API key missing or invalid. {e}")


# Initialize the Flask app
app = Flask(__name__, static_folder='public', static_url_path='/static')

# --- UPDATED: CORS Configuration ---
# This setup trusts your frontend dev server, Flask server, and 'file://'
CORS(app, 
     origins=["http://127.0.0.1:5500", "http://127.0.0.1:5501", "http://127.0.0.1:5000", "http://localhost:5000", "null"],
     supports_credentials=True)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), 'uploads')
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# --- Make user available to templates ---
@app.before_request
def load_current_user():
    g.user = session.get('user')

# Lightweight AI hint proxy (no API key on frontend)
@app.route('/api/hint', methods=['POST'])
def ai_hint():
    """Gemini AI-powered hints - IMPORTANT: Auto-triggers when student makes mistakes"""
    data = request.get_json(silent=True) or {}
    code = (data.get('code') or '').strip()
    student_name = data.get('student_name', 'Student')
    challenge = data.get('challenge', 1)
    topic = data.get('topic', 'print')  # NEW: Topic parameter (print, variables, loops, etc.)
    
    # Topic-specific default hints
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
    
    # Get appropriate default hint
    if topic in topic_hints and challenge in topic_hints[topic]:
        default_hint = topic_hints[topic][challenge]
    else:
        default_hint = f'Hey {student_name}! Check your syntax and try again!'
    
    try:
        if not os.getenv('GEMINI_API_KEY'):
            return jsonify({"hint": default_hint}), 200
            
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build topic-specific context and goals
        if topic == 'print':
            if challenge == 1:
                goal = 'help them type print() with ANY text in quotes, like print("Hi!")'
                context = f'{student_name} is learning to use print() with strings (text in quotes)'
            else:
                goal = 'help them type print() with a number (NO quotes), like print(20)'
                context = f'{student_name} is learning to use print() with numbers (no quotes)'
                
        elif topic == 'variables':
            if challenge == 1:
                goal = 'help them store a NUMBER in a variable: variable_name = 3 (NO quotes!)'
                context = f'{student_name} is learning to STORE NUMBERS in variables using the = operator'
            elif challenge == 2:
                goal = 'help them store TEXT in a variable: variable_name = "text" (quotes REQUIRED for text!)'
                context = f'{student_name} is learning to STORE TEXT in variables using quotes'
            else:
                goal = 'help them PRINT a variable using: print(variable_name)'
                context = f'{student_name} is learning to DISPLAY stored variables using print()'
        
        elif topic == 'input':
            if challenge == 1:
                goal = 'help them ASK for user input and STORE it: name = input("What is your name? ")'
                context = f'{student_name} is learning to use input() to ask questions and store answers in variables'
            elif challenge == 2:
                goal = 'help them JOIN text with a variable using +: print("Hello " + name)'
                context = f'{student_name} is learning to concatenate (join) strings with variables using the + operator'
            else:
                goal = 'help them ask another question with input(): age = input("How old are you? ")'
                context = f'{student_name} is practicing input() to collect different information from the user'
                
        elif topic == 'loops':
            if challenge == 1:
                goal = 'help them write a for loop: for i in range(5):'
                context = f'{student_name} is learning to create for loops'
            else:
                goal = 'help them indent code inside the loop'
                context = f'{student_name} is learning about loop indentation'
        else:
            # Generic
            goal = 'help them with their Python code'
            context = f'{student_name} is learning Python'
        
        system = f'''You are Donki, a friendly female Python coding assistant for high school students.
CURRENT TOPIC: {topic.upper()}
{context}

CRITICAL RULES:
1. Address the student as "{student_name}" in your hint
2. Keep hints SHORT (1-2 sentences max)
3. Be encouraging and friendly with a warm, supportive tone
4. DON'T give the full answer - guide them step by step
5. Point out their specific mistake if you can identify it
6. Stay STRICTLY on topic - ONLY teach about {topic.upper()}, NOT other Python concepts!
7. If they're learning variables, DON'T talk about print() - focus on assignment (=)
8. If they're learning print(), focus on print() syntax, NOT variables

Be like a helpful friend, not a teacher!'''
        
        prompt = f'''TOPIC: {topic.upper()}
Student {student_name} typed: "{code or '(nothing yet)'}"

Their CURRENT goal: {goal}

What mistake did they make? Give {student_name} a friendly, specific hint about {topic.upper()} ONLY.'''
        
        resp = model.generate_content([system, prompt])
        text = getattr(resp, 'text', None)
        
        if not text:
            try:
                candidates = getattr(resp, 'candidates', [])
                if candidates:
                    parts = candidates[0].content.parts
                    if parts:
                        text = getattr(parts[0], 'text', None)
            except Exception:
                text = None
        
        hint_text = text or default_hint
        # Clean up the response
        hint_text = hint_text.strip().strip('"').strip("'")
        
        return jsonify({"hint": hint_text}), 200
        
    except Exception as e:
        print(f"❌ AI Hint error: {e}")
        return jsonify({"hint": default_hint}), 200

# NEW: API endpoint to get current user's name
@app.route('/api/user-info', methods=['GET'])
def get_user_info():
    """Returns the current user's name from session"""
    try:
        user = session.get('user')
        if user and user.get('user_id'):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                # Note: users table uses 'id' column, not 'user_id'
                cursor.execute("SELECT name FROM users WHERE id = ?", (user['user_id'],))
                user_row = cursor.fetchone()
                conn.close()
                if user_row:
                    return jsonify({"name": user_row['name']}), 200
        return jsonify({"name": None}), 200
    except Exception as e:
        print(f"❌ User info error: {e}")
        return jsonify({"name": None}), 200

# NEW: AI-powered personalized dialogue generator
@app.route('/api/dialogue', methods=['POST'])
def ai_dialogue():
    """Generate personalized, context-aware dialogue using Gemini AI"""
    data = request.get_json(silent=True) or {}
    student_name = data.get('student_name', 'Student')
    stage = data.get('stage', 'greeting')  # greeting, string_response, age_question, age_response
    user_input = data.get('user_input', '')
    challenge = data.get('challenge', 1)  # 1 for string, 2 for number
    
    default_responses = {
        'greeting': f'Hello {student_name}! How are you?',
        'string_response': 'I\'m doing well!',
        'age_question': f'That\'s great {student_name}! How old are you?',
        'age_response': 'I\'m 20 years old!',
        'celebration': 'Awesome! You\'ve mastered print()!'
    }
    
    try:
        if not os.getenv('GEMINI_API_KEY'):
            return jsonify({"dialogue": default_responses.get(stage, '...'), "should_continue": True}), 200
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build context-aware prompts
        if stage == 'greeting':
            system_prompt = f"""You are Sam, a friendly character in a Python learning game. 
The student's name is {student_name}. Alex (another character) just greeted you and asked how you are.
Respond naturally as Sam in ONE short sentence (max 8 words). Be friendly and conversational.
Example: "Hello {student_name}! I'm doing great!" or "Hi {student_name}! I'm good, thanks!"
Keep it natural and vary your response."""
            prompt = f"Generate Sam's greeting response to {student_name}"
            
        elif stage == 'string_response':
            system_prompt = f"""You are Sam in a Python learning game. {student_name} just helped you speak by typing: print("{user_input}")
You need to respond naturally to what they made you say. If they said something creative or funny, acknowledge it!
Respond in ONE short sentence (max 10 words). Be enthusiastic and natural.
Examples: 
- If they said "Hi!": "Thanks {student_name}! That worked!"
- If they said something funny: "Haha! That's creative {student_name}!"
Stay on topic of learning Python print()."""
            prompt = f'{student_name} made you say: "{user_input}". Respond naturally as Sam.'
            
        elif stage == 'age_question':
            system_prompt = f"""You are Alex in a Python learning game teaching {student_name} about Python print().
Sam just responded: "{user_input}"
Now ask {student_name} about their age in ONE short, friendly sentence (max 10 words).
Make it natural and conversational. Don't be too formal.
Examples: 
- "Nice! {student_name}, how old are you?"
- "Cool! What's your age {student_name}?"
- "{student_name}, tell me your age!"
Vary your response naturally."""
            prompt = f'Sam said "{user_input}". Now ask {student_name} their age naturally.'
            
        elif stage == 'age_response':
            # Check if user input is a valid number
            try:
                age = int(user_input.strip())
                system_prompt = f"""You are Sam in a Python learning game. {student_name} just taught you to print your age: {age}
Respond enthusiastically in ONE short sentence (max 10 words).
Examples:
- "I'm {age} years old!"
- "Yes! I'm {age}!"
- "{age}! That's my age!"
Be natural and excited."""
                prompt = f"{student_name} helped you print the number {age}. Respond as Sam saying your age."
            except:
                system_prompt = f"""You are Sam. {student_name} typed something but it's not working correctly yet.
Respond confused in ONE short sentence (max 8 words).
Examples: "Hmm, that's not quite right..." or "I'm a bit confused..."
Stay friendly and encouraging."""
                prompt = f"{student_name} is trying to help. Respond confused but friendly."
                
        elif stage == 'celebration':
            system_prompt = f"""You are Alex celebrating {student_name}'s success in learning Python print().
They mastered BOTH printing strings (with quotes) and numbers (without quotes).
Respond enthusiastically in ONE short sentence (max 12 words).
Examples:
- "Awesome {student_name}! You're a Python star!"
- "Fantastic work {student_name}! You've got this!"
- "Amazing {student_name}! You mastered print()!"
Be very encouraging and celebratory."""
            prompt = f"Celebrate {student_name}'s success in mastering Python print()"
        else:
            return jsonify({"dialogue": default_responses.get(stage, '...'), "should_continue": True}), 200
        
        # Generate AI response
        resp = model.generate_content([system_prompt, prompt])
        text = getattr(resp, 'text', None)
        
        if not text:
            try:
                candidates = getattr(resp, 'candidates', [])
                if candidates:
                    parts = candidates[0].content.parts
                    if parts:
                        text = getattr(parts[0], 'text', None)
            except Exception:
                text = None
        
        dialogue_text = text or default_responses.get(stage, '...')
        
        # Clean up the response (remove quotes if AI added them)
        dialogue_text = dialogue_text.strip().strip('"').strip("'")
        
        return jsonify({
            "dialogue": dialogue_text,
            "should_continue": True
        }), 200
        
    except Exception as e:
        print(f"❌ Dialogue generation error: {e}")
        return jsonify({
            "dialogue": default_responses.get(stage, '...'),
            "should_continue": True
        }), 200

# Simple helpers to simulate login for server-side pages
def set_user_session_from_token(token):
    try:
        identity = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        session['user'] = {
            'user_id': identity.get('user_id'),
            'role': identity.get('role')
        }
        return True
    except Exception:
        return False

# --- Database Helper Function ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        db_path = os.getenv("DATABASE_PATH", "codedonki.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        # Enable foreign keys in SQLite
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

# --- NEW: Slug Helper Function ---
def create_slug(title):
    """Generates a URL-friendly slug from a title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[\s_]+', '-', slug)      # Replace spaces with hyphens
    slug = slug.strip('-')
    return slug

# --- Startup Test Function ---
def test_db_connection():
    """Tests the database connection on startup."""
    conn = get_db_connection()
    if conn:
        print("[SUCCESS] Database connection successful!")
        conn.close()

def setup_database():
    """Setup database tables and sample data."""
    conn = get_db_connection()
    if not conn:
        print("❌ Cannot setup database - connection failed")
        return False
    
    try:
        cursor = conn.cursor()
        # If core tables already exist, assume DB is initialized and skip seeding
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users','categories','lessons') LIMIT 1")
        if cursor.fetchone():
            cursor.close()
            conn.close()
            print("[INFO] Database already initialized; skipping setup script.")
            return True
        
        # Disable foreign keys temporarily for initial setup
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Read and execute the SQLite database schema
        with open('database_schema_sqlite.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Execute the entire script
        cursor.executescript(sql_script)
        
        # Re-enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[SUCCESS] Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database setup failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

# --- Auth Decorator Functions ---
def get_jwt_identity():
    """Helper to get identity from JWT in the 'Authorization' header."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, "Missing Authorization header"
    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return None, "Invalid Authorization header format"
    token = parts[1]
    try:
        identity = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        return identity, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"

def admin_required(f):
    """Decorator to protect routes that require 'admin' role."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        identity, error = get_jwt_identity()
        if not identity: return jsonify({"error": error}), 401
        if identity.get('role') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    """Decorator to protect routes that require any logged-in user."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        identity, error = get_jwt_identity()
        if not identity: return jsonify({"error": error}), 401
        request.current_user = identity 
        return f(*args, **kwargs)
    return decorated_function

# --- Auth Routes ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not name or not email or not password:
        return jsonify({"error": "Missing name, email, or password"}), 400
    hashed_password = pbkdf2_sha256.hash(password)
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, hashed_password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if 'UNIQUE constraint failed' in str(e): 
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, hashed_password, role FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if not user: return jsonify({"error": "Invalid credentials"}), 401
        user_id = user['id']
        user_name = user['name']
        user_email = user['email']
        user_hash = user['hashed_password']
        user_role = user['role']
        if pbkdf2_sha256.verify(password, user_hash):
            token = jwt.encode({
                'user_id': user_id, 'role': user_role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config["JWT_SECRET_KEY"], algorithm="HS256")
            return jsonify({"message": "Login successful", "token": token, "name": user_name, "email": user_email, "role": user_role}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Handles forgot password requests."""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    conn = get_db_connection()
    if not conn: 
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        # Check if user exists
        cursor.execute("SELECT id, name FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            # For security, don't reveal if email exists or not
            return jsonify({"message": "If the email exists, a reset link has been sent"}), 200
        
        user_id, user_name = user
        
        # Generate a reset token (expires in 1 hour)
        reset_token = jwt.encode({
            'user_id': user_id,
            'type': 'password_reset',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config["JWT_SECRET_KEY"], algorithm="HS256")
        
        # In a real application, you would send an email here
        # For now, we'll just return success
        print(f"Password reset token for {email}: {reset_token}")
        
        return jsonify({
            "message": "If the email exists, a reset link has been sent",
            "reset_token": reset_token  # Only for development - remove in production
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# --- Protected Routes ---
@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """Gets the profile information of the currently logged-in user."""
    user_id = request.current_user['user_id']
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        # --- THIS QUERY IS UPDATED ---
        cursor.execute("SELECT name, email, role, xp, avatar_url FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get avatar_url
        avatar_url = user['avatar_url']
        # If no avatar is set, use the default profile picture
        if not avatar_url:
            avatar_url = "/uploads/profile.png"
        
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
        if conn: conn.close()

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    """Updates the user's name."""
    user_id = request.current_user['user_id']
    data = request.get_json()
    new_name = data.get('name')

    if not new_name:
        return jsonify({"error": "Name is required"}), 400

    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET name = ? WHERE id = ?",
            (new_name, user_id)
        )
        conn.commit()
        return jsonify({"message": "Profile updated successfully", "name": new_name}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Uploads a new profile picture for the user."""
    user_id = request.current_user['user_id']
    
    if 'avatar' not in request.files:
        return jsonify({"error": "No avatar file provided"}), 400
        
    file = request.files['avatar']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Create a unique filename to avoid conflicts
        # e.g., "avatar_1_timestamp.jpg"
        ext = os.path.splitext(file.filename)[1]
        filename = secure_filename(f"avatar_{user_id}_{int(datetime.datetime.now().timestamp())}{ext}")
        
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        # This is the public URL we will store in the DB
        avatar_url = f"/uploads/{filename}" 

        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        try:
            cursor = conn.cursor()
            # Update the user's avatar_url in the database
            cursor.execute(
                "UPDATE users SET avatar_url = ? WHERE id = ?",
                (avatar_url, user_id)
            )
            conn.commit()
            return jsonify({"message": "Avatar updated successfully", "avatar_url": avatar_url}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn: conn.close()
            
    return jsonify({"error": "File upload failed"}), 500

@app.route('/api/profile/password', methods=['PUT'])
@login_required
def change_password():
    """Change user password."""
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
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Get current password hash (column is 'hashed_password' in schema)
        cursor.execute("SELECT hashed_password FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify current password using pbkdf2_sha256 (matches signup/login)
        if not pbkdf2_sha256.verify(current_password, user['hashed_password']):
            return jsonify({"error": "Current password is incorrect"}), 400
        
        # Hash new password using pbkdf2_sha256 (consistent with signup)
        new_password_hash = pbkdf2_sha256.hash(new_password)
        
        # Update password
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (new_password_hash, user_id)
        )
        conn.commit()
        
        return jsonify({"message": "Password changed successfully"}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, color, icon, slug, meta_description, created_at FROM categories ORDER BY name")
        categories = []
        for cat in cursor.fetchall():
            categories.append({
                "id": cat['id'], 
                "name": cat['name'],
                "description": cat['description'],
                "color": cat['color'],
                "icon": cat['icon'],
                "slug": cat['slug'],
                "meta_description": cat['meta_description'],
                "created_at": cat['created_at'] if cat['created_at'] else None
            })
        return jsonify(categories), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/lessons', methods=['GET'])
@login_required
def get_lessons():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT l.id, l.title, l.description, c.name as category_name, l.xp_min, l.xp_max, l.ar_model_url, l.category_id, l.order_in_category, l.pass_threshold, l.slug
            FROM lessons l
            LEFT JOIN categories c ON l.category_id = c.id
            ORDER BY l.category_id, l.order_in_category
            """
        )
        lessons_list = [
            {
                "id": row['id'], 
                "title": row['title'], 
                "description": row['description'], 
                "category": row['category_name'] if row['category_name'] else 'General', 
                "category_id": row['category_id'],
                "xp_min": row['xp_min'], 
                "xp_max": row['xp_max'],
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
        if conn: conn.close()

# --- Your New Endpoints (ID and Slug) ---
def get_lesson_by_field(field, value):
    """Helper function to fetch a lesson by ID or Slug."""
    sql_query = """
        SELECT title, description, ar_model_url, xp_min, xp_max, id, slug
        FROM lessons WHERE 
    """
    if field == 'id':
        sql_query += "id = ?"
    elif field == 'slug':
        sql_query += "slug = ?"
    else:
        return None

    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query, (value,))
        lesson = cursor.fetchone()
        if not lesson: return None
        return {
            "title": lesson['title'], 
            "description": lesson['description'],
            "ar_model_url": lesson['ar_model_url'], 
            "xp_min": lesson['xp_min'], 
            "xp_max": lesson['xp_max'],
            "id": lesson['id'], 
            "slug": lesson['slug']
        }
    except Exception as e:
        print(f"❌ ERROR in get_lesson_by_field: {e}")
        return None
    finally:
        if conn: conn.close()

@app.route('/api/lessons/<int:lesson_id>', methods=['GET'])
@login_required
def get_lesson_by_id_route(lesson_id):
    lesson = get_lesson_by_field('id', lesson_id)
    if not lesson: return jsonify({"error": "Lesson not found"}), 404
    return jsonify(lesson), 200

@app.route('/api/lessons/slug/<lesson_slug>', methods=['GET'])
@login_required
def get_lesson_by_slug_route(lesson_slug):
    lesson = get_lesson_by_field('slug', lesson_slug)
    if not lesson: return jsonify({"error": "Lesson not found"}), 404
    return jsonify(lesson), 200

# --- Admin-Only Routes ---
@app.route('/api/admin/lessons', methods=['POST'])
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
    
    # Handle AR model/code upload
    model_url = None
    if ar_code:
        # Save AR code as HTML file
        filename = f"lesson_{int(time.time())}.html"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(ar_code)
        model_url = f"/uploads/{filename}"
    elif 'ar_model' in request.files and request.files['ar_model'].filename:
        file = request.files['ar_model']
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        model_url = f"/uploads/{filename}"
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        # Generate slug from title
        lesson_slug = create_slug(title)
        
        cursor.execute(
            """
            INSERT INTO lessons (title, description, category_id, xp_min, xp_max, 
                               order_in_category, pass_threshold, ar_model_url, slug)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, category_id, xp_min, xp_max, order_in_category, pass_threshold, model_url, lesson_slug)
        )
        lesson_id = cursor.lastrowid
        conn.commit()
        return jsonify({"message": "Lesson created successfully", "lesson_id": lesson_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/lessons/<int:lesson_id>', methods=['GET'])
@admin_required
def get_lesson_details(lesson_id):
    """Get detailed information about a specific lesson."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT l.*, c.name as category_name
            FROM lessons l
            LEFT JOIN categories c ON l.category_id = c.id
            WHERE l.id = ?
            """, (lesson_id,)
        )
        lesson = cursor.fetchone()
        
        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404
        
        # Handle the case where created_at and updated_at might not exist
        lesson_dict = {
            'id': lesson[0],
            'title': lesson[1],
            'description': lesson[2],
            'category_id': lesson[3],
            'category': lesson[11] if len(lesson) > 11 else None,  # category_name from JOIN
            'ar_model_url': lesson[4],
            'xp_min': lesson[6],  # Fixed index - xp_min is at index 6
            'xp_max': lesson[7],  # Fixed index - xp_max is at index 7
            'order_in_category': lesson[8],  # Fixed index - order_in_category is at index 8
            'pass_threshold': lesson[9],  # Fixed index - pass_threshold is at index 9
            'is_locked_by_default': lesson[10]  # Fixed index - is_locked_by_default is at index 10
        }
        
        # Add created_at and updated_at if they exist (these columns don't exist in current schema)
        # if len(lesson) > 12:
        #     lesson_dict['created_at'] = lesson[12].isoformat() if lesson[12] else None
        # if len(lesson) > 13:
        #     lesson_dict['updated_at'] = lesson[13].isoformat() if lesson[13] else None
        
        return jsonify(lesson_dict), 200
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/lessons/<int:lesson_id>', methods=['PUT'])
@admin_required
def update_lesson(lesson_id):
    """Update an existing lesson."""
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    category_id = data.get('category_id')
    xp_min = data.get('xp_min')
    xp_max = data.get('xp_max')
    order_in_category = data.get('order_in_category')
    pass_threshold = data.get('pass_threshold')
    ar_code = data.get('ar_code')
    
    # Title is only required if we're updating other fields (not just AR code)
    if not title and not ar_code:
        return jsonify({"error": "Title is required"}), 400
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Handle AR code update
        model_url = None
        if ar_code:
            # Save AR code as HTML file
            filename = f"lesson_{lesson_id}_{int(time.time())}.html"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(ar_code)
            model_url = f"/uploads/{filename}"
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        if title: 
            update_fields.append("title = ?")
            update_values.append(title)
            # Update slug when title changes
            update_fields.append("slug = ?")
            update_values.append(create_slug(title))
        if description is not None: 
            update_fields.append("description = ?")
            update_values.append(description)
        if category_id: 
            update_fields.append("category_id = ?")
            update_values.append(category_id)
        if xp_min is not None: 
            update_fields.append("xp_min = ?")
            update_values.append(xp_min)
        if xp_max is not None: 
            update_fields.append("xp_max = ?")
            update_values.append(xp_max)
        if order_in_category: 
            update_fields.append("order_in_category = ?")
            update_values.append(order_in_category)
        if pass_threshold is not None: 
            update_fields.append("pass_threshold = ?")
            update_values.append(pass_threshold)
        if model_url: 
            update_fields.append("ar_model_url = ?")
            update_values.append(model_url)
        
        # Don't try to update updated_at if column doesn't exist
        # update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        update_values.append(lesson_id)
        
        query = f"UPDATE lessons SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Lesson not found"}), 404
        
        conn.commit()
        return jsonify({"message": "Lesson updated successfully"}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/lessons/<int:lesson_id>', methods=['DELETE'])
@admin_required
def delete_lesson(lesson_id):
    """Delete a lesson and automatically reorder remaining lessons in the category."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Get lesson details before deletion
        cursor.execute("SELECT category_id, order_in_category FROM lessons WHERE id = ?", (lesson_id,))
        lesson_data = cursor.fetchone()
        
        if not lesson_data:
            return jsonify({"error": "Lesson not found"}), 404
        
        category_id, deleted_order = lesson_data
        
        # Delete the lesson
        cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Lesson not found"}), 404
        
        # Reorder remaining lessons in the same category
        cursor.execute(
            """
            UPDATE lessons 
            SET order_in_category = order_in_category - 1
            WHERE category_id = ? AND order_in_category > ?
            """, (category_id, deleted_order)
        )
        
        conn.commit()
        return jsonify({"message": "Lesson deleted successfully and remaining lessons reordered"}), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/lessons/next-level', methods=['GET'])
@admin_required
def get_next_level():
    """Get the next available level for a category."""
    category_id = request.args.get('category_id')
    
    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(MAX(order_in_category), 0) + 1 FROM lessons WHERE category_id = ?",
            (category_id,)
        )
        next_level = cursor.fetchone()[0]
        
        return jsonify({"next_level": next_level}), 200
        
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# --- File Serving Route ---
@app.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    """Serves files from the 'uploads' directory, including subdirectories."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- NEW: Gamification & AI Routes (Phase 7) ---

@app.route('/api/lessons/complete', methods=['POST'])
@login_required
def complete_lesson():
    """Marks a lesson as complete for a user and awards XP."""
    user_id = request.current_user['user_id']
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    xp_to_award = data.get('xp', 20) # Get XP from request, default to 20

    if not lesson_id:
        return jsonify({"error": "Missing lesson_id"}), 400

    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # 1. Check if lesson is already completed
        cursor.execute(
            "SELECT * FROM completed_lessons WHERE user_id = ? AND lesson_id = ?",
            (user_id, lesson_id)
        )
        if cursor.fetchone():
            return jsonify({"message": "Lesson already completed"}), 200

        # 2. Add to completed_lessons
        cursor.execute(
            "INSERT INTO completed_lessons (user_id, lesson_id) VALUES (?, ?)",
            (user_id, lesson_id)
        )
        
        # 3. Update user's XP
        cursor.execute(
            "UPDATE users SET xp = xp + ? WHERE id = ?",
            (xp_to_award, user_id)
        )
        # Get the updated XP value
        cursor.execute("SELECT xp FROM users WHERE id = ?", (user_id,))
        new_xp = cursor.fetchone()['xp']
        
        conn.commit()
        return jsonify({"message": "Lesson completed!", "new_xp": new_xp}), 201
        
    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR in complete_lesson: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/leaderboard', methods=['GET'])
@login_required
def get_leaderboard():
    """Fetches top 50 users by XP."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, xp, avatar_url FROM users ORDER BY xp DESC LIMIT 50")
        leaderboard = []
        for row in cursor.fetchall():
            avatar_url = row['avatar_url']
            # Use default profile picture if no avatar is set
            if not avatar_url:
                avatar_url = "/uploads/profile.png"
            leaderboard.append({
                "name": row['name'], 
                "xp": row['xp'],
                "avatar_url": avatar_url
            })
        return jsonify(leaderboard), 200
    except Exception as e:
        print(f"❌ ERROR in get_leaderboard: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/ai-suggestion', methods=['POST'])
@login_required
def get_ai_suggestion():
    """Gets a simple learning tip from Gemini based on a lesson title."""
    data = request.get_json()
    lesson_title = data.get('title')
    
    if not lesson_title:
        return jsonify({"error": "Missing lesson title"}), 400
        
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        I am a student learning programming on a gamified AR/VR platform called Codedonki.
        I just finished a lesson called "{lesson_title}".
        Give me one short, helpful tip (about 1-2 sentences) related to this topic
        to help me remember it. Start the tip directly, e.g., "Remember that..."
        or "A great way to practice...". Do not use markdown.
        """
        response = model.generate_content(prompt)
        return jsonify({"suggestion": response.text}), 200
    except Exception as e:
        print(f"❌ ERROR in get_ai_suggestion: {e}")
        # Provide a fallback tip if the API fails
        return jsonify({"suggestion": "Great job on finishing the lesson! Make sure to practice what you've learned."}), 200


# --- NEW: Enhanced Admin APIs ---

@app.route('/api/lessons/unlocked', methods=['GET'])
@login_required
def get_unlocked_lessons():
    """Get lessons that are unlocked for the current user."""
    user_id = request.current_user['user_id']
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
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
                "id": row['id'], 
                "title": row['title'], 
                "description": row['description'],
                "category": row['category_name'], 
                "xp_min": row['xp_min'], 
                "xp_max": row['xp_max'],
                "ar_model_url": row['ar_model_url'], 
                "order_in_category": row['order_in_category'],
                "is_completed": row['is_completed'], 
                "is_unlocked": row['is_unlocked'],
                "slug": row['slug'] if row['slug'] else create_slug(row['title'])
            })
        return jsonify(lessons), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# --- New: All lessons with per-user status (locked + unlocked) ---
@app.route('/api/lessons/all-status', methods=['GET'])
@login_required
def get_all_lessons_with_status():
    """Get all lessons for the current user with unlocked/completed flags.
    Defaults: first lesson in a category is unlocked if no explicit record exists.
    """
    user_id = request.current_user['user_id']
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
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
            LEFT JOIN lesson_progress lp ON l.id = lp.lesson_id AND lp.user_id = ?
            ORDER BY c.name, l.order_in_category
            """,
            (user_id,)
        )
        lessons = []
        for row in cursor.fetchall():
            lessons.append({
                "id": row['id'], 
                "title": row['title'], 
                "description": row['description'],
                "category": row['category_name'], 
                "xp_min": row['xp_min'], 
                "xp_max": row['xp_max'],
                "ar_model_url": row['ar_model_url'], 
                "category_id": row['category_id'],
                "order_in_category": row['order_in_category'],
                "is_completed": row['is_completed'], 
                "is_unlocked": row['is_unlocked'],
                "slug": row['slug'] if row['slug'] else create_slug(row['title'])
            })
        return jsonify(lessons), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# --- Quiz Management APIs ---
@app.route('/api/admin/quiz', methods=['GET', 'POST'])
@admin_required
def manage_quiz_questions():
    """Get all quiz questions or create a new quiz question."""
    
    # GET: Return all quiz questions
    if request.method == 'GET':
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, lesson_id, question_text, option_a, option_b, option_c, 
                       option_d, correct_answer, explanation 
                FROM quiz_questions 
                ORDER BY lesson_id, id
                """
            )
            questions = []
            for row in cursor.fetchall():
                questions.append({
                    "id": row['id'],
                    "lesson_id": row['lesson_id'],
                    "question_text": row['question_text'],
                    "option_a": row['option_a'],
                    "option_b": row['option_b'],
                    "option_c": row['option_c'],
                    "option_d": row['option_d'],
                    "correct_answer": row['correct_answer'],
                    "explanation": row['explanation']
                })
            return jsonify(questions), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        finally:
            if conn: conn.close()
    
    # POST: Create a new quiz question
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
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_questions (lesson_id, question_text, option_a, option_b, 
                                      option_c, option_d, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (lesson_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
        )
        question_id = cursor.lastrowid
        conn.commit()
        return jsonify({"message": "Quiz question created successfully", "question_id": question_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/quiz/<int:question_id>', methods=['PUT'])
@admin_required
def update_quiz_question(question_id):
    """Update an existing quiz question."""
    data = request.get_json()
    question_text = data.get('question_text')
    option_a = data.get('option_a')
    option_b = data.get('option_b')
    option_c = data.get('option_c')
    option_d = data.get('option_d')
    correct_answer = data.get('correct_answer')
    explanation = data.get('explanation', '')
    
    if correct_answer and correct_answer not in ['A', 'B', 'C', 'D']:
        return jsonify({"error": "Correct answer must be A, B, C, or D"}), 400
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        update_fields = []
        update_values = []
        
        if question_text:
            update_fields.append("question_text = %s")
            update_values.append(question_text)
        if option_a:
            update_fields.append("option_a = %s")
            update_values.append(option_a)
        if option_b:
            update_fields.append("option_b = %s")
            update_values.append(option_b)
        if option_c:
            update_fields.append("option_c = %s")
            update_values.append(option_c)
        if option_d:
            update_fields.append("option_d = %s")
            update_values.append(option_d)
        if correct_answer:
            update_fields.append("correct_answer = %s")
            update_values.append(correct_answer)
        if explanation is not None:
            update_fields.append("explanation = %s")
            update_values.append(explanation)
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400
        
        update_values.append(question_id)
        cursor.execute(
            f"UPDATE quiz_questions SET {', '.join(update_fields)} WHERE id = %s",
            update_values
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Quiz question not found"}), 404
        conn.commit()
        return jsonify({"message": "Quiz question updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/quiz/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_quiz_question(question_id):
    """Delete a quiz question."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quiz_questions WHERE id = ?", (question_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Quiz question not found"}), 404
        conn.commit()
        return jsonify({"message": "Quiz question deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/lessons/<int:lesson_id>/quiz', methods=['GET'])
@admin_required
def get_lesson_quiz_questions(lesson_id):
    """Get all quiz questions for a specific lesson."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation FROM quiz_questions WHERE lesson_id = ? ORDER BY id",
            (lesson_id,)
        )
        questions = []
        for row in cursor.fetchall():
            questions.append({
                "id": row['id'], 
                "question_text": row['question_text'], 
                "option_a": row['option_a'],
                "option_b": row['option_b'], 
                "option_c": row['option_c'], 
                "option_d": row['option_d'],
                "correct_answer": row['correct_answer'], 
                "explanation": row['explanation']
            })
        return jsonify(questions), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/quiz/<int:lesson_id>', methods=['GET'])
@login_required
def get_quiz_for_user(lesson_id):
    """Get quiz questions for a user (without correct answers)."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, question_text, option_a, option_b, option_c, option_d FROM quiz_questions WHERE lesson_id = ? ORDER BY id",
            (lesson_id,)
        )
        questions = []
        for row in cursor.fetchall():
            questions.append({
                "id": row['id'], 
                "question_text": row['question_text'], 
                "option_a": row['option_a'],
                "option_b": row['option_b'], 
                "option_c": row['option_c'], 
                "option_d": row['option_d']
            })
        return jsonify(questions), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/quiz/submit', methods=['POST'])
@login_required
def submit_quiz():
    """Submit quiz answers and calculate score with time-based XP bonus."""
    user_id = request.current_user['user_id']
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    answers = data.get('answers')  # Should be {question_id: 'A', question_id: 'B', ...}
    time_taken = data.get('time_taken', 0)  # Time in seconds
    
    if not lesson_id or not answers:
        return jsonify({"error": "Missing lesson_id or answers"}), 400
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Get all questions for this lesson with correct answers
        cursor.execute(
            "SELECT id, correct_answer FROM quiz_questions WHERE lesson_id = ?",
            (lesson_id,)
        )
        questions = cursor.fetchall()
        
        if not questions:
            return jsonify({"error": "No quiz questions found for this lesson"}), 404
        
        # Calculate score
        correct_count = 0
        total_questions = len(questions)
        
        for question_id, correct_answer in questions:
            user_answer = answers.get(str(question_id))
            if user_answer == correct_answer:
                correct_count += 1
        
        score = int((correct_count / total_questions) * 100)
        
        # Get lesson details for pass threshold, XP range, category and order
        cursor.execute(
            "SELECT pass_threshold, xp_min, xp_max, category_id, order_in_category FROM lessons WHERE id = ?",
            (lesson_id,)
        )
        lesson_details = cursor.fetchone()
        if not lesson_details:
            return jsonify({"error": "Lesson not found"}), 404
        
        pass_threshold, xp_min, xp_max, category_id, order_in_category = lesson_details
        passed = score >= pass_threshold
        
        # Calculate XP to award with time-based bonus if passed
        import random
        base_xp = random.randint(xp_min, xp_max) if passed else 0
        time_bonus = 0
        
        if passed and time_taken > 0:
            # Time-based bonus calculation
            # Formula: Faster completion = more bonus XP
            # Expected time: 30 seconds per question as baseline
            expected_time = total_questions * 30
            
            if time_taken < expected_time:
                # Fast completion: Award bonus
                time_saved = expected_time - time_taken
                # Bonus: up to 50% of base XP for very fast completion
                max_bonus = base_xp * 0.5
                time_bonus = int(max_bonus * (time_saved / expected_time))
                # Cap bonus at max_bonus
                time_bonus = min(time_bonus, int(max_bonus))
            elif time_taken > expected_time * 2:
                # Very slow completion: Apply penalty (reduce XP)
                time_penalty = int(base_xp * 0.2)  # Max 20% penalty
                time_bonus = -time_penalty
        
        xp_awarded = max(base_xp + time_bonus, 0)  # Ensure XP never goes negative
        
        # Store quiz attempt
        cursor.execute(
            """
            INSERT INTO user_quiz_attempts (user_id, lesson_id, quiz_questions, user_answers, score, passed, xp_awarded)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, lesson_id, str(questions), str(answers), score, passed, xp_awarded)
        )
        
        # If passed, update user XP and lesson progress
        if passed:
            # Update user XP
            cursor.execute(
                "UPDATE users SET xp = xp + ? WHERE id = ?",
                (xp_awarded, user_id)
            )
            # Get the updated XP value
            cursor.execute("SELECT xp FROM users WHERE id = ?", (user_id,))
            new_total_xp = cursor.fetchone()['xp']
            
            # Update lesson progress - SQLite uses INSERT OR REPLACE
            cursor.execute(
                """
                INSERT OR REPLACE INTO lesson_progress (user_id, lesson_id, is_completed, is_unlocked, xp_earned, completed_at)
                VALUES (?, ?, 1, 1, ?, CURRENT_TIMESTAMP)
                """, (user_id, lesson_id, xp_awarded)
            )
            
            # Check for new badges
            cursor.execute(
                """
                SELECT b.id, b.name, b.description, b.icon_url 
                FROM badges b 
                WHERE b.xp_threshold <= ? 
                AND b.id NOT IN (
                    SELECT ub.badge_id FROM user_badges ub WHERE ub.user_id = ?
                )
                AND b.is_active = 1
                """, (new_total_xp, user_id)
            )
            new_badges = cursor.fetchall()
            
            # Award new badges
            for badge_id, badge_name, badge_description, badge_icon in new_badges:
                cursor.execute(
                    "INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)",
                    (user_id, badge_id)
                )
            
            # Unlock next lesson in same category when passed
            cursor.execute(
                """
                SELECT id FROM lessons
                WHERE category_id = ? AND order_in_category = ? + 1
                LIMIT 1
                """,
                (category_id, order_in_category)
            )
            next_row = cursor.fetchone()
            if next_row:
                next_lesson_id = next_row[0]
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO lesson_progress (user_id, lesson_id, is_unlocked)
                    VALUES (?, ?, 1)
                    """,
                    (user_id, next_lesson_id)
                )

            conn.commit()

            return jsonify({
                "message": "Quiz submitted successfully",
                "score": score,
                "passed": passed,
                "xp_awarded": xp_awarded,
                "base_xp": base_xp,
                "time_bonus": time_bonus,
                "new_total_xp": new_total_xp,
                "new_badges": [{"id": b[0], "name": b[1], "description": b[2], "icon_url": b[3]} for b in new_badges]
            }), 200
        else:
            conn.commit()
            return jsonify({
                "message": "Quiz submitted successfully",
                "score": score,
                "passed": passed,
                "xp_awarded": 0,
                "retry_message": "You need to score at least 70% to pass. You can retry the quiz."
            }), 200
            
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# --- Category Management APIs ---
@app.route('/api/admin/categories', methods=['POST'])
@admin_required
def create_category():
    """Create a new category."""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    color = data.get('color', '#3498db')
    icon = data.get('icon', 'fas fa-tag')
    slug = data.get('slug', '')
    meta_description = data.get('meta_description', '')
    
    if not name:
        return jsonify({"error": "Category name is required"}), 400
    
    # Generate slug from name if not provided
    if not slug:
        slug = create_slug(name)
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categories (name, description, color, icon, slug, meta_description) VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, color, icon, slug, meta_description)
        )
        category_id = cursor.lastrowid
        conn.commit()
        return jsonify({"message": "Category created successfully", "category_id": category_id}), 201
    except sqlite3.Error as e:
        conn.rollback()
        if 'UNIQUE constraint failed' in str(e):  # Unique violation
            return jsonify({"error": "Category name or slug already exists"}), 409
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """Update an existing category."""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    color = data.get('color')
    icon = data.get('icon')
    slug = data.get('slug')
    meta_description = data.get('meta_description')
    
    if not name:
        return jsonify({"error": "Category name is required"}), 400
    
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        if name:
            update_fields.append("name = ?")
            update_values.append(name)
        if description is not None:
            update_fields.append("description = ?")
            update_values.append(description)
        if color:
            update_fields.append("color = ?")
            update_values.append(color)
        if icon:
            update_fields.append("icon = ?")
            update_values.append(icon)
        if slug:
            update_fields.append("slug = ?")
            update_values.append(slug)
        if meta_description is not None:
            update_fields.append("meta_description = ?")
            update_values.append(meta_description)
        
        update_values.append(category_id)
        
        query = f"UPDATE categories SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Category not found"}), 404
        conn.commit()
        return jsonify({"message": "Category updated successfully"}), 200
    except sqlite3.Error as e:
        conn.rollback()
        if 'UNIQUE constraint failed' in str(e):  # Unique violation
            return jsonify({"error": "Category name or slug already exists"}), 409
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """Delete a category."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Category not found"}), 404
        conn.commit()
        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# --- Badge System APIs ---
@app.route('/api/admin/badges', methods=['POST'])
@admin_required
def create_badge():
    """Create a new badge with optional icon image upload."""
    try:
        # Get form data - ensure we extract strings, not dict objects
        name = str(request.form.get('name', ''))
        description = str(request.form.get('description', ''))
        xp_threshold = request.form.get('xp_threshold')
        color = str(request.form.get('color', '#FFD700'))
        
        if not name or not xp_threshold:
            return jsonify({"error": "Badge name and XP threshold are required"}), 400
        
        # Convert xp_threshold to integer
        try:
            xp_threshold = int(xp_threshold)
        except (ValueError, TypeError):
            return jsonify({"error": "XP threshold must be a number"}), 400
        
        # Handle badge icon upload - save in uploads/badges/
        icon_url = ''
        if 'badge_icon' in request.files and request.files['badge_icon'].filename:
            file = request.files['badge_icon']
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"badge_{name.replace(' ', '_')}_{int(time.time())}{ext}")
            
            # Create badges folder if it doesn't exist
            badges_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'badges')
            os.makedirs(badges_folder, exist_ok=True)
            
            save_path = os.path.join(badges_folder, filename)
            file.save(save_path)
            icon_url = f"/uploads/badges/{filename}"
            print(f"✅ Badge icon saved: {icon_url}")
        
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO badges (name, description, icon_url, xp_threshold, color) VALUES (?, ?, ?, ?, ?)",
                (name, description, icon_url, xp_threshold, color)
            )
            badge_id = cursor.lastrowid
            conn.commit()
            print(f"✅ Badge created: {name} (ID: {badge_id})")
            return jsonify({"message": "Badge created successfully", "badge_id": badge_id}), 201
        except sqlite3.Error as e:
            conn.rollback()
            print(f"❌ Database error in create_badge: {str(e)}")
            if 'UNIQUE constraint failed' in str(e):
                return jsonify({"error": "Badge name already exists"}), 409
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn: conn.close()
    except Exception as e:
        print(f"❌ Error in create_badge: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/admin/badges/<int:badge_id>', methods=['PUT'])
@admin_required
def update_badge(badge_id):
    """Update an existing badge with optional icon image upload."""
    try:
        # Get form data - ensure we extract strings, not dict objects
        name = request.form.get('name')
        if name is not None:
            name = str(name)
        
        description = request.form.get('description')
        if description is not None:
            description = str(description)
        
        xp_threshold = request.form.get('xp_threshold')
        if xp_threshold is not None:
            try:
                xp_threshold = int(xp_threshold)
            except (ValueError, TypeError):
                return jsonify({"error": "XP threshold must be a number"}), 400
        
        color = request.form.get('color')
        if color is not None:
            color = str(color)
        
        is_active_str = request.form.get('is_active')
        # Convert to integer for SQLite (0 or 1)
        is_active = None
        if is_active_str is not None:
            is_active_str = str(is_active_str)
            is_active = 1 if is_active_str.lower() in ['true', '1', 'yes'] else 0
        
        existing_icon_url = request.form.get('existing_icon_url')
        if existing_icon_url is not None:
            existing_icon_url = str(existing_icon_url)
        
        # Handle badge icon upload - save in uploads/badges/
        icon_url = existing_icon_url  # Keep existing by default
        if 'badge_icon' in request.files and request.files['badge_icon'].filename:
            file = request.files['badge_icon']
            ext = os.path.splitext(file.filename)[1]
            # Use name if available, otherwise use badge_id
            badge_name = name if name else f"badge_{badge_id}"
            filename = secure_filename(f"badge_{badge_name.replace(' ', '_')}_{int(time.time())}{ext}")
            
            # Create badges folder if it doesn't exist
            badges_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'badges')
            os.makedirs(badges_folder, exist_ok=True)
            
            save_path = os.path.join(badges_folder, filename)
            file.save(save_path)
            icon_url = f"/uploads/badges/{filename}"
            print(f"✅ Badge icon updated: {icon_url}")
        
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        update_fields = []
        update_values = []
        
        if name:
            update_fields.append("name = ?")
            update_values.append(name)
        if description is not None:
            update_fields.append("description = ?")
            update_values.append(description)
        if icon_url is not None:
            update_fields.append("icon_url = ?")
            update_values.append(icon_url)
        if xp_threshold is not None:
            update_fields.append("xp_threshold = ?")
            update_values.append(xp_threshold)
        if color:
            update_fields.append("color = ?")
            update_values.append(color)
        if is_active is not None:
            update_fields.append("is_active = ?")
            update_values.append(is_active)
        
        if not update_fields:
            if conn: conn.close()
            return jsonify({"error": "No fields to update"}), 400
        
        update_values.append(badge_id)
        cursor.execute(
            f"UPDATE badges SET {', '.join(update_fields)} WHERE id = ?",
            update_values
        )
        if cursor.rowcount == 0:
            if conn: conn.close()
            return jsonify({"error": "Badge not found"}), 404
        conn.commit()
        conn.close()
        print(f"✅ Badge updated: ID {badge_id}")
        return jsonify({"message": "Badge updated successfully"}), 200
        
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"❌ Database error in update_badge: {str(e)}")
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({"error": "Badge name already exists"}), 409
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"❌ Error in update_badge: {str(e)}")
        print(f"   Name: {name}, Description: {description}, XP: {xp_threshold}, Color: {color}, Is Active: {is_active}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/admin/badges/<int:badge_id>', methods=['DELETE'])
@admin_required
def delete_badge(badge_id):
    """Delete a badge."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM badges WHERE id = ?", (badge_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Badge not found"}), 404
        conn.commit()
        return jsonify({"message": "Badge deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/badges', methods=['GET'])
@login_required
def get_all_badges():
    """Get all badges (active only for regular users, all for admins)."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        # Check if user is admin
        identity, error_msg = get_jwt_identity()
        is_admin = False
        if identity:
            # Get role directly from JWT identity instead of querying database
            is_admin = identity.get('role') == 'admin'
        
        cursor = conn.cursor()
        # Show all badges for admins, only active badges for regular users
        if is_admin:
            cursor.execute("SELECT id, name, description, icon_url, xp_threshold, color, is_active FROM badges ORDER BY xp_threshold")
        else:
            cursor.execute("SELECT id, name, description, icon_url, xp_threshold, color, is_active FROM badges WHERE is_active = 1 ORDER BY xp_threshold")
        
        badges = []
        for row in cursor.fetchall():
            badge_data = {
                "id": row['id'], 
                "name": row['name'], 
                "description": row['description'],
                "icon_url": row['icon_url'], 
                "xp_threshold": row['xp_threshold'], 
                "color": row['color']
            }
            if is_admin:
                badge_data['is_active'] = bool(row['is_active'])
            badges.append(badge_data)
        
        print(f"✅ Loaded {len(badges)} badges for {'admin' if is_admin else 'user'}")
        return jsonify(badges), 200
    except Exception as e:
        print(f"❌ Error in get_all_badges: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/profile/badges', methods=['GET'])
@login_required
def get_user_badges():
    """Get badges earned by the current user."""
    user_id = request.current_user['user_id']
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.id, b.name, b.description, b.icon_url, b.xp_threshold, b.color, ub.earned_at
            FROM badges b
            INNER JOIN user_badges ub ON b.id = ub.badge_id
            WHERE ub.user_id = ? AND b.is_active = 1
            ORDER BY ub.earned_at DESC
            """, (user_id,)
        )
        badges = []
        for row in cursor.fetchall():
            badges.append({
                "id": row['id'], 
                "name": row['name'], 
                "description": row['description'],
                "icon_url": row['icon_url'], 
                "xp_threshold": row['xp_threshold'], 
                "color": row['color'],
                "earned_at": row['earned_at'] if row['earned_at'] else None
            })
        return jsonify(badges), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# --- User Management APIs ---
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users with their stats."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
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
                "id": row['id'], 
                "name": row['name'], 
                "email": row['email'], 
                "xp": row['xp'],
                "avatar_url": row['avatar_url'], 
                "created_at": row['created_at'] if row['created_at'] else None,
                "role": row['role'] or "user", 
                "completed_lessons": row['completed_lessons'], 
                "badges_earned": row['badges_earned']
            })
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/users/<int:user_id>/reset-progress', methods=['PUT'])
@admin_required
def reset_user_progress(user_id):
    """Reset a user's progress (admin only)."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Reset user XP to 0
        cursor.execute("UPDATE users SET xp = 0 WHERE id = ?", (user_id,))
        
        # Delete all lesson progress
        cursor.execute("DELETE FROM lesson_progress WHERE user_id = ?", (user_id,))
        
        # Delete all user badges
        cursor.execute("DELETE FROM user_badges WHERE user_id = ?", (user_id,))
        
        # Delete all quiz attempts
        cursor.execute("DELETE FROM user_quiz_attempts WHERE user_id = ?", (user_id,))
        
        conn.commit()
        return jsonify({"message": "User progress reset successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/users/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user permanently (admin only)."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT name FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Delete all user-related data (cascading deletes should handle this, but being explicit)
        cursor.execute("DELETE FROM user_quiz_attempts WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM user_badges WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM lesson_progress WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        return jsonify({"message": f"User {user[0]} deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/users/<int:user_id>/promote', methods=['PUT'])
@admin_required
def promote_user(user_id):
    """Promote a user to admin role (admin only)."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Check if user exists and get current role
        cursor.execute("SELECT name, role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_name, current_role = user
        
        # Check if already admin
        if current_role == 'admin':
            return jsonify({"error": "User is already an admin"}), 400
        
        # Promote to admin
        cursor.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user_id,))
        
        conn.commit()
        return jsonify({"message": f"User {user_name} promoted to admin successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/users/<int:user_id>/award-badges', methods=['POST'])
@admin_required
def award_missing_badges(user_id):
    """Award missing badges to a user based on their current XP (admin only)."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Get user's current XP
        cursor.execute("SELECT name, xp FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_name, user_xp = user
        
        # Find badges this user should have earned but doesn't have
        cursor.execute("""
            SELECT b.id, b.name, b.xp_threshold 
            FROM badges b 
            WHERE b.xp_threshold <= ? 
            AND b.is_active = 1
            AND b.id NOT IN (
                SELECT ub.badge_id FROM user_badges ub WHERE ub.user_id = ?
            )
            ORDER BY b.xp_threshold
        """, (user_xp, user_id))
        
        missing_badges = cursor.fetchall()
        
        if not missing_badges:
            return jsonify({"message": f"User {user_name} already has all eligible badges"}), 200
        
        # Award the missing badges
        awarded_badges = []
        for badge_id, badge_name, xp_threshold in missing_badges:
            cursor.execute("""
                INSERT INTO user_badges (user_id, badge_id, earned_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, badge_id))
            awarded_badges.append({"name": badge_name, "xp_threshold": xp_threshold})
        
        conn.commit()
        return jsonify({
            "message": f"Awarded {len(awarded_badges)} badges to {user_name}",
            "awarded_badges": awarded_badges
        }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/users/<int:user_id>/activity', methods=['GET'])
@admin_required
def get_user_recent_activity(user_id):
    """Get recent activity for a specific user (admin only)."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()

        activities = []

        # Registration
        try:
            cursor.execute("SELECT name, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row and row['created_at']:
                activities.append({
                    "type": "registration",
                    "title": "Joined the platform",
                    "details": row['name'],
                    "timestamp": row['created_at']
                })
        except Exception:
            pass

        # Lesson completions
        try:
            cursor.execute(
                """
                SELECT l.title as lesson_title, lp.completed_at, lp.xp_earned
                FROM lesson_progress lp
                JOIN lessons l ON l.id = lp.lesson_id
                WHERE lp.user_id = ? AND lp.is_completed = 1 AND lp.completed_at IS NOT NULL
                ORDER BY lp.completed_at DESC
                LIMIT 20
                """,
                (user_id,)
            )
            for r in cursor.fetchall():
                activities.append({
                    "type": "completion",
                    "title": f"Completed lesson",
                    "details": r['lesson_title'],
                    "xp": r['xp_earned'] or 0,
                    "timestamp": r['completed_at']
                })
        except Exception:
            pass

        # Quiz attempts
        try:
            cursor.execute(
                """
                SELECT l.title as lesson_title, uqa.score, uqa.passed, uqa.attempted_at
                FROM user_quiz_attempts uqa
                JOIN lessons l ON l.id = uqa.lesson_id
                WHERE uqa.user_id = ?
                ORDER BY uqa.attempted_at DESC
                LIMIT 20
                """,
                (user_id,)
            )
            for r in cursor.fetchall():
                activities.append({
                    "type": "quiz",
                    "title": "Quiz attempted",
                    "details": r['lesson_title'],
                    "score": r['score'],
                    "passed": bool(r['passed']),
                    "timestamp": r['attempted_at']
                })
        except Exception:
            pass

        # Badges earned
        try:
            cursor.execute(
                """
                SELECT b.name as badge_name, ub.earned_at
                FROM user_badges ub
                JOIN badges b ON b.id = ub.badge_id
                WHERE ub.user_id = ?
                ORDER BY ub.earned_at DESC
                LIMIT 20
                """,
                (user_id,)
            )
            for r in cursor.fetchall():
                activities.append({
                    "type": "badge",
                    "title": "Badge earned",
                    "details": r['badge_name'],
                    "timestamp": r['earned_at']
                })
        except Exception:
            pass

        # Sort by timestamp (string in ISO-like format) descending and limit
        activities.sort(key=lambda a: (a.get('timestamp') or ''), reverse=True)
        activities = activities[:30]

        return jsonify(activities), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# --- Media Library APIs ---
@app.route('/api/admin/media', methods=['GET'])
@admin_required
def list_media_files():
    """List all files under the uploads directory (recursively)."""
    root = app.config['UPLOAD_FOLDER']
    media = []
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            for fname in filenames:
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, root).replace('\\', '/')
                url = f"/uploads/{rel_path}"
                size = os.path.getsize(full_path)
                mime, _ = mimetypes.guess_type(full_path)
                media.append({
                    "name": fname,
                    "path": rel_path,
                    "url": url,
                    "size": size,
                    "mime": mime or "application/octet-stream"
                })
        # Sort by name (could sort by mtime if needed)
        media.sort(key=lambda x: x['name'].lower())
        return jsonify(media), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list media: {str(e)}"}), 500

@app.route('/api/admin/media/upload', methods=['POST'])
@admin_required
def upload_media_files():
    """Upload one or more media files to uploads/ (supports any file type)."""
    if 'files' not in request.files:
        return jsonify({"error": "No files part in request"}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files selected"}), 400

    saved = []
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    timestamp = int(time.time())
    try:
        for idx, f in enumerate(files):
            if not f or not f.filename:
                continue
            base, ext = os.path.splitext(f.filename)
            safe = secure_filename(base) or 'file'
            filename = f"{safe}_{timestamp}_{idx}{ext}"
            dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(dest)
            rel_path = filename
            url = f"/uploads/{rel_path}"
            size = os.path.getsize(dest)
            mime, _ = mimetypes.guess_type(dest)
            saved.append({
                "name": filename,
                "path": rel_path,
                "url": url,
                "size": size,
                "mime": mime or "application/octet-stream"
            })
        return jsonify({"message": "Files uploaded", "files": saved}), 201
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/api/admin/media/delete', methods=['DELETE'])
@admin_required
def delete_media_file():
    """Delete a media file from uploads/ directory."""
    data = request.get_json()
    file_path = data.get('path')
    
    if not file_path:
        return jsonify({"error": "File path is required"}), 400
    
    try:
        # Security: ensure the path is within uploads folder
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        normalized = os.path.normpath(full_path)
        
        if not normalized.startswith(os.path.normpath(app.config['UPLOAD_FOLDER'])):
            return jsonify({"error": "Invalid file path"}), 400
        
        if not os.path.exists(normalized):
            return jsonify({"error": "File not found"}), 404
        
        os.remove(normalized)
        return jsonify({"message": "File deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Delete failed: {str(e)}"}), 500
# --- Dashboard Statistics APIs ---
@app.route('/api/admin/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get comprehensive dashboard statistics for admin panel."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        # Initialize default values
        stats = {
            "total_users": 0,
            "total_lessons": 0,
            "total_categories": 0,
            "total_quiz_questions": 0,
            "total_badges": 0,
            "completed_lessons": 0,
            "recent_users": 0,
            "recent_completions": 0,
            "total_xp_awarded": 0
        }
        
        # Get total users (with error handling)
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            stats["total_users"] = cursor.fetchone()[0]
        except:
            stats["total_users"] = 0
        
        # Get total lessons (with error handling)
        try:
            cursor.execute("SELECT COUNT(*) FROM lessons")
            stats["total_lessons"] = cursor.fetchone()[0]
        except:
            stats["total_lessons"] = 0
        
        # Get total categories (with error handling)
        try:
            cursor.execute("SELECT COUNT(*) FROM categories")
            stats["total_categories"] = cursor.fetchone()[0]
        except:
            stats["total_categories"] = 0
        
        # Get total quiz questions (with error handling)
        try:
            cursor.execute("SELECT COUNT(*) FROM quiz_questions")
            stats["total_quiz_questions"] = cursor.fetchone()[0]
        except:
            stats["total_quiz_questions"] = 0
        
        # Get total badges (with error handling)
        try:
            cursor.execute("SELECT COUNT(*) FROM badges")
            stats["total_badges"] = cursor.fetchone()[0]
        except:
            stats["total_badges"] = 0
        
        # Get completed lessons count (with error handling)
        try:
            cursor.execute("SELECT COUNT(*) FROM lesson_progress WHERE is_completed = TRUE")
            stats["completed_lessons"] = cursor.fetchone()[0]
        except:
            stats["completed_lessons"] = 0
        
        # Get recent users (last 7 days) (with error handling)
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE created_at >= datetime('now', '-7 days')
            """)
            stats["recent_users"] = cursor.fetchone()[0]
        except:
            stats["recent_users"] = 0
        
        # Get recent lesson completions (last 7 days) (with error handling)
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM lesson_progress 
                WHERE completed_at >= datetime('now', '-7 days')
            """)
            stats["recent_completions"] = cursor.fetchone()[0]
        except:
            stats["recent_completions"] = 0
        
        # Get total XP awarded (with error handling)
        try:
            cursor.execute("SELECT COALESCE(SUM(xp), 0) FROM users")
            stats["total_xp_awarded"] = cursor.fetchone()[0]
        except:
            stats["total_xp_awarded"] = 0
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/dashboard/recent-activity', methods=['GET'])
@admin_required
def get_recent_activity():
    """Get recent activity for dashboard."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        activities = []
        
        # Get recent user registrations (with error handling)
        try:
            cursor.execute("""
                SELECT 'registration' as type, name, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_registrations = cursor.fetchall()
            
            for reg in recent_registrations:
                activities.append({
                    "type": "registration",
                    "text": f"New user registered: {reg[1]}",
                    "time": reg[2],
                    "timestamp": reg[2]
                })
        except:
            pass
        
        # Get recent lesson completions (with error handling)
        try:
            cursor.execute("""
                SELECT 'completion' as type, u.name, l.title, lp.completed_at
                FROM lesson_progress lp
                JOIN users u ON lp.user_id = u.id
                JOIN lessons l ON lp.lesson_id = l.id
                WHERE lp.is_completed = TRUE
                ORDER BY lp.completed_at DESC 
                LIMIT 5
            """)
            recent_completions = cursor.fetchall()
            
            for comp in recent_completions:
                activities.append({
                    "type": "completion",
                    "text": f"Lesson '{comp[2]}' completed by {comp[1]}",
                    "time": comp[3],
                    "timestamp": comp[3]
                })
        except:
            pass
        
        # Get recent badge earnings (with error handling)
        try:
            cursor.execute("""
                SELECT 'badge' as type, u.name, b.name as badge_name, ub.earned_at
                FROM user_badges ub
                JOIN users u ON ub.user_id = u.id
                JOIN badges b ON ub.badge_id = b.id
                ORDER BY ub.earned_at DESC 
                LIMIT 5
            """)
            recent_badges = cursor.fetchall()
            
            for badge in recent_badges:
                activities.append({
                    "type": "badge",
                    "text": f"Badge '{badge[2]}' earned by {badge[1]}",
                    "time": badge[3],
                    "timestamp": badge[3]
                })
        except:
            pass
        
        # Sort by timestamp and limit to 10 most recent
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:10]
        
        # Format timestamps to relative time
        from datetime import datetime
        now = datetime.now()
        
        for activity in activities:
            if activity["timestamp"]:
                diff = now - activity["timestamp"]
                if diff.days > 0:
                    activity["time"] = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
                elif diff.seconds > 3600:
                    hours = diff.seconds // 3600
                    activity["time"] = f"{hours} hour{'s' if hours > 1 else ''} ago"
                elif diff.seconds > 60:
                    minutes = diff.seconds // 60
                    activity["time"] = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                else:
                    activity["time"] = "Just now"
        
        return jsonify(activities), 200
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

@app.route('/api/admin/dashboard/analytics', methods=['GET'])
@admin_required
def get_dashboard_analytics():
    """Get analytics data for charts."""
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        
        analytics = {
            "user_activity": [],
            "completion_stats": {"total": 0, "completed": 0, "in_progress": 0},
            "category_distribution": []
        }
        
        # Get user activity over last 7 days (with error handling)
        try:
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM users 
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """)
            user_activity = cursor.fetchall()
            analytics["user_activity"] = [{"date": str(row[0]), "count": row[1]} for row in user_activity]
        except:
            analytics["user_activity"] = []
        
        # Get lesson completion rates (with error handling)
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_attempts,
                    COUNT(CASE WHEN is_completed = TRUE THEN 1 END) as completed,
                    COUNT(CASE WHEN is_completed = FALSE THEN 1 END) as in_progress
                FROM lesson_progress
            """)
            completion_data = cursor.fetchone()
            analytics["completion_stats"] = {
                "total": completion_data[0] or 0,
                "completed": completion_data[1] or 0,
                "in_progress": completion_data[2] or 0
            }
        except:
            analytics["completion_stats"] = {"total": 0, "completed": 0, "in_progress": 0}
        
        # Get category distribution (with error handling)
        try:
            cursor.execute("""
                SELECT c.name, COUNT(l.id) as lesson_count
                FROM categories c
                LEFT JOIN lessons l ON c.id = l.category_id
                GROUP BY c.id, c.name
                ORDER BY lesson_count DESC
            """)
            category_data = cursor.fetchall()
            analytics["category_distribution"] = [{"name": row[0], "count": row[1]} for row in category_data]
        except:
            analytics["category_distribution"] = []
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        if conn: conn.close()

# --- Database Setup Route ---
@app.route('/setup-database')
def setup_database_route():
    """Route to setup database tables and sample data."""
    if setup_database():
        return jsonify({"message": "Database setup completed successfully!", "status": "success"})
    else:
        return jsonify({"message": "Database setup failed!", "status": "error"}), 500

# --- Main Route ---
@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/lessons')
def lessons_page():
    # Check if category_id is provided in query parameters
    category_id = request.args.get('category_id')
    if not category_id:
        return redirect(url_for('archive_page'))
    return render_template('lessons.html')

@app.route('/lesson')
def lesson_page():
    """Handle lesson page with either ID or slug parameter."""
    lesson_id = request.args.get('id')
    lesson_slug = request.args.get('slug')
    
    if not lesson_id and not lesson_slug:
        return redirect(url_for('archive_page'))
    
    return render_template('lesson.html')

@app.route('/quiz')
def quiz_page():
    """Handle quiz page."""
    lesson_id = request.args.get('lesson_id')
    lesson_title = request.args.get('title')
    lesson_slug = request.args.get('slug')
    
    if not lesson_id:
        return redirect(url_for('archive_page'))
    
    return render_template('quiz.html')

@app.route('/leaderboard')
def leaderboard_page():
    if not g.user:
        return redirect(url_for('auth_page'))
    return render_template('leaderboard.html')

@app.route('/games')
def games_page():
    if not g.user:
        return redirect(url_for('auth_page'))
    return render_template('games.html')

@app.route('/profile')
def profile_page():
    if not g.user:
        return redirect(url_for('auth_page'))
    return render_template('profile.html')

@app.route('/archive')
def archive_page():
    if not g.user:
        return redirect(url_for('auth_page'))
    return render_template('archive.html')

@app.route('/admin-login')
def admin_login_test():
    """Test route to log in as admin for testing purposes"""
    # Create a test token for admin user
    from datetime import datetime, timedelta
    admin_token = jwt.encode({
        'user_id': 1,
        'role': 'admin',
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config["JWT_SECRET_KEY"], algorithm="HS256")
    
    # Set user session
    if set_user_session_from_token(admin_token):
        return redirect(url_for('admin_panel'))
    else:
        return "Failed to create admin session", 500

@app.route('/admin')
def admin_panel():
    if not g.user:
        print("DEBUG: No user in session, redirecting to auth")
        return redirect(url_for('auth_page'))
    
    print(f"DEBUG: User in session: {g.user}")
    print(f"DEBUG: User role: {g.user.get('role')}")
    
    # Check if user is admin
    if g.user.get('role') != 'admin':
        print("DEBUG: User is not admin, redirecting to home")
        return redirect(url_for('home_page'))
    
    print("DEBUG: User is admin, rendering admin panel")
    return render_template('admin/index.html')

@app.route('/admin/lessons')
def admin_lessons():
    if not g.user:
        return redirect(url_for('auth_page'))
    
    # Check if user is admin
    if g.user.get('role') != 'admin':
        return redirect(url_for('home_page'))
    
    return render_template('admin/lessons.html')

@app.route('/admin/quiz')
def admin_quiz():
    if not g.user:
        return redirect(url_for('auth_page'))
    
    # Check if user is admin
    if g.user.get('role') != 'admin':
        return redirect(url_for('home_page'))
    
    return render_template('admin/quiz.html')

@app.route('/admin/categories')
def admin_categories():
    if not g.user:
        return redirect(url_for('auth_page'))
    
    # Check if user is admin
    if g.user.get('role') != 'admin':
        return redirect(url_for('home_page'))
    
    return render_template('admin/categories.html')

@app.route('/admin/badges')
def admin_badges():
    if not g.user:
        return redirect(url_for('auth_page'))
    
    # Check if user is admin
    if g.user.get('role') != 'admin':
        return redirect(url_for('home_page'))
    
    return render_template('admin/badges.html')

@app.route('/admin/users')
def admin_users():
    if not g.user:
        return redirect(url_for('auth_page'))
    
    # Check if user is admin
    if g.user.get('role') != 'admin':
        return redirect(url_for('home_page'))
    
    return render_template('admin/users.html')

@app.route('/admin/media')
def admin_media():
    if not g.user:
        return redirect(url_for('auth_page'))
    if g.user.get('role') != 'admin':
        return redirect(url_for('home_page'))
    return render_template('admin/media.html')

# Backward-compat: redirect /archive.html → /archive
@app.route('/archive.html')
def archive_html_redirect():
    return redirect(url_for('archive_page'))

@app.route('/auth', methods=['GET', 'POST'])
def auth_page():
    if request.method == 'POST':
        token = request.form.get('token')
        if token and set_user_session_from_token(token):
            return redirect(url_for('archive_page'))
        return render_template('auth.html'), 401
    return render_template('auth.html')

@app.route('/logout', methods=['POST'])
def logout_page():
    session.pop('user', None)
    return redirect(url_for('home_page'))

# --- Run the App ---
if __name__ == '__main__':
    test_db_connection()
    # Setup database tables and sample data
    setup_database()
    app.run(debug=True, port=5000)