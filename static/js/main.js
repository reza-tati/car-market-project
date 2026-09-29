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

// ===== انتخاب رنگ با آیکون =====
$(document).ready(function() {
    console.log('🔍 Checking color field...');
    console.log('Color element count:', $('#id_color').length);
    
    if ($('#id_color').length) {
        const colorMap = {
            'white': '#ffffff',
            'black': '#000000',
            'silver': '#c0c0c0',
            'gray': '#808080',
            'red': '#dc3545',
            'blue': '#0d6efd',
            'green': '#198754',
            'brown': '#8b4513',
            'yellow': '#ffc107',
            'orange': '#fd7e14',
        };
        
        function formatColor(option) {
            if (!option.id) return option.text;
            
            const bgColor = colorMap[option.id] || '#ccc';
            
            return $(`
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="width: 20px; height: 20px; border-radius: 50%; background: ${bgColor}; border: 2px solid #ddd; display: inline-block;"></span>
                    <span>${option.text}</span>
                </div>
            `);
        }
        
        $('#id_color').select2({
            theme: 'bootstrap-5',
            templateResult: formatColor,
            templateSelection: formatColor,
            language: 'fa',
            placeholder: 'انتخاب رنگ',
            allowClear: true,
        });
        
        console.log('✅ Select2 applied to color field!');
    } else {
        console.log('❌ Color field not found!');
    }
});