"""
WSGI entry point for Vercel and other WSGI hosts.
Vercel's Python runtime expects a module-level `app` object.
"""
from app import app

# Vercel uses this `app` variable
