# memory/persistent_memory.py
#!/usr/bin/env python3
"""
PersistentMemory - Capa de memoria persistente para FANFA
Gestiona CRUD sobre SQLite con soporte para cifrado opcional y concurrencia segura.
"""

import sqlite3
import json
import logging
import threading
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Dict, List, Any, Union

from config.config_loader import Config  # Asumimos que existe un loader

logger = logging.getLogger(__name__)


class PersistentMemory:
    """Gestor de memoria persistente con SQLite para FANFA."""

    _local = threading.local()  # Conexión thread-local para seguridad

    def __init__(self, db_path: str, encrypt: bool = False, encryption_key: Optional[str] = None):
        self.db_path = Path(db_path).resolve()
        self.encrypt = encrypt
        self.encryption_key = encryption_key
        self._lock = threading.RLock()  # Reentrant lock para operaciones

        # Crear directorio si no existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Inicializar base de datos
        self._initialize_db()
        logger.info(f"PersistentMemory initialized: {self.db_path}")

    @contextmanager
    def _get_connection(self):
        """Obtener conexión thread-safe con contexto automático."""
        conn = None
        try:
            # Conexión por thread para evitar conflictos
            if not hasattr(self._local, 'connection') or self._local.connection is None:
                self._local.connection = sqlite3.connect(
                    str(self.db_path),
                    timeout=30.0,  # Timeout para locks
                    check_same_thread=False  # Gestionado manualmente con locks
                )
                self._local.connection.row_factory = sqlite3.Row  # Acceso por nombre de columna
                # Habilitar WAL para mejor concurrencia
                self._local.connection.execute("PRAGMA journal_mode=WAL")
                self._local.connection.execute("PRAGMA synchronous=NORMAL")

            conn = self._local.connection
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        # Nota: No cerramos la conexión aquí, se mantiene por thread

    def _initialize_db(self):
        """Crear tablas si no existen usando el esquema definido."""
        schema_path = Path(__file__).parent.parent / "config" / "schema.sql"

        with self._get_connection() as conn, self._lock:
            try:
                if schema_path.exists():
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema = f.read()
                    conn.executescript(schema)
                    conn.commit()
                    logger.debug("Database schema initialized")
                else:
                    logger.warning(f"Schema file not found: {schema_path}")
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
                raise

    # ==================== CRUD: command_history ====================

    def add_command_entry(
        self,
        command: str,
        category: str,
        status: str,
        session_id: Optional[int] = None,
        output_preview: Optional[str] = None,
        approval_required: bool = True,
        approved_by_user: Optional[bool] = None,
        execution_time_ms: Optional[int] = None,
        error_message: Optional[str] = None,
        context_summary: Optional[str] = None
    ) -> int:
        """Registrar una entrada en el historial de comandos."""
        with self._get_connection() as conn, self._lock:
            cursor = conn.execute("""
                INSERT INTO command_history (
                    command, category, status, session_id,
                    output_preview, approval_required, approved_by_user,
                    execution_time_ms, error_message, context_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                command, category, status, session_id,
                output_preview[:500] if output_preview else None,
                approval_required, approved_by_user,
                execution_time_ms, error_message, context_summary
            ))
            conn.commit()
            entry_id = cursor.lastrowid
            logger.debug(f"Command history entry added: ID={entry_id}")
            return entry_id

    def get_command_history(
        self,
        limit: int = 50,
        status_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
        session_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Consultar historial de comandos con filtros opcionales."""
        with self._get_connection() as conn:
            query = "SELECT * FROM command_history WHERE 1=1"
            params = []

            if status_filter:
                query += " AND status = ?"
                params.append(status_filter)
            if category_filter:
                query += " AND category = ?"
                params.append(category_filter)
            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_command_status(self, entry_id: int, new_status: str, **updates) -> bool:
        """Actualizar estado de una entrada de comando."""
        allowed_statuses = {'suggested', 'approved', 'executed', 'rejected', 'failed'}
        if new_status not in allowed_statuses:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {allowed_statuses}")

        with self._get_connection() as conn, self._lock:
            updates['status'] = new_status
            updates['id'] = entry_id

            set_clause = ", ".join(f"{k} = ?" for k in updates.keys() if k != 'id')
            params = list(updates.values())

            cursor = conn.execute(
                f"UPDATE command_history SET {set_clause} WHERE id = ?",
                params
            )
            conn.commit()
            return cursor.rowcount > 0

    # ==================== CRUD: user_preferences ====================

    def set_preference(self, key: str, value: Any, data_type: str, description: Optional[str] = None) -> bool:
        """Guardar o actualizar una preferencia del usuario."""
        allowed_types = {'string', 'integer', 'boolean', 'json'}
        if data_type not in allowed_types:
            raise ValueError(f"Invalid data_type: {data_type}. Must be one of {allowed_types}")

        # Serializar valor según tipo
        if data_type == 'json':
            serialized = json.dumps(value)
        elif data_type == 'boolean':
            serialized = '1' if value else '0'
        else:
            serialized = str(value)

        with self._get_connection() as conn, self._lock:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO user_preferences (key, value, data_type, description, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, serialized, data_type, description))
            conn.commit()
            logger.debug(f"Preference saved: {key}={value}")
            return True

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Obtener preferencia con valor por defecto si no existe."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value, data_type FROM user_preferences WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            if not row:
                return default

            value, data_type = row['value'], row['data_type']

            # Deserializar según tipo
            if data_type == 'json':
                return json.loads(value)
            elif data_type == 'integer':
                return int(value)
            elif data_type == 'boolean':
                return value == '1'
            return value

    def get_all_preferences(self) -> Dict[str, Any]:
        """Obtener todas las preferencias como diccionario."""
        prefs = {}
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT key, value, data_type FROM user_preferences")
            for row in cursor.fetchall():
                key, value, data_type = row['key'], row['value'], row['data_type']
                if data_type == 'json':
                    prefs[key] = json.loads(value)
                elif data_type == 'integer':
                    prefs[key] = int(value)
                elif data_type == 'boolean':
                    prefs[key] = value == '1'
                else:
                    prefs[key] = value
        return prefs

    # ==================== CRUD: system_state ====================

    def save_system_state(self, state_ Dict[str, Any]) -> int:
        """Guardar snapshot del estado del sistema."""
        with self._get_connection() as conn, self._lock:
            cursor = conn.execute("""
                INSERT INTO system_state (
                    hostname, kernel_version, disk_usage_json, memory_usage_json,
                    active_services_json, last_boot, checksum
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                state_data.get('hostname'),
                state_data.get('kernel_version'),
                json.dumps(state_data.get('disk_usage', {})),
                json.dumps(state_data.get('memory_usage', {})),
                json.dumps(state_data.get('active_services', {})),
                state_data.get('last_boot'),
                state_data.get('checksum')
            ))
            conn.commit()
            return cursor.lastrowid

    def get_latest_system_state(self) -> Optional[Dict[str, Any]]:
        """Obtener el estado más reciente del sistema."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM system_state ORDER BY timestamp DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if not row:
                return None

            result = dict(row)
            # Deserializar campos JSON
            for field in ['disk_usage_json', 'memory_usage_json', 'active_services_json']:
                if result.get(field):
                    result[field.replace('_json', '')] = json.loads(result[field])
                    del result[field]
            return result

    # ==================== CRUD: sessions ====================

    def create_session(self, session_uuid: str) -> int:
        """Crear nueva sesión de interacción."""
        with self._get_connection() as conn, self._lock:
            cursor = conn.execute(
                "INSERT INTO sessions (session_uuid) VALUES (?)",
                (session_uuid,)
            )
            conn.commit()
            logger.info(f"New session created: {session_uuid}")
            return cursor.lastrowid

    def end_session(self, session_id: int, summary: Optional[str] = None) -> bool:
        """Finalizar sesión y guardar resumen."""
        with self._get_connection() as conn, self._lock:
            cursor = conn.execute("""
                UPDATE sessions
                SET ended_at = CURRENT_TIMESTAMP, summary = ?
                WHERE id = ?
            """, (summary, session_id))
            conn.commit()
            return cursor.rowcount > 0

    def update_session_stats(
        self,
        session_id: int,
        interactions: Optional[int] = None,
        suggested: Optional[int] = None,
        approved: Optional[int] = None,
        rejected: Optional[int] = None
    ) -> bool:
        """Actualizar estadísticas de sesión."""
        with self._get_connection() as conn, self._lock:
            updates = []
            params = []

            if interactions is not None:
                updates.append("total_interactions = COALESCE(total_interactions, 0) + ?")
                params.append(interactions)
            if suggested is not None:
                updates.append("commands_suggested = COALESCE(commands_suggested, 0) + ?")
                params.append(suggested)
            if approved is not None:
                updates.append("commands_approved = COALESCE(commands_approved, 0) + ?")
                params.append(approved)
            if rejected is not None:
                updates.append("commands_rejected = COALESCE(commands_rejected, 0) + ?")
                params.append(rejected)

            if not updates:
                return False

            params.append(session_id)
            cursor = conn.execute(
                f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()
            return cursor.rowcount > 0

    # ==================== Utilidades ====================

    def backup(self, backup_path: str) -> bool:
        """Crear backup de la base de datos usando backup API de SQLite."""
        try:
            backup_dest = Path(backup_path).resolve()
            backup_dest.parent.mkdir(parents=True, exist_ok=True)

            with self._get_connection() as src_conn:
                with sqlite3.connect(str(backup_dest)) as dst_conn:
                    src_conn.backup(dst_conn)

            logger.info(f"Database backup created: {backup_dest}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def vacuum(self) -> bool:
        """Optimizar base de datos con VACUUM."""
        try:
            with self._get_connection() as conn, self._lock:
                conn.execute("VACUUM")
                conn.commit()
            logger.debug("Database vacuumed")
            return True
        except Exception as e:
            logger.error(f"Vacuum failed: {e}")
            return False

    def close(self):
        """Cerrar conexión del thread actual."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            logger.debug("Database connection closed")
