document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".header-menu-toggle");
    const menu = document.getElementById("siteHeaderMenu");

    if (toggle && menu) {
        function setMenuOpen(isOpen) {
            toggle.classList.toggle("is-open", isOpen);
            menu.classList.toggle("is-open", isOpen);
            toggle.setAttribute("aria-expanded", String(isOpen));
            toggle.setAttribute("aria-label", isOpen ? "Закрыть меню" : "Открыть меню");
        }

        toggle.addEventListener("click", () => {
            setMenuOpen(!menu.classList.contains("is-open"));
        });

        menu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", () => setMenuOpen(false));
        });

        document.addEventListener("click", (event) => {
            if (menu.classList.contains("is-open") && !event.target.closest(".site-header")) {
                setMenuOpen(false);
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                setMenuOpen(false);
            }
        });

        window.addEventListener("resize", () => {
            if (window.matchMedia("(min-width: 981px)").matches) {
                setMenuOpen(false);
            }
        });
    }

    document.querySelectorAll("[data-carousel]").forEach((carousel) => {
        const stage = carousel.querySelector("[data-carousel-stage]");
        const slides = Array.from(carousel.querySelectorAll("[data-carousel-slide]"));
        const thumbs = Array.from(carousel.querySelectorAll("[data-carousel-thumb]"));
        const previousButton = carousel.querySelector("[data-carousel-prev]");
        const nextButton = carousel.querySelector("[data-carousel-next]");
        const currentLabel = carousel.querySelector("[data-carousel-current]");
        const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        if (!stage || slides.length === 0) {
            return;
        }

        let activeIndex = 0;
        let autoplayTimer = null;
        let touchStartX = 0;

        function showSlide(index, scrollThumb = true) {
            activeIndex = (index + slides.length) % slides.length;

            slides.forEach((slide, slideIndex) => {
                slide.classList.toggle("active", slideIndex === activeIndex);
                slide.setAttribute("aria-hidden", String(slideIndex !== activeIndex));
            });

            thumbs.forEach((thumb, thumbIndex) => {
                const isActive = thumbIndex === activeIndex;
                thumb.classList.toggle("active", isActive);
                thumb.setAttribute("aria-pressed", String(isActive));
            });

            if (currentLabel) {
                currentLabel.textContent = String(activeIndex + 1);
            }

            if (scrollThumb && thumbs[activeIndex]) {
                thumbs[activeIndex].scrollIntoView({behavior: reduceMotion ? "auto" : "smooth", block: "nearest", inline: "center"});
            }
        }

        function stopAutoplay() {
            if (autoplayTimer) {
                window.clearInterval(autoplayTimer);
                autoplayTimer = null;
            }
        }

        function startAutoplay() {
            stopAutoplay();
            if (!reduceMotion && slides.length > 1) {
                autoplayTimer = window.setInterval(() => showSlide(activeIndex + 1, false), 5500);
            }
        }

        function selectSlide(index) {
            showSlide(index);
            startAutoplay();
        }

        previousButton?.addEventListener("click", () => selectSlide(activeIndex - 1));
        nextButton?.addEventListener("click", () => selectSlide(activeIndex + 1));
        thumbs.forEach((thumb, index) => thumb.addEventListener("click", () => selectSlide(index)));

        carousel.addEventListener("mouseenter", stopAutoplay);
        carousel.addEventListener("mouseleave", startAutoplay);
        carousel.addEventListener("focusin", stopAutoplay);
        carousel.addEventListener("focusout", startAutoplay);

        stage.addEventListener("touchstart", (event) => {
            touchStartX = event.changedTouches[0].clientX;
        }, {passive: true});

        stage.addEventListener("touchend", (event) => {
            const distance = event.changedTouches[0].clientX - touchStartX;
            if (Math.abs(distance) > 45) {
                selectSlide(activeIndex + (distance < 0 ? 1 : -1));
            }
        }, {passive: true});

        showSlide(0, false);
        startAutoplay();
    });
});
