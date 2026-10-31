import os
import subprocess
import time
import sys

# Обеспечиваем безопасный вывод UTF-8 в консоли Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from .config import CHROME_PATH, ASSETS_DIR

def render_html_to_png(html_content: str, output_path: str, width: int, height: int) -> bool:
    """Рендерит HTML-шаблон в PNG-изображение через Chrome Headless."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    temp_html = output_path + ".temp.html"
    
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={width},{height}",
        f"--screenshot={output_path}",
        os.path.abspath(temp_html)
    ]

    try:
        subprocess.run(cmd, check=True)
        if os.path.exists(temp_html):
            os.remove(temp_html)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        if os.path.exists(temp_html):
            os.remove(temp_html)
        print(f"Ошибка рендеринга изображения {output_path}: {e}")
        return False

# Базовый CSS для всех макетов в корпоративном стиле LocalWeb
BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #F8FAFC;
    background-image: radial-gradient(rgba(148, 163, 184, 0.22) 1.2px, transparent 1.2px);
    background-size: 24px 24px;
    color: #0F172A;
    -webkit-font-smoothing: antialiased;
    overflow: hidden;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon {
    width: 44px; height: 44px; border-radius: 13px;
    background: #2563EB; display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 900; font-size: 20px;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
}
.brand-icon svg { width: 24px; height: 24px; fill: none; stroke: currentColor; stroke-width: 2.5; }
.brand-name { font-size: 28px; font-weight: 900; letter-spacing: -0.6px; color: #0F172A; }
.brand-name span { color: #2563EB; }
.pill-blue {
    display: inline-flex; align-items: center; gap: 8px;
    background: #EFF6FF; color: #2563EB; border: 1.5px solid #BFDBFE;
    padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0.5px;
}
.pill-green {
    display: inline-flex; align-items: center; gap: 8px;
    background: #ECFDF5; color: #059669; border: 1.5px solid #A7F3D0;
    padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 800;
}
.pill-dot { width: 8px; height: 8px; border-radius: 50%; background: #10B981; box-shadow: 0 0 8px #10B981; }
.bento-card {
    background: #FFFFFF; border: 1.5px solid #E2E8F0; border-radius: 18px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
}
"""

def generate_avatar(output_path: str = None) -> str:
    """Генерирует аватар сообщества (800x800) с идеальным центрированием под круг ВК."""
    if output_path is None:
        output_path = os.path.join(ASSETS_DIR, "avatar.png")

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        {BASE_CSS}
        body {{
            width: 800px; height: 800px;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            position: relative;
        }}
        .circle-safe {{
            width: 680px; height: 680px; border-radius: 50%;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            background: rgba(255, 255, 255, 0.7);
            border: 2px dashed rgba(37, 99, 235, 0.2);
            box-shadow: 0 20px 60px rgba(37, 99, 235, 0.1);
            backdrop-filter: blur(8px);
            padding: 40px;
        }}
        .avatar-logo {{
            width: 140px; height: 140px; border-radius: 36px;
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 900; font-size: 64px;
            box-shadow: 0 16px 40px rgba(37, 99, 235, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.3);
            margin-bottom: 28px;
        }}
        .avatar-title {{
            font-size: 54px; font-weight: 900; letter-spacing: -1.5px;
            color: #0F172A; margin-bottom: 12px;
        }}
        .avatar-title span {{ color: #2563EB; }}
        .avatar-sub {{
            font-size: 20px; font-weight: 600; color: #64748B;
            margin-bottom: 28px; letter-spacing: -0.2px; text-align: center;
        }}
        .badges-row {{
            display: flex; gap: 12px; align-items: center; justify-content: center;
        }}
        .badge-mvp {{
            background: #ECFDF5; color: #059669; border: 2px solid #A7F3D0;
            padding: 10px 22px; border-radius: 30px; font-size: 17px; font-weight: 800;
            display: flex; align-items: center; gap: 8px;
        }}
        .badge-price {{
            background: #EFF6FF; color: #2563EB; border: 2px solid #BFDBFE;
            padding: 10px 22px; border-radius: 30px; font-size: 17px; font-weight: 800;
        }}
    </style>
</head>
<body>
    <div class="circle-safe">
        <div class="avatar-logo">
            <svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="16 18 22 12 16 6"></polyline>
                <polyline points="8 6 2 12 8 18"></polyline>
            </svg>
        </div>
        <div class="avatar-title">Local<span>Web</span></div>
        <div class="avatar-sub">Студия разработки сайтов для бизнеса</div>
        <div class="badges-row">
            <div class="badge-mvp">
                <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#10B981;"></span>
                24ч Черновик (0 ₽)
            </div>
            <div class="badge-price">7 500 ₽ под ключ</div>
        </div>
    </div>
</body>
</html>"""
    render_html_to_png(html, output_path, 800, 800)
    return output_path

def generate_public_cover(output_path: str = None) -> str:
    """Генерирует главную обложку сообщества (1920x768) с полным брендингом и мокапом."""
    if output_path is None:
        output_path = os.path.join(ASSETS_DIR, "public_cover.png")

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        {BASE_CSS}
        body {{
            width: 1920px; height: 768px;
            display: flex; flex-direction: column;
            justify-content: space-between;
            padding: 44px 80px 36px 80px;
        }}
        .cover-header {{
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid #E2E8F0; padding-bottom: 20px;
        }}
        .brand-icon {{ width: 54px; height: 54px; border-radius: 16px; font-size: 26px; }}
        .brand-icon svg {{ width: 30px; height: 30px; }}
        .brand-name {{ font-size: 36px; }}
        .cover-body {{
            display: flex; justify-content: space-between; align-items: center;
            gap: 60px; margin: 30px 0;
        }}
        .left-col {{
            flex: 1.3; display: flex; flex-direction: column; justify-content: center;
        }}
        .top-notice {{
            display: inline-flex; align-items: center; gap: 8px;
            background: #EFF6FF; color: #2563EB; border: 1.5px solid #BFDBFE;
            padding: 8px 18px; border-radius: 20px; font-size: 16px; font-weight: 800;
            width: fit-content; margin-bottom: 18px;
        }}
        .headline {{
            font-size: 50px; font-weight: 900; letter-spacing: -1.6px;
            color: #0F172A; line-height: 1.15; margin-bottom: 14px;
        }}
        .headline-sub {{
            font-size: 20px; color: #475569; font-weight: 500; line-height: 1.45;
            margin-bottom: 30px; max-width: 950px;
        }}
        .stats-grid {{
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;
        }}
        .stat-card {{
            background: white; border: 2px solid #E2E8F0; border-radius: 20px;
            padding: 20px 24px; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
            display: flex; flex-direction: column; justify-content: center;
        }}
        .stat-card.blue {{ border-color: #2563EB; background: #F8FAFF; }}
        .stat-card.green {{ border-color: #10B981; background: #F6FEF9; }}
        .stat-num {{
            font-size: 38px; font-weight: 900; letter-spacing: -1px; margin-bottom: 4px;
        }}
        .stat-label {{
            font-size: 15px; font-weight: 700; color: #64748B;
        }}
        .right-col {{
            flex: 0.7; display: flex; justify-content: center; align-items: center;
        }}
        .phone-mockup {{
            width: 320px; background: white; border: 7px solid #0F172A;
            border-radius: 40px; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
            overflow: hidden; padding: 18px; display: flex; flex-direction: column; gap: 14px;
        }}
        .phone-notch {{
            width: 90px; height: 16px; background: #0F172A; border-radius: 10px;
            margin: 0 auto 6px auto;
        }}
        .phone-header {{
            display: flex; justify-content: space-between; align-items: center;
            font-size: 14px; font-weight: 900;
        }}
        .phone-card {{
            background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 14px;
            padding: 14px; font-size: 13px;
        }}
        .phone-btn {{
            background: #2563EB; color: white; text-align: center;
            padding: 12px; border-radius: 12px; font-weight: 800; font-size: 14px;
        }}
        .phone-speed {{
            background: #ECFDF5; border: 1px solid #A7F3D0; color: #059669;
            text-align: center; padding: 10px; border-radius: 10px; font-weight: 800; font-size: 13px;
        }}
        .cover-footer {{
            display: flex; justify-content: space-between; align-items: center;
            border-top: 2px solid #E2E8F0; padding-top: 18px; font-size: 17px; color: #475569;
        }}
        .cover-footer strong {{ color: #0F172A; }}
    </style>
</head>
<body>
    <div class="cover-header">
        <div class="brand">
            <div class="brand-icon">
                <svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
            </div>
            <div class="brand-name">Local<span>Web</span></div>
        </div>
        <div style="display: flex; gap: 16px; align-items: center;">
            <div class="pill-green"><span class="pill-dot"></span> Осталось 2 слота на этой неделе</div>
            <div class="pill-blue">ОФИЦИАЛЬНЫЙ ПАБЛИК 2026</div>
        </div>
    </div>

    <div class="cover-body">
        <div class="left-col">
            <div class="top-notice">⚡ Без предоплаты и затягивания сроков</div>
            <h1 class="headline">Сайт для вашего дела за 24 часа.<br>Сначала рабочий черновик, оплата — потом.</h1>
            <p class="headline-sub">Разрабатываем понятные, быстрые сайты для локального бизнеса с лидогенерацией в Telegram и 100% соблюдением законов РФ. Без абонентских плат за конструкторы.</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-num" style="color: #2563EB;">24 часа</div>
                    <div class="stat-label">Готовый сайт до оплаты</div>
                </div>
                <div class="stat-card green">
                    <div class="stat-num" style="color: #059669;">0 ₽</div>
                    <div class="stat-label">Предоплата на старте</div>
                </div>
                <div class="stat-card blue">
                    <div class="stat-num" style="color: #2563EB;">7 500 ₽</div>
                    <div class="stat-label">Финал под ключ</div>
                </div>
            </div>
        </div>

        <div class="right-col">
            <div class="phone-mockup">
                <div class="phone-notch"></div>
                <div class="phone-header">
                    <span>LocalWeb</span>
                    <span style="color:#059669; font-size:12px;">🟢 24ч MVP</span>
                </div>
                <div class="phone-card">
                    <strong style="font-size:15px; color:#0F172A;">Автосервис "Драйв"</strong>
                    <div style="color:#64748B; margin-top:2px;">Кузовной ремонт и ТО</div>
                    <div style="color:#2563EB; font-weight:800; margin-top:8px;">✓ Диагностика 0 ₽</div>
                    <div style="color:#64748B; font-size:11px;">Гарантия на работы 1 год</div>
                </div>
                <div class="phone-btn">Записаться в WhatsApp</div>
                <div class="phone-speed">⚡ Загрузка: 0.8с (98/100)</div>
                <div style="text-align:center; font-size:12px; color:#64748B; font-weight:600;">📱 Тест на смартфоне</div>
            </div>
        </div>
    </div>

    <div class="cover-footer">
        <div>Официальный сайт: <strong>local-web.ru</strong> • Студия разработки сайтов LocalWeb</div>
        <div>Связаться с разработчиком: <strong>@LocalWebRu</strong> • Бот заявок: <strong>@LocalWebRuBot</strong></div>
    </div>
</body>
</html>"""
    render_html_to_png(html, output_path, 1920, 768)
    return output_path

# Генерация 14 карточек для постов (1080x1080)
def generate_post_card(post_data: dict, output_path: str) -> str:
    """Генерирует высококонверсионную инфографику 1080x1080 для конкретного поста."""
    day = post_data["day"]
    title = post_data["title"]
    tag = post_data.get("tag", "LOCALWEB")
    badge = post_data.get("badge", "2026")

    # Формируем уникальный визуальный контент в центре в зависимости от дня
    center_content = ""

    if day == 1:
        # Соцсеть vs Личный сайт
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px;">
            <div class="bento-card" style="padding: 28px; border-color: #FECDD3; background: #FFF1F2;">
                <div style="font-size: 20px; font-weight: 900; color: #E11D48; margin-bottom: 16px;">❌ Только соцсеть:</div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 14px; font-size: 17px; font-weight: 600; color: #4C0519;">
                    <li>• Внезапные блокировки аккаунта</li>
                    <li>• Умная лента режет охваты до 5%</li>
                    <li>• Клиенты из Яндекса уходят к другим</li>
                    <li>• Часы пустых переписок в ЛС</li>
                </ul>
            </div>
            <div class="bento-card" style="padding: 28px; border-color: #A7F3D0; background: #ECFDF5;">
                <div style="font-size: 20px; font-weight: 900; color: #059669; margin-bottom: 16px;">✓ Свой сайт на домене:</div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 14px; font-size: 17px; font-weight: 600; color: #064E3B;">
                    <li>• Ваша 100% собственность 24/7</li>
                    <li>• Заявки из Яндекс Поиска и Карт</li>
                    <li>• Прайс и фото отвечают за вас</li>
                    <li>• Доверие и статус компании</li>
                </ul>
            </div>
        </div>
        """
    elif day == 2:
        # 3 шага тест-драйва
        center_content = """
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 30px;">
            <div class="bento-card" style="padding: 24px; text-align: left;">
                <div class="pill-green" style="font-size: 12px; margin-bottom: 12px;">Шаг 1 • БЕЗ РИСКА</div>
                <div style="font-size: 20px; font-weight: 900; margin-bottom: 10px;">Бриф за 10 мин</div>
                <div style="color: #64748B; font-size: 15px; line-height: 1.4;">Расскажите о бизнесе голосом или текстом в Telegram.</div>
                <div style="font-size: 22px; font-weight: 900; color: #059669; margin-top: 16px;">0 ₽ предоплата</div>
            </div>
            <div class="bento-card" style="padding: 24px; text-align: left; border-color: #2563EB;">
                <div class="pill-blue" style="font-size: 12px; margin-bottom: 12px;">Шаг 2 • ТЕСТ-ДРАЙВ</div>
                <div style="font-size: 20px; font-weight: 900; margin-bottom: 10px;">Черновик за 24ч</div>
                <div style="color: #64748B; font-size: 15px; line-height: 1.4;">Открываете готовый сайт прямо на своем смартфоне.</div>
                <div style="font-size: 22px; font-weight: 900; color: #2563EB; margin-top: 16px;">Ровно 24 часа</div>
            </div>
            <div class="bento-card" style="padding: 24px; text-align: left;">
                <div class="pill-green" style="font-size: 12px; margin-bottom: 12px;">Шаг 3 • РЕШЕНИЕ</div>
                <div style="font-size: 20px; font-weight: 900; margin-bottom: 10px;">Запуск / Отказ</div>
                <div style="color: #64748B; font-size: 15px; line-height: 1.4;">Понравилось — 7 500 ₽ и домен. Не подошло — 0 ₽.</div>
                <div style="font-size: 22px; font-weight: 900; color: #0F172A; margin-top: 16px;">100% гарантия</div>
            </div>
        </div>
        """
    elif day == 3:
        # Таблица сравнения
        center_content = """
        <div class="bento-card" style="margin-top: 24px; overflow: hidden; padding: 0;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 16px;">
                <tr style="background: #F1F5F9; border-bottom: 2px solid #E2E8F0;">
                    <th style="padding: 16px 20px;">Критерий</th>
                    <th style="padding: 16px 20px; color: #2563EB;">LocalWeb 🟢</th>
                    <th style="padding: 16px 20px;">Конструкторы (Tilda)</th>
                    <th style="padding: 16px 20px;">Веб-студии</th>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 14px 20px; font-weight: 700;">Предоплата</td>
                    <td style="padding: 14px 20px; color: #059669; font-weight: 800;">0 ₽ (черновик)</td>
                    <td style="padding: 14px 20px; color: #64748B;">Своими руками / от 25к</td>
                    <td style="padding: 14px 20px; color: #64748B;">50–100% (от 40к)</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 14px 20px; font-weight: 700;">Срок сборки</td>
                    <td style="padding: 14px 20px; color: #2563EB; font-weight: 800;">24 часа</td>
                    <td style="padding: 14px 20px; color: #64748B;">Недели мучений</td>
                    <td style="padding: 14px 20px; color: #64748B;">3–8 недель</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 14px 20px; font-weight: 700;">Хостинг/год</td>
                    <td style="padding: 14px 20px; color: #059669; font-weight: 800;">0 ₽ НАВСЕГДА</td>
                    <td style="padding: 14px 20px; color: #E11D48;">От 9 000 ₽/год</td>
                    <td style="padding: 14px 20px; color: #E11D48;">От 6 000 ₽/год</td>
                </tr>
                <tr>
                    <td style="padding: 14px 20px; font-weight: 700;">Скорость</td>
                    <td style="padding: 14px 20px; color: #059669; font-weight: 800;">0.8 сек (98/100)</td>
                    <td style="padding: 14px 20px; color: #64748B;">3–5 сек (тяжело)</td>
                    <td style="padding: 14px 20px; color: #64748B;">Как повезет</td>
                </tr>
            </table>
        </div>
        """
    elif day == 4:
        # Speed & PageSpeed
        center_content = """
        <div style="display: flex; gap: 24px; align-items: center; margin-top: 24px;">
            <div class="bento-card" style="flex: 1; padding: 36px; text-align: center; border-color: #10B981; background: #F6FEF9;">
                <div style="font-size: 15px; font-weight: 800; color: #059669; margin-bottom: 10px;">GOOGLE PAGESPEED INSIGHTS</div>
                <div style="font-size: 96px; font-weight: 900; color: #059669; line-height: 1;">98</div>
                <div style="font-size: 20px; font-weight: 700; color: #64748B; margin-top: 6px;">из 100 баллов</div>
            </div>
            <div style="flex: 1.2; display: flex; flex-direction: column; gap: 16px;">
                <div class="bento-card" style="padding: 22px 26px;">
                    <div style="font-size: 32px; font-weight: 900; color: #2563EB;">0.4 сек</div>
                    <div style="font-size: 15px; font-weight: 700; color: #64748B;">Рендеринг первого экрана на смартфоне</div>
                </div>
                <div class="bento-card" style="padding: 22px 26px;">
                    <div style="font-size: 32px; font-weight: 900; color: #059669;">0.8 сек</div>
                    <div style="font-size: 15px; font-weight: 700; color: #64748B;">Полная загрузка интерактивной страницы</div>
                </div>
            </div>
        </div>
        """
    elif day == 5:
        # 152-ФЗ Роскомнадзор
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 24px;">
            <div class="bento-card" style="padding: 24px;">
                <div style="font-size: 32px; margin-bottom: 10px;">🇷🇺</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 6px;">Сервер в РФ (Москва)</div>
                <div style="color: #64748B; font-size: 14px;">Первичная фиксация данных клиентов строго в ЦОД РФ (ч. 5 ст. 18 152-ФЗ).</div>
            </div>
            <div class="bento-card" style="padding: 24px;">
                <div style="font-size: 32px; margin-bottom: 10px;">📝</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 6px;">Чекбоксы под формы</div>
                <div style="color: #64748B; font-size: 14px;">Юридически точная политика и явное согласие пользователя под каждой кнопкой.</div>
            </div>
            <div class="bento-card" style="padding: 24px;">
                <div style="font-size: 32px; margin-bottom: 10px;">🛡️</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 6px;">72ч очистка логов</div>
                <div style="color: #64748B; font-size: 14px;">Данные не накапливаются в открытых базах — удаление сразу после доставки.</div>
            </div>
            <div class="bento-card" style="padding: 24px;">
                <div style="font-size: 32px; margin-bottom: 10px;">🧾</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 6px;">Чеки ФНС для учета</div>
                <div style="color: #64748B; font-size: 14px;">Работа по ФЗ № 422, чеки с QR-кодом для снижения налога ИП и ООО.</div>
            </div>
        </div>
        """
    elif day == 6:
        # Заявки в Telegram за 0.5с
        center_content = """
        <div style="display: flex; gap: 24px; align-items: center; margin-top: 24px;">
            <div class="bento-card" style="flex: 1.2; padding: 26px; border-color: #2563EB; background: #F8FAFF;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <span style="font-size: 14px; font-weight: 900; color: #2563EB;">LW LocalWeb Bot</span>
                    <span style="font-size: 12px; color: #64748B;">только что • 0.5с</span>
                </div>
                <div style="font-size: 18px; font-weight: 900; color: #0F172A; margin-bottom: 10px;">🚀 НОВАЯ ЗАЯВКА С САЙТА!</div>
                <div style="font-size: 15px; line-height: 1.6; color: #334155;">
                    👤 <b>Клиент:</b> Алексей Смирнов<br>
                    🏢 <b>Компания:</b> Автосервис "Механика"<br>
                    📞 <b>Телефон / TG:</b> @smirnov_auto<br>
                    📝 <b>Задача:</b> Запуск сайта к открытию бокса
                </div>
            </div>
            <div style="flex: 0.9; display: flex; flex-direction: column; gap: 14px;">
                <div class="bento-card" style="padding: 16px 20px;">
                    <div style="font-weight: 800; color: #059669;">📊 Google Sheets / Excel</div>
                    <div style="font-size: 13px; color: #64748B; margin-top: 4px;">Автозапись в общую таблицу</div>
                </div>
                <div class="bento-card" style="padding: 16px 20px;">
                    <div style="font-weight: 800; color: #2563EB;">✉️ Резерв на Email</div>
                    <div style="font-size: 13px; color: #64748B; margin-top: 4px;">Дубликат руководителю</div>
                </div>
                <div class="bento-card" style="padding: 16px 20px;">
                    <div style="font-weight: 800; color: #D97706;">🪤 Honeypot-фильтр</div>
                    <div style="font-size: 13px; color: #64748B; margin-top: 4px;">100% защита от спама</div>
                </div>
            </div>
        </div>
        """
    elif day == 7:
        # Домен .RU собственность
        center_content = """
        <div class="bento-card" style="padding: 34px; margin-top: 24px; text-align: left; background: #FFFFFF; border-color: #2563EB;">
            <div class="pill-blue" style="margin-bottom: 16px;">ГОСУДАРСТВЕННЫЙ РЕЕСТР РУНЕТА (ТЦИ)</div>
            <div style="font-size: 32px; font-weight: 900; color: #0F172A; margin-bottom: 14px;">Оформление строго на ваши реквизиты</div>
            <div style="font-size: 18px; color: #475569; line-height: 1.5; margin-bottom: 24px;">
                Мы принципиально не оформляем домен клиента на себя. Вы — единственный официальный администратор имени: на ИП, ООО или паспорт физлица.
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;">
                <div style="background: #F8FAFC; border-radius: 12px; padding: 14px; font-size: 14px; font-weight: 700; color: #334155;">
                    ✓ 4 DNS сервера
                </div>
                <div style="background: #F8FAFC; border-radius: 12px; padding: 14px; font-size: 14px; font-weight: 700; color: #334155;">
                    ✓ Бесплатный SSL (HTTPS)
                </div>
                <div style="background: #F8FAFC; border-radius: 12px; padding: 14px; font-size: 14px; font-weight: 700; color: #334155;">
                    ✓ Продление от ~190 ₽/год
                </div>
            </div>
        </div>
        """
    elif day == 8:
        # Всё включено 7 500 ₽ (8 пунктов)
        center_content = """
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 24px;">
            <div class="bento-card" style="padding: 16px;">
                <div style="font-size: 18px; font-weight: 900; color: #2563EB;">01</div>
                <div style="font-weight: 800; font-size: 14px; margin-top: 4px;">Landing Page</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Под ключ под вашу нишу</div>
            </div>
            <div class="bento-card" style="padding: 16px;">
                <div style="font-size: 18px; font-weight: 900; color: #2563EB;">02</div>
                <div style="font-weight: 800; font-size: 14px; margin-top: 4px;">Mobile-First</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Кнопки под палец</div>
            </div>
            <div class="bento-card" style="padding: 16px;">
                <div style="font-size: 18px; font-weight: 900; color: #2563EB;">03</div>
                <div style="font-weight: 800; font-size: 14px; margin-top: 4px;">Копирайтинг</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Понятные тексты без воды</div>
            </div>
            <div class="bento-card" style="padding: 16px;">
                <div style="font-size: 18px; font-weight: 900; color: #2563EB;">04</div>
                <div style="font-weight: 800; font-size: 14px; margin-top: 4px;">Telegram-бот</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Заявки за 0.5 сек</div>
            </div>
            <div class="bento-card" style="padding: 16px;">
                <div style="font-size: 18px; font-weight: 900; color: #10B981;">05</div>
                <div style="font-weight: 800; font-size: 14px; margin-top: 4px;">Хостинг 0 ₽</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Навсегда на Edge CDN</div>
            </div>
            <div class="bento-card" style="padding: 16px;">
                <div style="font-size: 18px; font-weight: 900; color: #10B981;">06</div>
                <div style="font-weight: 800; font-size: 14px; margin-top: 4px;">Домен .RU</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Строго на ваши данные</div>
            </div>
            <div class="bento-card" style="padding: 16px;">
                <div style="font-size: 18px; font-weight: 900; color: #10B981;">07</div>
                <div style="font-weight: 800; font-size: 14px; margin-top: 4px;">152-ФЗ РФ</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Сервер в РФ + чеки</div>
            </div>
            <div class="bento-card" style="padding: 16px;">
                <div style="font-size: 18px; font-weight: 900; color: #10B981;">08</div>
                <div style="font-weight: 800; font-size: 14px; margin-top: 4px;">30 дней</div>
                <div style="font-size: 12px; color: #64748B; margin-top: 4px;">Бесплатной гарантии</div>
            </div>
        </div>
        """
    elif day == 9:
        # Кейс
        center_content = """
        <div style="display: flex; gap: 24px; align-items: center; margin-top: 24px;">
            <div class="bento-card" style="flex: 1; padding: 28px; background: #0F172A; color: white;">
                <div class="pill-green" style="font-size: 12px; margin-bottom: 12px;">АВТОСЕРВИС "ДРАЙВ"</div>
                <div style="font-size: 28px; font-weight: 900; margin-bottom: 10px;">Окупаемость за 3 дня</div>
                <div style="color: #94A3B8; font-size: 15px; line-height: 1.5;">Сайт с понятным прайсом и онлайн-записью через WhatsApp окупил 7 500 ₽ уже со второго клиента.</div>
            </div>
            <div style="flex: 1; display: flex; flex-direction: column; gap: 14px;">
                <div class="bento-card" style="padding: 18px 24px;">
                    <div style="font-size: 30px; font-weight: 900; color: #059669;">+35% записей</div>
                    <div style="font-size: 14px; color: #64748B; font-weight: 600;">Конверсия из Яндекс Карт и 2GIS</div>
                </div>
                <div class="bento-card" style="padding: 18px 24px;">
                    <div style="font-size: 30px; font-weight: 900; color: #2563EB;">-70% времени</div>
                    <div style="font-size: 14px; color: #64748B; font-weight: 600;">Меньше пустых звонков с расспросами</div>
                </div>
            </div>
        </div>
        """
    elif day == 10:
        # Honeypot
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px;">
            <div class="bento-card" style="padding: 30px; text-align: center; border-color: #10B981; background: #F6FEF9;">
                <div style="font-size: 64px; margin-bottom: 8px;">👤</div>
                <div style="font-size: 24px; font-weight: 900; color: #059669; margin-bottom: 8px;">0 капчи для людей</div>
                <div style="color: #64748B; font-size: 15px;">Никаких светофоров и гидрантов. Клиент отправляет заявку за 5 секунд.</div>
            </div>
            <div class="bento-card" style="padding: 30px; text-align: center; border-color: #2563EB; background: #F8FAFF;">
                <div style="font-size: 64px; margin-bottom: 8px;">🤖</div>
                <div style="font-size: 24px; font-weight: 900; color: #2563EB; margin-bottom: 8px;">100% блок спам-ботов</div>
                <div style="color: #64748B; font-size: 15px;">Скрытая honeypot-ловушка отсекает ботов на стороне сервера.</div>
            </div>
        </div>
        """
    elif day == 11:
        # Чеки ФНС
        center_content = """
        <div class="bento-card" style="padding: 32px; margin-top: 24px; border-color: #10B981; background: #FFFFFF;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div class="pill-green">422-ФЗ • САМОЗАНЯТОСТЬ</div>
                <div style="font-weight: 900; color: #0F172A; font-size: 18px;">ФНС РОССИИ 🧾</div>
            </div>
            <div style="font-size: 26px; font-weight: 900; color: #0F172A; margin-bottom: 12px;">
                Электронный фискальный чек с QR-кодом
            </div>
            <div style="font-size: 17px; color: #475569; line-height: 1.5; margin-bottom: 20px;">
                Официальные расходы для ИП и ООО. Уменьшает налог на прибыль или УСН. Исполнитель зарегистрирован в официальном реестре налоговой РФ.
            </div>
            <div style="background: #F8FAFC; border-radius: 12px; padding: 14px 20px; font-size: 15px; font-weight: 700; color: #334155;">
                Яровенко А. С. • ИНН: 420560867537 • 100% белая сделка
            </div>
        </div>
        """
    elif day == 12:
        # 30 дней гарантии
        center_content = """
        <div style="display: flex; gap: 24px; align-items: center; margin-top: 24px;">
            <div class="bento-card" style="flex: 1; padding: 34px; text-align: center; border-color: #2563EB; background: #F8FAFF;">
                <div style="font-size: 72px; font-weight: 900; color: #2563EB; line-height: 1;">30</div>
                <div style="font-size: 22px; font-weight: 900; color: #0F172A; margin-top: 8px;">ДНЕЙ ГАРАНТИИ</div>
                <div style="color: #64748B; font-size: 15px; margin-top: 4px;">Бесплатные правки после сдачи</div>
            </div>
            <div style="flex: 1.3; display: flex; flex-direction: column; gap: 14px;">
                <div class="bento-card" style="padding: 18px 22px; font-weight: 700; color: #334155;">
                    ✓ Бесплатно обновим цены и прайс-лист
                </div>
                <div class="bento-card" style="padding: 18px 22px; font-weight: 700; color: #334155;">
                    ✓ Добавим новые фото работ и отзывы
                </div>
                <div class="bento-card" style="padding: 18px 22px; font-weight: 700; color: #334155;">
                    ✓ По одному сообщению в Telegram без счетов
                </div>
            </div>
        </div>
        """
    elif day == 13:
        # Чеклист
        center_content = """
        <div class="bento-card" style="padding: 24px; margin-top: 24px; display: flex; flex-direction: column; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 12px; font-size: 17px; font-weight: 700; color: #0F172A;">
                <span style="color:#059669; font-size:22px;">✓</span> 1. Скорость загрузки до 1.0 секунды
            </div>
            <div style="display: flex; align-items: center; gap: 12px; font-size: 17px; font-weight: 700; color: #0F172A;">
                <span style="color:#059669; font-size:22px;">✓</span> 2. Кнопки звонка и WhatsApp под большой палец
            </div>
            <div style="display: flex; align-items: center; gap: 12px; font-size: 17px; font-weight: 700; color: #0F172A;">
                <span style="color:#059669; font-size:22px;">✓</span> 3. Мгновенная доставка заявок в Telegram
            </div>
            <div style="display: flex; align-items: center; gap: 12px; font-size: 17px; font-weight: 700; color: #0F172A;">
                <span style="color:#059669; font-size:22px;">✓</span> 4. Прозрачный прайс-лист без "цена по запросу"
            </div>
            <div style="display: flex; align-items: center; gap: 12px; font-size: 17px; font-weight: 700; color: #0F172A;">
                <span style="color:#059669; font-size:22px;">✓</span> 5. 100% соблюдение 152-ФЗ РФ и сервер в Москве
            </div>
        </div>
        """
    else:
        # Day 14: CTA
        center_content = """
        <div class="bento-card" style="padding: 34px; margin-top: 24px; text-align: center; border-color: #2563EB; background: #F8FAFF;">
            <div class="pill-green" style="margin-bottom: 16px;">⚡ ОСТАЛОСЬ 2 СЛОТА НА ЭТОЙ НЕДЕЛЕ</div>
            <div style="font-size: 34px; font-weight: 900; color: #0F172A; margin-bottom: 14px;">
                Черновик вашего сайта уже завтра
            </div>
            <div style="font-size: 18px; color: #475569; max-width: 700px; margin: 0 auto 24px auto;">
                Напишите нам в Telegram и коротко расскажите о своем деле. Через 24 часа смотрите результат на смартфоне. 0 ₽ предоплаты.
            </div>
            <div style="display: inline-flex; align-items: center; gap: 12px; background: #2563EB; color: white; padding: 16px 36px; border-radius: 16px; font-size: 20px; font-weight: 800;">
                Написать в Telegram: @LocalWebRu
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        {BASE_CSS}
        body {{
            width: 1080px; height: 1080px;
            display: flex; flex-direction: column;
            justify-content: space-between;
            padding: 56px 64px 44px 64px;
        }}
        .header {{
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 2px solid #E2E8F0; padding-bottom: 22px;
        }}
        .headline {{
            font-size: 38px; font-weight: 900; letter-spacing: -1.2px;
            color: #0F172A; line-height: 1.22; margin-top: 28px;
        }}
        .footer {{
            display: flex; justify-content: space-between; align-items: center;
            border-top: 2px solid #E2E8F0; padding-top: 22px; font-size: 18px; color: #64748B;
        }}
        .footer strong {{ color: #0F172A; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="brand">
            <div class="brand-icon">
                <svg viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
            </div>
            <div class="brand-name">Local<span>Web</span></div>
        </div>
        <div style="display: flex; gap: 14px; align-items: center;">
            <div class="pill-blue">{tag}</div>
            <div class="pill-green"><span class="pill-dot"></span> ДЕНЬ {day:02d} / 14</div>
        </div>
    </div>

    <div style="flex: 1; display: flex; flex-direction: column; justify-content: center;">
        <h1 class="headline">{title}</h1>
        {center_content}
    </div>

    <div class="footer">
        <div>Официальный сайт: <strong>local-web.ru</strong></div>
        <div>Связаться с разработчиком: <strong>@LocalWebRu</strong></div>
    </div>
</body>
</html>"""

    render_html_to_png(html, output_path, 1080, 1080)
    return output_path

def generate_all_assets() -> dict:
    """Генерирует все графические материалы: аватар, обложку и 14 постов."""
    print("[ASSETS] Генерация графических материалов LocalWeb...")
    from .content_plan import POSTS

    os.makedirs(ASSETS_DIR, exist_ok=True)
    generated = {
        "avatar": generate_avatar(),
        "cover": generate_public_cover(),
        "posts": []
    }
    print("[OK] Аватар сообщества сгенерирован (800x800).")
    print("[OK] Обложка сообщества сгенерирована (1920x768).")

    for p in POSTS:
        filename = p.get("image_file", f"post_{p['day']:02d}.png")
        card_path = os.path.join(ASSETS_DIR, filename)
        generate_post_card(p, card_path)
        generated["posts"].append(card_path)
        print(f"[OK] Карточка поста День {p['day']:02d} сгенерирована (1080x1080).")

    print(f"[SUCCESS] Все {len(generated['posts']) + 2} визуальных ассета успешно сгенерированы в {ASSETS_DIR}!")
    return generated
