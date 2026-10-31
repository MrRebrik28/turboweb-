import os
import sys
import time
from datetime import datetime, timedelta
import logging

from .config import (
    VK_USER_TOKEN,
    VK_API_VERSION,
    GROUP_ID,
    PUBLIC_TITLE,
    PUBLIC_DESCRIPTION,
    PUBLIC_WEBSITE,
    PUBLIC_CATEGORY,
    PUBLIC_SUBTYPE,
    POST_HOUR,
    POST_MINUTE,
    ASSETS_DIR
)
from .vk_api import VkApiClient, VkApiException
from .content_plan import POSTS
from .asset_generator import generate_all_assets

# Безопасный вывод UTF-8 в консоли Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VkAgent")

class VkLocalWebAgent:
    """
    Автономный агент для автоматизации ВКонтакте:
    1. Проверка прав и авторизация
    2. Генерация брендового графического оформления в стиле LocalWeb
    3. Создание или привязка паблика, заполнение всех данных и контактов
    4. Загрузка обложки и аватара сообщества
    5. Заполнение отложки на 14 дней в личном профиле ВК
    6. Заполнение отложки (или предложки) на 14 дней в сообществе ВК теми же постами
    """

    def __init__(self, token: str = None, group_id: int = None, as_suggested: bool = False):
        self.token = token or VK_USER_TOKEN
        self.group_id = int(group_id) if group_id else (int(GROUP_ID) if GROUP_ID else None)
        self.as_suggested = as_suggested
        self.vk = None
        self.user_info = None

    def initialize(self):
        """Инициализирует и проверяет подключение к VK API."""
        if not self.token:
            raise ValueError(
                "Токен ВКонтакте не найден! Укажите VK_USER_TOKEN в файле .env или параметре запуска."
            )
        self.vk = VkApiClient(self.token, VK_API_VERSION)
        self.user_info = self.vk.get_user_info()
        logger.info(
            f"Авторизован аккаунт: {self.user_info.get('first_name')} {self.user_info.get('last_name')} "
            f"(https://vk.com/id{self.user_info.get('id')})"
        )

    def prepare_assets(self, force_regenerate: bool = False):
        """Проверяет наличие ассетов, при необходимости генерирует."""
        avatar_path = os.path.join(ASSETS_DIR, "avatar.png")
        cover_path = os.path.join(ASSETS_DIR, "public_cover.png")
        
        all_posts_exist = all(
            os.path.exists(os.path.join(ASSETS_DIR, p.get("image_file", f"post_{p['day']:02d}.png")))
            for p in POSTS
        )

        if force_regenerate or not (os.path.exists(avatar_path) and os.path.exists(cover_path) and all_posts_exist):
            logger.info("Генерация полного комплекта графических материалов...")
            generate_all_assets()
        else:
            logger.info("Все графические ассеты уже сгенерированы и готовы к загрузке.")

    def setup_community(self) -> int:
        """Создает и настраивает сообщество, загружает аватар и обложку."""
        if not self.group_id:
            logger.info("Создание новой официальной публичной страницы...")
            self.group_id = self.vk.create_group(
                title=PUBLIC_TITLE,
                description=PUBLIC_DESCRIPTION,
                category=PUBLIC_CATEGORY,
                subtype=PUBLIC_SUBTYPE
            )
            time.sleep(1)
        else:
            logger.info(f"Использование существующего сообщества ID: {self.group_id}")

        # Обновляем описание и сайт сообщества
        try:
            self.vk.edit_group(
                group_id=self.group_id,
                title=PUBLIC_TITLE,
                description=PUBLIC_DESCRIPTION,
                website=PUBLIC_WEBSITE
            )
        except Exception as e:
            logger.warning(f"Не удалось обновить настройки паблика: {e}")

        # Загрузка обложки (баннера 1920x768)
        cover_path = os.path.join(ASSETS_DIR, "public_cover.png")
        if os.path.exists(cover_path):
            try:
                self.vk.upload_group_cover(self.group_id, cover_path)
                logger.info("Баннер-обложка паблика успешно загружен и установлен.")
            except Exception as e:
                logger.error(f"Ошибка загрузки обложки: {e}")

        # Загрузка аватара
        avatar_path = os.path.join(ASSETS_DIR, "avatar.png")
        if os.path.exists(avatar_path):
            try:
                self.vk.upload_group_avatar(self.group_id, avatar_path)
                logger.info("Аватар паблика успешно загружен и установлен.")
            except Exception as e:
                logger.error(f"Ошибка загрузки аватара: {e}")

        return self.group_id

    def calculate_schedule_timestamps(self, start_date: datetime = None) -> list:
        """
        Вычисляет Unixtime метки времени для 14 постов.
        По умолчанию начинает с завтрашнего дня в указанное время (POST_HOUR:POST_MINUTE).
        """
        if start_date is None:
            now = datetime.now()
            # Завтрашний день в POST_HOUR:POST_MINUTE
            start_date = (now + timedelta(days=1)).replace(
                hour=POST_HOUR, minute=POST_MINUTE, second=0, microsecond=0
            )

        timestamps = []
        for i in range(len(POSTS)):
            post_time = start_date + timedelta(days=i)
            timestamps.append(int(post_time.timestamp()))
        return timestamps

    def schedule_profile_posts(self, timestamps: list) -> list:
        """Планирует 14 постов в отложку личного профиля."""
        user_id = self.user_info.get("id")
        logger.info(f"Заполнение отложки на 14 дней в личном профиле (ID: {user_id})...")
        scheduled_posts = []

        for i, post in enumerate(POSTS):
            day = post["day"]
            ts = timestamps[i]
            dt_str = datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
            img_file = post.get("image_file", f"post_{day:02d}.png")
            img_path = os.path.join(ASSETS_DIR, img_file)

            logger.info(f"Профиль • День {day:02d} ({dt_str}): загрузка фото и создание отложенного поста...")
            
            # Загружаем фото на стену пользователя
            attachment = None
            if os.path.exists(img_path):
                try:
                    attachment = self.vk.upload_wall_photo(img_path)
                except Exception as e:
                    logger.warning(f"Не удалось загрузить фото для дня {day}: {e}")

            # Публикуем в отложку
            post_id = self.vk.schedule_post(
                owner_id=user_id,
                message=post["text"],
                publish_date=ts,
                attachments=attachment
            )
            scheduled_posts.append({
                "day": day,
                "post_id": post_id,
                "date": dt_str,
                "owner_id": user_id
            })
            logger.info(f"Профиль • День {day:02d}: Успешно запланирован пост ID {post_id} на {dt_str}")

        return scheduled_posts

    def schedule_community_posts(self, timestamps: list) -> list:
        """
        Планирует 14 постов в отложку (или предложку) паблика.
        Если as_suggested=False (по умолчанию): от имени группы (from_group=1) в очередь публикации.
        Если as_suggested=True: в предложенные новости (from_group=0).
        """
        if not self.group_id:
            raise ValueError("ID сообщества не определен.")

        queue_type = "предложку" if self.as_suggested else "отложку"
        from_group = 0 if self.as_suggested else 1

        logger.info(f"Заполнение 14 постов в {queue_type} паблика (ID: {self.group_id})...")
        scheduled_posts = []

        for i, post in enumerate(POSTS):
            day = post["day"]
            ts = timestamps[i]
            dt_str = datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
            img_file = post.get("image_file", f"post_{day:02d}.png")
            img_path = os.path.join(ASSETS_DIR, img_file)

            logger.info(f"Паблик • День {day:02d} ({dt_str}): загрузка фото и создание поста...")

            # Загружаем фото для стены сообщества
            attachment = None
            if os.path.exists(img_path):
                try:
                    attachment = self.vk.upload_wall_photo(img_path, group_id=self.group_id)
                except Exception as e:
                    logger.warning(f"Не удалось загрузить фото для дня {day}: {e}")

            # Публикуем в сообщество
            post_id = self.vk.schedule_post(
                owner_id=-self.group_id,
                message=post["text"],
                publish_date=ts,
                attachments=attachment,
                from_group=from_group
            )
            scheduled_posts.append({
                "day": day,
                "post_id": post_id,
                "date": dt_str,
                "group_id": self.group_id
            })
            logger.info(f"Паблик • День {day:02d}: Успешно запланирован пост ID {post_id} на {dt_str}")

        return scheduled_posts

    def run(self, schedule_profile: bool = True, schedule_group: bool = True, start_date: datetime = None) -> dict:
        """Запуск полного цикла работы агента."""
        logger.info("=== Запуск автономного агента LocalWeb VK ===")
        
        # 1. Авторизация
        self.initialize()

        # 2. Подготовка оформления и баннеров
        self.prepare_assets()

        # 3. Настройка сообщества
        if schedule_group:
            self.setup_community()

        # 4. Расчет расписания на 14 дней
        timestamps = self.calculate_schedule_timestamps(start_date)

        # 5. Планирование в личный профиль
        profile_results = []
        if schedule_profile:
            profile_results = self.schedule_profile_posts(timestamps)

        # 6. Планирование в сообщество
        group_results = []
        if schedule_group:
            group_results = self.schedule_community_posts(timestamps)

        logger.info("=== Работа агента успешно завершена! ===")
        return {
            "user_id": self.user_info.get("id"),
            "group_id": self.group_id,
            "profile_posts_count": len(profile_results),
            "group_posts_count": len(group_results),
            "profile_posts": profile_results,
            "group_posts": group_results
        }
