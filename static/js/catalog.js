document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("catalogSearch");
    const filterButtons = document.querySelectorAll(".catalog-filter");
    const selectFilters = document.querySelectorAll("[data-filter]");
    const sortSelect = document.getElementById("catalogSort");
    const resetButton = document.getElementById("catalogReset");
    const grid = document.getElementById("catalogGrid");
    const cards = Array.from(document.querySelectorAll(".catalog-card"));
    const countElement = document.getElementById("catalogCount");
    const emptyMessage = document.getElementById("catalogEmpty");
    const viewButtons = document.querySelectorAll(".catalog-view-button");
    const mobileFilterToggle = document.getElementById("catalogMobileFilterToggle");
    const filterPanel = document.getElementById("catalogFilterPanel");
    const params = new URLSearchParams(window.location.search);
    const viewStorageKey = "rus-les-catalog-view";

    let activeCategory = normalize(params.get("category") || "all");
    let activePurpose = normalize(params.get("purpose") || "");
    let activeMaterials = normalize(params.get("materials") || "");
    let activeWoods = normalize(params.get("woods") || "");
    let filterFrame = null;

    function normalize(value) {
        return String(value || "").trim().toLowerCase();
    }

    function getActivePurposes() {
        return activePurpose.split("|").map(normalize).filter(Boolean);
    }

    function getActiveTerms(value) {
        return value.split("|").map(normalize).filter(Boolean);
    }

    function updateSelectState(select) {
        select.classList.toggle("is-placeholder", normalize(select.value) === "");
    }

    function setFilterPanelOpen(isOpen) {
        if (!mobileFilterToggle || !filterPanel) {
            return;
        }

        filterPanel.classList.toggle("is-open", isOpen);
        mobileFilterToggle.setAttribute("aria-expanded", String(isOpen));

        const label = mobileFilterToggle.querySelector("strong");
        if (label) {
            label.textContent = isOpen
                ? (mobileFilterToggle.dataset.hideLabel || "Скрыть")
                : (mobileFilterToggle.dataset.openLabel || "Открыть");
        }
    }

    function getSavedView() {
        try {
            return window.localStorage.getItem(viewStorageKey);
        } catch (error) {
            return null;
        }
    }

    function applyView(view) {
        if (!grid) {
            return;
        }

        const allowedViews = ["grid", "compact", "list"];
        const activeView = allowedViews.includes(view) ? view : "grid";

        allowedViews.forEach((item) => grid.classList.toggle(`catalog-grid--${item}`, item === activeView));
        viewButtons.forEach((button) => {
            const isActive = button.dataset.view === activeView;
            button.classList.toggle("active", isActive);
            button.setAttribute("aria-pressed", String(isActive));
        });

        try {
            window.localStorage.setItem(viewStorageKey, activeView);
        } catch (error) {
            // The catalog still works when storage is disabled by the browser.
        }
    }

    function getFilterValues() {
        return Array.from(selectFilters).reduce((values, select) => {
            values[select.dataset.filter] = normalize(select.value);
            return values;
        }, {});
    }

    function compareCards(first, second) {
        const sortMode = sortSelect ? sortSelect.value : "default";

        if (sortMode === "price-asc" || sortMode === "price-desc") {
            const difference = Number(first.dataset.price) - Number(second.dataset.price);
            return sortMode === "price-desc" ? -difference : difference;
        }

        if (sortMode === "name-asc") {
            return (first.dataset.name || "").localeCompare(second.dataset.name || "", "ru");
        }

        if (sortMode === "availability") {
            const firstAvailable = first.dataset.availability === "в наличии" ? 0 : 1;
            const secondAvailable = second.dataset.availability === "в наличии" ? 0 : 1;
            return firstAvailable - secondAvailable || Number(first.dataset.index) - Number(second.dataset.index);
        }

        return Number(first.dataset.index) - Number(second.dataset.index);
    }

    function updateCardsOrder() {
        if (!grid) {
            return;
        }

        cards.sort(compareCards).forEach((card) => grid.appendChild(card));
    }

    function formatCount(count) {
        if (document.documentElement.lang === "kk") {
            const foundLabel = countElement ? countElement.dataset.foundLabel : "Табылды";
            const productsLabel = countElement ? countElement.dataset.productsLabel : "тауар";
            return `${foundLabel}: ${count} ${productsLabel}`;
        }

        const lastTwoDigits = count % 100;
        const lastDigit = count % 10;
        let word = "товаров";

        if (lastTwoDigits < 11 || lastTwoDigits > 14) {
            if (lastDigit === 1) {
                word = "товар";
            } else if (lastDigit >= 2 && lastDigit <= 4) {
                word = "товара";
            }
        }

        return `Найдено: ${count} ${word}`;
    }

    function applyFilters() {
        filterFrame = null;
        const query = normalize(searchInput ? searchInput.value : "");
        const values = getFilterValues();
        const activePurposes = getActivePurposes();
        const materialTerms = getActiveTerms(activeMaterials);
        const woodTerms = getActiveTerms(activeWoods);
        let visibleCount = 0;

        cards.forEach((card) => {
            const searchableText = card.dataset.search || card.dataset.name || "";
            const matchesCategory = activeCategory === "all" || card.dataset.category === activeCategory;
            const matchesPurpose = activePurposes.length === 0 || activePurposes.some((purpose) => {
                return (card.dataset.purpose || "").includes(purpose);
            });
            const matchesMaterials = materialTerms.length === 0 || materialTerms.some((term) => {
                return searchableText.includes(term);
            });
            const matchesWoods = woodTerms.length === 0 || woodTerms.some((term) => {
                return searchableText.includes(term);
            });
            const matchesSearch = !query || searchableText.includes(query);
            const matchesSelects = Object.entries(values).every(([field, value]) => {
                return !value || (card.dataset[field] || "") === value;
            });
            const isVisible = matchesCategory
                && matchesPurpose
                && matchesMaterials
                && matchesWoods
                && matchesSearch
                && matchesSelects;

            card.hidden = !isVisible;

            if (isVisible) {
                visibleCount += 1;
            }
        });

        updateCardsOrder();

        if (countElement) {
            countElement.textContent = formatCount(visibleCount);
        }

        if (emptyMessage) {
            emptyMessage.hidden = visibleCount > 0;
        }
    }

    function scheduleFilters() {
        if (filterFrame) {
            cancelAnimationFrame(filterFrame);
        }
        filterFrame = requestAnimationFrame(applyFilters);
    }

    filterButtons.forEach((button) => {
        const buttonCategory = normalize(button.dataset.category || "all");

        if (buttonCategory === activeCategory) {
            filterButtons.forEach((item) => item.classList.remove("active"));
            button.classList.add("active");
        }

        button.addEventListener("click", () => {
            activeCategory = normalize(button.dataset.category || "all");

            filterButtons.forEach((item) => item.classList.remove("active"));
            button.classList.add("active");

            if (window.matchMedia("(max-width: 720px)").matches) {
                setFilterPanelOpen(false);
            }

            scheduleFilters();
        });
    });

    selectFilters.forEach((select) => {
        updateSelectState(select);
        select.addEventListener("change", () => {
            updateSelectState(select);
            scheduleFilters();
        });
    });

    if (sortSelect) {
        sortSelect.addEventListener("change", scheduleFilters);
    }

    if (searchInput) {
        searchInput.value = params.get("q") || "";
        searchInput.addEventListener("input", scheduleFilters);
    }

    viewButtons.forEach((button) => {
        button.addEventListener("click", () => applyView(button.dataset.view));
    });

    if (mobileFilterToggle && filterPanel) {
        mobileFilterToggle.addEventListener("click", () => {
            setFilterPanelOpen(!filterPanel.classList.contains("is-open"));
        });
    }

    if (resetButton) {
        resetButton.addEventListener("click", () => {
            activeCategory = "all";
            activePurpose = "";
            activeMaterials = "";
            activeWoods = "";

            if (searchInput) {
                searchInput.value = "";
            }

            selectFilters.forEach((select) => {
                select.value = "";
                updateSelectState(select);
            });

            if (sortSelect) {
                sortSelect.value = "default";
            }

            filterButtons.forEach((button) => {
                button.classList.toggle("active", normalize(button.dataset.category) === "all");
            });

            window.history.replaceState({}, "", window.location.pathname);
            scheduleFilters();
        });
    }

    applyView(getSavedView() || "grid");
    applyFilters();
});
