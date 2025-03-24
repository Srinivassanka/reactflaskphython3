import json
import logging
from flask import request, jsonify, render_template
from app import app

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Render the main page."""
    logger.debug("Rendering index page")
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_data():
    """
    Process data received from the frontend.
    
    Expected JSON format:
    {
        "text": "string to process",
        "operation": "uppercase|lowercase|reverse|wordcount"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        text = data.get('text', '')
        operation = data.get('operation', '')
        
        logger.debug(f"Processing data: text='{text}', operation='{operation}'")
        
        result = None
        
        if operation == 'uppercase':
            result = text.upper()
        elif operation == 'lowercase':
            result = text.lower()
        elif operation == 'reverse':
            result = text[::-1]
        elif operation == 'wordcount':
            result = len(text.split())
        else:
            return jsonify({"error": f"Unknown operation: {operation}"}), 400
        
        return jsonify({
            "original": text,
            "operation": operation,
            "result": result
        })
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    """API health check endpoint."""
    return jsonify({"status": "ok"})
