import os
import subprocess

html_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Презентация студии LocalWeb</title>
    <style>
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
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #F8FAFC;
            color: #0F172A;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        .slide {
            width: 297mm;
            height: 210mm;
            page-break-after: always;
            break-after: page;
            position: relative;
            overflow: hidden;
            padding: 14mm 18mm 12mm 18mm;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            background: #F8FAFC;
        }
        .slide-dark {
            background: #0F172A;
            color: #FFFFFF;
        }
        
        /* Top Navigation Header on Slides */
        .slide-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1.5px solid #E2E8F0;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }
        .slide-dark .slide-header {
            border-bottom-color: #334155;
        }
        .logo-wrap {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .logo-box {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: #2563EB;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 900;
            font-size: 16px;
        }
        .logo-text {
            font-size: 20px;
            font-weight: 900;
            letter-spacing: -0.5px;
            color: #0F172A;
        }
        .slide-dark .logo-text {
            color: #FFFFFF;
        }
        .logo-text span {
            color: #2563EB;
        }
        .badge {
            background: #EFF6FF;
            color: #2563EB;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid #DBEAFE;
        }
        .slide-dark .badge {
            background: rgba(37, 99, 235, 0.2);
            color: #60A5FA;
            border-color: rgba(96, 165, 250, 0.3);
        }
        .slide-num {
            font-size: 13px;
            font-weight: 700;
            color: #94A3B8;
        }

        /* Slide Content Area */
        .slide-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .slide-title {
            font-size: 28px;
            font-weight: 900;
            line-height: 1.15;
            letter-spacing: -0.5px;
            color: #0F172A;
            margin-bottom: 6px;
        }
        .slide-dark .slide-title {
            color: #FFFFFF;
        }
        .slide-subtitle {
            font-size: 14px;
            color: #64748B;
            line-height: 1.4;
            margin-bottom: 16px;
        }
        .slide-dark .slide-subtitle {
            color: #94A3B8;
        }

        /* Footer */
        .slide-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #E2E8F0;
            padding-top: 8px;
            font-size: 11px;
            color: #64748B;
        }
        .slide-dark .slide-footer {
            border-top-color: #334155;
            color: #64748B;
        }
        .slide-footer a {
            color: #2563EB;
            text-decoration: none;
            font-weight: 700;
        }
        .slide-dark .slide-footer a {
            color: #60A5FA;
        }

        /* Grid Cards Layouts */
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        .grid-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 16px;
        }
        .grid-4 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 14px;
        }

        /* Card Styles */
        .card {
            background: #FFFFFF;
            border: 1.5px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
        }
        .slide-dark .card {
            background: #1E293B;
            border-color: #334155;
        }
        .card-danger {
            background: #FFF5F5;
            border-color: #FED7D7;
        }
        .card-success {
            background: #F0FDF4;
            border-color: #BBF7D0;
        }
        .card-primary {
            background: #EFF6FF;
            border-color: #BFDBFE;
        }

        .card-title {
            font-size: 16px;
            font-weight: 800;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .text-danger { color: #DC2626; }
        .text-success { color: #16A34A; }
        .text-primary { color: #2563EB; }

        .list-items {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 12px;
            line-height: 1.45;
            color: #334155;
        }
        .list-items li {
            position: relative;
            padding-left: 18px;
        }
        .list-items li::before {
            content: "•";
            position: absolute;
            left: 4px;
            color: #2563EB;
            font-weight: 900;
            font-size: 14px;
        }
        .list-danger li::before { content: "✕"; color: #DC2626; font-size: 11px; }
        .list-success li::before { content: "✓"; color: #16A34A; font-size: 12px; }

        /* Cover Slide Specifics */
        .cover-hero {
            text-align: center;
            max-width: 220mm;
            margin: 0 auto;
        }
        .cover-tag {
            display: inline-block;
            background: rgba(37, 99, 235, 0.15);
            color: #60A5FA;
            padding: 6px 18px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 16px;
            border: 1px solid rgba(96, 165, 250, 0.3);
        }
        .cover-title {
            font-size: 38px;
            font-weight: 900;
            line-height: 1.15;
            letter-spacing: -1px;
            margin-bottom: 14px;
        }
        .cover-title span {
            color: #38BDF8;
        }
        .cover-subtitle {
            font-size: 17px;
            color: #94A3B8;
            line-height: 1.5;
            margin-bottom: 26px;
        }
        .stat-banner {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 16px;
            margin-top: 10px;
        }
        .stat-card {
            background: rgba(30, 41, 59, 0.8);
            border: 1.5px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 16px 20px;
            text-align: center;
        }
        .stat-val {
            font-size: 30px;
            font-weight: 900;
            color: #38BDF8;
            line-height: 1;
            margin-bottom: 6px;
        }
        .stat-label {
            font-size: 13px;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 2px;
        }
        .stat-desc {
            font-size: 11px;
            color: #94A3B8;
        }

        /* Step Circles */
        .step-num {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background: #2563EB;
            color: white;
            font-weight: 900;
            font-size: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }

        /* Pill Features */
        .pill-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .pill-item {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 12px 14px;
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }
        .pill-icon {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            background: #EFF6FF;
            color: #2563EB;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            flex-shrink: 0;
            font-weight: 900;
        }

        /* Law Badge */
        .law-card {
            background: #FFFFFF;
            border: 1.5px solid #E2E8F0;
            border-radius: 12px;
            padding: 18px;
            position: relative;
        }
        .law-tag {
            position: absolute;
            top: 14px;
            right: 14px;
            background: #FEF3C7;
            color: #B45309;
            font-size: 10px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 4px;
        }

        /* Contact Details */
        .contact-box {
            background: #FFFFFF;
            border: 2px solid #2563EB;
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.08);
        }
    </style>
</head>
<body>

    <!-- ==================== СЛАЙД 1: ОБЛОЖКА ==================== -->
    <div class="slide slide-dark">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Коммерческое предложение 2026</div>
        </div>

        <div class="slide-content">
            <div class="cover-hero">
                <div class="cover-tag">Разработка под ключ • Без предоплаты</div>
                <h1 class="cover-title">Сайты для малого бизнеса,<br>которые приносят <span>клиентов</span>, а не расходы</h1>
                <p class="cover-subtitle">
                    Создаем быстрые и конверсионные сайты с готовым рабочим прототипом за 24 часа.<br>
                    Без навязанных подписок, без ежемесячной абонентской платы и со 100% соблюдением законов РФ.
                </p>

                <div class="stat-banner">
                    <div class="stat-card">
                        <div class="stat-val">7 500 ₽</div>
                        <div class="stat-label">Фиксированная цена</div>
                        <div class="stat-desc">Под ключ. Без скрытых доплат</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-val">24 часа</div>
                        <div class="stat-label">Прототип до оплаты</div>
                        <div class="stat-desc">Оцениваете сайт на своем телефоне</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-val">0 ₽ / мес</div>
                        <div class="stat-label">Пожизненный хостинг</div>
                        <div class="stat-desc">Без плат за Tilda, CMS и движки</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>Официальный сайт: <a href="https://local-web.ru">local-web.ru</a> • Студия LocalWeb</div>
            <div>Руководитель: Александр Яровенко • TG: @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 2: ПРОБЛЕМА РЫНКА VS РЕШЕНИЕ ==================== -->
    <div class="slide">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Сравнение подходов</div>
            <div class="slide-num">02 / 10</div>
        </div>

        <div class="slide-content">
            <h2 class="slide-title">Почему бизнес боится заказывать сайты?</h2>
            <p class="slide-subtitle">Большинство предпринимателей уже обжигались на веб-студиях. Мы перевернули привычные правила игры.</p>

            <div class="grid-2">
                <div class="card card-danger">
                    <div class="card-title text-danger">
                        <span>✕</span> Как делают 90% веб-студий
                    </div>
                    <ul class="list-items list-danger">
                        <li><strong>Предоплата 50–100%:</strong> Вы платите от 40 000 ₽ вперед, не понимая, что получите в итоге.</li>
                        <li><strong>Сроки от 3 до 8 недель:</strong> Бесконечные созвоны, заполнение ТЗ на 20 страниц и срыв дедлайнов.</li>
                        <li><strong>«Игла» абонентской платы:</strong> Вас сажают на Tilda или Bitrix — платите от 750 до 3 000 ₽ каждый месяц (до 36 000 ₽/год). Забыли оплатить — сайт отключен.</li>
                        <li><strong>Медленные сайты:</strong> Конструкторы перегружены тяжелым кодом. Загрузка 5–8 секунд — клиенты уходят к конкурентам.</li>
                        <li><strong>Риск штрафов:</strong> Отсутствие политики конфиденциальности по 152-ФЗ грозит штрафами до 6 000 000 ₽.</li>
                    </ul>
                </div>

                <div class="card card-success">
                    <div class="card-title text-success">
                        <span>✓</span> Стандарт работы LocalWeb
                    </div>
                    <ul class="list-items list-success">
                        <li><strong>0 ₽ предоплаты на старте:</strong> Вы сначала вживую смотрите работающий сайт на своем телефоне. Оплата — только если всё нравится.</li>
                        <li><strong>Готовый MVP за 24 часа:</strong> Быстрый запуск для получения первых заявок уже на этой неделе.</li>
                        <li><strong>0 ₽ абонентской платы НАВСЕГДА:</strong> Чистый HTML5/CSS код без сторонних платных движков. Хостинг бесплатный.</li>
                        <li><strong>Мгновенная загрузка (0.8 сек):</strong> 95–100 баллов в Google PageSpeed. Идеально открывается даже при слабом 4G.</li>
                        <li><strong>100% защита по законам РФ:</strong> Локализация в Москве, согласия на обработку, фискальный чек ФНС.</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>LocalWeb • Сайты для локального бизнеса</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 3: ПРИНЦИП "ОПЛАТА ЗА РЕЗУЛЬТАТ" ==================== -->
    <div class="slide">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Бизнес-модель</div>
            <div class="slide-num">03 / 10</div>
        </div>

        <div class="slide-content">
            <h2 class="slide-title">Наш принцип: сначала результат — оплата потом</h2>
            <p class="slide-subtitle">Мы полностью убрали финансовый риск для заказчика. Никаких «котов в мешке» и пустых обещаний.</p>

            <div class="grid-3">
                <div class="card">
                    <div class="step-num">1</div>
                    <h3 style="font-size: 16px; font-weight: 800; margin-bottom: 6px;">Экспресс-старт за 10 минут</h3>
                    <p style="font-size: 12px; color: #64748B; line-height: 1.45; margin-bottom: 10px;">
                        Вам не нужно писать сложные технические задания. Вы просто рассказываете о своем бизнесе в переписке или голосовым сообщением в Telegram.
                    </p>
                    <div style="background: #F1F5F9; padding: 8px 10px; border-radius: 6px; font-size: 11px; color: #475569; font-weight: 600;">
                        Предоплата: 0 ₽
                    </div>
                </div>

                <div class="card" style="border-color: #BFDBFE; background: #F8FAFC;">
                    <div class="step-num" style="background: #2563EB;">2</div>
                    <h3 style="font-size: 16px; font-weight: 800; margin-bottom: 6px;">Тест-драйв на смартфоне</h3>
                    <p style="font-size: 12px; color: #64748B; line-height: 1.45; margin-bottom: 10px;">
                        Ровно через 24 часа мы присылаем вам секретную ссылку. Вы открываете настоящий интерактивный сайт на своем телефоне, нажимаете кнопки и проверяете подачу.
                    </p>
                    <div style="background: #EFF6FF; padding: 8px 10px; border-radius: 6px; font-size: 11px; color: #2563EB; font-weight: 600;">
                        Срок: 24 часа
                    </div>
                </div>

                <div class="card">
                    <div class="step-num" style="background: #10B981;">3</div>
                    <h3 style="font-size: 16px; font-weight: 800; margin-bottom: 6px;">Решение без давления</h3>
                    <p style="font-size: 12px; color: #64748B; line-height: 1.45; margin-bottom: 10px;">
                        Если вам всё нравится — вы оплачиваете 7 500 ₽, мы подключаем ваш домен и настраиваем ботов. Если нет — вы не платите ни рубля, и мы расходимся друзьями.
                    </p>
                    <div style="background: #ECFDF5; padding: 8px 10px; border-radius: 6px; font-size: 11px; color: #059669; font-weight: 600;">
                        Оплата: 7 500 ₽ (по факту)
                    </div>
                </div>
            </div>

            <div style="margin-top: 14px; background: #EFF6FF; border: 1.5px dashed #60A5FA; border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 13px; font-weight: 700; color: #1E40AF;">
                    🛡️ Мы уверены в качестве своей работы, поэтому берем весь коммерческий риск на себя.
                </div>
                <div style="font-size: 12px; font-weight: 800; color: #2563EB;">Гарантия честной сделки</div>
            </div>
        </div>

        <div class="slide-footer">
            <div>LocalWeb • Прозрачная разработка для бизнеса</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 4: ПОШАГОВЫЙ ПРОЦЕСС ==================== -->
    <div class="slide">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Этапы работы</div>
            <div class="slide-num">04 / 10</div>
        </div>

        <div class="slide-content">
            <h2 class="slide-title">От вашей идеи до готового сайта за 3 дня</h2>
            <p class="slide-subtitle">Четкий и структурированный производственный процесс без задержек и бюрократии.</p>

            <div class="grid-4">
                <div class="card">
                    <div style="color: #2563EB; font-weight: 900; font-size: 12px; margin-bottom: 4px;">ДЕНЬ 1 (УТРО)</div>
                    <div class="card-title">1. Экспресс-бриф</div>
                    <p style="font-size: 11px; color: #64748B; line-height: 1.4;">
                        10-минутный диалог в Telegram. Уточняем специфику бизнеса, ключевые преимущества, прайс-лист, фото (если есть) и контакты для приема заказов.
                    </p>
                </div>

                <div class="card">
                    <div style="color: #2563EB; font-weight: 900; font-size: 12px; margin-bottom: 4px;">ДЕНЬ 1–2</div>
                    <div class="card-title">2. Сборка MVP</div>
                    <p style="font-size: 11px; color: #64748B; line-height: 1.4;">
                        Пишем емкие продающие тексты без "воды", верстаем современный адаптивный дизайн, настраиваем удобные формы захвата контактов.
                    </p>
                </div>

                <div class="card">
                    <div style="color: #2563EB; font-weight: 900; font-size: 12px; margin-bottom: 4px;">ДЕНЬ 2</div>
                    <div class="card-title">3. Демо и правки</div>
                    <p style="font-size: 11px; color: #64748B; line-height: 1.4;">
                        Вы тестируете сайт со смартфона. Если нужно скорректировать формулировку цены, акцент или фотографию — вносим правки моментально.
                    </p>
                </div>

                <div class="card" style="border-color: #10B981; background: #F0FDF4;">
                    <div style="color: #059669; font-weight: 900; font-size: 12px; margin-bottom: 4px;">ДЕНЬ 3</div>
                    <div class="card-title" style="color: #065F46;">4. Релиз и запуск</div>
                    <p style="font-size: 11px; color: #166534; line-height: 1.4;">
                        Привязываем ваш домен, выпускаем SSL, подключаем Telegram-бота, передаем права, выдаем официальный фискальный чек ФНС.
                    </p>
                </div>
            </div>

            <div style="margin-top: 16px;" class="card">
                <div style="font-size: 13px; font-weight: 800; color: #0F172A; margin-bottom: 6px;">
                    🎁 Бонус после запуска: 30 дней бесплатной поддержки
                </div>
                <div style="font-size: 12px; color: #64748B; line-height: 1.4;">
                    В течение первого месяца работы мы бесплатно заменим цены, обновим акции, поменяем контактный телефон или текст. Вы не останетесь один на один с сайтом.
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>LocalWeb • Понятный путь к результату</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 5: ТЕХНОЛОГИИ И ХОСТИНГ ==================== -->
    <div class="slide">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Технологии и экономия</div>
            <div class="slide-num">05 / 10</div>
        </div>

        <div class="slide-content">
            <h2 class="slide-title">Хостинг за 0 ₽: почему сайт работает бесплатно</h2>
            <p class="slide-subtitle">Мы используем современные серверные стандарты вместо устаревших и прожорливых CMS.</p>

            <div class="grid-2">
                <div class="card">
                    <div class="card-title text-primary">
                        <span>⚡</span> Чистый код вместо тяжелых CMS
                    </div>
                    <p style="font-size: 12px; color: #475569; line-height: 1.5; margin-bottom: 12px;">
                        Обычные сайты на WordPress или Tilda под капотом подгружают сотни мегабайт сторонних скриптов, баз данных и плагинов. Поэтому они требуют постоянной аренды мощных серверов и ежемесячной оплаты.
                    </p>
                    <p style="font-size: 12px; color: #475569; line-height: 1.5;">
                        <strong>Сайты LocalWeb написаны на чистом HTML5, Tailwind CSS и Vanilla JavaScript:</strong> они весят меньше одной фотографии, открываются за доли секунды и не требуют базы данных, которая может "упасть" или заразиться вирусом.
                    </p>
                </div>

                <div class="card">
                    <div class="card-title text-success">
                        <span>🌐</span> Облачный Edge CDN хостинг (0 ₽/мес)
                    </div>
                    <p style="font-size: 12px; color: #475569; line-height: 1.5; margin-bottom: 12px;">
                        Мы размещаем сайты в отказоустойчивой мировой сети GitHub & Cloudflare Edge CDN с узлами по всему миру и в России.
                    </p>
                    <ul class="list-items list-success">
                        <li><strong>Экономия:</strong> Вы экономите от 9 000 до 36 000 ₽ каждый год на абонентских платах хостинга.</li>
                        <li><strong>Надежность 99.99%:</strong> Сайт не сломается от наплыва тысяч посетителей в рекламе.</li>
                        <li><strong>Бесплатный SSL (HTTPS):</strong> Бессрочный сертификат безопасности с зеленым замочком в браузере.</li>
                    </ul>
                </div>
            </div>

            <div style="margin-top: 14px; background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-around;">
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: 900; color: #16A34A;">98 / 100</div>
                    <div style="font-size: 11px; color: #64748B;">Google PageSpeed (Mobile)</div>
                </div>
                <div style="text-align: center; border-left: 1px solid #CBD5E1; border-right: 1px solid #CBD5E1; padding: 0 20px;">
                    <div style="font-size: 20px; font-weight: 900; color: #2563EB;">0.8 сек</div>
                    <div style="font-size: 11px; color: #64748B;">Время полной загрузки</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: 900; color: #0F172A;">0 ₽</div>
                    <div style="font-size: 11px; color: #64748B;">Ежемесячная плата за хостинг</div>
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>LocalWeb • Инженерный подход к веб-разработке</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 6: ДОМЕН И СОБСТВЕННОСТЬ ==================== -->
    <div class="slide">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Правовая чистота</div>
            <div class="slide-num">06 / 10</div>
        </div>

        <div class="slide-content">
            <h2 class="slide-title">Домен: ваша 100% юридическая собственность</h2>
            <p class="slide-subtitle">Мы категорически против привязки клиентов к студии через удержание прав на домен.</p>

            <div class="grid-2">
                <div class="card">
                    <div class="card-title text-primary">
                        <span>🏷️</span> Домен в зоне .RU / .РФ оформляется на вас
                    </div>
                    <p style="font-size: 12px; color: #475569; line-height: 1.5; margin-bottom: 10px;">
                        В отличие от недобросовестных агентств, которые регистрируют домены на своих сотрудников или вебмастеров, мы регистрируем домен <strong>строго на ваши данные</strong>:
                    </p>
                    <ul class="list-items">
                        <li>На реквизиты вашей компании (ИП или ООО);</li>
                        <li>Либо на ваш паспорт (для физических лиц и самозанятых).</li>
                    </ul>
                    <p style="font-size: 12px; color: #475569; line-height: 1.5; margin-top: 10px;">
                        Вы являетесь единственным полноправным администратором домена в государственном реестре Координационного центра Рунета (ТЦИ).
                    </p>
                </div>

                <div class="card">
                    <div class="card-title text-success">
                        <span>🛡️</span> Полная свобода и прозрачность
                    </div>
                    <ul class="list-items list-success">
                        <li><strong>Никакого шантажа:</strong> Никто не сможет потребовать выкуп за домен, если вы решите сменить подрядчика.</li>
                        <li><strong>Честная стоимость продления:</strong> Вы платите за продление напрямую аккредитованному регистратору (от ~190 ₽ в год) без наших скрытых наценок.</li>
                        <li><strong>Полная настройка DNS:</strong> Мы профессионально настраиваем все системные записи (A, CNAME, SPF, DKIM), чтобы сайт и почта работали без сбоев.</li>
                        <li><strong>Если у вас уже есть домен:</strong> Мы бесплатно подключим сайт к вашему существующему доменному имени.</li>
                    </ul>
                </div>
            </div>

            <div style="margin-top: 14px; background: #EFF6FF; border: 1.5px solid #BFDBFE; border-radius: 10px; padding: 12px 16px;">
                <div style="font-size: 12px; color: #1E40AF; line-height: 1.45;">
                    💡 <strong>Пример:</strong> Наш собственный домен <strong style="color: #2563EB;">local-web.ru</strong> зарегистрирован по аналогичной схеме напрямую у официального аккредитованного регистратора РФ и защищен двухфакторной аутентификацией.
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>LocalWeb • Домен принадлежит только вам</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 7: ЗАКОНОДАТЕЛЬСТВО РФ ==================== -->
    <div class="slide">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Безопасность и закон</div>
            <div class="slide-num">07 / 10</div>
        </div>

        <div class="slide-content">
            <h2 class="slide-title">100% защита от штрафов Роскомнадзора</h2>
            <p class="slide-subtitle">Штрафы за нарушения работы с персональными данными в РФ достигают 6 000 000 ₽. Мы защищаем ваш бизнес.</p>

            <div class="grid-3">
                <div class="law-card">
                    <div class="law-tag">152-ФЗ РФ</div>
                    <div class="card-title text-primary">Локализация данных</div>
                    <p style="font-size: 11px; color: #475569; line-height: 1.45; margin-bottom: 8px;">
                        Вся первичная фиксация и сбор заявок производятся на серверах, физически расположенных в Российской Федерации (Яндекс Облако, Москва).
                    </p>
                    <div style="font-size: 10px; color: #16A34A; font-weight: 700;">✓ Требование ч. 5 ст. 18 152-ФЗ соблюдено</div>
                </div>

                <div class="law-card">
                    <div class="law-tag">152-ФЗ РФ</div>
                    <div class="card-title text-primary">Согласие и Политика</div>
                    <p style="font-size: 11px; color: #475569; line-height: 1.45; margin-bottom: 8px;">
                        В каждой форме устанавливается обязательный чекбокс согласия, а на сайте размещается персональная Политика обработки данных с реквизитами вашей компании.
                    </p>
                    <div style="font-size: 10px; color: #16A34A; font-weight: 700;">✓ Защита от проверок РКН</div>
                </div>

                <div class="law-card">
                    <div class="law-tag">ФНС РФ</div>
                    <div class="card-title text-primary">Чеки и Бухгалтерия</div>
                    <p style="font-size: 11px; color: #475569; line-height: 1.45; margin-bottom: 8px;">
                        Официальная работа в статусе Самозанятого (ФЗ № 422-ФЗ). Предоставляем электронный чек из приложения «Мой налог» для уменьшения вашей налогооблагаемой базы.
                    </p>
                    <div style="font-size: 10px; color: #16A34A; font-weight: 700;">✓ Официально для ИП и ООО</div>
                </div>
            </div>

            <div style="margin-top: 14px; background: #F8FAFC; border: 1.5px solid #E2E8F0; border-radius: 10px; padding: 12px 16px;">
                <div style="font-size: 12px; color: #334155; line-height: 1.45;">
                    🔐 <strong>Протокол 72-часового удаления:</strong> Данные клиентов не накапливаются в публичных шлюзах. После моментальной доставки заявки вам в Telegram и таблицу запускается протокол очистки промежуточных логов.
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>LocalWeb • Юридически безупречные решения</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 8: КУДА ИДУТ ЗАЯВКИ ==================== -->
    <div class="slide">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Лидогенерация</div>
            <div class="slide-num">08 / 10</div>
        </div>

        <div class="slide-content">
            <h2 class="slide-title">Куда приходят заявки: мгновенно и без потерь</h2>
            <p class="slide-subtitle">Вы не упустите ни одного клиента. Трехуровневая система маршрутизации лидов.</p>

            <div class="grid-3">
                <div class="card">
                    <div style="font-size: 26px; margin-bottom: 6px;">📱</div>
                    <div class="card-title text-primary">1. Telegram-бот (0.5 сек)</div>
                    <p style="font-size: 12px; color: #475569; line-height: 1.45;">
                        Заявка моментально падает в ваш личный Telegram или в рабочий чат менеджеров.
                    </p>
                    <ul class="list-items" style="margin-top: 8px;">
                        <li>Имя и контакты клиента в 1 клик</li>
                        <li>Ниша и комментарий к заказу</li>
                        <li>Время и страница перехода</li>
                    </ul>
                </div>

                <div class="card">
                    <div style="font-size: 26px; margin-bottom: 6px;">📊</div>
                    <div class="card-title text-primary">2. Онлайн-CRM таблица</div>
                    <p style="font-size: 12px; color: #475569; line-height: 1.45;">
                        Каждый лид автоматически сохраняется в защищенную таблицу Google Таблицы / Excel.
                    </p>
                    <ul class="list-items" style="margin-top: 8px;">
                        <li>Удобно вести воронку продаж</li>
                        <li>Все контакты в одном надежном месте</li>
                        <li>Экспорт в любую CRM-систему</li>
                    </ul>
                </div>

                <div class="card">
                    <div style="font-size: 26px; margin-bottom: 6px;">✉️</div>
                    <div class="card-title text-primary">3. Резерв на Email</div>
                    <p style="font-size: 12px; color: #475569; line-height: 1.45;">
                        Красивое форматированное HTML-письмо с деталями заказа на вашу почту руководителя (Яндекс).
                    </p>
                    <ul class="list-items" style="margin-top: 8px;">
                        <li>Резервная копия всех обращений</li>
                        <li>Удобно для архива и юристов</li>
                        <li>100% гарантия сохранности данных</li>
                    </ul>
                </div>
            </div>

            <div style="margin-top: 14px; background: #F0FDF4; border: 1.5px solid #BBF7D0; border-radius: 10px; padding: 12px 16px; display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 22px;">🪤</div>
                <div style="font-size: 12px; color: #166534; line-height: 1.4;">
                    <strong>Встроенная защита от ботов (Honeypot):</strong> Невидимая ловушка для спам-роботов на сайте отсекает 100% спама и рассылок. Вы получаете уведомления только о реальных заявках от живых клиентов.
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>LocalWeb • Конверсионные инструменты захвата</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 9: ЧТО ВХОДИТ В 7 500 РУБЛЕЙ ==================== -->
    <div class="slide">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Тариф «Всё включено»</div>
            <div class="slide-num">09 / 10</div>
        </div>

        <div class="slide-content">
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px;">
                <div>
                    <h2 class="slide-title">Что входит в фиксированные 7 500 ₽</h2>
                    <p class="slide-subtitle" style="margin-bottom: 0;">Полный комплект для запуска продаж в интернете без необходимости что-либо докупать.</p>
                </div>
                <div style="background: #2563EB; color: white; padding: 8px 18px; border-radius: 12px; text-align: right;">
                    <div style="font-size: 20px; font-weight: 900; line-height: 1;">7 500 ₽</div>
                    <div style="font-size: 10px; font-weight: 700; opacity: 0.9;">ОДНОКРАТНО</div>
                </div>
            </div>

            <div class="pill-grid">
                <div class="pill-item">
                    <div class="pill-icon">01</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Индивидуальный Landing Page</div>
                        <div style="font-size: 11px; color: #64748B;">Продающая структура: главный экран, каталог услуг, УТП, блок доверия, FAQ, формы захвата.</div>
                    </div>
                </div>

                <div class="pill-item">
                    <div class="pill-icon">02</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Идеальная мобильная версия</div>
                        <div style="font-size: 11px; color: #64748B;">Сайт разрабатывается по принципу Mobile-First: кнопки под большой палец, быстрый звонок и WhatsApp.</div>
                    </div>
                </div>

                <div class="pill-item">
                    <div class="pill-icon">03</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Продающий копирайтинг</div>
                        <div style="font-size: 11px; color: #64748B;">Пишем понятные тексты под вашу целевую аудиторию без скучных шаблонов и воды.</div>
                    </div>
                </div>

                <div class="pill-item">
                    <div class="pill-icon">04</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Telegram-бот + CRM-таблица</div>
                        <div style="font-size: 11px; color: #64748B;">Мгновенная доставка лидов в мессенджер директора или менеджеров и табличный учет.</div>
                    </div>
                </div>

                <div class="pill-item">
                    <div class="pill-icon">05</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Пожизненный хостинг и SSL (0 ₽/мес)</div>
                        <div style="font-size: 11px; color: #64748B;">Бесплатное размещение на скоростном Edge CDN. Замочек HTTPS без ежегодных оплат.</div>
                    </div>
                </div>

                <div class="pill-item">
                    <div class="pill-icon">06</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Подключение домена .RU / .РФ</div>
                        <div style="font-size: 11px; color: #64748B;">Помощь в выборе и полная техническая привязка DNS-записей напрямую к вашему аккаунту.</div>
                    </div>
                </div>

                <div class="pill-item">
                    <div class="pill-icon">07</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #0F172A;">Пакет соответствия 152-ФЗ РФ</div>
                        <div style="font-size: 11px; color: #64748B;">Юридически выверенная Политика конфиденциальности и чекбоксы согласия для РКН.</div>
                    </div>
                </div>

                <div class="pill-item" style="border-color: #10B981; background: #F0FDF4;">
                    <div class="pill-icon" style="background: #10B981; color: white;">08</div>
                    <div>
                        <div style="font-size: 13px; font-weight: 800; color: #065F46;">30 дней бесплатной поддержки</div>
                        <div style="font-size: 11px; color: #166534;">Бесплатно заменим цены, добавим новые акции, скорректируем текст или фото после запуска.</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>LocalWeb • Фиксированная стоимость без сюрпризов</div>
            <div>https://local-web.ru • @LocalWebRu</div>
        </div>
    </div>

    <!-- ==================== СЛАЙД 10: КОНТАКТЫ И СТАРТ ==================== -->
    <div class="slide slide-dark">
        <div class="slide-header">
            <div class="logo-wrap">
                <div class="logo-box">LW</div>
                <div class="logo-text">Local<span>Web</span></div>
            </div>
            <div class="badge">Контакты и заказ</div>
            <div class="slide-num">10 / 10</div>
        </div>

        <div class="slide-content">
            <div class="grid-2" style="align-items: center; gap: 24px;">
                <div>
                    <div class="cover-tag" style="margin-bottom: 12px;">Старт без риска</div>
                    <h2 class="slide-title" style="font-size: 32px; margin-bottom: 12px;">Получите готовый прототип вашего сайта уже завтра</h2>
                    <p class="slide-subtitle" style="font-size: 14px; margin-bottom: 18px;">
                        Напишите нам в Telegram и коротко расскажите о вашей деятельности. Через 24 часа мы отправим ссылку на готовый интерактивный сайт.
                    </p>
                    <div style="background: rgba(30, 41, 59, 0.9); border: 1px solid #334155; border-radius: 12px; padding: 14px 18px;">
                        <div style="font-size: 12px; color: #94A3B8; margin-bottom: 4px;">Напоминаем:</div>
                        <div style="font-size: 14px; font-weight: 800; color: #38BDF8;">
                            Оплата 7 500 ₽ только после того, как вы лично проверите сайт на своем телефоне и скажете: «Мне нравится!»
                        </div>
                    </div>
                </div>

                <div class="contact-box" style="background: #1E293B; border-color: #2563EB;">
                    <div style="font-size: 18px; font-weight: 900; color: #FFFFFF; margin-bottom: 14px;">Прямые контакты студии:</div>
                    
                    <div style="display: flex; flex-direction: column; gap: 10px; font-size: 13px;">
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                            <span style="color: #94A3B8;">Официальный сайт:</span>
                            <a href="https://local-web.ru" style="color: #38BDF8; font-weight: 800; text-decoration: none;">local-web.ru</a>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                            <span style="color: #94A3B8;">Telegram руководителя:</span>
                            <a href="https://t.me/LocalWebRu" style="color: #38BDF8; font-weight: 800; text-decoration: none;">@LocalWebRu</a>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                            <span style="color: #94A3B8;">Telegram-бот заявок:</span>
                            <span style="color: #FFFFFF; font-weight: 700;">@LocalWebRuBot</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 8px;">
                            <span style="color: #94A3B8;">Рабочий Email:</span>
                            <a href="mailto:jarovenkoaleksander@yandex.ru" style="color: #E2E8F0; font-weight: 600; text-decoration: none;">jarovenkoaleksander@yandex.ru</a>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding-top: 4px;">
                            <span style="color: #94A3B8;">Разработчик / Исполнитель:</span>
                            <span style="color: #FFFFFF; font-weight: 700;">Яровенко А. С. (Самозанятый)</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #94A3B8;">ИНН для проверки в ФНС:</span>
                            <span style="color: #94A3B8; font-family: monospace;">420560867537</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="slide-footer">
            <div>Студия веб-разработки LocalWeb • 2026</div>
            <div>https://local-web.ru • Связаться в TG: @LocalWebRu</div>
        </div>
    </div>

</body>
</html>
'''

with open('presentation.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("presentation.html created successfully!")
