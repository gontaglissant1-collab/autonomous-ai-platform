import os
import sys
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# DON\"T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'frontend_build')) # Assuming frontend build will be here
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Microservices configuration
MICROSERVICES = {
    'planning-brain': 'http://localhost:5001',
    'tools-manager': 'http://localhost:5002', 
    'memory-service': 'http://localhost:5003'
}

# API Gateway routes for microservices
@app.route('/api/planning/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_planning(path):
    """Proxy requests to Planning Brain service"""
    try:
        url = f"{MICROSERVICES['planning-brain']}/api/{path}"
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return jsonify({'error': f'Planning service unavailable: {str(e)}'}), 503

@app.route('/api/tools/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_tools(path):
    """Proxy requests to Tools Manager service"""
    try:
        url = f"{MICROSERVICES['tools-manager']}/api/{path}"
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return jsonify({'error': f'Tools service unavailable: {str(e)}'}), 503

@app.route('/api/memory/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_memory(path):
    """Proxy requests to Memory service"""
    try:
        url = f"{MICROSERVICES['memory-service']}/api/{path}"
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )
        return response.content, response.status_code, response.headers.items()
    except Exception as e:
        return jsonify({'error': f'Memory service unavailable: {str(e)}'}), 503

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    services_status = {}
    for service_name, service_url in MICROSERVICES.items():
        try:
            response = requests.get(f"{service_url}/api/health", timeout=5)
            services_status[service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            services_status[service_name] = {
                'status': 'unavailable',
                'error': str(e)
            }
    
    return jsonify({
        'gateway': 'healthy',
        'services': services_status
    })

# Serve React Frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

