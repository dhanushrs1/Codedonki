"""
CodeDonki – Entry Point
Thin wrapper that creates the Flask app from the factory pattern.
Run locally: python app.py
Vercel: uses wsgi.py which imports `app` from here.
"""
from backend import create_app
from backend.db import setup_database, get_db_connection

app = create_app()

if __name__ == '__main__':
    # Test DB connection and run setup on first launch
    conn = get_db_connection()
    if conn:
        print("[SUCCESS] Database connection successful!")
        conn.close()
    setup_database()
    app.run(debug=True, port=5000)