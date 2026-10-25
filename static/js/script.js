
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
