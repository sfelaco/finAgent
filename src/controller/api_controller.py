from flask import Flask, request, jsonify, render_template
from typing import Dict, Any
import os
import logging
from dotenv import load_dotenv
from graph.graph import create_graph
from graph.state import GraphState
from langgraph.checkpoint.redis import RedisSaver
from langsmith import traceable

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Flask app with template directory
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

# Initialize the graph
graph = create_graph()

@app.route('/asset-analysis', methods=['GET'])
@traceable(name="invoke_asset_analysis")
def asset_analysis():
    """
    API endpoint for asset analysis
    
    Query Parameters:
    - thread_id (string, required): The thread identifier
    - asset (string, required): The asset to analyze
    
    Returns:
    - JSON response with analysis results or error message
    """
    try:
        # Get query parameters
        thread_id = request.args.get('thread_id')
        asset = request.args.get('asset')
        logger.info(f"/asset-analysis: {thread_id}:{asset}")
        
        # Validate required parameters
        if not thread_id:
            return render_template('error.html', 
                                 error_message='Missing required parameter: thread_id',
                                 status_code=400), 400
            
        if not asset:
            return render_template('error.html', 
                                 error_message='Missing required parameter: asset',
                                 status_code=400), 400
        
        logger.info(f"Starting asset analysis for asset: {asset}, thread_id: {thread_id}")
        
        # Get Redis connection parameters
        REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
        
        # Create checkpointer to access saved state
        with RedisSaver.from_conn_string(f"redis://{REDIS_HOST}:{REDIS_PORT}") as checkpointer:
            # Retrieve the current state from Redis using thread_id
            config = {"configurable": {"thread_id": thread_id}}
            
            try:
                # Get the saved state
                saved_state = checkpointer.get(config)
                
                if saved_state and saved_state.values:
                    # Use the existing state values
                    current_state = saved_state.values
                    logger.info(f"Retrieved existing state for thread_id: {thread_id}")
                else:
                    # Create initial state if no saved state exists
                    current_state = {
                        'rss_title': '',
                        'rss_link': '',
                        'documents': None,
                        'answer_language': 'en',
                        'news_scoring': None,
                        'thread_id': int(thread_id),
                        'asset_to_analyze': asset
                    }
                    logger.info(f"Created new state for thread_id: {thread_id}")
                
                # Update the asset_to_analyze field with the provided asset
                current_state['asset_to_analyze'] = asset
                current_state['thread_id'] = int(thread_id)
                
                # Use update_state to set the current state and start from HUMAN_FEEDBACK
                logger.info(f"Updating state and starting from HUMAN_FEEDBACK node")
                
                # Update the state in the graph
                graph.update_state(config, current_state, as_node="HUMAN_FEEDBACK")
                
            
                # Now invoke the graph to continue from HUMAN_FEEDBACK
                graph.ainvoke(None, config=config)
                
                logger.info(f"Graph execution completed successfully")
                
                # Return the HTML page with analysis progress message
                return render_template('analysis_progress.html', 
                                     asset=asset.upper(), 
                                     thread_id=thread_id)
                
            except Exception as e:
                logger.error(f"Error accessing Redis state: {str(e)}")
                return render_template('error.html', 
                                     error_message=f'Error accessing saved state: {str(e)}',
                                     status_code=500), 500
                
    except Exception as e:
        logger.error(f"Error in asset analysis: {str(e)}")
        return render_template('error.html', 
                             error_message=f'Internal server error: {str(e)}',
                             status_code=500), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return render_template('health.html')

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                         error_message='Endpoint not found',
                         status_code=404), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html', 
                         error_message='Internal server error',
                         status_code=500), 500

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
