"""
Plotly Visualizations Module for Research Digest Generator
Creates interactive, publication-quality visualizations with proper emoji rendering
"""

import logging
import os
import json
from typing import Dict, List, Optional
from collections import defaultdict

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Professional color scheme
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#06A77D',
    'data': '#FFB627',
    'process': '#6C757D',
    'light_bg': '#F8F9FA',
    'border': '#333333',
    'white': '#FFFFFF',
    'p001': '#E63946',    # p<.001 - high significance (red)
    'p01': '#F4A261',     # p<.01 - moderate significance (orange)
    'p05': '#2A9D8F',     # p<.05 - significance (teal)
    'ns': '#ADB5BD',      # not significant (gray)
}

# Chart dimensions
CHART_WIDTH = 1400
CHART_HEIGHT = 900
CHART_DPI = 300


def extract_sample_size(methodology: Dict) -> int:
    """
    Extract N from methodology.sample_size (e.g., "N=32")
    Returns 0 if parsing fails
    """
    sample_text = methodology.get('sample_size', 'N=?')
    try:
        # Handle formats like "N=32", "N=32 participants", "32"
        n_str = sample_text.replace('N=', '').replace('n=', '').split()[0]
        n = int(''.join(filter(str.isdigit, n_str)))
        logger.debug(f"Extracted sample size N={n} from '{sample_text}'")
        return n
    except (ValueError, IndexError, AttributeError) as e:
        logger.warning(f"Could not extract sample size from '{sample_text}': {e}")
        return 0


def create_participant_icons(n: int, max_icons: int = 15) -> str:
    """Create participant icon string with appropriate count"""
    icon_count = min(n // 10, max_icons) if n > 0 else 4
    icon_count = max(icon_count, 1)  # At least 1 icon
    return '👤' * icon_count


def get_significance_color(stat_text: str) -> str:
    """Determine color based on p-value significance"""
    stat_lower = stat_text.lower()
    if 'p<.001' in stat_lower or 'p<0.001' in stat_lower or 'p < .001' in stat_lower:
        return COLORS['p001']
    elif 'p<.01' in stat_lower or 'p<0.01' in stat_lower or 'p < .01' in stat_lower:
        return COLORS['p01']
    elif 'p<.05' in stat_lower or 'p<0.05' in stat_lower or 'p < .05' in stat_lower:
        return COLORS['p05']
    else:
        return COLORS['ns']


def get_significance_value(stat_text: str) -> float:
    """Convert significance to numeric value for bar chart"""
    stat_lower = stat_text.lower()
    if 'p<.001' in stat_lower or 'p<0.001' in stat_lower:
        return 95
    elif 'p<.01' in stat_lower or 'p<0.01' in stat_lower:
        return 85
    elif 'p<.05' in stat_lower or 'p<0.05' in stat_lower:
        return 75
    else:
        return 60


def _extract_short_label(text: str, max_words: int = 4) -> str:
    """Extract a short label (2-5 words) from longer text."""
    if not text or text in ['Study Design', 'Study Materials', 'Data Collection', 'Statistical Analysis']:
        return text
    words = str(text).split()[:max_words]
    return ' '.join(words)


def _format_hover_text(label: str, full_text: str) -> str:
    """Format hover text with label and full details."""
    if full_text and len(full_text) > len(label):
        return f"<b>{label}</b><br>{full_text}"
    return f"<b>{label}</b>"


def create_methodology_flowchart(paper: Dict, output_path: str):
    """
    Create conceptual research methodology overview using Plotly.
    
    Design principles:
    - Short labels (2-5 words) with key quantitative markers in boxes
    - Full details in hover text
    - Horizontal grid layout (conceptual overview, not pipeline)
    - Keep emojis for visual clarity
    - Suitable for academic paper Figure 1
    """
    logger.info(f"Creating methodology overview for: {paper.get('title', 'Unknown')[:50]}...")
    
    methodology = paper.get('methodology', {})
    title = paper.get('title', 'Research Study')[:80]
    
    # Extract sample size
    n = extract_sample_size(methodology)
    participant_icons = create_participant_icons(n, max_icons=8)
    sample_text = methodology.get('sample_size', f'N={n}' if n > 0 else 'N=?')
    
    # Extract full methodology details for hover text
    design_full = methodology.get('design', 'Study Design')
    materials_full = methodology.get('materials', 'Study Materials')
    if isinstance(materials_full, list):
        materials_full = ', '.join(materials_full)
    procedures_full = methodology.get('procedures', 'Data Collection')
    if isinstance(procedures_full, list):
        procedures_full = ', '.join(procedures_full)
    analysis_full = methodology.get('analysis', 'Statistical Analysis')
    if isinstance(analysis_full, list):
        analysis_full = ', '.join(analysis_full)
    
    # Create SHORT labels for boxes (2-5 words + key metric)
    design_short = _extract_short_label(design_full, 3)
    materials_short = _extract_short_label(str(materials_full), 3)
    procedures_short = _extract_short_label(str(procedures_full), 3)
    analysis_short = _extract_short_label(str(analysis_full), 3)
    
    # Create figure with subplots for conceptual grid layout
    fig = go.Figure()
    
    # Define grid layout positions (2 rows x 3 columns for conceptual overview)
    # Row 1: Participants, Design, Materials
    # Row 2: Measures, Analysis, Outcomes
    components = [
        # Row 1
        {
            'x': 0.17, 'y': 0.70, 'w': 0.22, 'h': 0.25,
            'emoji': '👥', 'label': 'Participants',
            'value': f'{participant_icons}\n{sample_text}',
            'hover': f'<b>👥 Participants</b><br>Sample: {sample_text}<br>N = {n} participants',
            'color': COLORS['primary']
        },
        {
            'x': 0.50, 'y': 0.70, 'w': 0.22, 'h': 0.25,
            'emoji': '📋', 'label': 'Design',
            'value': design_short,
            'hover': _format_hover_text('📋 Experimental Design', design_full),
            'color': COLORS['secondary']
        },
        {
            'x': 0.83, 'y': 0.70, 'w': 0.22, 'h': 0.25,
            'emoji': '🔧', 'label': 'Materials',
            'value': materials_short,
            'hover': _format_hover_text('🔧 Materials & Stimuli', str(materials_full)),
            'color': COLORS['accent']
        },
        # Row 2
        {
            'x': 0.17, 'y': 0.30, 'w': 0.22, 'h': 0.25,
            'emoji': '📊', 'label': 'Measures',
            'value': procedures_short,
            'hover': _format_hover_text('📊 Data Collection', str(procedures_full)),
            'color': COLORS['data']
        },
        {
            'x': 0.50, 'y': 0.30, 'w': 0.22, 'h': 0.25,
            'emoji': '📈', 'label': 'Analysis',
            'value': analysis_short,
            'hover': _format_hover_text('📈 Statistical Analysis', str(analysis_full)),
            'color': COLORS['process']
        },
        {
            'x': 0.83, 'y': 0.30, 'w': 0.22, 'h': 0.25,
            'emoji': '✅', 'label': 'Outcomes',
            'value': 'See Findings',
            'hover': '<b>✅ Key Outcomes</b><br>See Results visualization',
            'color': COLORS['success']
        },
    ]
    
    # Add invisible scatter points for hover functionality
    for comp in components:
        fig.add_trace(go.Scatter(
            x=[comp['x']],
            y=[comp['y']],
            mode='markers',
            marker=dict(size=80, opacity=0),
            hoverinfo='text',
            hovertext=comp['hover'],
            showlegend=False
        ))
    
    # Draw component boxes
    for comp in components:
        x0 = comp['x'] - comp['w']/2
        y0 = comp['y'] - comp['h']/2
        x1 = comp['x'] + comp['w']/2
        y1 = comp['y'] + comp['h']/2
        
        # Add rectangle shape
        fig.add_shape(
            type="rect",
            x0=x0, y0=y0, x1=x1, y1=y1,
            fillcolor=comp['color'],
            opacity=0.75,
            line=dict(color=COLORS['border'], width=2),
            layer='below'
        )
        
        # Add emoji + label at top of box
        fig.add_annotation(
            x=comp['x'], y=comp['y'] + 0.06,
            text=f"<b>{comp['emoji']} {comp['label']}</b>",
            showarrow=False,
            font=dict(size=14, color='white', family='Arial'),
            align='center'
        )
        
        # Add value/metric below
        fig.add_annotation(
            x=comp['x'], y=comp['y'] - 0.03,
            text=comp['value'],
            showarrow=False,
            font=dict(size=11, color='white', family='Arial'),
            align='center'
        )
    
    # Draw connecting arrows (flow indicators)
    arrow_pairs = [
        (0, 1), (1, 2),  # Row 1 flow
        (0, 3), (1, 4), (2, 5),  # Vertical connections
        (3, 4), (4, 5),  # Row 2 flow
    ]
    
    for start_idx, end_idx in arrow_pairs:
        start = components[start_idx]
        end = components[end_idx]
        
        # Calculate arrow positions
        if start['y'] == end['y']:  # Horizontal
            ax = start['x'] + start['w']/2 - 0.02
            ay = start['y']
            x = end['x'] - end['w']/2 + 0.02
            y = end['y']
        else:  # Vertical
            ax = start['x']
            ay = start['y'] - start['h']/2
            x = end['x']
            y = end['y'] + end['h']/2
        
        fig.add_annotation(
            x=x, y=y,
            ax=ax, ay=ay,
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor=COLORS['process'],
            opacity=0.5
        )
    
    # Add sample size progress bar at top
    if n > 0:
        progress_pct = min(n / 150, 1.0)  # Normalize to max 150
        
        fig.add_shape(
            type="rect",
            x0=0.1, y0=0.92, x1=0.9, y1=0.96,
            fillcolor=COLORS['light_bg'],
            line=dict(color=COLORS['border'], width=1),
        )
        
        fig.add_shape(
            type="rect",
            x0=0.1, y0=0.92, x1=0.1 + 0.8 * progress_pct, y1=0.96,
            fillcolor=COLORS['primary'],
            opacity=0.8,
            line=dict(width=0),
        )
        
        fig.add_annotation(
            x=0.5, y=0.94,
            text=f"📊 Sample: {sample_text}",
            showarrow=False,
            font=dict(size=12, color=COLORS['border'], family='Arial Bold'),
        )
    
    # Add legend/caption at bottom
    fig.add_annotation(
        x=0.5, y=0.02,
        text="<i>Hover over components for detailed methodology information</i>",
        showarrow=False,
        font=dict(size=10, color='gray', family='Arial'),
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"<b>Research Methodology Overview</b><br><sub>{title}</sub>",
            x=0.5,
            font=dict(size=16, family='Arial')
        ),
        xaxis=dict(range=[0, 1], showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        yaxis=dict(range=[0, 1], showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=100, b=50),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    
    # Save PNG
    png_path = output_path.replace('.png', '') + '.png'
    try:
        fig.write_image(png_path, scale=2)
        logger.info(f"Saved methodology PNG: {png_path}")
        print(f"  ✓ Methodology overview (PNG)")
    except Exception as e:
        logger.error(f"Error saving PNG: {e}")
        print(f"  ⚠️ Could not save PNG (kaleido may not be installed)")
    
    # Save interactive HTML
    html_path = output_path.replace('.png', '_interactive.html')
    fig.write_html(html_path, include_plotlyjs='cdn')
    logger.info(f"Saved methodology HTML: {html_path}")
    print(f"  ✓ Methodology overview (HTML)")


def create_results_bar_chart(paper: Dict, output_path: str):
    """
    Create horizontal bar chart of findings using Plotly.
    
    Features:
    - Parse p-values to determine significance
    - Color code bars by significance level
    - Add vertical lines at p<.001, p<.01, p<.05 thresholds
    - Save PNG + HTML
    """
    logger.info(f"Creating results chart for: {paper.get('title', 'Unknown')[:50]}...")
    
    findings = paper.get('findings', [])
    title = paper.get('title', 'Research Study')[:80]
    
    if not findings or len(findings) < 1:
        # Create placeholder chart
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="Results visualization<br>(Quantitative findings pending)",
            showarrow=False,
            font=dict(size=16, color='gray'),
            xref='paper', yref='paper'
        )
        fig.update_layout(
            title=dict(text=f"<b>Key Findings</b><br><sub>{title}</sub>", x=0.5),
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            width=CHART_WIDTH,
            height=CHART_HEIGHT // 2,
            plot_bgcolor='white',
        )
    else:
        # Process findings
        labels = []
        values = []
        colors = []
        stats = []
        
        for i, finding in enumerate(findings[:6], 1):
            text = finding.get('text', f'Finding {i}')
            stat = finding.get('statistic', '')
            
            # Truncate long text
            if len(text) > 55:
                text = text[:55] + '...'
            
            labels.append(f"F{i}: {text}")
            stats.append(stat)
            values.append(get_significance_value(stat))
            colors.append(get_significance_color(stat))
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=labels,
            x=values,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color=COLORS['border'], width=1.5)
            ),
            text=stats,
            textposition='outside',
            textfont=dict(size=10, family='Arial'),
            hovertemplate='<b>%{y}</b><br>Significance: %{x}<br>Stats: %{text}<extra></extra>'
        ))
        
        # Add significance threshold lines
        fig.add_vline(x=95, line=dict(color=COLORS['p001'], width=2, dash='dot'),
                      annotation_text="p<.001", annotation_position="top")
        fig.add_vline(x=85, line=dict(color=COLORS['p01'], width=2, dash='dot'),
                      annotation_text="p<.01", annotation_position="top")
        fig.add_vline(x=75, line=dict(color=COLORS['p05'], width=2, dash='dot'),
                      annotation_text="p<.05", annotation_position="top")
        
        fig.update_layout(
            title=dict(
                text=f"<b>Key Findings</b><br><sub>{title}</sub>",
                x=0.5,
                font=dict(size=16, family='Arial')
            ),
            xaxis=dict(
                title='Statistical Significance / Effect Strength',
                range=[0, 110],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
            ),
            yaxis=dict(
                title='',
                autorange='reversed',
                tickfont=dict(size=10),
            ),
            width=CHART_WIDTH,
            height=max(400, len(labels) * 80 + 200),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=350, r=100, t=100, b=80),
            showlegend=False,
        )
    
    # Save PNG
    png_path = output_path.replace('.png', '') + '.png'
    try:
        fig.write_image(png_path, scale=2)
        logger.info(f"Saved results PNG: {png_path}")
        print(f"  ✓ Results chart (PNG)")
    except Exception as e:
        logger.error(f"Error saving PNG: {e}")
        print(f"  ⚠️ Could not save PNG (kaleido may not be installed)")
    
    # Save interactive HTML
    html_path = output_path.replace('.png', '_interactive.html')
    fig.write_html(html_path, include_plotlyjs='cdn')
    logger.info(f"Saved results HTML: {html_path}")
    print(f"  ✓ Results chart (HTML)")


def create_domain_distribution_chart(papers: List[Dict], output_path: str):
    """
    Create pie chart of research domains with percentages.
    """
    logger.info(f"Creating domain distribution chart for {len(papers)} papers")
    
    # Count papers by domain
    domain_counts = defaultdict(int)
    for paper in papers:
        domain = paper.get('research_domain', 'General')
        domain_counts[domain] += 1
    
    labels = list(domain_counts.keys())
    values = list(domain_counts.values())
    
    # Define colors for domains
    domain_colors = [
        COLORS['primary'], COLORS['secondary'], COLORS['accent'],
        COLORS['success'], COLORS['data'], COLORS['process'],
        '#9B59B6', '#3498DB', '#E74C3C', '#1ABC9C'
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(
            colors=domain_colors[:len(labels)],
            line=dict(color=COLORS['white'], width=2)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=11),
        hovertemplate='<b>%{label}</b><br>Papers: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text=f"<b>Research Domain Distribution</b><br><sub>{len(papers)} papers across {len(labels)} domains</sub>",
            x=0.5,
            font=dict(size=18, family='Arial')
        ),
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=100, b=50),
        annotations=[dict(
            text=f'📚<br>{len(papers)}<br>Papers',
            x=0.5, y=0.5,
            font=dict(size=20, family='Arial'),
            showarrow=False
        )]
    )
    
    # Save PNG
    png_path = output_path.replace('.png', '') + '.png'
    try:
        fig.write_image(png_path, scale=2)
        logger.info(f"Saved domain distribution PNG: {png_path}")
        print(f"✓ Domain distribution chart (PNG)")
    except Exception as e:
        logger.error(f"Error saving PNG: {e}")
        print(f"⚠️ Could not save PNG")
    
    # Save interactive HTML
    html_path = output_path.replace('.png', '_interactive.html')
    fig.write_html(html_path, include_plotlyjs='cdn')
    logger.info(f"Saved domain distribution HTML: {html_path}")
    print(f"✓ Domain distribution chart (HTML)")


def create_timeline_chart(papers: List[Dict], output_path: str):
    """
    Create bar chart of publication timeline.
    """
    logger.info(f"Creating timeline chart for {len(papers)} papers")
    
    # Count papers by year-month
    date_counts = defaultdict(int)
    for paper in papers:
        year = paper.get('year', 'Unknown')
        month = paper.get('month')
        if month:
            date_key = f"{year}-{int(month):02d}"
        else:
            date_key = str(year)
        date_counts[date_key] += 1
    
    # Sort by date
    sorted_dates = sorted(date_counts.keys())
    labels = sorted_dates
    values = [date_counts[d] for d in sorted_dates]
    
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=COLORS['primary'],
            line=dict(color=COLORS['border'], width=1)
        ),
        text=values,
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Papers: %{y}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text=f"<b>Publication Timeline</b><br><sub>{len(papers)} papers</sub>",
            x=0.5,
            font=dict(size=18, family='Arial')
        ),
        xaxis=dict(
            title='Publication Date',
            tickangle=45,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            title='Number of Papers',
            gridcolor='rgba(0,0,0,0.1)',
        ),
        width=CHART_WIDTH,
        height=CHART_HEIGHT // 2 + 100,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=80, r=50, t=100, b=100),
        bargap=0.3,
    )
    
    # Save PNG
    png_path = output_path.replace('.png', '') + '.png'
    try:
        fig.write_image(png_path, scale=2)
        logger.info(f"Saved timeline PNG: {png_path}")
        print(f"✓ Timeline chart (PNG)")
    except Exception as e:
        logger.error(f"Error saving PNG: {e}")
        print(f"⚠️ Could not save PNG")
    
    # Save interactive HTML
    html_path = output_path.replace('.png', '_interactive.html')
    fig.write_html(html_path, include_plotlyjs='cdn')
    logger.info(f"Saved timeline HTML: {html_path}")
    print(f"✓ Timeline chart (HTML)")


def generate_all_visualizations(data_file: str, output_dir: str = "visualizations") -> Dict[str, List[str]]:
    """
    Main function to generate all visualizations.
    
    - Load enhanced_papers.json
    - Generate 2 charts per paper (methodology + results)
    - Generate 2 digest-wide charts (domain distribution + timeline)
    - Create both PNG and HTML versions
    
    Args:
        data_file: Path to enhanced_papers.json
        output_dir: Output directory for visualizations
    
    Returns:
        Dict with lists of generated file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Load data
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    logger.info(f"Loaded {len(papers)} papers from {data_file}")
    
    print(f"\n{'='*50}")
    print(f"GENERATING PLOTLY VISUALIZATIONS")
    print(f"{'='*50}")
    print(f"Papers: {len(papers)}")
    print(f"Output: {output_dir}/")
    print(f"{'='*50}")
    
    generated_files = {
        'methodology': [],
        'results': [],
        'digest_wide': []
    }
    
    # Generate per-paper visualizations
    for i, paper in enumerate(papers, 1):
        # Create unique ID: index + DOI (sanitized for filenames)
        doi = paper.get('doi', f'paper_{i}').split('?')[0]
        paper_id = f"{i}_{doi.replace('/', '_').replace('.', '_')}"
        
        print(f"\n[{i}/{len(papers)}] {paper.get('title', '')[:50]}...")
        
        # Methodology flowchart
        methodology_path = f"{output_dir}/{paper_id}_methodology.png"
        create_methodology_flowchart(paper, methodology_path)
        generated_files['methodology'].append(methodology_path)
        
        # Results bar chart
        results_path = f"{output_dir}/{paper_id}_results.png"
        create_results_bar_chart(paper, results_path)
        generated_files['results'].append(results_path)
    
    # Generate digest-wide visualizations
    print(f"\n{'='*50}")
    print(f"GENERATING DIGEST-WIDE CHARTS")
    print(f"{'='*50}")
    
    # Domain distribution
    domain_path = f"{output_dir}/digest_domain_distribution.png"
    create_domain_distribution_chart(papers, domain_path)
    generated_files['digest_wide'].append(domain_path)
    
    # Timeline
    timeline_path = f"{output_dir}/digest_timeline.png"
    create_timeline_chart(papers, timeline_path)
    generated_files['digest_wide'].append(timeline_path)
    
    # Summary
    total_charts = len(generated_files['methodology']) + len(generated_files['results']) + len(generated_files['digest_wide'])
    print(f"\n{'='*50}")
    print(f"✅ VISUALIZATION COMPLETE")
    print(f"{'='*50}")
    print(f"Per-paper charts: {len(papers) * 2} (methodology + results)")
    print(f"Digest-wide charts: 2 (domain distribution + timeline)")
    print(f"Total charts: {total_charts}")
    print(f"Output formats: PNG + Interactive HTML")
    print(f"Location: {output_dir}/")
    print(f"{'='*50}")
    
    logger.info(f"Generated {total_charts} visualizations")
    
    return generated_files


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Plotly visualizations')
    parser.add_argument('--data-file', type=str, default='data/enhanced_papers.json',
                       help='Path to enhanced papers JSON')
    parser.add_argument('--output-dir', type=str, default='visualizations',
                       help='Output directory')
    
    args = parser.parse_args()
    
    if os.path.exists(args.data_file):
        generate_all_visualizations(args.data_file, args.output_dir)
    else:
        print(f"Error: Data file not found: {args.data_file}")
        print("Run the main pipeline first to generate enhanced_papers.json")
