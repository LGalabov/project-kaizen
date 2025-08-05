# FastMCP Logging Guidelines

## Logging Overview

FastMCP provides server-to-client logging capabilities that send log messages directly from server functions to MCP clients. This enables real-time visibility into function execution, debugging, progress tracking, and error reporting.

## Log Levels and Usage

### Debug Level
Use for detailed diagnostic information during development and troubleshooting.

```python
@mcp.tool
async def complex_analysis(data: list, ctx: Context) -> dict:
    """Perform complex data analysis."""
    await ctx.debug(f"Starting analysis with {len(data)} data points")
    await ctx.debug(f"Analysis parameters: {get_analysis_config()}")
    
    # Detailed execution logging
    for step in analysis_steps:
        await ctx.debug(f"Executing step: {step}")
    
    return analysis_result
```

### Info Level
Use for general execution information and important milestones.

```python
@mcp.tool
async def process_documents(documents: list[str], ctx: Context) -> dict:
    """Process multiple documents."""
    await ctx.info(f"Processing {len(documents)} documents")
    
    processed = 0
    for doc in documents:
        result = process_document(doc)
        processed += 1
        await ctx.info(f"Processed document {processed}/{len(documents)}")
    
    await ctx.info("All documents processed successfully")
    return {"processed_count": processed}
```

### Warning Level
Use for potential issues that don't prevent execution but require attention.

```python
@mcp.tool
async def validate_data(data: dict, ctx: Context) -> dict:
    """Validate input data with warnings."""
    validation_result = {"valid": True, "warnings": []}
    
    if len(data) > 1000:
        await ctx.warning("Large dataset detected, processing may be slow")
        validation_result["warnings"].append("large_dataset")
    
    if "timestamp" not in data:
        await ctx.warning("Timestamp field missing, using current time")
        validation_result["warnings"].append("missing_timestamp")
    
    return validation_result
```

### Error Level
Use for problems that might allow continued operation but indicate significant issues.

```python
@mcp.tool
async def robust_operation(data: str, ctx: Context) -> str:
    """Perform operation with error recovery."""
    try:
        return primary_processing(data)
    except ProcessingError as e:
        await ctx.error(f"Primary processing failed: {str(e)}")
        await ctx.info("Attempting fallback processing")
        
        try:
            return fallback_processing(data)
        except Exception as fallback_error:
            await ctx.error(f"Fallback processing also failed: {str(fallback_error)}")
            raise ToolError("All processing methods failed")
```

## Structured Logging Patterns

### Basic Structured Logging
```python
@mcp.tool
async def track_performance(operation: str, ctx: Context) -> dict:
    """Track operation performance with structured logs."""
    start_time = time.time()
    
    # Log with structured data
    await ctx.info(
        "Operation started",
        extra={
            "operation": operation,
            "start_time": start_time,
            "user_id": get_current_user_id()
        }
    )
    
    result = perform_operation(operation)
    
    duration = time.time() - start_time
    await ctx.info(
        "Operation completed",
        extra={
            "operation": operation,
            "duration": duration,
            "result_size": len(str(result))
        }
    )
    
    return result
```

### Error Context Logging
```python
@mcp.tool
async def error_prone_operation(data: dict, ctx: Context) -> dict:
    """Operation with comprehensive error logging."""
    try:
        await ctx.debug("Validating input data")
        validate_input(data)
        
        await ctx.info("Starting processing")
        result = process_data(data)
        
        return result
    except ValidationError as e:
        await ctx.error(
            "Input validation failed",
            extra={
                "error_type": "validation",
                "invalid_fields": e.fields,
                "input_size": len(data)
            }
        )
        raise ToolError(f"Invalid input: {e}")
    except ProcessingError as e:
        await ctx.error(
            "Processing failed",
            extra={
                "error_type": "processing",
                "stage": e.stage,
                "data_type": type(data).__name__
            }
        )
        raise ToolError(f"Processing error: {e}")
```

## Progress Tracking with Logging

### Long-Running Operations
```python
@mcp.tool
async def batch_process(items: list, ctx: Context) -> dict:
    """Process items with progress logging."""
    total_items = len(items)
    await ctx.info(f"Starting batch processing of {total_items} items")
    
    processed = 0
    failed = 0
    
    for i, item in enumerate(items):
        try:
            process_item(item)
            processed += 1
            
            # Progress logging every 10% or every 100 items
            if (i + 1) % max(1, total_items // 10) == 0 or (i + 1) % 100 == 0:
                await ctx.info(
                    f"Progress: {i + 1}/{total_items} ({((i + 1)/total_items)*100:.1f}%)",
                    extra={
                        "processed": processed,
                        "failed": failed,
                        "completion_percent": ((i + 1) / total_items) * 100
                    }
                )
        except Exception as e:
            failed += 1
            await ctx.warning(f"Failed to process item {i + 1}: {str(e)}")
    
    await ctx.info(
        "Batch processing completed",
        extra={
            "total_items": total_items,
            "processed": processed,
            "failed": failed,
            "success_rate": (processed / total_items) * 100
        }
    )
    
    return {
        "processed": processed,
        "failed": failed,
        "total": total_items
    }
```

## Client-Specific Logging Considerations

### Development vs Production Logging
```python
import os

@mcp.tool
async def environment_aware_logging(data: str, ctx: Context) -> str:
    """Adjust logging based on environment."""
    is_development = os.getenv("ENVIRONMENT") == "development"
    
    if is_development:
        await ctx.debug(f"Development mode: processing data of length {len(data)}")
        await ctx.debug(f"Data preview: {data[:100]}...")
    
    await ctx.info("Processing started")
    result = process_data(data)
    
    if is_development:
        await ctx.debug(f"Result preview: {str(result)[:100]}...")
    
    await ctx.info("Processing completed")
    return result
```

### Conditional Logging
```python
@mcp.tool
async def conditional_logging(data: dict, verbose: bool = False, ctx: Context) -> dict:
    """Provide different logging levels based on parameters."""
    if verbose:
        await ctx.info("Verbose mode enabled")
        await ctx.debug(f"Input data keys: {list(data.keys())}")
    
    await ctx.info("Starting operation")
    
    for key, value in data.items():
        if verbose:
            await ctx.debug(f"Processing key: {key}")
        
        processed_value = process_value(value)
        
        if verbose:
            await ctx.debug(f"Key {key} processed successfully")
    
    await ctx.info("Operation completed")
    return {"status": "completed", "processed_keys": len(data)}
```

## Standards for AI Logging

### Log Message Guidelines
- Use clear, descriptive messages that explain what's happening
- Include relevant context and parameters in log messages
- Avoid logging sensitive information (passwords, API keys, personal data)
- Use consistent formatting and terminology across tools

### Performance Logging
```python
@mcp.tool
async def performance_monitored_operation(data: list, ctx: Context) -> dict:
    """Operation with performance monitoring."""
    start_time = time.time()
    memory_start = get_memory_usage()
    
    await ctx.info(
        "Operation started",
        extra={
            "data_size": len(data),
            "start_memory_mb": memory_start
        }
    )
    
    result = expensive_operation(data)
    
    duration = time.time() - start_time
    memory_end = get_memory_usage()
    
    await ctx.info(
        "Operation completed",
        extra={
            "duration_seconds": duration,
            "memory_delta_mb": memory_end - memory_start,
            "result_count": len(result)
        }
    )
    
    return result
```

### Security and Privacy
- Never log passwords, API keys, or other secrets
- Sanitize user input before logging
- Consider data privacy regulations when logging user data
- Use log levels appropriately to avoid exposing sensitive information

### Best Practices for AI Development
- Log at appropriate levels to provide useful debugging information
- Use structured logging for complex operations
- Implement consistent logging patterns across all tools
- Consider the client's logging capabilities and preferences
- Monitor log volume to avoid overwhelming clients