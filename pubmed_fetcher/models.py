"""Data models for PubMed paper results."""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Author:
    """Represents an author of a research paper."""
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    is_corresponding: bool = False


@dataclass
class PaperResult:
    """Represents a research paper result."""
    pubmed_id: str
    title: str
    publication_date: Optional[datetime]
    authors: List[Author]
    non_academic_authors: List[str]
    company_affiliations: List[str]
    corresponding_author_email: Optional[str]
    
    def to_csv_row(self) -> dict:
        """Convert to CSV row format."""
        return {
            "PubmedID": self.pubmed_id,
            "Title": self.title,
            "Publication Date": self.publication_date.strftime("%Y-%m-%d") if self.publication_date else "",
            "Non-academic Author(s)": "; ".join(self.non_academic_authors),
            "Company Affiliation(s)": "; ".join(self.company_affiliations),
            "Corresponding Author Email": self.corresponding_author_email or ""
        }