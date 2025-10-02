# OpenManus Unifié

Une application web complète qui recrée et améliore Manus IA en combinant les fonctionnalités open-source d'Open Manus avec des modèles avancés de Hugging Face pour créer une plateforme multimodale d'agents autonomes.

## 🚀 Fonctionnalités

### Agents IA Autonomes
- Création et gestion d'agents personnalisés
- Support pour différents types d'agents (génération de texte, images, audio)
- Interface de configuration avancée
- Monitoring en temps réel

### Intégration Hugging Face
- **Génération de texte** : Modèles de dialogue et raisonnement
- **Génération d'images** : Stable Diffusion et autres modèles
- **Synthèse vocale** : Conversion texte vers audio
- **Analyse d'images** : Description automatique d'images

### Workflows Avancés
- **Contenu Multimodal** : Génération simultanée de texte, image et audio
- **Analyse de Contenu** : Traitement intelligent de différents types de médias
- **Orchestration** : Coordination de tâches complexes entre plusieurs agents
- **Création d'Agents** : Workflow pour créer des agents personnalisés

### Interface Moderne
- Design responsive avec Tailwind CSS
- Thème sombre avec dégradés
- Tableaux de bord interactifs
- Navigation par onglets intuitive

## 🏗️ Architecture

### Backend (Node.js)
- **Express.js** : Serveur API REST
- **Hugging Face Inference** : Intégration des modèles IA
- **MongoDB** : Base de données (avec fallback local)
- **CORS** : Support cross-origin
- **Workflows** : Gestionnaire de tâches complexes

### Frontend (React)
- **React 18** : Interface utilisateur moderne
- **Tailwind CSS** : Styling responsive
- **shadcn/ui** : Composants UI professionnels
- **Lucide React** : Icônes modernes
- **React Router** : Navigation

### Fonctionnalités Multimodales
- Génération d'images via API locale et Hugging Face
- Synthèse vocale intégrée
- Interface unifiée pour tous les types de contenu

## 📦 Installation

### Prérequis
- Node.js 18+
- npm ou pnpm
- MongoDB (optionnel)

### Backend
```bash
cd backend
npm install
cp .env.example .env
# Configurer HUGGINGFACE_API_KEY dans .env
npm start
```

### Frontend
```bash
cd frontend/app
npm install
npm run dev
```

## 🔧 Configuration

### Variables d'environnement
```env
HUGGINGFACE_API_KEY=your_api_key_here
PORT=3000
MONGODB_URI=mongodb://localhost:27017
DB_NAME=openmanus_unified
```

### Modèles Hugging Face supportés
- **Texte** : microsoft/DialoGPT-medium
- **Images** : stabilityai/stable-diffusion-2-1
- **Audio** : microsoft/speecht5_tts
- **Analyse** : Salesforce/blip-image-captioning-base

## 🚀 Déploiement

### Frontend
Le frontend est déployé automatiquement et accessible via l'interface de déploiement.

### Backend
```bash
# Pour déployer le backend
cd backend
npm run build
# Déployer sur Railway, Render ou service similaire
```

## 📊 Fonctionnalités Avancées

### Gestion des Agents
- Création d'agents avec configuration personnalisée
- Types d'agents : text_generation, image_generation, audio_synthesis
- Statut en temps réel (actif, inactif, en cours)
- Historique des tâches

### Workflows Intelligents
- **Multimodal** : Génère texte → image → audio en séquence
- **Analyse** : Traite et analyse différents types de contenu
- **Orchestration** : Coordonne plusieurs agents pour des tâches complexes

### API REST Complète
```
GET /api/agents - Liste des agents
POST /api/agents/create - Créer un agent
POST /api/text/generate - Génération de texte
POST /api/image/generate - Génération d'image
POST /api/audio/synthesize - Synthèse vocale
POST /api/workflows/multimodal - Workflow multimodal
```

## 🔍 Tests et Qualité

### Tests Effectués
- ✅ Interface utilisateur complète
- ✅ Navigation et interactions
- ✅ Génération multimodale locale
- ✅ API backend fonctionnelle
- ⚠️ Intégration Hugging Face (nécessite clé API)

### Métriques
- **Agents Actifs** : 2 agents par défaut
- **Workflows** : 4 types disponibles
- **Tâches Simultanées** : Support jusqu'à 10
- **Modèles HF** : 5 modèles intégrés

## 🤝 Contribution

Ce projet combine les meilleures fonctionnalités de :
- [FoundationAgents/OpenManus](https://github.com/FoundationAgents/OpenManus)
- [OpenManus/OpenManus-RL](https://github.com/OpenManus/OpenManus-RL)

### Améliorations Apportées
- Interface utilisateur moderne et intuitive
- Intégration complète Hugging Face
- Workflows avancés pour tâches complexes
- Architecture modulaire et extensible
- Support multimodal complet

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- Équipe OpenManus pour les bases solides
- Hugging Face pour les modèles IA
- Communauté open-source pour les outils utilisés

---

**OpenManus Unifié** - Votre plateforme d'agents IA autonomes de nouvelle génération 🤖✨

