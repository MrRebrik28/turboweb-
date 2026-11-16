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

    def get_selected_posts(self, from_day: int = 1, to_day: int = 999) -> list:
        """Возвращает посты контент-плана в заданном диапазоне дней."""
        return [p for p in POSTS if from_day <= p["day"] <= to_day]

    def prepare_assets(self, from_day: int = 1, to_day: int = 999, force_regenerate: bool = False):
        """Проверяет наличие ассетов, при необходимости генерирует недостающие."""
        avatar_path = os.path.join(ASSETS_DIR, "avatar.png")
        cover_path = os.path.join(ASSETS_DIR, "public_cover.png")
        selected = self.get_selected_posts(from_day, to_day)

        all_posts_exist = all(
            os.path.exists(os.path.join(ASSETS_DIR, p.get("image_file", f"post_{p['day']:02d}.png")))
            for p in selected
        )

        if force_regenerate or not (os.path.exists(avatar_path) and os.path.exists(cover_path) and all_posts_exist):
            logger.info(f"Генерация графических материалов (дни {from_day}–{to_day})...")
            generate_all_assets(from_day=from_day, to_day=to_day, force=force_regenerate)
        else:
            logger.info("Все необходимые графические ассеты уже сгенерированы и готовы к загрузке.")

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

    def calculate_schedule_timestamps(self, start_date: datetime = None, count: int = None) -> list:
        """
        Вычисляет Unixtime метки времени для count постов.
        По умолчанию начинает с завтрашнего дня в указанное время (POST_HOUR:POST_MINUTE).
        """
        if start_date is None:
            now = datetime.now()
            start_date = (now + timedelta(days=1)).replace(
                hour=POST_HOUR, minute=POST_MINUTE, second=0, microsecond=0
            )

        total = count if count is not None else len(POSTS)
        return [int((start_date + timedelta(days=i)).timestamp()) for i in range(total)]

    def _schedule_posts_for_target(
        self,
        owner_id: int,
        posts: list,
        timestamps: list,
        label: str,
        group_id: int = None,
        from_group: int = 1,
    ) -> list:
        """Планирует заданный список постов в отложку/предложку указанной стены."""
        scheduled_posts = []
        id_key = "group_id" if group_id else "owner_id"
        id_val = group_id if group_id else owner_id

        for i, post in enumerate(posts):
            day = post["day"]
            ts = timestamps[i]
            dt_str = datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M")
            img_file = post.get("image_file", f"post_{day:02d}.png")
            img_path = os.path.join(ASSETS_DIR, img_file)

            logger.info(f"{label} • День {day:02d} ({dt_str}): загрузка фото и создание отложенного поста...")

            attachment = None
            if os.path.exists(img_path):
                try:
                    attachment = self.vk.upload_wall_photo(img_path, group_id=group_id)
                except Exception as e:
                    logger.warning(f"Не удалось загрузить фото для дня {day}: {e}")

            post_id = self.vk.schedule_post(
                owner_id=owner_id,
                message=post["text"],
                publish_date=ts,
                attachments=attachment,
                from_group=from_group,
            )
            scheduled_posts.append({
                "day": day,
                "post_id": post_id,
                "date": dt_str,
                id_key: id_val,
            })
            logger.info(f"{label} • День {day:02d}: Успешно запланирован пост ID {post_id} на {dt_str}")

        return scheduled_posts

    def schedule_profile_posts(self, timestamps: list, posts: list = None) -> list:
        """Планирует посты в отложку личного профиля."""
        target_posts = posts if posts is not None else POSTS
        user_id = self.user_info.get("id")
        logger.info(f"Заполнение отложки ({len(target_posts)} постов) в личном профиле (ID: {user_id})...")
        return self._schedule_posts_for_target(
            owner_id=user_id,
            posts=target_posts,
            timestamps=timestamps,
            label="Профиль",
        )

    def schedule_community_posts(self, timestamps: list, posts: list = None) -> list:
        """
        Планирует посты в отложку (или предложку) паблика.
        Если as_suggested=False: от имени группы (from_group=1).
        Если as_suggested=True: в предложенные новости (from_group=0).
        """
        if not self.group_id:
            raise ValueError("ID сообщества не определен.")

        target_posts = posts if posts is not None else POSTS
        queue_type = "предложку" if self.as_suggested else "отложку"
        from_group = 0 if self.as_suggested else 1

        logger.info(f"Заполнение {len(target_posts)} постов в {queue_type} паблика (ID: {self.group_id})...")
        return self._schedule_posts_for_target(
            owner_id=-self.group_id,
            posts=target_posts,
            timestamps=timestamps,
            label="Паблик",
            group_id=self.group_id,
            from_group=from_group,
        )

    def run(
        self,
        schedule_profile: bool = True,
        schedule_group: bool = True,
        start_date: datetime = None,
        from_day: int = 1,
        to_day: int = 999,
        skip_branding: bool = False,
    ) -> dict:
        """Запуск цикла работы агента для выбранного диапазона дней."""
        logger.info(f"=== Запуск автономного агента LocalWeb VK (дни {from_day}–{to_day}) ===")

        selected_posts = self.get_selected_posts(from_day, to_day)
        if not selected_posts:
            raise ValueError(f"Нет постов в диапазоне дней {from_day}–{to_day}.")

        # 1. Авторизация
        self.initialize()

        # 2. Подготовка оформления и баннеров
        self.prepare_assets(from_day=from_day, to_day=to_day)

        # 3. Настройка сообщества (если группа ещё не создана или не пропущено)
        if schedule_group and (not self.group_id or not skip_branding):
            self.setup_community()

        # 4. Расчет расписания
        timestamps = self.calculate_schedule_timestamps(start_date, count=len(selected_posts))

        # 5. Планирование в личный профиль
        profile_results = []
        if schedule_profile:
            profile_results = self.schedule_profile_posts(timestamps, posts=selected_posts)

        # 6. Планирование в сообщество
        group_results = []
        if schedule_group:
            group_results = self.schedule_community_posts(timestamps, posts=selected_posts)

        logger.info("=== Работа агента успешно завершена! ===")
        return {
            "user_id": self.user_info.get("id"),
            "group_id": self.group_id,
            "profile_posts_count": len(profile_results),
            "group_posts_count": len(group_results),
            "profile_posts": profile_results,
            "group_posts": group_results
        }
