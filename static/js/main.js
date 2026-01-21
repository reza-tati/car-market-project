// تابع تغییر تصویر اصلی در گالری
function changeCarImage(thumbnail) {
    const mainImage = document.getElementById('main-car-image');
    if (mainImage && thumbnail.dataset.full) {
        mainImage.src = thumbnail.dataset.full;
        
        // به‌روزرسانی thumbnailهای فعال
        document.querySelectorAll('.car-thumbnail').forEach(function(item) {
            item.classList.remove('active');
        });
        
        thumbnail.classList.add('active');
    }
}

// وقتی صفحه لود شد
document.addEventListener('DOMContentLoaded', function() {
    console.log('فایل JS بارگذاری شد');
    
    // اضافه کردن ایونت به thumbnailها
    document.querySelectorAll('.car-thumbnail').forEach(function(thumb) {
        thumb.addEventListener('click', function() {
            changeCarImage(this);
        });
    });
});