"""
Improved rendering module for professor-level research digest
"""

import json
import pdfkit
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
from pathlib import Path


def render_digest(data_file: str, template_file: str = "digest.html", 
                 output_pdf: str = "research_digest.pdf"):
    """
    Render the complete research digest as a professional PDF
    """
    
    print("Loading enhanced paper data...")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    synthesis = data.get('synthesis', {})
    metadata = data.get('metadata', {})
    
    # Get absolute base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

    PDFKIT_CONFIG = pdfkit.configuration(
        wkhtmltopdf=WKHTMLTOPDF_PATH)
    
# Add visualization paths to papers with file:// URLs for wkhtmltopdf
    for i, paper in enumerate(papers, 1):  # ADD enumerate with index
        # UNIQUE ID: index + DOI (matches visualization naming)
        doi = paper.get('doi', f'paper_{i}')
        paper_id = f"{i}_{doi.replace('/', '_').replace('.', '_')}"
        
        # Create absolute file:// URLs for images
        methodology_path = os.path.join(BASE_DIR, "visualizations", f"{paper_id}_methodology.png")
        results_path = os.path.join(BASE_DIR, "visualizations", f"{paper_id}_results.png")
        
        # Convert to file:// URL format
        paper['methodology_diagram'] = Path(methodology_path).as_uri() if os.path.exists(methodology_path) else ""
        paper['results_visualization'] = Path(results_path).as_uri() if os.path.exists(results_path) else ""
        
        # Debug
        if os.path.exists(methodology_path):
            print(f"✓ Found methodology: paper {i}")
        else:
            print(f"✗ Missing methodology: {methodology_path}")    
    # Calculate statistics
    stats = calculate_statistics(papers)
    
    # Prepare template data
    template_data = {
        'title': 'Agentic AI & Gaming Research Digest',
        'date': datetime.now().strftime('%B %d, %Y'),
        'paper_count': len(papers),
        'papers': papers,
        'synthesis': synthesis,
        'total_participants': stats.get('total_participants', 0),
        'avg_citations': stats.get('avg_citations', 0),
        'date_range': metadata.get('date_range', '2024'),
        'executive_summary': synthesis.get('executive_summary', ''),
        'key_themes': synthesis.get('key_themes', [])
    }
    
    # Load Jinja2 template
    print("\nRendering HTML template...")
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)
    
    html_content = template.render(**template_data)
    
    # Save HTML for debugging
    html_output = output_pdf.replace('.pdf', '.html')
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✓ HTML saved to: {html_output}")
    
    # Configure PDF options for high quality
    options = {
        'page-size': 'A4',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,  # CRITICAL for loading images
        'print-media-type': None,
        'dpi': 300,
        'image-dpi': 300,
        'image-quality': 100,
        'quiet': ''
    }
    
    # Windows wkhtmltopdf configuration
    WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    
    print("\nGenerating PDF...")
    try:
        pdfkit.from_file(html_output, output_pdf, options=options, configuration=config)
        print(f"✓ PDF generated successfully: {output_pdf}")
        
        if os.path.exists(output_pdf):
            print(f"  Size: {os.path.getsize(output_pdf) / 1024 / 1024:.2f} MB")
        
        return output_pdf
    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        print("\n💡 Troubleshooting:")
        print("  1. Make sure wkhtmltopdf is installed")
        print("  2. Check that images exist in visualizations/ folder")
        print("  3. Open the HTML file to debug layout issues")
        return None


def calculate_statistics(papers: list) -> dict:
    """
    Calculate aggregate statistics across papers
    """
    stats = {
        'total_participants': 0,
        'avg_citations': 0,
        'year_range': '',
        'venue_distribution': {},
        'methodology_distribution': {}
    }
    
    # Count participants
    for paper in papers:
        sample_size = paper.get('methodology', {}).get('sample_size', '')
        if 'N=' in sample_size:
            try:
                n = int(sample_size.split('N=')[1].split()[0].replace(',', ''))
                stats['total_participants'] += n
            except:
                pass
    
    # Average citations
    citations = [int(p.get('citations', 0)) for p in papers if p.get('citations')]
    if citations:
        stats['avg_citations'] = sum(citations) // len(citations)
    
    # Year range
    years = [str(p.get('year', '')) for p in papers if p.get('year')]
    if years:
        stats['year_range'] = f"{min(years)} - {max(years)}"
    
    # Venue distribution
    for paper in papers:
        venue = paper.get('venue', 'Unknown')
        stats['venue_distribution'][venue] = stats['venue_distribution'].get(venue, 0) + 1
    
    # Methodology distribution
    for paper in papers:
        design = paper.get('methodology', {}).get('design', 'Unknown')
        stats['methodology_distribution'][design] = stats['methodology_distribution'].get(design, 0) + 1
    
    return stats


if __name__ == "__main__":
    import sys
    
    data_file = sys.argv[1] if len(sys.argv) > 1 else "data/enhanced_papers.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "research_digest.pdf"
    
    render_digest(data_file, output_pdf=output_file)