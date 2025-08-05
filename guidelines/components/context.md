# FastMCP Context Management Guidelines

## Context Overview

Context provides tools with access to advanced server capabilities including logging, progress reporting, resource access, LLM sampling, user interaction, and state management.

## Context Access Patterns

### 1. Dependency Injection (Recommended)
```python
from fastmcp import Context

@mcp.tool
async def process_file(file_uri: str, ctx: Context) -> str:
    """Process a file with progress tracking."""
    await ctx.info(f"Starting to process {file_uri}")
    
    # Processing logic here
    await ctx.info("Processing complete")
    return "File processed successfully"
```

### 2. Global Context Function
```python
from fastmcp import get_context

@mcp.tool
async def analyze_data(data: list[float]) -> dict:
    """Analyze data with contextual logging."""
    ctx = get_context()
    await ctx.info(f"Analyzing {len(data)} data points")
    
    # Analysis logic
    result = {"average": sum(data) / len(data)}
    await ctx.info(f"Analysis complete: average = {result['average']}")
    return result
```

## Core Context Capabilities

### Logging Functions
```python
@mcp.tool
async def complex_operation(data: str, ctx: Context) -> str:
    """Perform complex operation with comprehensive logging."""
    await ctx.debug("Starting complex operation")
    await ctx.info("Processing input data")
    
    try:
        # Processing logic
        result = process_data(data)
        await ctx.info("Operation completed successfully")
        return result
    except Exception as e:
        await ctx.error(f"Operation failed: {str(e)}")
        raise
```

### Progress Reporting
```python
@mcp.tool
async def long_running_task(items: list, ctx: Context) -> dict:
    """Process items with progress tracking."""
    total = len(items)
    processed = 0
    
    for item in items:
        # Report progress
        progress = (processed / total) * 100
        await ctx.progress(f"Processing item {processed + 1}/{total}", progress)
        
        # Process item
        process_item(item)
        processed += 1
    
    await ctx.info("All items processed")
    return {"processed_count": processed}
```

### Resource Access
```python
@mcp.tool
async def use_server_resource(resource_uri: str, ctx: Context) -> str:
    """Access and process server resource."""
    try:
        resource_content = await ctx.read_resource(resource_uri)
        await ctx.info(f"Retrieved resource: {resource_uri}")
        return f"Processed: {resource_content}"
    except Exception as e:
        await ctx.error(f"Failed to access resource {resource_uri}: {e}")
        raise
```

### LLM Sampling (Text Generation)
```python
@mcp.tool
async def generate_summary(text: str, ctx: Context) -> str:
    """Generate summary using client's LLM."""
    prompt = f"Please summarize the following text:\n\n{text}"
    
    try:
        summary = await ctx.sample_llm(prompt, max_tokens=100)
        await ctx.info("Summary generated successfully")
        return summary
    except Exception as e:
        await ctx.error(f"Failed to generate summary: {e}")
        raise
```

### User Interaction
```python
@mcp.tool
async def interactive_configuration(ctx: Context) -> dict:
    """Get configuration from user interaction."""
    try:
        # Request structured input from user
        config = await ctx.request_user_input(
            "Please provide configuration",
            schema={
                "type": "object",
                "properties": {
                    "threshold": {"type": "number"},
                    "mode": {"type": "string", "enum": ["fast", "thorough"]}
                }
            }
        )
        await ctx.info(f"Received configuration: {config}")
        return config
    except Exception as e:
        await ctx.error(f"Failed to get user input: {e}")
        raise
```

## State Management Patterns

### Shared State Across Tools
```python
@mcp.tool
async def initialize_session(session_id: str, ctx: Context) -> str:
    """Initialize a processing session."""
    # Store session data in context state
    await ctx.set_state(f"session_{session_id}", {
        "started_at": time.time(),
        "status": "active"
    })
    
    await ctx.info(f"Session {session_id} initialized")
    return f"Session {session_id} ready"

@mcp.tool
async def get_session_status(session_id: str, ctx: Context) -> dict:
    """Get session status from shared state."""
    session_data = await ctx.get_state(f"session_{session_id}")
    if not session_data:
        await ctx.warning(f"Session {session_id} not found")
        return {"status": "not_found"}
    
    return session_data
```

### Cross-Tool Communication
```python
@mcp.tool
async def store_analysis_result(data: dict, ctx: Context) -> str:
    """Store analysis result for other tools."""
    result_id = generate_unique_id()
    await ctx.set_state(f"analysis_{result_id}", data)
    await ctx.info(f"Analysis result stored with ID: {result_id}")
    return result_id

@mcp.tool
async def retrieve_analysis_result(result_id: str, ctx: Context) -> dict:
    """Retrieve previously stored analysis result."""
    result = await ctx.get_state(f"analysis_{result_id}")
    if not result:
        raise ToolError(f"Analysis result {result_id} not found")
    
    await ctx.info(f"Retrieved analysis result: {result_id}")
    return result
```

## Context Integration Patterns

### Middleware Integration
```python
@mcp.tool
async def authenticated_operation(data: str, ctx: Context) -> str:
    """Operation that requires authentication context."""
    # Access authentication info from context
    user_info = await ctx.get_state("current_user")
    if not user_info:
        await ctx.warning("Unauthenticated request")
        raise ToolError("Authentication required")
    
    await ctx.info(f"Processing request for user: {user_info['username']}")
    return process_authenticated_data(data, user_info)
```

### Resource and Context Coordination
```python
@mcp.resource("data://processed")
async def get_processed_data(ctx: Context) -> str:
    """Resource that uses context for dynamic content."""
    processing_status = await ctx.get_state("processing_status")
    await ctx.debug(f"Resource accessed, status: {processing_status}")
    
    if processing_status == "complete":
        return "Processed data available"
    else:
        return "Processing in progress"
```

## Standards for AI Context Usage

### Context Parameter Guidelines
- Make context parameter optional when possible
- Use type hints: `ctx: Context` for dependency injection
- Handle context unavailability gracefully
- Don't expose context operations to LLM interfaces

### Logging Best Practices
- Use appropriate log levels (debug, info, warning, error)
- Provide meaningful, actionable log messages
- Include relevant context in log messages
- Avoid logging sensitive information

### State Management Guidelines
- Use descriptive keys for state storage
- Implement proper cleanup of temporary state
- Handle state not found scenarios gracefully
- Consider state persistence requirements

### Error Handling with Context
- Log errors before raising exceptions
- Provide context-aware error messages
- Use structured logging for complex errors
- Implement proper error recovery mechanisms

### Performance Considerations
- Minimize context operations in tight loops
- Cache frequently accessed context data
- Use async patterns for all context operations
- Monitor context operation performance