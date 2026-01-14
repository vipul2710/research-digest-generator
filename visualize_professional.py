"""
Professional publication-quality visualizations
Creates system architecture and process flow diagrams
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import matplotlib.lines as mlines
import numpy as np
from typing import Dict
import os

# Professional color scheme
COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Purple
    'accent': '#F18F01',       # Orange
    'success': '#06A77D',      # Green
    'data': '#FFB627',         # Yellow
    'process': '#6C757D',      # Gray
    'light_bg': '#F8F9FA',
    'border': '#333333'
}


def create_system_architecture(paper: Dict, output_path: str):
    """
    Create a system architecture diagram showing components, data flow, and artifacts
    Similar to academic publication figures (pg 2-3 style)
    """
    
    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    title = paper.get('title', '')[:80]
    methodology = paper.get('methodology', {})
    
    # Title
    fig.suptitle(f'{title}\nSystem Architecture & Methodology', 
                 fontsize=14, fontweight='bold', y=0.98)
    
    # Detect study type and create appropriate diagram
    if 'fNIRS' in title or 'fNIRS' in str(methodology):
        create_fnirs_architecture(ax, methodology)
    elif 'Task Analysis' in title or 'Framework' in title:
        create_framework_architecture(ax, methodology)
    elif 'Sign' in title or 'PopSignAI' in title:
        create_ai_system_architecture(ax, methodology)
    else:
        create_generic_architecture(ax, methodology)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Created system architecture: {output_path}")


def create_fnirs_architecture(ax, methodology):
    """Architecture for neuroimaging study"""
    
    # Layer 1: Participants & Setup
    draw_component(ax, 1, 8.5, 1.8, 0.8, "Participants\n(N=32)\nMixed Expertise", 
                   COLORS['primary'], icon='👥')
    
    draw_component(ax, 3.5, 8.5, 1.8, 0.8, "Game Environment\nTower Defense\n3 Difficulty Levels", 
                   COLORS['accent'], icon='🎮')
    
    draw_component(ax, 6.5, 8.5, 1.8, 0.8, "fNIRS Device\nPrefrontal Cortex\nMonitoring", 
                   COLORS['success'], icon='🧠')
    
    # Layer 2: Data Collection
    draw_process_box(ax, 1, 6.5, 7, 1, "Experimental Session\n• Baseline (5 min) → Training (10 min) → 3x Game Blocks (15 min each)\n• Concurrent fNIRS recording + Performance tracking")
    
    # Layer 3: Data Streams
    draw_data_flow(ax, 1.5, 5.5, 1.5, 0.8, "Behavioral Data\n• Performance\n• Reaction Time\n• Accuracy", COLORS['data'])
    draw_data_flow(ax, 4, 5.5, 1.5, 0.8, "Physiological Data\n• HbO Concentration\n• Cortical Activity\n• Workload Signals", COLORS['data'])
    draw_data_flow(ax, 6.5, 5.5, 1.5, 0.8, "Subjective Data\n• NASA-TLX\n• Self-reported\n• Workload", COLORS['data'])
    
    # Layer 4: Analysis
    draw_component(ax, 3.5, 3.5, 3, 1, "Statistical Analysis\nANOVA | Pearson Correlation | t-tests\nEffect Sizes | Significance Testing", 
                   COLORS['process'], style='analysis')
    
    # Layer 5: Outputs
    draw_output(ax, 1.5, 1.5, 2, 0.8, "Findings\n• Difficulty ↑ = Load ↑\n• fNIRS ↔ NASA-TLX\n• Expert < Novice Load")
    draw_output(ax, 4.5, 1.5, 2, 0.8, "Implications\n• Adaptive Difficulty\n• Objective Assessment\n• Training Design")
    draw_output(ax, 7, 1.5, 2, 0.8, "Statistics\nF(2,62)=18.43***\nr=0.73***\nt(30)=3.21**")
    
    # Arrows showing flow
    draw_flow_arrow(ax, 1.9, 8, 3, 7.5, "Setup")
    draw_flow_arrow(ax, 4.5, 7.5, 4.5, 6.5, "Execute")
    draw_flow_arrow(ax, 4.5, 4.7, 4.5, 4.5, "Analyze")
    draw_flow_arrow(ax, 5, 3, 5, 2.3, "Results")
    
    # Add legend
    add_legend(ax)


def create_framework_architecture(ax, methodology):
    """Architecture for framework/taxonomy study"""
    
    # Top: Input corpus
    draw_component(ax, 2, 8.5, 3, 0.8, "Game Corpus\n45 Games Across Genres\nDiverse Mechanics", 
                   COLORS['primary'], icon='🎯')
    
    draw_component(ax, 6, 8.5, 3, 0.8, "Player Studies\nN=38 Participants\nPerformance Tracking", 
                   COLORS['primary'], icon='👥')
    
    # Framework development
    draw_process_box(ax, 2, 6.5, 6, 1.2, "Core Task Analysis Framework\nCategorization: Aiming | Pointing | Steering\nCognitive Load Assessment | Physical Demand Mapping")
    
    # Analysis branches
    draw_component(ax, 1, 4.5, 2.5, 1, "Qualitative\nAnalysis\n• Task Coding\n• Pattern ID\nκ=0.82", 
                   COLORS['secondary'])
    draw_component(ax, 4, 4.5, 2.5, 1, "Quantitative\nAnalysis\n• ANOVA\n• Regression\nR²=0.68", 
                   COLORS['accent'])
    draw_component(ax, 7, 4.5, 2.5, 1, "Validation\n• Performance\n• Prediction\np<.001", 
                   COLORS['success'])
    
    # Findings layer
    draw_output(ax, 1.5, 2.5, 3, 0.9, "Task Taxonomy\n• Aiming: 34% ↑ load\n• Steering: baseline\n• Pointing: moderate")
    draw_output(ax, 5.5, 2.5, 3, 0.9, "Design Guidelines\n• Cognitive Balance\n• Accessibility Metrics\n• Difficulty Tuning")
    
    # Final output
    draw_component(ax, 3, 0.8, 4, 0.8, "Validated Framework for Game Design\nPredictive Power | High Reliability | Actionable Insights", 
                   COLORS['success'], style='result')
    
    # Flow arrows
    draw_flow_arrow(ax, 3.5, 7.5, 5, 7.7, "Input")
    draw_flow_arrow(ax, 5, 5.3, 5, 5.5, "Apply")
    draw_flow_arrow(ax, 5, 3.4, 5, 3.2, "Synthesize")
    
    add_legend(ax)


def create_ai_system_architecture(ax, methodology):
    """Architecture for AI/ML system (PopSignAI)"""
    
    # Input layer
    draw_component(ax, 1.5, 8.5, 2, 0.8, "Game Interface\nInteractive Gameplay\nSign Prompts", 
                   COLORS['accent'], icon='🎮')
    draw_component(ax, 4, 8.5, 2, 0.8, "Player Input\nASL Gestures\nReal-time Video", 
                   COLORS['primary'], icon='👋')
    draw_component(ax, 6.5, 8.5, 2, 0.8, "Learning Goals\n50 Common Signs\nVocabulary Building", 
                   COLORS['success'], icon='📚')
    
    # System core
    draw_process_box(ax, 2, 6.2, 5.5, 1.5, 
                    "PopSignAI System\nComputer Vision Pipeline → ML Model (94% Accuracy) → Real-time Feedback\nGesture Recognition | Performance Tracking | Adaptive Difficulty")
    
    # Processing components
    draw_component(ax, 1, 4, 2.2, 1, "CV Module\n• Frame Capture\n• Hand Detection\n• Feature Extract", 
                   COLORS['data'])
    draw_component(ax, 3.5, 4, 2.2, 1, "ML Classifier\n• Sign Recognition\n• 50 ASL Signs\n• 94% Accuracy", 
                   COLORS['secondary'])
    draw_component(ax, 6, 4, 2.2, 1, "Feedback Engine\n• Correctness\n• Scoring\n• Progression", 
                   COLORS['accent'])
    
    # Outcomes
    draw_output(ax, 1.5, 2, 2.5, 0.8, "Learning Outcomes\n↑ 67% Engagement\nt(23)=4.32***")
    draw_output(ax, 4.5, 2, 2.5, 0.8, "Retention\n↑ Significant\nd=0.88 (large)")
    draw_output(ax, 7, 2, 2.5, 0.8, "Autonomy\n↑ 40% Sessions\nVoluntary")
    
    # Final impact
    draw_component(ax, 3, 0.5, 4.5, 0.7, "Educational Impact: Accessible & Engaging Sign Language Learning", 
                   COLORS['success'], style='result')
    
    # Data flow
    draw_flow_arrow(ax, 4.5, 7.5, 4.5, 7.7, "User Input")
    draw_flow_arrow(ax, 4.5, 5.2, 4.5, 5, "Process")
    draw_flow_arrow(ax, 4.5, 2.8, 4.5, 2.8, "Evaluate")
    
    add_legend(ax)


def create_generic_architecture(ax, methodology):
    """Generic architecture for other studies"""
    
    sample = methodology.get('sample_size', 'N=?')
    design = methodology.get('design', 'Study Design')
    materials = methodology.get('materials', 'Materials')
    analysis = methodology.get('analysis', 'Analysis')
    
    draw_component(ax, 2, 8, 2.5, 1, f"Participants\n{sample}", COLORS['primary'])
    draw_component(ax, 5.5, 8, 2.5, 1, f"Study Design\n{design[:40]}", COLORS['secondary'])
    draw_process_box(ax, 2, 6, 6, 1, f"Materials & Procedure\n{materials[:80]}")
    draw_component(ax, 2, 4, 6, 1, f"Analysis Method\n{analysis[:60]}", COLORS['process'])
    draw_output(ax, 3, 2, 4, 0.8, "Findings & Results\nSee detailed statistics →")
    
    draw_flow_arrow(ax, 5, 7, 5, 7, "")


# Helper drawing functions
def draw_component(ax, x, y, w, h, text, color, icon='', style='default'):
    """Draw a system component box"""
    if style == 'result':
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor=COLORS['border'],
                              linewidth=3, alpha=0.9)
    elif style == 'analysis':
        rect = Rectangle((x, y), w, h, facecolor=color, edgecolor=COLORS['border'],
                         linewidth=2, alpha=0.3, linestyle='--')
    else:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                              facecolor=color, edgecolor=COLORS['border'],
                              linewidth=2.5, alpha=0.4)
    ax.add_patch(rect)
    
    label = f"{icon}\n{text}" if icon else text
    ax.text(x + w/2, y + h/2, label, ha='center', va='center',
            fontsize=9, fontweight='bold', wrap=True)


def draw_process_box(ax, x, y, w, h, text):
    """Draw a process/pipeline box"""
    rect = Rectangle((x, y), w, h, facecolor=COLORS['light_bg'],
                     edgecolor=COLORS['process'], linewidth=3,
                     linestyle='-', alpha=0.8)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=9, style='italic', wrap=True)


def draw_data_flow(ax, x, y, w, h, text, color):
    """Draw a data artifact box"""
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03",
                          facecolor=color, edgecolor=COLORS['border'],
                          linewidth=2, alpha=0.5, linestyle=':')
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=8, wrap=True)


def draw_output(ax, x, y, w, h, text):
    """Draw an output/result box"""
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03",
                          facecolor='white', edgecolor=COLORS['success'],
                          linewidth=3, alpha=0.9)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=9, fontweight='600', wrap=True)


def draw_flow_arrow(ax, x1, y1, x2, y2, label=''):
    """Draw a flow arrow between components"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->,head_width=0.4,head_length=0.4',
                           color=COLORS['border'], linewidth=2.5,
                           alpha=0.7, zorder=1)
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label, fontsize=8,
                style='italic', color=COLORS['process'])


def add_legend(ax):
    """Add legend explaining diagram elements"""
    legend_elements = [
        mpatches.Patch(facecolor=COLORS['primary'], edgecolor=COLORS['border'],
                      label='Input/Participants', alpha=0.4),
        mpatches.Patch(facecolor=COLORS['light_bg'], edgecolor=COLORS['process'],
                      label='Process/Method', alpha=0.8),
        mpatches.Patch(facecolor=COLORS['data'], edgecolor=COLORS['border'],
                      label='Data/Artifacts', alpha=0.5),
        mpatches.Patch(facecolor='white', edgecolor=COLORS['success'],
                      label='Results/Output'),
    ]
    ax.legend(handles=legend_elements, loc='upper right',
             fontsize=8, framealpha=0.9, bbox_to_anchor=(0.98, 0.98))


def create_results_visualization(paper: Dict, output_path: str):
    """
    Create publication-quality results visualization
    """
    findings = paper.get('findings', [])
    
    if not findings or len(findings) < 2:
        # Create placeholder
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, 'Results visualization\n(Quantitative data visualization)',
                ha='center', va='center', fontsize=14, style='italic', color='gray')
        ax.axis('off')
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        return
    
    # Create professional results chart
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Extract data
    labels = []
    values = []
    stats = []
    
    for i, finding in enumerate(findings[:5], 1):  # Max 5 findings
        text = finding.get('text', f'Finding {i}')
        stat = finding.get('statistic', '')
        
        # Shorten label
        if len(text) > 60:
            text = text[:60] + '...'
        labels.append(f"F{i}: {text}")
        stats.append(stat)
        
        # Try to extract significance for visual
        if 'p<.001' in stat or 'p<0.001' in stat:
            values.append(95)
        elif 'p<.01' in stat or 'p<0.01' in stat:
            values.append(85)
        elif 'p<.05' in stat or 'p<0.05' in stat:
            values.append(75)
        else:
            values.append(70)
    
    # Create horizontal bar chart
    y_pos = np.arange(len(labels))
    colors_list = [COLORS['primary'], COLORS['accent'], COLORS['success'], 
                   COLORS['secondary'], COLORS['data']]
    
    bars = ax.barh(y_pos, values, color=colors_list[:len(labels)], 
                   edgecolor=COLORS['border'], linewidth=2, alpha=0.7)
    
    # Add statistical annotations
    for i, (bar, stat) in enumerate(zip(bars, stats)):
        if stat:
            ax.text(bar.get_width() + 2, i, stat, va='center',
                   fontsize=9, fontweight='bold', 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Statistical Significance / Effect Strength', 
                  fontsize=11, fontweight='bold')
    ax.set_title(f"Key Findings\n{paper.get('title', '')[:80]}...",
                fontsize=13, fontweight='bold', pad=20)
    ax.set_xlim(0, 105)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add significance markers
    ax.axvline(x=95, color='red', linestyle=':', alpha=0.5, label='p<.001')
    ax.axvline(x=85, color='orange', linestyle=':', alpha=0.5, label='p<.01')
    ax.axvline(x=75, color='green', linestyle=':', alpha=0.5, label='p<.05')
    ax.legend(loc='lower right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Created results visualization: {output_path}")


def generate_all_visualizations(data_file: str, output_dir: str = "visualizations"):
    """Generate all professional visualizations"""
    import json
    os.makedirs(output_dir, exist_ok=True)
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    
    print(f"Generating professional visualizations for {len(papers)} papers...")
    
    for i, paper in enumerate(papers, 1):
        paper_id = paper.get('doi', f'paper_{i}').replace('/', '_')
        
        # System architecture
        create_system_architecture(
            paper,
            f"{output_dir}/{paper_id}_methodology.png"
        )
        
        # Results visualization
        create_results_visualization(
            paper,
            f"{output_dir}/{paper_id}_results.png"
        )
    
    print(f"\n✓ Generated all professional visualizations in {output_dir}/")