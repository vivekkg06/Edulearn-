from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone

from .models import Course, Category, Module, Lesson, Enrollment, LessonProgress, Discussion, Review
from .forms import CourseForm, ModuleForm, LessonForm, ReviewForm, DiscussionForm


def course_list(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    level = request.GET.get('level', '').strip()
    price_filter = request.GET.get('price', '').strip()
    sort = request.GET.get('sort', 'popular')

    courses = Course.objects.filter(is_published=True).select_related('category', 'instructor').annotate(
        enrollment_count=Count('enrollments')
    )

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(subtitle__icontains=query) |
            Q(description__icontains=query)
        )

    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    if level:
        courses = courses.filter(level=level)

    if price_filter == 'free':
        courses = courses.filter(price=0)
    elif price_filter == 'paid':
        courses = courses.filter(price__gt=0)

    if sort == 'newest':
        courses = courses.order_by('-created_at')
    elif sort == 'rating':
        courses = courses.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:  # popular
        courses = courses.order_by('-enrollment_count', '-created_at')

    categories = Category.objects.annotate(count=Count('courses')).order_by('-count')

    context = {
        'courses': courses,
        'categories': categories,
        'search_query': query,
        'selected_category': category_slug,
        'selected_level': level,
        'selected_price': price_filter,
        'selected_sort': sort,
        'total_count': courses.count(),
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.select_related('category', 'instructor'), slug=slug)
    modules = course.modules.prefetch_related('lessons').all()
    reviews = course.reviews.select_related('student').order_by('-created_at')
    
    is_enrolled = False
    enrollment = None
    user_review = None

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None or request.user == course.instructor or request.user.is_superuser
        user_review = reviews.filter(student=request.user).first()

    review_form = ReviewForm()

    context = {
        'course': course,
        'modules': modules,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'user_review': user_review,
        'review_form': review_form,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    
    if created:
        messages.success(request, f"Congratulations! You are now enrolled in '{course.title}'. Let's start learning!")
    else:
        messages.info(request, f"Welcome back to '{course.title}'!")

    return redirect('course_learn', slug=course.slug)


@login_required
def course_learn(request, slug, lesson_id=None):
    course = get_object_or_404(Course, slug=slug)
    
    # Check enrollment or instructor access
    is_authorized = (
        request.user == course.instructor or
        request.user.is_superuser or
        Enrollment.objects.filter(student=request.user, course=course).exists()
    )

    if not is_authorized:
        # Check if requested lesson is preview
        if lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
            if not lesson.is_preview:
                messages.warning(request, "Please enroll in this course to access this lesson.")
                return redirect('course_detail', slug=slug)
        else:
            messages.warning(request, "Please enroll in this course to start learning.")
            return redirect('course_detail', slug=slug)

    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    modules = course.modules.prefetch_related('lessons').all()
    all_lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order'))

    if not all_lessons:
        messages.info(request, "This course currently does not have any lessons published.")
        return redirect('course_detail', slug=slug)

    # Determine active lesson
    active_lesson = None
    if lesson_id:
        active_lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    else:
        # Default to first incomplete lesson if student is enrolled
        if enrollment:
            completed_lesson_ids = set(
                enrollment.lesson_progress.filter(is_completed=True).values_list('lesson_id', flat=True)
            )
            for l in all_lessons:
                if l.id not in completed_lesson_ids:
                    active_lesson = l
                    break
        if not active_lesson:
            active_lesson = all_lessons[0]

    # Find prev and next lesson
    current_index = all_lessons.index(active_lesson) if active_lesson in all_lessons else 0
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None

    # Status of current lesson
    is_current_completed = False
    completed_ids = set()
    if enrollment:
        completed_ids = set(enrollment.lesson_progress.filter(is_completed=True).values_list('lesson_id', flat=True))
        is_current_completed = active_lesson.id in completed_ids

    # Discussions for this lesson
    discussions = Discussion.objects.filter(lesson=active_lesson, parent__isnull=True).select_related('user').prefetch_related('replies__user')
    discussion_form = DiscussionForm()

    # Quizzes
    lesson_quizzes = active_lesson.quizzes.filter(is_published=True)
    course_quizzes = course.quizzes.filter(is_published=True, lesson__isnull=True)

    context = {
        'course': course,
        'modules': modules,
        'active_lesson': active_lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'enrollment': enrollment,
        'is_current_completed': is_current_completed,
        'completed_ids': completed_ids,
        'discussions': discussions,
        'discussion_form': discussion_form,
        'lesson_quizzes': lesson_quizzes,
        'course_quizzes': course_quizzes,
    }
    return render(request, 'courses/course_learn.html', context)


@login_required
def toggle_lesson_progress(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.module.course
    enrollment, _ = Enrollment.objects.get_or_create(student=request.user, course=course)

    progress, created = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    progress.is_completed = not progress.is_completed
    progress.completed_at = timezone.now() if progress.is_completed else None
    progress.save()

    # Check if whole course is completed
    if enrollment.progress_percentage() >= 100:
        if not enrollment.completed:
            enrollment.completed = True
            enrollment.completed_at = timezone.now()
            enrollment.save()
            messages.success(request, f"🎉 Outstanding achievement! You have completed the entire course: {course.title}!")
    else:
        if enrollment.completed:
            enrollment.completed = False
            enrollment.completed_at = None
            enrollment.save()

    return redirect('course_learn_lesson', slug=course.slug, lesson_id=lesson.id)


@login_required
def add_discussion(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        parent_id = request.POST.get('parent_id')
        parent = Discussion.objects.filter(id=parent_id).first() if parent_id else None

        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.course = lesson.module.course
            discussion.lesson = lesson
            discussion.user = request.user
            discussion.parent = parent
            discussion.save()
            messages.success(request, "Your comment has been posted!")

    return redirect('course_learn_lesson', slug=lesson.module.course.slug, lesson_id=lesson.id)


@login_required
def add_review(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.get_or_create(course=course, student=request.user)
            review.rating = form.cleaned_data['rating']
            review.comment = form.cleaned_data['comment']
            review.save()
            messages.success(request, "Thank you! Your course review has been saved.")

    return redirect('course_detail', slug=slug)


# Instructor Studio Views
@login_required
def instructor_course_create(request):
    if not request.user.is_instructor:
        messages.error(request, "Only registered instructors can create courses.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, f"Course '{course.title}' created successfully! Now add modules and lessons.")
            return redirect('instructor_course_edit', slug=course.slug)
    else:
        form = CourseForm()

    return render(request, 'courses/instructor_course_create.html', {'form': form})


@login_required
def instructor_course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    modules = course.modules.prefetch_related('lessons').all()

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('instructor_course_edit', slug=course.slug)
    else:
        form = CourseForm(instance=course)

    module_form = ModuleForm()

    context = {
        'course': course,
        'modules': modules,
        'form': form,
        'module_form': module_form,
    }
    return render(request, 'courses/instructor_course_edit.html', context)


@login_required
def instructor_module_create(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, f"Module '{module.title}' added.")

    return redirect('instructor_course_edit', slug=course.slug)


@login_required
def instructor_lesson_create(request, module_id):
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, f"Lesson '{lesson.title}' added successfully!")
            return redirect('instructor_course_edit', slug=module.course.slug)
    else:
        form = LessonForm()

    return render(request, 'courses/instructor_lesson_create.html', {'form': form, 'module': module})
