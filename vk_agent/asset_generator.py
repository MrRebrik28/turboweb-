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

# Генерация карточек для постов (1080x1080)
def generate_post_card(post_data: dict, output_path: str, total_days: int = 30) -> str:
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
    elif day == 14:
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
    elif day == 15:
        # Перенос с Tilda и Wix
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px;">
            <div class="bento-card" style="padding: 28px; border-color: #FECDD3; background: #FFF1F2;">
                <div style="font-size: 14px; font-weight: 800; color: #E11D48; margin-bottom: 8px;">КОНСТРУКТОР (TILDA / WIX)</div>
                <div style="font-size: 44px; font-weight: 900; color: #E11D48; line-height: 1.1; margin-bottom: 14px;">~45 000 ₽</div>
                <div style="font-size: 15px; font-weight: 700; color: #881337; margin-bottom: 14px;">расход за 3 года аренды</div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 10px; font-size: 15px; font-weight: 600; color: #4C0519;">
                    <li>• Не заплатил — сайт отключили</li>
                    <li>• Загрузка 3–5 сек на смартфоне</li>
                    <li>• Код и платформа вам не принадлежат</li>
                </ul>
            </div>
            <div class="bento-card" style="padding: 28px; border-color: #A7F3D0; background: #ECFDF5;">
                <div style="font-size: 14px; font-weight: 800; color: #059669; margin-bottom: 8px;">ПЕРЕНОС НА ЧИСТЫЙ КОД</div>
                <div style="font-size: 44px; font-weight: 900; color: #059669; line-height: 1.1; margin-bottom: 14px;">5 500 ₽</div>
                <div style="font-size: 15px; font-weight: 700; color: #065F46; margin-bottom: 14px;">разово • хостинг 0 ₽ навсегда</div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 10px; font-size: 15px; font-weight: 600; color: #064E3B;">
                    <li>• Скорость взлетает до 0.8 сек</li>
                    <li>• Ваш дизайн сохраняется на 100%</li>
                    <li>• Подключим Telegram-бот и 152-ФЗ</li>
                </ul>
            </div>
        </div>
        """
    elif day == 16:
        # Многостраничный сайт до 5 страниц
        center_content = """
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 24px;">
            <div class="bento-card" style="padding: 22px; border-color: #2563EB; background: #F8FAFF;">
                <div class="pill-blue" style="font-size: 11px; margin-bottom: 10px;">СТРАНИЦА 1</div>
                <div style="font-size: 19px; font-weight: 900; margin-bottom: 6px;">Главная + УТП</div>
                <div style="font-size: 14px; color: #64748B; line-height: 1.4;">Навигация, оффер, доверие и форма заявки в Telegram.</div>
            </div>
            <div class="bento-card" style="padding: 22px;">
                <div class="pill-green" style="font-size: 11px; margin-bottom: 10px;">СТРАНИЦЫ 2–4</div>
                <div style="font-size: 19px; font-weight: 900; margin-bottom: 6px;">Разделы услуг</div>
                <div style="font-size: 14px; color: #64748B; line-height: 1.4;">Отдельные SEO-адреса (/repair, /price) для топа Яндекса и Директа.</div>
            </div>
            <div class="bento-card" style="padding: 22px;">
                <div class="pill-blue" style="font-size: 11px; margin-bottom: 10px;">СТРАНИЦА 5</div>
                <div style="font-size: 19px; font-weight: 900; margin-bottom: 6px;">Прайс и контакты</div>
                <div style="font-size: 14px; color: #64748B; line-height: 1.4;">Полный прайс-лист, карта проезда, реквизиты и 152-ФЗ.</div>
            </div>
        </div>
        <div class="bento-card" style="padding: 20px 28px; margin-top: 16px; display: flex; justify-content: space-between; align-items: center; background: #0F172A; color: white;">
            <div style="font-size: 19px; font-weight: 800;">Многостраничник под ключ (до 5 стр.) + Хостинг 0 ₽</div>
            <div style="font-size: 28px; font-weight: 900; color: #34D399;">14 900 ₽</div>
        </div>
        """
    elif day == 17:
        # Квиз-сайт
        center_content = """
        <div style="display: flex; gap: 22px; align-items: stretch; margin-top: 24px;">
            <div class="bento-card" style="flex: 1.25; padding: 26px; border-color: #2563EB; background: #F8FAFF;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                    <span class="pill-blue" style="font-size: 11px;">ШАГ 2 ИЗ 4 • КАЛЬКУЛЯТОР</span>
                    <span style="font-weight: 800; font-size: 13px; color: #059669;">Скидка +10%</span>
                </div>
                <div style="font-size: 21px; font-weight: 900; color: #0F172A; margin-bottom: 16px;">Какой объём работ планируется?</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div style="padding: 12px 14px; border-radius: 10px; border: 2px solid #2563EB; background: #EFF6FF; font-weight: 800; font-size: 14px; color: #1D4ED8;">✓ До 30 м²</div>
                    <div style="padding: 12px 14px; border-radius: 10px; border: 1.5px solid #CBD5E1; background: #FFFFFF; font-weight: 600; font-size: 14px; color: #475569;">30 – 60 м²</div>
                    <div style="padding: 12px 14px; border-radius: 10px; border: 1.5px solid #CBD5E1; background: #FFFFFF; font-weight: 600; font-size: 14px; color: #475569;">60 – 100 м²</div>
                    <div style="padding: 12px 14px; border-radius: 10px; border: 1.5px solid #CBD5E1; background: #FFFFFF; font-weight: 600; font-size: 14px; color: #475569;">Нужен замер</div>
                </div>
            </div>
            <div style="flex: 0.9; display: flex; flex-direction: column; justify-content: space-between; gap: 14px;">
                <div class="bento-card" style="padding: 20px; border-color: #10B981; background: #ECFDF5;">
                    <div style="font-size: 28px; font-weight: 900; color: #059669;">До 2× выше</div>
                    <div style="font-size: 14px; font-weight: 700; color: #065F46; margin-top: 4px;">Конверсия по сравнению с формой «Заказать звонок»</div>
                </div>
                <div class="bento-card" style="padding: 20px;">
                    <div style="font-size: 26px; font-weight: 900; color: #2563EB;">9 900 ₽</div>
                    <div style="font-size: 14px; font-weight: 600; color: #64748B; margin-top: 4px;">Готовая анкета с параметрами сразу в Telegram</div>
                </div>
            </div>
        </div>
        """
    elif day == 18:
        # Яндекс Карты + сайт
        center_content = """
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 24px;">
            <div class="bento-card" style="padding: 24px;">
                <div style="font-size: 32px; margin-bottom: 10px;">📍</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 8px;">1. Яндекс Карты и 2ГИС</div>
                <div style="font-size: 14px; color: #64748B; line-height: 1.45;">Клиент ищет услугу рядом, читает отзывы и жмёт кнопку «Сайт».</div>
            </div>
            <div class="bento-card" style="padding: 24px; border-color: #2563EB; background: #F8FAFF;">
                <div style="font-size: 32px; margin-bottom: 10px;">⚡</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 8px;">2. Быстрый сайт (0.8с)</div>
                <div style="font-size: 14px; color: #64748B; line-height: 1.45;">Показывает чёткий прайс, фото работ и доверие без зависаний.</div>
            </div>
            <div class="bento-card" style="padding: 24px; border-color: #10B981; background: #ECFDF5;">
                <div style="font-size: 32px; margin-bottom: 10px;">📲</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 8px;">3. Заявка за 0.5 сек</div>
                <div style="font-size: 14px; color: #065F46; line-height: 1.45;">Контакт падает вам в Telegram. 0 ₽ расходов на платные клики!</div>
            </div>
        </div>
        <div class="bento-card" style="padding: 18px 26px; margin-top: 16px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 17px; font-weight: 800; color: #0F172A;">Упаковка карточки Яндекс Карт / 2ГИС под ключ</span>
            <span class="pill-blue" style="font-size: 16px;">4 500 ₽</span>
        </div>
        """
    elif day == 19:
        # Разбор ошибок: 200 товаров на одностраничнике
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 24px;">
            <div class="bento-card" style="padding: 24px; border-color: #FECDD3; background: #FFF1F2;">
                <div style="font-size: 18px; font-weight: 900; color: #E11D48; margin-bottom: 14px;">🚩 Красные флаги реального аудита:</div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 11px; font-size: 15px; font-weight: 600; color: #4C0519;">
                    <li>• 213 товаров запихнули в 1 лендинг</li>
                    <li>• HTML-код раздулся до ~900 КБ</li>
                    <li>• Тег &lt;H1&gt; повесили на номер телефона</li>
                    <li>• Нет URL-страниц под модели в Яндексе</li>
                    <li>• Пустая «рыба» в политике 152-ФЗ</li>
                </ul>
            </div>
            <div class="bento-card" style="padding: 24px; border-color: #A7F3D0; background: #ECFDF5;">
                <div style="font-size: 18px; font-weight: 900; color: #059669; margin-bottom: 14px;">✓ Как должно быть:</div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 11px; font-size: 15px; font-weight: 600; color: #064E3B;">
                    <li>• Свой URL и карточка под разделы/модели</li>
                    <li>• Лёгкие страницы (загрузка за 0.8 сек)</li>
                    <li>• Правильная иерархия H1 → H2 → H3</li>
                    <li>• Органический трафик из поиска РФ</li>
                    <li>• Заполненные реквизиты оператора 152-ФЗ</li>
                </ul>
            </div>
        </div>
        """
    elif day == 20:
        # SEO ошибки (H1, Description, Sitemap)
        center_content = """
        <div style="display: flex; flex-direction: column; gap: 14px; margin-top: 22px;">
            <div class="bento-card" style="padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; border-color: #FECDD3;">
                <div>
                    <div style="font-size: 17px; font-weight: 900; color: #E11D48;">Ошибка 1: &lt;h1&gt;+7 (950) 000-00-00&lt;/h1&gt;</div>
                    <div style="font-size: 14px; color: #64748B;">Заголовок H1 вешают на телефон или логотип. Поисковик не понимает тему сайта.</div>
                </div>
                <div class="pill-green">Лечим</div>
            </div>
            <div class="bento-card" style="padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; border-color: #FECDD3;">
                <div>
                    <div style="font-size: 17px; font-weight: 900; color: #E11D48;">Ошибка 2: Пустые Title, Description и H2/H3</div>
                    <div style="font-size: 14px; color: #64748B;">В выдаче Яндекса выводится случайный обрывок текста вместо УТП и цены.</div>
                </div>
                <div class="pill-green">Лечим</div>
            </div>
            <div class="bento-card" style="padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; border-color: #2563EB; background: #F8FAFF;">
                <div>
                    <div style="font-size: 18px; font-weight: 900; color: #0F172A;">Базовое SEO + Яндекс Метрика + Вебмастер под ключ</div>
                    <div style="font-size: 14px; color: #64748B;">sitemap.xml, robots.txt, Schema.org, цели и проверка индексации</div>
                </div>
                <div style="font-size: 26px; font-weight: 900; color: #2563EB;">3 000 ₽</div>
            </div>
        </div>
        """
    elif day == 21:
        # Яндекс Директ слив бюджета
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 24px;">
            <div class="bento-card" style="padding: 26px; border-color: #FECDD3; background: #FFF1F2;">
                <div style="font-size: 48px; font-weight: 900; color: #E11D48; line-height: 1;">-40%</div>
                <div style="font-size: 18px; font-weight: 900; color: #881337; margin: 10px 0;">кликов уходит впустую</div>
                <div style="font-size: 15px; color: #4C0519; line-height: 1.45;">Если сайт в рекламе грузится 4+ секунды или в Метрике не настроены реальные цели, Директ просто сливает деньги.</div>
            </div>
            <div class="bento-card" style="padding: 26px; border-color: #A7F3D0; background: #ECFDF5;">
                <div style="font-size: 48px; font-weight: 900; color: #059669; line-height: 1;">0.8 с</div>
                <div style="font-size: 18px; font-weight: 900; color: #065F46; margin: 10px 0;">скорость посадочной LocalWeb</div>
                <div style="font-size: 15px; color: #064E3B; line-height: 1.45;">Автостратегии Директа сразу обучаются на цели <code style="font-weight:800;">lead_form_submit</code> и снижают цену заявки.</div>
            </div>
        </div>
        """
    elif day == 22:
        # OpenGraph и брендовые превью
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 24px;">
            <div class="bento-card" style="padding: 26px; background: #F1F5F9; border-color: #CBD5E1;">
                <div style="font-size: 13px; font-weight: 800; color: #64748B; margin-bottom: 14px;">❌ ОБЫЧНЫЙ САЙТ В ТЕЛЕГРАМЕ:</div>
                <div style="background: white; padding: 16px; border-radius: 12px; border-left: 4px solid #94A3B8;">
                    <div style="font-size: 13px; color: #2563EB; text-decoration: underline;">https://old-site-123.ru</div>
                    <div style="font-size: 16px; font-weight: 700; color: #334155; margin-top: 6px;">Index | Без названия</div>
                    <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">Картинка отсутствует... Политика... 2019</div>
                </div>
            </div>
            <div class="bento-card" style="padding: 26px; background: #EFF6FF; border-color: #2563EB;">
                <div style="font-size: 13px; font-weight: 800; color: #2563EB; margin-bottom: 14px;">✓ СТАНДАРТ LOCALWEB (OPENGRAPH):</div>
                <div style="background: white; padding: 16px; border-radius: 12px; border-left: 4px solid #2563EB; box-shadow: 0 6px 18px rgba(37,99,235,0.12);">
                    <div style="height: 82px; border-radius: 8px; background: linear-gradient(135deg, #1D4ED8, #2563EB); color: white; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 20px; margin-bottom: 10px;">
                        Брендовая обложка 1200×630
                    </div>
                    <div style="font-size: 15px; font-weight: 900; color: #0F172A;">Сильный заголовок + УТП + Город</div>
                    <div style="font-size: 12px; color: #475569; margin-top: 4px;">SVG-фавикон и микроразметка Schema.org в комплекте</div>
                </div>
            </div>
        </div>
        """
    elif day == 23:
        # 152-ФЗ пустая заглушка
        center_content = """
        <div style="display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 22px; margin-top: 24px;">
            <div class="bento-card" style="padding: 24px; border-color: #FECDD3; background: #FFF1F2;">
                <div style="font-size: 15px; font-weight: 900; color: #E11D48; margin-bottom: 12px;">⚠️ ОПАСНЫЙ ШАБЛОН КОНСТРУКТОРА:</div>
                <div style="background: white; border: 1px dashed #F43F5E; padding: 16px; border-radius: 12px; font-size: 15px; color: #4C0519; line-height: 1.55;">
                    «...настоящим даю своё согласие <mark style="background:#FFE4E6; padding:2px 6px; font-weight:800;">НАЗВАНИЕ КОМПАНИИ</mark> на сайте <mark style="background:#FFE4E6; padding:2px 6px; font-weight:800;">http://(адрес сайта)</mark>...»
                </div>
                <div style="font-size: 14px; font-weight: 700; color: #881337; margin-top: 12px;">Юридически ничтожно по ст. 9 152-ФЗ!</div>
            </div>
            <div class="bento-card" style="padding: 24px; border-color: #A7F3D0; background: #ECFDF5; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="font-size: 18px; font-weight: 900; color: #059669; margin-bottom: 8px;">✓ Настройка 152-ФЗ РФ</div>
                    <div style="font-size: 14px; color: #064E3B; line-height: 1.45;">Реальные реквизиты вашего ИП/ООО, чекбоксы под каждой формой и ссылка в подвале.</div>
                </div>
                <div style="font-size: 32px; font-weight: 900; color: #059669; margin-top: 16px;">2 500 ₽</div>
            </div>
        </div>
        """
    elif day == 24:
        # Яндекс Метрика и Вебвизор 2.0
        center_content = """
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-top: 24px;">
            <div class="bento-card" style="padding: 24px;">
                <div style="font-size: 32px; margin-bottom: 10px;">🎥</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 8px;">Вебвизор 2.0</div>
                <div style="font-size: 14px; color: #64748B; line-height: 1.45;">Видеозапись каждого визита: видно, где клиент остановился или не понял цену.</div>
            </div>
            <div class="bento-card" style="padding: 24px;">
                <div style="font-size: 32px; margin-bottom: 10px;">🔥</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 8px;">Карта кликов</div>
                <div style="font-size: 14px; color: #64748B; line-height: 1.45;">Показывает, какие кнопки и разделы работают лучше всего.</div>
            </div>
            <div class="bento-card" style="padding: 24px; border-color: #2563EB; background: #F8FAFF;">
                <div style="font-size: 32px; margin-bottom: 10px;">🎯</div>
                <div style="font-size: 18px; font-weight: 900; margin-bottom: 8px;">Цели по JS</div>
                <div style="font-size: 14px; color: #1E40AF; line-height: 1.45;">Точный учёт каждой заявки и обучение алгоритмов Директа.</div>
            </div>
        </div>
        """
    elif day == 25:
        # Telegram-бот интеграция за 3 500
        center_content = """
        <div style="display: flex; gap: 22px; align-items: center; margin-top: 24px;">
            <div class="bento-card" style="flex: 1.1; padding: 26px; border-color: #2563EB; background: #F8FAFF;">
                <div class="pill-blue" style="margin-bottom: 14px;">ДЛЯ ЛЮБОГО ГОТОВОГО САЙТА</div>
                <div style="font-size: 24px; font-weight: 900; color: #0F172A; margin-bottom: 10px;">Заявки больше не падают в спам</div>
                <div style="font-size: 15px; color: #475569; line-height: 1.5;">Подключим приём форм в Telegram за 0.5 сек + автозапись в Google Таблицу + Honeypot-фильтр от спама.</div>
            </div>
            <div class="bento-card" style="flex: 0.75; padding: 28px; text-align: center; border-color: #10B981; background: #ECFDF5;">
                <div style="font-size: 14px; font-weight: 800; color: #059669; margin-bottom: 8px;">ПОД КЛЮЧ ЗА 1 ДЕНЬ</div>
                <div style="font-size: 46px; font-weight: 900; color: #059669; line-height: 1;">3 500 ₽</div>
                <div style="font-size: 14px; font-weight: 600; color: #065F46; margin-top: 10px;">Без переделки вашего текущего сайта</div>
            </div>
        </div>
        """
    elif day == 26:
        # ТОП-5 ниш
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 22px;">
            <div class="bento-card" style="padding: 16px 20px;">
                <div style="font-weight: 900; font-size: 17px; color: #0F172A;">🚗 1. Автосервисы и детейлинг</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">Средний чек 5 000 – 45 000 ₽</div>
            </div>
            <div class="bento-card" style="padding: 16px 20px;">
                <div style="font-weight: 900; font-size: 17px; color: #0F172A;">🛠️ 2. Ремонт, сантехника, электрика</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">Средний чек 8 000 – 200 000+ ₽</div>
            </div>
            <div class="bento-card" style="padding: 16px 20px;">
                <div style="font-weight: 900; font-size: 17px; color: #0F172A;">💆 3. Бьюти-студии и клиники</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">LTV клиента 25 000 – 100 000 ₽/год</div>
            </div>
            <div class="bento-card" style="padding: 16px 20px;">
                <div style="font-weight: 900; font-size: 17px; color: #0F172A;">⚖️ 4. Юристы, бухгалтеры, B2B</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">Доверие и статус с первого экрана</div>
            </div>
        </div>
        <div class="bento-card" style="padding: 16px 24px; margin-top: 14px; display: flex; justify-content: space-between; align-items: center; border-color: #10B981; background: #ECFDF5;">
            <div style="font-weight: 900; font-size: 17px; color: #064E3B;">🧹 5. Локальный сервис (клининг, доставка, мастера)</div>
            <div style="font-weight: 900; font-size: 18px; color: #059669;">Окупается с 1–2 заказов</div>
        </div>
        """
    elif day == 27:
        # Миф о бесплатном сайте своими руками
        center_content = """
        <div class="bento-card" style="margin-top: 24px; overflow: hidden; padding: 0;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 16px;">
                <tr style="background: #F1F5F9; border-bottom: 2px solid #E2E8F0;">
                    <th style="padding: 16px 20px;">Скрытая статья расходов</th>
                    <th style="padding: 16px 20px; color: #E11D48;">«Сам на конструкторе»</th>
                    <th style="padding: 16px 20px; color: #059669;">LocalWeb под ключ</th>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 14px 20px; font-weight: 700;">Подключение домена .RU и SSL</td>
                    <td style="padding: 14px 20px; color: #64748B;">Только на платном тарифе</td>
                    <td style="padding: 14px 20px; color: #059669; font-weight: 800;">Включено в 7 500 ₽</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 14px 20px; font-weight: 700;">Плата за платформу (год)</td>
                    <td style="padding: 14px 20px; color: #E11D48; font-weight: 800;">9 000 – 15 000 ₽/год</td>
                    <td style="padding: 14px 20px; color: #059669; font-weight: 800;">0 ₽ НАВСЕГДА</td>
                </tr>
                <tr>
                    <td style="padding: 14px 20px; font-weight: 700;">Ваше личное время</td>
                    <td style="padding: 14px 20px; color: #64748B;">15–30 часов вечерами</td>
                    <td style="padding: 14px 20px; color: #2563EB; font-weight: 800;">10 минут на бриф</td>
                </tr>
            </table>
        </div>
        """
    elif day == 28:
        # Mobile-First
        center_content = """
        <div style="display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 24px; margin-top: 24px;">
            <div class="bento-card" style="padding: 28px; text-align: center; border-color: #2563EB; background: #F8FAFF;">
                <div style="font-size: 72px; font-weight: 900; color: #2563EB; line-height: 1;">85%</div>
                <div style="font-size: 18px; font-weight: 900; color: #0F172A; margin-top: 10px;">клиентов заходят со смартфона</div>
                <div style="font-size: 14px; color: #64748B; margin-top: 6px;">с Яндекс Карт, поиска и рекламы в дороге</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div class="bento-card" style="padding: 16px 20px; font-weight: 700; font-size: 15px; color: #0F172A;">✓ Крупные кнопки звонка и Telegram под палец</div>
                <div class="bento-card" style="padding: 16px 20px; font-weight: 700; font-size: 15px; color: #0F172A;">✓ Контрастный прайс без зумирования</div>
                <div class="bento-card" style="padding: 16px 20px; font-weight: 700; font-size: 15px; color: #0F172A;">✓ Ноль горизонтальных переполнений</div>
                <div class="bento-card" style="padding: 16px 20px; font-weight: 700; font-size: 15px; color: #059669;">✓ Моментальный тест на вашем телефоне за 24ч</div>
            </div>
        </div>
        """
    elif day == 29:
        # Партнерская программа
        center_content = """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 24px;">
            <div class="bento-card" style="padding: 24px; border-color: #2563EB; background: #F8FAFF;">
                <div class="pill-blue" style="margin-bottom: 12px;">МОДЕЛЬ А • АГЕНТСКАЯ</div>
                <div style="font-size: 28px; font-weight: 900; color: #2563EB; margin-bottom: 12px;">20% с каждого заказа</div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 15px; font-weight: 700; color: #1E293B;">
                    <li>• Лендинг (7 500 ₽) ➔ <span style="color:#059669;">+1 500 ₽</span></li>
                    <li>• Сайт-квиз (9 900 ₽) ➔ <span style="color:#059669;">+2 000 ₽</span></li>
                    <li>• Многостраничник ➔ <span style="color:#059669;">+3 000 ₽</span></li>
                </ul>
            </div>
            <div class="bento-card" style="padding: 24px; border-color: #10B981; background: #ECFDF5;">
                <div class="pill-green" style="margin-bottom: 12px;">МОДЕЛЬ Б • WHITE LABEL</div>
                <div style="font-size: 28px; font-weight: 900; color: #059669; margin-bottom: 12px;">Опт от 6 000 ₽</div>
                <div style="font-size: 15px; font-weight: 600; color: #064E3B; line-height: 1.5;">
                    Продавайте сайт под своим брендом директолога/маркетолога за 15–25 тыс. ₽ — всю разработку берём на себя!
                </div>
            </div>
        </div>
        """
    else:
        # Day 30: Итоги и FAQ старт
        center_content = """
        <div class="bento-card" style="padding: 30px; margin-top: 22px; text-align: center; border-color: #2563EB; background: #F8FAFF;">
            <div class="pill-green" style="margin-bottom: 14px;">✓ 0 ₽ ПРЕДОПЛАТА • 7 500 ₽ ПОД КЛЮЧ • ХОСТИНГ 0 ₽</div>
            <div style="font-size: 32px; font-weight: 900; color: #0F172A; margin-bottom: 12px;">
                Проверьте рабочий макет уже завтра
            </div>
            <div style="font-size: 17px; color: #475569; max-width: 720px; margin: 0 auto 22px auto; line-height: 1.5;">
                Напишите о вашей нише за 10 минут. Получите готовую ссылку на смартфон через 24 часа, официальный чек ФНС и 30 дней гарантии.
            </div>
            <div style="display: flex; justify-content: center; gap: 16px;">
                <div style="background: #2563EB; color: white; padding: 14px 28px; border-radius: 14px; font-size: 18px; font-weight: 800;">
                    Telegram: @LocalWebRu
                </div>
                <div style="background: #0F172A; color: white; padding: 14px 28px; border-radius: 14px; font-size: 18px; font-weight: 800;">
                    Сайт: local-web.ru
                </div>
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
            font-size: 36px; font-weight: 900; letter-spacing: -1.1px;
            color: #0F172A; line-height: 1.22; margin-top: 22px;
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
            <div class="pill-green"><span class="pill-dot"></span> ДЕНЬ {day:02d} / {total_days}</div>
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

def generate_all_assets(from_day: int = 1, to_day: int = 999, force: bool = False) -> dict:
    """Генерирует графические материалы: при необходимости аватар, обложку и карточки постов."""
    print(f"[ASSETS] Генерация графических материалов LocalWeb (дни {from_day}–{to_day})...")
    from .content_plan import POSTS

    os.makedirs(ASSETS_DIR, exist_ok=True)
    generated = {
        "avatar": os.path.join(ASSETS_DIR, "avatar.png"),
        "cover": os.path.join(ASSETS_DIR, "public_cover.png"),
        "posts": []
    }
    if force or not os.path.exists(generated["avatar"]):
        generate_avatar(generated["avatar"])
        print("[OK] Аватар сообщества сгенерирован (800x800).")
    if force or not os.path.exists(generated["cover"]):
        generate_public_cover(generated["cover"])
        print("[OK] Обложка сообщества сгенерирована (1920x768).")

    total_days = len(POSTS)
    for p in POSTS:
        if not (from_day <= p["day"] <= to_day):
            continue
        filename = p.get("image_file", f"post_{p['day']:02d}.png")
        card_path = os.path.join(ASSETS_DIR, filename)
        if force or not os.path.exists(card_path):
            generate_post_card(p, card_path, total_days=total_days)
            print(f"[OK] Карточка поста День {p['day']:02d} сгенерирована (1080x1080).")
        generated["posts"].append(card_path)

    print(f"[SUCCESS] Подготовлено карточек постов: {len(generated['posts'])} в {ASSETS_DIR}!")
    return generated
