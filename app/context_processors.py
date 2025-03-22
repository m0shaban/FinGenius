from datetime import datetime

def utility_processor():
    """Add utility functions and objects to template context"""
    return {
        'datetime': datetime,
    }

def init_app(app):
    """Initialize context processors with the Flask app"""
    app.context_processor(utility_processor)
