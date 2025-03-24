import os
import logging
from flask import Flask
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_testing")

# Enable CORS
CORS(app)

# Import routes
from routes import *
