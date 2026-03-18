"""
Page-rendering routes (HTML pages served by Flask templates).
"""
from flask import Blueprint, redirect, url_for, render_template, request

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def home_page():
    return render_template('home.html')


@pages_bp.route('/auth', methods=['GET'])
def auth_page():
    return render_template('auth.html')


@pages_bp.route('/lessons')
def lessons_page():
    category_id = request.args.get('category_id')
    if not category_id:
        return redirect(url_for('pages.archive_page'))
    return render_template('lessons.html')


@pages_bp.route('/lesson')
def lesson_page():
    lesson_id = request.args.get('id')
    lesson_slug = request.args.get('slug')
    if not lesson_id and not lesson_slug:
        return redirect(url_for('pages.archive_page'))
    return render_template('lesson.html')


@pages_bp.route('/quiz')
def quiz_page():
    lesson_id = request.args.get('lesson_id')
    if not lesson_id:
        return redirect(url_for('pages.archive_page'))
    return render_template('quiz.html')


@pages_bp.route('/leaderboard')
def leaderboard_page():
    return render_template('leaderboard.html')


@pages_bp.route('/games')
def games_page():
    return render_template('games.html')


@pages_bp.route('/profile')
def profile_page():
    return render_template('profile.html')


@pages_bp.route('/archive')
def archive_page():
    return render_template('archive.html')


@pages_bp.route('/archive.html')
def archive_html_redirect():
    return redirect(url_for('pages.archive_page'))


@pages_bp.route('/admin')
def admin_panel():
    return render_template('admin/index.html')


@pages_bp.route('/admin/lessons')
def admin_lessons():
    return render_template('admin/lessons.html')


@pages_bp.route('/admin/quiz')
def admin_quiz():
    return render_template('admin/quiz.html')


@pages_bp.route('/admin/categories')
def admin_categories():
    return render_template('admin/categories.html')


@pages_bp.route('/admin/badges')
def admin_badges():
    return render_template('admin/badges.html')


@pages_bp.route('/admin/users')
def admin_users():
    return render_template('admin/users.html')


@pages_bp.route('/admin/media')
def admin_media():
    return render_template('admin/media.html')
