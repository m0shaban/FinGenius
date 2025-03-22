import os
import sys
import shutil
import subprocess
import venv
from pathlib import Path

class FinGeniusManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.venv_dir = self.base_dir / "venv"
        self.requirements_file = self.base_dir / "requirements.txt"
        self.uploads_dir = self.base_dir / "uploads"
        self.sample_data_dir = self.base_dir / "sample_data"
        self.db_file = self.base_dir / "app.db"
        self.env_file = self.base_dir / ".env"
        self.python_exe = self.venv_dir / "Scripts" / "python.exe"

    def create_venv(self):
        """Create virtual environment if it doesn't exist"""
        print("Setting up virtual environment...")
        if not self.venv_dir.exists():
            venv.create(self.venv_dir, with_pip=True)
        return self.python_exe.exists()

    def install_requirements(self):
        """Install required packages"""
        print("Installing dependencies...")
        subprocess.run([
            str(self.python_exe), "-m", "pip", "install",
            "--no-cache-dir", "-r", str(self.requirements_file)
        ], check=True)

    def setup_directories(self):
        """Create necessary directories"""
        print("Creating directories...")
        self.uploads_dir.mkdir(exist_ok=True)
        self.sample_data_dir.mkdir(exist_ok=True)

    def create_env_file(self):
        """Create .env file if it doesn't exist"""
        if not self.env_file.exists():
            print("Creating .env file...")
            env_content = """FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=dev-key-change-this-in-production
CLAUDE_API_KEY=your-claude-api-key-here
"""
            self.env_file.write_text(env_content)

    def init_database(self):
        """Initialize the database"""
        print("Initializing database...")
        if self.db_file.exists():
            self.db_file.unlink()
        
        subprocess.run([
            str(self.python_exe), "-c",
            "from app import create_app, db; "
            "from app.core.models import User; "
            "app = create_app(); "
            "app.app_context().push(); "
            "db.create_all(); "
            "admin = User(username='admin', email='admin@fingenius.com', role='admin'); "
            "admin.set_password('adminpass'); "
            "db.session.add(admin); "
            "db.session.commit()"
        ], check=True)

    def run_app(self):
        """Run the Flask application"""
        print("\nStarting FinGenius...")
        subprocess.run([str(self.python_exe), "run.py"])

    def clean(self):
        """Clean installation files"""
        print("Cleaning installation...")
        dirs_to_clean = ["__pycache__", "migrations", "venv"]
        files_to_clean = ["app.db"]
        
        for d in dirs_to_clean:
            path = self.base_dir / d
            if path.exists():
                shutil.rmtree(path)
                
        for f in files_to_clean:
            path = self.base_dir / f
            if path.exists():
                path.unlink()

    def install(self):
        """Full installation process"""
        try:
            print("Starting FinGenius installation...")
            self.create_venv()
            self.install_requirements()
            self.setup_directories()
            self.create_env_file()
            self.init_database()
            print("\nInstallation completed successfully!")
            print("You can now run the application with: python manage.py run")
            print("\nDefault login:")
            print("Username: admin")
            print("Password: adminpass")
        except Exception as e:
            print(f"Error during installation: {e}")
            sys.exit(1)

def main():
    manager = FinGeniusManager()
    
    if len(sys.argv) < 2:
        print("Usage: python manage.py [command]")
        print("\nCommands:")
        print("  install  - Install FinGenius and dependencies")
        print("  run      - Run the application")
        print("  clean    - Remove all generated files")
        print("  update   - Update dependencies and database")
        sys.exit(1)

    command = sys.argv[1]
    
    try:
        if command == "install":
            manager.install()
        elif command == "run":
            manager.run_app()
        elif command == "clean":
            manager.clean()
        elif command == "update":
            manager.install_requirements()
            manager.init_database()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
