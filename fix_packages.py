import subprocess
import sys

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Fix pip and package dependencies"""
    print("Installing/upgrading setuptools which includes pkg_resources...")
    install_package("setuptools")
    
    print("Installing/upgrading pip...")
    install_package("--upgrade pip")
    
    # Ensure specific versions for compatibility
    packages = [
        "anthropic==0.2.10",
        "flask==2.2.5",
        "flask-sqlalchemy==3.0.3",
        "werkzeug==2.2.3"
    ]
    
    print("Installing compatible packages...")
    for package in packages:
        print(f"Installing {package}")
        install_package(package)
    
    print("\nPackage installation complete!")
    print("You can now run: python fing_manager.py run")

if __name__ == "__main__":
    main()
