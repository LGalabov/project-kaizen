# Project Kaizen - Behavior Examples

This document provides concrete examples of how AI should behave with the MCP knowledge system across various scenarios, from basic knowledge storage to complex real-world workflows.

*Note: Knowledge enters the system through explicit MCP endpoint calls. The system uses namespace:scope hierarchy with full-text search and conflict resolution.*

## Knowledge Storage Behaviors

### Teaching Session Example

**User initiates teaching:**
```
User: "I need to teach you about our coding standards"
AI: "I'm ready to learn about your coding standards."

User: "We use 4 spaces for indentation, never tabs"
AI: [Stores knowledge in frontend-team scope with indentation context]
    "I've stored the indentation standard for the frontend team."

User: "All functions must have docstrings explaining parameters and return values"
AI: [Stores knowledge in frontend-team scope with documentation context]
    "Stored the docstring requirement."

User: "Variable names use snake_case, class names use PascalCase"
AI: [Stores knowledge in frontend-team scope with naming convention context]
    "I've stored the naming conventions and will apply them in all future work."
```

### Research and Knowledge Storage

**User-initiated research and storage:**
```
User: "Research current best practices for frontend performance optimization"
AI: [Searches and presents findings]
    "I found several key patterns:
     - Use memoization for expensive components
     - Implement code splitting with lazy loading
     - Cache callback functions appropriately"

User: "Store the memoization and callback patterns as our standards"
AI: [Stores performance optimization knowledge in frontend-team scope with performance context]
    "I've stored the performance optimization standards for the frontend team."
```

### Post-Success Knowledge Addition

**After successful task completion:**
```
AI: [Successfully implements user authentication]

User: "Remember that we always hash passwords with bcrypt, cost factor 12"
AI: [Stores password security knowledge in backend-team scope with authentication context]
    "I've stored the password hashing standard for the backend team."
```

### Learning from Failure with Conflict Resolution

**When an error occurs and creates conflicting knowledge:**
```
AI: [Implements data processing that fails due to memory error]
Error: "Out of memory processing large dataset"

AI: "I failed because I tried to load the entire dataset into memory. Should I store this lesson?"

User: "Yes, process in chunks of 5,000 records maximum"
AI: [Stores dataset processing knowledge in data-team scope with memory optimization context]

[Later, discovers existing conflicting knowledge]
AI: [Searches for dataset processing knowledge and finds conflict]
    "I found conflicting guidance:
     - New: Process in chunks of 5,000 records
     - Existing: Load full datasets for accuracy
     
     Should I resolve this conflict?"

User: "Yes, the chunking approach is better"
AI: [Resolves conflict by marking chunking approach as active, suppressing full dataset approach]
    "Conflict resolved - chunking approach is now active."
```

## Real-World User Journey Examples

### Initial Project Setup

**Software Architect begins new fintech project:**
```
User: "This is a fintech platform for small business loans"
AI: [Stores project context in acme:default scope]
    "I've stored the fintech project context."

User: "We must comply with SOC2 and PCI standards"  
AI: [Stores compliance requirements in acme:default scope with security context]
    "Stored compliance requirements - SOC2 and PCI standards."

User: "Tech stack is REST API backend with modern frontend framework"
AI: [Stores tech stack in acme:default scope with architecture context]
    "I've stored the REST API and frontend framework architecture."

User: "We use a relational database with strict naming conventions"
AI: [Stores database preferences in acme:default scope with database context]
    "Stored database preference with naming conventions note."
```

### Daily Development Workflow

**Week 1, Monday - Backend Development:**
```
User: "Create the user authentication service"
AI: [Retrieves stored context: REST API architecture, security standards]
    [Implements authentication with compliance requirements]
    "I've implemented the authentication service using our REST API architecture with SOC2/PCI compliance patterns."

[Error occurs: Rate limiting not implemented]
AI: "The implementation failed security review - missing rate limiting. Should I store this lesson?"
User: "Yes, use 5 attempts per minute for auth endpoints"
AI: [Stores rate limiting rule in acme:default scope with authentication context]
    "I've stored the rate limiting requirement for authentication endpoints."
```

**Week 1, Wednesday - Frontend Development:**
```
User: "Create the login form"
AI: [Switches to frontend context, implements form]
    "I've created the login form using our frontend framework."

User: "Always use our custom FormField component for consistency"
AI: [Stores UI component rule in acme:default scope with frontend context]
    "I've stored the FormField component requirement and will use it for all forms."
```

**Week 2, Monday - Returning to Backend:**
```
User: "Add password reset functionality" 
AI: [Retrieves authentication context, automatically includes rate limiting]
    "I've implemented password reset with 5 attempts per minute rate limiting 
     (following the authentication endpoint standard from last week)."
```

### Cross-Domain Context Switching

**Morning - Database Layer:**
```
User: "Add a new table for transaction history"
AI: [Retrieves database naming conventions, creates table with audit columns]
    "I've created the transaction_history table following our database naming conventions."

User: "Include a composite index on user_id and created_at"
AI: [Stores indexing pattern in acme:default scope with database context]
    "Added the composite index and stored this indexing pattern for future tables."
```

**Afternoon - API Layer:**
```
User: "Expose the transaction history endpoint"
AI: [Knows about new table, implements with proper joins and rate limiting]
    "I've implemented the transaction history endpoint with:
     - Proper joins to the new table structure
     - Rate limiting (standard for financial data)
     - Pagination (learned from mobile timeout issues)"
```

**Next Day - Frontend:**
```
User: "Show transaction history in the dashboard"
AI: [Knows API structure, uses stored UI patterns]
    "I've implemented the transaction history view using:
     - The API endpoint created yesterday
     - FormField components (our UI standard)
     - Error handling for rate limits
     - Stored data table patterns"
```

### Learning from Production Failures

**Initial Implementation:**
```
User: "Implement webhook handler for payment notifications"
AI: [Creates basic handler]
    "I've implemented the payment webhook handler."

[Deployed to production - duplicate webhooks cause double-charging]

User: "The handler must be idempotent - we had duplicate payments"
AI: "Should I store this lesson to prevent future webhook issues?"
User: "Yes, using the event ID as idempotency key"
AI: [Stores idempotency pattern in acme:default scope with webhook context]
    "I've stored the webhook idempotency requirement using event IDs."
```

**Future Implementation:**
```
User: "Add shipping notification webhook"
AI: [Automatically implements with idempotency]
    "I've implemented the shipping webhook with idempotency using event IDs
     (learned from the payment webhook double-charging issue)."
```

## Context Retrieval Behaviors

### Session Initialization with Multi-Query

**Starting a new session:**
```
User: "Let's continue working on the API"
AI: [Searches for API development context using multiple targeted queries across scope hierarchy]
    "I see we're working on the fintech platform API. Last session we completed 
     the user authentication endpoints. The project uses REST API architecture with 
     our relational database. Should I continue with the next planned feature - transaction 
     history endpoints?"

User: "Yes, go ahead"
AI: [Proceeds with full context awareness from scope hierarchy]
```

### Context Switching with Scope Changes

**Moving between domains:**
```
Morning Session:
User: "Update the database schema for transactions"
AI: [Retrieves backend-team context and applies stored naming conventions]
    [Works with database using established patterns]

Afternoon Session:
User: "Now update the mobile API for transactions"
AI: [Switches to mobile-team scope, searches for mobile API requirements and transaction context]
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
AI: [Implements improved error handling]
User: "Remember that payment errors must always be logged to our audit system"
AI: [Stores payment error logging requirement in payments-team scope with compliance context]

Friday:
User: "Add refund webhook handling"
AI: [Searches for webhook patterns, payment handling, and refund requirements across scope hierarchy]
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
AI: [Searches for refund patterns, payment standards, and audit requirements across payment service hierarchy]
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
AI: [Stores logging standard in payments:default scope with tracing context]

Two weeks later in Core Services:
User: "Add request_id to all log entries"
AI: [Stores logging standard in core:default scope, then searches for similar patterns]
    "I notice both Payment and Core services now require request_id in logs. 
     Should this become a global standard?"
        
User: "Yes, make it universal"
AI: [Stores universal logging standard in global:default scope]
    "Promoted to global logging standard."
```

## Task Size and Complexity Filtering

### Size-Appropriate Knowledge Retrieval

**Quick fix (XS):**
```
User: "Fix the typo in the error message"
AI: [Searches for quick-fix knowledge using XS task size filter]
    "Fixed the typo using standard error message format."
```

**Large implementation (L):**
```
User: "Implement complete OAuth 2.0 integration with multiple providers"
AI: [Searches for comprehensive OAuth knowledge using L task size filter and multiple focused queries]
    "This is a large implementation. I'll approach it systematically using:
     - OAuth 2.0 architectural patterns
     - Multi-provider configuration strategies
     - Security hardening requirements
     - Integration testing approaches
     - Monitoring and observability patterns"
```

## Advanced Conflict Resolution

### Handling Conflicting Standards

**When scope inheritance creates conflicts:**
```
User: "Use tabs for indentation in this specific service"
AI: [Stores service-specific indentation rule]
       
    [Later, when searching returns conflicting rules]
    "I found conflicting indentation rules:
     - Global standard: 4 spaces for indentation
     - Service-specific: Use tabs for indentation
     
     The service-specific rule takes precedence due to scope hierarchy."
        
[Service rule automatically overrides global due to scope precedence]
```

### Explicit Conflict Resolution

**When same-level conflicts occur:**
```
AI: [Search returns two conflicting entries from same scope]
    "I found conflicting API timeout values in the mobile-team scope:
     - Entry K1: 30-second timeout for API calls
     - Entry K2: 60-second timeout for API calls
     
     Which should be active?"

User: "Use 30 seconds, the 60-second rule is outdated"
AI: [Resolves conflict by marking 30-second rule as active, suppressing 60-second rule]
    "Conflict resolved - 30-second timeout is now active, 60-second rule suppressed."
```

## Knowledge Search Validation Examples

### Test Knowledge Entries
1. "Always use HTTPS for external API calls to prevent data interception"
2. "Google OAuth 2.0 setup: client registration, redirect URIs, scope configuration"  
3. "OAuth with PKCE for mobile apps: security best practices and implementation"
4. "Git commit message conventions: semantic versioning and clear descriptions"
5. "Git push safety: force push alternatives, branch protection, team workflows"
6. "Java code formatting: Checkstyle rules, indentation, naming conventions"
7. "Mobile Google Sign-In: SDK integration, credential handling"
8. "JWT token authentication for database access and session management"
9. "API rate limiting: throttling strategies, Redis implementation, error responses"
10. "Mobile app security: certificate pinning, keychain storage, biometric auth"

### AI Query Validation Results

| AI Query | Expected Returns | Reasoning |
|----------|------------------|-----------|
| "implement Google OAuth for mobile app" | K2, K3, K7, K10 | Matches "google oauth", "oauth mobile", "mobile auth" |
| "commit and push code safely" (decomposed) | K4, K5 | Separate queries for commit and push |
| "Java code formatting rules" | K6 | Exact match "java formatting" |
| "secure API communication" | K1, K9 | Matches "API security", "HTTPS", "rate limiting" |
| "mobile authentication best practices" | K3, K7, K10 | Matches "mobile auth", "security practices" |

## Summary

These examples demonstrate how Project Kaizen enables:

1. **Explicit knowledge management** through MCP endpoint calls
2. **Multi-query context retrieval** for complex task understanding
3. **Scope hierarchy inheritance** for organized knowledge access
4. **Task size filtering** for appropriate knowledge complexity
5. **Conflict resolution** for conflicting information
6. **Context field strategy** for effective searchability
7. **Full-text search** with relevance ranking

The key is that AI uses structured MCP protocols while maintaining natural conversational flow, creating a robust knowledge management system that scales with team and project complexity.
