# Project Kaizen MCP Server - AI Instructions

## Quick Reference Links
- 📐 **Architecture**: [docs/architecture.md](docs/architecture.md) - FastMCP patterns + server structure
- 🔍 **Examples**: [docs/fastmcp-examples.md](docs/fastmcp-examples.md) - Proven project layouts
- ⚠️ **Pitfalls**: [docs/pitfalls.md](docs/pitfalls.md) - Known issues + solutions
- 🛡️ **Type Safety**: [docs/type-safety.md](docs/type-safety.md) - mypy + validation patterns
- 🗃️ **Database**: [docs/database.md](docs/database.md) - PostgreSQL + AsyncPG decisions
- 🔧 **Tooling**: [docs/tooling.md](docs/tooling.md) - Development workflow

## Project Overview
Project Kaizen is an MCP server that elevates transient AI interactions into a persistent foundation of organizational knowledge.

## Git Commit Messages

Follow semantic versioning (semver) format for all commits:

```
<type>: <description>
[optional bullet points]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Rules**:
- Use present tense ("add feature" not "added feature")
- Maximum 5 lines total per commit message
- No empty lines between lines
- Bullet points allowed for listing changes
- No Claude signatures or attribution messages
- Be concise and descriptive

**Example**:
```
feat: add knowledge persistence to Neo4j
- Implement node creation for knowledge entries
- Add relationship mapping between concepts
- Configure database connection pooling
```

## Code Formatting Rules

- All files must end with a newline character
- Ensure proper file termination when creating or editing files

## Pre-Commit Validation

Before any `git commit` or `git push`, AI must verify:

- **File endings**: All changed files that will be committed must end with a trailing newline character
- **Best practices compliance**: Check staged files follow proper file termination standards
- **Validation process**: Use git status/diff to identify changed files, then verify each ends with newline

**Implementation**: Run validation check on all staged files before executing commit commands.

## Development Guidelines

**For detailed implementation patterns, refer to the documentation links above.**

Key principles:
- Follow FastMCP single instance pattern (see Architecture docs)
- Use strict type checking with zero tolerance for errors
- Validate all database operations and nullable results
- Implement proper error handling with structured logging

**Pre-commit Requirements:**
```bash
uv run mypy src/ --strict      # Must pass with zero errors
uv run ruff check src/ --fix   # Auto-fix linting issues
```

## Communication Style

- Keep terminal outputs concise and conversational
- Break large changes into small, understandable pieces
- Use output tokens efficiently - avoid verbose explanations
- Present information in digestible chunks
- Focus on what matters most to the user's immediate needs