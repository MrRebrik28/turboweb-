import subprocess
import os

# 1. Primary Avatar (Vibrant Royal Blue Icon - Perfect for Telegram / WhatsApp circles)
html_v1 = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    width: 1024px;
    height: 1024px;
    background: #0B1120;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}
.glow {
    position: absolute;
    width: 700px;
    height: 700px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(37, 99, 235, 0.45) 0%, transparent 65%);
}
.squircle {
    width: 640px;
    height: 640px;
    border-radius: 170px;
    background: linear-gradient(145deg, #3B82F6 0%, #2563EB 40%, #1D4ED8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 35px 80px -15px rgba(37, 99, 235, 0.6), 0 0 0 2px rgba(255, 255, 255, 0.2) inset;
    position: relative;
    z-index: 2;
}
.icon {
    width: 360px;
    height: 360px;
}
</style>
</head>
<body>
<div class="glow"></div>
<div class="squircle">
    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>
</div>
</body>
</html>'''

# 2. Dark Premium Glass Avatar with Monogram & Code Bracket
html_v2 = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@900&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    width: 1024px;
    height: 1024px;
    background: radial-gradient(circle at 50% 30%, #1E293B 0%, #0F172A 70%, #020617 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
    font-family: 'Inter', sans-serif;
}
.circle-glow {
    position: absolute;
    width: 800px;
    height: 800px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(37, 99, 235, 0.3) 0%, transparent 60%);
}
.card {
    width: 660px;
    height: 660px;
    border-radius: 180px;
    background: rgba(30, 41, 59, 0.7);
    border: 3px solid rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(40px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 40px 90px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(37, 99, 235, 0.3);
    position: relative;
    z-index: 2;
}
.brand-title {
    font-size: 155px;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -6px;
    display: flex;
    align-items: center;
    line-height: 1;
}
.brand-title span {
    color: #38BDF8;
}
.status-pill {
    margin-top: 24px;
    background: rgba(16, 185, 129, 0.15);
    border: 1.5px solid rgba(16, 185, 129, 0.4);
    padding: 10px 28px;
    border-radius: 30px;
    font-size: 24px;
    font-weight: 800;
    color: #10B981;
    display: flex;
    align-items: center;
    gap: 12px;
}
.status-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 12px #10B981;
}
</style>
</head>
<body>
<div class="circle-glow"></div>
<div class="card">
    <div class="brand-title">Local<span>Web</span></div>
    <div class="status-pill">
        <span class="status-dot"></span> DEV STUDIO
    </div>
</div>
</body>
</html>'''

# 3. Clean Full-Circle Electric Avatar (Ideal for mobile messengers)
html_v3 = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@900&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    width: 1024px;
    height: 1024px;
    background: linear-gradient(135deg, #1E40AF 0%, #2563EB 50%, #0284C7 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
    font-family: 'Inter', sans-serif;
}
.decor-circle {
    position: absolute;
    width: 900px;
    height: 900px;
    border-radius: 50%;
    border: 2px dashed rgba(255, 255, 255, 0.2);
}
.monogram {
    font-size: 320px;
    font-weight: 900;
    color: #FFFFFF;
    letter-spacing: -14px;
    line-height: 0.9;
    text-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}
.monogram span {
    color: #67E8F9;
}
.tagline {
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 12px;
    color: rgba(255, 255, 255, 0.9);
    margin-top: 15px;
    text-transform: uppercase;
}
</style>
</head>
<body>
<div class="decor-circle"></div>
<div class="monogram">L<span>W</span></div>
<div class="tagline">LOCALWEB</div>
</body>
</html>'''

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

for idx, (name, content) in enumerate([
    ('avatar_primary.png', html_v1),
    ('avatar_dark.png', html_v2),
    ('avatar_circle.png', html_v3)
], 1):
    temp_html = f'temp_avatar_{idx}.html'
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(content)
    
    abs_html = os.path.abspath(temp_html)
    png_path = os.path.abspath(name)
    cmd = [
        chrome,
        '--headless=new',
        '--disable-gpu',
        '--window-size=1024,1024',
        f'--screenshot={png_path}',
        abs_html
    ]
    subprocess.run(cmd, check=True)
    os.remove(temp_html)
    print(f"{name} generated! Size: {os.path.getsize(png_path)}")
