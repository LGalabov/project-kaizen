# Project Kaizen

*MCP server that elevates transient AI interactions into a persistent foundation of organizational knowledge*

**Kaizen** (改善) - Japanese for "continuous improvement" - captures how AI agents learn incrementally with each interaction, transforming from tools into knowledgeable team members.

## Project Overview

Project Kaizen enables AI agents to maintain persistent knowledge across sessions, transforming them from stateless assistants into learning team members with deep project understanding.

## Documentation

### 📋 [Product Specification](./docs/product-specification.md)
The complete product vision, use cases, and expected behaviors. **Start here** to understand what we're building and why.

### 📖 [Behavior Examples](./docs/behavior-examples.md)
Detailed examples of how the AI agent should behave with the MCP knowledge system in various scenarios.

### 🔧 [MCP Protocol & Actions](./docs/mcp-protocol+actions.md)
Complete technical specification of all MCP endpoints, request/response schemas, and API behaviors.

### 🔍 [Knowledge Discovery System](./docs/knowledge-discovery-system.md)
Technical design for PostgreSQL-based search, multi-query decomposition, and context field strategies.

## Core Concept

Without this system, every AI agent session starts from zero. With it, the AI agent:
- Remembers project context through namespace:scope hierarchy
- Learns from failures using collision resolution
- Searches knowledge using multi-query decomposition
- Becomes more effective with each interaction

Knowledge is stored through structured MCP endpoints with:
- Explicit write_knowledge calls with content and searchable context
- Multi-query retrieval for complex tasks
- Task size filtering (XS to XL complexity)
- PostgreSQL full-text search with relevance ranking

Designed for small trusted teams and individual developers.

## Value Proposition

- **For Developers**: No more re-explaining context every session
- **For Teams**: Institutional knowledge preserved and accessible
- **For Projects**: Faster delivery with fewer repeated mistakes

## Project Status

This project includes complete product specification and technical implementation design. The MCP server architecture is defined with PostgreSQL backend, ready for development.
