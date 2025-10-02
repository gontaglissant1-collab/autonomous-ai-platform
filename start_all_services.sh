#!/bin/bash

# Script pour démarrer tous les microservices OpenManus Unifié

echo "🚀 Démarrage des microservices OpenManus Unifié..."

# Fonction pour démarrer un service en arrière-plan
start_service() {
    local service_name=$1
    local port=$2
    
    echo "📦 Démarrage de $service_name sur le port $port..."
    cd $service_name
    source venv/bin/activate
    nohup python src/main.py > nohup.out 2>&1 &
    echo $! > ../${service_name}.pid
    cd ..
    sleep 2
}

# Démarrer tous les services
start_service "api-gateway-service" "5000"
start_service "planning-brain-service" "5001"
start_service "tools-manager-service" "5002"
start_service "memory-service" "5003"

echo ""
echo "✅ Tous les microservices sont démarrés !"
echo ""
echo "📋 Services disponibles :"
echo "  🌐 API Gateway      : http://localhost:5000"
echo "  🧠 Planning Brain   : http://localhost:5001"
echo "  🔧 Tools Manager    : http://localhost:5002"
echo "  💾 Memory Service   : http://localhost:5003"
echo ""
echo "🔍 Vérification de l'état des services :"
echo "  curl http://localhost:5000/api/health"
echo ""
echo "⏹️  Pour arrêter tous les services, exécutez : ./stop_all_services.sh"

