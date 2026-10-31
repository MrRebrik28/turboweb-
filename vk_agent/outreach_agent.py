# -*- coding: utf-8 -*-
"""
LocalWeb VK Outreach — Автономный агент поиска клиентов и безопасного аутрича.
Строго соблюдает лимиты ВКонтакте, фильтрует нецелевые группы, генерирует
уникальный спинтакс-текст и ведет историю отправок в SQLite.
"""

import time
import random
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from vk_agent.vk_api import VkApiClient, VkApiException
from vk_agent.database import OutreachDatabase
from vk_agent.spintax import generate_personalized_pitch, clean_group_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VkOutreachAgent")

# Черный список стоп-слов для фильтрации некоммерческих/мусорных сообществ
STOP_WORDS = [
    "новости", "подслушано", "барахолка", "отдам даром", "объявления", 
    "работа", "мемы", "приколы", "18+", "чат", "порно", "ставки", 
    "казино", "секонд", "знакомства", "скидки", "бесплатно", "купоны",
    "аренда жилья", "доска объявлений", "происшествия", "дпс", "дтп"
]

# Список доменов бесплатных конструкторов и визиток
BUILDER_DOMAINS = [
    "taplink.cc", "vk.link", "tilda.ws", "wixsite.com", 
    "linktr.ee", "mssg.me", "setup.ru", "site123.me"
]

class VkOutreachAgent:
    def __init__(self, token: str, db: OutreachDatabase = None, 
                 daily_limit: int = 15, min_delay: int = 75, max_delay: int = 140):
        self.vk = VkApiClient(token)
        self.db = db or OutreachDatabase()
        self.daily_limit = daily_limit
        self.min_delay = min_delay
        self.max_delay = max_delay

    def evaluate_group(self, group: Dict[str, Any]) -> (bool, str, str):
        """
        Оценивает сообщество на соответствие критериям целевого клиента.
        Возвращает кортеж: (is_qualified, lead_tier, reject_reason)
        """
        group_id = group.get("id")
        name = group.get("name", "").strip()
        desc = (group.get("description") or "").lower()
        name_lower = name.lower()

        # 1. Проверка сообщений сообщества
        can_message = group.get("can_message", 0)
        if can_message != 1:
            return False, "", "messages_disabled"

        # 2. Проверка закрытости сообщества
        is_closed = group.get("is_closed", 0)
        if is_closed != 0:
            return False, "", "closed_group"

        # 3. Проверка блокировки / удаления сообщества
        if group.get("deactivated"):
            return False, "", "deactivated"

        # 4. Проверка количества подписчиков (sweet spot: 70 - 25 000)
        members_count = group.get("members_count", 0)
        if members_count < 70:
            return False, "", f"too_small ({members_count} members)"
        if members_count > 25000:
            return False, "", f"too_large_federal ({members_count} members)"

        # 5. Проверка стоп-слов
        for sw in STOP_WORDS:
            if sw in name_lower:
                return False, "", f"stop_word_in_name ('{sw}')"
            if sw in desc[:200]:
                return False, "", f"stop_word_in_desc ('{sw}')"

        # 6. Определение категории сайта (Lead Tier)
        site = (group.get("site") or "").strip().lower()
        if not site or site.startswith("https://vk.com") or site.startswith("http://vk.com"):
            lead_tier = "no_site"  # Наивысший приоритет
        elif any(b in site for b in BUILDER_DOMAINS):
            lead_tier = "builder_site"  # Высокий приоритет (визитка/конструктор)
        else:
            lead_tier = "custom_site"  # Средний приоритет (есть сайт)

        return True, lead_tier, ""

    def search_candidates(self, query: str, city: str = "", count: int = 40) -> List[Dict[str, Any]]:
        """
        Ищет целевые группы по ключевым словам и городу, фильтрует нецелевые и дубли.
        """
        search_query = f"{query} {city}".strip()
        logger.info(f"🔎 Поиск сообществ по запросу: '{search_query}' (макс. {count})...")

        raw_results = self.vk.search_groups(
            query=search_query,
            count=count,
            fields="can_message,site,description,members_count,city,contacts,status"
        )

        items = raw_results.get("items", []) if isinstance(raw_results, dict) else []
        logger.info(f"Найдено групп в VK: {len(items)}")

        qualified_candidates = []

        for group in items:
            group_id = group.get("id")
            name = group.get("name", "")

            # Проверяем, не было ли сообщество обработано ранее
            if self.db.is_lead_processed(group_id):
                continue

            is_qualified, lead_tier, reject_reason = self.evaluate_group(group)

            if not is_qualified:
                # Фиксируем в БД причину пропуска, чтобы не проверять заново
                self.db.mark_lead_skipped(group_id, reject_reason, name=name, screen_name=group.get("screen_name", ""))
                continue

            # Сохраняем в БД как найденный перспективный лид
            city_title = ""
            g_city = group.get("city")
            if isinstance(g_city, dict):
                city_title = g_city.get("title", "")
            elif isinstance(g_city, str):
                city_title = g_city
            else:
                city_title = city

            self.db.save_found_lead(
                group_id=group_id,
                name=name,
                screen_name=group.get("screen_name", ""),
                city=city_title,
                niche=query,
                members_count=group.get("members_count", 0),
                site=group.get("site", ""),
                lead_tier=lead_tier
            )

            group["lead_tier"] = lead_tier
            group["detected_niche"] = query
            group["detected_city"] = city_title
            qualified_candidates.append(group)

        # Сортируем: сначала без сайта (Tier 1), затем конструкторы, затем остальные
        tier_weights = {"no_site": 0, "builder_site": 1, "custom_site": 2}
        qualified_candidates.sort(key=lambda g: tier_weights.get(g.get("lead_tier", "custom_site"), 3))

        logger.info(f"Целевых квалифицированных лидов после фильтрации: {len(qualified_candidates)}")
        return qualified_candidates

    def send_pitch_to_group(self, group: Dict[str, Any], niche: str, city: str = "", dry_run: bool = False) -> Dict[str, Any]:
        """
        Генерирует уникальный текст и отправляет сообщение в диалог сообщества (peer_id = -group_id).
        """
        group_id = group.get("id")
        name = group.get("name", "")
        lead_tier = group.get("lead_tier", "no_site")

        # Генерируем уникальный персонализированный спинтакс-оффер
        message_text = generate_personalized_pitch(group, niche=niche, city=city)

        if dry_run:
            logger.info(f"[DRY-RUN] Имитация отправки в группу ID {group_id} ({clean_group_name(name)})")
            return {
                "success": True,
                "group_id": group_id,
                "name": name,
                "lead_tier": lead_tier,
                "message": message_text,
                "dry_run": True
            }

        # Реальная отправка через VK API
        peer_id = -group_id
        try:
            res = self.vk.send_message(peer_id=peer_id, message=message_text)
            self.db.mark_lead_sent(
                group_id=group_id,
                message_text=message_text,
                name=name,
                screen_name=group.get("screen_name", ""),
                city=city or group.get("detected_city", ""),
                niche=niche or group.get("detected_niche", ""),
                members_count=group.get("members_count", 0),
                site=group.get("site", ""),
                lead_tier=lead_tier
            )
            logger.info(f"✅ Успешно отправлено в группу ID {group_id} ({clean_group_name(name)}), msg_id: {res}")
            return {
                "success": True,
                "group_id": group_id,
                "name": name,
                "lead_tier": lead_tier,
                "message": message_text,
                "response": res
            }

        except VkApiException as e:
            # Критические ошибки: капча (14) или флуд-контроль (9) -> аварийный останов
            if e.error_code in (14, 9, 17):
                logger.error(f"🛑 КРИТИЧЕСКАЯ ОШИБКА VK [{e.error_code}]: {e.error_msg}. Аутрич остановлен во избежание блокировки!")
                raise

            # Ошибки закрытого доступа или черного списка
            logger.warning(f"⚠️ Не удалось отправить в группу ID {group_id}: {e.error_msg} (Код: {e.error_code})")
            self.db.mark_lead_failed(group_id, e.error_code, e.error_msg, name=name)
            return {
                "success": False,
                "group_id": group_id,
                "name": name,
                "error_code": e.error_code,
                "error_msg": e.error_msg
            }

    def run_campaign(self, queries: List[str], cities: List[str], 
                     run_limit: int = 10, dry_run: bool = True) -> Dict[str, Any]:
        """
        Запускает цикл поиска и безопасного аутрича с соблюдением суточных лимитов и задержек.
        """
        sent_today = self.db.count_sent_last_24h()
        logger.info(f"📊 Статистика: за последние 24ч отправлено {sent_today} сообщений (суточный безопасный лимит: {self.daily_limit}).")

        available_quota = max(0, self.daily_limit - sent_today)
        effective_limit = min(run_limit, available_quota)

        if effective_limit <= 0 and not dry_run:
            logger.warning("⛔ Суточный лимит отправок исчерпан! Следующие отправки станут доступны после истечения 24ч окна.")
            return {"status": "quota_exceeded", "sent_today": sent_today, "processed": 0}

        sent_count = 0
        failed_count = 0
        processed_groups = []

        logger.info(f"🚀 Старт кампании аутрича: целевой лимит для текущей сессии = {effective_limit} (Dry-run: {dry_run})")

        for query in queries:
            if sent_count >= effective_limit:
                break

            for city in cities:
                if sent_count >= effective_limit:
                    break

                candidates = self.search_candidates(query=query, city=city, count=30)

                for candidate in candidates:
                    if sent_count >= effective_limit:
                        break

                    # Отправляем сообщение (или имитируем в dry-run)
                    result = self.send_pitch_to_group(candidate, niche=query, city=city, dry_run=dry_run)
                    processed_groups.append(result)

                    if result.get("success"):
                        sent_count += 1
                    else:
                        failed_count += 1

                    # Если еще остались лиды для отправки в текущей сессии — выдерживаем безопасную паузу
                    if sent_count < effective_limit:
                        if dry_run:
                            # В dry-run имитируем паузу 0.2 сек
                            time.sleep(0.2)
                        else:
                            # Случайная пауза человека (75 - 140 сек)
                            delay = random.uniform(self.min_delay, self.max_delay)
                            
                            # Микро-пауза (каждые 3-4 сообщения дополнительный перерыв 2.5 - 4 мин)
                            if sent_count > 0 and sent_count % 3 == 0:
                                extra_delay = random.uniform(150, 240)
                                logger.info(f"☕ Микро-пауза человека ({extra_delay:.0f} сек) после 3 отправок...")
                                time.sleep(extra_delay)
                            else:
                                logger.info(f"⏳ Безопасная пауза перед следующим сообщением: {delay:.1f} сек...")
                                time.sleep(delay)

        logger.info(f"🏁 Кампания завершена. Обработано лидов: {len(processed_groups)}, успешно отправлено: {sent_count}, ошибок: {failed_count}")
        return {
            "status": "completed",
            "dry_run": dry_run,
            "processed": len(processed_groups),
            "sent": sent_count,
            "failed": failed_count,
            "groups": processed_groups
        }
