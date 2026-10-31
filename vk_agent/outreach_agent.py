# -*- coding: utf-8 -*-
"""
LocalWeb VK Outreach — Автономный агент лидогенерации и 2-шагового безопасного аутрича.

Двухшаговая стратегия («Касание без продажи»):
1. Шаг 1 (Пинг): Короткий вопрос под видом клиента или партнера без ссылок и спам-слов.
   Благодаря естественности и отсутствию спам-триггеров суточный лимит можно увеличить до 30-40 диалогов в день!
2. Проверка ответов (Listening): Агент проверяет входящие сообщения. Когда сообщество отвечает,
   диалог официально становится взаимным для алгоритмов ВК.
3. Шаг 2 (Оффер): В открытый взаимный диалог отправляется персонализированное предложение
   со ссылкой на local-web.ru, тест-драйвом за 24 часа и ценой 7 500 ₽ под ключ.
"""

import time
import random
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from vk_agent.vk_api import VkApiClient, VkApiException
from vk_agent.database import OutreachDatabase
from vk_agent.spintax import (
    generate_step1_ping, 
    generate_step2_pitch, 
    generate_personalized_pitch, 
    clean_group_name
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VkOutreachAgent")

# Черный список стоп-слов для фильтрации нецелевых сообществ
STOP_WORDS = [
    "новости", "подслушано", "барахолка", "отдам даром", "объявления", 
    "работа", "мемы", "приколы", "18+", "чат", "порно", "ставки", 
    "казино", "секонд", "знакомства", "скидки", "бесплатно", "купоны",
    "аренда жилья", "доска объявлений", "происшествия", "дпс", "дтп"
]

BUILDER_DOMAINS = [
    "taplink.cc", "vk.link", "tilda.ws", "wixsite.com", 
    "linktr.ee", "mssg.me", "setup.ru", "site123.me"
]

class VkOutreachAgent:
    def __init__(self, token: str, db: OutreachDatabase = None, 
                 step1_daily_limit: int = 35, step2_daily_limit: int = 50,
                 min_delay_step1: int = 50, max_delay_step1: int = 90):
        self.vk = VkApiClient(token)
        self.db = db or OutreachDatabase()
        self.step1_daily_limit = step1_daily_limit
        self.step2_daily_limit = step2_daily_limit
        self.min_delay_step1 = min_delay_step1
        self.max_delay_step1 = max_delay_step1
        # Для обратной совместимости
        self.daily_limit = step1_daily_limit
        self.min_delay = min_delay_step1
        self.max_delay = max_delay_step1

    def evaluate_group(self, group: Dict[str, Any]) -> (bool, str, str):
        """Оценивает сообщество на соответствие критериям целевого бизнеса."""
        group_id = group.get("id")
        name = group.get("name", "").strip()
        desc = (group.get("description") or "").lower()
        name_lower = name.lower()

        # 1. Открыты ли сообщения группы
        can_message = group.get("can_message", 0)
        if can_message != 1:
            return False, "", "messages_disabled"

        # 2. Не закрытая ли группа
        is_closed = group.get("is_closed", 0)
        if is_closed != 0:
            return False, "", "closed_group"

        # 3. Не забанена ли страница
        if group.get("deactivated"):
            return False, "", "deactivated"

        # 4. Диапазон участников: 70 - 25 000
        members_count = group.get("members_count", 0)
        if members_count < 70:
            return False, "", f"too_small ({members_count} members)"
        if members_count > 25000:
            return False, "", f"too_large_federal ({members_count} members)"

        # 5. Стоп-слова
        for sw in STOP_WORDS:
            if sw in name_lower:
                return False, "", f"stop_word_in_name ('{sw}')"
            if sw in desc[:200]:
                return False, "", f"stop_word_in_desc ('{sw}')"

        # 6. Наличие сайта
        site = (group.get("site") or "").strip().lower()
        if not site or site.startswith("https://vk.com") or site.startswith("http://vk.com"):
            lead_tier = "no_site"
        elif any(b in site for b in BUILDER_DOMAINS):
            lead_tier = "builder_site"
        else:
            lead_tier = "custom_site"

        return True, lead_tier, ""

    def search_candidates(self, query: str, city: str = "", count: int = 40) -> List[Dict[str, Any]]:
        """Ищет сообщества по ключевым словам и городу, фильтрует нецелевые и дубли."""
        search_query = f"{query} {city}".strip()
        logger.info(f"🔎 Поиск сообществ по запросу: '{search_query}' (до {count})...")

        raw_results = self.vk.search_groups(
            query=search_query,
            count=count,
            fields="can_message,site,description,members_count,city,contacts,status"
        )

        items = raw_results.get("items", []) if isinstance(raw_results, dict) else []
        logger.info(f"Найдено в VK: {len(items)}")

        qualified_candidates = []

        for group in items:
            group_id = group.get("id")
            name = group.get("name", "")

            if self.db.is_lead_processed(group_id):
                continue

            is_qualified, lead_tier, reject_reason = self.evaluate_group(group)

            if not is_qualified:
                self.db.mark_lead_skipped(group_id, reject_reason, name=name, screen_name=group.get("screen_name", ""))
                continue

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

        tier_weights = {"no_site": 0, "builder_site": 1, "custom_site": 2}
        qualified_candidates.sort(key=lambda g: tier_weights.get(g.get("lead_tier", "custom_site"), 3))

        logger.info(f"Квалифицированных лидов готово к пингу: {len(qualified_candidates)}")
        return qualified_candidates

    # ==================== ШАГ 1: ОТПРАВКА ПИНГА ====================

    def send_step1_ping(self, group: Dict[str, Any], niche: str, city: str = "", dry_run: bool = False) -> Dict[str, Any]:
        """Отправляет короткий естественный вопрос Шага 1 в сообщения сообщества."""
        group_id = group.get("id")
        name = group.get("name", "")
        lead_tier = group.get("lead_tier", "no_site")

        ping_text = generate_step1_ping(group, niche=niche, city=city)

        if dry_run:
            logger.info(f"[DRY-RUN ШАГ 1] Имитация отправки пинга в группу ID {group_id} ({clean_group_name(name)})")
            return {
                "success": True,
                "group_id": group_id,
                "name": name,
                "lead_tier": lead_tier,
                "message": ping_text,
                "dry_run": True
            }

        peer_id = -group_id
        try:
            res = self.vk.send_message(peer_id=peer_id, message=ping_text)
            self.db.mark_ping_sent(
                group_id=group_id,
                ping_text=ping_text,
                name=name,
                screen_name=group.get("screen_name", ""),
                city=city or group.get("detected_city", ""),
                niche=niche or group.get("detected_niche", ""),
                members_count=group.get("members_count", 0),
                site=group.get("site", ""),
                lead_tier=lead_tier
            )
            logger.info(f"✅ [ШАГ 1] Пинг доставлен в группу ID {group_id} ({clean_group_name(name)}), msg_id: {res}")
            return {
                "success": True,
                "group_id": group_id,
                "name": name,
                "lead_tier": lead_tier,
                "message": ping_text,
                "response": res
            }

        except VkApiException as e:
            if e.error_code in (14, 9, 17):
                logger.error(f"🛑 КРИТИЧЕСКАЯ ОШИБКА VK [{e.error_code}]: {e.error_msg}. Аутрич остановлен!")
                raise
            logger.warning(f"⚠️ Ошибка отправки в группу ID {group_id}: {e.error_msg} (Код: {e.error_code})")
            self.db.mark_lead_failed(group_id, e.error_code, e.error_msg, name=name)
            return {"success": False, "group_id": group_id, "name": name, "error_code": e.error_code, "error_msg": e.error_msg}

    # ==================== СЛУШАТЕЛЬ ВХОДЯЩИХ ОТВЕТОВ (LISTENER) ====================

    def check_incoming_replies(self) -> List[Dict[str, Any]]:
        """
        Проверяет диалоги с сообществами на наличие новых входящих ответов.
        Если группа ответила на наш пинг — диалог фиксируется как взаимный!
        """
        logger.info("📬 Проверка входящих ответов от сообществ через VK API...")
        try:
            convs = self.vk.get_conversations(count=60)
        except Exception as e:
            logger.error(f"Ошибка получения бесед: {e}")
            return []

        items = convs.get("items", []) if isinstance(convs, dict) else []
        discovered_replies = []

        for item in items:
            conversation = item.get("conversation", {})
            last_message = item.get("last_message", {})
            peer_id = conversation.get("peer", {}).get("id", 0)

            # Нас интересуют диалоги с группами (peer_id < 0)
            if peer_id >= 0:
                continue

            group_id = abs(peer_id)
            lead = self.db.get_lead(group_id)

            if not lead:
                continue

            # Если мы отправляли пинг и ждем ответа
            if lead.get("status") == "ping_sent":
                # out == 0 означает, что последнее сообщение отправлено сообществом нам!
                is_incoming = last_message.get("out") == 0
                if is_incoming:
                    reply_text = last_message.get("text", "").strip()
                    reply_date = datetime.fromtimestamp(last_message.get("date", time.time())).isoformat()
                    
                    self.db.mark_lead_replied(group_id, reply_text=reply_text, replied_at=reply_date)
                    logger.info(f"🎉 [ВЗАИМНЫЙ ДИАЛОГ] Группа ID {group_id} («{lead.get('name')}») ответила: \"{reply_text[:80]}\"")
                    discovered_replies.append({
                        "group_id": group_id,
                        "name": lead.get("name"),
                        "reply_text": reply_text,
                        "replied_at": reply_date
                    })

        logger.info(f"Всего новых зафиксированных ответов: {len(discovered_replies)}")
        return discovered_replies

    # ==================== ШАГ 2: ОТПРАВКА ОФФЕРА ВО ВЗАИМНЫЙ ДИАЛОГ ====================

    def send_step2_pitch(self, lead: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """
        Отправляет продающий оффер Шага 2 во ВЗАИМНЫЙ диалог (сообщество уже ответило).
        Здесь спам-фильтр ВК нейтрализован.
        """
        group_id = lead.get("group_id")
        name = lead.get("name", "")
        niche = lead.get("niche") or "вашей сферы"
        city = lead.get("city") or ""

        pitch_text = generate_step2_pitch(lead, niche=niche, city=city)

        if dry_run:
            logger.info(f"[DRY-RUN ШАГ 2] Имитация отправки оффера в группу ID {group_id} ({clean_group_name(name)})")
            return {
                "success": True,
                "group_id": group_id,
                "name": name,
                "message": pitch_text,
                "dry_run": True
            }

        peer_id = -group_id
        try:
            res = self.vk.send_message(peer_id=peer_id, message=pitch_text)
            self.db.mark_pitch_sent(group_id, pitch_text)
            logger.info(f"🚀 [ШАГ 2] Коммерческий оффер доставлен в группу ID {group_id} ({clean_group_name(name)}), msg_id: {res}")
            return {
                "success": True,
                "group_id": group_id,
                "name": name,
                "message": pitch_text,
                "response": res
            }
        except VkApiException as e:
            if e.error_code in (14, 9, 17):
                logger.error(f"🛑 КРИТИЧЕСКАЯ ОШИБКА VK [{e.error_code}]: {e.error_msg}.")
                raise
            logger.warning(f"⚠️ Ошибка отправки Шага 2 в группу ID {group_id}: {e.error_msg}")
            return {"success": False, "group_id": group_id, "name": name, "error_code": e.error_code, "error_msg": e.error_msg}

    # ==================== ЦИКЛЫ ВЫПОЛНЕНИЯ ====================

    def run_step1_campaign(self, queries: List[str], cities: List[str], 
                           run_limit: int = 25, dry_run: bool = True) -> Dict[str, Any]:
        """Запускает рассылку естественных пингов Шага 1."""
        pings_24h = self.db.count_pings_last_24h()
        logger.info(f"📊 Статистика Шага 1: за последние 24ч отправлено {pings_24h} пингов (безопасный лимит: {self.step1_daily_limit}).")

        available_quota = max(0, self.step1_daily_limit - pings_24h)
        effective_limit = min(run_limit, available_quota)

        if effective_limit <= 0 and not dry_run:
            logger.warning("⛔ Суточный лимит пингов исчерпан! Ожидайте истечения 24-часового окна.")
            return {"status": "quota_exceeded", "sent_today": pings_24h, "processed": 0}

        sent_count = 0
        processed_groups = []

        logger.info(f"🚀 Старт кампании Шага 1: целевой объем сессии = {effective_limit} (Dry-run: {dry_run})")

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

                    res = self.send_step1_ping(candidate, niche=query, city=city, dry_run=dry_run)
                    processed_groups.append(res)

                    if res.get("success"):
                        sent_count += 1

                    if sent_count < effective_limit:
                        if dry_run:
                            time.sleep(0.15)
                        else:
                            delay = random.uniform(self.min_delay_step1, self.max_delay_step1)
                            if sent_count > 0 and sent_count % 4 == 0:
                                break_delay = random.uniform(120, 180)
                                logger.info(f"☕ Человеческая микро-пауза ({break_delay:.0f} сек) после 4 сообщений...")
                                time.sleep(break_delay)
                            else:
                                logger.info(f"⏳ Безопасная пауза перед следующим пингом: {delay:.1f} сек...")
                                time.sleep(delay)

        return {
            "status": "completed",
            "step": 1,
            "dry_run": dry_run,
            "processed": len(processed_groups),
            "sent": sent_count,
            "groups": processed_groups
        }

    def run_step2_campaign(self, dry_run: bool = True) -> Dict[str, Any]:
        """Отправляет продающие офферы Шага 2 всем лидам, которые ответили на пинг."""
        ready_leads = self.db.get_leads_ready_for_pitch()
        logger.info(f"🎯 Лидов, ответивших на пинг и готовых к получению оффера: {len(ready_leads)}")

        if not ready_leads:
            return {"status": "no_leads_ready", "sent": 0}

        sent_count = 0
        processed = []

        for lead in ready_leads:
            res = self.send_step2_pitch(lead, dry_run=dry_run)
            processed.append(res)
            if res.get("success"):
                sent_count += 1

            if not dry_run and sent_count < len(ready_leads):
                delay = random.uniform(35, 70)
                logger.info(f"⏳ Пауза перед следующим оффером: {delay:.1f} сек...")
                time.sleep(delay)

        return {
            "status": "completed",
            "step": 2,
            "dry_run": dry_run,
            "sent": sent_count,
            "groups": processed
        }

    def run_auto_pipeline(self, queries: List[str], cities: List[str], 
                          step1_limit: int = 25, dry_run: bool = False) -> Dict[str, Any]:
        """
        Полный автоматический конвейер:
        1. Проверяет новые ответы на ранее отправленные пинги.
        2. Отправляет офферы Шага 2 тем, кто ответил.
        3. Отправляет свежие пинги Шага 1 новым группам в рамках квоты.
        """
        logger.info("🔄 ЗАПУСК АВТОМАТИЧЕСКОГО КОНВЕЙЕРА (ШАГ 1 + ОТВЕТЫ + ШАГ 2)...")
        
        # 1. Проверяем ответы
        new_replies = self.check_incoming_replies() if not dry_run else []

        # 2. Отправляем офферы тем, кто ответил
        step2_res = self.run_step2_campaign(dry_run=dry_run)

        # 3. Отправляем новые пинги
        step1_res = self.run_step1_campaign(queries=queries, cities=cities, run_limit=step1_limit, dry_run=dry_run)

        return {
            "status": "completed",
            "new_replies_count": len(new_replies),
            "step2_pitches_sent": step2_res.get("sent", 0),
            "step1_pings_sent": step1_res.get("sent", 0)
        }

    # Для обратной совместимости с run_campaign
    def run_campaign(self, queries: List[str], cities: List[str], run_limit: int = 10, dry_run: bool = True) -> Dict[str, Any]:
        return self.run_step1_campaign(queries=queries, cities=cities, run_limit=run_limit, dry_run=dry_run)

    def send_pitch_to_group(self, group: Dict[str, Any], niche: str, city: str = "", dry_run: bool = False) -> Dict[str, Any]:
        return self.send_step1_ping(group, niche=niche, city=city, dry_run=dry_run)
