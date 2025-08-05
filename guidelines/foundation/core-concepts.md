# FastMCP Core Concepts

## Purpose and Vision
FastMCP is a Python framework for building Model Context Protocol (MCP) servers and clients, described as "the USB-C port for AI" - providing a standardized way to connect LLMs to resources.

## Key Components

### Resources
- Expose data through standardized interfaces
- Provide structured access to information sources

### Tools
- Provide functionality via executable functions
- Enable LLMs to perform actions and computations

### Prompts
- Define interaction patterns with reusable message templates
- Structure communication between LLMs and services

## Core Features
- Authentication support
- Comprehensive logging
- Progress tracking capabilities
- High-level, Pythonic interface
- Minimal boilerplate code
- Production-ready infrastructure patterns

## Basic Implementation Pattern
```python
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

## Design Philosophy
- **Fast**: Quick development cycles
- **Simple**: Minimal setup requirements
- **Pythonic**: Natural Python idioms and patterns
- **Complete**: Full-featured platform with comprehensive ecosystem

## Key Integrations
- Anthropic API
- ChatGPT
- OpenAI
- Claude
- FastAPI
- OAuth providers

## Standards for AI Development
- Use type annotations for automatic schema generation
- Implement proper error handling with standard Python exceptions
- Follow async patterns for scalable operations
- Leverage decorators for clean component registration