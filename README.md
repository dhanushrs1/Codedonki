# 🦍 CodeDonki - Interactive AR/3D Coding Learning Platform

![CodeDonki](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)

**CodeDonki** is a gamified, interactive learning platform designed to teach coding to primary school students (ages 8-12) through engaging **3D visualizations**, **Augmented Reality (AR)** experiences, and **AI-powered personalized tutoring**.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Core Features](#core-features)
- [Admin Dashboard](#admin-dashboard)
- [AI Integration](#ai-integration)
- [Universal Lesson Framework](#universal-lesson-framework)
- [Usage Guide](#usage-guide)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

CodeDonki transforms coding education into an exciting adventure where students:
- **Learn by doing**: Interactive 3D games and AR experiences
- **Earn rewards**: XP points, badges, and leaderboard rankings
- **Get personalized help**: AI-powered hints and dialogue
- **Track progress**: Comprehensive learning dashboard
- **Take quizzes**: Test knowledge with dynamic quiz system

### Target Audience
- **Primary Students**: Ages 8-12 (higher primary school)
- **Beginners**: No prior coding experience required
- **Visual Learners**: 3D/AR visualization of coding concepts

---

## ✨ Key Features

### 🎮 Gamified Learning Experience
- **XP System**: Earn 50-100 XP per lesson completion
- **Badges**: Unlock achievements (Beginner → Explorer → Achiever → Expert → Master → Legend)
- **Leaderboard**: Compete with peers globally
- **Progressive Unlocking**: Complete lessons to unlock next challenges

### 🌟 Interactive 3D/AR Lessons
- **3D Visualizations**: Python concepts come alive in 3D space
- **AR Integration**: View code structures in your physical environment
- **Hands-On Coding**: Type real Python code in-game
- **Immediate Feedback**: See results instantly

### 🤖 AI-Powered Learning (Gemini AI)
- **Personalized Hints**: Context-aware coding assistance
- **Dynamic Dialogue**: Characters respond naturally using student's name
- **Adaptive Learning**: AI adjusts to student's skill level
- **Topic-Specific Guidance**: Focused help on current lesson

### 📚 Comprehensive Curriculum
- **Python Basics**: print(), variables, input(), loops
- **Web Development**: HTML, CSS, JavaScript
- **Data Structures**: Arrays, objects, algorithms
- **Progressive Difficulty**: Beginner to advanced

### 👨‍💼 Robust Admin System
- **User Management**: CRUD operations for students
- **Lesson Creation**: Upload custom 3D games/AR experiences
- **Quiz Builder**: Create multi-choice questions
- **Badge System**: Configure achievements
- **Analytics**: Track student progress

### 🔒 Secure Authentication
- **JWT Tokens**: Stateless authentication
- **Password Hashing**: pbkdf2_sha256 encryption
- **Role-Based Access**: User vs Admin permissions
- **Session Management**: Flask sessions

---

## 🛠 Technology Stack

### Backend
- **Flask 3.1.2**: Python web framework
- **SQLite**: Lightweight database
- **JWT**: Token-based authentication
- **Passlib**: Password hashing
- **Google Gemini AI**: AI-powered tutoring

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **Vanilla JavaScript**: ES6+ features
- **Three.js**: 3D visualizations
- **AR.js / WebXR**: Augmented reality
- **GSAP**: Animations

### APIs & Integrations
- **Google Generative AI**: Gemini 2.0 Flash
- **Flask-CORS**: Cross-origin resource sharing
- **python-dotenv**: Environment management

---

## 📁 Project Structure

```
luminex/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── database_schema_sqlite.sql      # Database schema
├── codedonki.db                    # SQLite database
├── .env                            # Environment variables (not in repo)
│
├── templates/                      # Jinja2 templates
│   ├── base.html                   # Base layout
│   ├── home.html                   # Landing page
│   ├── auth.html                   # Login/Signup
│   ├── dashboard.html              # Student dashboard
│   ├── lessons/                    # Lesson pages
│   │   ├── lesson_view.html        # Lesson container (iframe)
│   │   └── categories.html         # Browse lessons
│   ├── quiz/
│   │   └── quiz.html               # Quiz interface
│   ├── leaderboard/
│   │   └── leaderboard.html        # Global rankings
│   ├── profile/
│   │   └── profile.html            # User profile
│   └── admin/                      # Admin dashboard
│       ├── admin_dashboard.html
│       ├── admin_users.html
│       ├── admin_lessons.html
│       ├── admin_quiz.html
│       └── admin_badges.html
│
├── public/                         # Static assets
│   ├── css/                        # Stylesheets
│   │   ├── main.css                # Global styles
│   │   ├── home.css                # Landing page
│   │   ├── dashboard.css
│   │   ├── lesson.css
│   │   ├── quiz.css
│   │   ├── admin-*.css             # Admin styles
│   │   └── ...
│   └── js/                         # JavaScript modules
│       ├── api.js                  # API utilities
│       ├── auth.js                 # Authentication
│       ├── lesson.js               # Lesson logic
│       ├── quiz.js                 # Quiz system
│       ├── leaderboard.js
│       ├── profile.js
│       ├── admin.js                # Admin functions
│       └── ...
│
├── uploads/                        # User-uploaded content
│   ├── lessons/                    # 3D game HTML files
│   ├── badges/                     # Badge images
│   └── avatars/                    # User avatars
│
├── python_hello_world_3d.html      # Python print() 3D lesson
├── python_variables_backpack.html  # Variables 3D lesson
├── python_input_chat.html          # Input 3D lesson
├── python_if_traffic.html          # If statements 3D lesson
│
└── Documentation/                  # Project docs
    ├── UNIVERSAL_LESSON_FRAMEWORK.md
    ├── AI_DIALOGUE_SYSTEM.md
    ├── AI_HINT_SYSTEM.md
    └── README.md (this file)
```

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+**
- **pip** (Python package manager)
- **Modern browser** (Chrome, Firefox, Edge)
- **Google Gemini API Key** (for AI features)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/codedonki.git
cd codedonki
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database
DATABASE_PATH=codedonki.db

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key-here

# Optional
FLASK_ENV=development
DEBUG=True
```

**To get a Gemini API Key**:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy to `.env` file

### Step 4: Initialize Database
```bash
python app.py
```
The database will be automatically initialized on first run using `database_schema_sqlite.sql`.

### Step 5: Access Application
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Default Admin Credentials
- **Email**: `admin@codedonki.com`
- **Password**: `admin123`

---

## 🗄 Database Schema

### Users Table
| Column           | Type      | Description                     |
|------------------|-----------|---------------------------------|
| id               | INTEGER   | Primary key                     |
| name             | TEXT      | User's full name                |
| email            | TEXT      | Unique email                    |
| hashed_password  | TEXT      | pbkdf2_sha256 hash              |
| role             | TEXT      | 'user' or 'admin'               |
| xp               | INTEGER   | Experience points               |
| avatar_url       | TEXT      | Profile picture path            |
| created_at       | TIMESTAMP | Account creation date           |

### Lessons Table
| Column               | Type    | Description                        |
|----------------------|---------|------------------------------------|
| id                   | INTEGER | Primary key                        |
| title                | TEXT    | Lesson name                        |
| description          | TEXT    | Lesson overview                    |
| category_id          | INTEGER | Foreign key to categories          |
| ar_model_url         | TEXT    | Path to 3D/AR HTML file            |
| slug                 | TEXT    | URL-friendly identifier            |
| xp_min / xp_max      | INTEGER | XP range awarded                   |
| order_in_category    | INTEGER | Lesson sequence                    |
| pass_threshold       | INTEGER | Min % to pass quiz (default 70%)   |
| is_locked_by_default | BOOLEAN | Lock until prerequisite complete   |

### Quiz Questions Table
| Column          | Type    | Description                    |
|-----------------|---------|--------------------------------|
| id              | INTEGER | Primary key                    |
| lesson_id       | INTEGER | Foreign key to lessons         |
| question_text   | TEXT    | Question prompt                |
| option_a/b/c/d  | TEXT    | Answer choices                 |
| correct_answer  | TEXT    | 'A', 'B', 'C', or 'D'          |
| explanation     | TEXT    | Answer explanation             |

### Badges Table
| Column        | Type    | Description                  |
|---------------|---------|------------------------------|
| id            | INTEGER | Primary key                  |
| name          | TEXT    | Badge title                  |
| description   | TEXT    | Achievement description      |
| icon_url      | TEXT    | Badge emoji/image            |
| xp_threshold  | INTEGER | XP required to unlock        |
| color         | TEXT    | Badge color hex              |

**See `database_schema_sqlite.sql` for complete schema and relationships.**

---

## 🔌 API Endpoints

### Authentication

#### `POST /api/signup`
Register a new user.

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "message": "User created successfully"
}
```

#### `POST /api/login`
Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user"
}
```

### Lessons

#### `GET /api/categories`
Fetch all lesson categories.

**Response**:
```json
[
  {
    "id": 1,
    "name": "Python Programming",
    "description": "Master Python from basics to advanced",
    "color": "#27ae60",
    "icon": "fab fa-python",
    "slug": "python-programming"
  }
]
```

#### `GET /api/lessons`
Get all lessons with progress (requires auth).

**Headers**:
```
Authorization: Bearer <token>
```

**Response**:
```json
[
  {
    "id": 1,
    "title": "Python Hello World",
    "description": "Learn print() with 3D characters",
    "ar_model_url": "/python_hello_world_3d.html",
    "xp_min": 50,
    "xp_max": 100,
    "is_completed": false,
    "is_unlocked": true
  }
]
```

### Quiz System

#### `POST /api/quiz/submit`
Submit quiz answers and receive score.

**Request Body**:
```json
{
  "lesson_id": 1,
  "answers": ["A", "C", "B"]
}
```

**Response**:
```json
{
  "score": 66,
  "passed": false,
  "xp_awarded": 0,
  "pass_threshold": 70,
  "message": "Keep trying!"
}
```

### AI Features

#### `POST /api/hint`
Get AI-powered coding hint.

**Request Body**:
```json
{
  "code": "print('Hello)",
  "student_name": "John",
  "challenge": 1,
  "topic": "print"
}
```

**Response**:
```json
{
  "hint": "Hey John! Don't forget to close your quotes with another ' or \"!"
}
```

#### `POST /api/dialogue`
Generate personalized AI dialogue.

**Request Body**:
```json
{
  "student_name": "John",
  "stage": "greeting",
  "user_input": "",
  "challenge": 1
}
```

**Response**:
```json
{
  "dialogue": "Hello John! I'm doing great!",
  "should_continue": true
}
```

### Leaderboard

#### `GET /api/leaderboard`
Fetch global rankings.

**Response**:
```json
[
  {
    "rank": 1,
    "name": "Alice Johnson",
    "xp": 2500,
    "avatar_url": "/uploads/avatars/alice.png"
  }
]
```

---

## 🎓 Core Features

### 1. Universal Lesson Framework

All 3D games use a **universal completion signal** that triggers quiz popups automatically.

**In Any Game File**:
```javascript
// Signal lesson completion
function signalLessonComplete() {
    if (window.parent && window.parent !== window) {
        window.parent.postMessage({
            type: 'LESSON_COMPLETE',
            studentName: studentName,
            timestamp: new Date().toISOString()
        }, '*');
    }
}

// Call when student finishes
signalLessonComplete();
```

**Parent Page Listener** (in `lesson.js`):
```javascript
window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'LESSON_COMPLETE') {
        showQuizPopup(event.data.studentName);
    }
});
```

**Benefits**:
- ✅ No duplicate code in each game
- ✅ Consistent quiz flow across all lessons
- ✅ Easy to add new games without modification

See `UNIVERSAL_LESSON_FRAMEWORK.md` for details.

---

### 2. AI-Powered Personalized Dialogue

Characters in 3D lessons use the student's name and respond dynamically.

**Example Flow**:
1. **Game Fetches Name**: From session or user input
2. **Student Codes**: Types `print("Hi!")`
3. **AI Responds**: "Thanks John! That worked perfectly!"
4. **Celebration**: "Awesome John! You're a Python star!"

**Key Features**:
- Uses **Gemini 2.0 Flash** for fast responses
- Context-aware (knows what student is learning)
- Topic-focused (won't go off-topic)
- Fallback responses if API unavailable

See `AI_DIALOGUE_SYSTEM.md` for implementation.

---

### 3. Intelligent Hint System

Auto-triggers when students make mistakes:

```javascript
// Student types incorrect code
const hint = await getHint(userCode, 'print', 1);
// Returns: "Hey John! Strings need quotes: print(\"Hi!\")"
```

**Topic-Specific Hints**:
- **print()**: Quote usage, syntax
- **variables**: Assignment, naming
- **input()**: User input, concatenation
- **loops**: Indentation, range()

**AI Enhancement**:
- Analyzes student's code
- Identifies specific mistake
- Provides step-by-step guidance
- Encouraging and friendly tone

See `AI_HINT_SYSTEM.md` for details.

---

### 4. Progressive XP & Badge System

**XP Calculation**:
```python
xp_earned = xp_min + (xp_max - xp_min) * (score / 100)
```

**Example**:
- Lesson XP range: 50-100
- Quiz score: 80%
- XP earned: 50 + (50 × 0.8) = **90 XP**

**Badges**:
| Badge      | XP Required | Icon |
|------------|-------------|------|
| Beginner   | 0           | 🌱   |
| Explorer   | 100         | 🔍   |
| Achiever   | 250         | ⭐   |
| Expert     | 500         | 🏆   |
| Master     | 1000        | 👑   |
| Legend     | 2000        | 💎   |

**Auto-Award**:
- Badges automatically awarded when threshold reached
- Notification shown to user
- Displayed on profile and leaderboard

---

### 5. Quiz System with Timer

**Features**:
- 10 minutes per quiz
- Real-time countdown
- Auto-submit on timeout
- Randomized question order
- Immediate feedback
- Explanation for wrong answers
- Pass threshold: 70% (configurable)

**Quiz Flow**:
1. Complete lesson
2. Quiz popup appears
3. Click "Take Quiz Now"
4. Answer multiple-choice questions
5. Submit answers
6. View score and explanations
7. Earn XP if passed
8. Unlock next lesson

---

## 👨‍💼 Admin Dashboard

Access: `/admin/dashboard` (requires admin role)

### Features

#### 1. User Management (`/admin/users`)
- View all registered users
- Edit user details (name, email, XP)
- Change user roles (user ↔ admin)
- Delete users
- Search and filter

#### 2. Lesson Management (`/admin/lessons`)
- Create new lessons
- Upload 3D game HTML files
- Set XP range (min/max)
- Configure pass threshold
- Set lesson order
- Lock/unlock lessons
- Assign categories
- Edit/delete lessons

#### 3. Quiz Builder (`/admin/quiz`)
- Create questions for any lesson
- 4-option multiple choice
- Set correct answer
- Add explanations
- Bulk import questions
- Edit/delete questions

#### 4. Badge Configuration (`/admin/badges`)
- Create custom badges
- Set XP thresholds
- Upload badge icons
- Configure colors
- Activate/deactivate badges

#### 5. Category Management
- Create lesson categories
- Set category colors and icons
- Organize lessons by topic

---

## 🤖 AI Integration (Google Gemini)

### Configuration

**Model**: Gemini 2.0 Flash (fast, cost-effective)

**Key Features**:
1. **Personalized Hints**: Context-aware coding assistance
2. **Dynamic Dialogue**: Natural conversations with characters
3. **Topic Constraints**: AI stays on-topic
4. **Error Handling**: Graceful fallbacks

### API Calls

**Hint Generation**:
```python
model = genai.GenerativeModel('gemini-2.0-flash-exp')
system_prompt = f"You are Donki, a friendly Python tutor for {student_name}..."
response = model.generate_content([system_prompt, user_code])
```

**Dialogue Generation**:
```python
# Character speaks naturally using student's name
dialogue = ai_dialogue(
    student_name="John",
    stage="celebration",
    user_input="",
    challenge=1
)
# Returns: "Awesome John! You're a Python star!"
```

### Security

✅ **API Key on Backend Only**: Never exposed to frontend  
✅ **Proxy Endpoint**: All AI calls go through Flask  
✅ **Rate Limiting**: Prevent abuse  
✅ **Fallback Responses**: Works without API key

---

## 📖 Usage Guide

### For Students

#### 1. Sign Up
1. Visit homepage
2. Click "Start Your Adventure!"
3. Fill signup form
4. Verify email (if configured)

#### 2. Browse Lessons
1. Go to Dashboard
2. Click "Browse Lessons"
3. Select a category
4. View available lessons

#### 3. Complete Lesson
1. Click unlocked lesson
2. Watch introduction
3. Play 3D game in iframe
4. Code along with challenges
5. Get AI hints if stuck
6. Complete all challenges

#### 4. Take Quiz
1. Quiz popup appears
2. Click "Take Quiz Now"
3. Answer questions (10 min timer)
4. Submit answers
5. View score and explanations

#### 5. Track Progress
- **Dashboard**: View completed lessons
- **Profile**: See XP, badges, stats
- **Leaderboard**: Compare with peers

---

### For Admins

#### 1. Access Admin Panel
- Login with admin account
- Navigate to `/admin/dashboard`

#### 2. Upload New Lesson
1. Go to "Lessons" tab
2. Click "Create Lesson"
3. Fill form:
   - Title
   - Description
   - Category
   - XP range
   - Upload 3D game HTML
4. Save lesson

#### 3. Create Quiz Questions
1. Go to "Quiz" tab
2. Select lesson
3. Click "Add Question"
4. Fill question details
5. Set correct answer
6. Add explanation
7. Save

#### 4. Monitor Users
1. Go to "Users" tab
2. View all students
3. Check progress
4. Adjust XP if needed

---

## 🔐 Security Best Practices

### Implemented Protections

✅ **Password Hashing**: pbkdf2_sha256 with salt  
✅ **JWT Authentication**: Stateless, secure tokens  
✅ **Role-Based Access Control**: User vs Admin permissions  
✅ **SQL Injection Prevention**: Parameterized queries  
✅ **CORS Configuration**: Whitelisted origins only  
✅ **File Upload Validation**: Secure filename handling  
✅ **API Key Protection**: Backend-only storage  

### Recommended Enhancements

- [ ] Add HTTPS/SSL certificate
- [ ] Implement rate limiting (Flask-Limiter)
- [ ] Add CSRF protection (Flask-WTF)
- [ ] Email verification for signup
- [ ] Password reset functionality
- [ ] Two-factor authentication (2FA)
- [ ] Audit logging for admin actions

---

## 🧪 Testing

### Manual Testing Checklist

**Authentication**:
- [ ] Signup with new user
- [ ] Login with credentials
- [ ] Logout and session clear
- [ ] Admin vs User role access

**Lessons**:
- [ ] Browse categories
- [ ] View lesson details
- [ ] Complete 3D game
- [ ] Quiz popup appears
- [ ] Take and submit quiz
- [ ] XP awarded correctly
- [ ] Next lesson unlocks

**AI Features**:
- [ ] Personalized dialogue uses name
- [ ] Hints generate correctly
- [ ] Fallback responses work without API

**Admin**:
- [ ] Create new lesson
- [ ] Upload game file
- [ ] Add quiz questions
- [ ] Manage users
- [ ] Configure badges

---

## 🐛 Troubleshooting

### Database Issues
**Problem**: Database connection failed  
**Solution**:
```bash
# Check file exists
ls codedonki.db

# Reinitialize database
rm codedonki.db
python app.py
```

### AI Not Working
**Problem**: AI hints return default responses  
**Solution**:
1. Check `.env` has `GEMINI_API_KEY`
2. Verify API key is valid
3. Check Flask console for errors
4. Ensure internet connection

### Quiz Not Loading
**Problem**: Quiz page shows no questions  
**Solution**:
1. Admin → Quiz → Check questions exist for lesson
2. Verify `lesson_id` in URL
3. Check browser console for errors

### Lesson Not Unlocking
**Problem**: Next lesson stays locked after quiz pass  
**Solution**:
1. Check quiz score ≥ pass_threshold (70%)
2. Verify lesson sequence in database
3. Check `lesson_progress` table for correct entries

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 1. Fork Repository
```bash
git clone https://github.com/yourusername/codedonki.git
cd codedonki
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow existing code style
- Add comments for complex logic
- Test thoroughly before committing

### 3. Commit and Push
```bash
git add .
git commit -m "feat: Add new 3D game for loops"
git push origin feature/your-feature-name
```

### 4. Create Pull Request
- Describe your changes
- Reference related issues
- Request review from maintainers

### Contribution Ideas

**New Features**:
- [ ] Additional programming languages (JavaScript, Java, C++)
- [ ] Mobile app version
- [ ] Parent/Teacher dashboard
- [ ] Video lessons integration
- [ ] Code playgrounds
- [ ] Social features (friend system, challenges)

**Improvements**:
- [ ] Better 3D graphics
- [ ] More AR experiences
- [ ] Expanded AI capabilities
- [ ] Accessibility features
- [ ] Internationalization (i18n)

**Bug Fixes**:
- Report issues on GitHub
- Provide detailed reproduction steps
- Include screenshots/logs if applicable

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 CodeDonki

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support & Contact

### Documentation
- **Main README**: This file
- **AI System**: `AI_DIALOGUE_SYSTEM.md`, `AI_HINT_SYSTEM.md`
- **Lesson Framework**: `UNIVERSAL_LESSON_FRAMEWORK.md`

### Community
- **Issues**: [GitHub Issues](https://github.com/yourusername/codedonki/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/codedonki/discussions)
- **Email**: admin@codedonki.com

### Acknowledgments

**Technologies Used**:
- Flask (Pallets Projects)
- Google Gemini AI (Google)
- Three.js (Mr.doob)
- Font Awesome (Fonticons)

**Inspiration**:
- Scratch (MIT Media Lab)
- Code.org
- Khan Academy

---

## 🎉 Get Started Today!

Transform coding education into an adventure:

```bash
# Clone the repo
git clone https://github.com/yourusername/codedonki.git

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Visit in browser
http://127.0.0.1:5000
```

**Start Your Coding Journey with CodeDonki!** 🦍🚀

---

*Last Updated: October 24, 2025*  
*Version: 1.0.0*  
*Maintainer: CodeDonki Team*

