# Contributing to Avalanche Intelligence

Thank you for your interest in contributing to Avalanche Intelligence!

## Development Setup

1. **Fork the repository**
   ```bash
   # On GitHub, click "Fork" button
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/avalanche-intelligence-skill.git
   cd avalanche-intelligence-skill
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

5. **Run tests**
   ```bash
   pytest
   ```

## Code Style

- Use **Black** for code formatting
- Use **mypy** for type checking
- Use **flake8** for linting

```bash
black avalanche_intelligence/
mypy avalanche_intelligence/
flake8 avalanche_intelligence/
```

## Project Structure

```
avalanche-intelligence-skill/
├── avalanche_intelligence/        # Main package
│   ├── collectors/              # Data collectors (Twitter, Reddit, etc.)
│   ├── analyzers/               # Processing (sentiment, entities, trends)
│   ├── storage/                 # Data persistence (vector DB, time-series)
│   ├── alerts/                  # Alert system
│   ├── api/                     # REST/GraphQL API
│   ├── utils/                   # Helper functions
│   ├── config.py                # Configuration management
│   ├── engine.py                # Main intelligence engine
│   └── cli.py                   # CLI interface
├── config/                      # Configuration files
├── tests/                       # Test files
├── docs/                        # Documentation
├── data/                        # Data directories (gitignored)
└── requirements.txt             # Python dependencies
```

## Adding a New Collector

1. Create a new file in `avalanche_intelligence/collectors/`
2. Inherit from `BaseCollector`
3. Implement `collect()` and `search()` methods
4. Register in `avalanche_intelligence/engine.py`

Example:
```python
from .base import BaseCollector

class NewCollector(BaseCollector):
    async def collect(self, hours: int = 24):
        # Your collection logic
        pass

    async def search(self, query: str):
        # Your search logic
        pass
```

## Adding a New Analyzer

1. Create a new file in `avalanche_intelligence/analyzers/`
2. Implement your analysis logic
3. Integrate in `avalanche_intelligence/engine.py`

## Testing

- Write tests for new features in `tests/`
- Ensure all tests pass before submitting PR
- Test with real data (when applicable)

## Submitting a Pull Request

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow code style guidelines
   - Add tests
   - Update documentation

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "Pull Request"
   - Describe your changes

## Questions?

Feel free to open an issue for questions or discussion.
