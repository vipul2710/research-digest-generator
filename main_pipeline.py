"""
Complete standalone pipeline for generating professor-level research digest
RSS-powered - automatically fetches latest papers from ACM feeds
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from paper_tracker import filter_new_papers, get_stats

# Import our enhanced modules
from improved_summarize import summarize_all_papers
from plotly_visualizations import generate_all_visualizations
from improved_render import render_digest
from enhanced_rss_feeds import fetch_papers_from_all_feeds
from config import OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_directories():
    """Create necessary directories"""
    directories = ['data', 'visualizations', 'output']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directory ready: {directory}/")


def normalize_papers(raw_papers: List[Dict]) -> List[Dict]:
    """
    Normalize paper data to consistent format
    Extracts and structures all relevant fields
    """
    print("\nNormalizing paper data...")
    logger.info(f"Normalizing {len(raw_papers)} papers")
    
    normalized = []
    for paper in raw_papers:
        normalized_paper = {
            "title": paper.get("title", "Unknown Title"),
            "authors": paper.get("authors", "Unknown Authors"),
            "abstract": paper.get("abstract", "No abstract available"),
            "doi": paper.get("doi", ""),
            "venue": paper.get("venue", "Unknown Venue"),
            "year": str(paper.get("year", "2024")),
            "month": paper.get("month"),
            "published_date": paper.get("published_date"),
            "citations": paper.get("citations", 0),
            "url": paper.get("url", ""),
            "research_domain": paper.get("research_domain", "General")
        }
        normalized.append(normalized_paper)
        logger.debug(f"Normalized paper: {normalized_paper['title'][:50]}...")
    
    print(f"✓ Normalized {len(normalized)} papers")
    logger.info(f"Normalization complete: {len(normalized)} papers")
    return normalized


def main(
    max_papers: int = 20,
    start_year: int = 2024,
    start_month: Optional[int] = None,
    end_year: Optional[int] = None,
    end_month: Optional[int] = None
):
    """
    Complete pipeline:
    1. Fetch papers from ACM RSS feeds (10 research domains, with date filtering)
    2. Normalize data
    3. Generate deep summaries
    4. Create visualizations (Plotly)
    5. Render PDF
    
    Args:
        max_papers: Maximum number of papers to include in digest
        start_year: Start year for filtering (required)
        start_month: Start month (1-12, optional)
        end_year: End year (optional)
        end_month: End month (1-12, optional)
    """
    
    # Build date range string for logging
    date_range_str = f"{start_year}"
    if start_month:
        date_range_str = f"{start_year}-{start_month:02d}"
        if end_year or end_month:
            end_display = f"{end_year or start_year}-{end_month:02d}" if end_month else f"{end_year}"
            date_range_str += f" to {end_display}"
    
    logger.info(f"Starting pipeline: max_papers={max_papers}, date_range={date_range_str}")
    
    print("="*70)
    print("PROFESSOR-LEVEL RESEARCH DIGEST GENERATOR")
    print("="*70)
    print(f"Date Range: {date_range_str}")
    print(f"Max Papers: {max_papers}")
    print()
    
    # Ensure directories exist
    ensure_directories()
    
    # Step 1: Fetch papers from RSS (10 research domains)
    print(f"\n{'='*70}")
    print(f"[1/5] FETCHING PAPERS FROM 10 RESEARCH DOMAINS")
    print(f"{'='*70}")
    
    try:
        # Fetch from all 10 domains with date filtering
        raw_papers = fetch_papers_from_all_feeds(
            max_per_feed=15,
            start_year=start_year,
            start_month=start_month,
            end_year=end_year,
            end_month=end_month
        )
        logger.info(f"Fetched {len(raw_papers)} papers from all domains")
        
        if not raw_papers:
            print(f"\n❌ No papers found for the specified date range.")
            print(f"   Requested: {date_range_str}")
            print(f"   Try adjusting --start-year, --start-month, --end-year, --end-month")
            logger.warning(f"No papers found for date range: {date_range_str}")
            sys.exit(1)
        
        # Filter out previously processed papers
        print(f"\n🔍 Filtering for NEW papers (checking against history)...")
        new_papers = filter_new_papers(raw_papers)
        
        if not new_papers:
            print("\n⚠️  No new papers found (all previously processed)")
            stats = get_stats()
            print(f"📊 Total papers in history: {stats['total_processed']}")
            print(f"📅 By year: {stats['by_year']}")
            sys.exit(0)
        
        # Limit to max_papers
        papers_to_use = new_papers[:max_papers]
        
        with open('data/raw_papers.json', 'w', encoding='utf-8') as f:
            json.dump(papers_to_use, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Using {len(papers_to_use)} NEW papers for digest")
        print(f"   (Skipped {len(raw_papers) - len(new_papers)} already processed)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)    
    # Step 2: Normalize data
    print(f"\n{'='*70}")
    print(f"[2/5] NORMALIZING DATA")
    print(f"{'='*70}")
    
    try:
        # Use papers_to_use (limited by max_papers), NOT raw_papers
        normalized_papers = normalize_papers(papers_to_use)
        
        with open('data/normalized_papers.json', 'w', encoding='utf-8') as f:
            json.dump(normalized_papers, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Saved normalized papers to: data/normalized_papers.json")
        
    except Exception as e:
        print(f"✗ Error normalizing papers: {e}")
        sys.exit(1)
    
    # Step 3: Generate deep summaries
    print(f"\n{'='*70}")
    print(f"[3/5] GENERATING PROFESSOR-LEVEL ANALYSIS")
    print(f"{'='*70}")
    print(f"⏱️  This may take 5-10 minutes depending on paper count...")
    print(f"💰 Estimated cost: ${len(normalized_papers) * 0.15:.2f} (using GPT-4)")
    
    try:
        enhanced_data = summarize_all_papers(normalized_papers)
        
        with open('data/enhanced_papers.json', 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Generated deep analysis for {len(enhanced_data['papers'])} papers")
        print(f"✓ Created cross-paper synthesis")
        print(f"✓ Saved to: data/enhanced_papers.json")
        
    except Exception as e:
        print(f"\n✗ Error generating summaries: {e}")
        print(f"💡 Make sure OPENAI_API_KEY is set in .env file")
        print(f"💡 Check you have sufficient API credits")
        sys.exit(1)
    
    # Step 4: Create visualizations
    print(f"\n{'='*70}")
    print(f"[4/5] CREATING RESEARCH VISUALIZATIONS")
    print(f"{'='*70}")
    
    try:
        viz_paths = generate_all_visualizations('data/enhanced_papers.json')
        
        paper_count = len(enhanced_data['papers'])
        print(f"\n✓ Generated {paper_count * 2} paper-specific visualizations (methodology + results)")
        print(f"✓ Generated 2 digest-wide visualizations (domain distribution + timeline)")
        print(f"✓ Both PNG and interactive HTML versions created")
        print(f"✓ Saved to: visualizations/")
        logger.info(f"Visualizations complete: {paper_count * 2 + 2} total charts")
        
    except Exception as e:
        print(f"\n✗ Error creating visualizations: {e}")
        print(f"💡 Make sure plotly and kaleido are installed: pip install plotly kaleido")
        logger.error(f"Visualization error: {e}", exc_info=True)
        sys.exit(1)
    
    # Step 5: Render PDF
    print(f"\n{'='*70}")
    print(f"[5/5] RENDERING FINAL PDF")
    print(f"{'='*70}")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"output/research_digest_{timestamp}.pdf"
    
    try:
        pdf_path = render_digest(
            'data/enhanced_papers.json',
            template_file='digest.html',
            output_pdf=output_filename
        )
        
        if pdf_path and os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / 1024 / 1024
            print(f"\n{'='*70}")
            print(f"✅ SUCCESS! RESEARCH DIGEST GENERATED")
            print(f"{'='*70}")
            print(f"📄 Location: {pdf_path}")
            print(f"📊 Size: {file_size:.2f} MB")
            print(f"📚 Papers: {len(enhanced_data['papers'])}")
            print(f"🎨 Visualizations: {paper_count * 2 + 2} (PNG + HTML)")
            print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}")
            
            # Also save HTML version
            html_path = output_filename.replace('.pdf', '.html')
            if os.path.exists(html_path):
                print(f"🌐 HTML version: {html_path}")
            
        else:
            print(f"\n✗ PDF generation failed. Check error messages above.")
            print(f"💡 Make sure wkhtmltopdf is installed")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Error rendering PDF: {e}")
        print(f"💡 Check wkhtmltopdf installation")
        sys.exit(1)


def generate_sample_digest():
    """
    Generate a sample digest with just 3 papers for testing
    Faster and cheaper for initial testing
    """
    print("="*70)
    print("GENERATING SAMPLE DIGEST (3 PAPERS FROM 10 DOMAINS)")
    print("="*70)
    logger.info("Starting sample digest generation")
    
    ensure_directories()
    
    # Fetch and use only first 3 papers from all domains
    papers = fetch_papers_from_all_feeds(
        max_per_feed=2,  # Small number per feed for sample
        start_year=2024,
        start_month=None,
        end_year=None,
        end_month=None
    )
    papers = papers[:3]  # Limit to 3 papers
    normalized = normalize_papers(papers)
    
    # Save sample data
    with open('data/normalized_papers_sample.json', 'w', encoding='utf-8') as f:
        json.dump(normalized, f, indent=2)
    
    print("\n💰 Sample cost estimate: $0.50 (3 papers)")
    print("⏱️  Estimated time: 2-3 minutes")
    
    # Process
    enhanced_data = summarize_all_papers(normalized)
    
    with open('data/enhanced_papers_sample.json', 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, indent=2)
    
    generate_all_visualizations('data/enhanced_papers_sample.json')
    
    pdf_path = render_digest(
        'data/enhanced_papers_sample.json',
        output_pdf='output/sample_digest.pdf'
    )
    
    if pdf_path and os.path.exists(pdf_path):
        print(f"\n✅ Sample digest created: {pdf_path}")
        print(f"📊 Review this before generating full digest")
    else:
        print(f"\n✗ Sample generation failed")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate professor-level research digest from ACM RSS feeds (10 domains)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_pipeline.py --sample                    # Generate sample with 3 papers
  python main_pipeline.py --max-papers 20 --start-year 2024
  
  # Monthly filtering examples:
  python main_pipeline.py --start-year 2024 --start-month 10
  python main_pipeline.py --start-year 2024 --start-month 10 --end-month 10
  python main_pipeline.py --start-year 2024 --start-month 10 --end-month 12
  python main_pipeline.py --start-year 2024 --start-month 10 --end-year 2025 --end-month 1
  
NOTE: Papers are fetched from 10 research domains with date filtering!
        """
    )
    
    parser.add_argument('--sample', action='store_true', 
                       help='Generate sample digest with 3 papers (fast, cheap test)')
    parser.add_argument('--max-papers', type=int, default=20, 
                       help='Maximum number of papers (default: 20)')
    parser.add_argument('--start-year', type=int, default=2024, 
                       help='Start year for papers (default: 2024)')
    parser.add_argument('--start-month', type=int, choices=range(1, 13), metavar='MONTH',
                       help='Start month (1-12, optional)')
    parser.add_argument('--end-year', type=int,
                       help='End year (optional)')
    parser.add_argument('--end-month', type=int, choices=range(1, 13), metavar='MONTH',
                       help='End month (1-12, optional)')
    
    args = parser.parse_args()
    
    # Validation
    if args.end_month and not args.end_year:
        print("❌ Error: --end-month requires --end-year")
        logger.error("Invalid args: --end-month without --end-year")
        sys.exit(1)
    
    if args.end_year and args.end_year < args.start_year:
        print("❌ Error: end-year must be >= start-year")
        logger.error(f"Invalid args: end-year {args.end_year} < start-year {args.start_year}")
        sys.exit(1)
    
    if args.start_month and args.end_month and not args.end_year:
        # Same year, different months
        if args.end_month < args.start_month:
            print("❌ Error: end-month must be >= start-month within same year")
            logger.error(f"Invalid args: end-month {args.end_month} < start-month {args.start_month}")
            sys.exit(1)
    
    # Check if OpenAI API key is set
    if not OPENAI_API_KEY:
        print("✗ Error: OPENAI_API_KEY not found in environment")
        print("💡 Create a .env file with: OPENAI_API_KEY=your-key-here")
        logger.error("Missing OPENAI_API_KEY")
        sys.exit(1)
    
    logger.info(f"Arguments: {args}")
    
    # Run sample or full pipeline
    if args.sample:
        generate_sample_digest()
    else:
        main(
            max_papers=args.max_papers,
            start_year=args.start_year,
            start_month=args.start_month,
            end_year=args.end_year,
            end_month=args.end_month
        )