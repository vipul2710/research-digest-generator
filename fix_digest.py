"""
Quick fixes for common digest issues
"""

import os
import re

def fix_html_template():
    """Fix digest.html for better PDF rendering"""
    
    with open('digest.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace gradients with solid colors
    html = re.sub(
        r'background:\s*linear-gradient\([^)]+\);',
        'background: #667eea;',
        html
    )
    
    # Ensure white text on colored backgrounds
    html = html.replace(
        '.paper-header {',
        '.paper-header { color: white !important;'
    )
    
    html = html.replace(
        '.cover-page {',
        '.cover-page { color: white !important;'
    )
    
    with open('digest.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ Fixed digest.html")

def check_visualizations():
    """Check if visualizations exist"""
    
    viz_dir = 'visualizations'
    if not os.path.exists(viz_dir):
        os.makedirs(viz_dir)
        print(f"Created {viz_dir}/")
    
    files = os.listdir(viz_dir)
    png_files = [f for f in files if f.endswith('.png')]
    
    print(f"\n📊 Visualizations: {len(png_files)} images found")
    for f in png_files:
        size = os.path.getsize(os.path.join(viz_dir, f))
        print(f"  - {f} ({size} bytes)")
    
    if len(png_files) == 0:
        print("⚠️  No visualizations found!")
        print("   Run: python -c \"from visualize_enhanced import generate_all_visualizations; generate_all_visualizations('data/enhanced_papers_sample.json')\"")

def fix_citation_display():
    """Fix citation count in template"""
    
    with open('digest.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find and replace N/A with actual variable
    html = html.replace(
        '{{ avg_citations }}',
        '{{ avg_citations if avg_citations else "Data pending" }}'
    )
    
    with open('digest.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ Fixed citation display")

if __name__ == "__main__":
    print("Running digest fixes...\n")
    fix_html_template()
    check_visualizations()
    fix_citation_display()
    print("\n✅ Fixes complete! Regenerate digest now.")