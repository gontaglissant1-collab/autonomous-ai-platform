const express = require('express');
const cors = require('cors');
const { HfInference } = require('@huggingface/inference');
const Database = require('./database');
const WorkflowManager = require('./workflows');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

// Configuration CORS pour permettre les requêtes cross-origin
app.use(cors());
app.use(express.json());

// Initialisation de l'API Hugging Face
const hf = new HfInference(process.env.HUGGINGFACE_API_KEY);

// Initialisation de la base de données
const database = new Database();

// Initialisation du gestionnaire de workflows
const workflowManager = new WorkflowManager(hf);

// Connexion à la base de données au démarrage
database.connect().then(connected => {
  if (connected) {
    console.log('Base de données connectée avec succès');
  } else {
    console.log('Fonctionnement sans base de données (mode local)');
  }
});

app.get('/', (req, res) => {
  res.send('Backend OpenManus unifié en cours d\'exécution !');
});

// Route pour la génération de texte
app.post('/api/text/generate', async (req, res) => {
  try {
    const { prompt, model = 'microsoft/DialoGPT-medium' } = req.body;
    
    const response = await hf.textGeneration({
      model: model,
      inputs: prompt,
      parameters: {
        max_new_tokens: 100,
        temperature: 0.7,
        return_full_text: false
      }
    });
    
    res.json({ success: true, result: response.generated_text });
  } catch (error) {
    console.error('Erreur génération de texte:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Route pour la génération d'images
app.post('/api/image/generate', async (req, res) => {
  try {
    const { prompt, model = 'stabilityai/stable-diffusion-2-1' } = req.body;
    
    const response = await hf.textToImage({
      model: model,
      inputs: prompt
    });
    
    // Convertir l'image en base64 pour l'envoi
    const buffer = Buffer.from(await response.arrayBuffer());
    const base64Image = buffer.toString('base64');
    
    res.json({ 
      success: true, 
      image: `data:image/png;base64,${base64Image}` 
    });
  } catch (error) {
    console.error('Erreur génération d\'image:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Route pour la synthèse vocale
app.post('/api/audio/synthesize', async (req, res) => {
  try {
    const { text, model = 'microsoft/speecht5_tts' } = req.body;
    
    const response = await hf.textToSpeech({
      model: model,
      inputs: text
    });
    
    // Convertir l'audio en base64
    const buffer = Buffer.from(await response.arrayBuffer());
    const base64Audio = buffer.toString('base64');
    
    res.json({ 
      success: true, 
      audio: `data:audio/wav;base64,${base64Audio}` 
    });
  } catch (error) {
    console.error('Erreur synthèse vocale:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Route pour l'analyse d'images
app.post('/api/image/analyze', async (req, res) => {
  try {
    const { imageUrl, model = 'Salesforce/blip-image-captioning-base' } = req.body;
    
    const response = await hf.imageToText({
      model: model,
      data: imageUrl
    });
    
    res.json({ success: true, description: response.generated_text });
  } catch (error) {
    console.error('Erreur analyse d\'image:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Route pour la gestion des agents
app.post('/api/agents/create', async (req, res) => {
  try {
    const { name, type, configuration } = req.body;
    
    const agent = {
      id: Date.now().toString(),
      name,
      type,
      configuration,
      status: 'active',
      createdAt: new Date().toISOString()
    };
    
    // Sauvegarder en base de données si disponible
    if (database.db) {
      const result = await database.createAgent(agent);
      if (result.success) {
        agent._id = result.id;
      }
    }
    
    res.json({ success: true, agent });
  } catch (error) {
    console.error('Erreur création d\'agent:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Route pour lister les agents
app.get('/api/agents', async (req, res) => {
  try {
    let agents = [];
    
    // Récupérer depuis la base de données si disponible
    if (database.db) {
      const result = await database.getAgents();
      if (result.success) {
        agents = result.agents;
      }
    } else {
      // Agents par défaut si pas de base de données
      agents = [
        {
          id: '1',
          name: 'Agent de génération de texte',
          type: 'text_generation',
          status: 'active',
          createdAt: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Agent de génération d\'images',
          type: 'image_generation',
          status: 'active',
          createdAt: new Date().toISOString()
        }
      ];
    }
    
    res.json({ success: true, agents });
  } catch (error) {
    console.error('Erreur récupération agents:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Routes pour les workflows
app.post('/api/workflows/multimodal', async (req, res) => {
  try {
    const { prompt, options } = req.body;
    const result = await workflowManager.createMultimodalContent(prompt, options);
    res.json(result);
  } catch (error) {
    console.error('Erreur workflow multimodal:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/workflows/analyze', async (req, res) => {
  try {
    const { content, contentType } = req.body;
    const result = await workflowManager.analyzeContent(content, contentType);
    res.json(result);
  } catch (error) {
    console.error('Erreur workflow d\'analyse:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/workflows/create-agent', async (req, res) => {
  try {
    const { agentConfig } = req.body;
    const result = await workflowManager.createCustomAgent(agentConfig);
    res.json(result);
  } catch (error) {
    console.error('Erreur workflow création d\'agent:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/workflows/orchestrate', async (req, res) => {
  try {
    const { taskDescription, agents } = req.body;
    const result = await workflowManager.orchestrateComplexTask(taskDescription, agents);
    res.json(result);
  } catch (error) {
    console.error('Erreur workflow d\'orchestration:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.get('/api/workflows', (req, res) => {
  try {
    const workflows = workflowManager.getAllWorkflows();
    res.json({ success: true, workflows });
  } catch (error) {
    console.error('Erreur récupération workflows:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Serveur backend écoutant sur le port ${port}`);
});

