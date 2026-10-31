#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LocalWeb VK Outreach — Консольный интерфейс автономного агента поиска клиентов.
Ищет бизнес-сообщества в ВК, проверяет наличие сайта, генерирует уникальные
персонализированные предложения и безопасно отправляет их в сообщения групп.

Использование:
  python run_outreach.py --dry-run                     # Безопасный предпросмотр без отправки
  python run_outreach.py --stats                       # Просмотр статистики базы данных и лимитов
  python run_outreach.py --test-group 242777884        # Тест генерации/отправки в конкретную группу
  python run_outreach.py --live --limit 5              # Реальная отправка с подтверждением
  python run_outreach.py --niche "кухни на заказ" --city "Кемерово" --dry-run
"""

import sys
import os
import argparse
import random
import time
from datetime import datetime

# Настройка безопасной кодировки для Windows консоли
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from vk_agent.config import VK_USER_TOKEN
from vk_agent.vk_api import VkApiClient, VkApiException
from vk_agent.database import OutreachDatabase
from vk_agent.outreach_agent import VkOutreachAgent
from vk_agent.spintax import generate_personalized_pitch, clean_group_name

# Стандартный пул прибыльных локальных ниш для поиска клиентов
DEFAULT_NICHES = [
    "детейлинг",
    "автосервис",
    "кузовной ремонт",
    "кухни на заказ",
    "ремонт квартир",
    "косметология",
    "барбершоп",
    "стоматология",
    "клининг"
]

# Стандартные города (начиная с домашнего региона Кемерово / Сибирь)
DEFAULT_CITIES = [
    "Кемерово",
    "Новокузнецк",
    "Новосибирск",
    "Томск",
    "Красноярск"
]

def print_banner():
    banner = """
================================================================================
   _                     _ __        __   _      ___        _                      _     
  | |    ___   ___ __ _| |\\ \\      / /__| |__   / _ \\ _   _| |_ _ __ ___  __ _  ___| |__  
  | |   / _ \\ / __/ _` | | \\ \\ /\\ / / _ \\ '_ \\ | | | | | | | __| '__/ _ \\/ _` |/ __| '_ \\ 
  | |__| (_) | (_| (_| | |  \\ V  V /  __/ |_) || |_| | |_| | |_| | |  __/ (_| | (__| | | |
  |_____\\___/ \\___\\__,_|_|   \\_/\\_/ \\___|_.__/  \\___/ \\__,_|\\__|_|  \\___|\\__,_|\\___|_| |_|

  Автономный агент лидогенерации и безопасного аутрича ВКонтакте
  Поиск бизнеса • Анализ сайтов • Уникальный Spintax • Защита от блокировок
================================================================================
"""
    print(banner)

def print_safety_rules():
    print("""
🛡️  ПРАВИЛА БЕЗОПАСНОСТИ И ЗАЩИТЫ ОТ БАНА ВКОНТАКТЕ:
  1. Суточный лимит: строго не более 15–20 сообщений в группы за 24 часа.
  2. Паузы между отправками: 75–140 секунд со случайным джиттером.
  3. Микро-паузы: каждые 3 сообщения агент делает перерыв на 3–4 минуты (эмуляция человека).
  4. 100% Уникальность текста: алгоритм Spintax с десятками тысяч вариаций (без спам-хеша).
  5. Дедупликация SQLite: группа никогда не получит сообщение повторно.
  6. Emergency Stop: при коде 14 (капча) или 9 (флуд) агент немедленно останавливается.
""")

def display_stats(db: OutreachDatabase, daily_limit: int = 15):
    stats = db.get_stats()
    sent_24h = stats["sent_last_24h"]
    quota_left = max(0, daily_limit - sent_24h)
    
    print("\n📊 --- ТЕКУЩАЯ СТАТИСТИКА ЛИДОГЕНЕРАЦИИ И КВОТ ---")
    print(f"  • Всего обнаружено групп в базе:      {stats['total_leads']}")
    print(f"  • Успешно отправлено за всё время:    {stats['total_sent']}")
    print(f"  • Отправлено за последние 24 часа:    {sent_24h} из {daily_limit} (безопасный максимум)")
    print(f"  • Доступная квота на сегодня:         {quota_left} сообщений")
    print(f"  • Отфильтровано нецелевых (пропущено): {stats['total_skipped']}")
    print(f"  • Ошибок отправки (закрытые ЛС и др): {stats['total_failed']}")
    
    recent = db.get_recent_sent(limit=3)
    if recent:
        print("\n📝 ПОСЛЕДНИЕ ОТПРАВЛЕННЫЕ СООБЩЕНИЯ:")
        for idx, r in enumerate(recent, 1):
            print(f"  [{idx}] Группа ID: {r['group_id']} | «{r['name']}» ({r['city'] or 'город не указан'})")
            print(f"      Отправлено: {r['sent_at']}")
            preview_text = r['message_text'].replace('\n', ' ')
            if len(preview_text) > 120:
                preview_text = preview_text[:120] + "..."
            print(f"      Текст: \"{preview_text}\"\n")
    print("--------------------------------------------------------------------------------")

def test_single_group(agent: VkOutreachAgent, group_id: int, niche: str = "услуг и бизнеса", 
                      city: str = "", send_live: bool = False, skip_confirm: bool = False):
    """Тестирует оценку, генерацию спинтакса и отправку в одну конкретную группу."""
    print(f"\n🧪 --- ТЕСТИРОВАНИЕ НА ГРУППЕ ID {group_id} ---")
    try:
        grp = agent.vk.get_group_by_id(group_id)
    except Exception as e:
        print(f"❌ Ошибка получения данных группы ID {group_id}: {e}")
        return

    name = grp.get("name", "")
    can_msg = grp.get("can_message", 0)
    site = grp.get("site", "")
    members = grp.get("members_count", 0)
    
    print(f"  • Название: {name}")
    print(f"  • Очищенное имя для обращения: {clean_group_name(name)}")
    print(f"  • Подписчиков: {members}")
    print(f"  • Сообщения группы открыты (can_message): {'ДА (1)' if can_msg == 1 else 'НЕТ (0)'}")
    print(f"  • Сайт: '{site}'")

    is_qual, tier, reason = agent.evaluate_group(grp)
    print(f"  • Оценка фильтра: {'✅ Квалифицирован' if is_qual else f'❌ Отклонен ({reason})'}")
    print(f"  • Категория лида (Tier): {tier or 'N/A'}")

    grp["lead_tier"] = tier
    pitch = generate_personalized_pitch(grp, niche=niche, city=city)
    
    print("\n📄 СГЕНЕРИРОВАННЫЙ ОФФЕР:")
    print("--- НАЧАЛО СООБЩЕНИЯ ---")
    print(pitch)
    print("--- КОНЕЦ СООБЩЕНИЯ ---\n")

    if send_live:
        confirmed = skip_confirm
        if not confirmed:
            confirm = input(f"⚠️ ВНИМАНИЕ: Вы действительно хотите отправить это сообщение в группу ID {group_id}? (да/нет): ")
            confirmed = confirm.strip().lower() in ("да", "yes", "y")
        
        if confirmed:
            res = agent.send_pitch_to_group(grp, niche=niche, city=city, dry_run=False)
            if res.get("success"):
                print(f"🎉 Сообщение успешно доставлено! Ответ API: {res.get('response')}")
            else:
                print(f"❌ Ошибка отправки: {res.get('error_msg')}")
        else:
            print("Отправка отменена пользователем.")
    else:
        print("💡 Для реальной отправки укажите флаг --live.")

def main():
    parser = argparse.ArgumentParser(
        description="LocalWeb — Автономный агент безопасного поиска клиентов и рассылки в группы ВК"
    )
    parser.add_argument("--dry-run", action="store_true", default=False, 
                        help="Режим безопасного предпросмотра (поиск и генерация без реальной отправки)")
    parser.add_argument("--live", action="store_true", default=False, 
                        help="Режим реальной отправки в сообщения групп")
    parser.add_argument("--niche", "-n", type=str, nargs="+", 
                        help="Поисковая ниша/ключевые слова (например: 'детейлинг' 'ремонт квартир')")
    parser.add_argument("--city", "-c", type=str, nargs="+", 
                        help="Город для поиска (например: 'Кемерово' 'Новосибирск')")
    parser.add_argument("--limit", "-l", type=int, default=5, 
                        help="Лимит сообщений на этот запуск (по умолчанию 5, макс 15)")
    parser.add_argument("--daily-limit", type=int, default=15,
                        help="Безопасный суточный максимум (по умолчанию 15)")
    parser.add_argument("--stats", action="store_true", 
                        help="Показать текущую статистику базы данных и лимитов")
    parser.add_argument("--test-group", type=int, 
                        help="Протестировать генерацию и отправку на одной конкретной группе по ее ID")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Пропустить запрос подтверждения в live-режиме")

    args = parser.parse_args()

    print_banner()

    if not VK_USER_TOKEN:
        print("❌ ОШИБКА: Не задан VK_USER_TOKEN в файле .env!")
        sys.exit(1)

    db = OutreachDatabase()

    if args.stats:
        print_safety_rules()
        display_stats(db, daily_limit=args.daily_limit)
        return

    agent = VkOutreachAgent(
        token=VK_USER_TOKEN,
        db=db,
        daily_limit=args.daily_limit,
        min_delay=75,
        max_delay=140
    )

    if args.test_group:
        niche = args.niche[0] if args.niche else "детейлинга и автосервиса"
        city = args.city[0] if args.city else "Кемерово"
        test_single_group(agent, args.test_group, niche=niche, city=city, send_live=args.live, skip_confirm=args.yes)
        return

    # Определяем режим работы (по умолчанию dry-run для максимальной безопасности)
    is_dry_run = not args.live

    print_safety_rules()
    display_stats(db, daily_limit=args.daily_limit)

    niches = args.niche if args.niche else DEFAULT_NICHES
    cities = args.city if args.city else DEFAULT_CITIES

    print(f"\n⚙️  ПАРАМЕТРЫ ЗАПУСКА:")
    print(f"  • Режим: {'🟡 DRY-RUN (БЕЗОПАСНАЯ ИМИТАЦИЯ, БЕЗ ОТПРАВКИ)' if is_dry_run else '🔴 LIVE (РЕАЛЬНАЯ ОТПРАВКА В ВК)'}")
    print(f"  • Ниши ({len(niches)}): {', '.join(niches[:4])}{'...' if len(niches) > 4 else ''}")
    print(f"  • Города ({len(cities)}): {', '.join(cities)}")
    print(f"  • Лимит текущей сессии: {args.limit} сообщений")
    print(f"  • Суточный максимум безопасности: {args.daily_limit} сообщений")

    if not is_dry_run and not args.yes:
        confirm = input("\n⚠️ ВНИМАНИЕ: Вы запускаете LIVE-рассылку в реальные сообщества ВК. Продолжить? (да/нет): ")
        if confirm.strip().lower() not in ("да", "yes", "y"):
            print("Операция отменена пользователем. Рекомендуем сначала выполнить запуск с --dry-run.")
            return

    print("\n🚀 ЗАПУСК АВТОНОМНОГО ЦИКЛА АУТРИЧА...\n")

    result = agent.run_campaign(
        queries=niches,
        cities=cities,
        run_limit=args.limit,
        dry_run=is_dry_run
    )

    print("\n================================================================================")
    print("📈 РЕЗУЛЬТАТЫ СЕССИИ:")
    print(f"  • Статус: {result.get('status')}")
    print(f"  • Всего обработано кандидатов: {result.get('processed', 0)}")
    print(f"  • Успешно {'сымитировано' if is_dry_run else 'отправлено'}: {result.get('sent', 0)}")
    print(f"  • Ошибок: {result.get('failed', 0)}")

    if is_dry_run and result.get("groups"):
        print("\n👀 ПРИМЕРЫ СГЕНЕРИРОВАННЫХ ПЕРСОНАЛИЗИРОВАННЫХ ОФФЕРОВ:")
        for idx, item in enumerate(result["groups"][:3], 1):
            print(f"\n--- [ПРИМЕР {idx}] Группа ID {item.get('group_id')} ({item.get('name')}) | Tier: {item.get('lead_tier')} ---")
            print(item.get("message"))
            print("--------------------------------------------------------------------------------")

    print("\n✅ Сессия успешно завершена.")
    if is_dry_run:
        print("💡 Для реальной отправки запустите: python run_outreach.py --live --limit 5")

if __name__ == "__main__":
    main()
