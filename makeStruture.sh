#!/bin/bash

cd /mnt/DATOS/Agentes/fanfa

# Crear directorios con __init__.py para módulos Python
for dir in core memory rag tools security ui tests/unit tests/integration tests/security scripts; do
    mkdir -p "$dir"
    touch "$dir/__init__.py"
done

# Archivos .gitkeep para directorios que deben existir pero estar vacíos
touch logs/.gitkeep
touch data/.gitkeep
mkdir -p data/vector_store
touch data/vector_store/.gitkeep
touch data/user_configs/.gitkeep
touch data/backups/.gitkeep
echo "# ChromaDB vector store - auto-generated, no commitear contenido" > data/vector_store/.gitkeep

# Archivos base vacíos (los rellenaremos a continuación)
touch config/{config.yaml,.env.example,system_prompt.txt,allowed_commands.yaml}
touch core/{agent_loop.py,llm_interface.py,error_handler.py}
touch memory/{persistent_memory.py,summarizer.py,encryption.py}
touch rag/{document_ingestor.py,retriever.py,query_cache.py,embeddings.py}
touch tools/{command_executor.py,config_reader.py,system_info.py,file_utils.py}
touch security/{permission_levels.py,command_validator.py,approval_system.py,alert_system.py}
touch ui/{cli_interface.py,approval_interface.py,emergency_stop.py}
touch scripts/{start_agent.sh,backup_memory.sh,update_model.sh}

# Hacer ejecutables los scripts bash
chmod +x scripts/*.sh tests/*.sh
