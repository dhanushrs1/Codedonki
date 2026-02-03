# 🦍 CodeDonki

CodeDonki is a web-based learning platform that teaches primary students (ages 8–12) Python fundamentals with interactive 3D/AR lessons, quizzes, XP, badges, and an admin dashboard.

## ✨ What’s in the website
- **Interactive lessons**: 3D/AR learning pages for Python basics (print, variables, input, if).
- **Quizzes**: Multiple-choice quizzes after lessons.
- **Progress & rewards**: XP, badges, and a leaderboard.
- **Accounts**: Student login and admin management.
- **Admin dashboard**: Manage users, lessons, quizzes, categories, and badges.

## 🛠 Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML/CSS/JavaScript (vanilla), Three.js

## 📁 Project Structure
```
app.py
requirements.txt
database_schema_sqlite.sql
public/          # CSS/JS assets
templates/       # HTML templates
uploads/         # user uploads
python_*_*.html  # lesson pages
```

## 🚀 Setup
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Create a .env file**
   ```env
   FLASK_SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   DATABASE_PATH=codedonki.db
   GEMINI_API_KEY=your-gemini-api-key
   DEBUG=True
   ```
3. **Run the app**
   ```bash
   python app.py
   ```
4. **Open the site**
   ```
   http://127.0.0.1:5000
   ```

## 🔑 Default Admin Credentials
- **Email**: `admin@codedonki.com`
- **Password**: `admin123`

## 📄 License
MIT License
