from flask import Blueprint

# Create a blueprint for the entire v1 API
v1_bp = Blueprint('v1', __name__)

# Import and register all endpoint blueprints
from .endpoints.perspective import perspective_bp
from .endpoints.column_state import column_state_bp
from .endpoints.filter_model import filter_model_bp

v1_bp.register_blueprint(perspective_bp, url_prefix='/perspectives')
v1_bp.register_blueprint(column_state_bp, url_prefix='/column_states')
v1_bp.register_blueprint(filter_model_bp, url_prefix='/filter_models')
