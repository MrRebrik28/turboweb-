import subprocess
import os

html_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            width: 1200px;
            height: 630px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0F172A;
            color: #FFFFFF;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 55px 70px;
            position: relative;
        }

        /* Glowing background accents */
        .glow-blue {
            position: absolute;
            top: -100px;
            right: -80px;
            width: 500px;
            height: 500px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(37, 99, 235, 0.35) 0%, transparent 70%);
            pointer-events: none;
        }
        .glow-emerald {
            position: absolute;
            bottom: -120px;
            left: 200px;
            width: 450px;
            height: 450px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, transparent 70%);
            pointer-events: none;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            z-index: 2;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .brand-icon {
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: #2563EB;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4);
        }
        .brand-icon svg {
            width: 26px;
            height: 26px;
        }
        .brand-title {
            font-size: 28px;
            font-weight: 900;
            letter-spacing: -0.5px;
        }
        .brand-title span { color: #38BDF8; }

        .tag-pill {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 8px 18px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 700;
            color: #94A3B8;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .hero {
            position: relative;
            z-index: 2;
            margin: 20px 0;
        }
        .hero-tag {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(37, 99, 235, 0.2);
            color: #60A5FA;
            border: 1px solid rgba(96, 165, 250, 0.3);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 800;
            margin-bottom: 14px;
        }
        .hero-title {
            font-size: 46px;
            font-weight: 900;
            line-height: 1.15;
            letter-spacing: -1.5px;
            margin-bottom: 12px;
        }
        .hero-title span {
            color: #10B981;
        }
        .hero-sub {
            font-size: 20px;
            color: #94A3B8;
            line-height: 1.4;
            max-width: 900px;
        }

        .footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 22px;
            position: relative;
            z-index: 2;
        }
        .stats-row {
            display: flex;
            gap: 14px;
        }
        .stat-badge {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 8px 16px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            font-weight: 700;
        }
        .stat-badge strong {
            color: #38BDF8;
            font-weight: 900;
        }
        .price-box {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .domain-text {
            font-size: 16px;
            font-weight: 700;
            color: #94A3B8;
        }
        .price-tag {
            background: #2563EB;
            color: white;
            padding: 8px 20px;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 900;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        }
    </style>
</head>
<body>
    <div class="glow-blue"></div>
    <div class="glow-emerald"></div>

    <div class="header">
        <div class="brand">
            <div class="brand-icon">
                <svg fill="none" stroke="#FFFFFF" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
            </div>
            <div class="brand-title">Local<span>Web</span></div>
        </div>
        <div class="tag-pill">Разработка под ключ • Без абонентской платы</div>
    </div>

    <div class="hero">
        <div class="hero-tag">⚡ Готовый черновик за 24 часа</div>
        <h1 class="hero-title">Сайты для малого бизнеса.<br>Сначала результат, оплата — <span>потом</span>.</h1>
        <p class="hero-sub">
            Современные, быстрые сайты с заявками в Telegram, пожизненным бесплатным хостингом и 100% защитой по законам РФ.
        </p>
    </div>

    <div class="footer">
        <div class="stats-row">
            <div class="stat-badge">⏱️ <strong>24 часа</strong> на прототип</div>
            <div class="stat-badge">🛡️ <strong>0 ₽</strong> предоплаты</div>
            <div class="stat-badge">🌐 <strong>0 ₽ / мес</strong> за хостинг</div>
        </div>
        <div class="price-box">
            <div class="domain-text">local-web.ru</div>
            <div class="price-tag">7 500 ₽</div>
        </div>
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
print("og-image.png successfully created! Size:", os.path.getsize(png_path))
os.remove('og-image-template.html')
