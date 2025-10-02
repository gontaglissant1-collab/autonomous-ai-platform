import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Brain, Image, MessageSquare, Mic, Users, Zap, Settings, Play, Pause, Download } from 'lucide-react'
import './App.css'

// Composant Dashboard principal
function Dashboard() {
  const [agents, setAgents] = useState([])
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchAgents()
    fetchWorkflows()
  }, [])

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/agents')
      const data = await response.json()
      if (data.success) {
        setAgents(data.agents)
      }
    } catch (error) {
      console.error('Erreur récupération agents:', error)
    }
  }

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('http://localhost:3000/api/workflows')
      const data = await response.json()
      if (data.success) {
        setWorkflows(data.workflows)
      }
    } catch (error) {
      console.error('Erreur récupération workflows:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Brain className="h-10 w-10 text-purple-400" />
            OpenManus Unifié
          </h1>
          <p className="text-slate-300 text-lg">
            Plateforme d'agents IA autonomes avec intégration Hugging Face
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Agents Actifs</CardTitle>
              <Users className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{agents.length}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Workflows</CardTitle>
              <Zap className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{workflows.length}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Tâches Simultanées</CardTitle>
              <Play className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">10</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Modèles HF</CardTitle>
              <Brain className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">5</div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="agents" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800/50">
            <TabsTrigger value="agents" className="text-slate-200">Agents</TabsTrigger>
            <TabsTrigger value="workflows" className="text-slate-200">Workflows</TabsTrigger>
            <TabsTrigger value="multimodal" className="text-slate-200">Multimodal</TabsTrigger>
            <TabsTrigger value="settings" className="text-slate-200">Paramètres</TabsTrigger>
          </TabsList>

          <TabsContent value="agents" className="space-y-6">
            <AgentsPanel agents={agents} onRefresh={fetchAgents} />
          </TabsContent>

          <TabsContent value="workflows" className="space-y-6">
            <WorkflowsPanel workflows={workflows} onRefresh={fetchWorkflows} />
          </TabsContent>

          <TabsContent value="multimodal" className="space-y-6">
            <MultimodalPanel />
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <SettingsPanel />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

// Composant pour la gestion des agents
function AgentsPanel({ agents, onRefresh }) {
  const [newAgent, setNewAgent] = useState({ name: '', type: '', configuration: {} })
  const [loading, setLoading] = useState(false)

  const createAgent = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:3000/api/agents/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAgent)
      })
      const data = await response.json()
      if (data.success) {
        setNewAgent({ name: '', type: '', configuration: {} })
        onRefresh()
      }
    } catch (error) {
      console.error('Erreur création agent:', error)
    }
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Créer un Nouvel Agent</CardTitle>
          <CardDescription className="text-slate-300">
            Configurez un agent IA personnalisé avec des capacités spécifiques
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Nom de l'agent"
            value={newAgent.name}
            onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Input
            placeholder="Type d'agent (text_generation, image_generation, etc.)"
            value={newAgent.type}
            onChange={(e) => setNewAgent({ ...newAgent, type: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Button onClick={createAgent} disabled={loading} className="bg-purple-600 hover:bg-purple-700">
            {loading ? 'Création...' : 'Créer Agent'}
          </Button>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <Card key={agent.id} className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-400" />
                {agent.name}
              </CardTitle>
              <CardDescription className="text-slate-300">
                Type: {agent.type}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <Badge variant={agent.status === 'active' ? 'default' : 'secondary'}>
                  {agent.status}
                </Badge>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="border-slate-600 text-slate-200">
                    <Settings className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="outline" className="border-slate-600 text-slate-200">
                    <Play className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Composant pour la gestion des workflows
function WorkflowsPanel({ workflows, onRefresh }) {
  return (
    <div className="space-y-6">
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Workflows Disponibles</CardTitle>
          <CardDescription className="text-slate-300">
            Orchestrez des tâches complexes avec plusieurs agents
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button className="bg-blue-600 hover:bg-blue-700 h-20 flex flex-col">
              <Zap className="h-6 w-6 mb-2" />
              Contenu Multimodal
            </Button>
            <Button className="bg-green-600 hover:bg-green-700 h-20 flex flex-col">
              <MessageSquare className="h-6 w-6 mb-2" />
              Analyse de Contenu
            </Button>
            <Button className="bg-orange-600 hover:bg-orange-700 h-20 flex flex-col">
              <Users className="h-6 w-6 mb-2" />
              Création d'Agent
            </Button>
            <Button className="bg-purple-600 hover:bg-purple-700 h-20 flex flex-col">
              <Brain className="h-6 w-6 mb-2" />
              Orchestration
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Composant pour les fonctionnalités multimodales
function MultimodalPanel() {
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const generateContent = async (type) => {
    setLoading(true)
    try {
      let endpoint = ''
      let body = {}

      switch (type) {
        case 'text':
          endpoint = '/api/text/generate'
          body = { prompt }
          break
        case 'image':
          endpoint = '/api/image/generate'
          body = { prompt }
          break
        case 'audio':
          endpoint = '/api/audio/synthesize'
          body = { text: prompt }
          break
        case 'multimodal':
          endpoint = '/api/workflows/multimodal'
          body = { prompt }
          break
      }

      const response = await fetch(`http://localhost:3000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Erreur génération:', error)
    }
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Génération Multimodale</CardTitle>
          <CardDescription className="text-slate-300">
            Générez du contenu texte, image et audio avec les modèles Hugging Face
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Entrez votre prompt ici..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="bg-slate-700 border-slate-600 text-white min-h-[100px]"
          />
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button 
              onClick={() => generateContent('text')} 
              disabled={loading || !prompt}
              className="bg-blue-600 hover:bg-blue-700 flex flex-col h-16"
            >
              <MessageSquare className="h-5 w-5 mb-1" />
              Texte
            </Button>
            <Button 
              onClick={() => generateContent('image')} 
              disabled={loading || !prompt}
              className="bg-green-600 hover:bg-green-700 flex flex-col h-16"
            >
              <Image className="h-5 w-5 mb-1" />
              Image
            </Button>
            <Button 
              onClick={() => generateContent('audio')} 
              disabled={loading || !prompt}
              className="bg-orange-600 hover:bg-orange-700 flex flex-col h-16"
            >
              <Mic className="h-5 w-5 mb-1" />
              Audio
            </Button>
            <Button 
              onClick={() => generateContent('multimodal')} 
              disabled={loading || !prompt}
              className="bg-purple-600 hover:bg-purple-700 flex flex-col h-16"
            >
              <Zap className="h-5 w-5 mb-1" />
              Tout
            </Button>
          </div>

          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400 mx-auto"></div>
              <p className="text-slate-300 mt-2">Génération en cours...</p>
            </div>
          )}

          {result && (
            <Card className="bg-slate-700/50 border-slate-600">
              <CardHeader>
                <CardTitle className="text-white">Résultat</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-slate-200 text-sm overflow-auto">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// Composant pour les paramètres
function SettingsPanel() {
  return (
    <div className="space-y-6">
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Configuration Hugging Face</CardTitle>
          <CardDescription className="text-slate-300">
            Configurez vos clés API et modèles préférés
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Clé API Hugging Face"
            type="password"
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Input
            placeholder="Modèle de texte par défaut"
            defaultValue="microsoft/DialoGPT-medium"
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Input
            placeholder="Modèle d'image par défaut"
            defaultValue="stabilityai/stable-diffusion-2-1"
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Button className="bg-purple-600 hover:bg-purple-700">
            Sauvegarder Configuration
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </Router>
  )
}

export default App
