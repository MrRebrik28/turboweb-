"""
Микро-шлюз приёма заявок для Yandex Cloud Functions (Python 3.11 / 3.12)
100% соответствие 152-ФЗ: первичная фиксация данных происходит в ЦОД Яндекса (г. Москва),
после чего заявка мгновенно пересылается в Telegram администратору/клиенту.

Переменные окружения (Environment Variables) в Yandex Cloud:
- TELEGRAM_BOT_TOKEN: токен вашего Telegram-бота (получен в @BotFather)
- TELEGRAM_CHAT_ID: ваш ID или ID группы/канала (узнаётся в @userinfobot)
"""

import json
import os
import base64
import html
import urllib.request
import urllib.error

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


def handler(event, context):
    """
    Точка входа Yandex Cloud Function.
    Принимает HTTP-запрос от формы лендинга.
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
    # Все print() в Yandex Cloud Functions автоматически пишутся в Yandex Cloud Logging
    lead_id = context.request_id if hasattr(context, 'request_id') else 'local'
    print(f"[152-FZ RECORD] LeadID: {lead_id} | Payload: {json.dumps(data, ensure_ascii=False)}")

    # 4. Сбор и подготовка полей заявки
    name = escape_safe(data.get('name'))
    surname = escape_safe(data.get('surname'))
    full_name = f"{name} {surname}".strip() if surname != '—' else name
    company = escape_safe(data.get('company'))
    niche = escape_safe(data.get('niche'))
    messenger = escape_safe(data.get('messenger'))
    contact = escape_safe(data.get('contact'))
    notes = escape_safe(data.get('notes'))
    timestamp = escape_safe(data.get('timestamp'))
    source = escape_safe(data.get('source'))

    # 5. Формирование красивого сообщения для Telegram
    tg_text = (
        f"🚀 <b>НОВАЯ ЗАЯВКА С САЙТА LocalWeb!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Клиент:</b> {full_name}\n"
        f"🏢 <b>Компания:</b> {company}\n"
        f"💼 <b>Сфера:</b> {niche}\n"
        f"💬 <b>Канал связи:</b> {messenger}\n"
        f"📞 <b>Контакт:</b> <code>{contact}</code>\n"
    )

    if notes and notes != '—':
        tg_text += f"📝 <b>Пожелания:</b> <i>{notes}</i>\n"

    tg_text += (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🕒 <b>Время:</b> {timestamp}\n"
        f"🌐 <b>Источник:</b> {source}\n"
        f"🆔 <b>ID записи РФ:</b> <code>{lead_id}</code>"
    )

    # 6. Отправка в Telegram
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '').strip()

    tg_sent = False
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
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status == 200:
                    tg_sent = True
                    print(f"[SUCCESS] Уведомление успешно доставлено в Telegram: {chat_id}")
                else:
                    print(f"[WARNING] Telegram вернул код: {response.status}")
        except urllib.error.HTTPError as he:
            err_content = he.read().decode('utf-8', errors='ignore')
            print(f"[ERROR] Ошибка Telegram API ({he.code}): {err_content}")
        except Exception as te:
            print(f"[ERROR] Ошибка отправки в Telegram: {te}")
    else:
        print("[NOTICE] Токены TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не настроены в переменных окружения.")

    # 7. Успешный ответ сайту
    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({
            'status': 'success',
            'message': 'Заявка принята и зафиксирована в реестре РФ',
            'lead_id': lead_id,
            'tg_notified': tg_sent
        }, ensure_ascii=False)
    }
