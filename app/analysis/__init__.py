from flask import Blueprint

bp = Blueprint('analysis', __name__, url_prefix='/analysis')

from app.analysis import routes
