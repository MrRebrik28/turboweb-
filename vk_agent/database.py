# -*- coding: utf-8 -*-
"""
LocalWeb VK Outreach — Модуль базы данных (SQLite).
Поддерживает двухшаговую стратегию касания:
- Шаг 1: Короткий естественный вопрос-пинг («Касание без продажи»)
- Проверка ответов: отслеживание входящих сообщений от сообществ (взаимный диалог)
- Шаг 2: Продающий оффер с макетом и сайтом за 24ч (отправляется только после ответа)
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
        """Создает таблицы базы данных и выполняет миграции для 2-шаговой стратегии."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Основная таблица лидов (сообществ)
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
                status TEXT NOT NULL,  -- 'found', 'ping_sent', 'replied', 'pitch_sent', 'sent', 'skipped', 'failed'
                skip_reason TEXT,
                message_text TEXT,
                sent_at TIMESTAMP,
                ping_text TEXT,
                ping_sent_at TIMESTAMP,
                reply_text TEXT,
                replied_at TIMESTAMP,
                pitch_text TEXT,
                pitch_sent_at TIMESTAMP,
                error_code INTEGER,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Безопасное добавление колонок для существующих баз данных (миграция)
            existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(leads)").fetchall()]
            new_columns = [
                ("ping_text", "TEXT"),
                ("ping_sent_at", "TIMESTAMP"),
                ("reply_text", "TEXT"),
                ("replied_at", "TIMESTAMP"),
                ("pitch_text", "TEXT"),
                ("pitch_sent_at", "TIMESTAMP")
            ]
            for col_name, col_type in new_columns:
                if col_name not in existing_cols:
                    cursor.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")

            # Таблица аудита и логов
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                group_id INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Индексы для быстрой выборки диалогов и контроля квот
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads (status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_ping_sent_at ON leads (ping_sent_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_replied_at ON leads (replied_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_pitch_sent_at ON leads (pitch_sent_at)")
            conn.commit()

    def is_lead_processed(self, group_id: int) -> bool:
        """Проверяет, было ли сообщество уже в работе (отправлен пинг, оффер или пропущено)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM leads WHERE group_id = ?", (group_id,))
            row = cursor.fetchone()
            if not row:
                return False
            # Сообщества в этих статусах повторно в поиск не берутся
            return row["status"] in ("ping_sent", "replied", "pitch_sent", "sent", "skipped", "failed")

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
        """Сохраняет найденное целевое сообщество в базу."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO leads 
            (group_id, name, screen_name, city, niche, members_count, site, lead_tier, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'found', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (group_id, name, screen_name, city, niche, members_count, site, lead_tier))
            conn.commit()
            return cursor.rowcount > 0

    # ==================== ШАГ 1: ПИНГ («Касание без продажи») ====================

    def mark_ping_sent(self, group_id: int, ping_text: str, name: str = "", screen_name: str = "",
                       city: str = "", niche: str = "", members_count: int = 0, site: str = "", lead_tier: str = ""):
        """Отмечает успешную отправку короткого вопроса Шага 1."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO leads (group_id, name, screen_name, city, niche, members_count, site, lead_tier, 
                               status, ping_text, ping_sent_at, sent_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ping_sent', ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(group_id) DO UPDATE SET
                status = 'ping_sent',
                ping_text = excluded.ping_text,
                ping_sent_at = excluded.ping_sent_at,
                sent_at = excluded.sent_at,
                updated_at = CURRENT_TIMESTAMP,
                error_code = NULL,
                error_message = NULL
            """, (group_id, name or f"Group {group_id}", screen_name, city, niche, members_count, site, lead_tier,
                  ping_text, now, now))
            
            cursor.execute("""
            INSERT INTO outreach_logs (event_type, group_id, details)
            VALUES ('ping_sent', ?, 'Отправлен естественный вопрос Шага 1 (Касание без продажи)')
            """, (group_id,))
            conn.commit()

    def get_pending_replies(self) -> List[Dict[str, Any]]:
        """Возвращает список лидов, которым отправлен Шаг 1, и мы ожидаем ответ."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM leads 
            WHERE status = 'ping_sent'
            ORDER BY ping_sent_at ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    # ==================== ФИКСАЦИЯ ОТВЕТА (ВЗАИМНЫЙ ДИАЛОГ) ====================

    def mark_lead_replied(self, group_id: int, reply_text: str, replied_at: str = None):
        """
        Фиксирует входящий ответ от сообщества! 
        Диалог стал взаимным, спам-фильтр ВК нейтрализован для этого диалога.
        """
        now = replied_at or datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE leads 
            SET status = 'replied', reply_text = ?, replied_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE group_id = ?
            """, (reply_text, now, group_id))

            cursor.execute("""
            INSERT INTO outreach_logs (event_type, group_id, details)
            VALUES ('reply_received', ?, ?)
            """, (group_id, f"Получен ответ: {reply_text[:100]}"))
            conn.commit()

    def get_leads_ready_for_pitch(self) -> List[Dict[str, Any]]:
        """Возвращает лиды, которые ответили на Шаг 1 и готовы к отправке коммерческого оффера."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM leads 
            WHERE status = 'replied'
            ORDER BY replied_at ASC
            """)
            return [dict(row) for row in cursor.fetchall()]

    # ==================== ШАГ 2: ПРОДАЮЩИЙ ОФФЕР ПОСЛЕ ОТВЕТА ====================

    def mark_pitch_sent(self, group_id: int, pitch_text: str):
        """Отмечает успешную отправку Шага 2 (оффер в теплый взаимный диалог)."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE leads 
            SET status = 'pitch_sent', pitch_text = ?, pitch_sent_at = ?, message_text = ?, sent_at = ?, updated_at = CURRENT_TIMESTAMP
            WHERE group_id = ?
            """, (pitch_text, now, pitch_text, now, group_id))

            cursor.execute("""
            INSERT INTO outreach_logs (event_type, group_id, details)
            VALUES ('pitch_sent', ?, 'Отправлен персонализированный оффер во взаимный диалог (Шаг 2)')
            """, (group_id,))
            conn.commit()

    # Для обратной совместимости с 1-шаговым режимом
    def mark_lead_sent(self, group_id: int, message_text: str, **kwargs):
        self.mark_pitch_sent(group_id, message_text)

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

    # ==================== СЧЕТЧИКИ КВОТ И СТАТИСТИКА ====================

    def count_pings_last_24h(self) -> int:
        """Считает количество отправленных коротких вопросов Шага 1 за 24 часа."""
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT COUNT(*) AS cnt FROM leads 
            WHERE ping_sent_at >= ?
            """, (cutoff,))
            row = cursor.fetchone()
            return row["cnt"] if row else 0

    def count_pitches_last_24h(self) -> int:
        """Считает количество отправленных офферов Шага 2 за 24 часа."""
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT COUNT(*) AS cnt FROM leads 
            WHERE pitch_sent_at >= ?
            """, (cutoff,))
            row = cursor.fetchone()
            return row["cnt"] if row else 0

    def count_sent_last_24h(self) -> int:
        """Суммарное количество исходящих первичных сообщений за 24 часа (для совместимости)."""
        return self.count_pings_last_24h()

    def get_two_step_stats(self) -> Dict[str, Any]:
        """Возвращает подробную воронку 2-шагового аутрича."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) AS cnt FROM leads")
            total_leads = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status IN ('ping_sent', 'replied', 'pitch_sent')")
            total_pings = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status IN ('replied', 'pitch_sent')")
            total_replied = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status = 'pitch_sent'")
            total_pitches = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status = 'replied'")
            waiting_pitch = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status = 'skipped'")
            total_skipped = cursor.fetchone()["cnt"]

            cursor.execute("SELECT COUNT(*) AS cnt FROM leads WHERE status = 'failed'")
            total_failed = cursor.fetchone()["cnt"]

            pings_24h = self.count_pings_last_24h()
            pitches_24h = self.count_pitches_last_24h()

            # Конверсия в ответ (Reply Rate)
            conversion_rate = (total_replied / total_pings * 100) if total_pings > 0 else 0.0

            # Последние ответы от сообществ
            cursor.execute("""
            SELECT group_id, name, reply_text, replied_at, status 
            FROM leads 
            WHERE reply_text IS NOT NULL 
            ORDER BY replied_at DESC LIMIT 5
            """)
            recent_replies = [dict(r) for r in cursor.fetchall()]

            return {
                "total_leads": total_leads,
                "total_pings": total_pings,
                "pings_last_24h": pings_24h,
                "total_replied": total_replied,
                "conversion_rate": round(conversion_rate, 1),
                "waiting_pitch": waiting_pitch,
                "total_pitches": total_pitches,
                "pitches_last_24h": pitches_24h,
                "total_skipped": total_skipped,
                "total_failed": total_failed,
                "recent_replies": recent_replies
            }

    def get_stats(self) -> Dict[str, Any]:
        """Общие показатели для совместимости."""
        s = self.get_two_step_stats()
        return {
            "total_leads": s["total_leads"],
            "total_sent": s["total_pings"],
            "sent_last_24h": s["pings_last_24h"],
            "total_queue": s["total_leads"] - s["total_pings"] - s["total_skipped"],
            "total_skipped": s["total_skipped"],
            "total_failed": s["total_failed"]
        }
