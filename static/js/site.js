document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".header-menu-toggle");
    const menu = document.getElementById("siteHeaderMenu");

    if (!toggle || !menu) {
        return;
    }

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
});
