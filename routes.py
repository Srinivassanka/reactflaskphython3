import json
import logging
import traceback
from flask import request, jsonify, render_template
from app import app
import momentumnifty100

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

@app.route('/api/momentum-analysis')
def momentum_analysis():
    """
    Run the Nifty 100 momentum analysis and return the results.
    """
    try:
        logger.info("Starting momentum analysis")
        # Set a longer timeout for this request as it may take time to fetch data
        results = momentumnifty100.get_momentum_data()
        logger.debug("Momentum analysis completed successfully")
        
        # Check if there's an error in the results
        if "error" in results:
            logger.warning(f"Momentum analysis returned with error: {results['error']}")
            # Still return 200 status since we have partial data
            return jsonify(results)
            
        return jsonify(results)
    except Exception as e:
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"Error in momentum analysis: {error_message}\n{stack_trace}")
        return jsonify({"error": error_message}), 500

@app.route('/api/momentum-durations')
def momentum_durations():
    """Get available durations for momentum analysis."""
    return jsonify({
        "durations": ["5d", "10d", "1mo", "3mo", "6mo", "1y"]
    })

@app.route('/api/health')
def health_check():
    """API health check endpoint."""
    return jsonify({"status": "ok"})
