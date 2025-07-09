# 6. README.md

# PubMed Paper Fetcher

A Python tool to fetch research papers from PubMed with pharmaceutical/biotech company authors.

## Features

- Fetch research papers from PubMed API
- Filter papers with at least one author from pharmaceutical/biotech companies
- Support for full PubMed query syntax
- Export results to CSV format
- Command-line interface with debug mode
- Type hints throughout the codebase

## Installation

### Prerequisites

- Python 3.13 or higher
- Poetry for dependency management

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pubmed-paper-fetcher
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

## Usage

### Command Line Interface

The main command is `get-papers-list`:

```bash
# Basic usage
get-papers-list "cancer treatment"

# Save results to CSV file
get-papers-list "COVID-19 AND vaccine" -f results.csv

# Enable debug mode
get-papers-list "diabetes" --debug

# Specify maximum results
get-papers-list "alzheimer" --max-results 50 -f alzheimer_papers.csv
```

### Command Line Options

- `-h, --help`: Show help message
- `-d, --debug`: Enable debug mode for detailed output
- `-f, --file FILENAME`: Save results to specified CSV file (default: print to console)
- `--max-results NUMBER`: Maximum number of results to fetch (default: 100)

### Query Syntax

The tool supports PubMed's full query syntax:

```bash
# Basic keyword search
get-papers-list "machine learning"

# Boolean operators
get-papers-list "cancer AND treatment"
get-papers-list "COVID-19 OR coronavirus"

# Field-specific searches
get-papers-list "cancer[Title] AND treatment[Abstract]"

# Date ranges
get-papers-list "diabetes AND 2020:2023[Date - Publication]"
```

## Code Organization

```
pubmed_fetcher/
├── __init__.py          # Package initialization
├── models.py            # Data models (Author, PaperResult)
├── fetcher.py           # Main fetching logic (PubMedFetcher)
└── cli.py               # Command-line interface
```

### Key Components

1. **PubMedFetcher**: Main class that handles API calls and paper processing
2. **PaperResult**: Data model representing a research paper
3. **Author**: Data model representing paper authors
4. **CLI**: Command-line interface built with Click

## Output Format

The CSV output contains the following columns:

- **PubmedID**: Unique identifier for the paper
- **Title**: Paper title
- **Publication Date**: Publication date (YYYY-MM-DD format)
- **Non-academic Author(s)**: Names of authors from pharmaceutical/biotech companies
- **Company Affiliation(s)**: Company names and affiliations
- **Corresponding Author Email**: Email of the corresponding author

## Company Detection Logic

The tool identifies pharmaceutical/biotech companies using:

1. **Keyword matching**: Searches for terms like "pharmaceutical", "biotech", "therapeutics", etc.
2. **Company name recognition**: Includes major pharma companies like Pfizer, Novartis, etc.
3. **Academic exclusion**: Excludes institutions with academic keywords like "university", "hospital", etc.

## Error Handling

The tool includes robust error handling for:

- Invalid PubMed queries
- API rate limits and failures
- Malformed XML responses
- Missing data fields
- Network connectivity issues

## Development

### Dependencies

- **requests**: HTTP library for API calls
- **click**: Command-line interface framework
- **beautifulsoup4**: XML parsing (backup parser)
- **lxml**: Fast XML processing

### Development Dependencies

- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black .
```

### Type Checking

```bash
poetry run mypy pubmed_fetcher/
```

## Tools Used

This project was developed with assistance from:

- **Claude AI**: For code structure and implementation guidance
- **PubMed E-utilities API**: https://www.ncbi.nlm.nih.gov/books/NBK25497/
- **Poetry**: https://python-poetry.org/
- **Click**: https://click.palletsprojects.com/

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## API Rate Limits

The tool respects PubMed's API guidelines:
- Maximum 3 requests per second
- Built-in rate limiting between batch requests
- Proper User-Agent headers

## Troubleshooting

### Common Issues

1. **No results found**: Check your query syntax and ensure it's valid for PubMed
2. **API errors**: Verify internet connection and try reducing max-results
3. **Missing affiliations**: Some papers may not have complete author affiliation data

### Debug Mode

Use the `--debug` flag to see detailed information about:
- API requests and responses
- Paper filtering process
- Error messages and warnings