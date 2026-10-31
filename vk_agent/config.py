import os
from datetime import datetime, timedelta

def _load_dotenv():
    # Ищем .env в текущей директории или в родительской (корень проекта)
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
                break
            except Exception:
                pass

_load_dotenv()

# VK API Configuration
# Токен пользователя ВКонтакте с правами: wall,groups,photos,messages,offline
VK_USER_TOKEN = os.getenv("VK_USER_TOKEN", "")

# Версия API ВКонтакте
VK_API_VERSION = "5.199"

# Параметры создаваемого или существующего паблика
# Если GROUP_ID указан (целое число), агент использует существующее сообщество
# Если GROUP_ID пустой или None, агент создаст новый паблик
GROUP_ID = os.getenv("VK_GROUP_ID", None)

# Данные для оформления и описания паблика LocalWeb
PUBLIC_TITLE = "LocalWeb | Сайты для бизнеса за 24ч без предоплаты"
PUBLIC_DESCRIPTION = """Студия разработки сайтов LocalWeb ⚡
Сайт для вашего дела за 24 часа. Сначала рабочий черновик, оплата — потом.

🔥 НАШИ ПРЕИМУЩЕСТВА:
• 0 ₽ предоплата — черновик на вашем смартфоне через 24 часа
• 7 500 ₽ фиксированная цена под ключ (никаких доплат)
• 0 ₽/год за хостинг НАВСЕГДА (чистый быстрый код на Edge CDN)
• 0.8 сек скорость загрузки (98/100 в Google PageSpeed)
• Домен .RU оформляется строго на ваши реквизиты (ИП / ООО / паспорт)
• 100% соблюдение 152-ФЗ РФ (сервер в РФ, чекбокс согласия, чеки ФНС)
• Мгновенные заявки в Telegram-бот за 0.5 сек + онлайн-таблица
• 30 дней гарантии и бесплатных правок после запуска

🌐 Официальный сайт: https://local-web.ru
💬 Связаться с разработчиком в Telegram: @LocalWebRu
🤖 Наш бот приема заявок: @LocalWebRuBot
✉️ Email: jarovenkoaleksander@yandex.ru
📋 Исполнитель: Яровенко А. С. (Самозанятый, ИНН: 420560867537)
"""

PUBLIC_WEBSITE = "https://local-web.ru"
PUBLIC_CATEGORY = 1  # 1 - Компания, организация, веб-сайт
PUBLIC_SUBTYPE = 1   # Компания, организация

# Настройки расписания постов (14 дней)
# Публикация каждый день в указанное время (по умолчанию 11:00 MSK)
POST_HOUR = 11
POST_MINUTE = 0

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CHROME_PATH = os.getenv("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
