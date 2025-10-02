#!/bin/bash

# Script pour arrêter tous les microservices OpenManus Unifié

echo "⏹️  Arrêt des microservices OpenManus Unifié..."

# Fonction pour arrêter un service
stop_service() {
    local service_name=$1
    local pid_file="${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat $pid_file)
        if ps -p $pid > /dev/null; then
            echo "🛑 Arrêt de $service_name (PID: $pid)..."
            kill $pid
            rm $pid_file
        else
            echo "⚠️  $service_name n'était pas en cours d'exécution"
            rm $pid_file
        fi
    else
        echo "⚠️  Fichier PID pour $service_name introuvable"
    fi
}

# Arrêter tous les services
stop_service "api-gateway-service"
stop_service "planning-brain-service"
stop_service "tools-manager-service"
stop_service "memory-service"

# Nettoyer les processus restants sur les ports utilisés
echo "🧹 Nettoyage des processus restants..."
for port in 5000 5001 5002 5003; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "🔫 Arrêt forcé du processus sur le port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
    fi
done

echo ""
echo "✅ Tous les microservices ont été arrêtés !"

