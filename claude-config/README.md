# Shucle AI Agent

Monorepo for Shucle AI Agents. This project leverages Google's **Agent Development Kit (ADK)** and **Gemini** models to create intelligent agents for mobility service analysis and management, with multi-model orchestration support through HChat.

## Project Structure

```
shucle-ai-agent/
├── agents/              # Agent implementations
│   ├── mobility_data_analyst/           # Direct Gemini implementation
│   ├── hchat_mobility_data_analyst/     # Multi-model variant
│   ├── demand_pattern_analyst/          # DRT demand analysis
│   ├── regional_analyst/                # Regional analysis
│   └── planning_qa_agent/               # Planning Q&A agent
├── apps/                # CLI runners and applications
│   ├── cli_runner/      # CLI application for running agents
│   └── planning_qa_slack_bot/           # Slack bot integration
├── libs/                # Shared libraries
│   ├── utils/           # Core utilities (PromptLoader, adk_utils, config)
│   ├── logger/          # Logging configuration
│   ├── data/            # Data I/O utilities
│   ├── hchat_service/   # Multi-model orchestration
│   ├── hchat_adk/       # HChat ADK adapter
│   ├── processing/      # Domain-specific data processing (demand, pubtrans, regional)
│   ├── knowledge/       # Knowledge base management
│   ├── report_templates/  # HTML report templates
│   └── slack_integration/  # Slack bot integration
├── data/                # Data files (zone-based structure)
│   ├── raw/             # Raw source data
│   └── processed/       # Preprocessed data organized by zone
│       ├── 40/          # Zone 40 data (Icheon)
│       ├── 47/          # Zone 47 data
│       ├── 67/          # Zone 67 data
│       └── 78/          # Zone 78 data
├── output/              # Generated artifacts
│   ├── reports/         # HTML reports
│   └── logs/            # Log files
└── scripts/             # Validation and utility scripts
```

## Prerequisites

- **Python 3.12+** - Check with `python --version`
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **Google API Key** - Required for Gemini model access
- **HChat API Key** - Optional, for multi-model orchestration

## Quick Start

### 1. Installation

Install `uv` package manager:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sync workspace dependencies:

```bash
uv sync
```

### 2. Configuration

Create a `.env` file in the root directory:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (for multi-model orchestration)
H_CHAT_API_KEY=your_hchat_api_key_here

# Optional (environment selector for secret files)
SHUCLE_ENV=local  # local, qa, or real

# Optional logging
LOG_LEVEL=INFO
```

**Getting API Keys:**

- Google Gemini: Visit https://ai.google.dev/ and create an API key
- HChat: Contact your HChat service provider

**Environment-Based Configuration:**

Secret files are selected based on `SHUCLE_ENV` environment variable (defaults to `local`):
- `SHUCLE_ENV=local` → `secrets/secret-local.yml`
- `SHUCLE_ENV=qa` → `secrets/secret-qa.yml`
- `SHUCLE_ENV=real` → `secrets/secret-real.yml`

Fetch secrets from AWS Secrets Manager:
```bash
./get_secrets.sh
```

### 3. Running Agents

**Standard Mobility Data Analyst (Gemini only):**

```bash
uv run python apps/cli_runner/src/cli_runner/runners/mobility_runner.py
```

**HChat Mobility Data Analyst (Multi-model with fallback):**

```bash
uv run python apps/cli_runner/src/cli_runner/runners/hchat_mobility_runner.py
```

**Regional Analyst (Zone-based analysis):**

```bash
uv run python apps/cli_runner/src/cli_runner/runners/hchat_regional_runner.py \
  --zone-id 67 \
  --log-level INFO
```

**Demand Pattern Analyst (DRT demand analysis):**

```bash
uv run python apps/cli_runner/src/cli_runner/runners/hchat_demand_runner.py \
  --zone-id 67 \
  --start-date 20251101 \
  --end-date 20251130 \
  --log-level INFO
```

**Planning Q&A Agent:**

```bash
uv run python apps/cli_runner/src/cli_runner/runners/planning_qa_runner.py
```

**With Custom Log Level:**

```bash
uv run python apps/cli_runner/src/cli_runner/runners/mobility_runner.py --log-level DEBUG
```

**Available log levels:** `TRACE`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Run as Web Service:**

```bash
cd agents/mobility_data_analyst/src
uv run --project agents/mobility_data_analyst adk web --port 8000
```

Access the web interface at http://localhost:8000

### 4. View Results

Reports are generated in:
- Mobility analysis: `output/reports/mobility_report.html`
- Demand analysis (Track A): `output/reports/demand_pattern_report_{zone_id}_{timestamp}.html`
- Regional analysis (Track A): `output/reports/regional_report_{zone_id}_{timestamp}.html`

Analysis results (JSON):
- `output/analysis_results/demand_analysis_{zone_id}_{start_date}_{end_date}_{timestamp}.json`
- `output/analysis_results/regional_analysis_{zone_id}_{timestamp}.json`

## Claude Skills (Recommended)

If you're using Claude Code CLI, this repository includes 4 custom skills to streamline development:

- `code-simplifier` - Simplifies and refines code for clarity and maintainability
- `lint-fix` - Run ruff linting with automatic fixing
- `python-patterns` - Pythonic idioms, PEP 8 standards, type hints, and best practices
- `python-testing` - Python testing strategies using pytest, TDD methodology

See `.claude/skills/` for detailed skill files.

## Development

### Running Tests

```bash
# Run all unit tests
uv run pytest -m unit

# Run integration tests
uv run pytest -m integration

# Run specific test suite
uv run pytest libs/utils/tests/ -v

# Run with coverage
uv run pytest --cov=agents
```

### Creating a New Agent

**Using Claude Skills (recommended):**

```bash
# Use the /scaffold skill for automated scaffolding
/scaffold
# Then follow interactive prompts
```

**Manual creation:**

1. **Create directory structure:**

```bash
mkdir -p agents/my_agent/src/my_agent/{prompts,tools}
mkdir -p agents/my_agent/tests
```

2. **Add `pyproject.toml`:**

```toml
[project]
name = "my-agent"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "google-genai>=1.56.0",
    "utils",
    "logger",
]

[tool.uv.sources]
utils = { workspace = true }
logger = { workspace = true }
```

3. **Implement agent in `src/my_agent/agent.py`**

4. **Create prompts in `src/my_agent/prompts/system.yaml`**

5. **Add tools in `src/my_agent/tools/`**

6. **Create runner in `apps/cli_runner/src/cli_runner/runners/`**

7. **Sync workspace:**

```bash
uv sync
```

See existing agents in `agents/` directory for complete working examples.

### Tool Development Best Practices

```python
def analyze_data(data_path: str, threshold: float = 0.5) -> dict:
    """
    Analyze data from CSV file.

    Args:
        data_path: Path to CSV file
        threshold: Analysis threshold (default: 0.5)

    Returns:
        dict: Analysis results with 'status' and 'data' keys
    """
    # Implementation
    return {"status": "success", "data": [...]}
```

**Key points:**

- Clear docstrings (used by ADK for tool descriptions)
- Type hints for all parameters and returns
- Simple return types (str, int, dict, list)
- Proper error handling

### Prompt Management

Prompts are stored in YAML with Jinja2 templates:

```yaml
main:
  template: |
    You are an expert in {{ task_description }}.

    Available tools:
    {% for tool in tools %}
    - {{ tool }}
    {% endfor %}
```

Load prompts:

```python
from utils.prompt_loader import PromptLoader

loader = PromptLoader(Path(__file__).parent / "prompts")
prompt = loader.load("system.yaml", "main", task_description="data analysis")
```

## Common Commands

```bash
# Sync dependencies after changes
uv sync

# Sync with dev dependencies
uv sync --dev

# Run tests with markers
uv run pytest -m unit
uv run pytest -m integration

# Run tests with coverage
uv run pytest --cov=agents --cov=libs

# Validate repository structure
uv run python scripts/validate_structure.py
```

## Data Structure

### Directory Organization

Processed data is organized by zone in `data/processed/{zone_id}/`:

```
data/processed/
├── 40/                                    # Zone 40 (Icheon)
│   ├── facility_zone_40.csv              # Individual POI records
│   ├── zone_grid_data_preprocessed_zone_40.csv  # Grid with demographics
│   ├── demand_data_preprocessed_40_*.csv # Demand data
│   └── ...
├── 47/                                    # Zone 47
├── 67/                                    # Zone 67
└── 78/                                    # Zone 78
```

### Standard Column Names

**POI Data (`facility_zone_{zone_id}.csv`):**
- `poi_name`: POI name (previously `fname`)
- `poi_lon`: Longitude (previously `center_x1`)
- `poi_lat`: Latitude (previously `center_y1`)
- `poi_insight_category`: Unified category (previously `ca_name/cb_name/cc_name`)
- Note: `cc_name` also exists for backward compatibility

**Grid Data (`zone_grid_data_preprocessed_zone_{zone_id}.csv`):**
- `grid_id`: Grid identifier
- `grid_geometry_4326`: WKT geometry in EPSG:4326 (previously `geometry_wkt`)
- `total_population`: Population count (previously `grid_population`)

**Polygon Data:**
- `boundary_type`: Type of boundary (e.g., 'zone')
- `geometry_wkt_4326`: WKT geometry in EPSG:4326

## Key Libraries

- **utils**: `PromptLoader` for YAML prompts, `adk_utils` for ADK helpers, environment-based config
- **logger**: Custom TRACE level, consistent formatting
- **data**: Data collection, processing, and storage (See [libs/data/README.md](libs/data/README.md))
- **hchat_service**: Multi-model orchestration with automatic fallback
- **hchat_adk**: Adapter to use HChat with Google ADK interface
- **processing**: Domain-specific data processing (demand, pubtrans, regional) - See [libs/processing/README.md](libs/processing/README.md)
- **knowledge**: Knowledge base management
- **report_templates**: HTML report generation templates
- **slack_integration**: Slack bot integration
