"""
Unit tests for enhanced RSS feeds and Plotly visualizations
Tests the new functionality added for multi-domain fetching and date filtering
"""

import unittest
import os
import json
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)

# Import modules under test
from enhanced_rss_feeds import (
    get_comprehensive_feeds,
    parse_date_from_rss,
    is_in_date_range,
)

from plotly_visualizations import (
    extract_sample_size,
    create_participant_icons,
    get_significance_color,
    get_significance_value,
    COLORS
)


class TestEnhancedRSSFeeds(unittest.TestCase):
    """Test cases for enhanced_rss_feeds.py"""
    
    def test_get_comprehensive_feeds_returns_10_domains(self):
        """Test that we get exactly 10 research domains"""
        feeds = get_comprehensive_feeds()
        self.assertEqual(len(feeds), 10, "Should return 10 research domains")
    
    def test_get_comprehensive_feeds_structure(self):
        """Test that each feed has required fields"""
        feeds = get_comprehensive_feeds()
        for feed in feeds:
            self.assertIn('name', feed, "Each feed should have a 'name' field")
            self.assertIn('url', feed, "Each feed should have a 'url' field")
            self.assertTrue(feed['url'].startswith('https://'), "URL should start with https://")
    
    def test_get_comprehensive_feeds_domain_names(self):
        """Test that all expected domains are present"""
        expected_domains = [
            "Gameplay Research",
            "HCI Research",
            "Virtual Reality",
            "Augmented Reality",
            "AI in Games",
            "Player Experience",
            "Game Analytics",
            "Serious Games",
            "Game Accessibility",
            "Game Design"
        ]
        feeds = get_comprehensive_feeds()
        domain_names = [f['name'] for f in feeds]
        
        for expected in expected_domains:
            self.assertIn(expected, domain_names, f"Domain '{expected}' should be present")
    
    def test_parse_date_from_rss_standard_format(self):
        """Test parsing standard RSS date format"""
        date_str = "Mon, 01 Jan 2024 00:00:00 GMT"
        result = parse_date_from_rss(date_str)
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)
    
    def test_parse_date_from_rss_iso_format(self):
        """Test parsing ISO date format"""
        date_str = "2024-10-15T12:30:00Z"
        result = parse_date_from_rss(date_str)
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 10)
        self.assertEqual(result.day, 15)
    
    def test_parse_date_from_rss_simple_date(self):
        """Test parsing simple date format"""
        date_str = "2024-10-15"
        result = parse_date_from_rss(date_str)
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 10)
    
    def test_parse_date_from_rss_empty_string(self):
        """Test parsing empty string returns None"""
        result = parse_date_from_rss("")
        self.assertIsNone(result)
    
    def test_parse_date_from_rss_none(self):
        """Test parsing None returns None"""
        result = parse_date_from_rss(None)
        self.assertIsNone(result)
    
    def test_is_in_date_range_year_only(self):
        """Test date range check with year only"""
        paper_date = datetime(2024, 6, 15)
        
        # Should be in range
        self.assertTrue(is_in_date_range(paper_date, None, None, start_year=2024))
        self.assertTrue(is_in_date_range(paper_date, None, None, start_year=2022))
        
        # Should not be in range
        self.assertFalse(is_in_date_range(paper_date, None, None, start_year=2025))
    
    def test_is_in_date_range_with_start_month(self):
        """Test date range check with start month (means 'from this month onwards')"""
        paper_date = datetime(2024, 10, 15)
        
        # Should be in range (Oct 2024 onwards)
        self.assertTrue(is_in_date_range(paper_date, None, None, start_year=2024, start_month=10))
        self.assertTrue(is_in_date_range(paper_date, None, None, start_year=2024, start_month=9))
        
        # Should not be in range (Nov 2024 onwards - Oct is before Nov)
        self.assertFalse(is_in_date_range(paper_date, None, None, start_year=2024, start_month=11))
        
        # Future date should be included when only start_month is specified (no end)
        paper_date_future = datetime(2025, 3, 15)
        self.assertTrue(is_in_date_range(paper_date_future, None, None, start_year=2024, start_month=10))
    
    def test_is_in_date_range_with_end_month(self):
        """Test date range check with start and end month"""
        paper_date = datetime(2024, 10, 15)
        
        # Should be in range (Oct to Dec)
        self.assertTrue(is_in_date_range(paper_date, None, None, start_year=2024, start_month=10, end_month=12))
        
        # Should be in range (exactly Oct)
        self.assertTrue(is_in_date_range(paper_date, None, None, start_year=2024, start_month=10, end_month=10))
        
        # Should not be in range (Nov to Dec only)
        self.assertFalse(is_in_date_range(paper_date, None, None, start_year=2024, start_month=11, end_month=12))
    
    def test_is_in_date_range_cross_year(self):
        """Test date range check crossing year boundary"""
        paper_date_jan = datetime(2025, 1, 15)
        paper_date_dec = datetime(2024, 12, 15)
        
        # Oct 2024 to Jan 2025
        self.assertTrue(is_in_date_range(paper_date_jan, None, None, start_year=2024, start_month=10, 
                                         end_year=2025, end_month=1))
        self.assertTrue(is_in_date_range(paper_date_dec, None, None, start_year=2024, start_month=10, 
                                         end_year=2025, end_month=1))
    
    def test_is_in_date_range_none_date_strict(self):
        """Test that None date is EXCLUDED when month filtering is active (strict mode)"""
        # With month filtering, unknown dates should be EXCLUDED
        self.assertFalse(is_in_date_range(None, None, None, start_year=2024, start_month=1))
        
    def test_is_in_date_range_none_date_with_fallback(self):
        """Test date range with fallback year when paper_date is None"""
        # Fallback year 2024 should be included for year-only filter
        self.assertTrue(is_in_date_range(None, 2024, 6, start_year=2024))
        # Fallback year 2023 should be excluded
        self.assertFalse(is_in_date_range(None, 2023, 6, start_year=2024))


class TestPlotlyVisualizations(unittest.TestCase):
    """Test cases for plotly_visualizations.py"""
    
    def test_extract_sample_size_standard_format(self):
        """Test extracting N from 'N=32' format"""
        methodology = {'sample_size': 'N=32'}
        result = extract_sample_size(methodology)
        self.assertEqual(result, 32)
    
    def test_extract_sample_size_with_text(self):
        """Test extracting N from 'N=32 participants' format"""
        methodology = {'sample_size': 'N=32 participants'}
        result = extract_sample_size(methodology)
        self.assertEqual(result, 32)
    
    def test_extract_sample_size_lowercase(self):
        """Test extracting N from lowercase 'n=32' format"""
        methodology = {'sample_size': 'n=32'}
        result = extract_sample_size(methodology)
        self.assertEqual(result, 32)
    
    def test_extract_sample_size_number_only(self):
        """Test extracting N from just '32' format"""
        methodology = {'sample_size': '32'}
        result = extract_sample_size(methodology)
        self.assertEqual(result, 32)
    
    def test_extract_sample_size_missing(self):
        """Test extracting N when sample_size is missing"""
        methodology = {}
        result = extract_sample_size(methodology)
        self.assertEqual(result, 0)
    
    def test_extract_sample_size_invalid(self):
        """Test extracting N from invalid format"""
        methodology = {'sample_size': 'unknown'}
        result = extract_sample_size(methodology)
        self.assertEqual(result, 0)
    
    def test_create_participant_icons_small_n(self):
        """Test icon creation for small N"""
        icons = create_participant_icons(10)
        self.assertEqual(icons, '👤')  # 10 // 10 = 1 icon
    
    def test_create_participant_icons_medium_n(self):
        """Test icon creation for medium N"""
        icons = create_participant_icons(50)
        self.assertEqual(icons, '👤👤👤👤👤')  # 50 // 10 = 5 icons
    
    def test_create_participant_icons_large_n(self):
        """Test icon creation for large N (should cap at max)"""
        icons = create_participant_icons(200, max_icons=15)
        self.assertEqual(len(icons), 15)  # Should cap at 15 icons
    
    def test_create_participant_icons_zero(self):
        """Test icon creation for N=0"""
        icons = create_participant_icons(0)
        self.assertEqual(len(icons) // len('👤'), 4)  # Default 4 icons
    
    def test_get_significance_color_p001(self):
        """Test significance color for p<.001"""
        color = get_significance_color("p<.001, η²=0.45")
        self.assertEqual(color, COLORS['p001'])
        
        color2 = get_significance_color("p<0.001")
        self.assertEqual(color2, COLORS['p001'])
    
    def test_get_significance_color_p01(self):
        """Test significance color for p<.01"""
        color = get_significance_color("p<.01")
        self.assertEqual(color, COLORS['p01'])
        
        color2 = get_significance_color("p<0.01, r=0.5")
        self.assertEqual(color2, COLORS['p01'])
    
    def test_get_significance_color_p05(self):
        """Test significance color for p<.05"""
        color = get_significance_color("p<.05")
        self.assertEqual(color, COLORS['p05'])
    
    def test_get_significance_color_not_significant(self):
        """Test significance color for non-significant result"""
        color = get_significance_color("n.s.")
        self.assertEqual(color, COLORS['ns'])
        
        color2 = get_significance_color("p=0.15")
        self.assertEqual(color2, COLORS['ns'])
    
    def test_get_significance_value_p001(self):
        """Test significance value for p<.001"""
        value = get_significance_value("p<.001")
        self.assertEqual(value, 95)
    
    def test_get_significance_value_p01(self):
        """Test significance value for p<.01"""
        value = get_significance_value("p<.01")
        self.assertEqual(value, 85)
    
    def test_get_significance_value_p05(self):
        """Test significance value for p<.05"""
        value = get_significance_value("p<.05")
        self.assertEqual(value, 75)
    
    def test_get_significance_value_not_significant(self):
        """Test significance value for non-significant"""
        value = get_significance_value("n.s.")
        self.assertEqual(value, 60)


class TestMainPipelineIntegration(unittest.TestCase):
    """Integration tests for main_pipeline.py"""
    
    def test_import_main_pipeline(self):
        """Test that main_pipeline imports without errors"""
        try:
            import main_pipeline
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import main_pipeline: {e}")
    
    def test_normalize_papers_adds_research_domain(self):
        """Test that normalize_papers adds research_domain field"""
        from main_pipeline import normalize_papers
        
        raw_papers = [{
            "title": "Test Paper",
            "authors": "Test Author",
            "abstract": "Test abstract",
            "doi": "10.1234/test",
            "year": "2024",
            "research_domain": "HCI Research"
        }]
        
        normalized = normalize_papers(raw_papers)
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0]['research_domain'], "HCI Research")
    
    def test_normalize_papers_default_domain(self):
        """Test that normalize_papers defaults research_domain to 'General'"""
        from main_pipeline import normalize_papers
        
        raw_papers = [{
            "title": "Test Paper",
            "authors": "Test Author",
            "abstract": "Test abstract",
        }]
        
        normalized = normalize_papers(raw_papers)
        self.assertEqual(normalized[0]['research_domain'], "General")


class TestVisualizationOutput(unittest.TestCase):
    """Tests for visualization output functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_output_dir = "test_visualizations"
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        self.sample_paper = {
            "title": "Test Research Paper on Virtual Reality Gaming",
            "methodology": {
                "sample_size": "N=32",
                "design": "Between-subjects",
                "materials": ["VR headset", "Game software"],
                "procedures": ["Calibration", "Gameplay", "Survey"],
                "analysis": ["ANOVA", "Correlation"]
            },
            "findings": [
                {"text": "VR increased immersion significantly", "statistic": "p<.001, η²=0.45"},
                {"text": "No effect on motion sickness", "statistic": "p=0.23"},
                {"text": "Positive user feedback", "statistic": "p<.05"}
            ],
            "research_domain": "Virtual Reality",
            "doi": "10.1234/test.vr"
        }
    
    def tearDown(self):
        """Clean up test output"""
        import shutil
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
    
    def test_create_methodology_flowchart_creates_html(self):
        """Test that methodology flowchart creates HTML output"""
        from plotly_visualizations import create_methodology_flowchart
        
        output_path = f"{self.test_output_dir}/test_methodology.png"
        create_methodology_flowchart(self.sample_paper, output_path)
        
        html_path = output_path.replace('.png', '_interactive.html')
        self.assertTrue(os.path.exists(html_path), "HTML file should be created")
    
    def test_create_results_bar_chart_creates_html(self):
        """Test that results chart creates HTML output"""
        from plotly_visualizations import create_results_bar_chart
        
        output_path = f"{self.test_output_dir}/test_results.png"
        create_results_bar_chart(self.sample_paper, output_path)
        
        html_path = output_path.replace('.png', '_interactive.html')
        self.assertTrue(os.path.exists(html_path), "HTML file should be created")
    
    def test_create_domain_distribution_chart(self):
        """Test domain distribution chart creation"""
        from plotly_visualizations import create_domain_distribution_chart
        
        papers = [
            {"research_domain": "HCI Research"},
            {"research_domain": "HCI Research"},
            {"research_domain": "Virtual Reality"},
            {"research_domain": "Game Design"},
        ]
        
        output_path = f"{self.test_output_dir}/test_domain.png"
        create_domain_distribution_chart(papers, output_path)
        
        html_path = output_path.replace('.png', '_interactive.html')
        self.assertTrue(os.path.exists(html_path), "HTML file should be created")
    
    def test_create_timeline_chart(self):
        """Test timeline chart creation"""
        from plotly_visualizations import create_timeline_chart
        
        papers = [
            {"year": "2024", "month": 10},
            {"year": "2024", "month": 10},
            {"year": "2024", "month": 11},
        ]
        
        output_path = f"{self.test_output_dir}/test_timeline.png"
        create_timeline_chart(papers, output_path)
        
        html_path = output_path.replace('.png', '_interactive.html')
        self.assertTrue(os.path.exists(html_path), "HTML file should be created")


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
