---
name: coding
description: Software engineering best practices for writing production-quality, maintainable code
license: MIT
allowed-tools:
  - PythonTools
  - ShellTools
  - FileTools
  - DuckDuckGoTools
  - GithubTools
---

# Coding Skill

Best practices and methodology for writing clean, maintainable, production-quality code.

## When to Use This Skill

Use this skill when writing new code from scratch, reviewing and refactoring existing code,
debugging complex issues, designing software architecture, or writing tests.

## Engineering Principles

### Code Quality Standards
- Readability first: Code is read 10x more than it is written
- Single responsibility: Each function/class does one thing well
- DRY: Don't Repeat Yourself — extract common patterns
- YAGNI: You Aren't Gonna Need It — don't over-engineer
- Fail fast: Validate inputs early, surface errors clearly

### Python Best Practices
Always use type hints, docstrings, and explicit error handling:

```python
def process_data(items: list[str], limit: int = 100) -> dict[str, int]:
    """Process items and return frequency count.

    Args:
        items: List of string items to process
        limit: Maximum number of items to process

    Returns:
        Dictionary mapping item to frequency count

    Raises:
        ValueError: If limit is negative
    """
    if limit < 0:
        raise ValueError(f"limit must be non-negative, got {limit}")

    result: dict[str, int] = {}
    for item in items[:limit]:
        result[item] = result.get(item, 0) + 1
    return result
```

### Error Handling Pattern
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

### Testing Approach
1. Write tests before or alongside code (TDD when practical)
2. Test happy path, edge cases, and error cases
3. Use descriptive test names: `test_should_return_empty_dict_when_input_is_empty`
4. Mock external dependencies

## Code Review Checklist
- Does it solve the stated problem?
- Are edge cases handled?
- Is error handling appropriate?
- Are there tests?
- Is it readable without comments?
- Are there any security issues?
- Is performance acceptable for expected load?

## Debugging Methodology
1. Reproduce the issue reliably
2. Isolate the failing component
3. Form a hypothesis
4. Test the hypothesis
5. Fix and verify
6. Add a test to prevent regression
