# FastMCP Examples Analysis

## Project Structures

### ATProto MCP (Bluesky Integration)
```
examples/atproto_mcp/
├── README.md
├── pyproject.toml               # Entry: atproto-mcp = "atproto_mcp.__main__:main"
└── src/
    └── atproto_mcp/
        ├── __init__.py
        ├── __main__.py          # def main(): atproto_mcp.run()
        ├── server.py            # Global FastMCP instance + decorators
        ├── settings.py          # Pydantic settings with .env
        ├── types.py             # Pydantic models for API responses
        └── _atproto/            # Business logic (prefixed with _)
            ├── __init__.py
            ├── _client.py       # Authentication + client setup
            ├── _posts.py        # Post creation logic
            ├── _profile.py      # Profile operations
            ├── _read.py         # Timeline/notifications
            └── _social.py       # Follow/like/repost operations
```

### Smart Home (Modular + Mounting)
```
examples/smart_home/
├── README.md
├── pyproject.toml
├── uv.lock
└── src/
    └── smart_home/
        ├── __init__.py
        ├── __main__.py          # def main(): hub_mcp.run()
        ├── hub.py               # Main FastMCP instance + mounting
        ├── settings.py          # Pydantic settings
        └── lights/              # Service module
            ├── __init__.py
            ├── server.py        # lights_mcp FastMCP instance
            └── hue_utils.py     # Business logic utilities
```

## Key Patterns

### Entry Point Pattern
```python
# __main__.py (Consistent across all examples)
from package.server import mcp_instance

def main():
    mcp_instance.run()

if __name__ == "__main__":
    main()
```

### Global Instance Pattern
```python
# server.py
from fastmcp import FastMCP

# Global instance - imported by other modules
mcp = FastMCP("Server Name")

@mcp.tool
def example_tool(input: str) -> str:
    return business_logic.process(input)
```

### Settings Pattern
```python
# settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env"], extra="ignore")
    
    api_key: str = Field(default=...)
    base_url: str = Field(default="https://api.example.com")
    default_limit: int = Field(default=10)

settings = Settings()  # Global instance
```

### Business Logic Separation
```python
# _business/ or _service/ (prefixed with _ for internal)
# Pure Python functions, no FastMCP decorators

def create_post(text: str, images: list[str] = None) -> PostResult:
    # Database operations
    # API calls  
    # Business logic
    return PostResult(id=post_id, url=post_url)
```

### Tool Decorator Usage
```python
# server.py
from typing import Annotated
from pydantic import Field

@mcp.tool
def post(
    text: Annotated[str, Field(max_length=300, description="Post content")],
    images: Annotated[list[str] | None, Field(max_length=4)] = None,
) -> PostResult:
    """Create a post with optional images."""
    return _business.create_post(text, images)
```

### Resource Pattern
```python
@mcp.resource("atproto://timeline")
def get_timeline() -> TimelineResult:
    """Get the authenticated user's timeline feed."""
    return _business.fetch_timeline(settings.default_limit)
```

## Advanced Patterns

### Service Mounting (Smart Home)
```python
# hub.py - Main server
hub_mcp = FastMCP("Smart Home Hub")

# Mount sub-services
hub_mcp.mount("hue", lights_mcp)    # lights_mcp from lights/server.py
hub_mcp.mount("thermo", thermo_mcp) # Future expansion

@hub_mcp.tool
def hub_status() -> str:
    """Main hub status check."""
    return check_all_services()
```

### Dependencies Declaration
```python
# server.py
mcp = FastMCP(
    "Server Name",
    dependencies=[
        "package@git+https://github.com/user/repo.git#subdirectory=examples/package",
    ],
)
```

## Simple Examples

### Minimal Echo Server
```python
# echo.py
from fastmcp import FastMCP

mcp = FastMCP("Echo Server")

@mcp.tool
def echo(text: str) -> str:
    """Echo the input text"""
    return text

# Run with: fastmcp run echo.py
```

### Configurable Server
```python
# config_server.py
import argparse
from fastmcp import FastMCP

parser = argparse.ArgumentParser()
parser.add_argument("--name", default="ConfigurableServer")
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

mcp = FastMCP(args.name)

@mcp.tool
def get_status() -> dict:
    return {"server_name": args.name, "debug_mode": args.debug}

if __name__ == "__main__":
    mcp.run()
```

## Package Configuration

### pyproject.toml Patterns
```toml
[project]
name = "package-name"
dependencies = [
    "fastmcp>=0.8.0",           # Always latest FastMCP
    "pydantic-settings>=2.0.0", # For settings
    # Business logic dependencies
]

[project.scripts]
package-mcp = "package.__main__:main"  # Standard entry point

[tool.hatch.metadata]
allow-direct-references = true         # For git dependencies
```

## Key Insights

### What Makes FastMCP Projects Work
1. **Single FastMCP Instance**: One global instance per service
2. **Minimal Entry Points**: Just call `mcp.run()`
3. **Clear Separation**: MCP decorators ≠ business logic
4. **Standard Structure**: `__main__.py` + `server.py` + business modules
5. **Pydantic Everything**: Settings, models, validation
6. **No Manual Async**: FastMCP handles all lifecycle management

### Proven File Naming
- `__main__.py`: Entry point (always)
- `server.py`: FastMCP instance + decorators
- `settings.py`: Pydantic settings
- `types.py`: Pydantic models
- `_business/`: Internal business logic (underscore prefix)
- `/service/server.py`: Sub-service FastMCP instances (for mounting)

### Scaling Strategies
- **Single Service**: All tools in one `server.py`
- **Modular Service**: Multiple modules, one main FastMCP instance
- **Microservices**: Multiple FastMCP instances with mounting (smart_home pattern)
