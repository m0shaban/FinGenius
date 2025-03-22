from flask import Blueprint

bp = Blueprint('comparison', __name__, url_prefix='/comparison')

from app.comparison import routes
