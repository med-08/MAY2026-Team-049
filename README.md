# 📚 LearnAtHome

## Application Overview

**LearnAtHome** is a modern home tuition management system designed to connect **Administrators, Tutors, Students, and Parents** through a single, user-friendly platform. The application provides dedicated dashboards for each user role, enabling efficient management of educational activities, communication, and learning progress.

The frontend is built using **Vue.js** and is fully responsive, offering a clean interface with support for both **Light** and **Dark** themes.

---

# 👥 User Roles & Dashboards

The application provides **four dedicated dashboards**, each designed to meet the requirements of a specific user role.

## 👨‍💼 Admin Dashboard

The Admin Dashboard enables administrators to manage the entire platform efficiently.

### Features

* Dashboard overview
* Student management
* Tutor management
* Parent management
* User search
* User filtering
* Block/Unblock users
* Delete users
* Analytics dashboard
* Responsive sidebar
* Light/Dark mode support
* Admin profile

---

## 👨‍🏫 Tutor Dashboard

The Tutor Dashboard helps tutors manage their teaching activities and student interactions.

### Features

* Dashboard overview
* View assigned students
* Manage upcoming sessions
* Track student progress
* Upload Study materials
* Notifications
* Profile management
* Responsive design
* Light/Dark mode support

---

## 🎓 Student Dashboard

The Student Dashboard provides students with all the tools required for their learning journey.

### Features

* Dashboard overview
* View upcoming classes
* View today's tasks
* Weekly quizzes
* Quiz results
* Learning progress
* Study materials
* Personalized study tips
* Session booking
* Notifications
* FAQ section
* Profile management
* Responsive design
* Light/Dark mode support

---

## 👨‍👩‍👧 Parent Dashboard

The Parent Dashboard allows parents to monitor their child's academic activities and tuition progress.

### Features

* Dashboard overview
* View child's progress
* Monitor upcoming sessions
* View attendance
* Track quiz performance
* Notifications
* Profile management
* Responsive design
* Light/Dark mode support

---

# 🛠️ Technologies Used

* Vue.js
* Vue Router
* Tailwind CSS
* Chart.js
* Heroicons
* Vite

---

# 🚀 Installation & Run Instructions

## Step 1: Download the Project

Download and extract the project ZIP file.

## Step 2: Open the Frontend Folder

Navigate into the extracted project directory and open the **Frontend** folder.

```bash
cd Frontend
```

## Step 3: Install Dependencies

```bash
npm install
```

## Step 4: Start the Development Server

```bash
npm run dev
```

The application will start on the local development server. Open the URL displayed in the terminal (typically `http://localhost:5173`) in your browser.

---

# 📦 Build for Production

To create a production build:

```bash
npm run build
```

---

# 📌 Notes

* This repository contains the **frontend implementation** of the LearnAtHome application.
* The application includes four separate dashboards for **Admin**, **Tutor**, **Student**, and **Parent** users.
* Each dashboard is designed with role-specific functionality and a responsive user interface.

---

# 🔧 Admin Dashboard: Backend Integration Notes

This section documents the Admin Dashboard's backend implementation and
its integration with the project's real login/session system.

## Run the backend

```bash
cd Backend
pip install -r requirements.txt
python seed.py     # creates learnathome.db and seeds roles/subjects/FAQs/demo users
python app.py       # starts the API on http://localhost:5000
```

Seeded demo accounts (from `seed.py`):

| Role   | Identifier                | Password    |
|--------|----------------------------|-------------|
| Admin  | `admin`                    | `admin123`  |
| Tutor  | `tutor@example.com`         | `tutor123`  |
| Parent | `parent@example.com`        | `parent123` |
| Student| `student@example.com`        | `student123`|

Run the backend test suite (64 tests, in-memory DB, never touches the
real `learnathome.db`):
```bash
cd Backend
python -m pytest tests/ test_db.py -v
```

## Run the frontend

```bash
cd Frontend
npm install
cp .env.example .env.local   # adjust VITE_API_BASE_URL if the backend runs elsewhere
npm run dev
```

Log in at `/login` with the seeded Admin account above (select the
"Admin" role tile). You'll land on `/admin` with the real dashboard.

## What's in the Admin Dashboard API

`Backend/admin/routes.py`, mounted at `/admin/*`, gated by the existing
`@admin_required` session decorator (`Backend/decorators.py`):

- `GET /admin/dashboard/stats`, `/admin/dashboard/analytics/*` — overview + charts
- `GET/PATCH/DELETE /admin/students*` — list/search/sort/filter, block/unblock, delete
- `GET/PATCH/DELETE /admin/parents*` — same, plus linked children
- `GET/PATCH/DELETE /admin/tutors*` — list (+ bonus block/delete, schema parity)
- `GET/PATCH /admin/approvals*` — review, approve, reject pending sign-ups
- `GET/PUT /admin/profile/me`, `PUT /admin/profile/me/password` — the logged-in admin's own profile

Full request/response spec: `Backend/api_docs.yaml` (OpenAPI 3.0).
Test suite: `Backend/tests/` (pytest; includes `test_auth_gate.py` proving
every route is actually protected).

On the frontend, every view under `Frontend/src/views/admin/*.vue` fetches
real data via `Frontend/src/services/adminApi.js` instead of the old
`Frontend/src/data/mockData.js` (no longer imported anywhere).

## Auth integration

The Admin Dashboard is plugged into the project's real login/session
system:

- All `/admin/*` routes require an authenticated session with
  `role == 'Admin'`. Unauthenticated calls get `401`; a logged-in
  non-admin gets `403`.
- Admin Profile endpoints use `/admin/profile/me` (reads identity from the
  session) rather than a client-supplied `/admin/profile/<id>`, avoiding
  an IDOR risk.
- `Frontend/src/services/apiClient.js` sends `credentials: 'include'` on
  every request so the Flask session cookie set by `POST /login` is
  attached automatically; CORS in `Backend/app.py` already allows
  credentialed requests from `http://localhost:5173`.
- `Frontend/src/views/LoginView.vue` now calls the shared
  `adminApi.login()` helper (configurable base URL) instead of a
  hardcoded `http://127.0.0.1:5000` fetch, and no longer silently
  navigates to a dashboard on a network error (that fallback bypassed
  auth entirely).
- Added a working logout button to the admin `Navbar.vue`, wired to the
  real `POST /logout`.

## Schema changes (flagged, additive only)

- `Admin` model gained `admin_name` and `email` columns — the original
  schema had no way to display an admin's name/email, which
  `AdminProfile.vue` needs. Nullable/defaulted, fully backward
  compatible; `seed.py` sets them for the default admin.
- `requirements.txt` now lists `Flask-Cors` and `PyJWT`, already used by
  `app.py`/`utils.py` but previously missing from the file.

## Known limitations / assumptions

- Tutor block/delete endpoints exist on the backend (schema parity) but
  aren't wired into `Tutors.vue`, which stays a read-only list per the
  original UI design.
- No `ON DELETE CASCADE` in the schema: deleting a parent nulls out
  linked students' `parent_id` defensively, but other dependent rows
  (e.g. `StudentSubject`, `AssignmentSubmission`) aren't cleaned up
  automatically. Flagged as a follow-up for a future migration.
- "Subjects taught" for a tutor is derived from their scheduled `Session`
  rows (no direct Tutor↔Subject table exists in the schema).
- `auth/routes.py::register` currently sets new Student/Parent accounts
  to `status='Active'` immediately, even though the model default is
  `'Pending'` and the Admin Dashboard has a full approve/reject flow.
  This is pre-existing behavior, not introduced by this merge — worth
  revisiting if new sign-ups should require admin approval.

## A bug found & fixed along the way

Searching for a literal `_` or `%` in the Students/Parents/Tutors tables
originally matched **every row** (a SQL `LIKE` wildcard bug), instead of
the expected 0 results — fixed by escaping wildcards in
`admin/helpers.py::apply_search()`. Regression tests live in
`Backend/tests/test_students.py`.
