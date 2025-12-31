
def brands_processor(request):
    # اگر هنوز مدل Car نداریم، فعلاً یک لیست نمونه برگردانیم
    return {
        "brands": ["Toyota", "BMW", "Mercedes", "Honda"]
    }