import json
import os
import re
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4
from xml.etree import ElementTree

from flask import Flask, Response, abort, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "rus-les-admin-session-key")

BASE_DIR = Path(__file__).resolve().parent
PRODUCTS_PATH = BASE_DIR / "data" / "products.json"
PRODUCT_IMAGES_PATH = BASE_DIR / "static" / "images" / "products"
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345").strip()
SITE_URL = os.getenv("SITE_URL", "").rstrip("/")
GOOGLE_SITE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION", "").strip()
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
WHATSAPP_NUMBER = "77772002742"
WAREHOUSE_ADDRESS = "ул. Волочаевская, 387а / ул. Айша-Биби, 387а"
WAREHOUSE_MAP_QUERY = "Улица Волочаевская, 387а · улица Айша-Биби, 387а"
WAREHOUSE_MAP_URL = f"https://2gis.kz/almaty/search/{quote(WAREHOUSE_MAP_QUERY, safe='')}"
WHATSAPP_BASIC_MESSAGE = (
    "Здравствуйте! Хочу узнать наличие и цену на пиломатериалы. "
    "Подскажите, пожалуйста."
)
WHATSAPP_CUSTOM_ORDER_MESSAGE = (
    "Здравствуйте! Хочу обсудить изделие из дерева под заказ. "
    "Подскажите, пожалуйста, по стоимости и срокам."
)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

SUPPORTED_LANGUAGES = {"ru", "kk"}
TRANSLATIONS = {
    "ru": {
        "language.label": "Язык сайта",
        "menu.open": "Открыть меню",
        "nav.home": "Главная",
        "nav.catalog": "Каталог",
        "nav.wood_products": "Изделия из дерева",
        "nav.about": "О нас",
        "nav.contacts": "Контакты",
        "search.placeholder": "Поиск товара",
        "search.submit": "Найти",
        "info.fast_loading": "Быстрая погрузка",
        "info.schedule": "Пн–Пт 08:00–17:00, Сб до 14:00",
        "info.positions": "Более 300 позиций",
        "info.in_stock": "в наличии на складе",
        "info.phones": "Телефоны",
        "chat.write": "Напишите нам",
        "mobile.navigation": "Быстрая мобильная навигация",
        "mobile.call": "Звонок",
        "footer.contact": "Мы на связи",
        "footer.phone": "Телефон",
        "footer.mobile": "Мобильный",
        "footer.customers": "Покупателям",
        "footer.delivery": "Доставка и самовывоз",
        "footer.returns": "Возврат и обмен",
        "footer.privacy": "Политика конфиденциальности",
        "hero.title": "Склад пиломатериалов в Алматы",
        "hero.description": "OSB, фанера, доска, брус, брусок, вагонка, планкен, покрытия и изделия из дерева в наличии на складе.",
        "hero.whatsapp_hint": "Ответим в WhatsApp",
        "hero.price": "Уточнить наличие и цену",
        "hero.catalog": "Смотреть каталог",
        "hero.map": "Склад на карте",
        "hero.positions": "позиций на складе",
        "hero.fast": "Быстро",
        "hero.loading": "погрузка со склада",
        "hero.units": "считаем в нужной единице",
        "hero.available": "В наличии",
        "hero.address": "Адрес",
        "section.categories": "Основные категории",
        "section.categories_title": "Материалы для стройки, отделки и ухода за деревом",
        "section.selection": "Подбор материала",
        "section.selection_title": "Поможем подобрать материал",
        "section.selection_text": "Не знаете, какой материал выбрать? Подберите по задаче — для бани, фасада, пола, террасы или внутренней отделки стен.",
        "purpose.bath": "Для бани",
        "purpose.bath_text": "Осина, липа, кедр: вагонка, полок и уголок",
        "purpose.facade": "Для фасада",
        "purpose.facade_text": "Планкен, блок-хаус и имитация бруса",
        "purpose.floor": "Для пола и террас",
        "purpose.floor_text": "Половой шпунт, террасная доска, планкен и доска пола",
        "purpose.walls": "Для отделки стен внутри",
        "purpose.walls_text": "Имитация бруса и вагонка для внутренней отделки",
        "section.popular": "Популярное",
        "section.popular_title": "Товары, которые чаще всего спрашивают",
        "product.from": "от",
        "product.details": "Подробнее",
        "custom.eyebrow": "Изделия из дерева",
        "custom.title": "Изделия под заказ для участка, дома и зоны отдыха",
        "custom.text": "Беседки, навесы, лавки, столы, садовые конструкции и декоративные элементы. Обсудим задачу, подберём материал, посчитаем стоимость и сроки.",
        "custom.action": "Обсудить заказ",
        "process.eyebrow": "Как работаем",
        "process.title": "Простой путь от вопроса до отгрузки",
        "process.one_title": "Пишите или звоните",
        "process.one_text": "Расскажите, какой материал нужен и для какой задачи.",
        "process.two_title": "Подбираем вариант",
        "process.two_text": "Сориентируем по наличию, размеру, толщине, сорту и цене.",
        "process.three_title": "Считаем заказ",
        "process.three_text": "Посчитаем по м², погонным метрам, штукам или объёму.",
        "process.four_title": "Отгружаем",
        "process.four_text": "Можно приехать на склад, посмотреть материал и забрать заказ.",
        "about.eyebrow": "О компании",
        "about.title": "Знаем древесину и помогаем выбрать материал без лишнего риска",
        "about.text": "«Русский Лес» работает в Алматы более двух десятилетий. Мы напрямую закупаем пиломатериалы у проверенных российских производителей, правильно храним их на складе и честно помогаем подобрать нужный сорт и размер.",
        "about.years": "года на рынке Казахстана",
        "about.history": "Нас знают мастера и строительные компании ещё со времён базы на Ташкентской-Мира.",
        "about.stock": "позиций в наличии",
        "about.direct": "Напрямую",
        "about.regions": "из северных регионов России",
        "about.inspect": "Материал можно осмотреть до покупки",
        "about.inspect_text": "На складе проще выбрать подходящую сортность, длину и качество древесины.",
        "about.storage": "Правильное хранение",
        "about.storage_text": "Следим, чтобы материал сохранял форму, геометрию и внешний вид.",
        "about.help": "Подбор под вашу задачу",
        "about.help_text": "Поможем выбрать материал для стройки, отделки, бани, фасада или террасы.",
        "about.loading": "Быстрая погрузка",
        "about.loading_text": "После покупки помогаем загрузить материал, чтобы вы не теряли время.",
        "about.visit": "Приезжайте посмотреть материал на складе",
        "about.map": "Открыть карту",
        "catalog.title": "Каталог пиломатериалов",
        "catalog.intro": "Выберите нужный материал, посмотрите варианты и отправьте запрос в WhatsApp. Мы уточним наличие на складе и подготовим расчёт.",
        "catalog.search": "Поиск по названию",
        "catalog.search_placeholder": "Например: OSB, брусок, доска",
        "catalog.filters_categories": "Фильтры и категории",
        "catalog.open": "Открыть",
        "catalog.hide": "Скрыть",
        "catalog.filters": "Фильтры по характеристикам",
        "catalog.reset": "Сбросить фильтры",
        "catalog.thickness": "Толщина",
        "catalog.width": "Ширина",
        "catalog.length": "Длина",
        "catalog.wood": "Порода",
        "catalog.grade": "Сорт",
        "catalog.unit": "Единица",
        "catalog.any_f": "Любая",
        "catalog.any_m": "Любой",
        "catalog.all": "Все товары",
        "catalog.found": "Найдено",
        "catalog.products": "товаров",
        "catalog.sort": "Сортировка",
        "catalog.default": "По умолчанию",
        "catalog.cheaper": "Сначала дешевле",
        "catalog.expensive": "Сначала дороже",
        "catalog.name": "По названию",
        "catalog.availability": "Сначала в наличии",
        "catalog.view": "Вид каталога",
        "catalog.grid": "Сетка",
        "catalog.compact": "Компактно",
        "catalog.list": "Список",
        "catalog.empty": "По вашему запросу товары не найдены. Попробуйте изменить поиск или выбрать другую категорию.",
        "product.back": "Вернуться в каталог",
        "product.specs": "Характеристики",
        "product.variant": "Выберите вариант",
        "product.quantity": "Количество",
        "product.quantity_placeholder": "Например: 10",
        "product.board_calculation": "Расчёт материала по доскам",
        "product.board_calculation_text": "Укажите количество досок и фактическую длину. Калькулятор посчитает площадь и погонные метры.",
        "product.board_count": "Количество досок",
        "product.board_length": "Длина одной доски, м",
        "product.linear": "Погонные метры",
        "product.area": "Площадь",
        "product.price": "Цена",
        "product.total": "Предварительная сумма",
        "product.enter_quantity": "Укажите количество",
        "product.total_formula": "Количество × цена за",
        "product.whatsapp": "Узнать наличие в WhatsApp",
        "category.eyebrow": "Категория",
        "category.extra": "На складе можно уточнить наличие, размеры, сорт и актуальную цену.",
        "category.check": "Уточнить наличие",
        "category.all_catalog": "Смотреть общий каталог",
        "category.suitable": "Подходит для",
        "category.uses": "Где используют этот материал",
        "category.available": "В наличии",
        "category.products": "Товары категории",
        "category.to_catalog": "В каталог",
        "category.order": "Как заказать",
        "category.order_title": "Согласуем наличие, размер и цену перед отгрузкой",
        "category.step_one": "Выберите товар",
        "category.step_one_text": "Откройте карточку или отправьте запрос по категории.",
        "category.step_two": "Напишите в WhatsApp",
        "category.step_two_text": "Уточним остатки, размеры, сорт и цену на складе.",
        "category.step_three": "Приезжайте на склад",
        "category.step_three_text": "Покажем материал и подготовим отгрузку.",
        "category.general_catalog": "Общий каталог",
    },
    "kk": {
        "language.label": "Сайт тілі",
        "menu.open": "Мәзірді ашу",
        "nav.home": "Басты бет",
        "nav.catalog": "Каталог",
        "nav.wood_products": "Ағаш бұйымдары",
        "nav.about": "Біз туралы",
        "nav.contacts": "Байланыс",
        "search.placeholder": "Тауар іздеу",
        "search.submit": "Іздеу",
        "info.fast_loading": "Жылдам тиеу",
        "info.schedule": "Дс–Жм 08:00–17:00, Сб 14:00-ге дейін",
        "info.positions": "300-ден астам тауар",
        "info.in_stock": "қоймада бар",
        "info.phones": "Телефондар",
        "chat.write": "Бізге жазыңыз",
        "mobile.navigation": "Жылдам мобильді навигация",
        "mobile.call": "Қоңырау",
        "footer.contact": "Бізбен байланыс",
        "footer.phone": "Телефон",
        "footer.mobile": "Ұялы телефон",
        "footer.customers": "Сатып алушыларға",
        "footer.delivery": "Жеткізу және алып кету",
        "footer.returns": "Қайтару және айырбастау",
        "footer.privacy": "Құпиялылық саясаты",
        "hero.title": "Алматыдағы ағаш материалдары қоймасы",
        "hero.description": "OSB, фанера, тақтай, брус, рейка, вагонка, планкен, жабындар және ағаш бұйымдары қоймада бар.",
        "hero.whatsapp_hint": "WhatsApp арқылы жауап береміз",
        "hero.price": "Қолжетімділігі мен бағасын нақтылау",
        "hero.catalog": "Каталогты қарау",
        "hero.map": "Қойма картада",
        "hero.positions": "қоймадағы тауар",
        "hero.fast": "Жылдам",
        "hero.loading": "қоймадан тиеу",
        "hero.units": "қажетті бірлікпен есептейміз",
        "hero.available": "Қоймада бар",
        "hero.address": "Мекенжай",
        "section.categories": "Негізгі санаттар",
        "section.categories_title": "Құрылысқа, әрлеуге және ағаш күтіміне арналған материалдар",
        "section.selection": "Материал таңдау",
        "section.selection_title": "Материал таңдауға көмектесеміз",
        "section.selection_text": "Қандай материал таңдау керегін білмейсіз бе? Моншаға, қасбетке, еденге, террасаға немесе ішкі қабырғаларға арналған материалды таңдаңыз.",
        "purpose.bath": "Моншаға",
        "purpose.bath_text": "Көктерек, жөке, самырсын: вагонка, сөре және бұрыш",
        "purpose.facade": "Қасбетке",
        "purpose.facade_text": "Планкен, блок-хаус және брус имитациясы",
        "purpose.floor": "Еден мен террасаға",
        "purpose.floor_text": "Еден тақтасы, террасалық тақта, планкен және еденге арналған тақта",
        "purpose.walls": "Ішкі қабырғаларды әрлеуге",
        "purpose.walls_text": "Ішкі әрлеуге арналған брус имитациясы мен вагонка",
        "section.popular": "Танымал",
        "section.popular_title": "Жиі сұралатын тауарлар",
        "product.from": "бастап",
        "product.details": "Толығырақ",
        "custom.eyebrow": "Ағаш бұйымдары",
        "custom.title": "Аулаға, үйге және демалыс аймағына тапсырыспен жасалатын бұйымдар",
        "custom.text": "Күркелер, бастырмалар, орындықтар, үстелдер, бақша конструкциялары және сәндік элементтер. Міндетті талқылап, материалды таңдап, құны мен мерзімін есептейміз.",
        "custom.action": "Тапсырысты талқылау",
        "process.eyebrow": "Қалай жұмыс істейміз",
        "process.title": "Сұрақтан бастап тиеуге дейінгі қарапайым жол",
        "process.one_title": "Жазыңыз немесе қоңырау шалыңыз",
        "process.one_text": "Қандай материал және қандай мақсатқа қажет екенін айтыңыз.",
        "process.two_title": "Нұсқаны таңдаймыз",
        "process.two_text": "Қоймадағы қор, өлшем, қалыңдық, сұрып және баға бойынша кеңес береміз.",
        "process.three_title": "Тапсырысты есептейміз",
        "process.three_text": "м², погон метр, дана немесе көлем бойынша есептейміз.",
        "process.four_title": "Тиейміз",
        "process.four_text": "Қоймаға келіп, материалды қарап, тапсырысты алып кете аласыз.",
        "about.eyebrow": "Компания туралы",
        "about.title": "Ағашты жақсы білеміз және материалды сенімді таңдауға көмектесеміз",
        "about.text": "«Русский Лес» Алматыда жиырма жылдан астам жұмыс істейді. Біз материалдарды сенімді ресейлік өндірушілерден тікелей сатып алып, қоймада дұрыс сақтаймыз және қажетті сұрып пен өлшемді таңдауға көмектесеміз.",
        "about.years": "Қазақстан нарығында",
        "about.history": "Шеберлер мен құрылыс компаниялары бізді Ташкентская-Мирадағы базамыздан бері біледі.",
        "about.stock": "тауар қоймада бар",
        "about.direct": "Тікелей",
        "about.regions": "Ресейдің солтүстік өңірлерінен",
        "about.inspect": "Материалды сатып алар алдында көруге болады",
        "about.inspect_text": "Қоймада қажетті сұрыпты, ұзындықты және ағаш сапасын таңдау оңай.",
        "about.storage": "Дұрыс сақтау",
        "about.storage_text": "Материалдың пішіні, геометриясы және сыртқы көрінісі сақталуын қадағалаймыз.",
        "about.help": "Мақсатыңызға сай таңдау",
        "about.help_text": "Құрылысқа, әрлеуге, моншаға, қасбетке немесе террасаға материал таңдауға көмектесеміз.",
        "about.loading": "Жылдам тиеу",
        "about.loading_text": "Сатып алғаннан кейін уақыт жоғалтпау үшін материалды тиеуге көмектесеміз.",
        "about.visit": "Материалды қоймаға келіп көріңіз",
        "about.map": "Картаны ашу",
        "catalog.title": "Ағаш материалдарының каталогы",
        "catalog.intro": "Қажетті материалды таңдап, нұсқаларын қарап, WhatsApp арқылы сұрау жіберіңіз. Біз қоймадағы қорды нақтылап, есеп дайындаймыз.",
        "catalog.search": "Атауы бойынша іздеу",
        "catalog.search_placeholder": "Мысалы: OSB, рейка, тақтай",
        "catalog.filters_categories": "Сүзгілер мен санаттар",
        "catalog.open": "Ашу",
        "catalog.hide": "Жасыру",
        "catalog.filters": "Сипаттамалар бойынша сүзгілер",
        "catalog.reset": "Сүзгілерді тазарту",
        "catalog.thickness": "Қалыңдығы",
        "catalog.width": "Ені",
        "catalog.length": "Ұзындығы",
        "catalog.wood": "Ағаш түрі",
        "catalog.grade": "Сұрып",
        "catalog.unit": "Өлшем бірлігі",
        "catalog.any_f": "Кез келген",
        "catalog.any_m": "Кез келген",
        "catalog.all": "Барлық тауарлар",
        "catalog.found": "Табылды",
        "catalog.products": "тауар",
        "catalog.sort": "Сұрыптау",
        "catalog.default": "Әдепкі бойынша",
        "catalog.cheaper": "Алдымен арзаны",
        "catalog.expensive": "Алдымен қымбаты",
        "catalog.name": "Атауы бойынша",
        "catalog.availability": "Алдымен қоймада бары",
        "catalog.view": "Каталог көрінісі",
        "catalog.grid": "Тор",
        "catalog.compact": "Ықшам",
        "catalog.list": "Тізім",
        "catalog.empty": "Сұрауыңыз бойынша тауар табылмады. Іздеуді өзгертіңіз немесе басқа санатты таңдаңыз.",
        "product.back": "Каталогқа оралу",
        "product.specs": "Сипаттамалар",
        "product.variant": "Нұсқаны таңдаңыз",
        "product.quantity": "Саны",
        "product.quantity_placeholder": "Мысалы: 10",
        "product.board_calculation": "Тақтай материалын есептеу",
        "product.board_calculation_text": "Тақтай санын және нақты ұзындығын көрсетіңіз. Калькулятор аудан мен погон метрді есептейді.",
        "product.board_count": "Тақтай саны",
        "product.board_length": "Бір тақтайдың ұзындығы, м",
        "product.linear": "Погон метр",
        "product.area": "Аудан",
        "product.price": "Бағасы",
        "product.total": "Алдын ала сома",
        "product.enter_quantity": "Санын көрсетіңіз",
        "product.total_formula": "Саны × бірлік бағасы",
        "product.whatsapp": "WhatsApp арқылы қорды нақтылау",
        "category.eyebrow": "Санат",
        "category.extra": "Қоймадағы қорды, өлшемді, сұрыпты және өзекті бағаны нақтылауға болады.",
        "category.check": "Қолжетімділігін нақтылау",
        "category.all_catalog": "Жалпы каталогты қарау",
        "category.suitable": "Қолдануға болады",
        "category.uses": "Бұл материал қайда қолданылады",
        "category.available": "Қоймада бар",
        "category.products": "Санат тауарлары",
        "category.to_catalog": "Каталогқа",
        "category.order": "Қалай тапсырыс беруге болады",
        "category.order_title": "Тиеу алдында қорды, өлшемді және бағаны келісеміз",
        "category.step_one": "Тауарды таңдаңыз",
        "category.step_one_text": "Тауар бетін ашыңыз немесе санат бойынша сұрау жіберіңіз.",
        "category.step_two": "WhatsApp арқылы жазыңыз",
        "category.step_two_text": "Қоймадағы қалдықты, өлшемді, сұрыпты және бағаны нақтылаймыз.",
        "category.step_three": "Қоймаға келіңіз",
        "category.step_three_text": "Материалды көрсетіп, тиеуге дайындаймыз.",
        "category.general_catalog": "Жалпы каталог",
    },
}

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

CATEGORY_PAGE_ALIASES = {
    "kleenyy-brus": "brus",
    "polovaya-doska": "doska",
    "sosna-kupit-dosku-v": "doska",
}

INFORMATION_PAGES = {
    "delivery": {
        "title": "Доставка и самовывоз",
        "description": "Условия самовывоза, доставки и погрузки пиломатериалов со склада Русский Лес в Алматы.",
    },
    "returns": {
        "title": "Возврат и обмен товара",
        "description": "Условия возврата и обмена пиломатериалов и товаров компании Русский Лес.",
    },
    "privacy": {
        "title": "Политика конфиденциальности",
        "description": "Информация о сборе, использовании и защите персональных данных посетителей сайта Русский Лес.",
    },
}

LEGACY_REDIRECTS = {
    "about-us": ("home", {"_anchor": "about"}),
    "contacts": ("home", {"_anchor": "contacts"}),
    "projects": ("home", {"_anchor": "wood-products"}),
    "услуги": ("home", {"_anchor": "wood-products"}),
    "vozvrat": ("information_page", {"page_slug": "returns"}),
    "job-openings": ("home", {"_anchor": "contacts"}),
    "les-v-almaty-catalog": ("catalog", {}),
    "shop-1": ("catalog", {}),
    "shop-9": ("catalog", {}),
    "shop-12": ("catalog", {}),
    "blank-1": ("catalog", {}),
    "blank-2": ("catalog", {}),
    "blank-3": ("catalog", {}),
    "blank-5": ("catalog", {}),
    "kupit-les-v-almaty-2": ("catalog", {}),
    "fanera-almaty": ("category_page", {"category_slug": "fanera"}),
    "vagonka-almaty": ("category_page", {"category_slug": "vagonka"}),
    "mebelnyy-shchit-almaty": ("category_page", {"category_slug": "mebelnyy-shchit"}),
    "kleenyy-brus-almaty": ("category_page", {"category_slug": "brus"}),
    "balk": ("category_page", {"category_slug": "brus"}),
    "polovaya-doska-almaty": ("category_page", {"category_slug": "doska"}),
    "sosna-kupit-dosku-v-almaty": ("category_page", {"category_slug": "doska"}),
    "coatings": ("catalog", {"category": "покрытия"}),
    "farbitex-profi-wood": ("catalog", {"category": "покрытия"}),
    "eurotex": ("catalog", {"category": "покрытия"}),
    "woodmaster": ("catalog", {"category": "покрытия"}),
    "aquatex-kupit-v-almaty": ("catalog", {"category": "покрытия"}),
}


def normalize_category(value: str) -> str:
    return (value or "").casefold()


def current_language() -> str:
    language = session.get("language", "ru")
    return language if language in SUPPORTED_LANGUAGES else "ru"


def translate(key: str) -> str:
    language = current_language()
    return TRANSLATIONS.get(language, {}).get(key, TRANSLATIONS["ru"].get(key, key))


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


def image_file_extension(filename: str) -> str:
    return Path(filename or "").suffix.lower().lstrip(".")


def image_signature_matches(file, extension: str) -> bool:
    header = file.stream.read(12)
    file.stream.seek(0)
    signatures = {
        "jpg": header.startswith(b"\xff\xd8\xff"),
        "jpeg": header.startswith(b"\xff\xd8\xff"),
        "png": header.startswith(b"\x89PNG\r\n\x1a\n"),
        "webp": header.startswith(b"RIFF") and header[8:12] == b"WEBP",
    }
    return signatures.get(extension, False)


def save_product_image(file, product_slug: str) -> str:
    extension = image_file_extension(file.filename)
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Можно загружать только JPG, PNG или WEBP.")

    if not image_signature_matches(file, extension):
        raise ValueError("Выбранный файл не является корректным изображением.")

    PRODUCT_IMAGES_PATH.mkdir(parents=True, exist_ok=True)
    safe_slug = secure_filename(product_slug) or "product"
    normalized_extension = "jpg" if extension == "jpeg" else extension
    filename = f"{safe_slug}-{uuid4().hex[:10]}.{normalized_extension}"
    file.save(PRODUCT_IMAGES_PATH / filename)
    return f"images/products/{filename}"


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
        "telephone": "+7 777 200 27 42",
        "email": "russianwood@inbox.ru",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": WAREHOUSE_ADDRESS,
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
    language = current_language()
    whatsapp_message = WHATSAPP_BASIC_MESSAGE
    custom_order_message = WHATSAPP_CUSTOM_ORDER_MESSAGE
    if language == "kk":
        whatsapp_message = (
            "Сәлеметсіз бе! Ағаш материалдарының қолжетімділігі мен бағасын "
            "білгім келеді. Кеңес беріңізші."
        )
        custom_order_message = (
            "Сәлеметсіз бе! Тапсырыспен жасалатын ағаш бұйымын талқылағым келеді. "
            "Бағасы мен мерзімі туралы ақпарат беріңізші."
        )

    return {
        "lang": language,
        "t": translate,
        "navigation_categories": CATEGORIES,
        "whatsapp_number": WHATSAPP_NUMBER,
        "warehouse_address": WAREHOUSE_ADDRESS,
        "warehouse_map_url": WAREHOUSE_MAP_URL,
        "whatsapp_url": f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(whatsapp_message, safe='')}",
        "whatsapp_custom_order_url": f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(custom_order_message, safe='')}",
        "seo_indexable": seo_indexable,
        "canonical_url": absolute_url(request.path) if seo_indexable else "",
        "google_site_verification": GOOGLE_SITE_VERIFICATION,
        "local_business_jsonld": build_local_business_jsonld() if seo_indexable else None,
    }


@app.route("/language/<language>")
def set_language(language):
    if language not in SUPPORTED_LANGUAGES:
        abort(404)

    session["language"] = language
    target = request.referrer or url_for("home")
    if not target.startswith(request.host_url):
        target = url_for("home")
    return redirect(target)


@app.route("/sitemap.xml")
def sitemap():
    ElementTree.register_namespace("", SITEMAP_NAMESPACE)
    urlset = ElementTree.Element(f"{{{SITEMAP_NAMESPACE}}}urlset")
    paths = [url_for("home"), url_for("catalog")]
    paths.extend(url_for("category_page", category_slug=item["slug"]) for item in CATEGORY_PAGES)
    paths.extend(url_for("product", slug=product["slug"]) for product in load_products())
    paths.extend(url_for("information_page", page_slug=slug) for slug in INFORMATION_PAGES)

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
    category_alias = CATEGORY_PAGE_ALIASES.get(category_slug)
    if category_alias:
        return redirect(url_for("category_page", category_slug=category_alias), code=301)

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


@app.route("/info/<page_slug>")
def information_page(page_slug):
    page = INFORMATION_PAGES.get(page_slug)
    if page is None:
        abort(404)

    return render_template(
        "information_page.html",
        page=page,
        page_slug=page_slug,
        breadcrumb_jsonld=build_breadcrumb_jsonld(
            [
                ("Главная", url_for("home")),
                (page["title"], url_for("information_page", page_slug=page_slug)),
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
    upload_error = ""

    if request.method == "POST":
        uploaded_image = request.files.get("image_file")
        uploaded_image_path = ""
        if uploaded_image and uploaded_image.filename:
            try:
                uploaded_image_path = save_product_image(uploaded_image, slug)
            except ValueError as error:
                upload_error = str(error)

        if upload_error:
            return render_template(
                "admin_edit_product.html",
                product=product_item,
                upload_error=upload_error,
            ), 400

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

        if uploaded_image_path:
            product_item["image"] = uploaded_image_path

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

    return render_template("admin_edit_product.html", product=product_item, upload_error=upload_error)


@app.route("/product-page/<path:legacy_slug>")
def legacy_product_page(legacy_slug):
    search_query = re.sub(r"[-_]+", " ", legacy_slug).strip()
    return redirect(url_for("catalog", q=search_query), code=301)


@app.route("/<path:legacy_path>")
def legacy_page_redirect(legacy_path):
    redirect_config = LEGACY_REDIRECTS.get(legacy_path.strip("/"))
    if redirect_config is None:
        abort(404)

    endpoint, values = redirect_config
    return redirect(url_for(endpoint, **values), code=301)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
