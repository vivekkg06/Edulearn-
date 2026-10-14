from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg

from .models import User
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm
from courses.models import Course, Category, Enrollment, Lesson
from quizzes.models import QuizAttempt


def home(request):
    featured_courses = Course.objects.filter(is_published=True, featured=True)[:6]
    if not featured_courses.exists():
        featured_courses = Course.objects.filter(is_published=True)[:6]
    
    recent_courses = Course.objects.filter(is_published=True).order_by('-created_at')[:6]
    categories = Category.objects.annotate(total_courses=Count('courses')).order_by('-total_courses')[:8]
    
    total_students = User.objects.filter(role=User.ROLE_STUDENT).count()
    total_courses = Course.objects.filter(is_published=True).count()
    total_lessons = Lesson.objects.count()
    
    top_instructors = User.objects.filter(role=User.ROLE_INSTRUCTOR)[:4]

    context = {
        'featured_courses': featured_courses,
        'recent_courses': recent_courses,
        'categories': categories,
        'total_students': total_students,
        'total_courses': total_courses,
        'total_lessons': total_lessons,
        'top_instructors': top_instructors,
    }
    return render(request, 'core/home.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, f"Welcome to EduLearn, {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        initial_role = request.GET.get('role', User.ROLE_STUDENT)
        form = UserRegisterForm(initial={'role': initial_role})

    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def dashboard_view(request):
    user = request.user
    if user.is_instructor:
        courses = Course.objects.filter(instructor=user)
        total_students = Enrollment.objects.filter(course__instructor=user).count()
        total_lessons = Lesson.objects.filter(module__course__instructor=user).count()
        recent_enrollments = Enrollment.objects.filter(course__instructor=user).select_related('student', 'course')[:10]

        context = {
            'courses': courses,
            'total_students': total_students,
            'total_lessons': total_lessons,
            'recent_enrollments': recent_enrollments,
        }
        return render(request, 'core/instructor_dashboard.html', context)
    else:
        enrollments = Enrollment.objects.filter(student=user).select_related('course').prefetch_related('lesson_progress')
        recent_attempts = QuizAttempt.objects.filter(student=user).select_related('quiz', 'quiz__course')[:5]
        
        # Calculate summary metrics
        completed_courses = [e for e in enrollments if e.progress_percentage() >= 100]
        in_progress_courses = [e for e in enrollments if e.progress_percentage() < 100]

        context = {
            'enrollments': enrollments,
            'in_progress_courses': in_progress_courses,
            'completed_courses': completed_courses,
            'recent_attempts': recent_attempts,
        }
        return render(request, 'core/dashboard.html', context)


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'core/profile.html', {'form': form})
