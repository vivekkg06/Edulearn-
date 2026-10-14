from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Quiz, Question, AnswerChoice, QuizAttempt, StudentAnswer


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz.objects.select_related('course', 'lesson'), id=quiz_id, is_published=True)
    previous_attempts = QuizAttempt.objects.filter(quiz=quiz, student=request.user).order_by('-completed_at')
    best_attempt = previous_attempts.filter(passed=True).first() or previous_attempts.first()

    context = {
        'quiz': quiz,
        'previous_attempts': previous_attempts,
        'best_attempt': best_attempt,
    }
    return render(request, 'quizzes/quiz_detail.html', context)


@login_required
def quiz_take(request, quiz_id):
    quiz = get_object_or_404(Quiz.objects.select_related('course', 'lesson'), id=quiz_id, is_published=True)
    questions = quiz.questions.prefetch_related('choices').all()

    if not questions.exists():
        messages.warning(request, "This quiz doesn't have any questions yet.")
        return redirect('course_learn', slug=quiz.course.slug)

    if request.method == 'POST':
        total_questions = questions.count()
        correct_count = 0

        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=request.user,
            total_questions=total_questions,
            correct_answers=0,
            score=0.0,
            passed=False,
        )

        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            selected_choice = None
            is_correct = False

            if choice_id:
                try:
                    selected_choice = question.choices.get(id=choice_id)
                    if selected_choice.is_correct:
                        is_correct = True
                        correct_count += 1
                except AnswerChoice.DoesNotExist:
                    pass

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice,
                is_correct=is_correct,
            )

        score_pct = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0
        passed = score_pct >= quiz.passing_score

        attempt.score = score_pct
        attempt.correct_answers = correct_count
        attempt.passed = passed
        attempt.save()

        if passed:
            messages.success(request, f"🎉 Congratulations! You scored {score_pct}% and PASSED the quiz!")
        else:
            messages.warning(request, f"You scored {score_pct}%. Passing score is {quiz.passing_score}%. You can review the answers and try again!")

        return redirect('quiz_result', attempt_id=attempt.id)

    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'quizzes/quiz_take.html', context)


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz', 'quiz__course', 'student').prefetch_related(
            'answers__question', 'answers__selected_choice', 'answers__question__choices'
        ),
        id=attempt_id
    )

    if attempt.student != request.user and not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'course': attempt.quiz.course,
    }
    return render(request, 'quizzes/quiz_result.html', context)
