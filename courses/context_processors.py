from .models import Category


def categories_processor(request):
    try:
        categories = Category.objects.all()
    except Exception:
        categories = []
    return {
        'all_categories': categories
    }
