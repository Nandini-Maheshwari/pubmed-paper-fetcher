# setup.py - Create this file if not using Poetry

from setuptools import setup, find_packages

setup(
    name="pubmed-paper-fetcher",
    version="0.1.0",
    description="Fetch research papers from PubMed with pharmaceutical/biotech company authors",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "click>=8.1.7",
        "beautifulsoup4>=4.12.2",
        "lxml>=4.9.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "get-papers-list=pubmed_fetcher.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)