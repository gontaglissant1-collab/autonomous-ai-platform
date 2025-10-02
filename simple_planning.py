from flask import Blueprint, request, jsonify
import os
import json
import requests
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

simple_planning_bp = Blueprint('simple_planning', __name__)

# Configuration
TOOLS_MANAGER_URL = "http://localhost:5002"
MEMORY_SERVICE_URL = "http://localhost:5003"

@simple_planning_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'simple-planning'})

@simple_planning_bp.route('/simple_plan', methods=['POST'])
def create_simple_plan():
    """Créer un plan simple avec décomposition d'objectif"""
    try:
        data = request.get_json()
        objective = data.get('objective', '')
        
        if not objective:
            return jsonify({'error': 'Objective is required'}), 400
        
        # Template de planification simple
        planning_template = """
        Tu es un expert en planification stratégique. Décompose cet objectif en étapes concrètes et réalisables.
        
        Objectif: {objective}
        
        Crée un plan structuré avec:
        1. Une analyse de l'objectif
        2. Les étapes principales (maximum 5 étapes)
        3. Pour chaque étape: description, outils nécessaires, critères de succès
        4. Les dépendances entre les étapes
        
        Réponds en format JSON avec cette structure:
        {{
            "analyse": "analyse de l'objectif",
            "etapes": [
                {{
                    "numero": 1,
                    "titre": "titre de l'étape",
                    "description": "description détaillée",
                    "outils_requis": ["outil1", "outil2"],
                    "criteres_succes": "comment mesurer le succès",
                    "dependances": []
                }}
            ],
            "estimation_duree": "estimation du temps total"
        }}
        """
        
        # Initialiser le LLM
        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        )
        
        
        # Créer le prompt
        prompt = PromptTemplate(template=planning_template, input_variables=["objective"])
        
        # Générer le plan
        chain = prompt | llm
        result = chain.invoke({"objective": objective})
        
        # Essayer de parser le JSON
        try:
            plan_json = json.loads(result.content)
        except json.JSONDecodeError:
            # Si le parsing JSON échoue, retourner le texte brut
            plan_json = {
                "analyse": "Plan généré en format texte",
                "plan_brut": result.content,
                "etapes": [],
                "estimation_duree": "Non spécifiée"
            }
        
        # Stocker l'expérience en mémoire
        try:
            memory_data = {
                'objective': objective,
                'plan': json.dumps(plan_json),
                'results': 'Plan créé avec succès',
                'success': True
            }
            requests.post(f"{MEMORY_SERVICE_URL}/api/store/experience", 
                         json=memory_data, timeout=30)
        except Exception as memory_error:
            print(f"Erreur lors du stockage en mémoire: {memory_error}")
        
        return jsonify({
            'objective': objective,
            'plan': plan_json,
            'status': 'completed',
            'method': 'simple_planning'
        })
        
    except Exception as e:
        return jsonify({'error': f'Simple planning failed: {str(e)}'}), 500

@simple_planning_bp.route('/execute_step', methods=['POST'])
def execute_single_step():
    """Exécuter une étape simple"""
    try:
        data = request.get_json()
        step = data.get('step', {})
        
        if not step:
            return jsonify({'error': 'Step is required'}), 400
        
        step_title = step.get('titre', step.get('title', 'Étape inconnue'))
        tools_required = step.get('outils_requis', step.get('tools_required', []))
        description = step.get('description', '')
        
        execution_results = []
        
        # Exécuter selon les outils requis
        for tool in tools_required:
            tool_result = {
                'tool': tool,
                'status': 'pending'
            }
            
            try:
                if tool.lower() in ['recherche_web', 'web_search', 'search']:
                    # Recherche web basée sur la description
                    response = requests.post(f"{TOOLS_MANAGER_URL}/api/search", 
                                           json={'query': description}, timeout=30)
                    if response.status_code == 200:
                        tool_result['status'] = 'completed'
                        tool_result['result'] = response.json()
                    else:
                        tool_result['status'] = 'error'
                        tool_result['error'] = response.text
                
                elif tool.lower() in ['generation_texte', 'text_generation']:
                    # Génération de texte
                    response = requests.post(f"{TOOLS_MANAGER_URL}/api/generate/text", 
                                           json={'prompt': f"Aide pour: {description}"}, timeout=60)
                    if response.status_code == 200:
                        tool_result['status'] = 'completed'
                        tool_result['result'] = response.json()
                    else:
                        tool_result['status'] = 'error'
                        tool_result['error'] = response.text
                
                else:
                    tool_result['status'] = 'simulated'
                    tool_result['result'] = f"Simulation de l'outil {tool} pour: {description}"
                    
            except Exception as e:
                tool_result['status'] = 'error'
                tool_result['error'] = str(e)
            
            execution_results.append(tool_result)
        
        return jsonify({
            'step_title': step_title,
            'description': description,
            'tools_executed': execution_results,
            'overall_status': 'completed' if all(r['status'] in ['completed', 'simulated'] for r in execution_results) else 'partial'
        })
        
    except Exception as e:
        return jsonify({'error': f'Step execution failed: {str(e)}'}), 500

@simple_planning_bp.route('/get_memory', methods=['POST'])
def get_relevant_memory():
    """Récupérer des expériences pertinentes de la mémoire"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Récupérer les expériences
        response = requests.post(f"{MEMORY_SERVICE_URL}/api/retrieve/experiences", 
                               json={'query': query, 'limit': 5}, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'error': f'Memory retrieval failed: {response.text}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Memory access failed: {str(e)}'}), 500

