from flask import Blueprint

# Base v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import route modules to register them on the blueprint
from . import health
