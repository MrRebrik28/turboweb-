#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LocalWeb VK Automation Agent — Главный запускной файл.
Заполняет отложку на 14 дней в личном профиле, создает паблик,
настраивает оформление (аватар, обложку) и заполняет отложку/предложку сообщества.
"""

import os
import sys
import argparse
from datetime import datetime

# Настройка безопасной кодировки для Windows консоли
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def load_dotenv_simple(filepath: str = ".env"):
    """Простая загрузка переменных из .env без внешних зависимостей."""
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k and k not in os.environ:
                os.environ[k] = v

load_dotenv_simple()

from vk_agent.agent import VkLocalWebAgent
from vk_agent.asset_generator import generate_all_assets
from vk_agent.content_plan import POSTS
from vk_agent.config import VK_USER_TOKEN, GROUP_ID, ASSETS_DIR

def print_banner():
    banner = """
======================================================================
  _                     _  __        __   _     
 | |    ___   ___ __ _| | \\ \\      / /__| |__  
 | |   / _ \\ / __/ _` | |  \\ \\ /\\ / / _ \\ '_ \\ 
 | |__| (_) | (_| (_| | |   \\ V  V /  __/ |_) |
 |_____\\___/ \\___\\__,_|_|    \\_/\\_/ \\___|_.__/  
                                                
 Автономный агент автопостинга и брендинга ВКонтакте
 14 дней отложки • Создание паблика • Баннеры и аватарки
======================================================================
"""
    print(banner)

def run_dry_run(agent: VkLocalWebAgent, start_date: datetime):
    """Режим демонстрации без совершения изменений в VK."""
    print("\n🔍 --- РЕЖИМ ПРОВЕРКИ (DRY-RUN) ---")
    print(f"Каталог графических материалов: {ASSETS_DIR}")
    
    avatar_exists = os.path.exists(os.path.join(ASSETS_DIR, "avatar.png"))
    cover_exists = os.path.exists(os.path.join(ASSETS_DIR, "public_cover.png"))
    print(f"• Аватар сообщества (800x800): {'[OK] Найден' if avatar_exists else '[MISSING] Отсутствует'}")
    print(f"• Обложка паблика (1920x768): {'[OK] Найдена' if cover_exists else '[MISSING] Отсутствует'}")

    timestamps = agent.calculate_schedule_timestamps(start_date)
    print(f"\n📅 Расписание 14 публикаций (по 1 посту в день):")
    for i, p in enumerate(POSTS):
        ts = timestamps[i]
        dt_str = datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
        img_name = p.get('image_file', f"post_{p['day']:02d}.png")
        img_path = os.path.join(ASSETS_DIR, img_name)
        status = "[OK]" if os.path.exists(img_path) else "[MISSING]"
        print(f"  День {p['day']:02d} | {dt_str} | {status} {img_name:<12} | {p['title'][:48]}...")

    if agent.token:
        try:
            print("\n🔑 Проверка токена VK API...")
            agent.initialize()
            print(f"Авторизация успешна! Пользователь ID: {agent.user_info.get('id')} ({agent.user_info.get('first_name')} {agent.user_info.get('last_name')})")
        except Exception as e:
            print(f"⚠️ Ошибка проверки токена: {e}")
    else:
        print("\n⚠️ Токен VK_USER_TOKEN не указан. Задайте его в .env или параметром --token.")
    print("--- КОНЕЦ ПРОВЕРКИ ---\n")

def main():
    parser = argparse.ArgumentParser(
        description="LocalWeb VK Automation Agent — наполнение профиля и паблика на 14 дней."
    )
    parser.add_argument("--token", help="VK User Access Token с правами wall,groups,photos,offline")
    parser.add_argument("--group-id", type=int, help="ID существующего паблика (если не указан, создаст новый)")
    parser.add_argument("--generate-assets", action="store_true", help="Сгенерировать только графические материалы (аватар, обложку и 14 карточек)")
    parser.add_argument("--dry-run", action="store_true", help="Проверить расписание и ассеты без публикации в VK")
    parser.add_argument("--profile-only", action="store_true", help="Заполнить отложку ТОЛЬКО в личном профиле")
    parser.add_argument("--group-only", action="store_true", help="Создать/настроить паблик и заполнить отложку ТОЛЬКО в паблике")
    parser.add_argument("--as-suggested", action="store_true", help="В паблике отправлять посты в предложку (от пользователя) вместо отложки админа")
    parser.add_argument("--start-date", help="Дата начала отложки в формате ГГГГ-ММ-ДД (по умолчанию: завтра)")

    args = parser.parse_args()
    print_banner()

    # Дата старта
    start_date = None
    if args.start_date:
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(hour=11, minute=0)
        except ValueError:
            print(f"❌ Ошибка: неверный формат даты '{args.start_date}'. Используйте ГГГГ-ММ-ДД, например 2026-11-01.")
            sys.exit(1)

    # Генерация ассетов
    if args.generate_assets:
        generate_all_assets()
        print("\n[SUCCESS] Все графические материалы готовы к использованию!")
        return

    token = args.token or os.getenv("VK_USER_TOKEN")
    group_id = args.group_id or os.getenv("VK_GROUP_ID")
    if group_id:
        group_id = int(group_id)

    agent = VkLocalWebAgent(token=token, group_id=group_id, as_suggested=args.as_suggested)

    if args.dry_run:
        run_dry_run(agent, start_date)
        return

    if not token:
        print("❌ ОШИБКА: Не указан токен доступа ВКонтакте (VK_USER_TOKEN)!")
        print("\nДля работы агента требуется токен пользователя с правами: wall,groups,photos,offline.")
        print("1. Скопируйте файл .env.example в .env:")
        print("   copy .env.example .env")
        print("2. Вставьте ваш токен в переменную VK_USER_TOKEN")
        print("3. Или передайте токен в командной строке:")
        print("   python run_agent.py --token YOUR_TOKEN\n")
        print("Подробная инструкция в файле README.md")
        sys.exit(1)

    schedule_profile = not args.group_only
    schedule_group = not args.profile_only

    try:
        result = agent.run(
            schedule_profile=schedule_profile,
            schedule_group=schedule_group,
            start_date=start_date
        )

        print("\n" + "="*60)
        print("🎉 ВСЕ ЗАДАЧИ АГЕНТА УСПЕШНО ВЫПОЛНЕНЫ!")
        print("="*60)
        print(f"👤 Пользователь: ID {result['user_id']} (https://vk.com/id{result['user_id']})")
        if schedule_profile:
            print(f"📅 Запланировано постов в профиле: {result['profile_posts_count']} шт.")
        if schedule_group:
            print(f"📢 Сообщество: ID {result['group_id']} (https://vk.com/public{result['group_id']})")
            print(f"📅 Запланировано постов в паблике: {result['group_posts_count']} шт.")
            print(f"🎨 Оформление (баннер 1920x768 и аватар): установлено")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Ошибка при выполнении агента: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
