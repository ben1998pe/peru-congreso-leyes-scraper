"""
Setup script for Peru Congress Laws Scraper
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="peru-congreso-leyes-scraper",
    version="2.0.0",
    author="Benjamin Oscco Arias",
    author_email="benjamin.oscco@example.com",
    description="Enhanced web scraper for Peru Congress Law Projects with advanced error handling, data validation, and performance monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ben1998pe/peru-congreso-leyes-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
        "analysis": [
            "jupyter>=1.0.0",
            "ipykernel>=6.26.0",
            "matplotlib>=3.8.0",
            "seaborn>=0.13.0",
            "plotly>=5.17.0",
        ],
        "monitoring": [
            "psutil>=5.9.0",
            "memory-profiler>=0.61.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "congreso-scraper=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/ben1998pe/peru-congreso-leyes-scraper/issues",
        "Source": "https://github.com/ben1998pe/peru-congreso-leyes-scraper",
        "Documentation": "https://github.com/ben1998pe/peru-congreso-leyes-scraper#readme",
    },
)
