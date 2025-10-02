from flask import Blueprint, request, jsonify
import os
import json
import sqlite3
from datetime import datetime
import hashlib

memory_bp = Blueprint('memory', __name__)

# Database path for memory storage
MEMORY_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'memory.db')

def init_memory_db():
    """Initialize the memory database"""
    conn = sqlite3.connect(MEMORY_DB_PATH)
    cursor = conn.cursor()
    
    # Create experiences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objective TEXT NOT NULL,
            task_description TEXT,
            plan TEXT,
            actions TEXT,
            results TEXT,
            success BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            embedding_vector TEXT,
            keywords TEXT
        )
    ''')
    
    # Create knowledge table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            embedding_vector TEXT,
            keywords TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on import
init_memory_db()

@memory_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'memory-service'})

@memory_bp.route('/store/experience', methods=['POST'])
def store_experience():
    """Store an experience in long-term memory"""
    try:
        data = request.get_json()
        objective = data.get("objective", "")
        task_description = data.get("task_description", "")
        plan = data.get("plan", "")
        actions = data.get("actions", [])
        results = data.get("results", "")
        success = data.get("success", False)
        
        if not objective:
            return jsonify({"error": "Objective is required"}), 400
        
        # Simulate embedding vector and keyword extraction
        experience_text = f"{objective} {task_description} {plan} {json.dumps(actions)} {results}"
        embedding_vector = hashlib.sha256(experience_text.encode()).hexdigest() # Placeholder for actual embedding
        keywords = ", ".join(sorted(list(set(word.lower() for word in experience_text.split() if len(word) > 2)))) # Simple keyword extraction
        
        conn = sqlite3.connect(MEMORY_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO experiences (objective, task_description, plan, actions, results, success, embedding_vector, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (objective, task_description, plan, json.dumps(actions), results, success, embedding_vector, keywords))
        
        experience_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "id": experience_id,
            "status": "stored",
            "embedding_vector": embedding_vector,
            "keywords": keywords
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to store experience: {str(e)}"}), 500

@memory_bp.route('/store/knowledge', methods=['POST'])
def store_knowledge():
    """Store knowledge in long-term memory"""
    try:
        data = request.get_json()
        topic = data.get('topic', '')
        content = data.get('content', '')
        source = data.get('source', '')
        
        if not topic or not content:
            return jsonify({'error': 'Topic and content are required'}), 400
        
        # Create a simple hash for the knowledge (in real implementation, use embeddings)
        knowledge_text = f"{topic} {content}"
        embedding_vector = hashlib.sha256(knowledge_text.encode()).hexdigest() # Placeholder for actual embedding
        keywords = ", ".join(sorted(list(set(word.lower() for word in knowledge_text.split() if len(word) > 2)))) # Simple keyword extraction
        
        conn = sqlite3.connect(MEMORY_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO knowledge (topic, content, source, embedding_vector, keywords)
            VALUES (?, ?, ?, ?, ?)
        """, (topic, content, source, embedding_vector, keywords))
        
        knowledge_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "id": knowledge_id,
            "status": "stored",
            "embedding_vector": embedding_vector,
            "keywords": keywords
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to store knowledge: {str(e)}'}), 500

@memory_bp.route('/retrieve/experiences', methods=['POST'])
def retrieve_experiences():
    """Retrieve similar experiences from memory"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        conn = sqlite3.connect(MEMORY_DB_PATH)
        cursor = conn.cursor()
        
        # Advanced text-based search using keywords and objective/task_description
        # In a real implementation, this would involve vector similarity search
        cursor.execute("""
            SELECT id, objective, task_description, plan, actions, results, success, timestamp, embedding_vector, keywords
            FROM experiences
            WHERE objective LIKE ? OR task_description LIKE ? OR keywords LIKE ? OR plan LIKE ? OR results LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        experiences = []
        for row in cursor.fetchall():
            experiences.append({
                'id': row[0],
                'objective': row[1],
                'task_description': row[2],
                'plan': row[3],
                'actions': json.loads(row[4]) if row[4] else [],
                'results': row[5],
                'success': bool(row[6]),
                'timestamp': row[7],
                'embedding_vector': row[8],
                'keywords': row[9]
            })
        
        conn.close()
        
        return jsonify({
            'query': query,
            'experiences': experiences,
            'count': len(experiences)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve experiences: {str(e)}'}), 500

@memory_bp.route('/retrieve/knowledge', methods=['POST'])
def retrieve_knowledge():
    """Retrieve relevant knowledge from memory"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        conn = sqlite3.connect(MEMORY_DB_PATH)
        cursor = conn.cursor()
        
        # Advanced text-based search using keywords and topic/content
        # In a real implementation, this would involve vector similarity search
        cursor.execute("""
            SELECT id, topic, content, source, timestamp, embedding_vector, keywords
            FROM knowledge
            WHERE topic LIKE ? OR content LIKE ? OR keywords LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        knowledge_items = []
        for row in cursor.fetchall():
            knowledge_items.append({
                'id': row[0],
                'topic': row[1],
                'content': row[2],
                'source': row[3],
                'timestamp': row[4],
                'embedding_vector': row[5],
                'keywords': row[6]
            })
        
        conn.close()
        
        return jsonify({
            'query': query,
            'knowledge': knowledge_items,
            'count': len(knowledge_items)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve knowledge: {str(e)}'}), 500

@memory_bp.route('/stats', methods=['GET'])
def memory_stats():
    """Get memory statistics"""
    try:
        conn = sqlite3.connect(MEMORY_DB_PATH)
        cursor = conn.cursor()
        
        # Count experiences
        cursor.execute('SELECT COUNT(*) FROM experiences')
        experience_count = cursor.fetchone()[0]
        
        # Count knowledge items
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        knowledge_count = cursor.fetchone()[0]
        
        # Count successful experiences
        cursor.execute('SELECT COUNT(*) FROM experiences WHERE success = 1')
        successful_experiences = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'experiences': {
                'total': experience_count,
                'successful': successful_experiences,
                'success_rate': successful_experiences / experience_count if experience_count > 0 else 0
            },
            'knowledge': {
                'total': knowledge_count
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get memory stats: {str(e)}'}), 500

