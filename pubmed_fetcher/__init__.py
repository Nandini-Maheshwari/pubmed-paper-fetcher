"""PubMed Paper Fetcher - A tool to fetch research papers with pharmaceutical/biotech company authors."""

__version__ = "0.1.0"

from .fetcher import PubMedFetcher
from .models import PaperResult

__all__ = ["PubMedFetcher", "PaperResult"]
