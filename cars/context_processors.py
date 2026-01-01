from .models import Brand

def brands_processor(request):
    return {
        'all_brands': Brand.objects.all().order_by('name')[:20],
        # ...
    }