# 📚 LearnAtHome

<div align="center">

# A Modern Home Tuition Management Platform

LearnAtHome is a full-stack web application that simplifies home tuition management by bringing **Students, Tutors, Parents, and Administrators** together on a single platform. It streamlines scheduling, progress tracking, communication, assessments, and resource management through dedicated role-based dashboards.

![Vue](https://img.shields.io/badge/Vue.js-3-42b883?logo=vue.js)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-Styled-38BDF8?logo=tailwindcss)

</div>

---

# ✨ Features

## 👨‍💼 Admin Dashboard
- Dashboard analytics
- Student, Tutor & Parent management
- User search and filtering
- Block / Unblock users
- Delete users
- Approve new registrations
- Profile management
- Responsive UI
- Light & Dark mode

---

## 👨‍🏫 Tutor Dashboard
- Manage assigned students
- Schedule sessions
- Upload study materials
- Track student progress
- Notifications
- Profile management
- Responsive UI
- Light & Dark mode

---

## 🎓 Student Dashboard
- Upcoming classes
- Weekly quizzes
- Quiz results
- Learning progress
- Study materials
- Session booking
- Personalized study tips
- Notifications
- FAQ section
- Responsive UI
- Light & Dark mode

---

## 👨‍👩‍👧 Parent Dashboard
- Child progress tracking
- Attendance monitoring
- Upcoming sessions
- Quiz performance
- Weekly summaries
- Notifications
- Profile management
- Responsive UI
- Light & Dark mode

---

# 🛠 Tech Stack

| Category | Technologies |
|-----------|--------------|
| Frontend | Vue.js 3, Vue Router, Tailwind CSS, Vite |
| Backend | Flask, Python |
| Database | SQLite |
| Charts | Chart.js |
| Icons | Heroicons |
| Testing | Pytest |

---

# 🚀 Quick Start

## Clone Repository

```bash
git clone https://github.com/med-08/MAY2026-Team-049.git
cd MAY2026-Team-049
```

---

## Backend Setup

### Create Virtual Environment and Enter inside backend folder

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

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Seed Database

```bash
python seed.py
```

This creates:

- `learnathome.db`
- Demo users
- Roles
- Subjects
- FAQs

### Run Backend

```bash
python app.py
```

Backend runs at

```
http://localhost:5000
```

---

## Frontend Setup

```bash
cd Frontend

npm install

```

Update

```
VITE_API_BASE_URL
```

if required.

Run

```bash
npm run dev
```

Frontend runs at

```
http://localhost:5173
```

---

# 🔐 Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin@Learnathome.com | admin123 |
| Tutor | tutor@example.com | tutor123 |
| Student | student@example.com | student123 |
| Parent | parent@example.com | parent123 |

> Select the appropriate role on the login page after entering the credentials.

---

# 🧪 Running Tests

Run the backend test suite:

```bash
cd Backend

python -m pytest tests/ test_db.py -v
```

✔ 64 automated tests

✔ Uses an in-memory database

✔ Never modifies `learnathome.db`

---

# 📖 API Documentation

OpenAPI Specification:

```
Backend/api_docs.yaml
```

---

# 📂 Project Structure

```
LearnAtHome
│
├── Backend
│   ├── admin
│   ├── auth
│   ├── models
│   ├── routes
│   ├── tests
│   ├── app.py
│   ├── seed.py
│   ├── api_docs.yaml
│   └── requirements.txt
│
├── Frontend
│   ├── src
│   │   ├── components
│   │   ├── views
│   │   ├── services
│   │   ├── router
│   │   └── assets
│   ├── public
│   └── package.json
│
└── README.md
```

---

# 🔒 Authentication

- Session-based authentication
- Role-based access control
- Protected Admin APIs
- Secure login & logout
- Credentials automatically included with API requests

---

# 🌟 Highlights

- Four dedicated dashboards
- Role-based authorization
- Responsive design
- Light & Dark theme
- RESTful API architecture
- Real backend integration
- Search & filtering
- Analytics dashboard
- Comprehensive test suite
- OpenAPI documentation

---

# ⚠ Known Limitations

- Tutor management UI is currently read-only.
- Subjects taught are derived from scheduled sessions.
- No cascade deletion for dependent records.

---

# 🤝 Contributing

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature/your-feature
```

3. Commit your changes

```bash
git commit -m "Add your feature"
```

4. Push the branch

```bash
git push origin feature/your-feature
```

5. Open a Pull Request

---

# 💙 Built By

**Team Synergy (Team-049)**

Indian Institute of Technology Madras  
BS Degree Program

---

## ⭐ If you found this project useful, don't forget to star the repository!
