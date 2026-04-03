-- config/schema.sql
-- ===========================================
-- Esquema inicial de FANFA - Memoria Persistente
-- ===========================================

-- Tabla: Historial de comandos ejecutados/consultados
CREATE TABLE IF NOT EXISTS command_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    command TEXT NOT NULL,
    category TEXT CHECK(category IN ('READ_ONLY', 'WRITE', 'ADMIN')),
    status TEXT CHECK(status IN ('suggested', 'approved', 'executed', 'rejected', 'failed')),
    output_preview TEXT,  -- Primeros 500 chars de la salida
    approval_required BOOLEAN DEFAULT TRUE,
    approved_by_user BOOLEAN,
    execution_time_ms INTEGER,
    error_message TEXT,
    context_summary TEXT,  -- Resumen del contexto de la consulta
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Tabla: Estado del sistema (snapshot periódico)
CREATE TABLE IF NOT EXISTS system_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    hostname TEXT,
    kernel_version TEXT,
    disk_usage_json TEXT,  -- JSON con uso de discos
    memory_usage_json TEXT,  -- JSON con uso de RAM/Swap
    active_services_json TEXT,  -- JSON con servicios críticos
    last_boot DATETIME,
    checksum TEXT  -- Para detectar cambios relevantes
);

-- Tabla: Preferencias del usuario
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    data_type TEXT CHECK(data_type IN ('string', 'integer', 'boolean', 'json')),
    description TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Sesiones de interacción
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_uuid TEXT UNIQUE NOT NULL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    total_interactions INTEGER DEFAULT 0,
    commands_suggested INTEGER DEFAULT 0,
    commands_approved INTEGER DEFAULT 0,
    commands_rejected INTEGER DEFAULT 0,
    summary TEXT  -- Resumen generado por LLM al finalizar
);

-- Tabla: Resúmenes automáticos de interacciones
CREATE TABLE IF NOT EXISTS interaction_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    trigger_event TEXT,  -- 'on_action_complete', 'periodic', 'manual'
    summary_text TEXT NOT NULL,
    key_points_json TEXT,  -- JSON con puntos clave extraídos
    related_commands TEXT,  -- IDs de comandos relacionados (comma-separated)
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- Índices para optimizar consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_command_history_timestamp ON command_history(timestamp);
CREATE INDEX IF NOT EXISTS idx_command_history_status ON command_history(status);
CREATE INDEX IF NOT EXISTS idx_command_history_category ON command_history(category);
CREATE INDEX IF NOT EXISTS idx_system_state_timestamp ON system_state(timestamp);
CREATE INDEX IF NOT EXISTS idx_user_preferences_key ON user_preferences(key);
CREATE INDEX IF NOT EXISTS idx_sessions_uuid ON sessions(session_uuid);
CREATE INDEX IF NOT EXISTS idx_summaries_session ON interaction_summaries(session_id);
