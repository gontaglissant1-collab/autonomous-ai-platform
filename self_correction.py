from flask import Blueprint, request, jsonify
import requests
import json
import os
from datetime import datetime
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

self_correction_bp = Blueprint('self_correction', __name__)

# Initialize OpenAI LLM
llm = OpenAI(
    model_name="gpt-4o-mini",
    temperature=0.3,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

@self_correction_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'self-correction'})

@self_correction_bp.route('/evaluate_result', methods=['POST'])
def evaluate_result():
    """Evaluate the result of a task execution and determine if correction is needed"""
    try:
        data = request.get_json()
        objective = data.get('objective', '')
        plan = data.get('plan', '')
        actions_taken = data.get('actions_taken', [])
        result = data.get('result', '')
        expected_outcome = data.get('expected_outcome', '')
        
        if not objective or not result:
            return jsonify({'error': 'Objective and result are required'}), 400
        
        # Create evaluation prompt
        evaluation_prompt = PromptTemplate(
            input_variables=["objective", "plan", "actions_taken", "result", "expected_outcome"],
            template="""
            Évaluez l'exécution de cette tâche et déterminez si une correction est nécessaire.

            Objectif: {objective}
            Plan: {plan}
            Actions prises: {actions_taken}
            Résultat obtenu: {result}
            Résultat attendu: {expected_outcome}

            Analysez:
            1. Le résultat correspond-il à l'objectif?
            2. Y a-t-il des erreurs ou des problèmes?
            3. Que pourrait-on améliorer?
            4. Une correction est-elle nécessaire?

            Répondez au format JSON:
            {{
                "success": true/false,
                "quality_score": 0-100,
                "issues_identified": ["liste des problèmes"],
                "correction_needed": true/false,
                "improvement_suggestions": ["liste des améliorations"],
                "reasoning": "explication détaillée"
            }}
            """
        )
        
        # Create evaluation chain
        evaluation_chain = LLMChain(llm=llm, prompt=evaluation_prompt)
        
        # Run evaluation
        evaluation_result = evaluation_chain.run(
            objective=objective,
            plan=plan,
            actions_taken=json.dumps(actions_taken),
            result=result,
            expected_outcome=expected_outcome
        )
        
        try:
            # Parse JSON response
            evaluation_data = json.loads(evaluation_result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            evaluation_data = {
                "success": False,
                "quality_score": 50,
                "issues_identified": ["Erreur d'analyse"],
                "correction_needed": True,
                "improvement_suggestions": ["Réessayer avec une approche différente"],
                "reasoning": "Impossible d'analyser le résultat correctement"
            }
        
        # Store evaluation in memory
        memory_data = {
            "objective": objective,
            "task_description": f"Évaluation de: {objective}",
            "plan": plan,
            "actions": actions_taken,
            "results": f"Score: {evaluation_data.get('quality_score', 0)}/100. {evaluation_data.get('reasoning', '')}",
            "success": evaluation_data.get('success', False)
        }
        
        try:
            requests.post(
                'http://localhost:5003/api/store/experience',
                json=memory_data,
                timeout=10
            )
        except:
            pass  # Continue even if memory storage fails
        
        return jsonify({
            'evaluation': evaluation_data,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        })
        
    except Exception as e:
        return jsonify({'error': f'Evaluation failed: {str(e)}'}), 500

@self_correction_bp.route('/generate_correction', methods=['POST'])
def generate_correction():
    """Generate a corrected plan based on identified issues"""
    try:
        data = request.get_json()
        original_objective = data.get('original_objective', '')
        original_plan = data.get('original_plan', '')
        issues_identified = data.get('issues_identified', [])
        previous_result = data.get('previous_result', '')
        
        if not original_objective or not issues_identified:
            return jsonify({'error': 'Original objective and issues are required'}), 400
        
        # Create correction prompt
        correction_prompt = PromptTemplate(
            input_variables=["objective", "original_plan", "issues", "previous_result"],
            template="""
            Générez un plan corrigé pour atteindre cet objectif, en tenant compte des problèmes identifiés.

            Objectif original: {objective}
            Plan original: {original_plan}
            Problèmes identifiés: {issues}
            Résultat précédent: {previous_result}

            Créez un nouveau plan qui:
            1. Corrige les problèmes identifiés
            2. Utilise une approche différente si nécessaire
            3. Inclut des étapes de vérification
            4. Apprend des erreurs précédentes

            Répondez au format JSON:
            {{
                "corrected_plan": {{
                    "objective": "objectif clarifié",
                    "strategy": "nouvelle stratégie",
                    "steps": [
                        {{
                            "step": 1,
                            "action": "action à effectuer",
                            "tool": "outil à utiliser",
                            "verification": "comment vérifier le succès"
                        }}
                    ],
                    "risk_mitigation": ["mesures préventives"],
                    "success_criteria": ["critères de réussite"]
                }},
                "changes_made": ["liste des changements par rapport au plan original"],
                "reasoning": "explication des corrections apportées"
            }}
            """
        )
        
        # Create correction chain
        correction_chain = LLMChain(llm=llm, prompt=correction_prompt)
        
        # Run correction
        correction_result = correction_chain.run(
            objective=original_objective,
            original_plan=original_plan,
            issues=json.dumps(issues_identified),
            previous_result=previous_result
        )
        
        try:
            # Parse JSON response
            correction_data = json.loads(correction_result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            correction_data = {
                "corrected_plan": {
                    "objective": original_objective,
                    "strategy": "Approche alternative",
                    "steps": [
                        {
                            "step": 1,
                            "action": "Réanalyser l'objectif",
                            "tool": "planning",
                            "verification": "Vérifier la clarté de l'objectif"
                        }
                    ],
                    "risk_mitigation": ["Validation à chaque étape"],
                    "success_criteria": ["Objectif atteint"]
                },
                "changes_made": ["Plan simplifié"],
                "reasoning": "Correction automatique appliquée"
            }
        
        # Store correction in memory
        memory_data = {
            "objective": f"Correction de: {original_objective}",
            "task_description": "Génération d'un plan corrigé",
            "plan": json.dumps(correction_data.get('corrected_plan', {})),
            "actions": ["Analyse des erreurs", "Génération de corrections"],
            "results": f"Plan corrigé généré. Changements: {', '.join(correction_data.get('changes_made', []))}",
            "success": True
        }
        
        try:
            requests.post(
                'http://localhost:5003/api/store/experience',
                json=memory_data,
                timeout=10
            )
        except:
            pass  # Continue even if memory storage fails
        
        return jsonify({
            'correction': correction_data,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        })
        
    except Exception as e:
        return jsonify({'error': f'Correction generation failed: {str(e)}'}), 500

@self_correction_bp.route('/learn_from_experience', methods=['POST'])
def learn_from_experience():
    """Learn patterns from past experiences to improve future performance"""
    try:
        data = request.get_json()
        task_type = data.get('task_type', 'general')
        limit = data.get('limit', 10)
        
        # Retrieve similar experiences from memory
        try:
            memory_response = requests.post(
                'http://localhost:5003/api/retrieve/experiences',
                json={'query': task_type, 'limit': limit},
                timeout=10
            )
            experiences = memory_response.json().get('experiences', [])
        except:
            experiences = []
        
        if not experiences:
            return jsonify({
                'patterns': [],
                'recommendations': ['Pas assez d\'expériences pour identifier des patterns'],
                'status': 'insufficient_data'
            })
        
        # Analyze experiences to identify patterns
        learning_prompt = PromptTemplate(
            input_variables=["experiences"],
            template="""
            Analysez ces expériences passées pour identifier des patterns et des leçons apprises.

            Expériences: {experiences}

            Identifiez:
            1. Les stratégies qui fonctionnent le mieux
            2. Les erreurs communes à éviter
            3. Les outils les plus efficaces
            4. Les patterns de succès et d'échec

            Répondez au format JSON:
            {{
                "patterns_identified": [
                    {{
                        "pattern": "description du pattern",
                        "frequency": "fréquence d'occurrence",
                        "success_rate": "taux de réussite",
                        "context": "contexte d'application"
                    }}
                ],
                "best_practices": ["liste des meilleures pratiques"],
                "common_mistakes": ["erreurs communes à éviter"],
                "tool_effectiveness": {{
                    "most_effective": ["outils les plus efficaces"],
                    "least_effective": ["outils les moins efficaces"]
                }},
                "recommendations": ["recommandations pour l'avenir"]
            }}
            """
        )
        
        # Create learning chain
        learning_chain = LLMChain(llm=llm, prompt=learning_prompt)
        
        # Run learning analysis
        learning_result = learning_chain.run(
            experiences=json.dumps(experiences[:5])  # Limit to avoid token limits
        )
        
        try:
            # Parse JSON response
            learning_data = json.loads(learning_result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            learning_data = {
                "patterns_identified": [],
                "best_practices": ["Continuer à apprendre des expériences"],
                "common_mistakes": ["Ne pas analyser les résultats"],
                "tool_effectiveness": {
                    "most_effective": ["planning", "memory"],
                    "least_effective": []
                },
                "recommendations": ["Améliorer l'analyse des patterns"]
            }
        
        # Store learning insights in memory as knowledge
        knowledge_data = {
            "topic": f"Apprentissage - {task_type}",
            "content": json.dumps(learning_data),
            "source": "auto-learning"
        }
        
        try:
            requests.post(
                'http://localhost:5003/api/store/knowledge',
                json=knowledge_data,
                timeout=10
            )
        except:
            pass  # Continue even if memory storage fails
        
        return jsonify({
            'learning_insights': learning_data,
            'experiences_analyzed': len(experiences),
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        })
        
    except Exception as e:
        return jsonify({'error': f'Learning failed: {str(e)}'}), 500

@self_correction_bp.route('/adaptive_retry', methods=['POST'])
def adaptive_retry():
    """Adaptively retry a failed task with improved strategy"""
    try:
        data = request.get_json()
        original_objective = data.get('original_objective', '')
        failure_reason = data.get('failure_reason', '')
        attempt_number = data.get('attempt_number', 1)
        max_attempts = data.get('max_attempts', 3)
        
        if not original_objective:
            return jsonify({'error': 'Original objective is required'}), 400
        
        if attempt_number >= max_attempts:
            return jsonify({
                'retry_plan': None,
                'should_retry': False,
                'reason': 'Maximum attempts reached',
                'status': 'max_attempts_exceeded'
            })
        
        # Learn from similar failures
        try:
            memory_response = requests.post(
                'http://localhost:5003/api/retrieve/experiences',
                json={'query': f"{original_objective} échec", 'limit': 5},
                timeout=10
            )
            similar_failures = memory_response.json().get('experiences', [])
        except:
            similar_failures = []
        
        # Generate adaptive retry strategy
        retry_prompt = PromptTemplate(
            input_variables=["objective", "failure_reason", "attempt_number", "similar_failures"],
            template="""
            Générez une stratégie de nouvelle tentative adaptative pour cet objectif qui a échoué.

            Objectif: {objective}
            Raison de l'échec: {failure_reason}
            Tentative numéro: {attempt_number}
            Échecs similaires: {similar_failures}

            Créez une stratégie qui:
            1. Adresse spécifiquement la raison de l'échec
            2. Utilise une approche différente
            3. Inclut des mesures préventives
            4. Apprend des échecs similaires

            Répondez au format JSON:
            {{
                "should_retry": true/false,
                "retry_strategy": {{
                    "approach": "nouvelle approche",
                    "modifications": ["changements par rapport à la tentative précédente"],
                    "preventive_measures": ["mesures pour éviter le même échec"],
                    "success_indicators": ["indicateurs de réussite à surveiller"]
                }},
                "estimated_success_probability": 0-100,
                "reasoning": "explication de la stratégie"
            }}
            """
        )
        
        # Create retry chain
        retry_chain = LLMChain(llm=llm, prompt=retry_prompt)
        
        # Run retry analysis
        retry_result = retry_chain.run(
            objective=original_objective,
            failure_reason=failure_reason,
            attempt_number=attempt_number,
            similar_failures=json.dumps(similar_failures[:3])
        )
        
        try:
            # Parse JSON response
            retry_data = json.loads(retry_result)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            retry_data = {
                "should_retry": True,
                "retry_strategy": {
                    "approach": "Approche simplifiée",
                    "modifications": ["Simplifier l'objectif"],
                    "preventive_measures": ["Validation à chaque étape"],
                    "success_indicators": ["Progression mesurable"]
                },
                "estimated_success_probability": 60,
                "reasoning": "Stratégie de fallback appliquée"
            }
        
        return jsonify({
            'retry_plan': retry_data,
            'attempt_number': attempt_number + 1,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        })
        
    except Exception as e:
        return jsonify({'error': f'Adaptive retry failed: {str(e)}'}), 500

