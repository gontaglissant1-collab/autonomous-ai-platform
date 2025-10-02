from flask import Blueprint, request, jsonify
import os
import json
import requests
from typing import List, Dict, Any
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

advanced_planning_bp = Blueprint('advanced_planning', __name__)

# Configuration
TOOLS_MANAGER_URL = "http://localhost:5002"
MEMORY_SERVICE_URL = "http://localhost:5003"

class PlanningCallbackHandler(BaseCallbackHandler):
    """Callback handler pour capturer les étapes de planification"""
    
    def __init__(self):
        self.steps = []
        self.thoughts = []
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> None:
        """Appelé quand l'agent prend une action"""
        self.steps.append({
            'type': 'action',
            'tool': action.tool,
            'tool_input': action.tool_input,
            'log': action.log
        })
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> None:
        """Appelé quand l'agent termine"""
        self.steps.append({
            'type': 'finish',
            'output': finish.return_values,
            'log': finish.log
        })

def create_tools():
    """Créer les outils disponibles pour l'agent"""
    
    def web_search(query: str) -> str:
        """Rechercher des informations sur le web"""
        try:
            response = requests.post(f"{TOOLS_MANAGER_URL}/api/search", 
                                   json={'query': query}, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return f"Résultats de recherche pour '{query}': {result.get('results', [])}"
            else:
                return f"Erreur de recherche: {response.text}"
        except Exception as e:
            return f"Erreur de connexion au service de recherche: {str(e)}"
    
    def execute_code(code: str) -> str:
        """Exécuter du code Python"""
        try:
            response = requests.post(f"{TOOLS_MANAGER_URL}/api/execute", 
                                   json={'code': code, 'language': 'python'}, timeout=60)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return f"Code exécuté avec succès:\n{result.get('stdout', '')}"
                else:
                    return f"Erreur d'exécution:\n{result.get('stderr', '')}"
            else:
                return f"Erreur du service d'exécution: {response.text}"
        except Exception as e:
            return f"Erreur de connexion au service d'exécution: {str(e)}"
    
    def generate_text(prompt: str) -> str:
        """Générer du texte avec Hugging Face"""
        try:
            response = requests.post(f"{TOOLS_MANAGER_URL}/api/generate/text", 
                                   json={'prompt': prompt}, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result.get('generated_text', 'Aucun texte généré')
            else:
                return f"Erreur de génération: {response.text}"
        except Exception as e:
            return f"Erreur de connexion au service de génération: {str(e)}"
    
    def retrieve_memory(query: str) -> str:
        """Récupérer des informations de la mémoire à long terme"""
        try:
            response = requests.post(f"{MEMORY_SERVICE_URL}/api/retrieve/experiences", 
                                   json={'query': query, 'limit': 3}, timeout=30)
            if response.status_code == 200:
                result = response.json()
                experiences = result.get('experiences', [])
                if experiences:
                    memory_text = "Expériences passées pertinentes:\n"
                    for exp in experiences:
                        memory_text += f"- Objectif: {exp.get('objective', '')}\n"
                        memory_text += f"  Résultat: {exp.get('results', '')}\n"
                        memory_text += f"  Succès: {exp.get('success', False)}\n\n"
                    return memory_text
                else:
                    return "Aucune expérience pertinente trouvée en mémoire"
            else:
                return f"Erreur d'accès à la mémoire: {response.text}"
        except Exception as e:
            return f"Erreur de connexion au service mémoire: {str(e)}"
    
    return [
        Tool(
            name="WebSearch",
            func=web_search,
            description="Utile pour rechercher des informations actuelles sur internet. Input: requête de recherche"
        ),
        Tool(
            name="CodeExecution", 
            func=execute_code,
            description="Utile pour exécuter du code Python et faire des calculs. Input: code Python à exécuter"
        ),
        Tool(
            name="TextGeneration",
            func=generate_text,
            description="Utile pour générer du texte créatif ou informatif. Input: prompt de génération"
        ),
        Tool(
            name="MemoryRetrieval",
            func=retrieve_memory,
            description="Utile pour récupérer des expériences passées similaires. Input: description de la tâche"
        )
    ]

@advanced_planning_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'advanced-planning'})

@advanced_planning_bp.route('/autonomous_plan', methods=['POST'])
    def create_autonomous_plan():
        """Créer un plan autonome avec LangChain"""
        try:
            data = request.get_json()
            objective = data.get("objective", "")
            context = data.get("context", "")
            
            if not objective:
                return jsonify({"error": "Objective is required"}), 400
            
            # Initialiser le LLM
            llm = ChatOpenAI(
                model="gpt-4.1-mini",
                temperature=0.7,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
            
        
        # Créer les outils
        tools = create_tools()
        
        # Initialiser la mémoire
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # Callback handler pour capturer les étapes
        callback_handler = PlanningCallbackHandler()
        
        # Initialiser l'agent
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            callbacks=[callback_handler],
            max_iterations=10,
            early_stopping_method="generate"
        )
        
        # Construire le prompt avec contexte
        full_prompt = f"""
        Objectif: {objective}
        
        Contexte additionnel: {context}
        
        Tu es un agent IA autonome expert en planification. Ton rôle est de:
        1. Analyser l'objectif et le contexte
        2. Décomposer la tâche en étapes logiques
        3. Utiliser les outils disponibles pour accomplir chaque étape
        4. Vérifier tes résultats et ajuster si nécessaire
        5. Fournir un plan détaillé et des résultats concrets
        
        Commence par récupérer des expériences similaires de ta mémoire, puis procède étape par étape.
        """
        
        # Exécuter l'agent
        result = agent.run(full_prompt)
        
        # Préparer la réponse
        plan_result = {
            'objective': objective,
            'context': context,
            'plan_result': result,
            'execution_steps': callback_handler.steps,
            'tools_used': list(set([step.get('tool', '') for step in callback_handler.steps if step.get('type') == 'action'])),
            'status': 'completed'
        }
        
        # Stocker l'expérience en mémoire
        try:
            memory_data = {
                'objective': objective,
                'plan': json.dumps(callback_handler.steps),
                'results': result,
                'success': True
            }
            requests.post(f"{MEMORY_SERVICE_URL}/api/store/experience", 
                         json=memory_data, timeout=30)
        except Exception as memory_error:
            print(f"Erreur lors du stockage en mémoire: {memory_error}")
        
        return jsonify(plan_result)
        
    except Exception as e:
        # Stocker l'échec en mémoire
        try:
            memory_data = {
                'objective': objective,
                'plan': '',
                'results': f'Erreur: {str(e)}',
                'success': False
            }
            requests.post(f"{MEMORY_SERVICE_URL}/api/store/experience", 
                         json=memory_data, timeout=30)
        except:
            pass
        
        return jsonify({'error': f'Planning failed: {str(e)}'}), 500

@advanced_planning_bp.route('/chain_of_thought', methods=['POST'])
    def chain_of_thought_planning():
        """Planification avec Chain-of-Thought reasoning"""
        try:
            data = request.get_json()
            objective = data.get("objective", "")
            
            if not objective:
                return jsonify({"error": "Objective is required"}), 400
            
            # Template pour Chain-of-Thought
            cot_template = """
            Tu es un expert en planification stratégique. Utilise la méthode Chain-of-Thought pour décomposer cet objectif.
            
            Objectif: {objective}
            
            Procède étape par étape:
            
            1. ANALYSE: Que demande exactement cet objectif? Quels sont les éléments clés?
            
            2. DÉCOMPOSITION: Quelles sont les étapes principales nécessaires?
            
            3. DÉPENDANCES: Quelles étapes dépendent d'autres étapes?
            
            4. OUTILS REQUIS: Quels outils ou ressources sont nécessaires pour chaque étape?
            
            5. PLAN D'ACTION: Séquence détaillée d'actions avec justifications
            
            6. CRITÈRES DE SUCCÈS: Comment savoir si chaque étape est réussie?
            
            Réponds en format JSON structuré avec ces sections.
            """
            
            # Initialiser le LLM
            llm = ChatOpenAI(
                model="gpt-4.1-mini",
                temperature=0.3,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
            
        
        # Créer la chaîne
        prompt = PromptTemplate(template=cot_template, input_variables=["objective"])
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Exécuter la chaîne
        result = chain.run(objective=objective)
        
        return jsonify({
            'objective': objective,
            'reasoning_method': 'chain_of_thought',
            'detailed_plan': result,
            'status': 'completed'
        })
        
    except Exception as e:
        return jsonify({'error': f'Chain-of-thought planning failed: {str(e)}'}), 500

@advanced_planning_bp.route('/multi_step_execution', methods=['POST'])
def multi_step_execution():
    """Exécution multi-étapes avec feedback"""
    try:
        data = request.get_json()
        steps = data.get('steps', [])
        
        if not steps:
            return jsonify({'error': 'Steps are required'}), 400
        
        execution_results = []
        
        for i, step in enumerate(steps):
            step_result = {
                'step_number': i + 1,
                'step_description': step.get('description', ''),
                'tool': step.get('tool', ''),
                'parameters': step.get('parameters', {}),
                'status': 'pending'
            }
            
            try:
                # Exécuter l'étape selon l'outil spécifié
                tool_name = step.get('tool', '')
                params = step.get('parameters', {})
                
                if tool_name == 'web_search':
                    response = requests.post(f"{TOOLS_MANAGER_URL}/api/search", 
                                           json={'query': params.get('query', '')}, timeout=30)
                elif tool_name == 'code_execution':
                    response = requests.post(f"{TOOLS_MANAGER_URL}/api/execute", 
                                           json={'code': params.get('code', ''), 'language': 'python'}, timeout=60)
                elif tool_name == 'text_generation':
                    response = requests.post(f"{TOOLS_MANAGER_URL}/api/generate/text", 
                                           json={'prompt': params.get('prompt', '')}, timeout=60)
                else:
                    step_result['status'] = 'error'
                    step_result['error'] = f'Unknown tool: {tool_name}'
                    execution_results.append(step_result)
                    continue
                
                if response.status_code == 200:
                    step_result['status'] = 'completed'
                    step_result['result'] = response.json()
                else:
                    step_result['status'] = 'error'
                    step_result['error'] = response.text
                    
            except Exception as e:
                step_result['status'] = 'error'
                step_result['error'] = str(e)
            
            execution_results.append(step_result)
            
            # Arrêter si une étape critique échoue
            if step_result['status'] == 'error' and step.get('critical', False):
                break
        
        return jsonify({
            'execution_results': execution_results,
            'total_steps': len(steps),
            'completed_steps': len([r for r in execution_results if r['status'] == 'completed']),
            'failed_steps': len([r for r in execution_results if r['status'] == 'error']),
            'overall_status': 'completed' if all(r['status'] == 'completed' for r in execution_results) else 'partial'
        })
        
    except Exception as e:
        return jsonify({'error': f'Multi-step execution failed: {str(e)}'}), 500

