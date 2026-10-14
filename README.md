# 🎓 EduLearn - Full-Stack Educational Platform

A comprehensive, production-ready educational website built with **Python 3**, **Django 6**, and modern **Tailwind CSS**.

---

## 🌟 Key Features

### 1. 🧑‍🎓 Student Experience
- **Explore & Filter Catalog**: Search courses by keywords, filter by category, difficulty level (Beginner, Intermediate, Advanced), or price (Free/Paid).
- **One-Click Enrollment**: Fast enrollment into any course.
- **Interactive Course Player**:
  - Distraction-free video lectures (YouTube/Vimeo responsive embeds) and rich reading notes.
  - Interactive syllabus sidebar showing real-time lesson progress checkmarks.
  - Mark lessons as complete or resume where left off.
  - Discussion forum & Q&A under every lesson with instructor replies.
- **Self-Grading Quizzes**:
  - Multiple-choice assessments with instant automated scoring.
  - Passing thresholds, pass/fail badges, and detailed question-by-question explanations.
  - Attempt history tracking.
- **Student Dashboard**: Real-time progress bars, enrolled courses, completed certificates, and quiz attempt scores.

### 2. 👨‍🏫 Instructor Studio
- **Instructor Dashboard**: Overview of created courses, student enrollment metrics, and lesson count.
- **Curriculum Builder**:
  - Create and edit courses with custom cover banners, levels, and pricing.
  - Add modules/chapters in sequence.
  - Add lessons (video lectures, rich text notes, code blocks, free preview toggle).
- **Course Discussion Feedback**: Reply to student questions directly within lessons.

### 3. ⚙️ Platform & Admin
- **Custom User Model**: Roles for `Student`, `Instructor`, and `Administrator`.
- **Django Admin**: Full management for categories, courses, lessons, quizzes, discussions, and enrollments.
- **Pre-populated Seed Data**: Instant demo dataset with realistic courses, lessons, quizzes, and demo accounts.

---

## 🚀 Quick Start Guide

### 1. Activate the Virtual Environment
Open PowerShell or your terminal in this directory:
```powershell
# Navigate to project
cd C:\Users\VIVEK\.gemini\antigravity\scratch\academy_portal

# Activate Virtual Environment
.\venv\Scripts\activate
```

### 2. Run Database Migrations (Already configured)
```powershell
python manage.py migrate
```

### 3. Seed Sample Content & Demo Accounts
```powershell
python manage.py seed_edu_data
```

### 4. Start the Development Server
```powershell
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser!

---

## 🔑 Demo Account Credentials

| Role | Username | Password | Notes |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Django Admin access at `/admin/` |
| **Instructor** | `sarah_dev` | `instructor123` | Course author & studio access |
| **Instructor** | `alex_ai` | `instructor123` | AI course author |
| **Student** | `john_student` | `student123` | Enrolled in courses with active progress |

*You can also register a brand new Student or Instructor account via the **Sign Up** page.*

---

## 📁 Project Architecture

```
academy_portal/
│
├── config/                      # Core Django configuration
│   ├── settings.py              # Settings, Auth User, Installed Apps
│   ├── urls.py                  # Root URL dispatcher
│   └── wsgi.py
│
├── core/                        # Authentication & Dashboard App
│   ├── models.py                # Custom User model with roles
│   ├── forms.py                 # Registration, login, profile forms
│   ├── views.py                 # Home, auth, student & instructor dashboards
│   ├── urls.py
│   └── management/commands/     # seed_edu_data command
│
├── courses/                     # Course & Curriculum App
│   ├── models.py                # Category, Course, Module, Lesson, Enrollment, Review
│   ├── forms.py                 # Course, Module, Lesson, Discussion forms
│   ├── views.py                 # Catalog, detail, learning room, progress toggling
│   ├── urls.py
│   └── tests.py                 # Automated unit and integration test suite
│
├── quizzes/                     # Interactive Assessment App
│   ├── models.py                # Quiz, Question, AnswerChoice, QuizAttempt
│   ├── views.py                 # Quiz instructions, interactive test, results breakdown
│   └── urls.py
│
├── templates/                   # Clean Tailwind CSS UI Templates
│   ├── base.html                # Responsive layout with modern navbar & footer
│   ├── core/                    # Home, login, register, dashboard, profile
│   ├── courses/                 # Catalog, detail, learning room player, instructor studio
│   └── quizzes/                 # Quiz taker & score breakdown
│
└── static/                      # Custom stylesheets and scripts
```
"# Edulearn-" 
