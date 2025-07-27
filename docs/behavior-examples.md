# Project Kaizen - Behavior Examples

This document provides concrete examples of how the AI agent should behave with the MCP knowledge system across various scenarios.

*Note: Knowledge enters the system through explicit MCP endpoint calls. The system uses namespace:scope hierarchy with PostgreSQL full-text search and collision resolution.*

## Knowledge Storage Behaviors

### Teaching Session Example

**User initiates teaching:**
```
User: "I need to teach you about our coding standards"
AI agent: "I'm ready to learn about your coding standards."

User: "We use 4 spaces for indentation, never tabs"
AI agent: [Stores knowledge in frontend-team scope with indentation context]
       "I've stored the indentation standard for the frontend team."

User: "All functions must have docstrings explaining parameters and return values"
AI agent: [Stores knowledge in frontend-team scope with documentation context]
       "Stored the docstring requirement."

User: "Variable names use snake_case, class names use PascalCase"
AI agent: [Stores knowledge in frontend-team scope with naming convention context]
       "I've stored the naming conventions and will apply them in all future work."
```

### Research and Knowledge Storage

**User-initiated research and storage:**
```
User: "Research current best practices for React performance optimization"
AI agent: [Searches and presents findings]
       "I found several key patterns:
        - Use React.memo for expensive components
        - Implement code splitting with lazy loading
        - Use useMemo and useCallback appropriately"

User: "Store the memo and callback patterns as our standards"
AI agent: [Stores React optimization knowledge in frontend-team scope with performance context]
       "I've stored the React optimization standards for the frontend team."
```

### Post-Success Knowledge Addition

**After successful task completion:**
```
AI agent: [Successfully implements user authentication]

User: "Remember that we always hash passwords with bcrypt, cost factor 12"
AI agent: [Stores password security knowledge in backend-team scope with authentication context]
       "I've stored the password hashing standard for the backend team."
```

### Learning from Failure with Collision Resolution

**When an error occurs and creates conflicting knowledge:**
```
AI agent: [Implements data processing that fails due to memory error]
Error: "Out of memory processing large dataset"

AI agent: "I failed because I tried to load the entire dataset into memory. Should I store this lesson?"

User: "Yes, process in chunks of 5,000 records maximum"
AI agent: [Stores dataset processing knowledge in data-team scope with memory optimization context]

[Later, discovers existing conflicting knowledge]
AI agent: [Searches for dataset processing knowledge and finds conflict]
       "I found conflicting guidance:
        - New: Process in chunks of 5,000 records
        - Existing: Load full datasets for accuracy
        
        Should I resolve this collision?"

User: "Yes, the chunking approach is better"
AI agent: [Resolves collision by marking chunking approach as active, suppressing full dataset approach]
       "Collision resolved - chunking approach is now active."
```

## Context Retrieval Behaviors

### Session Initialization with Multi-Query

**Starting a new session:**
```
User: "Let's continue working on the API"
AI agent: [Searches for API development context using multiple targeted queries across scope hierarchy]
       "I see we're working on the fintech platform API. Last session we completed 
        the user authentication endpoints. The project uses Python/FastAPI with 
        PostgreSQL. Should I continue with the next planned feature - transaction 
        history endpoints?"

User: "Yes, go ahead"
AI agent: [Proceeds with full context awareness from scope hierarchy]
```

### Context Switching with Scope Changes

**Moving between domains:**
```
Morning Session:
User: "Update the database schema for transactions"
AI agent: [Retrieves backend-team context and applies stored naming conventions]
       [Works with PostgreSQL using established patterns]

Afternoon Session:
User: "Now update the mobile API for transactions"
AI agent: [Switches to mobile-team scope, searches for mobile API requirements and transaction context]
       "Switching to mobile context. I'll implement the transaction API with:
        - 30-second timeout requirement (mobile team standard)
        - Pagination for large result sets
        - Response size limits for mobile bandwidth
        - The schema changes from this morning's backend work"
```

### Cross-Session Continuity with Knowledge Inheritance

**Days apart with scope hierarchy:**
```
Monday:
User: "The payment webhook needs better error handling"
AI agent: [Implements improved error handling]
User: "Remember that payment errors must always be logged to our audit system"
AI agent: [Stores payment error logging requirement in payments-team scope with compliance context]

Friday:
User: "Add refund webhook handling"
AI agent: [Searches for webhook patterns, payment handling, and refund requirements across scope hierarchy]
       "I'll implement refund webhook with:
        - Idempotency patterns (from global webhook standards)
        - Audit logging for payment errors (from Monday's payments-team rule)
        - Standard error handling patterns (inherited from default scope)"
```

## Namespace and Scope Management

### Working Within Service Groups

**In payment-gateway service (part of Payment Services group):**
```
User: "Implement the refund endpoint"
AI agent: [Searches for refund patterns, payment standards, and audit requirements across payment service hierarchy]
       "I'll implement the refund endpoint following the scope hierarchy:
        
        From payments:payment-gateway:
        - Use payment-commons library
        - Specific gateway timeout settings
        
        From payments:default:
        - Monetary values in integer cents
        - Idempotency with 24-hour keys
        - Audit logging for all transactions
        
        From global:default:
        - JWT authentication
        - Standard error responses"
```

### Knowledge Promotion Across Scopes

**Pattern emerges across teams:**
```
In Payment Services:
User: "Always include request_id in logs for tracing"
AI agent: [Stores logging standard in payments:default scope with tracing context]

Two weeks later in Core Services:
User: "Add request_id to all log entries"
AI agent: [Stores logging standard in core:default scope, then searches for similar patterns]
       "I notice both Payment and Core services now require request_id in logs. 
        Should this become a global standard?"
        
User: "Yes, make it universal"
AI agent: [Stores universal logging standard in global:default scope]
       "Promoted to global logging standard."
```

## Task Size and Complexity Filtering

### Size-Appropriate Knowledge Retrieval

**Quick fix (XS):**
```
User: "Fix the typo in the error message"
AI agent: [Searches for quick-fix knowledge using XS task size filter]
       "Fixed the typo using standard error message format."
```

**Large implementation (L):**
```
User: "Implement complete OAuth 2.0 integration with multiple providers"
AI agent: [Searches for comprehensive OAuth knowledge using L task size filter and multiple focused queries]
       "This is a large implementation. I'll approach it systematically using:
        - OAuth 2.0 architectural patterns
        - Multi-provider configuration strategies
        - Security hardening requirements
        - Integration testing approaches
        - Monitoring and observability patterns"
```

## Advanced Collision Resolution

### Handling Conflicting Standards

**When scope inheritance creates conflicts:**
```
User: "Use tabs for indentation in this specific service"
AI agent: [Stores service-specific indentation rule]
       
       [Later, when searching returns conflicting rules]
       "I found conflicting indentation rules:
        - Global standard: 4 spaces for indentation
        - Service-specific: Use tabs for indentation
        
        The service-specific rule takes precedence due to scope hierarchy."
        
[Service rule automatically overrides global due to scope precedence]
```

### Explicit Collision Resolution

**When same-level conflicts occur:**
```
AI agent: [Search returns two conflicting entries from same scope]
       "I found conflicting API timeout values in the mobile-team scope:
        - Entry K1: 30-second timeout for API calls
        - Entry K2: 60-second timeout for API calls
        
        Which should be active?"

User: "Use 30 seconds, the 60-second rule is outdated"
AI agent: [Resolves collision by marking 30-second rule as active, suppressing 60-second rule]
       "Collision resolved - 30-second timeout is now active, 60-second rule suppressed."
```

## Summary

These examples demonstrate how Project Kaizen enables:

1. **Explicit knowledge management** through MCP endpoint calls
2. **Multi-query context retrieval** for complex task understanding
3. **Scope hierarchy inheritance** for organized knowledge access
4. **Task size filtering** for appropriate knowledge complexity
5. **Collision resolution** for conflicting information
6. **Context field strategy** for effective searchability
7. **PostgreSQL full-text search** with relevance ranking

The key is that the AI agent uses structured MCP protocols while maintaining natural conversational flow, creating a robust knowledge management system that scales with team and project complexity.
