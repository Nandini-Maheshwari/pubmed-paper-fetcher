"""Command-line interface for PubMed paper fetcher."""

import click
import csv
import sys
from typing import List

from .fetcher import PubMedFetcher
# from .models import PaperResult

@click.command()
@click.argument("query", required=True)
@click.option(
    "-d", "--debug", is_flag=True, help="Print debug information during execution"
)
@click.option(
    "-f", "--file", "output_file", help="Specify the filename to save the results"
)
@click.option("--max-results", default=100, help="Maximum number of results to fetch")
def main(query: str, debug: bool, output_file: str, max_results: int):
    """
    Fetch research papers from PubMed with pharmaceutical/biotech company authors.

    QUERY: PubMed search query (supports full PubMed query syntax)

    Examples:
        get-papers-list "cancer treatment"
        get-papers-list "COVID-19 AND vaccine" -f results.csv
        get-papers-list "diabetes" --debug --max-results 50
    """
    try:
        fetcher = PubMedFetcher(debug=debug)

        if debug:
            print(f"Fetching papers for query: {query}")
            print(f"Maximum results: {max_results}")

        papers = fetcher.fetch_papers(query, max_results)

        if not papers:
            print("No papers found with pharmaceutical/biotech company authors.")
            return

        if debug:
            print(f"Found {len(papers)} papers with pharmaceutical/biotech authors")

        # Prepare CSV data
        csv_data = [paper.to_csv_row() for paper in papers]

        if output_file:
            write_csv_file(csv_data, output_file)
            print(f"Results saved to {output_file}")
        else:
            write_csv_stdout(csv_data)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def write_csv_file(data: List[dict], filename: str) -> None:
    """Write CSV data to file."""
    if not data:
        return

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def write_csv_stdout(data: List[dict]) -> None:
    """Write CSV data to stdout."""
    if not data:
        return

    fieldnames = data[0].keys()
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)


if __name__ == "__main__":
    main()
