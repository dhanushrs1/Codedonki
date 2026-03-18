"""
Database helpers for CodeDonki.
Uses PyMySQL to connect to a MySQL/MariaDB database.
Connection parameters are read from environment variables.
"""
import os
import re
import pymysql
import pymysql.cursors
from passlib.hash import pbkdf2_sha256


def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "codedonki"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            connect_timeout=10,
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


def create_slug(title):
    """Generates a URL-friendly slug from a title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-')
    return slug


def ensure_default_admin(conn):
    """Ensure the default admin user and demo user exist."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, hashed_password FROM users WHERE email = %s", ('admin@codedonki.com',))
        admin = cursor.fetchone()
        if admin is None:
            cursor.execute(
                "INSERT INTO users (id, name, email, hashed_password, role, xp) VALUES (1, 'Admin User', 'admin@codedonki.com', %s, 'admin', 0)",
                (pbkdf2_sha256.hash('admin123'),)
            )
            conn.commit()
            print("[SUCCESS] Default admin user created (email: admin@codedonki.com, password: admin123)")
        else:
            try:
                pbkdf2_sha256.verify('admin123', admin['hashed_password'])
            except ValueError:
                cursor.execute(
                    "UPDATE users SET hashed_password = %s WHERE email = %s",
                    (pbkdf2_sha256.hash('admin123'), 'admin@codedonki.com')
                )
                conn.commit()
                print("[SUCCESS] Default admin password hash repaired")

        cursor.execute("SELECT id FROM users WHERE email = %s", ('user@codedonki.com',))
        demo_user = cursor.fetchone()
        if demo_user is None:
            cursor.execute(
                "INSERT IGNORE INTO users (name, email, hashed_password, role, xp) VALUES ('Demo User', 'user@codedonki.com', %s, 'user', 0)",
                (pbkdf2_sha256.hash('user123'),)
            )
            conn.commit()
            print("[SUCCESS] Demo user created (email: user@codedonki.com, password: user123)")
        cursor.close()
    except Exception as e:
        print(f"[ERROR] Could not ensure default admin: {e}")


def setup_database():
    """Setup database tables and sample data from MySQL schema file."""
    conn = get_db_connection()
    if not conn:
        print("❌ Cannot setup database - connection failed")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN ('users','categories','lessons')"
        )
        row = cursor.fetchone()
        if row and row['cnt'] > 0:
            cursor.close()
            ensure_default_admin(conn)
            conn.close()
            print("[INFO] Database already initialized; skipping setup script.")
            return True

        # Read MySQL schema
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'database_schema_mysql.sql'
        )
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
        for statement in statements:
            try:
                cursor.execute(statement)
            except pymysql.Error as e:
                print(f"[WARN] Statement skipped: {e}")

        conn.commit()
        cursor.close()
        ensure_default_admin(conn)
        conn.close()
        print("[SUCCESS] Database setup completed successfully!")
        return True

    except Exception as e:
        print(f"[ERROR] Database setup failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
