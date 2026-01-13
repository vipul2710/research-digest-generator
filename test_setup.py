"""Test script to verify setup"""
import sys

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    try:
        import openai
        print("✓ openai")
        import jinja2
        print("✓ jinja2")
        import pdfkit
        print("✓ pdfkit")
        import matplotlib
        print("✓ matplotlib")
        import seaborn
        print("✓ seaborn")
        from config import OPENAI_API_KEY, OPENAI_MODEL
        print("✓ config loaded")
        print(f"  Model: {OPENAI_MODEL}")
        print(f"  API Key: {'*' * 20}{OPENAI_API_KEY[-4:]}")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_directories():
    """Test required directories exist"""
    import os
    print("\nTesting directories...")
    dirs = ['data', 'visualizations', 'output']
    for d in dirs:
        if os.path.exists(d):
            print(f"✓ {d}/")
        else:
            print(f"✗ {d}/ missing")
            os.makedirs(d)
            print(f"  Created {d}/")
    return True

def test_wkhtmltopdf():
    """Test wkhtmltopdf installation"""
    import subprocess
    import os
    print("\nTesting wkhtmltopdf...")
    
    # Windows path
    wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    
    if not os.path.exists(wkhtmltopdf_path):
        print("✗ wkhtmltopdf executable not found at expected path")
        print(f"  Expected at: {wkhtmltopdf_path}")
        print("  Download from: https://wkhtmltopdf.org/downloads.html")
        return False
    
    try:
        result = subprocess.run(
            [wkhtmltopdf_path, "--version"],
            capture_output=True,
            text=True
        )
        print("✓ wkhtmltopdf installed")
        print(f"  Version: {result.stdout.split()[1]}")
        return True
    except Exception as e:
        print(f"✗ wkhtmltopdf error: {e}")
        return False
    
def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI API...")
    try:
        from openai import OpenAI
        from config import OPENAI_API_KEY
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        print("✓ OpenAI API connected")
        print(f"  Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"✗ OpenAI API error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("SETUP VERIFICATION TEST")
    print("="*60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Directories", test_directories()))
    results.append(("wkhtmltopdf", test_wkhtmltopdf()))
    results.append(("OpenAI API", test_openai_connection()))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    if all(r[1] for r in results):
        print("\n🎉 All tests passed! Ready to generate digest.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Fix issues above before proceeding.")
        sys.exit(1)