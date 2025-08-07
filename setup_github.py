#!/usr/bin/env python3
"""
Setup script for GitHub repository
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_git_repo():
    """Set up Git repository and initial commit"""
    
    print("🚀 Setting up GitHub repository...")
    
    # Check if git is installed
    if not run_command("git --version", "Checking Git installation"):
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    # Initialize git repository
    if not run_command("git init", "Initializing Git repository"):
        return False
    
    # Add all files
    if not run_command("git add .", "Adding files to Git"):
        return False
    
    # Create initial commit
    if not run_command('git commit -m "Initial commit: Interventional Pulmonology AI Assistant"', "Creating initial commit"):
        return False
    
    print("\n🎉 Git repository setup complete!")
    print("\n📋 Next steps:")
    print("1. Create a new repository on GitHub:")
    print("   - Go to https://github.com/new")
    print("   - Name it: interventional-pulmonology-ai")
    print("   - Make it public or private")
    print("   - Don't initialize with README (we already have one)")
    print("\n2. Connect your local repository:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/interventional-pulmonology-ai.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    print("\n3. Set up GitHub Pages (optional):")
    print("   - Go to Settings > Pages")
    print("   - Source: Deploy from a branch")
    print("   - Branch: main, folder: /docs")
    
    return True

def main():
    """Main function"""
    print("🫁 Interventional Pulmonology AI Assistant - GitHub Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the project root directory")
        return
    
    # Set up git repository
    if setup_git_repo():
        print("\n✅ Repository setup completed successfully!")
    else:
        print("\n❌ Repository setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
