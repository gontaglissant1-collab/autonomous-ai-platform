# Fonctionnalités Clés des Projets OpenManus

## FoundationAgents/OpenManus
Ce dépôt semble être le cœur de l'agent IA général, avec des fonctionnalités pour:
- **Gestion des agents**: `app/agent/`
- **Outils**: `app/tool/` (probablement pour l'intégration d'outils externes)
- **LLM**: `app/llm.py` (gestion des modèles de langage)
- **Flux de travail**: `app/flow/` (pour l'orchestration de tâches complexes)
- **Configuration**: `config/` (fichiers de configuration pour les API LLM)
- **Exemples**: `examples/` (pour comprendre l'utilisation)
- **Sandbox**: `app/sandbox/` (environnement d'exécution isolé)

## OpenManus/OpenManus-RL
Ce dépôt est une extension axée sur l'apprentissage par renforcement pour les agents LLM, avec des éléments clés comme:
- **Logique RL**: `openmanus_rl/` (contient probablement les algorithmes et la logique RL)
- **Données**: `data/` (pour les datasets d'entraînement)
- **Exemples**: `examples/` (pour l'application de RL aux agents)
- **Scripts**: `scripts/` (pour l'entraînement et l'évaluation)

### Objectif d'intégration:
L'objectif est de combiner ces fonctionnalités pour créer une plateforme unifiée capable de:
1.  Gérer des agents IA autonomes.
2.  Utiliser des outils externes.
3.  Intégrer des modèles LLM avancés.
4.  Orchestrer des flux de travail complexes.
5.  Appliquer l'apprentissage par renforcement pour améliorer les performances des agents.

Ces fonctionnalités serviront de base pour l'intégration des modèles Hugging Face et le développement de l'application web complète.

