import subprocess
import os

html_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            width: 1200px;
            height: 630px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #F8FAFC;
            background-image: radial-gradient(rgba(148, 163, 184, 0.22) 1.2px, transparent 1.2px);
            background-size: 24px 24px;
            color: #0F172A;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 34px 50px 24px 50px;
            -webkit-font-smoothing: antialiased;
        }

        /* Top Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 12px;
            border-bottom: 1.5px solid #E2E8F0;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .brand-icon {
            width: 38px;
            height: 38px;
            border-radius: 12px;
            background: #2563EB;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }
        .brand-icon svg {
            width: 22px;
            height: 22px;
        }
        .brand-name {
            font-size: 24px;
            font-weight: 900;
            letter-spacing: -0.5px;
            color: #0F172A;
        }
        .brand-name span { color: #2563EB; }

        .header-meta {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .slot-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #ECFDF5;
            color: #059669;
            border: 1.5px solid #A7F3D0;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 800;
        }
        .slot-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 8px #10B981;
        }
        .slide-tag {
            background: #EFF6FF;
            color: #2563EB;
            border: 1.5px solid #BFDBFE;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* Center Bento */
        .content {
            display: grid;
            grid-template-columns: 1.35fr 1fr;
            gap: 28px;
            align-items: center;
            margin: 10px 0;
        }

        .pill-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 5px 14px;
            border-radius: 20px;
            background: #EFF6FF;
            border: 1.5px solid #BFDBFE;
            font-size: 12.5px;
            font-weight: 800;
            color: #2563EB;
            margin-bottom: 12px;
        }
        .headline {
            font-size: 38px;
            font-weight: 900;
            line-height: 1.15;
            letter-spacing: -1.2px;
            color: #0F172A;
            margin-bottom: 10px;
        }
        .headline span { color: #10B981; }

        .subtext {
            font-size: 15px;
            color: #64748B;
            line-height: 1.45;
            margin-bottom: 20px;
            max-width: 620px;
        }

        /* 3 Bento Cards */
        .cards-row {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
        }
        .bento-card {
            background: #FFFFFF;
            border: 1.5px solid #E2E8F0;
            border-radius: 14px;
            padding: 14px 10px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        }
        .card-emerald {
            border: 1.5px solid #10B981;
            background: linear-gradient(135deg, rgba(240, 253, 244, 0.7) 0%, #FFFFFF 100%);
        }
        .card-blue {
            border: 2px solid #2563EB;
            background: linear-gradient(135deg, rgba(239, 246, 255, 0.7) 0%, #FFFFFF 100%);
        }
        .card-num {
            font-size: 26px;
            font-weight: 900;
            line-height: 1;
            margin-bottom: 4px;
        }
        .card-sub {
            font-size: 11px;
            font-weight: 700;
            color: #64748B;
        }

        /* Smartphone Mockup */
        .phone-wrapper {
            display: flex;
            justify-content: center;
            position: relative;
        }
        .phone-frame {
            width: 215px;
            height: 385px;
            background: #0F172A;
            border-radius: 34px;
            padding: 9px;
            box-shadow: 0 20px 45px -10px rgba(15, 23, 42, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.2) inset;
            position: relative;
        }
        .phone-screen {
            width: 100%;
            height: 100%;
            background: #F8FAFC;
            border-radius: 26px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid #CBD5E1;
        }
        .phone-notch {
            width: 75px;
            height: 14px;
            background: #0F172A;
            border-radius: 0 0 12px 12px;
            margin: 0 auto;
        }
        .phone-inner {
            padding: 12px 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            text-align: center;
        }
        .phone-badge {
            position: absolute;
            bottom: 20px;
            right: 40px;
            background: white;
            border: 1.5px solid #CBD5E1;
            border-radius: 12px;
            padding: 10px 16px;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.12);
            font-size: 13px;
            font-weight: 800;
            color: #0F172A;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Footer */
        .footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 12px;
            border-top: 1.5px solid #E2E8F0;
            font-size: 13px;
            color: #64748B;
        }
        .footer strong {
            color: #2563EB;
        }
    </style>
</head>
<body>

    <div class="header">
        <div class="brand">
            <div class="brand-icon">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
            </div>
            <div class="brand-name">Local<span>Web</span></div>
        </div>
        <div class="header-meta">
            <div class="slot-pill"><span class="slot-dot"></span> Осталось 2 слота на этой неделе</div>
            <div class="slide-tag">Сайты под ключ</div>
        </div>
    </div>

    <div class="content">
        <div>
            <div class="pill-badge">
                <span>⚡</span> Без предоплаты и затягивания сроков
            </div>
            <h1 class="headline">
                Сайт для вашего дела за 24 часа.<br>
                Сначала рабочий черновик,<br>
                оплата — <span>потом</span>.
            </h1>
            <p class="subtext">
                Разрабатываем понятные, быстрые сайты для локального бизнеса по всей России. С лидогенерацией в Telegram и 100% соблюдением законов РФ. Без абонентских плат за конструкторы.
            </p>

            <div class="cards-row">
                <div class="bento-card">
                    <div class="card-num" style="color: #2563EB;">24 часа</div>
                    <div class="card-sub">Готовый сайт до оплаты</div>
                </div>
                <div class="bento-card card-emerald">
                    <div class="card-num" style="color: #059669;">0 ₽</div>
                    <div class="card-sub" style="color: #059669;">Предоплата на старте</div>
                </div>
                <div class="bento-card card-blue">
                    <div class="card-num" style="color: #0F172A;">7 500 ₽</div>
                    <div class="card-sub" style="color: #2563EB;">Финал под ключ</div>
                </div>
            </div>
        </div>

        <div class="phone-wrapper">
            <div class="phone-frame">
                <div class="phone-screen">
                    <div class="phone-notch"></div>
                    <div class="phone-inner">
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 10px; font-weight: 800; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;">
                            <span>Local<span style="color: #2563EB;">Web</span></span>
                            <span style="background: #ECFDF5; color: #059669; padding: 2px 6px; border-radius: 4px;">🟢 24ч MVP</span>
                        </div>
                        <div style="font-size: 13px; font-weight: 900; line-height: 1.25; color: #0F172A; margin-top: 6px;">
                            Автосервис "Драйв"<br><span style="font-size: 10px; color: #64748B; font-weight: 500;">Кузовной ремонт и ТО</span>
                        </div>
                        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 6px; font-size: 10px; text-align: left;">
                            <div style="font-weight: 800; color: #2563EB;">✓ Диагностика 0 ₽</div>
                            <div style="color: #64748B;">Гарантия на работы 1 год</div>
                        </div>
                        <div style="background: #2563EB; color: white; border-radius: 8px; padding: 7px; font-size: 11px; font-weight: 800;">
                            Записаться в WhatsApp
                        </div>
                        <div style="background: #F1F5F9; border-radius: 6px; padding: 5px; font-size: 10px; color: #475569;">
                            ⚡ Загрузка: 0.8с (98/100)
                        </div>
                    </div>
                </div>
            </div>

            <div class="phone-badge">
                <span>📱</span> Тест на вашем смартфоне
            </div>
        </div>
    </div>

    <div class="footer">
        <div>Официальный сайт: <strong>local-web.ru</strong> • Студия разработки сайтов LocalWeb</div>
        <div>Связаться с разработчиком: <strong>@LocalWebRu</strong></div>
    </div>

</body>
</html>'''

with open('og-image-template.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
html_path = os.path.abspath('og-image-template.html')
png_path = os.path.abspath('og-image.png')

cmd = [
    chrome,
    '--headless=new',
    '--disable-gpu',
    '--window-size=1200,630',
    f'--screenshot={png_path}',
    html_path
]

subprocess.run(cmd, check=True)
print("Updated og-image.png generated successfully! Size:", os.path.getsize(png_path))
os.remove('og-image-template.html')
