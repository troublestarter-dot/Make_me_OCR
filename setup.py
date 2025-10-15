"""Setup script for OCR Factory."""
from pathlib import Path
import sys

def setup_directories():
    """Create necessary directories."""
    base_dir = Path(__file__).parent
    
    directories = [
        'data/input',
        'data/processed',
        'data/originals',
        'data/index',
        'logs'
    ]
    
    print("Creating directories...")
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print("\nDirectories created successfully!")


def check_env_file():
    """Check if .env file exists."""
    base_dir = Path(__file__).parent
    env_file = base_dir / '.env'
    env_example = base_dir / '.env.example'
    
    if not env_file.exists():
        print("\n⚠️  WARNING: .env file not found!")
        print(f"   Please copy {env_example} to .env and configure it:")
        print(f"   cp .env.example .env")
        return False
    else:
        print("\n✓ .env file exists")
        return True


def check_requirements():
    """Check if requirements are installed."""
    print("\nChecking requirements...")
    
    required_packages = [
        'watchdog',
        'python-dotenv',
        'PyPDF2',
        'pdf2image',
        'Pillow',
        'google-auth',
        'gspread',
        'cloudconvert',
        'openai',
        'pandas',
        'requests',
        'imagehash',
        'colorlog'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All required packages installed")
        return True


def main():
    """Run setup."""
    print("=" * 60)
    print("OCR FACTORY SETUP")
    print("=" * 60)
    
    setup_directories()
    env_ok = check_env_file()
    req_ok = check_requirements()
    
    print("\n" + "=" * 60)
    if env_ok and req_ok:
        print("✓ Setup complete! You can now run: python src/main.py")
    else:
        print("⚠️  Setup incomplete. Please address the issues above.")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
