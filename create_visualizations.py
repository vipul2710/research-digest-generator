"""
Generate real research visualizations instead of generic AI images
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import numpy as np
from typing import Dict, List
import json
import os

# Set professional style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")

COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'accent': '#f093fb',
    'success': '#4caf50',
    'warning': '#ff9800',
    'danger': '#f44336'
}


def create_methodology_framework(paper: Dict, output_path: str):
    """
    Create a flowchart showing the methodology
    """
    fig, ax = plt.subplots(figsize=(14, 10))  # Increased size
    ax.axis('off')
    
    methodology = paper.get('methodology', {})
    
    # Title
    title = paper.get('title', '')
    if len(title) > 60:
        title = title[:60] + '...'
    fig.suptitle(f"Methodological Framework\n{title}", 
                 fontsize=13, fontweight='bold', y=0.96)
    
    # Truncate long text
    def truncate(text, max_len=40):
        if len(text) > max_len:
            return text[:max_len-3] + '...'
        return text
    
    # Get methodology details
    sample_size = methodology.get('sample_size', 'N=?')
    design = truncate(methodology.get('design', 'Not specified'), 25)
    materials = truncate(methodology.get('materials', 'Not specified'), 35)
    analysis = truncate(methodology.get('analysis', 'Not specified'), 35)
    
    # Define boxes with better spacing
    boxes = [
        {"text": f"Participants\n{sample_size}", "pos": (0.15, 0.75), "color": COLORS['primary'], "width": 0.18},
        {"text": f"Design\n{design}", "pos": (0.42, 0.75), "color": COLORS['secondary'], "width": 0.18},
        {"text": f"Materials\n{materials}", "pos": (0.69, 0.75), "color": COLORS['accent'], "width": 0.18},
        {"text": "Data Collection\nProcedure", "pos": (0.28, 0.50), "color": COLORS['warning'], "width": 0.20},
        {"text": f"Analysis\n{analysis}", "pos": (0.58, 0.50), "color": COLORS['success'], "width": 0.20},
        {"text": "Results &\nFindings", "pos": (0.43, 0.25), "color": COLORS['danger'], "width": 0.20}
    ]
    
    # Draw boxes with adjusted sizes
    for box in boxes:
        fancy_box = FancyBboxPatch(
            (box['pos'][0] - box['width']/2, box['pos'][1] - 0.06),
            box['width'], 0.12,
            boxstyle="round,pad=0.015",
            edgecolor=box['color'],
            facecolor=box['color'],
            alpha=0.3,
            linewidth=2.5
        )
        ax.add_patch(fancy_box)
        
        # Text inside box
        ax.text(box['pos'][0], box['pos'][1], box['text'],
                ha='center', va='center', fontsize=9, fontweight='bold',
                wrap=True)
    
    # Draw arrows with better positioning
    arrows = [
        ((0.15, 0.69), (0.28, 0.56)),   # Participants -> Data Collection
        ((0.42, 0.69), (0.43, 0.56)),   # Design -> Analysis (adjusted)
        ((0.69, 0.69), (0.58, 0.56)),   # Materials -> Analysis
        ((0.33, 0.44), (0.43, 0.31)),   # Data Collection -> Results
        ((0.63, 0.44), (0.53, 0.31))    # Analysis -> Results
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2.5, color=COLORS['primary'], alpha=0.6))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✓ Created methodology diagram: {output_path}")
    if os.path.exists(output_path):
        print(f"  Size: {os.path.getsize(output_path) / 1024:.1f} KB")

def create_results_comparison(paper: Dict, output_path: str):
    """
    Create bar chart or comparison visualization from findings
    """
    findings = paper.get('findings', [])
    
    if not findings or len(findings) < 2:
        # Create placeholder
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'Quantitative results visualization\nwould appear here with actual data',
                ha='center', va='center', fontsize=12, style='italic')
        ax.axis('off')
    else:
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Extract statistics if available
        categories = [f"Finding {i+1}" for i in range(len(findings))]
        
        # Try to extract numeric values (this is a simplified approach)
        # In real implementation, you'd parse the statistics more carefully
        values = []
        for f in findings:
            stat = f.get('statistic', '')
            # Try to find a percentage or p-value
            if 'p<' in stat or 'p=' in stat:
                # Use significance levels as proxy
                if 'p<.001' in stat or 'p<0.001' in stat:
                    values.append(95)
                elif 'p<.01' in stat or 'p<0.01' in stat:
                    values.append(85)
                elif 'p<.05' in stat or 'p<0.05' in stat:
                    values.append(75)
                else:
                    values.append(60)
            else:
                values.append(70)  # Default
        
        # Create bar chart
        bars = ax.barh(categories, values, color=[COLORS['primary'], COLORS['secondary'], 
                                                    COLORS['accent'], COLORS['warning']][:len(categories)])
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + 2, i, f"{findings[i].get('statistic', '')[:30]}", 
                   va='center', fontsize=9)
        
        ax.set_xlabel('Significance Level / Effect Strength', fontsize=11, fontweight='bold')
        ax.set_title(f"Key Findings Summary\n{paper.get('title', '')[:80]}...", 
                    fontsize=13, fontweight='bold', pad=20)
        ax.set_xlim(0, 100)
        ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Created results visualization: {output_path}")


def create_comparison_table(papers: List[Dict], output_path: str):
    """
    Create a comparison table across all papers
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('tight')
    ax.axis('off')
    
    # Extract data for comparison
    table_data = []
    headers = ['Paper', 'Sample Size', 'Design', 'Key Method', 'Main Finding']
    
    for paper in papers[:10]:  # Limit to 10 papers for readability
        methodology = paper.get('methodology', {})
        findings = paper.get('findings', [])
        main_finding = findings[0].get('text', 'Not available')[:80] if findings else 'Not available'
        
        row = [
            paper.get('title', 'Unknown')[:40] + '...',
            methodology.get('sample_size', 'N/A'),
            methodology.get('design', 'N/A')[:20],
            methodology.get('analysis', 'N/A')[:30],
            main_finding + '...'
        ]
        table_data.append(row)
    
    # Create table
    table = ax.table(cellText=table_data, colLabels=headers,
                    cellLoc='left', loc='center',
                    colWidths=[0.25, 0.1, 0.15, 0.2, 0.3])
    
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2)
    
    # Style header
    for i in range(len(headers)):
        cell = table[(0, i)]
        cell.set_facecolor(COLORS['primary'])
        cell.set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#f0f0f0')
    
    plt.title('Cross-Paper Comparison Matrix', fontsize=16, fontweight='bold', pad=20)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Created comparison table: {output_path}")


def create_research_timeline(papers: List[Dict], output_path: str):
    """
    Create a timeline showing publication years and topics
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Extract years and group papers
    year_counts = {}
    for paper in papers:
        year = paper.get('year', '2024')
        year_counts[year] = year_counts.get(year, 0) + 1
    
    years = sorted(year_counts.keys())
    counts = [year_counts[y] for y in years]
    
    # Create bar chart
    bars = ax.bar(years, counts, color=COLORS['primary'], alpha=0.7, edgecolor='black')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_xlabel('Publication Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Papers', fontsize=12, fontweight='bold')
    ax.set_title('Research Publication Timeline', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Created timeline visualization: {output_path}")


def create_methodology_distribution(papers: List[Dict], output_path: str):
    """
    Create pie chart showing distribution of methodologies
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Count methodology types
    method_counts = {}
    for paper in papers:
        design = paper.get('methodology', {}).get('design', 'Not specified')
        # Simplify design names
        if 'experimental' in design.lower():
            method_type = 'Experimental'
        elif 'mixed' in design.lower():
            method_type = 'Mixed Methods'
        elif 'survey' in design.lower():
            method_type = 'Survey'
        elif 'qualitative' in design.lower():
            method_type = 'Qualitative'
        else:
            method_type = 'Other'
        
        method_counts[method_type] = method_counts.get(method_type, 0) + 1
    
    # Create pie chart
    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], 
                   COLORS['warning'], COLORS['success']]
    
    wedges, texts, autotexts = ax.pie(method_counts.values(), 
                                       labels=method_counts.keys(),
                                       autopct='%1.1f%%',
                                       colors=colors_list[:len(method_counts)],
                                       startangle=90,
                                       textprops={'fontsize': 11, 'weight': 'bold'})
    
    # Make percentage text more visible
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
    
    ax.set_title('Methodological Approaches Distribution', 
                fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Created methodology distribution: {output_path}")


def generate_all_visualizations(data_file: str, output_dir: str = "visualizations"):
    """
    Generate all visualizations for the digest
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load enhanced papers
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    
    print(f"Generating visualizations for {len(papers)} papers...")
    
    # Create paper-specific visualizations
    for i, paper in enumerate(papers, 1):
        paper_id = paper.get('doi', f'paper_{i}').replace('/', '_')
        
        # Methodology framework
        create_methodology_framework(
            paper, 
            f"{output_dir}/{paper_id}_methodology.png"
        )
        
        # Results visualization
        create_results_comparison(
            paper,
            f"{output_dir}/{paper_id}_results.png"
        )
    
    # Create digest-wide visualizations
    create_comparison_table(papers, f"{output_dir}/comparison_table.png")
    create_research_timeline(papers, f"{output_dir}/timeline.png")
    create_methodology_distribution(papers, f"{output_dir}/methodology_distribution.png")
    
    print(f"\n✓ Generated all visualizations in {output_dir}/")
    
    # Return paths for templates
    viz_paths = {}
    for paper in papers:
        paper_id = paper.get('doi', '').replace('/', '_')
        viz_paths[paper_id] = {
            'methodology': f"{output_dir}/{paper_id}_methodology.png",
            'results': f"{output_dir}/{paper_id}_results.png"
        }
    
    return viz_paths


if __name__ == "__main__":
    # Generate visualizations
    generate_all_visualizations("data/enhanced_papers.json")