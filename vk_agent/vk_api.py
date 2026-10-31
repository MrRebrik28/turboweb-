import time
import requests
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VkApi")

class VkApiException(Exception):
    def __init__(self, error_code, error_msg, response=None):
        super().__init__(f"VK API Error [{error_code}]: {error_msg}")
        self.error_code = error_code
        self.error_msg = error_msg
        self.response = response

class VkApiClient:
    API_URL = "https://api.vk.com/method/"

    def __init__(self, token: str, api_version: str = "5.199"):
        if not token:
            raise ValueError("VK User Token is required.")
        self.token = token.strip()
        self.api_version = api_version
        self.session = requests.Session()
        self._user_info = None

    def call(self, method: str, params: dict = None, http_method: str = "POST") -> dict:
        """Вызов метода VK API с автоматической обработкой ошибок и задержкой."""
        if params is None:
            params = {}
        
        request_params = {
            "access_token": self.token,
            "v": self.api_version,
            **params
        }

        # Соблюдаем лимит запросов к VK API (до 3 запросов в секунду для пользователя)
        time.sleep(0.35)

        url = f"{self.API_URL}{method}"
        try:
            if http_method.upper() == "GET":
                resp = self.session.get(url, params=request_params, timeout=30)
            else:
                resp = self.session.post(url, data=request_params, timeout=30)
            
            data = resp.json()
        except Exception as e:
            logger.error(f"HTTP ошибка при вызове {method}: {e}")
            raise

        if "error" in data:
            error = data["error"]
            err_code = error.get("error_code", 0)
            err_msg = error.get("error_msg", "Unknown error")
            
            # Обработка лимита запросов (Error 6)
            if err_code == 6:
                logger.warning("Сработал лимит частоты запросов (Error 6). Ожидание 1.5 сек...")
                time.sleep(1.5)
                return self.call(method, params, http_method)
            
            logger.error(f"Ошибка VK API в {method}: {err_msg} (Код: {err_code})")
            raise VkApiException(err_code, err_msg, data)

        return data.get("response")

    def get_user_info(self) -> dict:
        """Проверяет валидность токена и возвращает данные текущего пользователя."""
        if self._user_info:
            return self._user_info
        res = self.call("users.get", {"fields": "screen_name,photo_200"})
        if res and len(res) > 0:
            self._user_info = res[0]
            logger.info(f"Успешная авторизация пользователя: {self._user_info.get('first_name')} {self._user_info.get('last_name')} (ID: {self._user_info.get('id')})")
            return self._user_info
        raise ValueError("Не удалось получить информацию о пользователе VK.")

    def create_group(self, title: str, description: str = "", category: int = 1, subtype: int = 1) -> int:
        """Создает публичную страницу (паблик). Возвращает ID созданной группы."""
        logger.info(f"Создание публичной страницы: '{title}'...")
        params = {
            "title": title,
            "description": description,
            "type": "public",
            "public_category": category,
            "subtype": subtype
        }
        res = self.call("groups.create", params)
        group_id = res.get("id")
        logger.info(f"Паблик успешно создан! ID: {group_id}")
        return group_id

    def edit_group(self, group_id: int, title: str = None, description: str = None, 
                   website: str = None, phone: str = None, email: str = None) -> bool:
        """Редактирует информацию и контакты паблика."""
        logger.info(f"Настройка параметров паблика ID {group_id}...")
        params = {"group_id": group_id}
        if title:
            params["title"] = title
        if description:
            params["description"] = description
        if website:
            params["website"] = website
        if phone:
            params["phone"] = phone
        if email:
            params["email"] = email
        
        res = self.call("groups.edit", params)
        logger.info(f"Параметры паблика успешно обновлены: {res}")
        return res == 1 or res == {"success": 1}

    def upload_group_cover(self, group_id: int, image_path: str) -> bool:
        """Загружает и устанавливает главную обложку паблика (баннер 1920x768)."""
        logger.info(f"Загрузка обложки сообщества из {image_path}...")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл обложки не найден: {image_path}")

        # 1. Получаем сервер для загрузки обложки
        upload_server = self.call("photos.getOwnerCoverPhotoUploadServer", {
            "group_id": group_id,
            "crop_x": 0,
            "crop_y": 0,
            "crop_x2": 1920,
            "crop_y2": 768
        })
        upload_url = upload_server.get("upload_url")

        # 2. Отправляем изображение на сервер
        with open(image_path, "rb") as f:
            upload_resp = requests.post(upload_url, files={"photo": f}, timeout=60).json()

        # 3. Сохраняем обложку
        save_res = self.call("photos.saveOwnerCoverPhoto", {
            "hash": upload_resp.get("hash"),
            "photo": upload_resp.get("photo")
        })
        logger.info(f"Обложка сообщества успешно сохранена!")
        return True

    def upload_group_avatar(self, group_id: int, image_path: str) -> bool:
        """Загружает аватар сообщества."""
        logger.info(f"Загрузка аватара паблика из {image_path}...")
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл аватара не найден: {image_path}")

        upload_server = self.call("photos.getOwnerPhotoUploadServer", {
            "owner_id": -group_id
        })
        upload_url = upload_server.get("upload_url")

        with open(image_path, "rb") as f:
            upload_resp = requests.post(upload_url, files={"photo": f}, timeout=60).json()

        save_res = self.call("photos.saveOwnerPhoto", {
            "server": upload_resp.get("server"),
            "photo": upload_resp.get("photo"),
            "hash": upload_resp.get("hash")
        })
        logger.info(f"Аватар сообщества успешно установлен!")
        return True

    def upload_wall_photo(self, image_path: str, group_id: int = None) -> str:
        """
        Загружает изображение для прикрепления к записи на стене.
        Если group_id передан, фото прикрепляется к стене сообщества,
        иначе — к стене личного профиля.
        Возвращает идентификатор вложения вида 'photo123_456'.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл для стены не найден: {image_path}")

        params = {}
        if group_id:
            params["group_id"] = group_id

        # 1. Получаем URL сервера загрузки фото на стену
        upload_server = self.call("photos.getWallUploadServer", params)
        upload_url = upload_server.get("upload_url")

        # 2. Загружаем файл
        with open(image_path, "rb") as f:
            upload_resp = requests.post(upload_url, files={"photo": f}, timeout=60).json()

        # 3. Сохраняем фото
        save_params = {
            "photo": upload_resp.get("photo"),
            "server": upload_resp.get("server"),
            "hash": upload_resp.get("hash")
        }
        if group_id:
            save_params["group_id"] = group_id

        saved = self.call("photos.saveWallPhoto", save_params)
        if saved and len(saved) > 0:
            photo_obj = saved[0]
            attachment_id = f"photo{photo_obj['owner_id']}_{photo_obj['id']}"
            return attachment_id

        raise ValueError("Ошибка сохранения фотографии на стену.")

    def schedule_post(self, owner_id: int, message: str, publish_date: int, 
                      attachments: str = None, from_group: int = 1) -> int:
        """
        Создает отложенную публикацию (в отложку) на личной странице или в паблике.
        owner_id: ID пользователя (>0) или -group_id (<0 для сообществ).
        publish_date: Unixtime в секундах (будущее время).
        from_group: 1 если от имени группы, 0 если от пользователя (или предложка).
        Возвращает ID созданного поста.
        """
        params = {
            "owner_id": owner_id,
            "message": message,
            "publish_date": publish_date
        }
        if owner_id < 0:
            params["from_group"] = from_group
        if attachments:
            params["attachments"] = attachments

        res = self.call("wall.post", params)
        post_id = res.get("post_id")
        return post_id
