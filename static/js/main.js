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
/* ============================================
   📱 منوی همبرگری موبایل
   ============================================ */
document.addEventListener('DOMContentLoaded', function () {
    var menuBtn = document.getElementById('mobile-menu-btn');
    var header  = document.querySelector('.site-header');

    if (!menuBtn || !header) return;

    /* باز/بسته کردن منو (forceClose = بستن اجباری) */
    function toggleMenu(forceClose) {
        var isOpen = (forceClose === true)
            ? false
            : header.classList.toggle('menu-open');

        menuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        menuBtn.setAttribute('aria-label', isOpen ? 'بستن منو' : 'باز کردن منو');
    }

    /* کلیک روی دکمه همبرگری */
    menuBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        toggleMenu();
    });

    /* بستن منو بعد از کلیک روی هر لینک */
    header.querySelectorAll('.main-nav a, .header-actions a').forEach(function (link) {
        link.addEventListener('click', function () {
            toggleMenu(true);
        });
    });

    /* بستن منو با کلیک بیرون از هدر */
    document.addEventListener('click', function (e) {
        if (header.classList.contains('menu-open') && !header.contains(e.target)) {
            toggleMenu(true);
        }
    });

    /* بستن منو با دکمه Esc کیبورد */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && header.classList.contains('menu-open')) {
            toggleMenu(true);
        }
    });

    /* اگه صفحه بزرگ شد و به دسکتاپ برگشت، منو بسته بشه */
    window.addEventListener('resize', function () {
        if (window.innerWidth > 768 && header.classList.contains('menu-open')) {
            toggleMenu(true);
        }
    });
});

