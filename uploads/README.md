# Uploads Directory

This directory contains user-uploaded content and static assets for the CodeDonki platform.

## Directory Structure

```
uploads/
├── badges/          # Badge images uploaded by admins
├── avatars/         # User profile pictures (ignored by git)
├── lessons/         # User-uploaded lesson HTML files (ignored by git)
└── *.svg           # Platform assets (logos, illustrations)
```

## Important Notes

- **User-generated content** (lesson files, avatars, badges with timestamps) is excluded from version control via `.gitignore`
- **Static assets** (SVG logos, default images) are tracked in Git
- The directory structure is preserved using `.gitkeep` files
- Uploaded files are named with timestamps to prevent conflicts

## Default Assets Included

- `codedonki-logo.svg` - Platform logo (light theme)
- `codedonki-logo-dark.svg` - Platform logo (dark theme)
- `sleeping_hero.svg` - Hero image for homepage
- `AR_Integration.svg` - AR feature illustration
- `Interactive_Learning.svg` - Interactive learning illustration
- `Gamified_Experience.svg` - Gamification illustration
- `profile.png` - Default profile picture

## File Naming Convention

### Admin Uploads
- Lessons: `lesson_{lesson_id}_{timestamp}.html`
- Badges: `badge_{badge_name}_{timestamp}.png`
- Avatars: `avatar_{user_id}_{timestamp}.jpg`

All uploaded files are automatically renamed by the backend to prevent filename conflicts.

