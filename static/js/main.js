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

/* ============================================
   🎠 اسلایدر بنرهای صفحه اصلی
   ============================================ */
document.addEventListener('DOMContentLoaded', function () {
    var slider = document.querySelector('.hero-slider');
    if (!slider) return;

    var slides  = slider.querySelectorAll('.hero-slide');
    var dots    = slider.querySelectorAll('.hero-slider-dot');
    var prevBtn = slider.querySelector('.hero-slider-prev');
    var nextBtn = slider.querySelector('.hero-slider-next');
    var current = 0;
    var total   = slides.length;
    var autoTimer = null;
    var AUTO_DELAY = 5000; // هر ۵ ثانیه بنر عوض می‌شه

    function goTo(index) {
        current = (index + total) % total; // چرخه‌ای: بعد از آخری، برگرد به اولی

        slides.forEach(function (slide, i) {
            var active = (i === current);
            slide.classList.toggle('is-active', active);
            slide.setAttribute('aria-hidden', active ? 'false' : 'true');
            if (active) {
                slide.removeAttribute('inert');
            } else {
                slide.setAttribute('inert', '');
            }
            slide.querySelectorAll('a').forEach(function (a) {
                a.tabIndex = active ? 0 : -1;
            });
        });

        dots.forEach(function (dot, i) {
            var active = (i === current);
            dot.classList.toggle('is-active', active);
            dot.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
    }

    function nextSlide() { goTo(current + 1); }
    function prevSlide() { goTo(current - 1); }

    function startAuto() {
        stopAuto();
        autoTimer = setInterval(nextSlide, AUTO_DELAY);
    }
    function stopAuto() {
        if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
    }

    /* فلش‌ها و دات‌ها */
    if (nextBtn) nextBtn.addEventListener('click', function () { nextSlide(); startAuto(); });
    if (prevBtn) prevBtn.addEventListener('click', function () { prevSlide(); startAuto(); });
    dots.forEach(function (dot, i) {
        dot.addEventListener('click', function () { goTo(i); startAuto(); });
    });

    /* هاور = توقف خودکار، خروج = ادامه */
    slider.addEventListener('mouseenter', stopAuto);
    slider.addEventListener('mouseleave', startAuto);

    /* وقتی تب غیرفعاله، اسلایدر نخوابه CPU */
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) { stopAuto(); } else { startAuto(); }
    });

    /* سوایپ لمسی برای موبایل */
    var touchX = null;
    slider.addEventListener('touchstart', function (e) {
        touchX = e.touches[0].clientX;
        stopAuto();
    }, { passive: true });
    slider.addEventListener('touchend', function (e) {
        if (touchX === null) return;
        var delta = e.changedTouches[0].clientX - touchX;
        if (Math.abs(delta) > 50) {
            if (delta < 0) { nextSlide(); } else { prevSlide(); }
        }
        touchX = null;
        startAuto();
    }, { passive: true });

    /* شروع */
    goTo(0);
    startAuto();
});