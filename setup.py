#!/usr/bin/env python3
"""
Setup script for the Autonomous Agent-Based Testing Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [line.strip() for line in requirements_path.read_text().splitlines() 
                   if line.strip() and not line.startswith("#")]

setup(
    name="autonomous-testing-framework",
    version="0.1.0",
    author="AdamG-74",
    author_email="gillespieads@gmail.com",
    description="Autonomous Agent-Based Testing Framework with Mutation Testing and Quality Assessment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crewai_testing",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "autonomous-testing=src.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="testing, ai, agents, mutation-testing, code-quality, automation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/crewai_testing/issues",
        "Source": "https://github.com/yourusername/crewai_testing",
        "Documentation": "https://github.com/yourusername/crewai_testing#readme",
    },
) 