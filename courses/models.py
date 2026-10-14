import re
from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default='fa-solid fa-graduation-cap', help_text="FontAwesome icon class")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def course_count(self):
        return self.courses.filter(is_published=True).count()

    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_BEGINNER = 'Beginner'
    LEVEL_INTERMEDIATE = 'Intermediate'
    LEVEL_ADVANCED = 'Advanced'
    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, 'Beginner'),
        (LEVEL_INTERMEDIATE, 'Intermediate'),
        (LEVEL_ADVANCED, 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instructed_courses')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=LEVEL_BEGINNER)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="0.00 for free course")
    thumbnail = models.ImageField(upload_to='courses/', blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True, help_text="External image URL for course banner")
    is_published = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_thumbnail(self):
        if self.thumbnail:
            try:
                return self.thumbnail.url
            except Exception:
                pass
        if self.thumbnail_url:
            return self.thumbnail_url
        return "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=800&auto=format&fit=crop"

    def total_lessons(self):
        return Lesson.objects.filter(module__course=self).count()

    def total_duration_minutes(self):
        total = sum(l.duration_minutes for l in Lesson.objects.filter(module__course=self))
        return total

    def total_enrolled_students(self):
        return self.enrollments.count()

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 5.0

    def review_count(self):
        return self.reviews.count()

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"


class Lesson(models.Model):
    TYPE_VIDEO = 'video'
    TYPE_ARTICLE = 'article'
    TYPE_INTERACTIVE = 'interactive'
    TYPE_CHOICES = [
        (TYPE_VIDEO, 'Video Lecture'),
        (TYPE_ARTICLE, 'Reading & Notes'),
        (TYPE_INTERACTIVE, 'Hands-on Practice'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    lesson_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_VIDEO)
    video_url = models.CharField(max_length=300, blank=True, null=True, help_text="YouTube URL, Vimeo or MP4")
    content = models.TextField(blank=True, help_text="Lesson reading material, markdown or HTML notes")
    duration_minutes = models.PositiveIntegerField(default=15)
    is_preview = models.BooleanField(default=False, help_text="Allow free preview before enrollment")

    class Meta:
        ordering = ['order', 'id']

    def get_embed_url(self):
        """Convert standard YouTube/Vimeo URLs to embed URLs"""
        if not self.video_url:
            return ""
        url = self.video_url.strip()
        # YouTube watch URL (youtube.com/watch?v=ID)
        yt_match = re.search(r'(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})', url)
        if yt_match:
            video_id = yt_match.group(1)
            return f"https://www.youtube.com/embed/{video_id}?rel=0"
        # Vimeo
        vimeo_match = re.search(r'vimeo\.com\/(?:video\/)?([0-9]+)', url)
        if vimeo_match:
            vimeo_id = vimeo_match.group(1)
            return f"https://player.vimeo.com/video/{vimeo_id}"
        return url

    def __str__(self):
        return f"{self.module.course.title} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']

    def progress_percentage(self):
        total_lessons = self.course.total_lessons()
        if total_lessons == 0:
            return 100 if self.completed else 0
        completed_count = self.lesson_progress.filter(is_completed=True).count()
        percent = int((completed_count / total_lessons) * 100)
        return min(percent, 100)

    def completed_lessons_count(self):
        return self.lesson_progress.filter(is_completed=True).count()

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.lesson.title}: {'Done' if self.is_completed else 'Pending'}"


class Discussion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='discussions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Discussion by {self.user.username} on {self.course.title}"


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} rated {self.course.title} ({self.rating}/5)"
