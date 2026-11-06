"""
Микро-шлюз приёма заявок и брифов для Yandex Cloud Functions (Python 3.11 / 3.12)
100% соответствие 152-ФЗ: первичная фиксация данных происходит в ЦОД Яндекса (г. Москва),
после чего заявка мгновенно пересылается в Telegram администратору и/или на Email.

Переменные окружения (Environment Variables) в Yandex Cloud:
- TELEGRAM_BOT_TOKEN: токен вашего Telegram-бота (получен в @BotFather)
- TELEGRAM_CHAT_ID: ваш ID или ID группы/канала (узнаётся в @userinfobot)

Опционально для отправки на Email (SMTP):
- SMTP_HOST: например, smtp.yandex.ru или smtp.mail.ru
- SMTP_PORT: 465 (SSL) или 587
- SMTP_USER: логин почты (например, lead@local-web.ru)
- SMTP_PASSWORD: пароль приложения для почты
- SMTP_TO: ваш email для получения заявок и брифов (например, timetry-bikes@yandex.ru или mrrebrik@yandex.ru)
"""

import json
import os
import base64
import html
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import urllib.request
import urllib.error

# Принудительно используем только IPv4, так как в облачных средах часто нет маршрутизации IPv6 к внешним серверам
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = _ipv4_only_getaddrinfo

# Заголовки CORS для работы с сайтом на любом домене
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Content-Type': 'application/json; charset=utf-8'
}


def escape_safe(val):
    """Экранирование спецсимволов HTML для безопасной отправки в Telegram."""
    if val is None:
        return '—'
    s = str(val).strip()
    return html.escape(s) if s else '—'


def send_email_smtp(subject, text_content, html_content=None):
    """Отправка email через SMTP (если настроены переменные окружения)."""
    smtp_host = os.environ.get('SMTP_HOST', '').strip()
    smtp_user = os.environ.get('SMTP_USER', '').strip()
    smtp_pass = os.environ.get('SMTP_PASSWORD', '').strip()
    smtp_to = os.environ.get('SMTP_TO', os.environ.get('NOTIFICATION_EMAIL', '')).strip()
    smtp_port = int(os.environ.get('SMTP_PORT', '465'))

    if not (smtp_host and smtp_user and smtp_pass and smtp_to):
        return False, "SMTP credentials not configured"

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = smtp_user
        msg['To'] = smtp_to

        part1 = MIMEText(text_content, 'plain', 'utf-8')
        msg.attach(part1)

        if html_content:
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.starttls()

        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [smtp_to], msg.as_string())
        server.quit()
        print(f"[SUCCESS] Email успешно отправлен на {smtp_to}")
        return True, "Email sent successfully"
    except Exception as e:
        print(f"[ERROR] Ошибка отправки Email: {e}")
        return False, str(e)


def handler(event, context):
    """
    Точка входа Yandex Cloud Function.
    Принимает HTTP-запрос от формы лендинга или страницы брифа.
    """
    http_method = event.get('httpMethod', 'GET').upper()

    # 1. Ответ на CORS Preflight (OPTIONS)
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({'status': 'ok'})
        }

    # Разрешаем только POST-запросы
    if http_method != 'POST':
        return {
            'statusCode': 405,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Метод не поддерживается. Используйте POST'})
        }

    # 2. Извлечение и парсинг тела запроса
    raw_body = event.get('body', '')
    if event.get('isBase64Encoded', False):
        try:
            raw_body = base64.b64decode(raw_body).decode('utf-8')
        except Exception as e:
            print(f"[ERROR] Ошибка декодирования base64: {e}")
            raw_body = ''

    try:
        data = json.loads(raw_body) if raw_body else {}
    except Exception as e:
        print(f"[ERROR] Невалидный JSON: {e}, сырое тело: {raw_body}")
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Некорректный формат JSON'})
        }

    # 3. Фиксация в российском реестре логов (152-ФЗ, дата-центр РФ)
    lead_id = context.request_id if hasattr(context, 'request_id') else 'local'
    print(f"[152-FZ RECORD] LeadID: {lead_id} | Payload: {json.dumps(data, ensure_ascii=False)}")

    is_brief = (data.get('type') == 'briefing') or ('brief_answers' in data) or ('project_code' in data)

    # 4. Формирование текстов сообщения для Telegram и Email
    timestamp = escape_safe(data.get('timestamp'))
    source = escape_safe(data.get('source'))

    if is_brief:
        # Режим обработки брифа
        code = escape_safe(data.get('project_code') or data.get('code'))
        company = escape_safe(data.get('company') or data.get('project_name'))
        client_name = escape_safe(data.get('name') or data.get('client_name'))
        contact = escape_safe(data.get('contact') or data.get('phone'))
        email = escape_safe(data.get('email'))
        answers_formatted = data.get('answers_text', '')

        # Если ответы переданы словарём, форматируем их
        if not answers_formatted and isinstance(data.get('brief_answers'), dict):
            parts = []
            for k, v in data.get('brief_answers', {}).items():
                parts.append(f"• <b>{html.escape(str(k))}:</b> {html.escape(str(v))}")
            answers_formatted = "\n".join(parts)

        tg_text = (
            f"📋 <b>НОВЫЙ ЗАПОЛНЕННЫЙ БРИФ ПРОЕКТА!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🔑 <b>Код проекта:</b> <code>{code}</code>\n"
            f"🏢 <b>Компания:</b> {company}\n"
            f"👤 <b>Контакт:</b> {client_name}\n"
            f"📞 <b>Телефон:</b> <code>{contact}</code>\n"
            f"✉️ <b>Email:</b> {email}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<b>КЛЮЧЕВЫЕ ТРЕБОВАНИЯ:</b>\n"
            f"{answers_formatted[:3000]}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🕒 <b>Время:</b> {timestamp}\n"
            f"🌐 <b>Источник:</b> {source}\n"
            f"🆔 <b>ID записи РФ:</b> <code>{lead_id}</code>"
        )
        email_subj = f"📋 Заполнен бриф проекта: {company} (код {code})"
        email_body = f"Заполнен новый бриф проекта {company} (код: {code})\nКонтактное лицо: {client_name}, {contact}, {email}\n\nТребования:\n{answers_formatted}"
    else:
        # Стандартная заявка с лендинга
        name = escape_safe(data.get('name'))
        surname = escape_safe(data.get('surname'))
        full_name = f"{name} {surname}".strip() if (surname and surname != '—') else name
        company = escape_safe(data.get('company'))
        niche = escape_safe(data.get('niche'))
        messenger = escape_safe(data.get('messenger'))
        contact = escape_safe(data.get('contact'))
        notes = escape_safe(data.get('notes'))

        # Кликабельный контакт для Telegram
        contact_display = f"<code>{contact}</code>"
        if messenger == 'Telegram' and contact != '—':
            clean_tg = contact.replace('@', '').replace('https://t.me/', '').replace('t.me/', '').strip()
            if clean_tg and not clean_tg.startswith('+') and not clean_tg.isdigit():
                contact_display = f'<a href="https://t.me/{clean_tg}">{contact}</a>'

        lines = [
            "🚀 <b>НОВАЯ ЗАЯВКА С САЙТА LocalWeb!</b>",
            "━━━━━━━━━━━━━━━━━━━",
            f"👤 <b>Клиент:</b> {full_name}"
        ]

        if company and company != '—':
            lines.append(f"🏢 <b>Компания:</b> {company}")
        if niche and niche != '—':
            lines.append(f"💼 <b>Сфера:</b> {niche}")

        lines.append(f"💬 <b>Канал связи:</b> {messenger}")
        lines.append(f"📞 <b>Контакт:</b> {contact_display}")

        if notes and notes != '—':
            lines.append(f"📝 <b>Пожелания:</b> <i>{notes}</i>")

        lines.extend([
            "━━━━━━━━━━━━━━━━━━━",
            f"🕒 <b>Время:</b> {timestamp}",
            f"🌐 <b>Источник:</b> {source}",
            f"🆔 <b>ID записи РФ:</b> <code>{lead_id}</code>"
        ])

        tg_text = "\n".join(lines)
        email_subj = f"🚀 Новая заявка с сайта LocalWeb: {full_name}" + (f" ({company})" if company and company != '—' else "")
        email_body = f"Новая заявка!\nИмя: {full_name}\n" + (f"Компания: {company}\n" if company and company != '—' else "") + (f"Сфера: {niche}\n" if niche and niche != '—' else "") + f"Контакт: {contact} ({messenger})\n" + (f"Пожелания: {notes}\n" if notes and notes != '—' else "")

    # 5. Отправка в Telegram
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip().strip('\'"')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '').strip().strip('\'"')

    tg_sent = False
    tg_debug = "No tokens configured"

    if bot_token and chat_id:
        tg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        tg_payload = {
            'chat_id': chat_id,
            'text': tg_text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }

        try:
            req = urllib.request.Request(
                tg_url,
                data=json.dumps(tg_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                resp_text = response.read().decode('utf-8')
                if response.status == 200:
                    tg_sent = True
                    tg_debug = "Delivered successfully"
                    print(f"[SUCCESS] Уведомление доставлено в Telegram: {chat_id}")
                else:
                    tg_debug = f"Status {response.status}: {resp_text}"
        except urllib.error.HTTPError as he:
            err_content = he.read().decode('utf-8', errors='ignore')
            tg_debug = f"Telegram API HTTP {he.code}: {err_content}"
            print(f"[ERROR] Ошибка Telegram API ({he.code}): {err_content}")
        except Exception as te:
            tg_debug = f"{type(te).__name__}: {str(te)}"
            print(f"[ERROR] Исключение при отправке в Telegram: {te}")
    else:
        tg_debug = f"Missing env tokens: token_len={len(bot_token)}, chat_id_len={len(chat_id)}"

    # 6. Отправка на Email через SMTP (если настроено)
    email_sent, email_debug = send_email_smtp(email_subj, email_body)

    # 7. Ответ клиенту
    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({
            'status': 'success',
            'message': 'Данные успешно зафиксированы и переданы',
            'lead_id': lead_id,
            'tg_notified': tg_sent,
            'tg_debug': tg_debug,
            'email_notified': email_sent,
            'email_debug': email_debug
        }, ensure_ascii=False)
    }
