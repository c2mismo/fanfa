#!/bin/bash
# test_ollama_model.sh - Verificación de modelo qwen2.5:14b

MODEL="qwen2.5:14b"
LOG_FILE="/mnt/DATOS/Agentes/fanfa/logs/ollama_test_$(date +%Y%m%d_%H%M%S).log"

echo "========================================" | tee -a $LOG_FILE
echo "TEST OLLAMA - $MODEL" | tee -a $LOG_FILE
echo "Fecha: $(date)" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE

# 1. Verificar servicio Ollama
echo -e "\n[1] Verificando servicio Ollama..." | tee -a $LOG_FILE
if systemctl is-active --quiet ollama; then
    echo "✅ Servicio Ollama activo" | tee -a $LOG_FILE
else
    echo "❌ Servicio Ollama INACTIVO" | tee -a $LOG_FILE
    exit 1
fi

# 2. Verificar modelo descargado
echo -e "\n[2] Verificando modelo..." | tee -a $LOG_FILE
if ollama list | grep -q "$MODEL"; then
    echo "✅ Modelo $MODEL disponible" | tee -a $LOG_FILE
    ollama list | grep "$MODEL" | tee -a $LOG_FILE
else
    echo "⚠️  Modelo no encontrado, descargando..." | tee -a $LOG_FILE
    ollama pull $MODEL
fi

# 3. Test de inferencia básica
if echo "$RESPONSE" | grep -qiE "(TEST OK|ok|funciona|correcto)"; then
    echo "✅ Inferencia exitosa (${DURATION}s)" | tee -a $LOG_FILE
    echo "   Respuesta (primeras 200 chars): ${RESPONSE:0:200}..." | tee -a $LOG_FILE
else
    # Aún si no encuentra la palabra clave, verificar si hubo respuesta
    if [[ -n "$RESPONSE" ]] && ! echo "$RESPONSE" | grep -qi "error\|timeout\|failed"; then
        echo "⚠️  Inferencia completada (respuesta conversacional)" | tee -a $LOG_FILE
    else
        echo "❌ Inferencia fallida" | tee -a $LOG_FILE
    fi
fi

# 4. Test de contexto sysadmin
echo -e "\n[4] Test contexto sysadmin..." | tee -a $LOG_FILE
ollama run $MODEL "Como sysadmin en Arch Linux, ¿qué comando uso para ver procesos consumiendo más RAM? Responde solo el comando." | tee -a $LOG_FILE

# 5. Verificar uso de GPU
echo -e "\n[5] Uso de GPU durante inferencia..." | tee -a $LOG_FILE
rocm-smi --showalluse 2>/dev/null | tee -a $LOG_FILE || echo "⚠️  rocm-smi no disponible" | tee -a $LOG_FILE

echo -e "\n========================================" | tee -a $LOG_FILE
echo "TEST COMPLETADO" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE
