import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Import components
from ceo_ai.agent import CEOAgent
from rag.system import RAGSystem
from mcu.server import MCUServer
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
rag_config = {
    'vector_db_host': Config.VECTOR_DB_HOST,
    'vector_db_port': Config.VECTOR_DB_PORT,
    'collection_name': Config.VECTOR_DB_COLLECTION,
    'model_endpoint': Config.RAG_MODEL_ENDPOINT 
    # Add other necessary RAG configs here
}
rag_system = RAGSystem(config=rag_config)

mcu_config = {
    'default_task_timeout': Config.TASK_TIMEOUT,
    'worker_timeout': Config.WORKER_TIMEOUT
    # Add other necessary MCU configs here (e.g., worker discovery mechanism)
}
mcu_server = MCUServer(config=mcu_config, socketio=socketio)

ceo_agent = CEOAgent(rag_system=rag_system, mcu_server=mcu_server)

# Register API routes
from api.routes import register_routes
register_routes(app, ceo_agent, rag_system, mcu_server)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "components": {
            "ceo_ai": "up",
            "rag": "up",
            "mcu": "up"
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# SocketIO events
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    mcu_server.register_client(request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")
    mcu_server.unregister_client(request.sid)

@socketio.on('worker_message')
def handle_worker_message(data):
    """Handle messages from worker AIs"""
    logger.info(f"Worker message received: {data}")
    mcu_server.handle_worker_message(data, request.sid)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AI Core on port {port}, debug={debug}")
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
