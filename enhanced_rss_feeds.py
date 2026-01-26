"""
Enhanced RSS Feeds Module for Research Digest Generator
Fetches papers from 10 research domains with date filtering support
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

import feedparser
from dateutil import parser as date_parser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_comprehensive_feeds() -> List[Dict[str, str]]:
    """
    Return list of 10 RSS feed configurations for different research domains.
    Each feed has: name (domain), url (ACM RSS feed URL)
    """
    base_url = "https://dl.acm.org/action/showFeed?ui=0&mi=19n0l1t&type=search&feed=rss&query=%2526AllField%253D{term}%2526content%253Dstandard%2526target%253Ddefault%2526sortBy%253Drecency"
    
    domains = [
        {"name": "Gameplay Research", "search_term": "Gameplay"},
        {"name": "HCI Research", "search_term": "Human%20Computer%20Interaction"},
        {"name": "Virtual Reality", "search_term": "Virtual%20Reality"},
        {"name": "Augmented Reality", "search_term": "Augmented%20Reality"},
        {"name": "AI in Games", "search_term": "Artificial%20Intelligence%20Games"},
        {"name": "Player Experience", "search_term": "Player%20Experience"},
        {"name": "Game Analytics", "search_term": "Game%20Analytics"},
        {"name": "Serious Games", "search_term": "Serious%20Games"},
        {"name": "Game Accessibility", "search_term": "Game%20Accessibility"},
        {"name": "Game Design", "search_term": "Game%20Design"},
    ]
    
    feeds = []
    for domain in domains:
        feed_config = {
            "name": domain["name"],
            "url": base_url.format(term=domain["search_term"])
        }
        feeds.append(feed_config)
        logger.debug(f"Configured feed for domain: {domain['name']}")
    
    logger.info(f"Configured {len(feeds)} research domain feeds")
    return feeds


def parse_date_from_rss(date_str: str) -> Optional[datetime]:
    """
    Parse various RSS date formats using dateutil.
    Returns None if parsing fails.
    
    Handles formats like:
    - "Mon, 01 Jan 2024 00:00:00 GMT"
    - "2024-01-01T00:00:00Z"
    - "2024-01-01"
    - etc.
    """
    if not date_str:
        logger.debug("Empty date string provided")
        return None
    
    try:
        parsed_date = date_parser.parse(date_str, fuzzy=True)
        logger.debug(f"Parsed date '{date_str}' to {parsed_date}")
        return parsed_date
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse date '{date_str}': {e}")
        return None


def is_in_date_range(
    paper_date: Optional[datetime],
    paper_year_fallback: Optional[int],
    paper_month_fallback: Optional[int],
    start_year: int,
    start_month: Optional[int] = None,
    end_year: Optional[int] = None,
    end_month: Optional[int] = None
) -> bool:
    """
    Check if paper falls within the specified date range.
    STRICT filtering: papers with unknown dates are EXCLUDED when month filtering is active.
    
    Args:
        paper_date: The publication date of the paper (parsed datetime)
        paper_year_fallback: Fallback year if paper_date is None
        paper_month_fallback: Fallback month if paper_date is None
        start_year: Start year (required)
        start_month: Start month (1-12, optional)
        end_year: End year (optional, defaults to start_year if start_month specified)
        end_month: End month (1-12, optional)
    
    Returns:
        True if paper is within range, False otherwise
    """
    # Determine paper year and month
    if paper_date is not None:
        paper_year = paper_date.year
        paper_month = paper_date.month
    elif paper_year_fallback is not None:
        paper_year = paper_year_fallback
        paper_month = paper_month_fallback if paper_month_fallback else 1
    else:
        # No date info at all - EXCLUDE when strict filtering is active
        if start_month is not None:
            logger.debug("No paper date, strict month filtering active - EXCLUDED")
            return False
        else:
            logger.debug("No paper date, year-only filtering - EXCLUDED (unknown year)")
            return False
    
    # Filter by start year (strict: must be >= start_year)
    if paper_year < start_year:
        logger.debug(f"Paper year {paper_year} < start_year {start_year} - EXCLUDED")
        return False
    
    # If no month filtering, just check year range
    if start_month is None and end_month is None:
        # Year-only mode: paper must be from start_year onwards
        logger.debug(f"Paper year {paper_year} >= start_year {start_year} - INCLUDED")
        return True
    
    # Month filtering is active - calculate exact range
    # If only start_month specified (no end), treat as "from this month onwards"
    # Use a far future date (2099-12) if no end is specified
    if end_year is None and end_month is None:
        # No end specified: "from start_year-start_month onwards"
        effective_end_year = 2099  # Far future
        effective_end_month = 12
    else:
        effective_end_year = end_year if end_year else start_year
        effective_end_month = end_month if end_month else 12
    
    effective_start_month = start_month if start_month else 1
    
    # Create comparable values (year * 12 + month)
    paper_value = paper_year * 12 + paper_month
    start_value = start_year * 12 + effective_start_month
    end_value = effective_end_year * 12 + effective_end_month
    
    in_range = start_value <= paper_value <= end_value
    logger.debug(
        f"Date check: {paper_year}-{paper_month:02d} "
        f"in [{start_year}-{effective_start_month:02d}, {effective_end_year}-{effective_end_month:02d}] = {in_range}"
    )
    return in_range


def fetch_papers_from_all_feeds(
    max_per_feed: int = 15,
    start_year: int = 2022,
    start_month: Optional[int] = None,
    end_year: Optional[int] = None,
    end_month: Optional[int] = None
) -> List[Dict]:
    """
    Fetch papers from all 10 research domains with date filtering.
    
    Args:
        max_per_feed: Maximum papers to fetch per domain (default: 15)
        start_year: Start year for filtering (default: 2022)
        start_month: Start month (1-12, optional)
        end_year: End year (optional)
        end_month: End month (1-12, optional)
    
    Returns:
        List of paper dicts with fields:
        - title, authors, abstract, url, doi
        - year, month, published_date
        - venue, citations, research_domain
    """
    feeds = get_comprehensive_feeds()
    all_papers = []
    domain_counts = defaultdict(int)
    date_counts = defaultdict(int)
    
    # Build date range string for display
    date_range_str = f"{start_year}"
    if start_month:
        date_range_str = f"{start_year}-{start_month:02d}"
        if end_year or end_month:
            end_display = f"{end_year or start_year}-{end_month:02d}" if end_month else f"{end_year}"
            date_range_str += f" to {end_display}"
    
    print(f"\n{'='*50}")
    print(f"FETCHING FROM 10 RESEARCH DOMAINS")
    print(f"Date Range: {date_range_str}")
    print(f"{'='*50}")
    logger.info(f"Starting fetch from {len(feeds)} domains")
    logger.info(f"Date range: {date_range_str}")
    
    for idx, feed_config in enumerate(feeds, 1):
        domain_name = feed_config["name"]
        feed_url = feed_config["url"]
        
        print(f"\n[{idx}/{len(feeds)}] {domain_name}...")
        logger.info(f"Fetching from domain: {domain_name}")
        
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parse warning for {domain_name}: {feed.bozo_exception}")
            
            domain_papers = []
            
            for entry in feed.entries:
                # Extract title for debug logging
                entry_title = entry.title if hasattr(entry, 'title') else "Unknown Title"
                
                # Extract DOI from link
                doi = ""
                if hasattr(entry, 'link') and 'doi' in entry.link:
                    doi = entry.link.split('doi/')[-1].split('?')[0]
                
                # DEBUG: Print all date-related attributes for first few entries
                if len(domain_papers) < 3:
                    date_attrs = {}
                    for attr in ['published', 'updated', 'prism_coverdate', 'prism_coverDate',
                                 'prism_publicationdate', 'prism_publicationDate', 'dc_date', 
                                 'pubDate', 'prism_publicationname']:
                        if hasattr(entry, attr):
                            date_attrs[attr] = getattr(entry, attr)
                    logger.info(f"[DEBUG] Entry attrs for '{entry_title[:30]}...': {date_attrs}")
                
                # Parse publication date - check MULTIPLE date fields
                # ACM RSS feeds use various date fields
                published_date = None
                year = None
                month = None
                date_source = None
                
                # List of potential date fields in ACM RSS feeds (in priority order)
                date_fields = [
                    ('prism_coverdate', 'prism_coverDate'),
                    ('prism_publicationdate', 'prism_publicationDate'),
                    ('published', None),
                    ('updated', None),
                    ('dc_date', None),
                    ('pubDate', None),
                ]
                
                # Try each date field until we find a valid one
                for field_lower, field_camel in date_fields:
                    date_str = None
                    
                    # Try lowercase version
                    if hasattr(entry, field_lower):
                        date_str = getattr(entry, field_lower)
                        date_source = field_lower
                    # Try camelCase version if provided
                    elif field_camel and hasattr(entry, field_camel):
                        date_str = getattr(entry, field_camel)
                        date_source = field_camel
                    
                    if date_str:
                        published_date = parse_date_from_rss(date_str)
                        if published_date:
                            year = published_date.year
                            month = published_date.month
                            logger.debug(f"Parsed date from '{date_source}': {date_str} -> {year}-{month:02d}")
                            break
                        else:
                            # Try to extract year from string directly as fallback
                            try:
                                year = int(str(date_str)[:4])
                                if 2000 <= year <= 2100:  # Sanity check
                                    # Also try to get month
                                    try:
                                        month = int(str(date_str)[5:7])
                                        if not (1 <= month <= 12):
                                            month = None
                                    except (ValueError, IndexError):
                                        month = None
                                    date_source = f"{field_lower or field_camel} (partial)"
                                    logger.debug(f"Extracted year/month from '{date_source}': {year}-{month}")
                                    break
                                else:
                                    year = None
                            except (ValueError, TypeError):
                                pass
                
                # Log if no date was found at all
                if year is None:
                    logger.warning(f"[DEBUG] NO DATE FOUND for '{entry_title[:50]}...' - will be excluded")
                
                # DEBUG: Log each entry's date parsing result
                month_str = f"{month:02d}" if month else "??"
                logger.info(
                    f"[DEBUG] Entry: '{entry_title[:50]}...' | "
                    f"Date source: {date_source} | "
                    f"Parsed: {year}-{month_str} | "
                    f"published_date: {published_date}"
                )
                
                # Check date range with strict filtering
                filter_result = is_in_date_range(
                    paper_date=published_date,
                    paper_year_fallback=year,
                    paper_month_fallback=month,
                    start_year=start_year,
                    start_month=start_month,
                    end_year=end_year,
                    end_month=end_month
                )
                
                # DEBUG: Log filter decision
                if filter_result:
                    logger.info(
                        f"[DEBUG] ✓ PASS | '{entry_title[:40]}...' | "
                        f"Date: {year}-{month_str}"
                    )
                else:
                    start_month_str = f"{start_month:02d}" if start_month else "01"
                    end_month_str = f"{end_month:02d}" if end_month else "12"
                    end_year_str = end_year if end_year else start_year
                    logger.info(
                        f"[DEBUG] ✗ FAIL | '{entry_title[:40]}...' | "
                        f"Date: {year}-{month_str} | "
                        f"Outside range: {start_year}-{start_month_str} to {end_year_str}-{end_month_str}"
                    )
                
                if not filter_result:
                    continue
                
                # Paper passed filter - log success
                print(f"    ✓ Including: {entry_title[:60]}... ({year}-{month_str})")
                
                # If we passed date filter but year is still None, use the start_year as minimum
                if year is None:
                    year = start_year
                
                # Extract authors
                authors = "Authors not listed in RSS feed"
                if hasattr(entry, 'author') and entry.author:
                    authors = entry.author
                elif hasattr(entry, 'dc_creator') and entry.dc_creator:
                    authors = entry.dc_creator
                elif hasattr(entry, 'authors') and entry.authors:
                    try:
                        authors = ', '.join([a.get('name', '') for a in entry.authors if a.get('name')])
                    except (TypeError, AttributeError):
                        authors = "Multiple authors"
                
                paper = {
                    "title": entry.title if hasattr(entry, 'title') else "Unknown Title",
                    "authors": authors,
                    "abstract": entry.summary if hasattr(entry, 'summary') else "No abstract available",
                    "url": entry.link if hasattr(entry, 'link') else "",
                    "doi": doi,
                    "year": str(year),
                    "month": month,
                    "published_date": published_date.isoformat() if published_date else None,
                    "venue": getattr(entry, 'prism_publicationname', 'ACM Publication'),
                    "citations": 0,
                    "research_domain": domain_name
                }
                
                domain_papers.append(paper)
                
                # Track date distribution
                if year and month:
                    date_key = f"{year}-{month:02d}"
                    date_counts[date_key] += 1
                
                # Limit papers per domain
                if len(domain_papers) >= max_per_feed:
                    break
            
            all_papers.extend(domain_papers)
            domain_counts[domain_name] = len(domain_papers)
            
            print(f"  ✅ Found {len(domain_papers)} papers in date range")
            logger.info(f"Domain {domain_name}: found {len(domain_papers)} papers")
            
        except Exception as e:
            print(f"  ⚠️  Warning: Could not fetch from {domain_name}: {e}")
            logger.error(f"Error fetching from {domain_name}: {e}", exc_info=True)
            continue
    
    # Remove duplicates based on DOI, fallback to title
    logger.info(f"Total papers before deduplication: {len(all_papers)}")
    seen_dois = set()
    seen_titles = set()
    unique_papers = []
    
    for paper in all_papers:
        doi = paper.get('doi', '')
        title = paper.get('title', '').lower().strip()
        
        # Check DOI first (most reliable)
        if doi:
            if doi not in seen_dois:
                seen_dois.add(doi)
                unique_papers.append(paper)
            else:
                logger.debug(f"Duplicate DOI found: {doi}")
        else:
            # Fallback to title-based deduplication
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
            else:
                logger.debug(f"Duplicate title found: {title[:50]}...")
    
    logger.info(f"Total papers after deduplication: {len(unique_papers)}")
    
    # Sort by date (newest first)
    def sort_key(p):
        try:
            year = int(p.get('year', 0))
            month = p.get('month', 1) or 1
            return (year * 12 + month)
        except (ValueError, TypeError):
            return 0
    
    unique_papers.sort(key=sort_key, reverse=True)
    
    # Print statistics
    print(f"\n{'='*50}")
    print(f"DATE DISTRIBUTION")
    print(f"{'='*50}")
    for date_key in sorted(date_counts.keys(), reverse=True)[:10]:
        print(f"{date_key}: {date_counts[date_key]} papers")
    
    print(f"\n{'='*50}")
    print(f"DOMAIN DISTRIBUTION")
    print(f"{'='*50}")
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{domain:25s}: {count} papers")
    
    print(f"\n{'='*50}")
    print(f"✓ Retrieved {len(unique_papers)} unique papers from {len(feeds)} domains")
    print(f"✓ Filtered to date range: {date_range_str}")
    print(f"{'='*50}")
    
    logger.info(f"Fetch complete: {len(unique_papers)} unique papers")
    
    return unique_papers


if __name__ == "__main__":
    # Test the module
    import argparse
    
    parser = argparse.ArgumentParser(description='Test enhanced RSS feeds')
    parser.add_argument('--start-year', type=int, default=2024, help='Start year')
    parser.add_argument('--start-month', type=int, help='Start month (1-12)')
    parser.add_argument('--end-year', type=int, help='End year')
    parser.add_argument('--end-month', type=int, help='End month (1-12)')
    parser.add_argument('--max-per-feed', type=int, default=5, help='Max papers per feed')
    
    args = parser.parse_args()
    
    papers = fetch_papers_from_all_feeds(
        max_per_feed=args.max_per_feed,
        start_year=args.start_year,
        start_month=args.start_month,
        end_year=args.end_year,
        end_month=args.end_month
    )
    
    print(f"\n\nSample papers:")
    for i, paper in enumerate(papers[:3], 1):
        print(f"\n{i}. {paper['title'][:60]}...")
        print(f"   Domain: {paper['research_domain']}")
        print(f"   Date: {paper['year']}-{paper.get('month', '?'):02d}" if paper.get('month') else f"   Year: {paper['year']}")
        print(f"   DOI: {paper['doi']}")
