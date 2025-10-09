"""Unit tests for fact-check quality features."""

import unittest
import sys
import os
from datetime import datetime, timedelta

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from schemas import FactCheckItem
from services.factcheck_service import _deduplicate_by_publisher, _filter_by_recency
from providers.factcheck_google import normalize_verdict


class TestFactCheckQuality(unittest.TestCase):
    """Test cases for fact-check quality features."""

    def test_deduplicate_by_publisher_keeps_higher_score(self):
        """Test that two results from same source keep only the higher-score one."""
        # Create two items from same publisher with different scores
        item1 = FactCheckItem(
            claim="Test claim 1",
            verdict="True",
            source="BBC Fact Check",
            similarity=0.6
        )
        
        item2 = FactCheckItem(
            claim="Test claim 2", 
            verdict="False",
            source="BBC Fact Check",
            similarity=0.8  # Higher score
        )
        
        items = [item1, item2]
        result = _deduplicate_by_publisher(items)
        
        # Should return only one item (the higher scoring one)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].similarity, 0.8)
        self.assertEqual(result[0].claim, "Test claim 2")

    def test_filter_by_recency_removes_old_items(self):
        """Test that an old item beyond max_age_months=12 is filtered out."""
        now = datetime.now()
        
        # Create recent item (within 12 months)
        recent_item = FactCheckItem(
            claim="Recent claim",
            verdict="True",
            source="Recent Publisher",
            publishedAt=now - timedelta(days=300),  # ~10 months ago
            similarity=0.7
        )
        
        # Create old item (beyond 12 months)
        old_item = FactCheckItem(
            claim="Old claim",
            verdict="False", 
            source="Old Publisher",
            publishedAt=now - timedelta(days=400),  # ~13 months ago
            similarity=0.8
        )
        
        items = [recent_item, old_item]
        result = _filter_by_recency(items, max_age_months=12)
        
        # Should only keep the recent item
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].claim, "Recent claim")

    def test_filter_by_recency_penalties_missing_dates(self):
        """Test that items with missing publishedAt get score penalty but are kept."""
        item_with_date = FactCheckItem(
            claim="Dated claim",
            verdict="True",
            source="Publisher",
            publishedAt=datetime.now() - timedelta(days=100),
            similarity=0.8
        )
        
        item_without_date = FactCheckItem(
            claim="Undated claim",
            verdict="False",
            source="Another Publisher", 
            publishedAt=None,
            similarity=0.8  # Same initial score
        )
        
        items = [item_with_date, item_without_date]
        result = _filter_by_recency(items, max_age_months=12)
        
        # Both items should be kept
        self.assertEqual(len(result), 2)
        
        # Find the item without date
        undated_result = next(item for item in result if item.publishedAt is None)
        
        # Should have penalty applied (0.8 - 0.05 = 0.75)
        self.assertEqual(undated_result.similarity, 0.75)

    def test_normalize_verdict_unknown_text(self):
        """Test that unknown verdict text normalizes to Unverified/Unsupported."""
        # Test various unknown/unrecognized verdicts
        self.assertEqual(normalize_verdict("completely made up verdict"), "Unverified/Unsupported")
        self.assertEqual(normalize_verdict("random text"), "Unverified/Unsupported")
        self.assertEqual(normalize_verdict("xyz123"), "Unverified/Unsupported")
        self.assertEqual(normalize_verdict(""), "Unverified/Unsupported")
        self.assertEqual(normalize_verdict(None), "Unverified/Unsupported")

    def test_normalize_verdict_known_mappings(self):
        """Test that known verdicts map correctly."""
        # Test exact mappings from VERDICT_MAP
        self.assertEqual(normalize_verdict("true"), "True")
        self.assertEqual(normalize_verdict("mostly true"), "Mostly True")
        self.assertEqual(normalize_verdict("half true"), "Mixed/Needs Context")
        self.assertEqual(normalize_verdict("mixture"), "Mixed/Needs Context")
        self.assertEqual(normalize_verdict("misleading"), "Misleading")
        self.assertEqual(normalize_verdict("false"), "False")
        self.assertEqual(normalize_verdict("unverified"), "Unverified/Unsupported")
        self.assertEqual(normalize_verdict("opinion"), "Opinion/Analysis")
        self.assertEqual(normalize_verdict("satire"), "Satire/Parody")

    def test_normalize_verdict_case_insensitive(self):
        """Test that verdict normalization is case-insensitive and strips punctuation."""
        # Test case variations
        self.assertEqual(normalize_verdict("TRUE"), "True")
        self.assertEqual(normalize_verdict("True"), "True")
        self.assertEqual(normalize_verdict("MOSTLY TRUE"), "Mostly True")
        
        # Test with punctuation
        self.assertEqual(normalize_verdict("true."), "True")
        self.assertEqual(normalize_verdict("false!"), "False")
        self.assertEqual(normalize_verdict("mixture?"), "Mixed/Needs Context")


if __name__ == '__main__':
    unittest.main(verbosity=2)