"""
Track processed papers to prevent duplicates
Simple file-based tracking system
"""

import json
import os
from datetime import datetime
from typing import List, Dict

HISTORY_FILE = "data/processed_papers.json"

def load_history() -> Dict:
    """Load history of processed papers"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history: Dict):
    """Save updated history"""
    os.makedirs("data", exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def filter_new_papers(papers: List[Dict]) -> List[Dict]:
    """
    Filter out papers we've already processed
    Returns only NEW papers
    """
    history = load_history()
    today = str(datetime.now().date())
    
    new_papers = []
    updated_history = history.copy()
    
    for paper in papers:
        doi = paper.get('doi', '')
        title = paper.get('title', '')
        
        # Use DOI as primary identifier, fall back to title
        identifier = doi if doi else title
        
        if identifier in history:
            print(f"⏭️  Skipping (already processed): {title[:60]}...")
        else:
            new_papers.append(paper)
            updated_history[identifier] = {
                'title': title,
                'processed_date': today,
                'doi': doi,
                'venue': paper.get('venue', ''),
                'year': paper.get('year', '')
            }
            print(f"✨ New paper: {title[:60]}...")
    
    save_history(updated_history)
    return new_papers

def get_stats() -> Dict:
    """Get processing statistics"""
    history = load_history()
    
    years = {}
    for entry in history.values():
        year = entry.get('year', 'Unknown')
        years[year] = years.get(year, 0) + 1
    
    return {
        'total_processed': len(history),
        'by_year': years
    }

def reset_history():
    """Reset tracking history (use with caution!)"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    print("✓ History reset")