# FastMCP Installation Guidelines

## Recommended Installation Methods

### Primary Method: Using uv (Recommended)
```bash
uv add fastmcp
```
Alternative uv command:
```bash
uv pip install fastmcp
```

### Alternative Method: Using pip
```bash
pip install fastmcp
```

## Installation Verification
Verify successful installation by running:
```bash
fastmcp version
```

Expected output includes:
- FastMCP version
- MCP version
- Python version
- Platform details

## Version Management Best Practices

### Pinning Dependencies
**Critical Guideline**: Always pin FastMCP to a specific version in dependencies to avoid breaking changes.

Example in `requirements.txt`:
```
fastmcp==2.1.0
```

### Breaking Changes Policy
- Breaking changes occur only on minor version updates
- Deprecation warnings issued before API removals
- Recommended to review release notes before upgrading

## Development Installation

### From Source
```bash
git clone https://github.com/jlowin/fastmcp.git
cd fastmcp
uv sync
```

### Running Tests
```bash
pytest
```

### Code Quality Tools
- Pre-commit hooks available for code quality
- Follow project's contribution guidelines

## Migration Guidelines

### Upgrading from MCP SDK 1.0 to FastMCP 2.0
- Generally straightforward migration path
- Update import statement:
  ```python
  from fastmcp import FastMCP
  ```
- Review breaking changes in release notes

## Standards for AI Projects
- Always use virtual environments
- Pin specific FastMCP versions in production
- Verify installation before proceeding with development
- Keep development dependencies separate from production requirements