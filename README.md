# Smart Civic Tracker

**Citizen-Centric Civic Issue Reporting and Resolution Platform**

A full-stack web app where citizens report civic issues (potholes, garbage, drainage, streetlights) with a photo and a map-pinned location, and admins verify, prioritize and resolve them through an audited workflow. Deployed on AWS EC2.

## Features

**Citizen:** register/login, report issues with photo and map location, track status on a timeline, reopen unresolved complaints, give feedback, receive notifications, edit profile.

**Admin:** analytics dashboard, search and filter complaints, change category/priority/status, map view, duplicate warnings, user list.

## Smart Features

- **Duplicate detection:** flags complaints in the same category, within about 300 m, with similar text (it only warns, never deletes)
- **Priority recommendation:** combines severity with category-based rules
- **Validated workflow:** 8 statuses with enforced transitions and a full history log

## Tech Stack

Python, Flask, MySQL/MariaDB, HTML/CSS/JavaScript, Bootstrap, Leaflet.js, Chart.js, gunicorn, Nginx, AWS EC2

## Run Locally

1. Import `schema.sql` into MySQL
2. `pip install flask flask-cors mysql-connector-python python-dotenv werkzeug`
3. Copy `.env.example` to `.env` and fill in your database details
4. Run `cd backend && python app.py`
5. Run `cd frontend && python -m http.server 5500`, then open `http://127.0.0.1:5500`

To create an admin, register normally and set `role = 'admin'` for that user in the database.

## Security

Hashed passwords, session-based auth, role-based access control, parameterized SQL, input validation, and validated image uploads.

## Author

[Your Name] | [GitHub link] | [LinkedIn link]
