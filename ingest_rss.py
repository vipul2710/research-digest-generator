"""
Fetch high-quality papers from ACM RSS feeds with quality filtering
"""

import feedparser
import yaml
import re
from datetime import datetime
from typing import List, Dict

# High-impact venues (h5-index > 30)
TOP_VENUES = [
    'CHI', 'CSCW', 'UIST', 'DIS', 'IMWUT', 'GROUP',
    'CHI PLAY', 'Games', 'TOG', 'TOCHI', 'PACM',
    'SIGGRAPH', 'UbiComp', 'IUI', 'MobileHCI'
]

def load_feeds(config_file: str = "feeds.yaml") -> List[str]:
    """Load RSS feed URLs from YAML config"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        feeds = []
        for category, urls in config.items():
            if urls:  # Check if not None
                feeds.extend(urls)
        return feeds
    except Exception as e:
        print(f"Error loading feeds: {e}")
        return []

def extract_doi(url: str) -> str:
    """Extract DOI from ACM URL"""
    if 'doi.org/' in url:
        return url.split('doi.org/')[-1]
    elif 'dl.acm.org/doi/' in url:
        return url.split('doi/')[-1]
    return ''

def extract_year(date_str: str) -> int:
    """Extract year from date string"""
    try:
        if date_str:
            return int(date_str[:4])
    except:
        pass
    return datetime.now().year

def is_high_quality_venue(venue: str) -> bool:
    """Check if venue is high-impact"""
    venue_upper = venue.upper()
    return any(top in venue_upper for top in TOP_VENUES)

def fetch_from_rss(feed_url: str, max_entries: int = 20) -> List[Dict]:
    """Fetch papers from single RSS feed"""
    try:
        feed = feedparser.parse(feed_url)
        papers = []
        
        for entry in feed.entries[:max_entries]:
            # Extract venue from entry
            venue = entry.get('prism_publicationname', '') or entry.get('source', '')
            
            paper = {
                'title': entry.get('title', ''),
                'authors': entry.get('author', entry.get('dc_creator', 'Unknown')),
                'abstract': entry.get('summary', entry.get('description', '')),
                'url': entry.get('link', ''),
                'published': entry.get('published', entry.get('prism_coverdate', '')),
                'doi': extract_doi(entry.get('link', '')),
                'venue': venue,
                'year': extract_year(entry.get('published', '')),
            }
            
            # Skip if no abstract
            if len(paper['abstract']) < 100:
                continue
                
            papers.append(paper)
        
        return papers
    except Exception as e:
        print(f"Error fetching feed: {e}")
        return []

def filter_quality_papers(papers: List[Dict], min_year: int = 2022) -> List[Dict]:
    """
    Filter papers by quality criteria:
    - Recent (2022+)
    - High-impact venue
    - Has substantial abstract
    """
    filtered = []
    
    for paper in papers:
        # Check year
        if paper['year'] < min_year:
            continue
        
        # Check venue quality
        if not is_high_quality_venue(paper['venue']):
            print(f"⏭️  Skipped (low-impact venue): {paper['venue']}")
            continue
        
        # Check abstract length
        if len(paper['abstract']) < 200:
            print(f"⏭️  Skipped (short abstract): {paper['title'][:50]}")
            continue
        
        filtered.append(paper)
        print(f"✅ Accepted: {paper['title'][:60]}... ({paper['venue']}, {paper['year']})")
    
    return filtered

def fetch_all_papers(max_per_feed: int = 10, min_year: int = 2022) -> List[Dict]:
    """Fetch high-quality papers from all configured feeds"""
    feeds = load_feeds()
    
    if not feeds:
        print("❌ No RSS feeds configured in feeds.yaml")
        return []
    
    all_papers = []
    
    print(f"\n📡 Fetching from {len(feeds)} RSS feeds...")
    
    for i, feed_url in enumerate(feeds, 1):
        print(f"\n[{i}/{len(feeds)}] Fetching from feed...")
        papers = fetch_from_rss(feed_url, max_per_feed)
        all_papers.extend(papers)
        print(f"  Found {len(papers)} papers")
    
    # Remove duplicates by DOI
    seen = set()
    unique = []
    for paper in all_papers:
        doi = paper.get('doi', '')
        if doi and doi not in seen:
            seen.add(doi)
            unique.append(paper)
    
    print(f"\n📊 Total unique papers: {len(unique)}")
    
    # Filter by quality
    print(f"\n🔍 Filtering for quality (min year: {min_year}, top venues only)...")
    quality_papers = filter_quality_papers(unique, min_year)
    
    print(f"\n✅ {len(quality_papers)} high-quality papers selected")
    print(f"   (Filtered out {len(unique) - len(quality_papers)} papers)")
    
    return quality_papers