from flask import Blueprint
import importlib.util
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the blueprint
bp = Blueprint('export', __name__, url_prefix='/export')

# Check if WeasyPrint is available
weasyprint_available = importlib.util.find_spec("weasyprint") is not None

# Create alternative blueprint for excel-only functionality
excel_only_bp = Blueprint('export', __name__, url_prefix='/export')

# Only import routes after blueprint creation
if weasyprint_available:
    try:
        from app.export import routes
        logger.info("Export routes with PDF support initialized")
    except ImportError as e:
        logger.warning(f"Failed to import full export routes: {e}")
        from app.export import excel_routes
        logger.info("Excel-only export routes initialized")
else:
    from app.export import excel_routes
    logger.info("Excel-only export routes initialized")
