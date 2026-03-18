# 🦍 CodeDonki

CodeDonki is a web-based learning platform that teaches primary students (ages 8–12) Python fundamentals with interactive 3D/AR lessons, quizzes, XP, badges, and an admin dashboard.

## ✨ What's in the website
- **Interactive lessons**: 3D/AR learning pages for Python basics (print, variables, input, if).
- **Quizzes**: Multiple-choice quizzes after lessons.
- **Progress & rewards**: XP, badges, and a leaderboard.
- **Accounts**: Student login and admin management.
- **Admin dashboard**: Manage users, lessons, quizzes, categories, and badges.

## 🛠 Tech Stack
- **Backend**: Flask (Python)
- **Database**: MySQL (via PyMySQL)
- **Frontend**: HTML/CSS/JavaScript (vanilla), Three.js

## 📁 Project Structure
```
app.py
requirements.txt
database_schema_mysql.sql
public/          # CSS/JS assets
templates/       # HTML templates
uploads/         # user uploads
python_*_*.html  # lesson pages
```

## 🚀 Setup

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a MySQL database**
   ```sql
   CREATE DATABASE codedonki CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Create a `.env` file** (copy from `env.template`)
   ```env
   FLASK_SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your-mysql-password
   MYSQL_DATABASE=codedonki
   GEMINI_API_KEY=your-gemini-api-key
   DEBUG=True
   ```

4. **Run the app** — the database schema and demo data are created automatically on first start
   ```bash
   python app.py
   ```

5. **Open the site**
   ```
   http://127.0.0.1:5000
   ```

### Cloud / Vercel Deployment
Set the environment variables below in your hosting dashboard. Use a managed MySQL provider such as [PlanetScale](https://planetscale.com/), [Railway](https://railway.app/), or [Aiven](https://aiven.io/).

| Variable           | Description                             |
|--------------------|-----------------------------------------|
| `FLASK_SECRET_KEY` | Random secret key for Flask sessions    |
| `JWT_SECRET_KEY`   | Random secret key for JWT tokens        |
| `MYSQL_HOST`       | MySQL server hostname                   |
| `MYSQL_PORT`       | MySQL server port (default `3306`)      |
| `MYSQL_USER`       | MySQL username                          |
| `MYSQL_PASSWORD`   | MySQL password                          |
| `MYSQL_DATABASE`   | Database name (e.g. `codedonki`)        |
| `GEMINI_API_KEY`   | Google Gemini AI key (optional)         |

## 🔑 Demo Credentials

Use these accounts to test the platform without registering. All demo accounts are created automatically on first startup.

### 👑 Admin Account
| Field    | Value                          |
|----------|--------------------------------|
| Email    | `admin@codedonki.com`          |
| Password | `admin123`                     |
| Role     | Admin (full dashboard access)  |

### 👤 Demo User Account
| Field    | Value                  |
|----------|------------------------|
| Email    | `user@codedonki.com`   |
| Password | `user123`              |
| Role     | Student                |

> **Tip:** You can also register a brand-new account from the `/auth` page.

## 📄 License
MIT License
