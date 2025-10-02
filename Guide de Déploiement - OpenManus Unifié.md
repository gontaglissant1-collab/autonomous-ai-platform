# Guide de Déploiement - OpenManus Unifié

## 🚀 Déploiement Frontend

### Option 1: Déploiement Automatique (Recommandé)
Le frontend a été préparé et est prêt pour le déploiement automatique.

1. **Build de production créé** : `/frontend/app/dist/`
2. **Déploiement configuré** : Prêt pour publication
3. **URL de déploiement** : Sera fournie après publication

### Option 2: Déploiement Manuel sur Vercel
```bash
# Installation de Vercel CLI
npm i -g vercel

# Déploiement
cd frontend/app
npm run build
vercel --prod
```

### Option 3: Déploiement sur Netlify
```bash
# Build du projet
cd frontend/app
npm run build

# Glisser-déposer le dossier dist/ sur netlify.com
# Ou utiliser Netlify CLI
npm i -g netlify-cli
netlify deploy --prod --dir=dist
```

## 🔧 Déploiement Backend

### Option 1: Railway (Recommandé)
```bash
# Installation de Railway CLI
npm i -g @railway/cli

# Connexion et déploiement
cd backend
railway login
railway init
railway up
```

### Option 2: Render
1. Connecter le repository GitHub à Render
2. Configurer les variables d'environnement :
   - `HUGGINGFACE_API_KEY`
   - `PORT=3000`
   - `NODE_ENV=production`
3. Déployer automatiquement

### Option 3: Heroku
```bash
# Installation Heroku CLI et déploiement
cd backend
heroku create openmanus-unified-backend
heroku config:set HUGGINGFACE_API_KEY=your_key_here
git push heroku main
```

## 🗄️ Base de Données

### Option 1: MongoDB Atlas (Cloud)
1. Créer un cluster sur [MongoDB Atlas](https://cloud.mongodb.com)
2. Obtenir l'URI de connexion
3. Configurer la variable `MONGODB_URI`

### Option 2: MongoDB Local
```bash
# Installation MongoDB
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Démarrage
sudo systemctl start mongodb
```

### Option 3: Mode Local (Sans Base de Données)
L'application fonctionne sans MongoDB avec un système de fallback intégré.

## 🔑 Configuration des Variables d'Environnement

### Backend (.env)
```env
# Obligatoire pour Hugging Face
HUGGINGFACE_API_KEY=hf_your_token_here

# Configuration serveur
PORT=3000
NODE_ENV=production

# Base de données (optionnel)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/openmanus
DB_NAME=openmanus_unified
```

### Frontend (Variables de build)
```env
# URL du backend en production
VITE_API_URL=https://your-backend-url.com
```

## 🔧 Configuration CORS

Pour la production, mettre à jour le backend :

```javascript
// server.js
app.use(cors({
  origin: [
    'https://your-frontend-domain.com',
    'http://localhost:5173' // Pour le développement
  ]
}));
```

## 📊 Monitoring et Logs

### Backend Monitoring
```javascript
// Ajouter dans server.js
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});
```

### Health Check Endpoint
```javascript
// Ajouter dans server.js
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});
```

## 🚀 Optimisations de Production

### Frontend
1. **Compression** : Activée automatiquement par Vite
2. **Code Splitting** : Configuré par défaut
3. **Cache** : Headers optimisés
4. **PWA** : Peut être ajouté avec Vite PWA plugin

### Backend
1. **Compression** : Ajouter middleware compression
```bash
npm install compression
```

```javascript
const compression = require('compression');
app.use(compression());
```

2. **Rate Limiting** : Protection contre les abus
```bash
npm install express-rate-limit
```

3. **Helmet** : Sécurité headers
```bash
npm install helmet
```

## 🔒 Sécurité

### Variables Sensibles
- ✅ Clés API dans variables d'environnement
- ✅ CORS configuré
- ⚠️ Ajouter rate limiting
- ⚠️ Ajouter validation des inputs

### Recommandations
1. Utiliser HTTPS en production
2. Configurer des domaines spécifiques pour CORS
3. Implémenter l'authentification utilisateur
4. Ajouter des logs de sécurité

## 📈 Scaling

### Horizontal Scaling
- Utiliser un load balancer (Nginx, Cloudflare)
- Déployer plusieurs instances du backend
- Utiliser Redis pour les sessions partagées

### Vertical Scaling
- Augmenter les ressources serveur
- Optimiser les requêtes base de données
- Implémenter le cache

## 🔍 Troubleshooting

### Problèmes Courants

1. **Erreur CORS**
   - Vérifier la configuration CORS
   - S'assurer que l'URL frontend est autorisée

2. **Erreur Hugging Face API**
   - Vérifier la clé API
   - Contrôler les quotas d'utilisation

3. **Erreur MongoDB**
   - Vérifier l'URI de connexion
   - L'application fonctionne sans MongoDB

4. **Build Frontend Échoue**
   - Vérifier les dépendances
   - Nettoyer node_modules et réinstaller

### Logs Utiles
```bash
# Backend logs
pm2 logs openmanus-backend

# Frontend build logs
npm run build -- --verbose

# MongoDB logs
tail -f /var/log/mongodb/mongod.log
```

## ✅ Checklist de Déploiement

### Avant le Déploiement
- [ ] Tests locaux réussis
- [ ] Variables d'environnement configurées
- [ ] Build de production créé
- [ ] CORS configuré pour la production
- [ ] Clé API Hugging Face valide

### Après le Déploiement
- [ ] Health check endpoint répond
- [ ] Frontend accessible
- [ ] API backend fonctionnelle
- [ ] Génération multimodale testée
- [ ] Monitoring configuré

## 🎯 URLs de Production

Une fois déployé, l'application sera accessible via :
- **Frontend** : URL fournie par le service de déploiement
- **Backend API** : URL du service backend + `/api`
- **Health Check** : URL backend + `/health`

---

**Votre plateforme OpenManus Unifié est maintenant prête pour la production ! 🚀**

