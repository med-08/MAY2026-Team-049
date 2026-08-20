# 📚 LearnAtHome

### A Modern Home Tuition Management Platform

LearnAtHome is a full-stack home tuition management platform connecting **Students, Tutors, Parents, and Administrators** through role-based dashboards.

**Vue.js 3 · Flask · Python · SQLite · Tailwind CSS · REST APIs · Google Meet · AI**

---

# ✨ Features

## 👨‍💼 Admin Dashboard

* Dashboard analytics
* Student, Tutor & Parent management
* Search & filtering
* Block / Unblock users
* Delete users
* Registration approval
* Profile management
* Responsive UI
* Light / Dark mode

## 👨‍🏫 Tutor Dashboard

* Assigned student management
* Session scheduling
* Subject-based sessions
* Attendance management
* Assignments
* Quizzes & quiz questions
* Study material upload/delete
* FAQs & doubts
* Tutor–Parent messaging
* Notifications
* Google Meet meetings
* Meeting start/end & duration tracking
* Earnings
* Profile management
* Responsive UI
* Light / Dark mode

## 🎓 Student Dashboard

* Upcoming sessions
* Subject-based session filtering
* Session booking
* Google Meet join option
* Meeting notifications
* Weekly quizzes
* Quiz submission & results
* Learning progress
* Assignments
* Study materials
* Resource sharing date
* Personalized study tips
* FAQs
* Profile & registered subjects
* Notifications
* Responsive UI
* Light / Dark mode

## 👨‍👩‍👧 Parent Dashboard

* Child profile
* Child progress tracking
* Attendance monitoring
* Quiz performance
* Upcoming sessions
* Curriculum
* Tutor–Parent messaging
* Meeting requests
* Meeting approval/status
* Google Meet join option
* Notifications
* Profile management
* Responsive UI
* Light / Dark mode

---

# 🎥 Google Meet Integration

Online sessions are integrated with Google Meet.

* Tutor can start/end online meetings
* Meeting links are available to relevant students
* Students receive meeting notifications
* Students can join active sessions
* Meeting duration is tracked from start to end
* Parent–Tutor meeting requests are supported
* Approved meetings provide meeting details to both sides

Google OAuth credentials are required for Google Meet functionality.

---

# 🤖 AI-Assisted Features

* AI-generated quizzes
* AI-generated flashcards
* AI-assisted FAQ / question answering
* AI-assisted learning insights

---

# 🔗 Real-Data Integration

Student, Tutor and Parent workflows use the **existing SQLite database** instead of frontend mock data.

Tutor-created content is connected to students through existing:

* Subjects
* StudentSubject
* Sessions
* SessionBooking
* Assignments
* Quizzes
* Resources
* Attendance
* Meetings
* Messages
* Notifications

**No database reset or seed operation is required.**

---

# 🛠 Tech Stack

| Category      | Technologies              |
| ------------- | ------------------------- |
| Frontend      | Vue.js 3, Vue Router      |
| Styling       | Tailwind CSS              |
| Build Tool    | Vite                      |
| Backend       | Flask, Python             |
| Database      | SQLite                    |
| Charts        | Chart.js                  |
| Icons         | Heroicons                 |
| Testing       | Pytest                    |
| API           | REST APIs                 |
| Documentation | OpenAPI / Swagger         |
| Meetings      | Google Meet               |
| AI            | AI-assisted learning APIs |

---

# 🚀 Quick Start

## Clone Repository

```bash
git clone https://github.com/med-08/MAY2026-Team-049.git
cd MAY2026-Team-049
```

## Backend

### Windows

```bash
python -m venv venv
venv\Scripts\activate
cd Backend
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
cd Backend
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run backend:

```bash
python app.py
```

Backend:

```text
http://localhost:5000
```

### Database

The project uses the **existing SQLite database**.

**No `seed.py` or database reset is required.**

---

# 🎨 Frontend

```bash
cd Frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

The frontend uses the configured:

```text
VITE_API_BASE_URL
```

Default backend:

```text
http://localhost:5000
```

---

# 🎥 Google Meet Setup

Google Meet functionality requires Google API/OAuth configuration.

Configure the required Google credentials before using:

* Online class meetings
* Tutor meeting start/end
* Parent–Tutor meetings
* Meeting links

Google credentials/tokens must **not** be committed to the repository.

If an OAuth token expires or is revoked, Google authorization must be completed again.

---

# 🧪 Running Tests

From `Backend`:

```bash
python -m pytest tests/ test_db.py -v
```

Current test suite:

* **64 automated tests**
* Pytest
* Isolated/in-memory database testing
* Main SQLite database is not modified by the test suite

---

# 📖 API Documentation

OpenAPI specification:

```text
Backend/api_docs.yaml
```

API coverage includes:

* Authentication
* Admin
* Student
* Tutor
* Parent
* Sessions
* Bookings
* Assignments
* Quizzes
* Resources
* Attendance
* Meetings
* Messages
* Notifications
* Progress
* AI-assisted features

---

# 📂 Project Structure

```text
MAY2026-Team-049/
│
├── Backend/
│   ├── admin/
│   ├── auth/
│   ├── models/
│   ├── routes/
│   ├── tests/
│   ├── uploads/
│   ├── app.py
│   ├── models.py
│   ├── google_meet.py
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

# 🔐 Authentication

* Session-based authentication
* Role-based access control
* Protected APIs
* Secure login/logout
* Authenticated API requests

Supported roles:

```text
Admin
Tutor
Student
Parent
```

---

# 🌟 Highlights

* Four role-based dashboards
* Real database integration
* RESTful API architecture
* Subject-based student sessions
* Session booking
* Assignments & quizzes
* Progress tracking
* Study resources
* Attendance
* Notifications
* Tutor–Parent communication
* Google Meet integration
* Online meeting management
* AI-assisted learning
* OpenAPI documentation
* Automated testing
* Responsive UI
* Light / Dark mode

---

# ⚠️ Known Limitations

* Tutor management UI is currently read-only where applicable.
* Subjects taught are derived from scheduled sessions.
* No cascade deletion for all dependent records.
* Google Meet requires valid Google OAuth credentials.
* Uploaded resources are stored locally under `Backend/uploads/`.

---

# 🤝 Contributing

```bash
git checkout -b feature/your-feature
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

Then open a Pull Request.

---

# 👥 Team

**Team Synergy — Team-049**

**Indian Institute of Technology Madras**

**BS Degree Program**

---

⭐ If you found LearnAtHome useful, don't forget to star the repository!
