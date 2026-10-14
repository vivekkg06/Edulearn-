from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('course/<slug:slug>/learn/<int:lesson_id>/', views.course_learn, name='course_learn_lesson'),
    path('lesson/<int:lesson_id>/toggle-complete/', views.toggle_lesson_progress, name='toggle_lesson_progress'),
    path('lesson/<int:lesson_id>/discussion/', views.add_discussion, name='add_discussion'),
    path('course/<slug:slug>/review/', views.add_review, name='add_review'),

    # Instructor studio routes
    path('instructor/course/create/', views.instructor_course_create, name='instructor_course_create'),
    path('instructor/course/<slug:slug>/edit/', views.instructor_course_edit, name='instructor_course_edit'),
    path('instructor/course/<slug:slug>/module/create/', views.instructor_module_create, name='instructor_module_create'),
    path('instructor/module/<int:module_id>/lesson/create/', views.instructor_lesson_create, name='instructor_lesson_create'),
]
