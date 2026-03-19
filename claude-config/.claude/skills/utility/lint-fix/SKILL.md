---
name: lint-fix
triggers:
  - "lint fix"
description: Run ruff linting with automatic fixing for code quality
---

# Lint & Fix Skill

**Purpose**: Run ruff linting with automatic fixing for code quality

## Description

This skill runs ruff for linting and formatting with smart auto-fixing. It:

- Checks code formatting issues
- Auto-fixes safe issues
- Sorts imports properly
- Formats code consistently
- Shows summary of fixed vs. remaining issues

## Working Directory

Must be executed from: `/Users/younghyunju/Projects/shucle/shucle-ai-agent`

## Execution Protocol

### 1. Parse User Intent

Determine lint operation from user input:

- `check` - Check for issues without fixing
- `fix` - Auto-fix safe issues (default)
- `imports` - Fix and sort imports
- `format` - Format code with ruff format
- `all` - Run check, fix, imports, and format

### 2. Execute Lint Operations

**Check only** (no fixes):

```bash
uv run ruff check libs/ agents/ apps/
```

**Auto-fix safe issues** (default):

```bash
uv run ruff check libs/ agents/ apps/ --fix
```

**Fix and sort imports**:

```bash
uv run ruff check --select I libs/ agents/ apps/ --fix
```

**Format code**:

```bash
uv run ruff format libs/ agents/ apps/
```

**Complete workflow** (all operations):

```bash
# 1. Fix issues
uv run ruff check libs/ agents/ apps/ --fix

# 2. Sort imports
uv run ruff check --select I libs/ agents/ apps/ --fix

# 3. Format code
uv run ruff format libs/ agents/ apps/
```

### 3. Parse Results

After linting:

- Count fixed issues
- List remaining issues
- Categorize by severity
- Show file locations

### 4. Handle Unfixable Issues

For issues that can't be auto-fixed:

- Show file path and line number
- Display issue description
- Suggest manual fix
- Provide ruff documentation link if needed

### 5. Error Handling

**Syntax errors**:

```
Error: Syntax error in file

File: libs/utils/src/utils/helper.py
Line: 45
Error: Expected ':' after function definition

To fix:
1. Check recent changes in this file
2. Look for: missing colons, unclosed brackets, indentation errors
3. Fix syntax error manually
4. Run /lint again to continue
```

**Unfixable linting issues**:

```
Warning: 3 issues require manual fixes

libs/utils/src/utils/helper.py:23:5 - F841 Local variable 'x' assigned but never used
agents/mobility/src/agent.py:67:1 - E501 Line too long (95 > 88 characters)
libs/logger/src/logger/config.py:34:12 - B008 Do not use mutable default argument

These issues need manual review and fixing.
```

**Import sorting conflicts**:

```
Warning: Import order conflicts detected

The following files have import issues:
- libs/utils/src/utils/__init__.py

Suggested fix order:
1. Standard library imports
2. Third-party imports
3. Local imports

Run: uv run ruff check --select I <file> --fix
```

## Usage Examples

User: "lint the code"
→ Run auto-fix on all directories

User: "check for linting issues"
→ Run check-only mode (no fixes)

User: "fix imports"
→ Run import sorting

User: "format everything"
→ Run complete workflow (fix + imports + format)

## Output Format

**Success with fixes**:

```
✓ Running ruff auto-fix...

Fixed issues:
- libs/utils/src/utils/helper.py: 3 issues fixed
- agents/mobility/src/agent.py: 2 issues fixed
- apps/cli_runner/src/config.py: 1 issue fixed

Total: 6 issues fixed

✓ Sorting imports...
Formatted 2 files

✓ Formatting code...
Formatted 15 files

All linting issues resolved!
```

**With remaining issues**:

```
⚠ Running ruff auto-fix...

Fixed: 6 issues
Remaining: 3 issues requiring manual fixes

Unfixable issues:
1. libs/utils/src/utils/helper.py:23:5
   F841: Local variable 'x' assigned but never used
   → Remove unused variable

2. agents/mobility/src/agent.py:67:1
   E501: Line too long (95 > 88 characters)
   → Break line or refactor

3. libs/logger/src/logger/config.py:34:12
   B008: Do not use mutable default argument
   → Use None and initialize in function

After fixing these manually, run: /lint
```

**Check-only mode**:

```
✓ Checking code quality...

Found 4 issues:
- libs/utils/src/utils/helper.py: 2 issues
- agents/mobility/src/agent.py: 2 issues

Run with auto-fix: /lint fix
```

## Lint Rules

Ruff is configured to check for:

- **F** - Pyflakes (unused imports, undefined names)
- **E/W** - pycodestyle (PEP 8 style violations)
- **I** - isort (import sorting)
- **N** - pep8-naming (naming conventions)
- **B** - flake8-bugbear (common bugs)
- **UP** - pyupgrade (modern Python syntax)

## Notes

- Ruff configuration is in `pyproject.toml` at project root
- Line length limit: 79 characters (team standard)
- Import order: stdlib → third-party → local
- Auto-fixes are safe and won't change code behavior
- Always review changes before committing
- Some issues (like unused variables) need manual review
- Format runs after fixes to ensure consistent style
- Ruff is much faster than pylint/flake8 (10-100x)
- CI/CD runs ruff check in lint workflow

## Gotchas (실패 포인트)

- ruff fix는 안전한 수정만 자동화 — unsafe 수정은 `--unsafe-fixes` 필요 (팀 확인)
- format 후 check 다시 실행 — 포맷이 새 lint 오류 만들 수 있음
- 대량 자동 수정 시 diff 반드시 검토 — 로직 변경 가능성
