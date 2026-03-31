# Fanfa - SysAdmin Assistant with Ollama

[![Status](https://img.shields.io/badge/Status-FASE%200%20Complete-blue)]()
[![Arch Linux](https://img.shields.io/badge/OS-Arch%20Linux-1793D1?logo=arch-linux)]()
[![License](https://img.shields.io/badge/License-GPL--3.0-orange)](LICENSE)

> **Asistente IA local para administración de sistemas**  
> 🤖 Sugiere · 📝 Documenta · 🔒 Nunca ejecuta sin aprobación humana

---

## 🎯 FINALIDAD DEL PROYECTO

Fanfa es un asistente de inteligencia artificial diseñado para **apoyar al administrador de sistemas** en tareas cotidianas, actuando como una herramienta de consulta y documentación que **nunca reemplaza el criterio humano**.

### Propósito Principal

| Lo que HARÁ ✅ | Lo que NUNCA hará ❌ |
|----------------|---------------------|
| Analizar logs y configuraciones | Ejecutar comandos sin aprobación |
| Sugerir comandos basados en documentación | Tomar decisiones autónomas críticas |
| Documentar acciones realizadas | Modificar configuraciones sin confirmación |
| Recordar preferencias del usuario | Exponer datos sensibles o credenciales |
| Recuperar información de man pages | Reemplazar el criterio del administrador |

### Filosofía de Diseño

El flujo de trabajo de Fanfa se basa en un principio fundamental: **la aprobación explícita del usuario es obligatoria antes de cualquier acción del sistema**.

| Componente | Descripción |
|------------|-------------|
| **USUARIO (SysAdmin)** | Inicia la solicitud |
| **[APROBACIÓN EXPLÍCITA REQUIRED]** | Validación obligatoria del usuario |
| **FANFA (Asistente IA)** | Procesa y sugiere acciones |
| **[SUGERENCIA / DOCUMENTACIÓN / ANÁLISIS]** | Proporciona recomendaciones |
| **SISTEMA (Comandos ejecutados SOLO con aprobación)** | Ejecuta solo con autorización |

Este modelo garantiza que **el usuario mantiene control total** en todo momento, y el asistente actúa como una herramienta de apoyo, nunca como un agente autónomo.

---

## 📊 ESTADO ACTUAL DEL PROYECTO

### Fases Completadas

| Fase | Estado | Progreso | Descripción |
|------|--------|----------|-------------|
| **FASE 0** | ✅ **COMPLETADA** | 100% | Preparación del entorno |
| FASE 1 | ⏳ Pendiente | 0% | Instalación de Ollama |
| FASE 2 | ⏳ Pendiente | 0% | Estructura del proyecto |
| FASE 3 | ⏳ Pendiente | 0% | Memoria persistente |
| FASE 4 | ⏳ Pendiente | 0% | Capa RAG |
| FASE 5 | ⏳ Pendiente | 0% | Herramientas |
| FASE 6 | ⏳ Pendiente | 0% | Orquestación |
| FASE 7 | ⏳ Pendiente | 0% | Human-in-the-loop |
| FASE 8 | ⏳ Pendiente | 0% | Logging |
| FASE 9 | ⏳ Pendiente | 0% | Documentación |
| FASE 10 | ⏳ Pendiente | 0% | Pruebas |
| FASE 11 | ⏳ Pendiente | 0% | Despliegue |
| FASE 12 | ⏳ Pendiente | 0% | Mantenimiento |


## ✅ DETALLE FASE 0 (COMPLETADA)

La **FASE 0** ha completado exitosamente la preparación del entorno de desarrollo. Todos los requisitos previos están en su lugar.

### [0.1] Verificar requisitos del sistema

- ✅ Hardware compatible verificado
- ✅ Firmware AMDGPU instalado
- ✅ Grupos render,video configurados

### [0.2] Crear directorio de proyecto

- ✅ Ubicación: `/mnt/DATOS/Agentes/fanfa`
- ✅ Permisos: `700` (solo usuario propietario)
- ✅ Estructura base creada

### [0.3] Crear entorno virtual Python

- ✅ `.venv` aislado del sistema
- ✅ `pip` actualizado

### [0.4] Configurar control de versiones (git)

- ✅ Repositorio local inicializado
- ✅ `.gitignore` configurado
- ✅ Repositorio remoto en GitHub



---

## 🖥️ HARDWARE DEL SISTEMA

| Componente | Especificación |
|------------|---------------|
| **Sistema Operativo** | Arch Linux x86_64 |
| **Kernel** | Linux Zen (rolling) |
| **CPU** | AMD Ryzen 5 9600X |
| **GPU** | AMD Radeon RX 9060 XT |
| **VRAM** | 15.922 GiB GDDR6 |
| **RAM** | 14.77 GiB |
| **Disco** | 400.98 GiB (Btrfs) |
| **Firmware GPU** | linux-firmware-amdgpu |

### Modelos IA Compatibles

| Modelo | Parámetros | Estado |
|--------|-----------|--------|
| `llama3.1:8b` | 8B | ✅ Recomendado |
| `mistral:7b` | 7B | ✅ Recomendado |
| `codellama:13b` | 13B | ⚠️ Ajustado |
| `llama3.1:70b` | 70B | ❌ No compatible |

---

## 📁 ESTRUCTURA DEL PROYECTO

La estructura del proyecto está organizada de forma modular para facilitar el mantenimiento y la escalabilidad:

| Ruta | Descripción |
|------|-------------|
| `.git/` | Repositorio Git |
| `.venv/` | Entorno virtual Python |
| `LICENSE` | Licencia GNU GPL v3 |
| `README.md` | Este archivo |
| `core/` | Lógica principal |
| `memory/` | Memoria persistente |
| `rag/` | Recuperación de conocimiento |
| `tools/` | Herramientas |
| `security/` | Permisos y validación |
| `config/` | Configuraciones |
| `logs/` | Registros (excluido de git) |
| `data/` | Datos persistentes (excluido de git) |
| `tests/` | Pruebas |


### Descripción de directorios principales

- **`core/`**: Contiene la lógica central del asistente y orquestación
- **`memory/`**: Gestión de memoria persistente y contexto del usuario
- **`rag/`**: Implementación de Retrieval-Augmented Generation para conocimiento
- **`tools/`**: Herramientas y utilidades disponibles para el asistente
- **`security/`**: Validación de permisos y control de acceso
- **`config/`**: Archivos de configuración y variables de entorno

---

## 🔒 SEGURIDAD

### Principios Críticos

- [ ] Ollama solo en localhost (127.0.0.1:11434)
- [ ] Asistente nunca corre como root
- [ ] Todos los comandos requieren aprobación explícita
- [ ] No hay ejecución autónoma de writes/admin
- [ ] Logs de todas las acciones
- [ ] Sistema de aborto de emergencia

### Checklist de Seguridad

- [ ] Ollama solo escucha en 127.0.0.1
- [ ] Asistente corre como usuario sin privilegios
- [ ] Todos los comandos requieren aprobación explícita
- [ ] No hay ejecución autónoma de writes/admin
- [ ] Memoria cifrada si contiene datos sensibles
- [ ] Logs de todas las acciones (aprobadas y rechazadas)
- [ ] Sistema de aborto de emergencia implementado
- [ ] Backup regular de memoria y configuración
- [ ] Firewall bloquea puertos innecesarios
- [ ] Revisión periódica de allowed_commands


---

## 🚀 PRÓXIMOS PASOS

### FASE 1: Instalación de Ollama

```bash
# Instalar stack ROCm
sudo pacman -S rocm-core rocm-hip-sdk rocm-llvm

# Instalar Ollama con soporte AMD
sudo pacman -S ollama-rocm

# Configurar para localhost
# Editar: /etc/systemd/system/ollama.service
# OLLAMA_HOST=127.0.0.1:11434

# Descargar modelos base
ollama pull llama3.1
ollama pull nomic-embed-text
```


📄 LICENCIA
Este proyecto está bajo la licencia GNU General Public License v3.0.
Ver archivo [LICENSE](https://github.com/c2mismo/fanfa/blob/main/LICENSE) para más detalles.


⚠️ DESCARGO DE RESPONSABILIDAD

IMPORTANTE: Este asistente es una herramienta de apoyo para administradores de sistemas.

    NUNCA debe usarse como único medio de toma de decisiones críticas
    SIEMPRE requiere supervisión humana para acciones que modifican el sistema
    El desarrollador NO se hace responsable de daños causados por mal uso
    TÚ eres el administrador. El asistente sugiere, TÚ decides.


<div align="center">

Fanfa · Hecho con ❤️ para SysAdmins
[Repositorio](https://github.com/c2mismo/fanfa)
 · [Roadmap](https://github.com/c2mismo/fanfa/blob/main/roadmap)
</div>
