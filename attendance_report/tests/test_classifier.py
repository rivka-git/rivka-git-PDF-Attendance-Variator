"""Tests for classifier module."""

import pytest

from attendance_report.classifier import Classifier


class TestClassifier:
    """Test suite for Classifier."""
    
    def setup_method(self):
        self.classifier = Classifier()
    
    def test_classify_type_a(self):
        """Test classification of TYPE_A keywords."""
        text = "דוח נוכחות של חברת הנשר כח אדם"
        assert self.classifier.classify(text) == "TYPE_A"
    
    def test_classify_type_b(self):
        """Test classification of TYPE_B keywords."""
        text = "כרטיס עובד לחודש עם מחיר לשעה"
        result = self.classifier.classify(text)
        assert result == "TYPE_B"
    
    def test_classify_unknown_no_keywords(self):
        """Test classification returns UNKNOWN when no keywords found."""
        text = "דוח כלשהו ללא מילים שמורות"
        assert self.classifier.classify(text) == "UNKNOWN"

    def test_classify_type_c(self):
        """Test classification of TYPE_C keywords."""
        text = "דוח חדש מסוג TYPE_C"
        assert self.classifier.classify(text) == "TYPE_C"
    
    def test_classify_collision_both_keywords(self):
        """Test classification returns UNKNOWN when both TYPE_A and TYPE_B keywords found."""
        text = "הנשר כח אדם עם מחיר לשעה"
        assert self.classifier.classify(text) == "UNKNOWN"

    def test_classify_collision_including_type_c_returns_unknown(self):
        text = "הנשר כח אדם וגם TYPE_C"
        assert self.classifier.classify(text) == "UNKNOWN"
