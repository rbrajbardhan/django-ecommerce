from .models import Category

def category_renderer(request):
    return {
        'all_categories': Category.objects.all()
    }