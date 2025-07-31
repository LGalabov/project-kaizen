# Project Kaizen

> Transform AI assistants from forgetful tools into persistent, learning team members

**Kaizen** (改善) - Japanese for "continuous improvement" - captures how AI learns incrementally with each interaction, evolving from a stateless assistant into a knowledgeable collaborator that understands your projects as deeply as you do.

## What It Does

Project Kaizen is an MCP server that gives AI persistent memory across sessions. Instead of re-explaining your project setup, coding standards, and lessons learned every time, AI remembers everything and gets smarter with each interaction.

**Before Kaizen:**
```
Day 1: "Here's our project setup, coding standards, and conventions..."
Day 2: "Here's our project setup, coding standards, and conventions..."
Day 3: AI makes the same mistake from last week
```

**With Kaizen:**
```
Day 1: Explain once, AI stores everything
Day 2: AI remembers, starts productive work immediately  
Day 3: AI prevents previous mistakes, suggests improvements
```

## Key Features

- **🧠 Persistent Memory**: AI retains project context, decisions, and lessons across sessions
- **📚 Organizational Knowledge**: Team knowledge survives member changes
- **🔍 Smart Search**: Multi-query decomposition with full-text search capabilities
- **🏗️ Scope Hierarchy**: Organized knowledge inheritance from global to project-specific
- **⚡ Learning from Failures**: Errors become permanent guardrails with user approval
- **🎯 Task-Aware**: Context filtering by complexity (XS to XL tasks)

## Documentation

- **📋 [Product Specification](./docs/product-specification.md)** - Vision, use cases, and business value
- **📖 [Behavior Examples](./docs/behavior-examples.md)** - Real-world usage scenarios and workflows  
- **🔧 [MCP Protocol & Actions](./docs/mcp-protocol+actions.md)** - Complete technical specification
- **🎯 [Search Optimization Guide](./docs/search-optimization-guide.md)** - Best practices for knowledge creation and AI query formation

## Who It's For

Designed for small trusted teams (2-10 people) and individual developers who want AI that gets smarter over time.

## Vision

Success is when developers forget AI wasn't always on the team - it knows so much project context it feels like a senior team member who's been there from day one.
