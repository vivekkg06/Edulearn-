from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Module, Lesson, Enrollment, LessonProgress
from quizzes.models import Quiz, Question, AnswerChoice, QuizAttempt

User = get_user_model()


class EduLearnPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create users
        self.instructor = User.objects.create_user(
            username='instructor_jane',
            password='testpassword123',
            role=User.ROLE_INSTRUCTOR,
            first_name='Jane',
            last_name='Smith'
        )
        self.student = User.objects.create_user(
            username='student_bob',
            password='testpassword123',
            role=User.ROLE_STUDENT,
            first_name='Bob',
            last_name='Brown'
        )
        # Create Category
        self.category = Category.objects.create(name='Python Testing', slug='python-testing')
        # Create Course
        self.course = Course.objects.create(
            title='Test Automation in Python',
            slug='test-automation-python',
            category=self.category,
            instructor=self.instructor,
            level=Course.LEVEL_BEGINNER,
            price=0.0,
            is_published=True
        )
        # Create Module & Lessons
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.lesson1 = Lesson.objects.create(module=self.module, title='Lesson 1', order=1, duration_minutes=10)
        self.lesson2 = Lesson.objects.create(module=self.module, title='Lesson 2', order=2, duration_minutes=15)

    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edu')
        self.assertContains(response, 'Test Automation in Python')

    def test_course_list_and_filter(self):
        response = self.client.get(reverse('course_list'), {'q': 'Automation'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Automation in Python')

    def test_course_detail(self):
        response = self.client.get(reverse('course_detail', kwargs={'slug': self.course.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Automation in Python')
        self.assertContains(response, 'Enroll Now')

    def test_student_enrollment_and_learning_player(self):
        self.client.login(username='student_bob', password='testpassword123')
        
        # Enroll
        enroll_url = reverse('enroll_course', kwargs={'slug': self.course.slug})
        response = self.client.post(enroll_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course).exists())

        # Toggle lesson 1 progress
        toggle_url = reverse('toggle_lesson_progress', kwargs={'lesson_id': self.lesson1.id})
        response = self.client.post(toggle_url, follow=True)
        self.assertEqual(response.status_code, 200)
        progress = LessonProgress.objects.get(enrollment__student=self.student, lesson=self.lesson1)
        self.assertTrue(progress.is_completed)

        # Dashboard shows enrolled course
        dash_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dash_response.status_code, 200)
        self.assertContains(dash_response, 'Test Automation in Python')

    def test_quiz_submission_and_grading(self):
        self.client.login(username='student_bob', password='testpassword123')
        # Create Quiz
        quiz = Quiz.objects.create(
            course=self.course,
            title='Python Test Quiz',
            passing_score=50,
            is_published=True
        )
        q1 = Question.objects.create(quiz=quiz, text='What is 2 + 2?', order=1)
        correct_c = AnswerChoice.objects.create(question=q1, text='4', is_correct=True)
        wrong_c = AnswerChoice.objects.create(question=q1, text='5', is_correct=False)

        # Submit quiz
        submit_url = reverse('quiz_take', kwargs={'quiz_id': quiz.id})
        response = self.client.post(submit_url, {f'question_{q1.id}': correct_c.id}, follow=True)
        self.assertEqual(response.status_code, 200)

        attempt = QuizAttempt.objects.filter(quiz=quiz, student=self.student).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.score, 100.0)
        self.assertTrue(attempt.passed)
