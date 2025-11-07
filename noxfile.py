"""Nox sessions for multi-version testing."""

import nox

nox.options.default_venv_backend = "uv"

# Python versions to test, matching pyproject.toml classifiers
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13", "3.14", "3.15"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite with coverage for each Python version."""
    session.install(
        "pytest>=8.2.0",
        "pytest-cov>=5.0.0",
        "coverage[toml]>=7.5.1",
        ".",
    )
    session.run(
        "pytest",
        "--cov=countdown",
        "--cov=tests",
        "--cov-report=term-missing",
        *session.posargs,
    )
