# -*- coding: utf-8 -*-
"""
LocalWeb VK Outreach — Генератор уникальных персонализированных сообщений (Spintax).
Обеспечивает разнообразие текста для обхода антиспам-фильтров ВКонтакте
и генерирует естественные коммерческие предложения без шаблонности.
"""

import re
import random
from typing import Dict, Any, Optional

def clean_group_name(raw_name: str) -> str:
    """
    Очищает название группы от спам-хвостов, городов, капслока и эмодзи,
    чтобы оно звучало естественно в живом обращении.
    Пример: 'НА БРОНЕ | ПРЕМИУМ ДЕТЕЙЛИНГ | КЕМЕРОВО' -> '«На Броне»'
    """
    if not raw_name:
        return "вашей компании"

    # Удаляем эмодзи и спецсимволы
    clean = re.sub(r'[\U00010000-\U0010ffff]', '', raw_name, flags=re.UNICODE)
    clean = re.sub(r'[\u2600-\u27ff]', '', clean)
    clean = clean.strip()

    # Если есть разделители (| / • - ~), берем первую смысловую часть (обычно это бренд)
    parts = re.split(r'\s*[|/•~—]\s*', clean)
    if parts and len(parts[0].strip()) >= 3:
        clean = parts[0].strip()

    # Удаляем кавычки в начале и конце, если есть
    clean = clean.strip('"\'«»„“')

    # Если текст полностью заглавными буквами и длиннее 4 символов — приводим к Title Case
    if clean.isupper() and len(clean) > 4:
        clean = clean.title()

    if not clean or len(clean) < 2:
        return "вашей компании"

    return f"«{clean}»"

def resolve_spintax(text: str) -> str:
    """
    Рекурсивно раскрывает спинтакс-шаблоны вида {вариант1|вариант2|вариант3}.
    Поддерживает вложенные конструкции: {A|B {C|D}}
    """
    pattern = re.compile(r'\{([^{}]+)\}')
    while True:
        match = pattern.search(text)
        if not match:
            break
        options = match.group(1).split('|')
        chosen = random.choice(options)
        text = text[:match.start()] + chosen + text[match.end():]
    return text

# Семейство шаблонов A: Прямой оффер с акцентом на нулевой риск (тест-драйв за 24ч)
TEMPLATE_ZERO_RISK = """{greeting}! {self_intro}.
{recognition} {clean_name}{city_mention}.

{lead_observation}

{pitch_core} {risk_free} {tech_perk}

{soft_cta}

{signoff}"""

# Семейство шаблонов B: Акцент на потерях клиентов из Яндекс Карт и Поиска
TEMPLATE_SEARCH_TRAFFIC = """{greeting}! {self_intro}.
{search_mention} {clean_name}{city_mention}.

{search_pain} {pitch_core}

{risk_free}
{tech_perk}

{soft_cta}

{signoff}"""

# Семейство шаблонов C: Краткий вежливый вопрос без воды
TEMPLATE_CONCISE = """{greeting}! {self_intro}.
{recognition} {clean_name}. {short_question}

{pitch_core} {risk_free}

{soft_cta}

{signoff}"""

SPINTAX_BLOCKS = {
    "greeting": [
        "Здравствуйте",
        "Добрый день",
        "Приветствую",
        "Доброго дня"
    ],
    "self_intro": [
        "Меня зовут Александр, я частный веб-разработчик",
        "Меня зовут Александр, я руковожу разработкой сайтов в LocalWeb",
        "Меня зовут Александр, я создаю сайты для локального бизнеса",
        "Александр из студии разработки сайтов LocalWeb"
    ],
    "recognition": [
        "Увидел ваше сообщество",
        "Нашел вашу группу в ВК",
        "Обратил внимание на вашу группу",
        "Наткнулся на вашу страницу в поиске ВК"
    ],
    "search_mention": [
        "Искал компании в сфере {niche} и обратил внимание на",
        "Просматривал сообщества по направлению {niche} и нашел",
        "Увидел ваше сообщество"
    ],
    "short_question": [
        "Подскажите, пожалуйста, актуален ли для вас сейчас запуск отдельного сайта для привлечения заявок?",
        "Скажите, рассматриваете ли создание отдельного быстрого сайта для приема клиентов из Яндекса?",
        "Хотел вежливо уточнить: планируете запускать отдельный сайт для клиентов помимо группы ВК?"
    ],
    "pitch_core": [
        "Мы создаем скоростные сайты для сферы {niche} всего за 24 часа.",
        "Разрабатываем современные продающие сайты под ключ за 1 день.",
        "Создаем быстрые мобильные сайты для локального бизнеса за 24 часа."
    ],
    "risk_free": [
        "Формат работы без риска: 0 ₽ предоплаты — сначала я собираю рабочий черновик на смартфоне, и только если вам понравится, оплачивается 7 500 ₽ под ключ.",
        "Работаем без предоплаты: сначала вы оцениваете готовый черновик сайта на своем телефоне, а оплата (7 500 ₽) только по факту утверждения.",
        "Без авансов: сначала готовый черновик через 24 часа, а оплата 7 500 ₽ — строго если результат вас полностью устроит."
    ],
    "tech_perk": [
        "Сайт открывается за 0.8 сек, заявки мгновенно падают вам в Telegram, а хостинг бесплатный навсегда.",
        "Скорость 98/100 в PageSpeed, заявки с сайта приходят прямо в Telegram за секунду, домен .RU оформляется на вас.",
        "Сайт оптимизирован под смартфоны, готов к запуску рекламы в Яндексе, а за хостинг платить не нужно никогда (0 ₽/год)."
    ],
    "search_pain": [
        "Многие потенциальные клиенты ищут {niche} через Яндекс Поиск и Карты, и когда у компании нет быстрого сайта, они часто уходят к конкурентам.",
        "ВКонтакте дает хорошую базу, но платежеспособные клиенты из поиска Яндекса привыкли сразу открывать отдельный сайт с прайсом и записью.",
        "Сейчас значительная часть клиентов приходит из мобильного поиска Яндекса, где без собственного сайта трудно конкурировать."
    ],
    "soft_cta": [
        "Если тема интересна — напишите в ответ «Да» или «+», и я бесплатно подготовлю черновик для вашего дела. Если нет — просто проигнорируйте, больше писать не буду.",
        "Если актуально — ответьте любым словом, и я покажу, как может выглядеть черновик для вас. Если нет — хорошего рабочего дня и приношу извинения за отвлечение!",
        "Подскажите, интересен ли такой вариант без предоплаты? Если да — соберу макет. Если нет — желаю отличных продаж и больше не беспокою.",
        "Если предложение имеет смысл — черкните «Да», вышлю предварительный набросок. Если сейчас не до этого — просто пропустите сообщение."
    ],
    "signoff": [
        "С уважением, Александр (сайт: local-web.ru)",
        "С уважением, Александр | LocalWeb (local-web.ru)",
        "С наилучшими пожеланиями, Александр (local-web.ru)"
    ]
}

def generate_personalized_pitch(group_data: Dict[str, Any], niche: str = "вашей сферы", city: str = "") -> str:
    """
    Генерирует уникальное персонализированное сообщение для конкретного сообщества.
    Адаптирует текст под наличие/отсутствие сайта, город и нишу.
    """
    raw_name = group_data.get("name", "")
    clean_name = clean_group_name(raw_name)
    site = (group_data.get("site") or "").strip().lower()

    # Анализ ситуации с сайтом
    if not site:
        lead_observation_spintax = (
            "{Заметил, что у вас в сообществе не указан отдельный сайт для заявок.|"
            "Обратил внимание, что вы принимаете обращения только через ВК, без собственного сайта.|"
            "Вижу, что у вас отличная группа, но нет отдельного сайта в контактах.}"
        )
    elif any(b in site for b in ["taplink", "vk.link", "tilda.ws", "wixsite", "mssg.me", "linktr.ee"]):
        lead_observation_spintax = (
            "{Заметил, что у вас в контактах прикреплена ссылка на сервис-визитку, которая долго грузится со смартфона.|"
            "Обратил внимание, что вместо полноценного сайта используется базовая страница-визитка, не приспособленная под продвижение в Яндексе.|"
            "Вижу, что у вас привязана ссылка на конструктор, теряющий мобильных клиентов из-за скорости.}"
        )
    else:
        lead_observation_spintax = (
            "{Заметил ваш сайт в контактах группы.|"
            "Обратил внимание на адрес вашего сайта в описании.|"
            "Вижу, что у вас указан сайт, но мы можем предложить современный легкий мобильный лендинг со скоростью загрузки до 1 сек.}"
        )

    # Город
    city_mention = ""
    group_city = group_data.get("city")
    if isinstance(group_city, dict):
        city_name = group_city.get("title", "")
    elif isinstance(group_city, str):
        city_name = group_city
    else:
        city_name = city

    if city_name:
        city_mention = random.choice([
            f" в {city_name}",
            f" ({city_name})",
            ""
        ])

    # Случайный выбор одного из трех семейств шаблонов
    template = random.choice([TEMPLATE_ZERO_RISK, TEMPLATE_SEARCH_TRAFFIC, TEMPLATE_CONCISE])

    # Сборка переменных для шаблона
    rendered = template.format(
        greeting=random.choice(SPINTAX_BLOCKS["greeting"]),
        self_intro=random.choice(SPINTAX_BLOCKS["self_intro"]),
        recognition=random.choice(SPINTAX_BLOCKS["recognition"]),
        search_mention=random.choice(SPINTAX_BLOCKS["search_mention"]).format(niche=niche),
        short_question=random.choice(SPINTAX_BLOCKS["short_question"]),
        clean_name=clean_name,
        city_mention=city_mention,
        lead_observation=lead_observation_spintax,
        pitch_core=random.choice(SPINTAX_BLOCKS["pitch_core"]).format(niche=niche),
        risk_free=random.choice(SPINTAX_BLOCKS["risk_free"]),
        tech_perk=random.choice(SPINTAX_BLOCKS["tech_perk"]),
        search_pain=random.choice(SPINTAX_BLOCKS["search_pain"]).format(niche=niche),
        soft_cta=random.choice(SPINTAX_BLOCKS["soft_cta"]),
        signoff=random.choice(SPINTAX_BLOCKS["signoff"])
    )

    # Раскрываем все вложенные спинтаксы
    final_message = resolve_spintax(rendered)
    
    # Нормализуем переносы строк (не более двух подряд)
    final_message = re.sub(r'\n{3,}', '\n\n', final_message).strip()
    return final_message
