# Current Task: Design MCP Knowledge Protocol

## Session Context
We are designing the data structure and communication protocol for Project Kaizen's knowledge retrieval system. Working on the mcp-knowledge-protocol.md file.

## Current Challenge
Designing a protocol that allows AI to discover and retrieve knowledge with automatic inheritance resolution (most specific wins).

## Key Decisions Made
1. **Terminology**:
   - **Tier**: Hierarchical level (GENERAL, PRODUCT, GROUP, PROJECT)
   - **Scope**: Named container at a tier (e.g., "checkout-api" at PROJECT tier)
   - **Entry**: Individual knowledge item
2. **Protocol**: 3-step discovery (Categories → Keywords → Knowledge) - but hitting edge cases
3. **Inheritance**: MCP should resolve internally, AI gets clean results

## Current Problem
The protocol assumes flat categories, but real-world has hierarchical categories:
```
git/
  workflows/
    - commit
    - push
  branching/
    - merge
```

This breaks the simple "get keywords for 'git'" approach.

## Communication Style Required
- User wants SHORT, CONCISE responses
- NO long explanations or overwhelming details
- Focus on solutions, not implementation details
- User will push back if responses are too verbose

## Next Steps
1. Redesign protocol to handle hierarchical categories
2. Consider category navigation/discovery mechanism
3. Keep inheritance resolution simple despite category complexity

## Important Context
- Project Kaizen is an MCP server for AI persistent memory
- Uses 4-tier inheritance: GENERAL → PRODUCT → GROUP → PROJECT
- "Most specific wins" is core principle
- We are designing the PROTOCOL, not choosing technology
- Must fit existing business requirements in documentation
- Technology decisions come AFTER protocol is solid

## Session Personality
- User appreciates pushback and debate
- Wants AI to "stand ground" when appropriate
- Values thinking through edge cases
- Gets frustrated with premature implementation details
