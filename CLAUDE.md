# Project Kaizen - Claude Instructions

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
feat: add knowledge persistence to PostgreSQL
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

## Complex Task Planning Protocol

For complex, multi-step tasks that involve significant changes or architectural decisions:

1. **Initial Investigation Phase**
   - Use TodoWrite tool to create detailed task breakdown
   - Research existing codebase and documentation thoroughly
   - Identify all potential impacts, dependencies, and edge cases

2. **Planning Communication Phase**
   - Present findings and proposed approach to user
   - Create detailed plan with clear steps and rationale
   - Request user feedback, context, and approval
   - Iterate on plan based on user input until approved

3. **Implementation Phase**
   - Only proceed with invasive actions after explicit user approval
   - Execute approved plan systematically using todo tracking
   - Update todos in real-time as work progresses
   - Communicate any deviations or issues immediately

**Complex Task Indicators:**
- Tasks affecting multiple files or system components
- Architectural changes or new feature implementations
- Specification creation or protocol design
- Tasks with potential for breaking changes
- Tasks requiring domain knowledge or business decisions

**Communication Requirements:**
- Always explain your reasoning and approach
- Highlight risks, assumptions, and trade-offs
- Ask clarifying questions when requirements are ambiguous
- Seek approval before making significant changes
- Keep user informed of progress and blockers

## Communication Style

- Keep terminal outputs concise and conversational
- Break large changes into small, understandable pieces
- Use output tokens efficiently - avoid verbose explanations
- Present information in digestible chunks
- Focus on what matters most to the user's immediate needs

## MCP Server Development

For MCP server specific development, see: `mcp-server/CLAUDE.md`