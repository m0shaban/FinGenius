from flask import jsonify, current_app
import os

# Define functions without decorators, they'll be registered with the app later

def claude_diagnostics():
    """Diagnostic endpoint for Claude integration"""
    from app.chat.claude_client import ClaudeClient, anthropic_available
    
    diagnostics = {
        'anthropic_installed': anthropic_available,
        'environment': {}
    }
    
    # Check environment variables
    for key in os.environ:
        if 'CLAUDE' in key or 'API' in key:
            # Mask the actual values for security
            diagnostics['environment'][key] = 'PRESENT' if os.environ[key] else 'EMPTY'
    
    # Check config
    diagnostics['config'] = {
        'CLAUDE_API_KEY': 'PRESENT' if 'CLAUDE_API_KEY' in current_app.config and current_app.config['CLAUDE_API_KEY'] else 'MISSING',
        'CLAUDE_MODEL': current_app.config.get('CLAUDE_MODEL', 'NOT SET')
    }
    
    # Test client initialization
    try:
        client = ClaudeClient()
        diagnostics['client_initialized'] = client.client is not None
        diagnostics['model'] = client.model
        diagnostics['api_version'] = 'new (0.3+)' if hasattr(client, 'use_new_api') and client.use_new_api else 'old (0.2.x)'
    except Exception as e:
        diagnostics['client_error'] = str(e)
        diagnostics['client_initialized'] = False
    
    return jsonify(diagnostics)

def deepseek_diagnostics():
    """Diagnostic endpoint for DeepSeek integration"""
    from app.chat.deepseek_client import DeepSeekClient, openai_available
    
    diagnostics = {
        'openai_installed': openai_available,
        'environment': {}
    }
    
    # Check environment variables
    for key in os.environ:
        if 'DEEPSEEK' in key or 'API' in key:
            # Mask the actual values for security
            diagnostics['environment'][key] = 'PRESENT' if os.environ[key] else 'EMPTY'
    
    # Check config
    diagnostics['config'] = {
        'DEEPSEEK_API_KEY': 'PRESENT' if 'DEEPSEEK_API_KEY' in current_app.config and current_app.config['DEEPSEEK_API_KEY'] else 'MISSING',
        'DEEPSEEK_MODEL': current_app.config.get('DEEPSEEK_MODEL', 'NOT SET'),
        'DEEPSEEK_BASE_URL': current_app.config.get('DEEPSEEK_BASE_URL', 'NOT SET')
    }
    
    # Test client initialization
    try:
        client = DeepSeekClient()
        diagnostics['client_initialized'] = client.client is not None
        diagnostics['model'] = client.model
        diagnostics['base_url'] = client.base_url
    except Exception as e:
        diagnostics['client_error'] = str(e)
        diagnostics['client_initialized'] = False
    
    return jsonify(diagnostics)
