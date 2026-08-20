# 📚 LearnAtHome

### A Modern Home Tuition Management Platform

LearnAtHome is a full-stack home tuition management platform connecting **Students, Tutors, Parents, and Administrators** through role-based dashboards.

**Vue.js 3 · Flask · Python · SQLite · Tailwind CSS · REST APIs · Google Meet · AI**

---

## ✨ Features

| 👨‍💼 **Admin**         | 👨‍🏫 **Tutor**       |
| ----------------------- | --------------------- |
| • Dashboard analytics   | • Student management  |
| • Student management    | • Session scheduling  |
| • Tutor management      | • Attendance          |
| • Parent management     | • Assignments         |
| • Search & filtering    | • Quizzes & questions |
| • Block / Unblock users | • Study materials     |
| • Delete users          | • FAQs & doubts       |
| • Registration approval | • Messages            |
| • Profile management    | • Notifications       |
| • Responsive UI         | • Google Meet         |
| • Light / Dark mode     | • Earnings & profile  |

| 🎓 **Student**            | 👨‍👩‍👧 **Parent**   |
| ------------------------- | --------------------- |
| • Upcoming sessions       | • Child profile       |
| • Subject-based sessions  | • Progress tracking   |
| • Session booking         | • Attendance          |
| • Google Meet joining     | • Quiz performance    |
| • Weekly quizzes          | • Upcoming sessions   |
| • Quiz results            | • Curriculum          |
| • Learning progress       | • Tutor messaging     |
| • Assignments             | • Meeting requests    |
| • Study materials         | • Meeting status      |
| • Personalized study tips | • Google Meet joining |
| • FAQs                    | • Notifications       |
| • Notifications           | • Profile management  |
| • Registered subjects     | • Responsive UI       |

---

## 🎥 Google Meet

* Online tutoring sessions
* Tutor start / end meeting
* Automatic meeting link availability
* Student **Join Meeting** option
* Meeting-start notifications
* Meeting duration tracking
* Parent–Tutor meeting requests
* Meeting approval and status
* Parent and Tutor meeting access

> Google API / OAuth credentials are required for Google Meet functionality.

---

## 🤖 AI Features

* AI-generated quizzes
* AI-generated flashcards
* AI-assisted FAQ / question answering
* AI-assisted learning insights

---

## 🔗 Real-Data Integration

The implemented workflows use the **existing SQLite database** instead of frontend mock data.

| Area          | Database Integration                                |
| ------------- | --------------------------------------------------- |
| Students      | Profile, subjects, sessions, bookings, progress     |
| Tutors        | Students, sessions, assignments, quizzes, resources |
| Parents       | Child relationship, progress, sessions, meetings    |
| Sessions      | Subjects, bookings, meeting information             |
| Learning      | Assignments, quizzes, resources, progress           |
| Communication | Messages, meetings, notifications                   |

**No database reset or `seed.py` execution is required.**

---

## 🛠 Tech Stack

| Category      | Technologies              |
| ------------- | ------------------------- |
| Frontend      | Vue.js 3, Vue Router      |
| Styling       | Tailwind CSS              |
| Build         | Vite                      |
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

### 1. Clone

```bash
git clone https://github.com/med-08/MAY2026-Team-049.git
cd MAY2026-Team-049
```

### 2. Backend

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
cd Backend
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
cd Backend
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python app.py
```

Backend:

```text
http://localhost:5000
```

### 3. Database

The application uses the **existing SQLite database**.

```text
No seed.py
No database reset
No schema replacement
```

### 4. Frontend

```bash
cd Frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Default API:

```text
VITE_API_BASE_URL=http://localhost:5000
```

---

# 🎥 Google Meet Configuration

Google Meet requires Google API/OAuth configuration.

Configure the required credentials before using:

* Online class meetings
* Meeting start/end
* Parent–Tutor meetings
* Meeting links

**Do not commit Google credentials, tokens, API keys, or secrets to Git.**

---

# 🧪 Testing

Run backend tests:

```bash
cd Backend
python -m pytest tests/ test_db.py -v
```

### Current Test Suite

| Item      | Details                |
| --------- | ---------------------- |
| Framework | Pytest                 |
| Tests     | **64 automated tests** |
| Database  | Isolated / in-memory   |
| Main DB   | Not modified by tests  |

---

# 📖 API Documentation

OpenAPI specification:

```text
Backend/api_docs.yaml
```

### API Areas

| Module         | Coverage                                   |
| -------------- | ------------------------------------------ |
| Authentication | Login, logout, sessions                    |
| Admin          | User management & approvals                |
| Student        | Dashboard, progress, quizzes, sessions     |
| Tutor          | Students, sessions, assignments, materials |
| Parent         | Child progress, schedule, meetings         |
| Communication  | Messages & notifications                   |
| Meetings       | Google Meet & meeting requests             |
| Learning       | Assignments, quizzes, resources            |
| AI             | AI-assisted learning features              |

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
* Secure login / logout
* Authenticated API requests

### Supported Roles

**Admin · Tutor · Student · Parent**

---

# 🌟 Key Highlights

| 📌 Platform               | 📚 Learning       | 🎥 Communication |
| ------------------------- | ----------------- | ---------------- |
| Role-based dashboards     | Assignments       | Google Meet      |
| Real database integration | Quizzes           | Meeting requests |
| REST APIs                 | Progress tracking | Messages         |
| Responsive UI             | Study resources   | Notifications    |
| Light / Dark mode         | Attendance        | Session updates  |
| Search & filtering        | AI features       | Meeting duration |

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

Open a Pull Request after pushing your branch.

---

# 👥 Team

### Team Synergy — Team-049

**Indian Institute of Technology Madras**
**BS Degree Program**

---

⭐ **If you found LearnAtHome useful, don't forget to star the repository!**
