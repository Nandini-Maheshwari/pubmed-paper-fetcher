"""Tests for the PubMed fetcher."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from pubmed_fetcher.fetcher import PubMedFetcher
from pubmed_fetcher.models import PaperResult, Author


class TestPubMedFetcher:
    """Test cases for PubMedFetcher."""

    def test_init(self):
        """Test fetcher initialization."""
        fetcher = PubMedFetcher(debug=True)
        assert fetcher.debug is True
        assert fetcher.session is not None

    def test_is_pharmaceutical_biotech_affiliation(self):
        """Test company affiliation detection."""
        fetcher = PubMedFetcher()

        # Should return True for pharma/biotech
        assert fetcher._is_pharmaceutical_biotech_affiliation("Pfizer Inc.")
        assert fetcher._is_pharmaceutical_biotech_affiliation(
            "Novartis Pharmaceuticals"
        )
        assert fetcher._is_pharmaceutical_biotech_affiliation("Biotech Research Corp")

        # Should return False for academic institutions
        assert not fetcher._is_pharmaceutical_biotech_affiliation("Harvard University")
        assert not fetcher._is_pharmaceutical_biotech_affiliation("Mayo Clinic")
        assert not fetcher._is_pharmaceutical_biotech_affiliation("MIT Laboratory")

    def test_extract_email_from_affiliation(self):
        """Test email extraction from affiliation."""
        fetcher = PubMedFetcher()

        affiliation = "Pfizer Inc., New York, NY. john.doe@pfizer.com"
        email = fetcher._extract_email_from_affiliation(affiliation)
        assert email == "john.doe@pfizer.com"

        no_email = "Pfizer Inc., New York, NY"
        email = fetcher._extract_email_from_affiliation(no_email)
        assert email is None

    @patch("pubmed_fetcher.fetcher.requests.Session.get")
    def test_search_papers_success(self, mock_get):
        """Test successful paper search."""
        mock_response = Mock()
        mock_response.content = b"""<?xml version="1.0"?>
        <eSearchResult>
            <IdList>
                <Id>12345</Id>
                <Id>67890</Id>
            </IdList>
        </eSearchResult>"""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fetcher = PubMedFetcher()
        result = fetcher.search_papers("test query")

        assert result == ["12345", "67890"]
        mock_get.assert_called_once()

    @patch("pubmed_fetcher.fetcher.requests.Session.get")
    def test_search_papers_no_results(self, mock_get):
        """Test paper search with no results."""
        mock_response = Mock()
        mock_response.content = b"""<?xml version="1.0"?>
        <eSearchResult>
        </eSearchResult>"""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fetcher = PubMedFetcher()
        result = fetcher.search_papers("test query")

        assert result == []
