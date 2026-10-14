from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from courses.models import Category, Course, Module, Lesson, Enrollment, LessonProgress, Discussion, Review
from quizzes.models import Quiz, Question, AnswerChoice, QuizAttempt, StudentAnswer

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds realistic educational platform sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding EduLearn database..."))

        # 1. Create Users
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Manager',
                'email': 'admin@edulearn.org',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'headline': 'Platform Lead Administrator',
                'bio': 'System administrator maintaining the EduLearn educational infrastructure.',
            }
        )
        admin.set_password('admin123')
        admin.save()

        instructor_sarah, _ = User.objects.get_or_create(
            username='sarah_dev',
            defaults={
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'email': 'sarah@edulearn.org',
                'role': User.ROLE_INSTRUCTOR,
                'headline': 'Staff Python & Django Engineer | Ex-Stripe',
                'bio': '10+ years engineering scalable backend systems in Python and Django. Passionate about teaching clean code architecture and developer ergonomics.',
                'avatar_url': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=300&auto=format&fit=crop',
            }
        )
        instructor_sarah.set_password('instructor123')
        instructor_sarah.save()

        instructor_alex, _ = User.objects.get_or_create(
            username='alex_ai',
            defaults={
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'email': 'alex@edulearn.org',
                'role': User.ROLE_INSTRUCTOR,
                'headline': 'Lead AI Research Engineer & Deep Learning Instructor',
                'bio': 'Specializing in computer vision, PyTorch, generative models, and applied data pipelines.',
                'avatar_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=300&auto=format&fit=crop',
            }
        )
        instructor_alex.set_password('instructor123')
        instructor_alex.save()

        student_john, _ = User.objects.get_or_create(
            username='john_student',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@student.edu',
                'role': User.ROLE_STUDENT,
                'headline': 'Aspiring Full-Stack Software Developer',
                'bio': 'Learning modern web engineering with Django, JavaScript, and Tailwind CSS.',
                'avatar_url': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=300&auto=format&fit=crop',
            }
        )
        student_john.set_password('student123')
        student_john.save()

        self.stdout.write(self.style.SUCCESS("Users created (admin, sarah_dev, alex_ai, john_student)."))

        # 2. Create Categories
        cat_python, _ = Category.objects.get_or_create(
            name='Python & Backend',
            defaults={
                'slug': 'python-backend',
                'icon': 'fa-brands fa-python',
                'description': 'Master Python 3, Django, REST APIs, databases, and microservices architecture.',
            }
        )

        cat_web, _ = Category.objects.get_or_create(
            name='Full-Stack Web',
            defaults={
                'slug': 'full-stack-web',
                'icon': 'fa-solid fa-code',
                'description': 'Modern web development with HTML5, CSS3, Tailwind CSS, JavaScript, and Django.',
            }
        )

        cat_ai, _ = Category.objects.get_or_create(
            name='AI & Data Science',
            defaults={
                'slug': 'ai-data-science',
                'icon': 'fa-solid fa-brain',
                'description': 'Machine learning, deep neural networks, PyTorch, Pandas, and data visualization.',
            }
        )

        cat_cloud, _ = Category.objects.get_or_create(
            name='Cloud & DevOps',
            defaults={
                'slug': 'cloud-devops',
                'icon': 'fa-solid fa-cloud',
                'description': 'Docker, CI/CD pipelines, Linux servers, PostgreSQL, and production hosting.',
            }
        )

        # 3. Create Course 1: Full-Stack Python & Django Mastery
        course1, _ = Course.objects.get_or_create(
            slug='full-stack-python-django-mastery',
            defaults={
                'title': 'Full-Stack Python & Django Mastery: From Zero to SaaS',
                'subtitle': 'Build real-world production web applications with Django 6, modern database models, user auth, and responsive UI.',
                'description': """Welcome to the most practical and comprehensive Django engineering course available!

In this masterclass, you will build full-scale, scalable web applications from absolute scratch. We skip superficial toy examples and dive directly into industry architectural standards used by leading tech organizations:

• High-performance Django ORM queries and indexing
• Custom Authentication systems and role-based permissions
• Clean modular templates with Tailwind CSS and responsive design
• Interactive quizzes and assessment pipelines
• Production deployment best practices and security hardening

Whether you are transition from beginner Python scripts or looking to craft complete production software, this course will guide you every single step of the way.""",
                'category': cat_python,
                'instructor': instructor_sarah,
                'level': Course.LEVEL_BEGINNER,
                'price': 0.00,
                'thumbnail_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=800&auto=format&fit=crop',
                'is_published': True,
                'featured': True,
            }
        )

        # Module 1 for Course 1
        m1, _ = Module.objects.get_or_create(
            course=course1,
            order=1,
            defaults={
                'title': 'Python Fundamentals & Environment Setup',
                'description': 'Setting up your development tools, virtual environments, and mastering core syntax.',
            }
        )

        l1, _ = Lesson.objects.get_or_create(
            module=m1,
            order=1,
            defaults={
                'title': '1. Welcome & Setting Up Python 3 Development Environment',
                'lesson_type': Lesson.TYPE_VIDEO,
                'video_url': 'https://www.youtube.com/watch?v=kqtD5dpn9C8',
                'duration_minutes': 12,
                'is_preview': True,
                'content': """### Overview

Welcome to the course! In this introductory lesson, we configure our development environment for Python.

#### Key Highlights:
1. Installing Python 3.13 and verifying via `python --version`
2. Setting up dedicated virtual environments:
   ```bash
   python -m venv venv
   # Windows Activation
   .\\venv\\Scripts\\activate
   ```
3. Understanding `pip` package manager and dependencies management with `requirements.txt`.

Ensure your environment is ready before proceeding to the next lesson!""",
            }
        )

        l2, _ = Lesson.objects.get_or_create(
            module=m1,
            order=2,
            defaults={
                'title': '2. Object-Oriented Programming (OOP) in Python',
                'lesson_type': Lesson.TYPE_ARTICLE,
                'duration_minutes': 18,
                'is_preview': True,
                'content': """### Object-Oriented Architecture

Django is fundamentally built around Object-Oriented principles. Let's inspect class inheritance, properties, and magic methods.

```python
class Student:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self._enrolled_courses = []

    def enroll(self, course_name: str):
        self._enrolled_courses.append(course_name)
        print(f"{self.name} enrolled in {course_name}")

    @property
    def total_courses(self) -> int:
        return len(self._enrolled_courses)
```

#### Key Concepts:
- Encapsulation through private attributes (`_attribute`)
- Custom `@property` getters
- Inheritance and polymorphism applied in Django Model classes.""",
            }
        )

        # Module 2 for Course 1
        m2, _ = Module.objects.get_or_create(
            course=course1,
            order=2,
            defaults={
                'title': 'Django Architecture, Models & Migrations',
                'description': 'Deep dive into Model-View-Template (MVT) architecture and database schemas.',
            }
        )

        l3, _ = Lesson.objects.get_or_create(
            module=m2,
            order=1,
            defaults={
                'title': '3. Mastering the Django ORM & Database Relationships',
                'lesson_type': Lesson.TYPE_VIDEO,
                'video_url': 'https://www.youtube.com/watch?v=F5mRW0jo-Uo',
                'duration_minutes': 24,
                'is_preview': False,
                'content': """### Django ORM Schema Design

Django provides a high-level Object-Relational Mapper (ORM) that enables you to interact with your database using pure Python objects.

```python
from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

#### Migrations Workflow:
- `python manage.py makemigrations`: inspects models and compiles migration instructions.
- `python manage.py migrate`: safely applies schema changes to SQLite or PostgreSQL.""",
            }
        )

        l4, _ = Lesson.objects.get_or_create(
            module=m2,
            order=2,
            defaults={
                'title': '4. Views, URL Routing, and Clean Templates',
                'lesson_type': Lesson.TYPE_ARTICLE,
                'duration_minutes': 20,
                'is_preview': False,
                'content': """### Understanding Django MVT Pattern

1. **Model**: Defines the structure of data in the database.
2. **View**: Handles the business logic and HTTP Request/Response flow.
3. **Template**: Presents data dynamically via Django Template Language (DTL).

```python
# views.py
from django.shortcuts import render, get_object_or_404
from .models import Course

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    return render(request, 'courses/detail.html', {'course': course})
```""",
            }
        )

        # 4. Quizzes for Course 1
        quiz1, _ = Quiz.objects.get_or_create(
            course=course1,
            lesson=l1,
            defaults={
                'title': 'Lesson 1 Knowledge Check: Python & Virtual Environments',
                'description': 'Assess your understanding of Python environments, pip, and interpreter basics.',
                'passing_score': 70,
                'time_limit_minutes': 10,
                'is_published': True,
            }
        )

        q1, _ = Question.objects.get_or_create(
            quiz=quiz1,
            order=1,
            defaults={
                'text': 'Which command is used to create an isolated Python virtual environment named "venv"?',
                'explanation': '`python -m venv venv` is standard across Python 3 installations to generate a local virtual environment sandbox.',
            }
        )
        if not q1.choices.exists():
            AnswerChoice.objects.create(question=q1, text='python -m venv venv', is_correct=True)
            AnswerChoice.objects.create(question=q1, text='pip install virtualenv', is_correct=False)
            AnswerChoice.objects.create(question=q1, text='python create environment venv', is_correct=False)
            AnswerChoice.objects.create(question=q1, text='pip make venv', is_correct=False)

        q2, _ = Question.objects.get_or_create(
            quiz=quiz1,
            order=2,
            defaults={
                'text': 'What is the purpose of the requirements.txt file in Python projects?',
                'explanation': 'requirements.txt pinpoints exact dependencies and versions required for reproducible builds.',
            }
        )
        if not q2.choices.exists():
            AnswerChoice.objects.create(question=q2, text='To track and freeze exact package dependencies for reproducible installs', is_correct=True)
            AnswerChoice.objects.create(question=q2, text='To compile Python source files into machine code', is_correct=False)
            AnswerChoice.objects.create(question=q2, text='To store user passwords securely', is_correct=False)
            AnswerChoice.objects.create(question=q2, text='To configure SQLite database settings', is_correct=False)

        q3, _ = Question.objects.get_or_create(
            quiz=quiz1,
            order=3,
            defaults={
                'text': 'What is the standard architecture pattern followed by Django?',
                'explanation': 'Django uses MVT: Model (data), View (controller logic), Template (presentation layer).',
            }
        )
        if not q3.choices.exists():
            AnswerChoice.objects.create(question=q3, text='Model-View-Template (MVT)', is_correct=True)
            AnswerChoice.objects.create(question=q3, text='Model-View-Presenter (MVP)', is_correct=False)
            AnswerChoice.objects.create(question=q3, text='Micro-Frontends (MFE)', is_correct=False)
            AnswerChoice.objects.create(question=q3, text='Single Page Architecture (SPA)', is_correct=False)

        # 5. Course 2: Practical AI & Machine Learning with Python
        course2, _ = Course.objects.get_or_create(
            slug='practical-ai-machine-learning-python',
            defaults={
                'title': 'Practical AI & Machine Learning with Python',
                'subtitle': 'Train neural networks, build predictive models, and deploy machine learning workflows.',
                'description': """Step into modern Artificial Intelligence with hands-on Python projects. Learn data preprocessing with NumPy and Pandas, model evaluation with Scikit-Learn, and deep learning neural architectures.""",
                'category': cat_ai,
                'instructor': instructor_alex,
                'level': Course.LEVEL_INTERMEDIATE,
                'price': 29.99,
                'thumbnail_url': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=800&auto=format&fit=crop',
                'is_published': True,
                'featured': True,
            }
        )

        m_ai_1, _ = Module.objects.get_or_create(
            course=course2,
            order=1,
            defaults={
                'title': 'Introduction to Data Preprocessing & Tensors',
                'description': 'NumPy arrays, data normalization, and feature matrices.',
            }
        )

        Lesson.objects.get_or_create(
            module=m_ai_1,
            order=1,
            defaults={
                'title': 'Vectorized Math and Linear Algebra for ML',
                'lesson_type': Lesson.TYPE_VIDEO,
                'video_url': 'https://www.youtube.com/watch?v=aircAruvnKk',
                'duration_minutes': 22,
                'is_preview': True,
                'content': 'Vectorization provides 100x performance improvements compared to nested Python loops when computing matrix operations.',
            }
        )

        # 6. Course 3: Modern Responsive Web Design & Tailwind CSS
        course3, _ = Course.objects.get_or_create(
            slug='modern-responsive-web-design-tailwind',
            defaults={
                'title': 'Modern Responsive Web Design with Tailwind CSS & UI Systems',
                'subtitle': 'Design clean, high-converting interfaces, component libraries, and polished interactive layouts.',
                'description': """Learn utility-first CSS using Tailwind CSS. Build responsive navigation menus, dashboard cards, forms, and typography systems without writing cumbersome spaghetti CSS.""",
                'category': cat_web,
                'instructor': instructor_sarah,
                'level': Course.LEVEL_BEGINNER,
                'price': 0.00,
                'thumbnail_url': 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?q=80&w=800&auto=format&fit=crop',
                'is_published': True,
                'featured': True,
            }
        )

        m_web_1, _ = Module.objects.get_or_create(
            course=course3,
            order=1,
            defaults={
                'title': 'Flexbox, CSS Grid, and Utility Styling',
                'description': 'Core layout mechanics and responsive breakpoints.',
            }
        )

        Lesson.objects.get_or_create(
            module=m_web_1,
            order=1,
            defaults={
                'title': 'Mastering Flexbox and Mobile-First Breakpoints',
                'lesson_type': Lesson.TYPE_ARTICLE,
                'duration_minutes': 15,
                'is_preview': True,
                'content': 'Discover Tailwind breakpoints: sm, md, lg, xl, and 2xl for fluid, adaptive responsive layouts.',
            }
        )

        # 7. Student Enrollment & Progress for demo account (john_student)
        enrollment1, _ = Enrollment.objects.get_or_create(
            student=student_john,
            course=course1,
        )

        LessonProgress.objects.get_or_create(
            enrollment=enrollment1,
            lesson=l1,
            defaults={'is_completed': True, 'completed_at': timezone.now()}
        )

        LessonProgress.objects.get_or_create(
            enrollment=enrollment1,
            lesson=l2,
            defaults={'is_completed': True, 'completed_at': timezone.now()}
        )

        # Sample Quiz Attempt
        attempt1, _ = QuizAttempt.objects.get_or_create(
            quiz=quiz1,
            student=student_john,
            defaults={
                'total_questions': 3,
                'correct_answers': 3,
                'score': 100.0,
                'passed': True,
            }
        )

        # Sample Discussion
        Discussion.objects.get_or_create(
            course=course1,
            lesson=l1,
            user=student_john,
            content="Should we prefer python3 -m venv or virtualenv wrapper on Linux servers?",
            defaults={
                'created_at': timezone.now()
            }
        )

        # Sample Course Reviews
        Review.objects.get_or_create(
            course=course1,
            student=student_john,
            defaults={
                'rating': 5,
                'comment': 'Exceptional course structure! Sarah explains difficult backend concepts with extreme clarity. The quizzes reinforce the lessons perfectly.',
            }
        )

        self.stdout.write(self.style.SUCCESS("[SUCCESS] EduLearn seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("""
Test User Credentials:
  - Admin: username='admin', password='admin123'
  - Instructor: username='sarah_dev', password='instructor123'
  - Instructor: username='alex_ai', password='instructor123'
  - Student: username='john_student', password='student123'
"""))
