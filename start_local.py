#!/usr/bin/env python3
"""
Hold Busters Dashboard - Local Startup Script
Checks dependencies and starts the Streamlit app
"""
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'databricks.sql',
        'databricks.sdk',
        'plotly',
        'pandas'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('.', '_') if '.' in package else package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    return missing

def check_secrets():
    """Check if secrets.toml exists"""
    secrets_path = Path('.streamlit/secrets.toml')
    if not secrets_path.exists():
        print("❌ .streamlit/secrets.toml not found")
        print("   Please create it from .streamlit/secrets.toml.template")
        return False
    print("✅ .streamlit/secrets.toml exists")
    return True

def main():
    """Main startup routine"""
    print("=" * 60)
    print("  Hold Busters Dashboard - Local Startup")
    print("=" * 60)
    print()
    
    # Check Python version
    print("📋 Checking Python version...")
    if not check_python_version():
        sys.exit(1)
    print()
    
    # Check dependencies
    print("📦 Checking dependencies...")
    missing = check_dependencies()
    print()
    
    if missing:
        print("⚠️  Missing packages detected!")
        print()
        response = input("Install missing packages now? (y/n): ")
        if response.lower() == 'y':
            print()
            print("Installing dependencies...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print()
        else:
            print("Cannot start without required packages.")
            sys.exit(1)
    
    # Check secrets
    print("🔐 Checking configuration...")
    if not check_secrets():
        print()
        print("Please set up your Databricks credentials in .streamlit/secrets.toml")
        sys.exit(1)
    print()
    
    # Start Streamlit
    print("=" * 60)
    print("🚀 Starting Hold Busters Dashboard...")
    print("=" * 60)
    print()
    print("📍 Dashboard URL: http://localhost:8501")
    print()
    print("✨ Features:")
    print("   • Invoice Overview Dashboard")
    print("   • Invoice Details Analysis")
    print("   • Deep Analysis with Drill-downs")
    print("   • Error Analysis Dashboard")
    print("   • Custom SQL Query Tool")
    print("   • Genie AI Q&A")
    print()
    print("⏹️  Press Ctrl+C to stop")
    print()
    print("=" * 60)
    print()
    
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
    except KeyboardInterrupt:
        print()
        print("Dashboard stopped.")

if __name__ == '__main__':
    main()

