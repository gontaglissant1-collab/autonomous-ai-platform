from flask import Blueprint, request, jsonify
import os
import openai

planning_bp = Blueprint('planning', __name__)

# Configuration OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')

@planning_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'planning-brain'})

@planning_bp.route('/plan', methods=['POST'])
def create_plan():
    """Create a plan from a high-level objective"""
    try:
        data = request.get_json()
        objective = data.get('objective', '')
        
        if not objective:
            return jsonify({'error': 'Objective is required'}), 400
        
        # Use OpenAI to decompose the objective into actionable steps
        prompt = f"""
        Tu es un agent IA expert en planification. Ton rôle est de décomposer un objectif complexe en étapes concrètes et exécutables.
        
        Objectif: {objective}
        
        Décompose cet objectif en étapes spécifiques et ordonnées. Pour chaque étape, indique:
        1. Description de l'action
        2. Outils nécessaires (recherche_web, generation_image, generation_texte, execution_code, etc.)
        3. Dépendances (quelles étapes doivent être terminées avant)
        4. Critères de succès
        
        Réponds au format JSON avec une liste d'étapes.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en planification d'agents IA autonomes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        plan_content = response.choices[0].message.content
        
        # Store the plan (for now, just return it)
        plan_result = {
            'objective': objective,
            'plan': plan_content,
            'status': 'created'
        }
        
        return jsonify(plan_result)
        
    except Exception as e:
        return jsonify({'error': f'Planning failed: {str(e)}'}), 500

@planning_bp.route('/execute', methods=['POST'])
def execute_step():
    """Execute a specific step of the plan"""
    try:
        data = request.get_json()
        step = data.get('step', {})
        
        if not step:
            return jsonify({'error': 'Step is required'}), 400
        
        # For now, simulate step execution
        result = {
            'step_id': step.get('id', 'unknown'),
            'status': 'executed',
            'result': 'Step executed successfully (simulated)',
            'next_action': 'proceed_to_next_step'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Execution failed: {str(e)}'}), 500

@planning_bp.route('/reflect', methods=['POST'])
def reflect_on_result():
    """Reflect on the result of an action and adjust the plan if needed"""
    try:
        data = request.get_json()
        result = data.get('result', {})
        original_plan = data.get('plan', {})
        
        # Use OpenAI to analyze the result and suggest adjustments
        prompt = f"""
        Analyse le résultat de cette action et détermine si le plan doit être ajusté.
        
        Plan original: {original_plan}
        Résultat obtenu: {result}
        
        Questions à considérer:
        1. L'action a-t-elle réussi?
        2. Le résultat nous rapproche-t-il de l'objectif?
        3. Faut-il ajuster les prochaines étapes?
        4. Y a-t-il des erreurs à corriger?
        
        Réponds avec une recommandation d'action: "continue", "adjust_plan", ou "retry_step".
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en auto-correction d'agents IA."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        reflection = response.choices[0].message.content
        
        reflection_result = {
            'reflection': reflection,
            'recommendation': 'continue',  # Parse from reflection
            'adjusted_plan': original_plan  # Would be modified based on reflection
        }
        
        return jsonify(reflection_result)
        
    except Exception as e:
        return jsonify({'error': f'Reflection failed: {str(e)}'}), 500

