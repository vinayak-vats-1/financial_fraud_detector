import subprocess
import sys

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {command}")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def push_to_github():
    print("🚀 AWS Fraud Detection Pipeline - GitHub Push Setup")
    print("=" * 60)
    
    # Get repository details
    repo_name = input("Enter GitHub repository name (e.g., aws-fraud-detection): ").strip()
    if not repo_name:
        repo_name = "aws-fraud-detection"
    
    github_username = input("Enter your GitHub username: ").strip()
    if not github_username:
        print("❌ GitHub username is required")
        return
    
    print(f"\n📋 Repository Details:")
    print(f"   Repository: {repo_name}")
    print(f"   Username: {github_username}")
    print(f"   URL: https://github.com/{github_username}/{repo_name}")
    
    confirm = input("\n✅ Proceed with push? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Push cancelled")
        return
    
    print("\n🔄 Setting up remote repository...")
    
    # Add remote origin
    remote_url = f"https://github.com/{github_username}/{repo_name}.git"
    if not run_command(f"git remote add origin {remote_url}"):
        print("⚠️  Remote might already exist, trying to set URL...")
        run_command(f"git remote set-url origin {remote_url}")
    
    # Push to GitHub
    print("\n📤 Pushing to GitHub...")
    if run_command("git push -u origin main"):
        print("\n🎉 SUCCESS! Your fraud detection system is now on GitHub!")
        print(f"🔗 Repository URL: https://github.com/{github_username}/{repo_name}")
        print("\n📚 What's included:")
        print("   ✅ Complete AWS infrastructure (Terraform)")
        print("   ✅ Fraud detection pipeline (Glue, SageMaker)")
        print("   ✅ AI Assistant with natural language queries")
        print("   ✅ Beautiful web interface")
        print("   ✅ Lambda functions and API Gateway")
        print("   ✅ Comprehensive documentation")
    else:
        print("\n❌ Push failed. You may need to:")
        print("   1. Create the repository on GitHub first")
        print("   2. Check your GitHub credentials")
        print("   3. Ensure you have push permissions")
        print("\n💡 Manual steps:")
        print(f"   1. Go to https://github.com/new")
        print(f"   2. Create repository: {repo_name}")
        print(f"   3. Run: git push -u origin main")

if __name__ == "__main__":
    push_to_github()