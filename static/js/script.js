
document.addEventListener("DOMContentLoaded", function () {



    

    /* =========================================
       ۱. منوی موبایل
       ========================================= */

    const menuToggle = document.querySelector(".menu-toggle");
    const mainNav = document.querySelector(".main-nav");

    if (menuToggle && mainNav) {

        menuToggle.addEventListener("click", function () {
            const isOpen = mainNav.classList.toggle("is-open");

            menuToggle.setAttribute("aria-expanded", String(isOpen));

            menuToggle.setAttribute(
                "aria-label",
                isOpen ? "بستن منو" : "باز کردن منو"
            );
        });

        mainNav.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                mainNav.classList.remove("is-open");

                menuToggle.setAttribute("aria-expanded", "false");
                menuToggle.setAttribute("aria-label", "باز کردن منو");
            });
        });
    }


    /* =========================================
       ۲. دکمه‌های علاقه‌مندی
       ========================================= */

    const favoriteButtons = document.querySelectorAll(".favorite-button");

    favoriteButtons.forEach(function (button) {

        button.addEventListener("click", function () {
            const isFavorite = button.classList.toggle("is-favorite");

            button.setAttribute("aria-pressed", String(isFavorite));

            button.setAttribute(
                "aria-label",
                isFavorite
                    ? "حذف از علاقه‌مندی‌ها"
                    : "افزودن به علاقه‌مندی‌ها"
            );

            /*
             * اگر قلب با SVG ساخته شده باشد، آن را حفظ می‌کنیم.
             * اگر دکمه با کاراکتر ♡ ساخته شده باشد، همان را تغییر می‌دهیم.
             */
            if (!button.querySelector("svg")) {
                button.textContent = isFavorite ? "♥" : "♡";
            }
        });

    });


    /* =========================================
       ۳. اسلایدر واقعی بنر
       ========================================= */

    const heroSlider = document.querySelector(".hero-slider");

    if (heroSlider) {

        const slides = Array.from(
            heroSlider.querySelectorAll(".hero-slide")
        );

        const dots = Array.from(
            heroSlider.querySelectorAll(".hero-slider-dot")
        );

        const prevButton = heroSlider.querySelector(".hero-slider-prev");
        const nextButton = heroSlider.querySelector(".hero-slider-next");

        const reducedMotion = window.matchMedia(
            "(prefers-reduced-motion: reduce)"
        );

        let currentIndex = Math.max(
            0,
            slides.findIndex(function (slide) {
                return slide.classList.contains("is-active");
            })
        );

        let autoPlayId = null;

        const autoPlayDelay = 5500;

        /*
         * نمایش اسلاید انتخاب‌شده و به‌روزرسانی نشانگرها.
         */
        function showSlide(index) {

            if (!slides.length) return;

            currentIndex = (index + slides.length) % slides.length;

            slides.forEach(function (slide, i) {

                const isActive = i === currentIndex;

                slide.classList.toggle("is-active", isActive);
                slide.setAttribute("aria-hidden", String(!isActive));

                /*
                 * محتوای اسلاید غیرفعال نباید با صفحه‌کلید انتخاب شود.
                 */
                if (isActive) {
                    slide.removeAttribute("inert");
                } else {
                    slide.setAttribute("inert", "");
                }

                slide.querySelectorAll(".hero-slide-cta").forEach(function (link) {
                    link.setAttribute("tabindex", isActive ? "0" : "-1");
                });

            });

            dots.forEach(function (dot, i) {

                const isActive = i === currentIndex;

                dot.classList.toggle("is-active", isActive);
                dot.setAttribute("aria-pressed", String(isActive));

            });
        }


        /*
         * رفتن به اسلاید بعدی.
         */
        function nextSlide() {
            showSlide(currentIndex + 1);
        }


        /*
         * رفتن به اسلاید قبلی.
         */
        function prevSlide() {
            showSlide(currentIndex - 1);
        }


        /*
         * متوقف کردن چرخش خودکار.
         */
        function stopAutoPlay() {

            if (autoPlayId !== null) {
                window.clearInterval(autoPlayId);
                autoPlayId = null;
            }

        }


        /*
         * شروع چرخش خودکار هر ۵٫۵ ثانیه.
         */
        function startAutoPlay() {

            stopAutoPlay();

            if (
                slides.length < 2 ||
                reducedMotion.matches ||
                document.hidden
            ) {
                return;
            }

            autoPlayId = window.setInterval(
                nextSlide,
                autoPlayDelay
            );
        }


        /*
         * اتصال دکمه‌های قبلی و بعدی.
         */
        if (nextButton) {
            nextButton.addEventListener("click", function () {
                nextSlide();
                startAutoPlay();
            });
        }

        if (prevButton) {
            prevButton.addEventListener("click", function () {
                prevSlide();
                startAutoPlay();
            });
        }


        /*
         * اتصال نقطه‌های زیر بنر.
         */
        dots.forEach(function (dot, index) {

            dot.addEventListener("click", function () {
                showSlide(index);
                startAutoPlay();
            });

        });


        /*
         * هنگام قرار گرفتن نشانگر ماوس روی بنر،
         * چرخش خودکار متوقف می‌شود.
         */
        heroSlider.addEventListener("mouseenter", stopAutoPlay);

        heroSlider.addEventListener("mouseleave", startAutoPlay);


        /*
         * هنگام تمرکز صفحه‌کلید روی بنر نیز اسلاید ثابت می‌ماند.
         */
        heroSlider.addEventListener("focusin", stopAutoPlay);

        heroSlider.addEventListener("focusout", function (event) {

            if (!heroSlider.contains(event.relatedTarget)) {
                startAutoPlay();
            }

        });


        /*
         * اگر کاربر تب دیگری را باز کند، تایمر متوقف می‌شود.
         */
        document.addEventListener("visibilitychange", function () {

            if (document.hidden) {
                stopAutoPlay();
            } else {
                startAutoPlay();
            }

        });


        /*
         * اگر تنظیم کاهش حرکت سیستم تغییر کند،
         * چرخش خودکار متناسب با آن تنظیم می‌شود.
         */
        if (reducedMotion.addEventListener) {
            reducedMotion.addEventListener("change", startAutoPlay);
        } else if (reducedMotion.addListener) {
            reducedMotion.addListener(startAutoPlay);
        }


        /*
         * شروع اسلایدر از اسلاید فعال و راه‌اندازی تایمر.
         */
        showSlide(currentIndex);
        startAutoPlay();

    }


    /* =========================================
       ۴. لینک‌های نمایشی ورود و ثبت آگهی
       ========================================= */

    const demoLinks = document.querySelectorAll(
        '.header-actions a[href="#footer"], ' +
        '.header-actions a[href="#cars"]'
    );

    demoLinks.forEach(function (link) {

        link.addEventListener("click", function (event) {

            if (link.classList.contains("login-button")) {
                event.preventDefault();

                alert(
                    "این نسخه نمایشی است؛ برای ورود واقعی " +
                    "باید فرم ورود و بخش سرور ساخته شود."
                );
            }

        });

    });

});
