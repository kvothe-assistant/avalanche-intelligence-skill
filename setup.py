"""Setup configuration for Avalanche Intelligence Skill."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="avalanche-intelligence",
    version="0.1.0",
    author="Kvothe",
    description="OpenClaw skill for Avalanche blockchain ecosystem monitoring and intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kvothe-assistant/avalanche-intelligence-skill",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.31",
        "aiohttp>=3.9",
        "pyyaml>=6.0",
        "rich>=13.0",
        "vaderSentiment>=3.3",
        "transformers>=4.35",
        "torch>=2.1",
        "chromadb>=0.4",
        "pandas>=2.1",
        "numpy>=1.24",
        "playwright>=1.40",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4",
            "black>=23.0",
            "mypy>=1.7",
            "flake8>=6.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "avalanche-intelligence=avalanche_intelligence.cli:main",
        ],
    },
)
