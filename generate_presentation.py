import os
import subprocess

html_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>LocalWeb — Презентация и коммерческое предложение</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        @page {
            size: 297mm 210mm;
            margin: 0;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #F8FAFC;
            color: #0F172A;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            -webkit-font-smoothing: antialiased;
        }

        .slide {
            width: 297mm;
            height: 210mm;
            page-break-after: always;
            break-after: page;
            position: relative;
            overflow: hidden;
            padding: 12mm 16mm 10mm 16mm;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: #F8FAFC;
        }

        /* Subtle grid background like website */
        .slide-grid-bg {
            background-image: radial-gradient(rgba(148, 163, 184, 0.15) 1px, transparent 1px);
            background-size: 24px 24px;
        }

        /* Top Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 8px;
            border-bottom: 1px solid #E2E8F0;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .brand-icon {
            width: 32px;
            height: 32px;
            border-radius: 10px;
            background: #2563EB;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
        }
        .brand-icon svg {
            width: 18px;
            height: 18px;
        }
        .brand-name {
            font-size: 19px;
            font-weight: 900;
            letter-spacing: -0.5px;
            color: #0F172A;
        }
        .brand-name span {
            color: #2563EB;
        }
        .header-meta {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .slot-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #ECFDF5;
            color: #059669;
            border: 1px solid #A7F3D0;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }
        .slot-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 6px #10B981;
        }
        .slide-tag {
            background: #EFF6FF;
            color: #2563EB;
            border: 1px solid #BFDBFE;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }
        .slide-num {
            font-size: 12px;
            font-weight: 800;
            color: #94A3B8;
        }

        /* Slide Body */
        .content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 8px 0;
        }
        .slide-headline {
            font-size: 26px;
            font-weight: 900;
            letter-spacing: -0.8px;
            color: #0F172A;
            line-height: 1.2;
            margin-bottom: 4px;
        }
        .slide-sub {
            font-size: 13px;
            color: #64748B;
            font-weight: 500;
            margin-bottom: 14px;
        }

        /* Footer */
        .footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 8px;
            border-top: 1px solid #E2E8F0;
            font-size: 11px;
            color: #64748B;
        }
        .footer a {
            color: #2563EB;
            font-weight: 700;
            text-decoration: none;
        }

        /* Card Glass (LocalWeb Signature Style) */
        .card-glass {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 2px 6px -1px rgba(15, 23, 42, 0.04);
            position: relative;
        }
        .card-glass-blue {
            border: 2px solid #2563EB;
            background: linear-gradient(135deg, rgba(239, 246, 255, 0.6) 0%, #FFFFFF 100%);
        }
        .card-glass-emerald {
            border: 1.5px solid #10B981;
            background: linear-gradient(135deg, rgba(240, 253, 244, 0.6) 0%, #FFFFFF 100%);
        }

        /* Badges */
        .badge-blue {
            display: inline-block;
            background: #EFF6FF;
            color: #2563EB;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-emerald {
            display: inline-block;
            background: #ECFDF5;
            color: #059669;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-rose {
            display: inline-block;
            background: #FFF1F2;
            color: #E11D48;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Grids */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
        .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; }
        .grid-bento-hero { display: grid; grid-template-columns: 1.3fr 1fr; gap: 16px; align-items: center; }

        /* Smartphone Mockup */
        .phone-frame {
            width: 175px;
            height: 310px;
            background: #0F172A;
            border-radius: 28px;
            padding: 7px;
            box-shadow: 0 16px 36px -8px rgba(15, 23, 42, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.2) inset;
            position: relative;
            margin: 0 auto;
        }
        .phone-screen {
            width: 100%;
            height: 100%;
            background: #F8FAFC;
            border-radius: 22px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid #CBD5E1;
        }
        .phone-notch {
            width: 60px;
            height: 12px;
            background: #0F172A;
            border-radius: 0 0 10px 10px;
            margin: 0 auto;
        }
        .phone-content {
            padding: 10px 8px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            text-align: center;
        }

        /* Telegram Bubble Mockup */
        .tg-bubble {
            background: #FFFFFF;
            border-radius: 14px;
            border: 1px solid #E2E8F0;
            box-shadow: 0 6px 18px -4px rgba(15, 23, 42, 0.08);
            padding: 14px;
            font-size: 11px;
            line-height: 1.45;
        }
        .tg-header {
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid #F1F5F9;
            padding-bottom: 8px;
            margin-bottom: 8px;
        }
        .tg-avatar {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #2563EB;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 11px;
        }

        /* Comparison Table */
        .comp-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }
        .comp-table th {
            padding: 8px 10px;
            text-align: left;
            font-weight: 800;
            border-bottom: 1.5px solid #E2E8F0;
            background: #F8FAFC;
        }
        .comp-table td {
            padding: 8px 10px;
            border-bottom: 1px solid #F1F5F9;
            vertical-align: middle;
        }
        .comp-table .lw-col {
            background: rgba(239, 246, 255, 0.6);
            font-weight: 700;
            color: #1E3A8A;
            border-left: 2px solid #2563EB;
            border-right: 2px solid #2563EB;
        }
        .comp-table tr:first-child .lw-col {
            border-top: 2px solid #2563EB;
        }
        .comp-table tr:last-child .lw-col {
            border-bottom: 2px solid #2563EB;
        }

        /* Icon Pill Card */
        .feature-item {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 10px 12px;
        }
        .feature-icon-box {
            width: 26px;
            height: 26px;
            border-radius: 6px;
            background: #EFF6FF;
            color: #2563EB;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 11px;
            flex-shrink: 0;
        }
    </style>
</head>
<body>

    <!-- ==================== СЛАЙД 1: ОБЛОЖКА В СТИЛЕ САЙТА ==================== -->
    <div class="slide slide-grid-bg">
        <div class="header">
            <div class="brand">
                <div class="brand-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>
                </div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slot-pill"><span class="slot-dot"></span> Осталось 2 слота на этой неделе</div>
                <div class="slide-tag">Презентация 2026</div>
            </div>
        </div>

        <div class="content">
            <div class="grid-bento-hero">
                <div>
                    <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; background: #EFF6FF; border: 1px solid #BFDBFE; font-size: 11px; font-weight: 800; color: #2563EB; margin-bottom: 12px;">
                        <span>⚡</span> Без предоплаты и затягивания сроков
                    </div>
                    
                    <h1 style="font-size: 34px; font-weight: 900; line-height: 1.15; letter-spacing: -1px; color: #0F172A; margin-bottom: 10px;">
                        Сайт для вашего дела за 24 часа.<br>
                        Сначала рабочий черновик, оплата — <span style="color: #10B981; font-weight: 900;">потом</span>.
                    </h1>
                    
                    <p style="font-size: 14px; color: #64748B; line-height: 1.45; margin-bottom: 18px;">
                        Разрабатываем понятные, быстрые сайты для локального бизнеса с лидогенерацией в Telegram и 100% соблюдением законов РФ. Без абонентских плат за конструкторы.
                    </p>

                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                        <div class="card-glass" style="text-align: center; padding: 12px 10px;">
                            <div style="font-size: 22px; font-weight: 900; color: #2563EB; line-height: 1;">24 часа</div>
                            <div style="font-size: 10px; color: #64748B; font-weight: 700; margin-top: 4px;">Готовый сайт до оплаты</div>
                        </div>
                        <div class="card-glass card-glass-emerald" style="text-align: center; padding: 12px 10px;">
                            <div style="font-size: 22px; font-weight: 900; color: #059669; line-height: 1;">0 ₽</div>
                            <div style="font-size: 10px; color: #059669; font-weight: 700; margin-top: 4px;">Предоплата на старте</div>
                        </div>
                        <div class="card-glass card-glass-blue" style="text-align: center; padding: 12px 10px;">
                            <div style="font-size: 22px; font-weight: 900; color: #0F172A; line-height: 1;">7 500 ₽</div>
                            <div style="font-size: 10px; color: #2563EB; font-weight: 800; margin-top: 4px;">Финал под ключ</div>
                        </div>
                    </div>
                </div>

                <!-- Мокап смартфона с реальным сайтом -->
                <div style="display: flex; justify-content: center; position: relative;">
                    <div class="phone-frame">
                        <div class="phone-screen">
                            <div class="phone-notch"></div>
                            <div class="phone-content">
                                <div style="display: flex; align-items: center; justify-content: space-between; font-size: 9px; font-weight: 800; border-bottom: 1px solid #E2E8F0; padding-bottom: 4px;">
                                    <span>Local<span style="color: #2563EB;">Web</span></span>
                                    <span style="background: #ECFDF5; color: #059669; padding: 1px 4px; border-radius: 4px;">🟢 24ч MVP</span>
                                </div>
                                <div style="font-size: 11px; font-weight: 900; line-height: 1.2; color: #0F172A; margin-top: 4px;">
                                    Автосервис "Драйв"<br><span style="font-size: 9px; color: #64748B; font-weight: 500;">Кузовной ремонт и ТО</span>
                                </div>
                                <div style="background: white; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 4px; font-size: 8px; text-align: left;">
                                    <div style="font-weight: 700; color: #2563EB;">✓ Диагностика 0 ₽</div>
                                    <div style="color: #64748B;">Гарантия на работы 1 год</div>
                                </div>
                                <div style="background: #2563EB; color: white; border-radius: 6px; padding: 5px; font-size: 9px; font-weight: 800;">
                                    Записаться в WhatsApp
                                </div>
                                <div style="background: #F1F5F9; border-radius: 6px; padding: 4px; font-size: 8px; color: #475569;">
                                    ⚡ Загрузка: 0.8с (98/100)
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Плашка "Проверено на мобильных" -->
                    <div style="position: absolute; bottom: 10px; right: 0; background: white; border: 1px solid #CBD5E1; border-radius: 10px; padding: 8px 12px; box-shadow: 0 8px 20px rgba(15,23,42,0.1); font-size: 11px; font-weight: 700;">
                        📱 Тест на вашем смартфоне
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <div>Официальный сайт: <a href="https://local-web.ru">local-web.ru</a> • Студия разработки сайтов LocalWeb</div>
            <div>Связаться с разработчиком: <a href="https://t.me/LocalWebRu">@LocalWebRu</a></div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 2: ЧЕСТНОЕ СРАВНЕНИЕ (ТАБЛИЦА С САЙТА) ==================== -->
    <div class="slide">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slide-tag">Честное сравнение</div>
                <div class="slide-num">02 / 10</div>
            </div>
        </div>

        <div class="content">
            <h2 class="slide-headline">Сравнение: мы, конструкторы или обычные веб-студии</h2>
            <p class="slide-sub">Почему предприниматели переплачивают в 5–10 раз за то, что должно стоить разумно и работать быстро.</p>

            <div class="card-glass" style="padding: 0; overflow: hidden;">
                <table class="comp-table">
                    <thead>
                        <tr>
                            <th style="width: 25%;">Критерий</th>
                            <th class="lw-col" style="width: 28%;">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <span>LocalWeb</span>
                                    <span class="badge-emerald" style="font-size: 9px;">Оптимально</span>
                                </div>
                            </th>
                            <th style="width: 23%;">Конструкторы (Tilda и др.)</th>
                            <th style="width: 24%;">Обычные веб-студии</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Предоплата на старте</strong></td>
                            <td class="lw-col"><strong>0 ₽</strong> (оплата после показа черновика)</td>
                            <td>100% своими руками или от 25 000 ₽</td>
                            <td>От 50% до 100% вперед (от 40 000 ₽)</td>
                        </tr>
                        <tr>
                            <td><strong>Срок первого результата</strong></td>
                            <td class="lw-col"><strong>24 часа</strong> (рабочая страница на телефоне)</td>
                            <td>Недели мучений по вечерам</td>
                            <td>От 3 до 8 недель согласований</td>
                        </tr>
                        <tr>
                            <td><strong>Плата за хостинг и движок</strong></td>
                            <td class="lw-col"><strong>0 ₽ НАВСЕГДА</strong> (чистый быстрый код)</td>
                            <td>От 9 000 ₽/год (абонентская плата)</td>
                            <td>От 6 000 ₽/год за хостинг и плагины</td>
                        </tr>
                        <tr>
                            <td><strong>Скорость на смартфонах</strong></td>
                            <td class="lw-col"><strong>0.8 сек</strong> (98/100 в Google PageSpeed)</td>
                            <td>3–5 сек (тяжелый конструктор)</td>
                            <td>Как повезет (часто тормозит)</td>
                        </tr>
                        <tr>
                            <td><strong>Юридическая чистота 152-ФЗ</strong></td>
                            <td class="lw-col"><strong>100% в коробке</strong> (сервер в РФ, чекбокс, чек)</td>
                            <td>Настраивать и писать самому</td>
                            <td>Отдельная платная услуга</td>
                        </tr>
                        <tr>
                            <td><strong>Правки после запуска</strong></td>
                            <td class="lw-col"><strong>30 дней бесплатно</strong> по сообщению в TG</td>
                            <td>Разбираться в интерфейсе самому</td>
                            <td>Почасовая оплата (от 2 500 ₽/час)</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Никаких скрытых условий и мелких шрифтов</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 3: ПРИНЦИП "БЕЗ КОТА В МЕШКЕ" ==================== -->
    <div class="slide">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slide-tag">Условия работы</div>
                <div class="slide-num">03 / 10</div>
            </div>
        </div>

        <div class="content">
            <h2 class="slide-headline">Понятный процесс без «кота в мешке»</h2>
            <p class="slide-sub">Сначала вы своими глазами видите сайт на смартфоне, и только потом принимаете решение.</p>

            <div class="grid-3" style="gap: 14px;">
                <div class="card-glass" style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span class="badge-emerald">Без риска</span>
                            <span style="font-size: 11px; font-weight: 800; color: #94A3B8;">Шаг 1</span>
                        </div>
                        <h3 style="font-size: 16px; font-weight: 900; line-height: 1.25; margin-bottom: 8px;">
                            Экспресс-бриф за 10 минут
                        </h3>
                        <p style="font-size: 12px; color: #64748B; line-height: 1.45;">
                            Вам не нужно заполнять анкеты на 20 страниц. Достаточно рассказать о бизнесе голосом или текстом в Telegram: чем занимаетесь, цены, фото и куда отправлять заявки.
                        </p>
                    </div>
                    <div style="margin-top: 12px; padding: 6px 10px; background: #F1F5F9; border-radius: 8px; font-size: 11px; font-weight: 700; color: #334155;">
                        💰 Предоплата: 0 ₽
                    </div>
                </div>

                <div class="card-glass card-glass-blue" style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span class="badge-blue">Тест-драйв</span>
                            <span style="font-size: 11px; font-weight: 800; color: #2563EB;">Шаг 2</span>
                        </div>
                        <h3 style="font-size: 16px; font-weight: 900; line-height: 1.25; margin-bottom: 8px;">
                            Черновик на телефоне через 24 часа
                        </h3>
                        <p style="font-size: 12px; color: #475569; line-height: 1.45;">
                            На следующий день мы присылаем персональную ссылку. Вы открываете настоящий интерактивный сайт на своем смартфоне: листаете блоки, кликаете кнопки и оцениваете тексты.
                        </p>
                    </div>
                    <div style="margin-top: 12px; padding: 6px 10px; background: #EFF6FF; border-radius: 8px; font-size: 11px; font-weight: 800; color: #2563EB;">
                        ⏱ Срок сборки: ровно 24 часа
                    </div>
                </div>

                <div class="card-glass card-glass-emerald" style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span class="badge-emerald">Решение</span>
                            <span style="font-size: 11px; font-weight: 800; color: #059669;">Шаг 3</span>
                        </div>
                        <h3 style="font-size: 16px; font-weight: 900; line-height: 1.25; margin-bottom: 8px;">
                            Понравилось — запускаем, нет — расходимся
                        </h3>
                        <p style="font-size: 12px; color: #065F46; line-height: 1.45;">
                            Если прототип вам понравился — вы оплачиваете 7 500 ₽, мы подключаем ваш домен и ботов. Если нет — вы не платите ни копейки, без обид и навязчивых звонков.
                        </p>
                    </div>
                    <div style="margin-top: 12px; padding: 6px 10px; background: #ECFDF5; border-radius: 8px; font-size: 11px; font-weight: 800; color: #059669;">
                        🤝 100% гарантия честной сделки
                    </div>
                </div>
            </div>

            <!-- Плашка под шагами -->
            <div style="margin-top: 12px; background: #FFFFFF; border: 1.5px dashed #2563EB; border-radius: 10px; padding: 10px 16px; display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 12px; font-weight: 700; color: #1E3A8A;">
                    💡 <strong>Почему мы так делаем?</strong> Потому что мы уверены в скорости и качестве своего кода и не хотим, чтобы клиенты боялись заказывать сайт.
                </div>
                <div style="font-size: 11px; font-weight: 800; color: #2563EB; white-space: nowrap;">Риск: 0%</div>
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Бизнес-модель, построенная на доверии</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 4: ЗАЧЕМ БИЗНЕСУ САЙТ (4 КАРТОЧКИ С САЙТА) ==================== -->
    <div class="slide">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slide-tag">Зачем это нужно</div>
                <div class="slide-num">04 / 10</div>
            </div>
        </div>

        <div class="content">
            <h2 class="slide-headline">Почему одной группы в соцсетях сегодня уже мало</h2>
            <p class="slide-sub">Сайт — это не дань моде, а независимый инструмент, который окупает себя с первых клиентов.</p>

            <div class="grid-2" style="gap: 12px;">
                <!-- 1. Соцсети -->
                <div class="card-glass" style="border-left: 4px solid #F43F5E;">
                    <div style="font-size: 10px; font-weight: 800; color: #E11D48; text-transform: uppercase; margin-bottom: 2px;">Риски чужих платформ</div>
                    <h3 style="font-size: 15px; font-weight: 900; color: #0F172A; margin-bottom: 6px;">
                        Внезапные блокировки и падение охватов
                    </h3>
                    <p style="font-size: 11.5px; color: #475569; line-height: 1.45;">
                        Сообщества в соцсетях могут заблокировать или урезать показы из-за смены алгоритмов. Собственный сайт на личном домене принадлежит только вам и работает 24/7 без оглядки на чужие правила.
                    </p>
                </div>

                <!-- 2. Поиск -->
                <div class="card-glass" style="border-left: 4px solid #F59E0B;">
                    <div style="font-size: 10px; font-weight: 800; color: #D97706; text-transform: uppercase; margin-bottom: 2px;">Горячий спрос</div>
                    <h3 style="font-size: 15px; font-weight: 900; color: #0F172A; margin-bottom: 6px;">
                        Поиск в Яндексе и на картах прямо сейчас
                    </h3>
                    <p style="font-size: 11.5px; color: #475569; line-height: 1.45;">
                        Когда человеку срочно нужен автосервис, ремонт, клиника или доставка — он открывает поиск. Если у вас нет простого и понятного сайта, клиент за 3 секунды уходит к конкуренту из соседней вкладки.
                    </p>
                </div>

                <!-- 3. Рутина -->
                <div class="card-glass" style="border-left: 4px solid #3B82F6;">
                    <div style="font-size: 10px; font-weight: 800; color: #2563EB; text-transform: uppercase; margin-bottom: 2px;">Экономия времени</div>
                    <h3 style="font-size: 15px; font-weight: 900; color: #0F172A; margin-bottom: 6px;">
                        Минус 90% однотипных вопросов в переписке
                    </h3>
                    <p style="font-size: 11.5px; color: #475569; line-height: 1.45;">
                        «А где вы находитесь?», «Сколько стоит?», «Есть примеры работ?». Сайт снимает эти вопросы за 30 секунд: показывает прайс, фото и сразу собирает заявку с номером телефона клиента.
                    </p>
                </div>

                <!-- 4. Доверие -->
                <div class="card-glass" style="border-left: 4px solid #6366F1;">
                    <div style="font-size: 10px; font-weight: 800; color: #4F46E5; text-transform: uppercase; margin-bottom: 2px;">Статус и чек</div>
                    <h3 style="font-size: 15px; font-weight: 900; color: #0F172A; margin-bottom: 6px;">
                        Доверие и готовность платить больше
                    </h3>
                    <p style="font-size: 11.5px; color: #475569; line-height: 1.45;">
                        Быстрый современный сайт сразу отличает надежный бизнес от временных исполнителей на бесплатных досках объявлений. Клиенты охотнее соглашаются на нормальный чек без торгов.
                    </p>
                </div>
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Инструменты продаж для малого бизнеса</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 5: ТЕХНОЛОГИИ И ХОСТИНГ 0 РУБ ==================== -->
    <div class="slide">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slide-tag">Технологии и экономия</div>
                <div class="slide-num">05 / 10</div>
            </div>
        </div>

        <div class="content">
            <h2 class="slide-headline">Хостинг за 0 ₽: почему сайт работает бесплатно навсегда</h2>
            <p class="slide-sub">Инженерный подход вместо устаревших и прожорливых платформ.</p>

            <div class="grid-bento-hero" style="gap: 16px;">
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div class="card-glass">
                        <div style="font-size: 11px; font-weight: 800; color: #2563EB; text-transform: uppercase; margin-bottom: 4px;">Чистый код без CMS</div>
                        <h3 style="font-size: 15px; font-weight: 900; margin-bottom: 6px;">Почему конструкторы берут плату каждый месяц?</h3>
                        <p style="font-size: 11.5px; color: #475569; line-height: 1.45;">
                            Tilda или WordPress под капотом подгружают тысячи строк тяжелых плагинов и баз данных, требуя дорогих серверов. 
                            <strong>Сайты LocalWeb написаны на чистом HTML5, Tailwind CSS и Vanilla JavaScript:</strong> они весят меньше одной фотографии, открываются за 0.8 сек и не требуют баз данных, которые могут упасть.
                        </p>
                    </div>

                    <div class="card-glass card-glass-emerald">
                        <div style="font-size: 11px; font-weight: 800; color: #059669; text-transform: uppercase; margin-bottom: 4px;">Облачный Edge CDN хостинг</div>
                        <h3 style="font-size: 15px; font-weight: 900; margin-bottom: 6px;">Пожизненный бесплатный сервер</h3>
                        <p style="font-size: 11.5px; color: #065F46; line-height: 1.45;">
                            Сайт размещается в отказоустойчивой инфраструктуре GitHub & Cloudflare Edge CDN с бесплатным SSL-сертификатом безопасности (зеленый замочек). Вы экономите от <strong>9 000 до 36 000 ₽ каждый год</strong> на абонентских платах.
                        </p>
                    </div>
                </div>

                <!-- Спидометр скорости PageSpeed -->
                <div class="card-glass" style="text-align: center; padding: 20px 14px; background: white; border: 2px solid #E2E8F0;">
                    <div style="font-size: 12px; font-weight: 800; color: #64748B; text-transform: uppercase; margin-bottom: 10px;">
                        Google PageSpeed Insights
                    </div>
                    
                    <div style="width: 100px; height: 100px; border-radius: 50%; border: 7px solid #10B981; margin: 0 auto 12px auto; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 16px rgba(16, 185, 129, 0.2);">
                        <div style="font-size: 32px; font-weight: 900; color: #0F172A; line-height: 1;">98</div>
                        <div style="font-size: 9px; font-weight: 800; color: #059669;">ИЗ 100</div>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px; margin-top: 10px; border-top: 1px solid #F1F5F9; padding-top: 10px;">
                        <div style="background: #F8FAFC; padding: 6px; border-radius: 6px;">
                            <div style="font-weight: 900; color: #2563EB;">0.4 сек</div>
                            <div style="color: #64748B; font-size: 9px;">Первый экран</div>
                        </div>
                        <div style="background: #F8FAFC; padding: 6px; border-radius: 6px;">
                            <div style="font-weight: 900; color: #10B981;">0.8 сек</div>
                            <div style="color: #64748B; font-size: 9px;">Полная загрузка</div>
                        </div>
                    </div>
                    <div style="font-size: 10px; color: #64748B; margin-top: 8px;">
                        🚀 Клиенты не уходят, ожидая загрузки страницы
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Скорость и надежность мирового уровня</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 6: ДОМЕН И СОБСТВЕННОСТЬ ==================== -->
    <div class="slide">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slide-tag">Ваша собственность</div>
                <div class="slide-num">06 / 10</div>
            </div>
        </div>

        <div class="content">
            <h2 class="slide-headline">Домен .RU: ваша 100% юридическая собственность</h2>
            <p class="slide-sub">Мы принципиально не привязываем клиентов к себе и не удерживаем доменные имена.</p>

            <div class="grid-2" style="gap: 14px;">
                <div class="card-glass" style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div class="badge-blue" style="margin-bottom: 8px;">Официальный реестр РФ</div>
                        <h3 style="font-size: 16px; font-weight: 900; margin-bottom: 8px;">Оформление строго на ваши реквизиты</h3>
                        <p style="font-size: 12px; color: #475569; line-height: 1.5; margin-bottom: 8px;">
                            Многие недобросовестные вебмастера оформляют домен на себя, требуя выкуп при уходе. 
                            <strong>Мы регистрируем домен строго на ваше имя:</strong>
                        </p>
                        <ul style="font-size: 11.5px; color: #334155; line-height: 1.5; padding-left: 14px;">
                            <li>На реквизиты вашей компании (ИП или ООО);</li>
                            <li>Либо на ваш паспорт (для физических лиц и самозанятых).</li>
                        </ul>
                        <p style="font-size: 11.5px; color: #475569; margin-top: 8px;">
                            Вы — единственный полноправный администратор в государственном реестре Координационного центра Рунета (ТЦИ).
                        </p>
                    </div>

                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 10px; font-size: 11px; color: #0F172A; font-weight: 700;">
                        🏷️ Стоимость продления домена: от ~190 ₽ в год напрямую регистратору без наценок
                    </div>
                </div>

                <div class="card-glass card-glass-blue" style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div class="badge-emerald" style="margin-bottom: 8px;">Технический сервис</div>
                        <h3 style="font-size: 16px; font-weight: 900; margin-bottom: 8px;">Полная настройка DNS под ключ</h3>
                        <p style="font-size: 12px; color: #334155; line-height: 1.5; margin-bottom: 8px;">
                            Вам не нужно разбираться в сложных аббревиатурах серверов. Мы берем на себя всю техническую часть:
                        </p>
                        <div style="display: flex; flex-direction: column; gap: 6px; font-size: 11px; color: #1E3A8A;">
                            <div style="background: white; padding: 6px 8px; border-radius: 6px; border: 1px solid #BFDBFE;">
                                ✓ 4 независимых IP-сервера для непрерывной доступности
                            </div>
                            <div style="background: white; padding: 6px 8px; border-radius: 6px; border: 1px solid #BFDBFE;">
                                ✓ Автоматический редирект с www.site.ru на site.ru
                            </div>
                            <div style="background: white; padding: 6px 8px; border-radius: 6px; border: 1px solid #BFDBFE;">
                                ✓ Выпуск и автообновление SSL-сертификата (HTTPS)
                            </div>
                            <div style="background: white; padding: 6px 8px; border-radius: 6px; border: 1px solid #BFDBFE;">
                                ✓ Если у вас уже есть домен — подключим его бесплатно
                            </div>
                        </div>
                    </div>

                    <div style="font-size: 10.5px; color: #2563EB; font-weight: 700; margin-top: 6px;">
                        💡 Наш собственный сайт <span style="text-decoration: underline;">local-web.ru</span> настроен по этой же схеме
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Домен принадлежит вам с первой секунды</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 7: ЗАКОНОДАТЕЛЬСТВО РФ ==================== -->
    <div class="slide">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slide-tag">Законодательство РФ</div>
                <div class="slide-num">07 / 10</div>
            </div>
        </div>

        <div class="content">
            <h2 class="slide-headline">100% защита от штрафов Роскомнадзора</h2>
            <p class="slide-sub">В 2024–2026 годах штрафы по 152-ФЗ выросли до 6 000 000 ₽. Мы закрываем все юридические риски.</p>

            <div class="grid-3" style="gap: 12px;">
                <div class="card-glass" style="border-top: 4px solid #2563EB;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 800; color: #2563EB;">152-ФЗ РФ</span>
                        <span style="font-size: 16px;">🇷🇺</span>
                    </div>
                    <h3 style="font-size: 14px; font-weight: 900; margin-bottom: 6px;">Локализация в Москве</h3>
                    <p style="font-size: 11px; color: #475569; line-height: 1.45;">
                        Серверная первичная фиксация данных клиентов производится в дата-центрах на территории РФ (Яндекс Облако, Москва).
                    </p>
                    <div style="font-size: 10px; color: #16A34A; font-weight: 800; margin-top: 8px;">
                        ✓ Соблюдение ч. 5 ст. 18 152-ФЗ
                    </div>
                </div>

                <div class="card-glass" style="border-top: 4px solid #10B981;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 800; color: #059669;">Политика и согласия</span>
                        <span style="font-size: 16px;">📝</span>
                    </div>
                    <h3 style="font-size: 14px; font-weight: 900; margin-bottom: 6px;">Чекбоксы под формы</h3>
                    <p style="font-size: 11px; color: #475569; line-height: 1.45;">
                        Каждая кнопка сопровождается обязательным чекбоксом согласия и юридически выверенной Политикой обработки с реквизитами вашей компании.
                    </p>
                    <div style="font-size: 10px; color: #16A34A; font-weight: 800; margin-top: 8px;">
                        ✓ Защита от жалоб в РКН
                    </div>
                </div>

                <div class="card-glass" style="border-top: 4px solid #F59E0B;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 800; color: #D97706;">ФНС России</span>
                        <span style="font-size: 16px;">🧾</span>
                    </div>
                    <h3 style="font-size: 14px; font-weight: 900; margin-bottom: 6px;">Чеки для бухгалтерии</h3>
                    <p style="font-size: 11px; color: #475569; line-height: 1.45;">
                        Работаем официально по ФЗ № 422-ФЗ (Самозанятость). Выдаем электронный фискальный чек с QR-кодом для учета расходов ИП или ООО.
                    </p>
                    <div style="font-size: 10px; color: #16A34A; font-weight: 800; margin-top: 8px;">
                        ✓ Уменьшает налог компании
                    </div>
                </div>
            </div>

            <div style="margin-top: 12px; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px; display: flex; align-items: center; gap: 12px;">
                <div style="width: 28px; height: 28px; border-radius: 8px; background: #ECFDF5; color: #059669; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 900; flex-shrink: 0;">
                    🛡️
                </div>
                <div style="font-size: 11.5px; color: #334155; line-height: 1.4;">
                    <strong>Протокол 72-часового удаления:</strong> Данные ваших клиентов не накапливаются в публичных сетевых хранилищах. После моментальной доставки заявки вам в Telegram и таблицу запускается автоматическая очистка промежуточных логов.
                </div>
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Полное соответствие законодательству РФ</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 8: КУДА ИДУТ ЗАЯВКИ (МОКАП TELEGRAM) ==================== -->
    <div class="slide">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slide-tag">Лидогенерация</div>
                <div class="slide-num">08 / 10</div>
            </div>
        </div>

        <div class="content">
            <h2 class="slide-headline">Куда приходят заявки: мгновенно и без потерь</h2>
            <p class="slide-sub">Трехуровневая система маршрутизации: вы не упустите ни одного клиента даже ночью.</p>

            <div class="grid-bento-hero" style="gap: 16px;">
                <!-- Мокап реального сообщения из Telegram бота -->
                <div>
                    <div style="font-size: 11px; font-weight: 800; color: #64748B; text-transform: uppercase; margin-bottom: 6px;">
                        Канал 1: Telegram-бот (доставка за 0.5 секунды)
                    </div>
                    <div class="tg-bubble">
                        <div class="tg-header">
                            <div class="tg-avatar">LW</div>
                            <div>
                                <div style="font-weight: 800; color: #0F172A; font-size: 12px;">LocalWeb Bot <span style="font-size: 10px; color: #2563EB;">bot</span></div>
                                <div style="font-size: 9px; color: #94A3B8;">только что • уведомление о лиде</div>
                            </div>
                        </div>
                        <div style="font-weight: 800; color: #0F172A; font-size: 12px; margin-bottom: 6px;">
                            🚀 НОВАЯ ЗАЯВКА С САЙТА!
                        </div>
                        <div style="color: #475569; display: flex; flex-direction: column; gap: 3px; font-size: 11px;">
                            <div>👤 <strong>Клиент:</strong> Алексей Смирнов</div>
                            <div>🏢 <strong>Компания:</strong> Автосервис "Механика"</div>
                            <div>💼 <strong>Сфера:</strong> Ремонт двигателей и ТО</div>
                            <div>💬 <strong>Связь:</strong> Telegram</div>
                            <div>📞 <strong>Контакт:</strong> <span style="background: #EFF6FF; color: #2563EB; padding: 2px 5px; border-radius: 4px; font-family: monospace; font-weight: 700;">@smirnov_auto</span></div>
                            <div>📝 <strong>Пожелания:</strong> Нужен запуск сайта к открытию нового бокса в субботу</div>
                            <div style="font-size: 9px; color: #94A3B8; margin-top: 4px; border-top: 1px solid #F1F5F9; padding-top: 4px;">
                                ⏱ 14:22 • Источник: local-web.ru
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Резервные каналы -->
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <div class="card-glass">
                        <div style="font-size: 12px; font-weight: 800; color: #2563EB; margin-bottom: 2px;">
                            📊 Канал 2: Онлайн-таблица (Google Sheets / Excel)
                        </div>
                        <p style="font-size: 11px; color: #475569; line-height: 1.4;">
                            Каждый лид автоматически заносится новой строкой в таблицу: имя, телефон, дата, источник. Готовая база для отдела продаж.
                        </p>
                    </div>

                    <div class="card-glass">
                        <div style="font-size: 12px; font-weight: 800; color: #2563EB; margin-bottom: 2px;">
                            ✉️ Канал 3: Резервный дубликат на Email (Яндекс)
                        </div>
                        <p style="font-size: 11px; color: #475569; line-height: 1.4;">
                            Стилизованное письмо отправляется на вашу почту руководителя как резервная копия на случай отсутствия доступа к Telegram.
                        </p>
                    </div>

                    <div class="card-glass card-glass-emerald" style="padding: 10px 12px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 16px;">🪤</span>
                            <div style="font-size: 11px; color: #065F46; line-height: 1.35;">
                                <strong>Honeypot-ловушка:</strong> встроенный скрытый фильтр отсекает 100% спам-роботов. Никаких пустых уведомлений.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Ни один клиент не будет потерян</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 9: ЧТО ВХОДИТ В 7 500 РУБЛЕЙ ==================== -->
    <div class="slide">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slide-tag">Тариф «Всё включено»</div>
                <div class="slide-num">09 / 10</div>
            </div>
        </div>

        <div class="content">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 10px;">
                <div>
                    <h2 class="slide-headline">Что входит в фиксированные 7 500 ₽</h2>
                    <p class="slide-sub" style="margin-bottom: 0;">Никаких мелких шрифтов, доплат за адаптив или наценок в процессе работы.</p>
                </div>
                <div style="background: #2563EB; color: white; padding: 6px 14px; border-radius: 10px; text-align: right; box-shadow: 0 4px 12px rgba(37,99,235,0.3);">
                    <div style="font-size: 20px; font-weight: 900; line-height: 1;">7 500 ₽</div>
                    <div style="font-size: 9px; font-weight: 700; opacity: 0.9;">ФИНАЛЬНАЯ ЦЕНА</div>
                </div>
            </div>

            <div class="grid-4" style="gap: 10px;">
                <div class="feature-item">
                    <div class="feature-icon-box">01</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Landing Page под ключ</div>
                        <div style="font-size: 10.5px; color: #64748B;">Качественный одностраничный сайт под специфику вашей ниши.</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon-box">02</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Mobile-First верстка</div>
                        <div style="font-size: 10.5px; color: #64748B;">Удобные кнопки под большой палец, быстрый звонок и WhatsApp.</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon-box">03</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Продающий копирайтинг</div>
                        <div style="font-size: 10.5px; color: #64748B;">Пишем понятные тексты без воды, раскрывая ваши выгоды и цены.</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon-box">04</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Telegram-бот + CRM</div>
                        <div style="font-size: 10.5px; color: #64748B;">Мгновенная доставка лидов в мессенджер директора или менеджеров.</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon-box">05</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Хостинг за 0 ₽/мес</div>
                        <div style="font-size: 10.5px; color: #64748B;">Пожизненное бесплатное размещение на скоростном Edge CDN.</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon-box">06</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Привязка домена .RU</div>
                        <div style="font-size: 10.5px; color: #64748B;">Помощь в выборе и полная настройка DNS на ваши реквизиты.</div>
                    </div>
                </div>

                <div class="feature-item">
                    <div class="feature-icon-box">07</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 800; color: #0F172A;">Защита по 152-ФЗ РФ</div>
                        <div style="font-size: 10.5px; color: #64748B;">Политика конфиденциальности, чекбоксы согласий и чек ФНС.</div>
                    </div>
                </div>

                <div class="feature-item" style="border: 1.5px solid #10B981; background: #F0FDF4;">
                    <div class="feature-icon-box" style="background: #10B981; color: white;">08</div>
                    <div>
                        <div style="font-size: 12px; font-weight: 800; color: #065F46;">30 дней гарантии</div>
                        <div style="font-size: 10.5px; color: #166534;">Бесплатно заменим цены, добавим акции и фото после релиза.</div>
                    </div>
                </div>
            </div>

            <div style="margin-top: 10px; background: #EFF6FF; border-radius: 8px; padding: 8px 12px; font-size: 11px; color: #1E3A8A; font-weight: 600; text-align: center;">
                Код сайта остается у вас навсегда. Вы платите один раз — сайт работает годами без списаний.
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Фиксированная стоимость без скрытых платежей</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 10: КОНТАКТЫ И СТАРТ РАБОТЫ ==================== -->
    <div class="slide slide-grid-bg">
        <div class="header">
            <div class="brand">
                <div class="brand-icon"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg></div>
                <div class="brand-name">Local<span>Web</span></div>
            </div>
            <div class="header-meta">
                <div class="slot-pill"><span class="slot-dot"></span> Начните без предоплаты</div>
                <div class="slide-num">10 / 10</div>
            </div>
        </div>

        <div class="content">
            <div class="grid-bento-hero" style="gap: 20px;">
                <div>
                    <span class="badge-emerald" style="margin-bottom: 8px;">Старт без риска</span>
                    <h2 style="font-size: 28px; font-weight: 900; line-height: 1.2; letter-spacing: -0.8px; color: #0F172A; margin-bottom: 10px;">
                        Получите рабочий черновик вашего сайта уже завтра
                    </h2>
                    <p style="font-size: 13px; color: #64748B; line-height: 1.45; margin-bottom: 14px;">
                        Напишите нам в Telegram и коротко расскажите о своем деле. Мы соберем работающую страницу и пришлем ссылку прямо на ваш смартфон.
                    </p>

                    <div class="card-glass card-glass-emerald" style="padding: 12px 14px;">
                        <div style="font-size: 11px; font-weight: 800; color: #059669; margin-bottom: 2px;">
                            Напоминаем главное правило:
                        </div>
                        <div style="font-size: 13px; font-weight: 800; color: #065F46; line-height: 1.35;">
                            Оплата 7 500 ₽ только после того, как вы лично проверите сайт на своем телефоне и скажете: «Мне нравится!»
                        </div>
                    </div>
                </div>

                <!-- Контактная карточка -->
                <div class="card-glass card-glass-blue" style="padding: 16px;">
                    <div style="font-size: 15px; font-weight: 900; color: #0F172A; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                        <span>Прямые контакты студии</span>
                        <span class="badge-blue">На связи</span>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;">
                            <span style="color: #64748B;">Официальный сайт:</span>
                            <a href="https://local-web.ru" style="color: #2563EB; font-weight: 800; text-decoration: none;">local-web.ru</a>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;">
                            <span style="color: #64748B;">Telegram разработчика:</span>
                            <a href="https://t.me/LocalWebRu" style="color: #2563EB; font-weight: 800; text-decoration: none;">@LocalWebRu</a>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;">
                            <span style="color: #64748B;">Telegram-бот заявок:</span>
                            <span style="font-weight: 700; color: #0F172A;">@LocalWebRuBot</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;">
                            <span style="color: #64748B;">Рабочий Email:</span>
                            <a href="mailto:jarovenkoaleksander@yandex.ru" style="color: #334155; font-weight: 600; text-decoration: none;">jarovenkoaleksander@yandex.ru</a>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px;">
                            <span style="color: #64748B;">Исполнитель:</span>
                            <span style="font-weight: 700; color: #0F172A;">Яровенко А. С. (Самозанятый)</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding-top: 2px;">
                            <span style="color: #64748B;">ИНН в реестре ФНС:</span>
                            <span style="font-family: monospace; font-weight: 700; color: #64748B;">420560867537</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <div>LocalWeb • Сайты для малого бизнеса с оплатой за результат</div>
            <div>https://local-web.ru • Написать в Telegram: @LocalWebRu</div>
        </div>
    </div>

</body>
</html>
'''

with open('presentation.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
html_path = os.path.abspath('presentation.html')
pdf_path = os.path.abspath('LocalWeb_Presentation.pdf')
screenshot_path = os.path.abspath('presentation_cover_v2.png')

# 1. Generate PDF
cmd_pdf = [
    chrome,
    '--headless=new',
    '--disable-gpu',
    f'--print-to-pdf={pdf_path}',
    '--no-pdf-header-footer',
    html_path
]
subprocess.run(cmd_pdf, check=True)

# 2. Generate Cover Screenshot
cmd_img = [
    chrome,
    '--headless=new',
    '--disable-gpu',
    '--window-size=1122,793',
    f'--screenshot={screenshot_path}',
    html_path
]
subprocess.run(cmd_img, check=True)

print("PDF and Screenshot generated successfully!")
