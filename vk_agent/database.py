# -*- coding: utf-8 -*-
"""
LocalWeb VK Outreach — Модуль базы данных (SQLite).
Отслеживает найденные группы, историю отправок, статусы, исключает дубли
и контролирует суточные лимиты безопасности ВКонтакте.
"""

import sqlite3
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

logger = logging.getLogger("VkOutreachDB")

class OutreachDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "vk_outreach.db")
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Создает таблицы базы данных, если они еще не существуют."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица лидов (сообществ)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                group_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                screen_name TEXT,
                city TEXT,
                niche TEXT,
                members_count INTEGER DEFAULT 0,
                site TEXT,
                lead_tier TEXT,
                status TEXT NOT NULL,  -- 'found', 'sent', 'skipped', 'failed', 'replied'
                skip_reason TEXT,
                message_text TEXT,
                sent_at TIMESTAMP,
                error_code INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Таблица логов действий
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                group_id INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Индексы для быстрой фильтрации и проверки квот
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads (status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_sent_at ON leads (sent_at)")
            conn.commit()

    def is_lead_processed(self, group_id: int) -> bool:
        """Проверяет, было ли сообщество уже обработано (отправлено или пропущено)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM leads WHERE group_id = ?", (group_id,))
            row = cursor.fetchone()
            if not row:
                return False
            # Если уже отправлено или сознательно пропущено/заблокировано — повторно не трогаем
            return row["status"] in ("sent", "skipped", "failed", "replied")

    def get_lead(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает информацию о лиде по group_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE group_id = ?", (group_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_found_lead(self, group_id: int, name: str, screen_name: str = "",
                        city: str = "", niche: str = "", members_count: int = 0,
                        site: str = "", lead_tier: str = "no_site") -> bool:
        """Сохраняет найденное сообщество в базу."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO leads 
            (group_id, name, screen_name, city, niche, members_count, site, lead_tier, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'found', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (group_id, name, screen_name, city, niche, members_count, site, lead_tier))
            conn.commit()
            return cursor.rowcount > 0

    def mark_lead_sent(self, group_id: int, message_text: str, name: str = "", screen_name: str = "",
                       city: str = "", niche: str = "", members_count: int = 0, site: str = "", lead_tier: str = ""):
        """Отмечает успешную отправку сообщения сообществу (вставляет запись, если ее нет, либо обновляет)."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO leads (group_id, name, screen_name, city, niche, members_count, site, lead_tier, status, message_text, sent_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sent', ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(group_id) DO UPDATE SET
                status = 'sent',
                message_text = excluded.message_text,
                sent_at = excluded.sent_at,
                updated_at = CURRENT_TIMESTAMP,
                error_code = NULL,
                error_message = NULL
            """, (group_id, name or f"Group {group_id}", screen_name, city, niche, members_count, site, lead_tier, message_text, now))
            
            cursor.execute("""
            INSERT INTO outreach_logs (event_type, group_id, details)
            VALUES ('message_sent', ?, 'Успешно отправлено коммерческое предложение')
            """, (group_id,))
            conn.commit()

    def mark_lead_skipped(self, group_id: int, reason: str, name: str = "", screen_name: str = ""):
        """Отмечает лид как пропущенный с указанием причины."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO leads (group_id, name, screen_name, status, skip_reason, created_at, updated_at)
            VALUES (?, ?, ?, 'skipped', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(group_id) DO UPDATE SET
                status = 'skipped',
                skip_reason = excluded.skip_reason,
                updated_at = CURRENT_TIMESTAMP
            """, (group_id, name, screen_name, reason))
            conn.commit()

    def mark_lead_failed(self, group_id: int, error_code: int, error_message: str, name: str = ""):
        """Отмечает ошибку отправки сообщения."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO leads (group_id, name, status, error_code, error_message, created_at, updated_at)
            VALUES (?, ?, 'failed', ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(group_id) DO UPDATE SET
                status = 'failed',
                error_code = excluded.error_code,
                error_message = excluded.error_message,
                updated_at = CURRENT_TIMESTAMP
            """, (group_id, name or f"Group {group_id}", error_code, error_message))
            
            cursor.execute("""
            INSERT INTO outreach_logs (event_type, group_id, details)
            VALUES ('send_error', ?, ?)
            """, (group_id, f"Error {error_code}: {error_message}"))
            conn.commit()

    def count_sent_last_24h(self) -> int:
        """Подсчитывает количество сообщений, отправленных за последние 24 часа (для соблюдения квоты ВК)."""
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT COUNT(*) AS cnt FROM leads 
            WHERE status = 'sent' AND sent_at >= ?
            """, (cutoff,))
            row = cursor.fetchone()
            return row["cnt"] if row else 0

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает общую статистику лидогенерации и рассылки."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) AS cnt FROM leads")
            total_leads = cursor.fetchone()["cnt"]
            
            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status = 'sent'")
            total_sent = cursor.fetchone()["cnt"]
            
            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status = 'skipped'")
            total_skipped = cursor.fetchone()["cnt"]
            
            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status = 'failed'")
            total_failed = cursor.fetchone()["cnt"]
            
            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status = 'found'")
            total_queue = cursor.fetchone()["cnt"]
            
            sent_24h = self.count_sent_last_24h()
            
            return {
                "total_leads": total_leads,
                "total_sent": total_sent,
                "sent_last_24h": sent_24h,
                "total_queue": total_queue,
                "total_skipped": total_skipped,
                "total_failed": total_failed
            }

    def get_recent_sent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Возвращает последние отправленные сообщения."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT group_id, name, city, niche, site, sent_at, message_text 
            FROM leads 
            WHERE status = 'sent' 
            ORDER BY sent_at DESC 
            LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
