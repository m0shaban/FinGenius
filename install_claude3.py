import subprocess
import sys
import os
import time

def main():
    print("="*60)
    print("Claude 3 Compatibility Installer")
    print("="*60)
    print("\nThis script will install the correct version of the Anthropic SDK for Claude 3 models.\n")
    
    # Check for existing anthropic package
    try:
        import pkg_resources
        try:
            version = pkg_resources.get_distribution("anthropic").version
            print(f"Current anthropic SDK version: {version}")
            
            if version.startswith("0.3") or version.startswith("0.4") or version.startswith("0.5"):
                print("You already have a compatible version for Claude 3 models.")
                response = input("Do you want to reinstall anyway? (y/n): ")
                if response.lower() != 'y':
                    print("Exiting without changes.")
                    return
            else:
                print(f"Version {version} is not compatible with Claude 3 models.")
        except pkg_resources.DistributionNotFound:
            print("Anthropic SDK is not installed.")
    except ImportError:
        print("Unable to check current installation.")
    
    # Confirm installation
    print("\nThis will upgrade or install anthropic SDK version 0.3.11 which supports Claude 3 models.")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Installation cancelled.")
        return
    
    # Uninstall any existing version
    print("\nRemoving any existing anthropic package...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "anthropic"])
        time.sleep(1)  # Give time for package to be fully removed
    except:
        # Ignore errors during uninstallation
        pass
    
    # Install new version
    print("\nInstalling anthropic SDK version 0.8.1...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic==0.8.1"])
        print("\nInstallation successful!")
        
        # Update .env file
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            # Update model if needed
            if "CLAUDE_MODEL=" in env_content and "claude-3" not in env_content:
                env_content = env_content.replace("CLAUDE_MODEL=claude-2", "CLAUDE_MODEL=claude-3-haiku-20240307")
                with open(env_file, 'w') as f:
                    f.write(env_content)
                print("\nUpdated .env file to use Claude 3 Haiku model.")
        
        print("\nYou can now use Claude 3 models with your application.")
        print("Supported models include:")
        print("- claude-3-opus-20240229")
        print("- claude-3-sonnet-20240229")
        print("- claude-3-haiku-20240307")
        
    except Exception as e:
        print(f"\nError installing package: {e}")
        print("Please try manually with: pip install anthropic==0.8.1")

if __name__ == "__main__":
    main()
