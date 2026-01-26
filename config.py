"""
Configuration file for Research Digest Generator
Loads API keys and settings from environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
OPENAI_MODEL = "gpt-4-turbo-preview"  # or "gpt-4o" if you have access
# Alternative cheaper model: "gpt-3.5-turbo" (lower quality but faster/cheaper)

# Digest Settings
DEFAULT_QUERY = "Gameplay"
DEFAULT_MAX_PAPERS = 5
DEFAULT_START_YEAR = 2022

# PDF Generation Settings
PDF_OPTIONS = {
    'page-size': 'A4',
    'margin-top': '20mm',
    'margin-right': '20mm',
    'margin-bottom': '20mm',
    'margin-left': '20mm',
    'encoding': "UTF-8",
    'no-outline': None,
    'enable-local-file-access': None,
    'print-media-type': None,
    'dpi': 300,
    'image-dpi': 300,
    'image-quality': 100,
    'quiet': ''
}

# Visualization Colors
VIZ_COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'accent': '#f093fb',
    'success': '#4caf50',
    'warning': '#ff9800',
    'danger': '#f44336'
}

# Monthly digest settings
DEFAULT_START_MONTH = None
DEFAULT_END_MONTH = None

# RSS feed settings
MAX_PAPERS_PER_FEED = 15
TOTAL_RESEARCH_DOMAINS = 10

# Plotly visualization settings
PLOTLY_CONFIG = {
    'width': 1400,
    'height': 900,
    'dpi': 300,
}

# Plotly color scheme (professional publication quality)
PLOTLY_COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#06A77D',
    'data': '#FFB627',
    'process': '#6C757D',
    'light_bg': '#F8F9FA',
    'border': '#333333',
    'p001': '#E63946',    # p<.001 - high significance
    'p01': '#F4A261',     # p<.01 - moderate significance
    'p05': '#2A9D8F',     # p<.05 - significance
    'ns': '#ADB5BD',      # not significant
}

# Validate configuration
def validate_config():
    """Validate that all required configuration is present"""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables.\n"
            "Please create a .env file with:\n"
            "OPENAI_API_KEY=your-key-here"
        )
    
    print("✓ Configuration loaded successfully")
    print(f"✓ Model: {OPENAI_MODEL}")
    print(f"✓ API Key: {'*' * 20}{OPENAI_API_KEY[-4:]}")
    return True

# Run validation when imported
if __name__ != "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"⚠️  Configuration Error: {e}")