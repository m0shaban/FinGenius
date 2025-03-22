import os
import sys
import importlib.util
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Print environment variables for debugging
print(f"DEEPSEEK_API_KEY: {'Set' if os.environ.get('DEEPSEEK_API_KEY') else 'Not set'}")
print(f"DEEPSEEK_MODEL: {os.environ.get('DEEPSEEK_MODEL', 'Not set')}")
print(f"DEEPSEEK_BASE_URL: {os.environ.get('DEEPSEEK_BASE_URL', 'Not set')}")

# Set Flask environment variables
os.environ.setdefault('FLASK_APP', 'run.py')
os.environ.setdefault('FLASK_DEBUG', '1')  # Use FLASK_DEBUG instead of deprecated FLASK_ENV

# Check for critical dependencies before importing the app
required_modules = ['flask', 'flask_sqlalchemy', 'pandas', 'numpy']
missing_modules = []

for module in required_modules:
    if importlib.util.find_spec(module) is None:
        missing_modules.append(module)

if missing_modules:
    print("ERROR: Missing required dependencies:")
    for module in missing_modules:
        print(f"  - {module}")
    print("\nPlease run: fix_install.bat")
    sys.exit(1)

# Import app only after checking dependencies
try:
    from app import create_app, db
    
    app = create_app()
    
    # Ensure database tables exist
    with app.app_context():
        try:
            # Check if user table exists by querying it
            from app.core.models import User
            User.query.first()
        except Exception as db_error:
            print(f"Database error: {db_error}")
            print("Creating database tables...")
            db.create_all()
            print("Database tables created.")
    
    if __name__ == '__main__':
        print("FinGenius starting...")
        
        # Check DeepSeek configuration
        print("=" * 40)
        print("DeepSeek AI Configuration")
        print("=" * 40)
        print(f"API KEY: {'CONFIGURED' if app.config.get('DEEPSEEK_API_KEY') else 'MISSING'}")
        print(f"MODEL: {app.config.get('DEEPSEEK_MODEL', 'Not set')}")
        print(f"BASE URL: {app.config.get('DEEPSEEK_BASE_URL', 'Not set')}")
        print("=" * 40)
        
        app.run(debug=True)
except ImportError as e:
    print(f"ERROR: {e}")
    
    # Specific handling for optional dependencies
    if "weasyprint" in str(e):
        print("\nThe weasyprint module is missing, but it's only needed for PDF exports.")
        print("You can still use the application without this feature.")
        print("To enable PDF exports, run: pip install weasyprint")
        
        # Ask if user wants to continue anyway
        response = input("Do you want to continue without PDF export support? (y/n): ")
        if response.lower() == 'y':
            # Continue with limited functionality
            from app import create_app
            app = create_app()
            if __name__ == '__main__':
                print("Starting FinGenius with limited functionality...")
                print("Access the application at: http://127.0.0.1:5000")
                print("Login with: admin / adminpass")
                app.run(debug=True)
        else:
            print("Please run fix_install.bat to install all dependencies.")
    else:
        print("\nThere seems to be a compatibility issue with the installed packages.")
        print("Please run the fix_install.bat script to install compatible versions.")
    
    sys.exit(1)
