"""Main PubMed fetcher implementation."""

import requests
import xml.etree.ElementTree as ET
from typing import List, Optional, Set
from datetime import datetime
import re
import time
from urllib.parse import urlencode

from .models import PaperResult, Author


class PubMedFetcher:
    """Fetches and processes research papers from PubMed API."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Keywords to identify pharmaceutical/biotech companies
    PHARMA_BIOTECH_KEYWORDS = {
        "pharmaceutical", "pharma", "biotech", "biotechnology", "biopharmaceutical",
        "drug", "therapeutics", "medicine", "clinical", "research", "development",
        "inc", "corp", "corporation", "company", "ltd", "llc", "ag", "gmbh",
        "novartis", "pfizer", "roche", "merck", "johnson", "bristol", "abbvie",
        "gilead", "amgen", "biogen", "celgene", "regeneron", "vertex", "alexion",
        "moderna", "biontech", "illumina", "thermo", "agilent", "waters"
    }
    
    # Keywords to identify academic institutions
    ACADEMIC_KEYWORDS = {
        "university", "college", "institute", "school", "hospital", "medical center",
        "research center", "laboratory", "lab", "department", "faculty", "academia"
    }
    
    def __init__(self, debug: bool = False):
        """Initialize the fetcher with debug mode."""
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PubMedFetcher/1.0 (research paper fetcher)'
        })
    
    def _debug_print(self, message: str) -> None:
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def _is_pharmaceutical_biotech_affiliation(self, affiliation: str) -> bool:
        """Check if affiliation is from pharmaceutical/biotech company."""
        if not affiliation:
            return False
        
        affiliation_lower = affiliation.lower()
        
        # Check for academic keywords first (exclude if found)
        for keyword in self.ACADEMIC_KEYWORDS:
            if keyword in affiliation_lower:
                return False
        
        # Check for pharma/biotech keywords
        for keyword in self.PHARMA_BIOTECH_KEYWORDS:
            if keyword in affiliation_lower:
                return True
        
        return False
    
    def _extract_email_from_affiliation(self, affiliation: str) -> Optional[str]:
        """Extract email address from affiliation string."""
        if not affiliation:
            return None
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, affiliation)
        return matches[0] if matches else None
    
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """Search for papers and return list of PubMed IDs."""
        self._debug_print(f"Searching for papers with query: {query}")
        
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml'
        }
        
        url = f"{self.BASE_URL}esearch.fcgi"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            id_list = root.find('IdList')
            
            if id_list is None:
                self._debug_print("No papers found")
                return []
            
            paper_ids = [id_elem.text for id_elem in id_list.findall('Id')]
            self._debug_print(f"Found {len(paper_ids)} papers")
            
            return paper_ids
            
        except requests.RequestException as e:
            raise Exception(f"Error searching PubMed: {e}")
        except ET.ParseError as e:
            raise Exception(f"Error parsing search results: {e}")
    
    def fetch_paper_details(self, paper_ids: List[str]) -> List[PaperResult]:
        """Fetch detailed information for papers."""
        if not paper_ids:
            return []
        
        self._debug_print(f"Fetching details for {len(paper_ids)} papers")
        
        # Process papers in batches to avoid API limits
        batch_size = 50
        all_results = []
        
        for i in range(0, len(paper_ids), batch_size):
            batch = paper_ids[i:i + batch_size]
            batch_results = self._fetch_batch_details(batch)
            all_results.extend(batch_results)
            
            # Rate limiting
            if i + batch_size < len(paper_ids):
                time.sleep(0.5)
        
        return all_results
    
    def _fetch_batch_details(self, paper_ids: List[str]) -> List[PaperResult]:
        """Fetch details for a batch of papers."""
        params = {
            'db': 'pubmed',
            'id': ','.join(paper_ids),
            'retmode': 'xml'
        }
        
        url = f"{self.BASE_URL}efetch.fcgi"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            results = []
            
            for article in root.findall('.//PubmedArticle'):
                try:
                    paper_result = self._parse_article(article)
                    if paper_result:
                        results.append(paper_result)
                except Exception as e:
                    self._debug_print(f"Error parsing article: {e}")
                    continue
            
            return results
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching paper details: {e}")
        except ET.ParseError as e:
            raise Exception(f"Error parsing paper details: {e}")
    
    def _parse_article(self, article: ET.Element) -> Optional[PaperResult]:
        """Parse a single article XML element."""
        try:
            # Extract PubMed ID
            pubmed_id = article.find('.//PMID').text
            
            # Extract title
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "No title"
            
            # Extract publication date
            pub_date = self._extract_publication_date(article)
            
            # Extract authors
            authors = self._extract_authors(article)
            
            # Filter for pharmaceutical/biotech authors
            non_academic_authors = []
            company_affiliations = []
            corresponding_author_email = None
            
            for author in authors:
                if author.affiliation and self._is_pharmaceutical_biotech_affiliation(author.affiliation):
                    non_academic_authors.append(author.name)
                    company_affiliations.append(author.affiliation)
                
                if author.is_corresponding and author.email:
                    corresponding_author_email = author.email
            
            # Only return papers with at least one pharmaceutical/biotech author
            if not non_academic_authors:
                return None
            
            # Remove duplicates
            company_affiliations = list(set(company_affiliations))
            
            return PaperResult(
                pubmed_id=pubmed_id,
                title=title,
                publication_date=pub_date,
                authors=authors,
                non_academic_authors=non_academic_authors,
                company_affiliations=company_affiliations,
                corresponding_author_email=corresponding_author_email
            )
            
        except Exception as e:
            self._debug_print(f"Error parsing article: {e}")
            return None
    
    def _extract_publication_date(self, article: ET.Element) -> Optional[datetime]:
        """Extract publication date from article."""
        try:
            # Try different date fields
            date_elem = (article.find('.//PubDate') or 
                        article.find('.//DateRevised') or 
                        article.find('.//DateCompleted'))
            
            if date_elem is None:
                return None
            
            year_elem = date_elem.find('Year')
            month_elem = date_elem.find('Month')
            day_elem = date_elem.find('Day')
            
            if year_elem is None:
                return None
            
            year = int(year_elem.text)
            month = 1
            day = 1
            
            if month_elem is not None:
                try:
                    month = int(month_elem.text)
                except ValueError:
                    # Handle month names
                    month_names = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    month = month_names.get(month_elem.text.lower()[:3], 1)
            
            if day_elem is not None:
                try:
                    day = int(day_elem.text)
                except ValueError:
                    day = 1
            
            return datetime(year, month, day)
            
        except Exception:
            return None
    
    def _extract_authors(self, article: ET.Element) -> List[Author]:
        """Extract authors from article."""
        authors = []
        
        author_list = article.find('.//AuthorList')
        if author_list is None:
            return authors
        
        for author_elem in author_list.findall('Author'):
            try:
                # Extract name
                last_name = author_elem.find('LastName')
                first_name = author_elem.find('ForeName')
                
                if last_name is not None:
                    name = last_name.text
                    if first_name is not None:
                        name = f"{first_name.text} {name}"
                else:
                    collective_name = author_elem.find('CollectiveName')
                    if collective_name is not None:
                        name = collective_name.text
                    else:
                        continue
                
                # Extract affiliation
                affiliation = None
                affiliation_elem = author_elem.find('.//Affiliation')
                if affiliation_elem is not None:
                    affiliation = affiliation_elem.text
                
                # Extract email from affiliation
                email = self._extract_email_from_affiliation(affiliation) if affiliation else None
                
                # Check if corresponding author (simplified check)
                is_corresponding = email is not None
                
                authors.append(Author(
                    name=name,
                    affiliation=affiliation,
                    email=email,
                    is_corresponding=is_corresponding
                ))
                
            except Exception as e:
                self._debug_print(f"Error parsing author: {e}")
                continue
        
        return authors
    
    def fetch_papers(self, query: str, max_results: int = 100) -> List[PaperResult]:
        """Main method to fetch papers with pharmaceutical/biotech authors."""
        paper_ids = self.search_papers(query, max_results)
        if not paper_ids:
            return []
        
        return self.fetch_paper_details(paper_ids)