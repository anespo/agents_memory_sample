#!/usr/bin/env python3
"""
Setup Verification Script for Agent Memory Management Application

This script verifies that all prerequisites are met before running the application.
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"❌ Python 3.10+ required. Found: {version.major}.{version.minor}.{version.micro}")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")
    required = [
        "streamlit",
        "boto3",
        "strands",
        "bedrock_agentcore",
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not found")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def check_aws_credentials():
    """Check if AWS credentials are configured."""
    print("\nChecking AWS credentials...")
    aws_dir = Path.home() / ".aws"
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    
    if not credentials_file.exists():
        print("❌ AWS credentials file not found")
        print(f"   Expected: {credentials_file}")
        print("   Run: aws configure")
        return False
    
    print(f"✅ AWS credentials file found")
    
    # Check for required profiles
    with open(credentials_file, "r") as f:
        content = f.read()
        has_default = "[default]" in content
        has_llm = "[default-xavi]" in content
    
    if has_default:
        print("✅ Profile 'default' found")
    else:
        print("❌ Profile 'default' not found")
    
    if has_llm:
        print("✅ Profile 'default-xavi' found")
    else:
        print("⚠️  Profile 'default-xavi' not found")
        print("   You may need to configure this profile for LLM operations")
    
    return has_default


def check_aws_region():
    """Check if AWS region is configured."""
    print("\nChecking AWS region configuration...")
    config_file = Path.home() / ".aws" / "config"
    
    if not config_file.exists():
        print("⚠️  AWS config file not found")
        print("   Region can be set via environment variable: AWS_DEFAULT_REGION=eu-west-1")
        return True  # Not critical
    
    with open(config_file, "r") as f:
        content = f.read()
        if "region" in content:
            print("✅ AWS region configured")
            return True
        else:
            print("⚠️  No region found in config")
            print("   Set via: aws configure set region eu-west-1")
            return True  # Not critical


def check_bedrock_access():
    """Check if Bedrock services are accessible."""
    print("\nChecking AWS Bedrock access...")
    try:
        import boto3
        
        # Test default profile
        try:
            session = boto3.Session(profile_name="default", region_name="eu-west-1")
            client = session.client("bedrock-agentcore-control")
            # Try to list memories (will fail if no permissions, but that's ok)
            client.list_memories(maxResults=1)
            print("✅ Bedrock AgentCore accessible with 'default' profile")
        except Exception as e:
            error_msg = str(e)
            if "AccessDenied" in error_msg or "UnauthorizedOperation" in error_msg:
                print("⚠️  Bedrock AgentCore accessible but may need IAM permissions")
            elif "InvalidClientTokenId" in error_msg or "SignatureDoesNotMatch" in error_msg:
                print("❌ Invalid AWS credentials for 'default' profile")
                return False
            else:
                print(f"⚠️  Could not verify Bedrock access: {error_msg[:100]}")
        
        # Test LLM profile
        try:
            session = boto3.Session(profile_name="default-xavi", region_name="eu-west-1")
            client = session.client("bedrock")
            client.list_foundation_models(byProvider="anthropic")
            print("✅ Bedrock Runtime accessible with 'default-xavi' profile")
        except Exception as e:
            error_msg = str(e)
            if "ProfileNotFound" in error_msg:
                print("⚠️  Profile 'default-xavi' not found (optional for testing)")
            elif "AccessDenied" in error_msg:
                print("⚠️  Bedrock Runtime accessible but may need model access")
            else:
                print(f"⚠️  Could not verify Bedrock Runtime: {error_msg[:100]}")
        
        return True
        
    except ImportError:
        print("❌ boto3 not installed")
        return False
    except Exception as e:
        print(f"⚠️  Error checking Bedrock access: {str(e)[:100]}")
        return True  # Don't fail on this


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Agent Memory Management - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Dependencies", check_dependencies()),
        ("AWS Credentials", check_aws_credentials()),
        ("AWS Region", check_aws_region()),
        ("Bedrock Access", check_bedrock_access()),
    ]
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the application.")
        print("\nRun: streamlit run app.py")
        print("Or:  ./run_app.sh")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help, see:")
        print("  - TROUBLESHOOTING.md")
        print("  - QUICKSTART.md")
        print("  - START_HERE.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
