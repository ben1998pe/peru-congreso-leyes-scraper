# Peru Congress Laws Scraper - Makefile
# Enhanced version with comprehensive project management

.PHONY: help install install-dev clean test lint format type-check run scrape clean-data validate analyze monitor setup-env docs

# Default target
help:
	@echo "🇵🇪 Peru Congress Laws Scraper - Enhanced Version"
	@echo "=================================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install        Install the package and dependencies"
	@echo "  install-dev    Install development dependencies"
	@echo "  setup-env      Setup development environment"
	@echo "  clean          Clean build artifacts and cache"
	@echo "  test           Run test suite"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code with black"
	@echo "  type-check     Run type checking with mypy"
	@echo "  run            Run basic scraping example"
	@echo "  scrape         Run enhanced scraper"
	@echo "  clean-data     Clean existing data files"
	@echo "  validate       Validate data quality"
	@echo "  analyze        Analyze scraped data"
	@echo "  analyze-complete Run complete analysis pipeline"
	@echo "  health-check    Run project health check"
	@echo "  monitor        Monitor system performance"
	@echo "  docs           Generate documentation"
	@echo "  setup-git      Setup git hooks and configuration"
	@echo ""

# Installation
install:
	@echo "📦 Installing package and dependencies..."
	pip install -r requirements.txt
	pip install -e .

install-dev: install
	@echo "🔧 Installing development dependencies..."
	pip install -e ".[dev]"

setup-env: install-dev setup-git
	@echo "🚀 Setting up development environment..."
	@echo "✅ Environment setup complete!"

# Code quality
clean:
	@echo "🧹 Cleaning build artifacts and cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

test:
	@echo "🧪 Running test suite..."
	python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

lint:
	@echo "🔍 Running linting checks..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	@echo "🎨 Formatting code with black..."
	black . --line-length 100 --target-version py38

type-check:
	@echo "🔍 Running type checking..."
	mypy . --ignore-missing-imports

# Scraping operations
run:
	@echo "🚀 Running basic scraping example..."
	python ejemplo_uso.py

scrape:
	@echo "🚀 Running enhanced scraper..."
	python cli.py scrape --monitor

scrape-custom:
	@echo "🚀 Running custom scraping..."
	@read -p "Enter start date (DD/MM/YYYY): " start_date; \
	read -p "Enter end date (DD/MM/YYYY): " end_date; \
	python cli.py scrape --fecha-desde "$$start_date" --fecha-hasta "$$end_date" --monitor

# Data operations
clean-data:
	@echo "🧹 Cleaning existing data files..."
	python cli.py clean --input data/proyectos_ley_*.csv --show-stats

validate:
	@echo "🔍 Validating data quality..."
	@if [ -z "$$(ls data/proyectos_ley_*.csv 2>/dev/null)" ]; then \
		echo "❌ No data files found in data/ directory"; \
		exit 1; \
	fi
	python cli.py validate --input data/proyectos_ley_*.csv

analyze:
	@echo "📊 Analyzing scraped data..."
	@if [ -z "$$(ls data/proyectos_ley_*.csv 2>/dev/null)" ]; then \
		echo "❌ No data files found in data/ directory"; \
		exit 1; \
	fi
	python cli.py analyze --input data/proyectos_ley_*.csv --format html

analyze-complete:
	@echo "📊 Running complete analysis..."
	python scripts/run_analysis.py

health-check:
	@echo "🏥 Running project health check..."
	python scripts/health_check.py

# Monitoring
monitor:
	@echo "📈 Starting performance monitoring..."
	python cli.py monitor --duration 60

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/html; \
		echo "📚 Documentation generated in docs/_build/html/"; \
	else \
		echo "❌ Sphinx not installed. Install with: pip install sphinx"; \
	fi

# Git setup
setup-git:
	@echo "🔧 Setting up git hooks..."
	@if [ -d .git ]; then \
		pre-commit install 2>/dev/null || echo "⚠️ Pre-commit not installed"; \
		echo "✅ Git hooks configured"; \
	else \
		echo "⚠️ Not a git repository"; \
	fi

# Development workflow
dev-setup: setup-env
	@echo "🎯 Development setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make test' to verify everything works"
	@echo "  2. Run 'make scrape' to test the scraper"
	@echo "  3. Run 'make analyze' to analyze data"

# Production deployment
deploy:
	@echo "🚀 Preparing for deployment..."
	make clean
	make test
	make lint
	make type-check
	@echo "✅ Ready for deployment!"

# Quick start
quickstart:
	@echo "🚀 Quick start setup..."
	make install
	make scrape
	@echo "✅ Quick start complete!"

# Data pipeline
pipeline: scrape clean-data validate analyze
	@echo "🔄 Data pipeline completed!"

# All quality checks
quality: lint format type-check test
	@echo "✅ All quality checks passed!"

# Update dependencies
update-deps:
	@echo "📦 Updating dependencies..."
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

# Show project info
info:
	@echo "🇵🇪 Peru Congress Laws Scraper - Enhanced Version"
	@echo "=================================================="
	@echo "Version: 2.0.0"
	@echo "Author: Benjamin Oscco Arias"
	@echo "Repository: https://github.com/ben1998pe/peru-congreso-leyes-scraper"
	@echo ""
	@echo "Features:"
	@echo "  ✅ Enhanced error handling"
	@echo "  ✅ Data validation"
	@echo "  ✅ Performance monitoring"
	@echo "  ✅ Comprehensive CLI"
	@echo "  ✅ Test suite"
	@echo "  ✅ Code quality tools"
	@echo ""
	@echo "Quick commands:"
	@echo "  make scrape    - Run the scraper"
	@echo "  make analyze   - Analyze data"
	@echo "  make test      - Run tests"
	@echo "  make help      - Show all commands"

# Default target
.DEFAULT_GOAL := help
