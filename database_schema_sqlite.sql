-- Database Schema for CodeDonki Learning Platform
-- SQLite Version

-- ============================================
-- Users Table
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin')),
    xp INTEGER DEFAULT 0,
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Categories Table
-- ============================================
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    color TEXT DEFAULT '#3498db',
    icon TEXT DEFAULT 'fas fa-tag',
    slug TEXT UNIQUE,
    meta_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Lessons Table
-- ============================================
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category_id INTEGER,
    ar_model_url TEXT,
    slug TEXT UNIQUE,
    xp_min INTEGER DEFAULT 50,
    xp_max INTEGER DEFAULT 100,
    order_in_category INTEGER DEFAULT 1,
    pass_threshold INTEGER DEFAULT 70,
    is_locked_by_default BOOLEAN DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- ============================================
-- Lesson Progress Table
-- ============================================
CREATE TABLE IF NOT EXISTS lesson_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    is_completed BOOLEAN DEFAULT 0,
    is_unlocked BOOLEAN DEFAULT 0,
    xp_earned INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    UNIQUE(user_id, lesson_id)
);

-- ============================================
-- Completed Lessons Table (Legacy - kept for backward compatibility)
-- ============================================
CREATE TABLE IF NOT EXISTS completed_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
    UNIQUE(user_id, lesson_id)
);

-- ============================================
-- Quiz Questions Table
-- ============================================
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A', 'B', 'C', 'D')),
    explanation TEXT,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);

-- ============================================
-- User Quiz Attempts Table
-- ============================================
CREATE TABLE IF NOT EXISTS user_quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    quiz_questions TEXT,
    user_answers TEXT,
    score INTEGER NOT NULL,
    passed BOOLEAN DEFAULT 0,
    xp_awarded INTEGER DEFAULT 0,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);

-- ============================================
-- Badges Table
-- ============================================
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon_url TEXT,
    xp_threshold INTEGER NOT NULL,
    color TEXT DEFAULT '#FFD700',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- User Badges Table
-- ============================================
CREATE TABLE IF NOT EXISTS user_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(id) ON DELETE CASCADE,
    UNIQUE(user_id, badge_id)
);

-- ============================================
-- Indexes for Performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_lessons_category ON lessons(category_id);
CREATE INDEX IF NOT EXISTS idx_lesson_progress_user ON lesson_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_lesson_progress_lesson ON lesson_progress(lesson_id);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_lesson ON quiz_questions(lesson_id);
CREATE INDEX IF NOT EXISTS idx_user_quiz_attempts_user ON user_quiz_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_user ON user_badges(user_id);

-- ============================================
-- Sample Data - Default Admin User
-- ============================================
-- Password: admin123 (hashed with pbkdf2_sha256)
INSERT OR IGNORE INTO users (id, name, email, hashed_password, role, xp)
VALUES (1, 'Admin User', 'admin@codedonki.com', 
        '$pbkdf2-sha256$29000$9N7bO.d8by11zlkLQcjZuw$dGE3b9kqKxRj6WGZqXqF3xXqD7kKGKJqJ7kqXqF3xA', 
        'admin', 0);

-- ============================================
-- Sample Categories
-- ============================================
INSERT OR IGNORE INTO categories (id, name, description, color, icon, slug)
VALUES 
    (1, 'Web Development', 'Learn HTML, CSS, and JavaScript fundamentals', '#3498db', 'fas fa-code', 'web-development'),
    (2, 'Python Programming', 'Master Python from basics to advanced', '#27ae60', 'fab fa-python', 'python-programming'),
    (3, 'Data Structures', 'Essential algorithms and data structures', '#e74c3c', 'fas fa-database', 'data-structures'),
    (4, 'Mobile Development', 'Build apps for iOS and Android', '#9b59b6', 'fas fa-mobile-alt', 'mobile-development');

-- ============================================
-- Sample Badges
-- ============================================
INSERT OR IGNORE INTO badges (id, name, description, icon_url, xp_threshold, color)
VALUES 
    (1, 'Beginner', 'Start your learning journey!', '🌱', 0, '#95a5a6'),
    (2, 'Explorer', 'You''re getting the hang of it!', '🔍', 100, '#3498db'),
    (3, 'Achiever', 'Making great progress!', '⭐', 250, '#f39c12'),
    (4, 'Expert', 'You''re becoming an expert!', '🏆', 500, '#e67e22'),
    (5, 'Master', 'You''ve mastered the basics!', '👑', 1000, '#9b59b6'),
    (6, 'Legend', 'Legendary skills achieved!', '💎', 2000, '#1abc9c');

-- ============================================
-- Sample Lessons for Web Development
-- ============================================
INSERT OR IGNORE INTO lessons (id, title, description, category_id, xp_min, xp_max, order_in_category, pass_threshold, slug)
VALUES 
    (1, 'Introduction to HTML', 'Learn the basics of HTML structure and tags', 1, 20, 50, 1, 70, 'introduction-to-html'),
    (2, 'CSS Fundamentals', 'Style your web pages with CSS', 1, 25, 60, 2, 70, 'css-fundamentals'),
    (3, 'JavaScript Basics', 'Get started with JavaScript programming', 1, 30, 70, 3, 70, 'javascript-basics'),
    (4, 'Responsive Design', 'Make your websites mobile-friendly', 1, 35, 80, 4, 70, 'responsive-design');

-- ============================================
-- Sample Quiz Questions for HTML Lesson
-- ============================================
INSERT OR IGNORE INTO quiz_questions (lesson_id, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
VALUES 
    (1, 'What does HTML stand for?', 
     'Hyper Text Markup Language', 
     'High Tech Modern Language', 
     'Home Tool Markup Language', 
     'Hyperlinks and Text Markup Language', 
     'A', 
     'HTML stands for Hyper Text Markup Language, which is the standard markup language for creating web pages.'),
    
    (1, 'Which HTML tag is used to define the largest heading?', 
     '<heading>', 
     '<h6>', 
     '<h1>', 
     '<head>', 
     'C', 
     'The <h1> tag defines the largest heading in HTML, with <h6> being the smallest.'),
    
    (1, 'What is the correct HTML tag for inserting a line break?', 
     '<break>', 
     '<lb>', 
     '<br>', 
     '<newline>', 
     'C', 
     'The <br> tag is used to insert a line break in HTML.');

-- ============================================
-- End of Schema
-- ============================================

