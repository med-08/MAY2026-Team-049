# 📚 LearnAtHome

### **A Modern Full-Stack Home Tuition Management Platform**

[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D?style=for-the-badge\&logo=vue.js\&logoColor=white)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge\&logo=flask)](https://flask.palletsprojects.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC?style=for-the-badge\&logo=tailwind-css\&logoColor=white)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.x-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white)](https://www.sqlite.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)

**LearnAtHome** is a full-stack home tuition management platform that connects **Students, Tutors, Parents, and Administrators** through dedicated role-based dashboards.

The platform centralizes **scheduling, learning resources, assignments, quizzes, attendance, progress tracking, communication, notifications, and online meetings** into a single ecosystem.

---

## ✨ Key Highlights

* 👥 **Four Role-Based Dashboards** — Admin, Tutor, Student, and Parent
* 📅 **Smart Scheduling** — Sessions, timetables, bookings, and meetings
* 📊 **Progress Tracking** — Student performance, attendance, and quiz results
* 📝 **Assessments** — Assignments, quizzes, and question management
* 📚 **Learning Resources** — Study materials and external resource links
* 💬 **Communication** — Role-based messaging and notifications
* 🎥 **Online Meetings** — Student-Tutor and Parent-related meeting workflows
* 🔐 **Role-Based Access Control** — Protected functionality based on user roles
* 🌓 **Modern Responsive UI** — Responsive design with Light/Dark mode

---

# 👥 Role-Based Features

## 👨‍💼 Admin Dashboard

* Platform analytics
* Student, Tutor, and Parent management
* User search and filtering
* Approve new registrations
* Block / Unblock users
* Delete users
* Profile management
* Role-based administration
* Responsive Light/Dark UI

---

## 👨‍🏫 Tutor Dashboard

* View assigned students
* Schedule and manage sessions
* Track attendance
* Create assignments
* Create quizzes and question banks
* Upload learning materials
* Track student progress
* Manage meetings
* Messaging
* Notifications
* Earnings management
* Profile management

---

## 🎓 Student Dashboard

* View upcoming classes
* View timetable
* Book sessions
* Schedule 1-on-1 meetings with tutors
* View assignments
* Submit assignments
* Attempt quizzes
* View quiz results
* Track learning progress
* Access study materials
* Personalized study tips
* Notifications
* FAQ
* Profile management

---

## 👨‍👩‍👧 Parent Dashboard

* Monitor child progress
* View attendance
* View upcoming sessions
* View schedules
* Monitor quiz performance
* View activity summaries
* Access relevant meetings
* Message tutors
* Receive notifications
* Profile management

---

# 🛠 Tech Stack

| Layer                  | Technologies                             |
| :--------------------- | :--------------------------------------- |
| **Frontend**           | Vue.js 3, Vue Router, Vite, Tailwind CSS |
| **Backend**            | Flask, Python, REST APIs                 |
| **Database**           | SQLite                                   |
| **Data Visualization** | Chart.js                                 |
| **Testing**            | Pytest                                   |
| **Icons**              | Heroicons                                |
| **API Documentation**  | OpenAPI / YAML                           |

---

# 📂 Project Structure

```text
LearnAtHome/
│
├── Backend/
│   ├── admin/
│   ├── auth/
│   ├── models/
│   ├── routes/
│   ├── tests/
│   ├── uploads/
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── api_docs.yaml
│   └── requirements.txt
│
├── Frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── services/
│   │   ├── router/
│   │   └── assets/
│   ├── public/
│   └── package.json
│
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Make sure the following are installed:

* **Python 3.10+**
* **Node.js + npm**
* **Git**

---

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/med-08/MAY2026-Team-049.git
cd MAY2026-Team-049
```

---

# 🐍 Backend Setup

## 2️⃣ Create a Virtual Environment

Navigate to the backend:

```bash
cd Backend
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

All required Python dependencies are maintained in:

```text
Backend/requirements.txt
```

---

## 4️⃣ Configure Environment Variables

If environment variables are required by the backend, create:

```text
Backend/.env
```

Use the variable names required by the current application configuration.

Example:

```env
SECRET_KEY=your_secret_key
```

> **Security:** Never commit `.env` files containing passwords, API keys, OAuth credentials, tokens, or other secrets.

For team development, maintain a safe:

```text
Backend/.env.example
```

containing placeholder values only.

---

# 🗄️ Database Initialization

LearnAtHome uses **SQLite**.

The project provides a `seed.py` script for initializing a clean database.

Run:

```bash
python seed.py
```

The script:

* Creates the database tables
* Creates the required application roles
* Creates the default subjects
* Creates the initial Admin account
* Does **not** create sample Tutor, Student, or Parent activity

### Roles Created

* Admin
* Tutor
* Parent
* Student

### Default Subjects

* English
* Mathematics
* Physics
* Science
* Chemistry
* Biology

### Default Admin Account

| Role      | Username | Password   |
| :-------- | :------- | :--------- |
| **Admin** | `admin`  | `admin123` |

> The default Admin account is intended for local development/testing. Change or remove development credentials before deploying to a production environment.

---

# ▶️ Run the Backend

From the `Backend` directory:

```bash
python app.py
```

Backend:

```text
http://localhost:5000
```

---

# 💻 Frontend Setup

Open a **new terminal**.

From the project root:

```bash
cd Frontend
```

Install dependencies:

```bash
npm install
```

---

## Frontend Environment Variables

If required by the current frontend configuration, create:

```text
Frontend/.env
```

Example:

```env
VITE_API_BASE_URL=http://localhost:5000
```

Use the actual environment variable names configured in the frontend codebase.

> Never commit sensitive `.env` values to Git.

---

## ▶️ Run the Frontend

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🔐 Authentication & Access Control

LearnAtHome uses role-based authentication and authorization.

The application provides:

* Secure login and logout
* Session-based authentication
* Role-based access control
* Protected backend routes
* Role-specific dashboards
* Authenticated API requests

New users can register through the application according to the available registration workflow.

Where applicable, registrations requiring administrative approval are reviewed through the **Admin Dashboard**.

---

# 📅 Meeting Management

LearnAtHome supports separate meeting workflows for Students, Tutors, and Parents.

## 🎓 Student → Tutor Meeting

When a **Student schedules a meeting with a Tutor**, it is treated as a private:

**Student ↔ Tutor meeting**

The Parent is **not automatically added as a participant** because the Student is associated with that Parent.

### Meeting Status

Before tutor approval:

> **Tutor approval pending**

After tutor approval:

> **Meeting scheduled with student and tutor**

The Parent:

* Is not treated as a participant
* Does not receive a Join Meeting action
* Cannot join a private Student ↔ Tutor meeting

---

## 👨‍👩‍👧 Parent Meeting

Parent-created meetings follow the Parent scheduling workflow.

The Parent is included as a participant **only when the meeting is explicitly created as a parent-involved meeting**.

The system does not infer meeting participation solely from the Student → Parent relationship.

---

# 🔄 Real-Data Integration

The implemented Student, Tutor, and Parent workflows are connected to the backend database rather than relying solely on frontend mock data.

### Student

* Dashboard
* Progress
* Sessions
* Timetable
* Assignments
* Quizzes
* Resources
* Meetings
* Notifications
* Profile

### Tutor

* Dashboard
* Students
* Schedule
* Attendance
* Assignments
* Quizzes
* Materials
* Messages
* Meetings
* Earnings
* Notifications
* Profile

### Parent

* Child information
* Overview
* Progress
* Schedule
* Meetings
* Messages
* Notifications
* Profile

The application uses the existing database structure and does not require replacing the database schema during normal development.

---

# 🔔 Notifications

Role-based notifications are generated for relevant application activities, including:

* Meeting requests
* Tutor approvals
* Scheduled meetings
* Session updates
* Messages
* Other role-specific events

Notifications are displayed according to the associated user and workflow.

---

# 📖 API Documentation

The backend API is documented using OpenAPI.

Documentation:

```text
Backend/api_docs.yaml
```

The specification documents available API endpoints, request formats, responses, and API behavior.

---

# 🧪 Testing

Run the backend test suite from the `Backend` directory:

```bash
python -m pytest tests/ test_db.py -v
```

Tests cover backend functionality including areas such as:

* Authentication
* Database behavior
* API functionality
* Role-based workflows

Keep the test suite updated whenever backend functionality changes.

---

# 🌿 Git Workflow

For new development, create a separate feature branch:

```bash
git switch -c feature/your-feature
```

Make your changes and test them locally.

Then:

```bash
git add .
git commit -m "Describe your changes"
git push -u origin feature/your-feature
```

After testing, open a Pull Request for review.

### Recommended Workflow

```text
Main / Development Branch
          │
          ├── feature/frontend-update
          │
          ├── feature/backend-update
          │
          ├── feature/meeting-update
          │
          └── feature/new-functionality
```

This keeps the stable branch protected and makes individual changes easier to review and merge.

---

# ⚠️ Development & Security Notes

* Never commit `.env` files containing secrets.
* Never commit OAuth tokens or private credentials.
* Keep `requirements.txt` synchronized with backend dependencies.
* Keep frontend and backend API contracts synchronized.
* Run backend tests after backend changes.
* Test frontend functionality after API changes.
* Use feature branches for new development.
* Do not unnecessarily reset or replace the existing database.
* Keep `.env.example` updated when new environment variables are introduced.

---

# 🤝 Contributing

1. Create a feature branch.
2. Make your changes.
3. Run the test suite.
4. Update documentation when necessary.
5. Commit your changes.
6. Push your branch.
7. Open a Pull Request.

Example:

```bash
git switch -c feature/my-feature
git add .
git commit -m "Add my feature"
git push -u origin feature/my-feature
```

---

# 💙 Built By

### **Team Synergy — Team 049**

**Indian Institute of Technology Madras**
**BS Degree Program**

---

<div align="center">

### ⭐ If you found LearnAtHome useful, consider starring the repository!

</div>
