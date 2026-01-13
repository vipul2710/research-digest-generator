"""
Enhanced summarization module for creating professor-level research digests
"""

import os
import json
from openai import OpenAI
from typing import Dict, List

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Use GPT-4 for better academic analysis
MODEL = "gpt-4-turbo-preview"


def extract_deep_summary(paper: Dict) -> Dict:
    """
    Extract comprehensive academic-level summary from paper metadata
    """
    
    prompt = f"""
You are an expert academic researcher analyzing this paper for a professor-level research digest.

Paper Title: {paper.get('title', '')}
Authors: {paper.get('authors', '')}
Abstract: {paper.get('abstract', '')}
DOI: {paper.get('doi', '')}
Venue: {paper.get('venue', '')}
Year: {paper.get('year', '')}

Create a COMPREHENSIVE academic analysis with these exact sections:

1. RESEARCH QUESTION (2-3 sentences):
Write a clear, specific research question this paper addresses. Not just "what" but "why" this matters.

2. MOTIVATION & CONTEXT (2 paragraphs):
- What gap in existing research does this fill?
- What prior work does it build on?
- Why is this important to the field?

3. SIGNIFICANCE (4-5 bullet points):
What are the genuine contributions? Be specific about:
- Methodological innovations
- Theoretical advances
- Practical implications

4. METHODOLOGY DETAILS:
Provide specific details:
- Research Design: [experimental, mixed-methods, survey, etc.]
- Sample Size: N=? (if available)
- Demographics: [age, experience level, etc.]
- Materials: [games used, equipment, measures]
- Analysis Approach: [statistical tests, qualitative methods]

5. KEY FINDINGS (4-6 findings):
For EACH finding provide:
- The finding itself (be specific)
- Quantitative results if available (F-values, p-values, effect sizes, percentages)
- What this means practically

Format as JSON array: [{{"text": "...", "statistic": "p<.001, η²=0.37"}}]

6. CRITICAL EVALUATION:

STRENGTHS (5 items minimum):
- Focus on methodological rigor, sample quality, validity
- What did they do particularly well?

LIMITATIONS (5 items minimum):
- Validity threats (internal, external, construct)
- Generalizability concerns
- What could have been done better?

7. THEORETICAL CONTRIBUTION (1 paragraph):
How does this advance theoretical understanding in the field?

8. PRACTICAL APPLICATIONS (4-5 specific items):
Real-world uses for:
- Game developers
- Researchers
- Designers
- Other stakeholders

9. FUTURE RESEARCH DIRECTIONS (5 specific questions):
What questions remain unanswered?
What should follow-up studies investigate?

10. CONNECTIONS (1 paragraph):
How might this relate to other gaming/HCI research?
What broader research trends does it connect to?

CRITICAL INSTRUCTIONS:
- Be SPECIFIC - use actual numbers, methodology names, theoretical frameworks
- Write at peer-review level, not popular science
- If information is not available in the abstract, acknowledge that
- Use academic tone and terminology
- Focus on DEPTH over breadth

Return response as valid JSON with these keys:
{{
    "research_question": "",
    "motivation": "",
    "significance": [],
    "methodology": {{
        "design": "",
        "sample_size": "",
        "materials": "",
        "analysis": ""
    }},
    "findings": [],
    "strengths": [],
    "limitations": [],
    "theoretical_contribution": "",
    "applications": [],
    "future_work": [],
    "connections": ""
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert academic researcher creating professor-level research summaries. Provide detailed, critical analysis with specific methodological and statistical details."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more factual output
            response_format={"type": "json_object"}
        )
        
        summary = json.loads(response.choices[0].message.content)
        return summary
        
    except Exception as e:
        print(f"Error in deep summarization: {e}")
        return create_fallback_summary(paper)


def create_executive_summary(papers: List[Dict]) -> Dict:
    """
    Create cross-paper synthesis and executive summary
    """
    
    titles = "\n".join([f"- {p.get('title', '')}" for p in papers])
    
    prompt = f"""
You are creating an executive summary for a research digest containing these {len(papers)} papers:

{titles}

Create a comprehensive synthesis that includes:

1. OVERVIEW (200 words):
Summarize the key themes across all papers. What are researchers focusing on in gaming/HCI?

2. KEY THEMES (5-7 themes):
Identify common threads:
- Methodological approaches
- Research domains
- Theoretical frameworks
- Types of games studied

3. METHODOLOGICAL TRENDS:
What research methods are being used? Any patterns?

4. CONVERGENCE:
What findings align across multiple papers?

5. CONTRADICTIONS:
Are there any conflicting results or approaches?

6. RESEARCH GAPS (5-7 gaps):
What's NOT being studied?
What questions remain unanswered?
What would make strong follow-up research?

Return as JSON:
{{
    "executive_summary": "",
    "key_themes": [],
    "methodology_trends": "",
    "convergence": "",
    "contradictions": "",
    "research_gaps": []
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert at synthesizing academic research and identifying trends and gaps."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error creating executive summary: {e}")
        return {
            "executive_summary": "Error generating summary",
            "key_themes": [],
            "methodology_trends": "",
            "convergence": "",
            "contradictions": "",
            "research_gaps": []
        }


def generate_paper_connections(papers: List[Dict]) -> List[str]:
    """
    Generate connections between papers
    """
    
    titles_and_summaries = "\n\n".join([
        f"Paper {i+1}: {p.get('title', '')}\nSummary: {p.get('research_question', '')}"
        for i, p in enumerate(papers)
    ])
    
    prompt = f"""
Analyze these papers and describe how they connect to each other:

{titles_and_summaries}

For EACH paper, write 2-3 sentences explaining:
- How it relates to other papers in this digest
- Whether it confirms, contradicts, or extends other work
- What unique perspective it offers

Return as JSON array with one connection per paper.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are an expert at identifying connections between research papers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error generating connections: {e}")
        return ["" for _ in papers]


def create_fallback_summary(paper: Dict) -> Dict:
    """Fallback summary if API fails"""
    return {
        "research_question": f"Research question not available for: {paper.get('title', 'Unknown')}",
        "motivation": "Motivation details not available.",
        "significance": ["Significance analysis pending"],
        "methodology": {
            "design": "Not specified",
            "sample_size": "Not specified",
            "materials": "Not specified",
            "analysis": "Not specified"
        },
        "findings": [{"text": "Findings not available", "statistic": ""}],
        "strengths": ["Analysis pending"],
        "limitations": ["Analysis pending"],
        "theoretical_contribution": "Theoretical contribution analysis pending.",
        "applications": ["Applications analysis pending"],
        "future_work": ["Future work analysis pending"],
        "connections": "Connections analysis pending."
    }


def summarize_all_papers(papers: List[Dict]) -> Dict:
    """
    Main function to summarize all papers and create synthesis
    """
    
    print(f"Analyzing {len(papers)} papers with deep academic analysis...")
    
    # Analyze each paper
    enhanced_papers = []
    for i, paper in enumerate(papers, 1):
        print(f"Analyzing paper {i}/{len(papers)}: {paper.get('title', '')[:60]}...")
        summary = extract_deep_summary(paper)
        
        # Merge with original paper data
        enhanced_paper = {**paper, **summary}
        enhanced_papers.append(enhanced_paper)
    
    print("Creating cross-paper synthesis...")
    
    # Generate connections between papers
    connections = generate_paper_connections(enhanced_papers)
    for paper, connection in zip(enhanced_papers, connections):
        paper['connections'] = connection
    
    # Create executive summary
    synthesis = create_executive_summary(enhanced_papers)
    
    # Calculate statistics
    total_participants = sum([
        int(p.get('methodology', {}).get('sample_size', '0').replace('N=', '').split()[0])
        if 'N=' in p.get('methodology', {}).get('sample_size', '')
        else 0
        for p in enhanced_papers
    ])
    
    return {
        "papers": enhanced_papers,
        "synthesis": synthesis,
        "metadata": {
            "paper_count": len(enhanced_papers),
            "total_participants": total_participants,
            "date_range": f"{min([p.get('year', '2024') for p in papers])} - {max([p.get('year', '2024') for p in papers])}"
        }
    }


if __name__ == "__main__":
    # Test with sample data
    import json
    
    # Load normalized papers
    with open("data/normalized_papers.json", "r") as f:
        papers = json.load(f)
    
    # Summarize
    result = summarize_all_papers(papers)
    
    # Save enhanced data
    with open("data/enhanced_papers.json", "w") as f:
        json.dump(result, indent=2, fp=f)
    
    print(f"✓ Enhanced {len(result['papers'])} papers with deep analysis")