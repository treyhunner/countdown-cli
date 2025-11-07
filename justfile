# Show available commands
_default:
    @printf 'Automation tasks:\n'
    @just --list --unsorted --list-heading '' --list-prefix '  - '

# Install dependencies
setup:
    uv sync --all-groups

# Run all checks (format, lint, test)
check: format lint test

# Format code with ruff
format *files='':
    uv run ruff check --fix {{ files }}
    uv run ruff format {{ files }}

# Lint source code
lint *files='':
    uv run ruff check {{ files }}
    uv run ruff format --check {{ files }}

# Run tests
test *args='':
    uv run pytest -v {{ args }}

# Run tests with coverage
test-cov:
    uv run pytest --cov=countdown --cov=tests --cov-report=term-missing --cov-report=html

# Run tests across all Python versions in parallel
test-all:
    uvx nox -p -s tests

# Bump version (usage: just bump-version patch|minor|major)
bump value:
    uv version --bump {{ value }}

# Build the package
build:
    uv sync  # Force uv version error if applicable
    uv build --clear

# Publish to PyPI
publish:
    uv publish
