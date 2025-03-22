import os
import logging
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from dotenv import load_dotenv

# Load environment variables from .env file right at startup
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Show loaded environment variables for debugging
    print("DeepSeek API Key:", os.environ.get('DEEPSEEK_API_KEY', 'Not set')[:5] + "..." if os.environ.get('DEEPSEEK_API_KEY') else None)
    print("DeepSeek Model:", os.environ.get('DEEPSEEK_MODEL', 'Not set'))
    print("DeepSeek Base URL:", os.environ.get('DEEPSEEK_BASE_URL', 'Not set'))
    
    app.config.from_object(config_class)
    
    # Configure logging for Render and other cloud platforms
    if app.config['LOG_TO_STDOUT']:
        import logging
        from logging import StreamHandler
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('FinGenius startup')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    
    # Register blueprints
    from app.core import bp as core_bp
    app.register_blueprint(core_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.chat import bp as chat_bp
    app.register_blueprint(chat_bp)
    
    from app.analysis import bp as analysis_bp
    app.register_blueprint(analysis_bp)
    
    from app.comparison import bp as comparison_bp
    app.register_blueprint(comparison_bp)
    
    # Register API blueprint
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)
    
    # Register the projections blueprint
    from app.projections import bp as projections_bp
    app.register_blueprint(projections_bp)
    
    # Try to import export module but don't crash if dependencies are missing
    try:
        import weasyprint
        # Register export blueprint with the full functionality
        from app.export import bp as export_bp
        app.register_blueprint(export_bp)
        logger.info("WeasyPrint is available. PDF export functionality enabled.")
    except ImportError as e:
        # Create a simple version of the export module without PDF functionality
        logger.warning(f"WeasyPrint not available. PDF export functionality disabled: {e}")
        logger.warning("To enable PDF export, follow installation instructions at: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html")
        
        # Import a simplified version of the export blueprint without WeasyPrint
        try:
            from app.export import excel_only_bp as export_bp
            app.register_blueprint(excel_only_bp)
        except ImportError:
            logger.warning("Could not import export module. Export functionality will be limited.")
    
    # Import diagnostic routes
    from app.routes import claude_diagnostics, deepseek_diagnostics
    
    # Register API diagnostic routes
    app.add_url_rule('/api/diagnostics/claude', 'claude_diagnostics', claude_diagnostics, methods=['GET'])
    app.add_url_rule('/api/diagnostics/deepseek', 'deepseek_diagnostics', deepseek_diagnostics, methods=['GET'])
    
    # Register context processors for datetime access in templates
    from app import context_processors
    context_processors.init_app(app)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
    
    return app

from app.core import models
