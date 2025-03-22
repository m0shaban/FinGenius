from flask import Blueprint

bp = Blueprint('projections', __name__)

from app.projections import routes
