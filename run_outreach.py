#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LocalWeb VK Outreach — Консольный интерфейс 2-шагового автономного агента.

Двухшаговая стратегия («Касание без продажи»):
1. Шаг 1: Короткий вопрос под видом клиента/партнера без ссылок и коммерческих слов.
   (Безопасный объем: до 30-40 диалогов в день!).
2. Проверка ответов: отслеживание входящих сообщений (диалог становится взаимным).
3. Шаг 2: Продающий оффер с сайтом за 24ч и 7 500 ₽ во взаимный диалог.

Использование:
  python run_outreach.py --stats                       # Просмотр 2-шаговой воронки и ответов
  python run_outreach.py --dry-run                     # Безопасный предпросмотр Шага 1 и Шага 2
  python run_outreach.py --step1 --limit 25            # Рассылка естественных пингов (Шаг 1)
  python run_outreach.py --check-replies               # Проверить, кто ответил на пинги
  python run_outreach.py --step2                       # Отправить офферы тем, кто ответил
  python run_outreach.py --auto --limit 25             # Полный автопилот (ответы -> офферы -> пинги)
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
from vk_agent.spintax import (
    generate_step1_ping, 
    generate_step2_pitch, 
    clean_group_name
)

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

  2-ШАГОВЫЙ АГЕНТ ЛИДОГЕНЕРАЦИИ ВКОНТАКТЕ («КАСАНИЕ БЕЗ ПРОДАЖИ»)
  Шаг 1: Пинг под видом клиента • Проверка ответов • Шаг 2: Оффер во взаимный диалог
================================================================================
"""
    print(banner)

def print_strategy_info():
    print("""
💡 КАК РАБОТАЕТ ДВУХШАГОВАЯ СТРАТЕГИЯ («КАСАНИЕ БЕЗ ПРОДАЖИ»):
  • Фильтр активности: агент в первую очередь проверяет дату последнего поста на стене.
    Если группа заброшена (> 60 дней без публикаций) — она сразу отсекается.
  • Шаг 1 (Пинг): короткий естественный вопрос («Подскажите, есть ли сайт с прайсом или смотреть в группе?»).
    Без ссылок, без цен, без рекламы студии. Антиспам-фильтры ВК не видят спама, 
    а администраторы групп охотно отвечают (конверсия в ответ 40-70%!).
    👉 За счет этого можно безопасно отправлять ДО 35-40 СООБЩЕНИЙ В ДЕНЬ!
  • Проверка ответов: как только сообщество ответит — диалог становится ВЗАИМНЫМ.
  • Шаг 2 (Оффер): в открытый взаимный диалог отправляется готовое предложение (Сайт за 24ч, 7 500 ₽).
    Спам-фильтр ВК нейтрализован, риск бана стремится к нулю.
""")

def display_two_step_stats(db: OutreachDatabase, step1_limit: int = 35):
    stats = db.get_two_step_stats()
    pings_24h = stats["pings_last_24h"]
    quota_left = max(0, step1_limit - pings_24h)
    
    print("\n📊 --- ВОРОНКА 2-ШАГОВОГО АУТРИЧА ---")
    print(f"  • Всего целевых групп в базе:            {stats['total_leads']}")
    print(f"  • Шаг 1: Отправлено пингов всего:        {stats['total_pings']}")
    print(f"  • Шаг 1: Пингов за последние 24 часа:    {pings_24h} из {step1_limit} (безопасный лимит)")
    print(f"  • Доступная квота на новые пинги:        {quota_left} сообщений")
    print(f"  • Получено ответов (взаимных диалогов):  {stats['total_replied']} (Конверсия: {stats['conversion_rate']}%)")
    print(f"  • Ожидают отправки оффера (Шаг 2):       {stats['waiting_pitch']} лидов")
    print(f"  • Шаг 2: Отправлено коммерческих офферов: {stats['total_pitches']}")
    print(f"  • Пропущено нецелевых групп:             {stats['total_skipped']}")
    
    recent_replies = stats.get("recent_replies", [])
    if recent_replies:
        print("\n💬 ПОСЛЕДНИЕ ПОЛУЧЕННЫЕ ОТВЕТЫ ОТ СООБЩЕСТВ:")
        for idx, r in enumerate(recent_replies, 1):
            print(f"  [{idx}] Группа ID: {r['group_id']} | «{r['name']}»")
            print(f"      Ответ в {r['replied_at']}: \"{r['reply_text']}\"")
            print(f"      Статус: {'Ждет оффер (Шаг 2)' if r['status'] == 'replied' else 'Оффер отправлен'}\n")
    print("--------------------------------------------------------------------------------")

def test_single_group_preview(agent: VkOutreachAgent, group_id: int, niche: str = "услуг и бизнеса"):
    """Тестирует генерацию Шага 1 и Шага 2 для конкретной группы."""
    print(f"\n🧪 --- ТЕСТИРОВАНИЕ 2-ШАГОВОЙ СТРАТЕГИИ НА ГРУППЕ ID {group_id} ---")
    try:
        grp = agent.vk.get_group_by_id(group_id)
    except Exception as e:
        print(f"❌ Ошибка получения данных группы ID {group_id}: {e}")
        return

    name = grp.get("name", "")
    site = grp.get("site", "")
    members = grp.get("members_count", 0)
    
    # Проверка даты последнего поста на стене
    last_post_ts = agent.vk.get_last_wall_post_date(group_id)
    wall_info = "нет постов или стена закрыта"
    if last_post_ts:
        wall_days = (time.time() - last_post_ts) / 86400.0
        post_date_str = datetime.fromtimestamp(last_post_ts).strftime("%d.%m.%Y")
        wall_info = f"{post_date_str} ({wall_days:.1f} дн. назад)"

    print(f"  • Название: {name}")
    print(f"  • Обращение: {clean_group_name(name)}")
    print(f"  • Подписчиков: {members} | Сайт: '{site}'")
    print(f"  • Последний пост на стене: {wall_info}")

    is_qual, tier, reason = agent.evaluate_group(grp)
    print(f"  • Квалификация: {'✅ Подходит' if is_qual else f'❌ Отклонен ({reason})'}")
    grp["lead_tier"] = tier

    ping = generate_step1_ping(grp, niche=niche)
    pitch = generate_step2_pitch(grp, niche=niche)

    print("\n[ШАГ 1: ПИНГ ПОД ВИДОМ КЛИЕНТА (БЕЗ СПАМА И ССЫЛОК)]")
    print(ping)
    print("\n[ШАГ 2: ОФФЕР ПОСЛЕ ТОГО, КАК АДМИН ОТВЕТИТ]")
    print(pitch)
    print("--------------------------------------------------------------------------------")

def main():
    parser = argparse.ArgumentParser(
        description="LocalWeb — 2-шаговый агент безопасного поиска клиентов через ВКонтакте"
    )
    # Основные режимы
    parser.add_argument("--step1", action="store_true", help="Запуск рассылки коротких пингов Шага 1")
    parser.add_argument("--check-replies", action="store_true", help="Проверить входящие ответы от сообществ")
    parser.add_argument("--step2", action="store_true", help="Отправить офферы Шага 2 тем, кто ответил")
    parser.add_argument("--auto", action="store_true", help="Автопилот: проверить ответы -> отправить офферы -> отправить новые пинги")
    parser.add_argument("--daemon", action="store_true", help="Режим автоответчика: непрерывное дежурство и автоответ на новые сообщения до конца дня")
    parser.add_argument("--interval", type=int, default=180, help="Интервал проверки ответов в секундах (по умолчанию 180)")
    parser.add_argument("--until", type=int, default=23, help="Час окончания дежурства автоответчика (по умолчанию 23:59)")
    
    # Флаги выполнения
    parser.add_argument("--dry-run", action="store_true", default=False, help="Предпросмотр без реальной отправки")
    parser.add_argument("--live", action="store_true", default=False, help="Реальная отправка в ВК")
    parser.add_argument("--stats", action="store_true", help="Показать статистику воронки и лимитов")
    parser.add_argument("--test-group", type=int, help="Протестировать шаблоны на ID группы")

    # Параметры фильтрации
    parser.add_argument("--niche", "-n", type=str, nargs="+", help="Поисковые ниши (например: 'детейлинг' 'кухни на заказ')")
    parser.add_argument("--city", "-c", type=str, nargs="+", help="Города для поиска (например: 'Кемерово' 'Новосибирск')")
    parser.add_argument("--limit", "-l", type=int, default=25, help="Лимит пингов Шага 1 на текущий запуск (по умолчанию 25)")
    parser.add_argument("--daily-limit", type=int, default=35, help="Безопасный суточный максимум пингов Шага 1 (по умолчанию 35)")
    parser.add_argument("--max-inactive-days", type=int, default=60, help="Максимальная давность последней публикации на стене в днях (по умолчанию 60)")
    parser.add_argument("--yes", "-y", action="store_true", help="Пропустить подтверждение в live-режиме")

    args = parser.parse_args()

    print_banner()

    if not VK_USER_TOKEN:
        print("❌ ОШИБКА: Не задан VK_USER_TOKEN в файле .env!")
        sys.exit(1)

    db = OutreachDatabase()
    agent = VkOutreachAgent(
        token=VK_USER_TOKEN,
        db=db,
        step1_daily_limit=args.daily_limit,
        min_delay_step1=50,
        max_delay_step1=90,
        max_inactive_days=args.max_inactive_days
    )

    if args.stats:
        print_strategy_info()
        display_two_step_stats(db, step1_limit=args.daily_limit)
        return

    if args.test_group:
        niche = args.niche[0] if args.niche else "детейлинга"
        test_single_group_preview(agent, args.test_group, niche=niche)
        return

    # Режим дежурства автоответчика
    if args.daemon:
        is_dry_run = not args.live
        print(f"🎧 ЗАПУСК РЕЖИМА АВТООТВЕТЧИКА (ДЕЖУРСТВО ДО {args.until:02d}:59, интервал: {args.interval}с, Режим: {'DRY-RUN' if is_dry_run else 'LIVE'})...")
        while True:
            now = datetime.now()
            if now.hour > args.until or (now.hour == args.until and now.minute >= 59):
                print(f"\n🌙 Время {args.until:02d}:59 наступило. Дежурство автоответчика завершено.")
                break

            try:
                # 1. Проверяем новые ответы
                agent.check_incoming_replies()
                
                # 2. Если есть лиды, ожидающие оффер Шага 2 — отправляем
                ready_leads = db.get_leads_ready_for_pitch()
                if ready_leads:
                    print(f"\n🎯 [АВТООТВЕТЧИК] Найдено {len(ready_leads)} лидов, ожидающих оффер. Отправка...")
                    agent.run_step2_campaign(dry_run=is_dry_run)
            except Exception as e:
                print(f"⚠️ Ошибка в цикле автоответчика: {e}")

            time.sleep(args.interval)
        return

    # Режим проверки ответов
    if args.check_replies:
        print("📬 ПРОВЕРКА ВХОДЯЩИХ ОТВЕТОВ ОТ СООБЩЕСТВ...")
        replies = agent.check_incoming_replies()
        display_two_step_stats(db, step1_limit=args.daily_limit)
        if replies:
            print(f"🎉 Найдено {len(replies)} новых ответов! Запустите: python run_outreach.py --step2 --live")
        else:
            print("Новых ответов пока нет. Запустите проверку позже.")
        return

    # Режим Шага 2 (отправка офферов)
    if args.step2:
        is_dry_run = not args.live
        print(f"🎯 ОТПРАВКА ОФФЕРОВ ШАГА 2 ВО ВЗАИМНЫЕ ДИАЛОГИ (Режим: {'DRY-RUN' if is_dry_run else 'LIVE'})...")
        if not is_dry_run and not args.yes:
            conf = input("Подтвердите отправку офферов ответившим группам (да/нет): ")
            if conf.strip().lower() not in ("да", "yes", "y"):
                print("Отменено.")
                return
        res = agent.run_step2_campaign(dry_run=is_dry_run)
        print(f"Успешно обработано: {res.get('sent', 0)} офферов.")
        return

    # Автопилот или Шаг 1
    niches = args.niche if args.niche else DEFAULT_NICHES
    cities = args.city if args.city else DEFAULT_CITIES
    is_dry_run = not args.live

    print_strategy_info()
    display_two_step_stats(db, step1_limit=args.daily_limit)

    print(f"⚙️  ПАРАМЕТРЫ ЗАПУСКА:")
    print(f"  • Режим: {'🟡 DRY-RUN (БЕЗОПАСНЫЙ ПРЕДПРОСМОТР)' if is_dry_run else '🔴 LIVE (РЕАЛЬНАЯ ОТПРАВКА В ВК)'}")
    print(f"  • Действие: {'Автопилот (Ответы -> Шаг 2 -> Шаг 1)' if args.auto else 'Шаг 1 (Пинги под видом клиента)'}")
    print(f"  • Ниши ({len(niches)}): {', '.join(niches[:4])}{'...' if len(niches) > 4 else ''}")
    print(f"  • Города ({len(cities)}): {', '.join(cities)}")
    print(f"  • Лимит пингов на запуск: {args.limit} (Суточный лимит: {args.daily_limit})")

    if not is_dry_run and not args.yes:
        confirm = input("\n⚠️ ВНИМАНИЕ: Запустить реальную отправку сообщений в ВК? (да/нет): ")
        if confirm.strip().lower() not in ("да", "yes", "y"):
            print("Отменено.")
            return

    print("\n🚀 ВЫПОЛНЕНИЕ...\n")

    if args.auto:
        result = agent.run_auto_pipeline(
            queries=niches,
            cities=cities,
            step1_limit=args.limit,
            dry_run=is_dry_run
        )
        print("\n📈 РЕЗУЛЬТАТЫ АВТОПИЛОТА:")
        print(f"  • Новых ответов зафиксировано: {result.get('new_replies_count')}")
        print(f"  • Офферов Шага 2 отправлено:   {result.get('step2_pitches_sent')}")
        print(f"  • Пингов Шага 1 отправлено:    {result.get('step1_pings_sent')}")
    else:
        # По умолчанию или --step1
        result = agent.run_step1_campaign(
            queries=niches,
            cities=cities,
            run_limit=args.limit,
            dry_run=is_dry_run
        )
        print("\n📈 РЕЗУЛЬТАТЫ ШАГА 1:")
        print(f"  • Всего обработано: {result.get('processed')}")
        print(f"  • Пингов отправлено: {result.get('sent')}")

        if is_dry_run and result.get("groups"):
            print("\n👀 ПРИМЕРЫ СГЕНЕРИРОВАННЫХ ВОПРОСОВ (ШАГ 1):")
            for idx, item in enumerate(result["groups"][:3], 1):
                print(f"  [{idx}] Группа ID {item.get('group_id')} ({item.get('name')}):")
                print(f"      \"{item.get('message')}\"\n")

    print("\n✅ Выполнение завершено.")
    if is_dry_run:
        print("💡 Для реальной отправки пингов запустите: python run_outreach.py --step1 --live --limit 25")

if __name__ == "__main__":
    main()
