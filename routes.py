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
        # Create a fallback structure
        fallback_results = {
            "error": "Unable to complete analysis",
            "comparison": {
                "dropped_from_top_10": [],
                "entered_top_10": [],
                "full_5d_top_10": [],
                "full_3mo_top_10": []
            }
        }
        
        durations = ["5d", "10d", "1mo", "3mo", "6mo", "1y"]
        for duration in durations:
            fallback_results[duration] = {
                "top_performers": {"Error": 0},
                "bottom_performers": {"Error": 0}
            }
        
        try:
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
            logger.error(f"Error in get_momentum_data: {error_message}\n{stack_trace}")
            fallback_results["error"] = f"Error processing data: {error_message}"
            return jsonify(fallback_results)
            
    except Exception as e:
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"Error in momentum analysis route: {error_message}\n{stack_trace}")
        return jsonify({
            "error": f"Server error: {error_message}",
            "comparison": {"dropped_from_top_10": [], "entered_top_10": [], "full_5d_top_10": [], "full_3mo_top_10": []},
            "5d": {"top_performers": {"Error": 0}, "bottom_performers": {"Error": 0}},
            "10d": {"top_performers": {"Error": 0}, "bottom_performers": {"Error": 0}},
            "1mo": {"top_performers": {"Error": 0}, "bottom_performers": {"Error": 0}},
            "3mo": {"top_performers": {"Error": 0}, "bottom_performers": {"Error": 0}},
            "6mo": {"top_performers": {"Error": 0}, "bottom_performers": {"Error": 0}},
            "1y": {"top_performers": {"Error": 0}, "bottom_performers": {"Error": 0}}
        })

@app.route('/api/test-data')
def test_data():
    """Test endpoint that always returns valid data"""
    # Create more comprehensive test data with proper sorting order (highest to lowest for top, lowest to highest for bottom)
    top_performers_5d = {
        "TESTSTOCK1.NS": 15.3,
        "TESTSTOCK2.NS": 12.7,
        "TESTSTOCK3.NS": 9.8,
        "TESTSTOCK4.NS": 8.5,
        "TESTSTOCK5.NS": 7.6,
        "TESTSTOCK6.NS": 6.9,
        "TESTSTOCK7.NS": 5.3,
        "TESTSTOCK8.NS": 4.2,
        "TESTSTOCK9.NS": 3.4,
        "TESTSTOCK10.NS": 2.8
    }
    
    bottom_performers_5d = {
        "TESTSTOCK11.NS": -12.5,
        "TESTSTOCK12.NS": -10.8,
        "TESTSTOCK13.NS": -8.7,
        "TESTSTOCK14.NS": -7.3,
        "TESTSTOCK15.NS": -6.2,
        "TESTSTOCK16.NS": -5.1,
        "TESTSTOCK17.NS": -4.3,
        "TESTSTOCK18.NS": -3.6,
        "TESTSTOCK19.NS": -2.8,
        "TESTSTOCK20.NS": -2.1
    }
    
    # Generate similar data for other time periods with slight variations
    results = {
        "status": "ok",
        "test_data": True,
        "message": "This is a test endpoint that always returns valid data regardless of Yahoo Finance API status",
        "comparison": {
            "dropped_from_top_10": ["TESTSTOCK6.NS", "TESTSTOCK7.NS", "TESTSTOCK8.NS"],
            "entered_top_10": ["TESTSTOCK31.NS", "TESTSTOCK32.NS", "TESTSTOCK33.NS"],
            "full_5d_top_10": list(top_performers_5d.keys()),
            "full_3mo_top_10": ["TESTSTOCK1.NS", "TESTSTOCK2.NS", "TESTSTOCK3.NS", 
                              "TESTSTOCK4.NS", "TESTSTOCK5.NS", "TESTSTOCK31.NS", 
                              "TESTSTOCK32.NS", "TESTSTOCK33.NS", "TESTSTOCK9.NS", "TESTSTOCK10.NS"]
        }
    }
    
    # 5d data (already defined above)
    results["5d"] = {
        "top_performers": top_performers_5d,
        "bottom_performers": bottom_performers_5d
    }
    
    # 10d data (slight variation from 5d)
    results["10d"] = {
        "top_performers": {k: v * 0.9 for k, v in top_performers_5d.items()},
        "bottom_performers": {k: v * 0.85 for k, v in bottom_performers_5d.items()}
    }
    
    # 1mo data
    results["1mo"] = {
        "top_performers": {
            "TESTSTOCK1.NS": 22.7,
            "TESTSTOCK2.NS": 19.5,
            "TESTSTOCK3.NS": 16.8,
            "TESTSTOCK31.NS": 15.1,
            "TESTSTOCK32.NS": 13.9,
            "TESTSTOCK33.NS": 12.4,
            "TESTSTOCK4.NS": 11.3,
            "TESTSTOCK5.NS": 10.2,
            "TESTSTOCK9.NS": 9.1,
            "TESTSTOCK10.NS": 8.5
        },
        "bottom_performers": {
            "TESTSTOCK11.NS": -18.3,
            "TESTSTOCK12.NS": -16.7,
            "TESTSTOCK13.NS": -14.9,
            "TESTSTOCK14.NS": -12.8,
            "TESTSTOCK15.NS": -10.6,
            "TESTSTOCK16.NS": -9.3,
            "TESTSTOCK17.NS": -8.2,
            "TESTSTOCK18.NS": -7.1,
            "TESTSTOCK19.NS": -6.3,
            "TESTSTOCK20.NS": -5.2
        }
    }
    
    # 3mo data
    results["3mo"] = {
        "top_performers": {
            "TESTSTOCK1.NS": 35.8,
            "TESTSTOCK2.NS": 32.6,
            "TESTSTOCK3.NS": 29.7,
            "TESTSTOCK31.NS": 27.3,
            "TESTSTOCK32.NS": 25.8,
            "TESTSTOCK33.NS": 22.9,
            "TESTSTOCK4.NS": 20.5,
            "TESTSTOCK5.NS": 18.7,
            "TESTSTOCK9.NS": 16.4,
            "TESTSTOCK10.NS": 14.2
        },
        "bottom_performers": {
            "TESTSTOCK11.NS": -25.7,
            "TESTSTOCK12.NS": -23.2,
            "TESTSTOCK13.NS": -21.1,
            "TESTSTOCK14.NS": -19.4,
            "TESTSTOCK15.NS": -17.2,
            "TESTSTOCK16.NS": -15.8,
            "TESTSTOCK17.NS": -13.7,
            "TESTSTOCK18.NS": -11.9,
            "TESTSTOCK19.NS": -9.6,
            "TESTSTOCK20.NS": -8.2
        }
    }
    
    # 6mo data
    results["6mo"] = {
        "top_performers": {
            "TESTSTOCK1.NS": 48.2,
            "TESTSTOCK2.NS": 45.6,
            "TESTSTOCK3.NS": 42.9,
            "TESTSTOCK31.NS": 39.5,
            "TESTSTOCK32.NS": 37.2,
            "TESTSTOCK33.NS": 35.1,
            "TESTSTOCK4.NS": 32.4,
            "TESTSTOCK5.NS": 30.6,
            "TESTSTOCK9.NS": 28.9,
            "TESTSTOCK10.NS": 26.5
        },
        "bottom_performers": {
            "TESTSTOCK11.NS": -35.8,
            "TESTSTOCK12.NS": -33.2,
            "TESTSTOCK13.NS": -30.7,
            "TESTSTOCK14.NS": -28.3,
            "TESTSTOCK15.NS": -26.1,
            "TESTSTOCK16.NS": -23.9,
            "TESTSTOCK17.NS": -21.3,
            "TESTSTOCK18.NS": -19.2,
            "TESTSTOCK19.NS": -17.5,
            "TESTSTOCK20.NS": -15.9
        }
    }
    
    # 1y data
    results["1y"] = {
        "top_performers": {
            "TESTSTOCK1.NS": 78.6,
            "TESTSTOCK2.NS": 74.3,
            "TESTSTOCK3.NS": 69.7,
            "TESTSTOCK31.NS": 65.2,
            "TESTSTOCK32.NS": 61.9,
            "TESTSTOCK33.NS": 58.3,
            "TESTSTOCK4.NS": 54.8,
            "TESTSTOCK5.NS": 51.2,
            "TESTSTOCK9.NS": 47.9,
            "TESTSTOCK10.NS": 44.6
        },
        "bottom_performers": {
            "TESTSTOCK11.NS": -52.3,
            "TESTSTOCK12.NS": -48.7,
            "TESTSTOCK13.NS": -45.2,
            "TESTSTOCK14.NS": -42.6,
            "TESTSTOCK15.NS": -39.8,
            "TESTSTOCK16.NS": -37.1,
            "TESTSTOCK17.NS": -34.5,
            "TESTSTOCK18.NS": -31.8,
            "TESTSTOCK19.NS": -29.2,
            "TESTSTOCK20.NS": -26.7
        }
    }
    
    return jsonify(results)

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
