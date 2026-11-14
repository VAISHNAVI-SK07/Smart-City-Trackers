Smart Civic Tracker

Citizen-Centric Civic Issue Reporting and Resolution Platform

A full-stack web app where citizens report civic issues (potholes, garbage, blocked drains, broken streetlights) with a photo and a map-pinned location, and administrators verify, prioritize and resolve them through an audited workflow. Built as a final-year engineering project and deployed on AWS EC2.

Features

Citizen

Register, log in, edit profile
Report an issue with photo, category, severity and map location
Track every complaint on a status timeline
Reopen unresolved complaints and leave a rating after resolution
In-app notifications on every status change

Admin

Analytics dashboard (totals, by category, by status, by month, average resolution time)
Search and filter complaints; change category, priority and status
Duplicate warnings, interactive complaint map, user list

Pages

Page	What it does
Landing page	Introduces the platform and links to register and log in
Register / Log in	Creates a citizen account or signs in; users are sent to the right dashboard for their role
Citizen dashboard	Shows total, pending, resolved and reopened counts, the user's complaints, and a notification bell
Report issue	Form for title, description, category, severity and photo, with a map to pin the location
Complaint details	Shows the complaint, its photo, the status timeline, and options to reopen it or leave feedback
Profile	Lets a citizen update their name, phone and address
Admin dashboard	Shows summary cards and charts by category, status and month, plus average resolution time
All complaints	Searchable, filterable list; the Manage window changes category, priority and status, and shows duplicate warnings
Map view	Plots complaints on a map, coloured by priority, with filters
Users	Read-only list of registered users and how many complaints each has filed


Tech Stack
Layer	Technology
Frontend	HTML, CSS, JavaScript, Bootstrap 5, Leaflet.js (OpenStreetMap), Chart.js
Backend	Python, Flask, Flask-CORS
Database	MySQL / MariaDB
Auth	Server-side sessions, hashed passwords (werkzeug.security)
Deployment	AWS EC2 (Ubuntu), Nginx, gunicorn, systemd

How It Works
Browser -> Nginx -> gunicorn -> Flask (routes -> services -> models) -> MySQL / MariaDB


Smart Features

Rule-based and explainable, with no black-box model.

Duplicate detection: flags a complaint when another open one has the same category, is within about 300 m, and has similar text (title or description at 40% or more, using character and word-overlap matching). It only warns and never deletes, so an admin decides.
Priority recommendation: starts from the reported severity, then applies category rules (for example, drainage is never below High). Admins can override it.
Audit trail: every status change is stored with who, when and remarks.
Database

Five tables: users, complaints, complaint_status_history, feedback and notifications. See schema.sql.

API Overview
Group	Endpoints
Auth	POST /api/register, POST /api/login, POST /api/logout, GET /api/me, GET/PUT /api/profile
Citizen	POST /api/complaints, GET /api/complaints/my, GET /api/complaints/<id>, PUT /api/complaints/<id>/reopen, POST /api/complaints/<id>/feedback
Notifications	GET /api/notifications, PUT /api/notifications/<id>/read
Admin	GET /api/admin/complaints, GET /api/admin/complaints/<id>, GET /api/admin/complaints/<id>/duplicates, PUT /api/admin/complaints/<id>/status, PUT .../priority, PUT .../category, GET /api/admin/analytics, GET /api/admin/users
Project Structure
smart-civic-tracker/
├── backend/
│   ├── app.py, config.py
│   ├── routes/     # HTTP endpoints
│   ├── services/   # duplicate detection, priority rules
│   ├── models/     # SQL queries
│   └── utils/      # DB connection, auth, validators, uploads
├── frontend/       # HTML pages, css/, js/api.js
├── schema.sql
├── requirements.txt
└── .env.example
Run Locally
Import the schema: mysql -u root -p < schema.sql
Install packages: pip install flask flask-cors mysql-connector-python python-dotenv werkzeug
Copy .env.example to .env and fill in your database details.
Start the backend: cd backend && python app.py
Start the frontend: cd frontend && python -m http.server 5500, then open http://127.0.0.1:5500

To create an admin, register normally, then run UPDATE users SET role = 'admin' WHERE email = 'you@example.com'; in the database. Admin creation is deliberately not exposed through the website.

Deployment

Runs on a single AWS EC2 Ubuntu instance:

Nginx serves the frontend and forwards /api and /uploads to the backend
gunicorn runs the Flask app, managed by systemd so it restarts automatically
MariaDB hosts the database on the same instance
A security group acts as the firewall, and all secrets live in .env

Because configuration comes from .env, moving the database to AWS RDS only needs a settings change.

Security

Hashed passwords, session-based authentication and role-based access control
Citizens can only access their own complaints; registration always creates a citizen
Parameterized SQL, input validation, and HTML escaping of user text
Image uploads limited by extension and a 5 MB cap, saved under random names


Limitations and Future Work

No HTTPS yet, so the browser's "current location" button is unavailable on the deployed site (map pinning works)
Duplicate detection compares words rather than meaning, and needs a map location
Next steps: AWS RDS and S3, HTTPS, haversine distance and text embeddings, email/SMS notifications, pagination
