import json
import os
import re
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree

from flask import Flask, Response, abort, redirect, render_template, request, session, url_for


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "rus-les-admin-session-key")

BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_PATH = BASE_DIR / "data" / "products.json"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345").strip()
SITE_URL = os.getenv("SITE_URL", "").rstrip("/")
GOOGLE_SITE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION", "").strip()
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
WHATSAPP_NUMBER = "77766546565"
WHATSAPP_BASIC_MESSAGE = (
    "Здравствуйте! Хочу узнать наличие и цену на пиломатериалы. "
    "Подскажите, пожалуйста."
)
WHATSAPP_CUSTOM_ORDER_MESSAGE = (
    "Здравствуйте! Хочу обсудить изделие из дерева под заказ. "
    "Подскажите, пожалуйста, по стоимости и срокам."
)

CARD_IMAGE_MAP = {
    "images/hero.png": "images/cards/hero.jpg",
    "images/Brusok-sosna.jpg": "images/cards/Brusok-sosna.jpg",
    "images/blok-haus.jpg": "images/cards/blok-haus.jpg",
    "images/imitaciya-brusa.jpg": "images/cards/imitaciya-brusa.jpg",
    "images/terrasnaya-doska.jpg": "images/cards/terrasnaya-doska.jpg",
    "images/vagonka.PNG": "images/cards/vagonka.jpg",
    "images/lipa_vagonka.jpg": "images/cards/lipa_vagonka.jpg",
    "images/evro_vagonka.jpg": "images/cards/evro_vagonka.jpg",
    "images/planken_listvinica.jpg": "images/cards/planken_listvinica.jpg",
}

DIMENSIONS_IN_NAME_PATTERN = re.compile(
    r"\d+(?:[.,]\d+)?\s*[*xх×]\s*\d+(?:[.,]\d+)?\s*[*xх×]\s*\d+(?:[.,]\d+)?",
    re.IGNORECASE,
)

CATEGORIES = [
    {"name": "Фанера", "slug": "fanera", "category": "фанера", "description": "Листы для черновых и отделочных работ", "image": "images/hero.png"},
    {"name": "OSB", "slug": "osb", "category": "OSB", "description": "Плиты для пола, стен и каркаса", "image": "images/hero.png"},
    {"name": "Доска", "slug": "doska", "category": "доска", "description": "Обрезной и строганный пиломатериал", "image": "images/Brusok-sosna.jpg"},
    {"name": "Брус", "slug": "brus", "category": "брус", "description": "Материал для каркасов и перекрытий", "image": "images/Brusok-sosna.jpg"},
    {"name": "Брусок", "slug": "brusok", "category": "брусок", "description": "Строганный материал для отделки", "image": "images/Brusok-sosna.jpg"},
    {"name": "Вагонка", "slug": "vagonka", "category": "вагонка", "description": "Отделка для стен, потолков и бань", "image": "images/vagonka.PNG"},
    {"name": "Планкен", "slug": "planken", "category": "планкен", "description": "Фасадная и интерьерная доска", "image": "images/planken_listvinica.jpg"},
    {"name": "Изделия из дерева", "slug": "izdeliya-iz-dereva", "category": "изделия из дерева", "description": "Готовые изделия и элементы под заказ", "image": "images/hero.png"},
    {"name": "Покрытия", "slug": "pokrytiya", "category": "покрытия", "description": "Защита и уход за древесиной", "image": "images/hero.png"},
]

CATEGORY_PAGES = [
    {
        "slug": "osb",
        "category": "OSB",
        "title": "OSB в Алматы",
        "description": "OSB-плиты для пола, стен, кровли и каркасных работ со склада Русский Лес.",
        "image": "images/hero.png",
    },
    {
        "slug": "vagonka",
        "category": "вагонка",
        "title": "Вагонка в Алматы",
        "description": "Вагонка из сосны, липы, кедра и лиственницы для стен, потолка и бани.",
        "image": "images/vagonka.PNG",
    },
    {
        "slug": "fanera",
        "category": "фанера",
        "title": "Фанера в Алматы",
        "description": "Фанера для черновых работ, опалубки, мебели и строительных задач.",
        "image": "images/hero.png",
    },
    {
        "slug": "brus",
        "category": "брус",
        "title": "Брус в Алматы",
        "description": "Брус для каркасов, стоек, балок и строительных конструкций.",
        "image": "images/Brusok-sosna.jpg",
    },
    {
        "slug": "brusok",
        "category": "брусок",
        "title": "Брусок в Алматы",
        "description": "Строганный брусок для обрешётки, отделки и столярных работ.",
        "image": "images/Brusok-sosna.jpg",
    },
    {
        "slug": "doska",
        "category": "доска",
        "title": "Доска в Алматы",
        "description": "Доска и пиломатериал для строительства, отделки и черновых работ.",
        "image": "images/Brusok-sosna.jpg",
    },
    {
        "slug": "planken",
        "category": "планкен",
        "title": "Планкен в Алматы",
        "description": "Планкен для фасада, декоративной отделки и ограждений.",
        "image": "images/planken_listvinica.jpg",
    },
    {
        "slug": "imitaciya-brusa",
        "category": "имитация бруса",
        "title": "Имитация бруса в Алматы",
        "description": "Имитация бруса для отделки стен и деревянной фактуры.",
        "image": "images/imitaciya-brusa.jpg",
    },
    {
        "slug": "blok-haus",
        "category": "блок-хаус",
        "title": "Блок-хаус в Алматы",
        "description": "Блок-хаус для фасадной и интерьерной отделки.",
        "image": "images/blok-haus.jpg",
    },
    {
        "slug": "terrasnaya-doska",
        "category": "террасная доска",
        "title": "Террасная доска в Алматы",
        "description": "Террасная доска для настилов, крыльца и открытых зон.",
        "image": "images/terrasnaya-doska.jpg",
    },
    {
        "slug": "mebelnyy-shchit",
        "category": "мебельный щит",
        "title": "Мебельный щит в Алматы",
        "description": "Мебельный щит для мебели, столешниц, ступеней и столярных изделий.",
        "image": "images/hero.png",
    },
    {
        "slug": "polok",
        "category": "полок для бани",
        "title": "Полок для бани в Алматы",
        "description": "Полок для бани, сауны и парной.",
        "image": "images/hero.png",
    },
    {
        "slug": "pogonazh",
        "category": "погонаж",
        "title": "Погонаж в Алматы",
        "description": "Погонажные изделия для отделки стыков, углов и проёмов.",
        "image": "images/hero.png",
    },
]

CATEGORY_PAGE_MAP = {item["slug"]: item for item in CATEGORY_PAGES}


def normalize_category(value: str) -> str:
    return (value or "").casefold()


CATEGORY_META_MAP = {normalize_category(item["category"]): item for item in CATEGORY_PAGES}


def enrich_product_display_fields(product: dict) -> None:
    dimension_label = " × ".join(
        product.get(field, "")
        for field in ("thickness", "width", "length")
        if product.get(field)
    )
    name = product.get("name", "")
    catalog_name = name

    if dimension_label:
        catalog_name = DIMENSIONS_IN_NAME_PATTERN.sub("", name, count=1)
        catalog_name = re.sub(r"\s+", " ", catalog_name).strip(" ,-") or name

    product["catalog_name"] = catalog_name
    product["dimension_label"] = dimension_label
    product["display_name"] = f"{catalog_name} — {dimension_label}" if dimension_label else catalog_name


def load_products() -> list[dict]:
    try:
        with PRODUCTS_PATH.open(encoding="utf-8") as file:
            products = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

    if not isinstance(products, list):
        return []

    normalized_products = []
    for product in products:
        if not isinstance(product, dict):
            continue

        product.setdefault("description", "")
        product.setdefault("image", "images/hero.png")
        product.setdefault("base_price", 0)
        product.setdefault("unit", "шт")
        product.setdefault("variants", [])
        product.setdefault("category", "прочее")
        enrich_product_display_fields(product)
        normalized_products.append(product)

    display_name_counts = {}
    for product in normalized_products:
        display_name = product["display_name"]
        display_name_counts[display_name] = display_name_counts.get(display_name, 0) + 1

    for product in normalized_products:
        display_name = product["display_name"]
        if display_name_counts[display_name] > 1:
            product["seo_name"] = f"{display_name} — арт. {product.get('id', product['slug'])}"
        else:
            product["seo_name"] = display_name

    return normalized_products


def save_products(products: list[dict]) -> None:
    PRODUCTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = PRODUCTS_PATH.with_suffix(".json.tmp")
    temp_path.write_text(
        json.dumps(products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp_path.replace(PRODUCTS_PATH)


def parse_price_value(value: str) -> int:
    cleaned = (value or "").replace(" ", "").replace(",", ".")
    try:
        return int(round(float(cleaned)))
    except ValueError:
        return 0


def build_variant_label(product: dict) -> str:
    parts = [
        product.get("thickness", ""),
        product.get("width", ""),
        product.get("length", ""),
    ]
    return " × ".join(part for part in parts if part) or product.get("grade") or "Стандарт"


def update_product_characteristics(product: dict) -> None:
    characteristics = {
        "Единица": product.get("unit", ""),
    }

    fields = [
        ("Порода", "wood_type"),
        ("Сорт", "grade"),
        ("Толщина", "thickness"),
        ("Ширина", "width"),
        ("Длина", "length"),
    ]
    for label, key in fields:
        if product.get(key):
            characteristics[label] = product[key]

    product["characteristics"] = characteristics


def admin_required():
    return bool(session.get("admin_logged_in"))


def redirect_to_login():
    return redirect(url_for("admin_login"))


def catalog_categories(products: list[dict]) -> list[str]:
    known_order = [item["category"] for item in CATEGORIES]
    found = {product.get("category", "прочее") for product in products}
    ordered = [category for category in known_order if category in found]
    rest = sorted(found - set(ordered), key=str.casefold)
    return ordered + rest


def dimension_sort_key(value: str) -> tuple[float, str]:
    match = re.search(r"\d+(?:[.,]\d+)?", value or "")
    number = float(match.group(0).replace(",", ".")) if match else float("inf")
    return number, (value or "").casefold()


def catalog_filter_options(products: list[dict]) -> dict[str, list[str]]:
    fields = ["thickness", "width", "length", "wood_type", "grade", "unit"]
    options = {
        field: sorted(
            {product.get(field, "") for product in products if product.get(field)},
            key=dimension_sort_key if field in {"thickness", "width", "length"} else str.casefold,
        )
        for field in fields
    }
    options["unit"] = sorted(
        options["unit"],
        key=lambda unit: {"шт": 0, "м²": 1, "п/м": 2, "м³": 3}.get(unit, 99),
    )
    return options


def products_by_category(products: list[dict], category: str) -> list[dict]:
    target = normalize_category(category)
    return [product for product in products if normalize_category(product.get("category")) == target]


def site_base_url() -> str:
    return SITE_URL or request.url_root.rstrip("/")


def absolute_url(path: str) -> str:
    return f"{site_base_url()}{path}"


def product_price(product: dict) -> int:
    prices = [variant.get("price", 0) for variant in product.get("variants", []) if variant.get("price")]
    return min(prices) if prices else product.get("base_price", 0)


def availability_schema_url(product: dict) -> str:
    if normalize_category(product.get("availability")) == "в наличии":
        return "https://schema.org/InStock"
    return "https://schema.org/LimitedAvailability"


def build_local_business_jsonld() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "Русский Лес",
        "url": absolute_url(url_for("home")),
        "logo": absolute_url(url_for("static", filename="images/logo.png")),
        "image": absolute_url(url_for("static", filename="images/hero.png")),
        "telephone": "+7 776 654 65 65",
        "email": "russianwood@inbox.ru",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Айша Биби 387А",
            "addressLocality": "Алматы",
            "addressCountry": "KZ",
        },
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "https://schema.org/Monday",
                    "https://schema.org/Tuesday",
                    "https://schema.org/Wednesday",
                    "https://schema.org/Thursday",
                    "https://schema.org/Friday",
                ],
                "opens": "08:00",
                "closes": "17:00",
            },
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": "https://schema.org/Saturday",
                "opens": "08:00",
                "closes": "14:00",
            },
        ],
        "sameAs": ["https://www.instagram.com/russian__wood/"],
    }


def build_breadcrumb_jsonld(items: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": absolute_url(path),
            }
            for position, (name, path) in enumerate(items, start=1)
        ],
    }


def build_product_jsonld(product: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product["display_name"],
        "description": product.get("description", ""),
        "image": [absolute_url(url_for("static", filename=product["image"]))],
        "sku": str(product.get("id", product["slug"])),
        "category": product.get("category", ""),
        "offers": {
            "@type": "Offer",
            "url": absolute_url(url_for("product", slug=product["slug"])),
            "priceCurrency": "KZT",
            "price": product_price(product),
            "availability": availability_schema_url(product),
            "itemCondition": "https://schema.org/NewCondition",
        },
    }


@app.template_filter("card_image")
def card_image(image_path: str) -> str:
    fallback = "images/hero.png"
    image_path = image_path or fallback
    return CARD_IMAGE_MAP.get(image_path, image_path)


@app.context_processor
def inject_navigation_data():
    seo_indexable = not request.path.startswith("/admin")
    return {
        "navigation_categories": CATEGORIES,
        "whatsapp_url": f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(WHATSAPP_BASIC_MESSAGE, safe='')}",
        "whatsapp_custom_order_url": f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(WHATSAPP_CUSTOM_ORDER_MESSAGE, safe='')}",
        "seo_indexable": seo_indexable,
        "canonical_url": absolute_url(request.path) if seo_indexable else "",
        "google_site_verification": GOOGLE_SITE_VERIFICATION,
        "local_business_jsonld": build_local_business_jsonld() if seo_indexable else None,
    }


@app.route("/sitemap.xml")
def sitemap():
    ElementTree.register_namespace("", SITEMAP_NAMESPACE)
    urlset = ElementTree.Element(f"{{{SITEMAP_NAMESPACE}}}urlset")
    paths = [url_for("home"), url_for("catalog")]
    paths.extend(url_for("category_page", category_slug=item["slug"]) for item in CATEGORY_PAGES)
    paths.extend(url_for("product", slug=product["slug"]) for product in load_products())

    for path in paths:
        url_element = ElementTree.SubElement(urlset, f"{{{SITEMAP_NAMESPACE}}}url")
        location = ElementTree.SubElement(url_element, f"{{{SITEMAP_NAMESPACE}}}loc")
        location.text = absolute_url(path)

    xml = ElementTree.tostring(urlset, encoding="utf-8", xml_declaration=True)
    return Response(xml, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin",
            f"Sitemap: {absolute_url(url_for('sitemap'))}",
            "",
        ]
    )
    return Response(content, mimetype="text/plain")


@app.route("/")
def home():
    products = load_products()
    popular_products = [product for product in products if product.get("popular")]
    if not popular_products:
        popular_products = products[:6]

    return render_template(
        "index.html",
        categories=CATEGORIES,
        products=products,
        popular_products=popular_products[:8],
    )


@app.route("/catalog")
def catalog():
    products = load_products()
    return render_template(
        "catalog.html",
        products=products,
        categories=catalog_categories(products),
        filter_options=catalog_filter_options(products),
        breadcrumb_jsonld=build_breadcrumb_jsonld(
            [
                ("Главная", url_for("home")),
                ("Каталог", url_for("catalog")),
            ]
        ),
    )


@app.route("/product/<slug>")
def product(slug):
    item = next((product for product in load_products() if product.get("slug") == slug), None)
    if item is None:
        abort(404)

    breadcrumbs = [
        ("Главная", url_for("home")),
        ("Каталог", url_for("catalog")),
    ]
    category_meta = CATEGORY_META_MAP.get(normalize_category(item.get("category")))
    if category_meta:
        breadcrumbs.append(
            (
                category_meta["title"],
                url_for("category_page", category_slug=category_meta["slug"]),
            )
        )
    breadcrumbs.append((item["display_name"], url_for("product", slug=item["slug"])))

    return render_template(
        "product.html",
        product=item,
        product_jsonld=build_product_jsonld(item),
        breadcrumb_jsonld=build_breadcrumb_jsonld(breadcrumbs),
    )


@app.route("/<category_slug>-almaty")
def category_page(category_slug):
    category_meta = CATEGORY_PAGE_MAP.get(category_slug)
    if category_meta is None:
        abort(404)

    products = products_by_category(load_products(), category_meta["category"])
    return render_template(
        "category_page.html",
        category=category_meta["category"],
        category_meta=category_meta,
        products=products,
        breadcrumb_jsonld=build_breadcrumb_jsonld(
            [
                ("Главная", url_for("home")),
                ("Каталог", url_for("catalog")),
                (category_meta["title"], url_for("category_page", category_slug=category_meta["slug"])),
            ]
        ),
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = ""

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        error = "Неверный пароль"

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin():
    if not admin_required():
        return redirect_to_login()

    return render_template("admin.html", products=load_products())


@app.route("/admin/product/<slug>/edit", methods=["GET", "POST"])
def admin_edit_product(slug):
    if not admin_required():
        return redirect_to_login()

    products = load_products()
    product_index = next((index for index, item in enumerate(products) if item.get("slug") == slug), None)
    if product_index is None:
        abort(404)

    product_item = products[product_index]

    if request.method == "POST":
        editable_fields = [
            "name",
            "category",
            "wood_type",
            "grade",
            "thickness",
            "width",
            "length",
            "availability",
            "description",
            "image",
            "unit",
        ]

        for field in editable_fields:
            product_item[field] = request.form.get(field, "").strip()

        product_item["base_price"] = parse_price_value(request.form.get("base_price", "0"))

        variants = []
        variant_names = request.form.getlist("variant_name")
        variant_prices = request.form.getlist("variant_price")
        for variant_name, variant_price in zip(variant_names, variant_prices):
            variant_name = variant_name.strip()
            variant_price_value = parse_price_value(variant_price)
            if variant_name and variant_price_value:
                variants.append({"name": variant_name, "price": variant_price_value})

        if product_item.get("variants"):
            product_item["variants"] = variants

        product_item["variant_label"] = build_variant_label(product_item)
        enrich_product_display_fields(product_item)
        update_product_characteristics(product_item)
        products[product_index] = product_item
        save_products(products)

        return redirect(url_for("admin"))

    return render_template("admin_edit_product.html", product=product_item)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
