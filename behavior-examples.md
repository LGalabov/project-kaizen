# Project Kaizen - Behavior Examples

This document provides concrete examples of how the AI agent should behave with the memory system across various scenarios.

*Note: Knowledge enters the system only through three triggers: user teaching sessions (including research tasks), voluntary post-success additions, and approved post-failure proposals. The system is designed for small trusted teams where simplicity matters more than complex security.*

## Knowledge Acquisition Behaviors

### Teaching Session Example

**User initiates teaching:**
```
User: "I need to teach you about our coding standards"
AI agent: "I'm ready to learn about your coding standards."

User: "We use 4 spaces for indentation, never tabs"
AI agent: "Understood - 4 spaces for indentation, never tabs."

User: "All functions must have docstrings explaining parameters and return values"
AI agent: "Got it - all functions require docstrings with parameter and return value documentation."

User: "Variable names use snake_case, class names use PascalCase"
AI agent: "Noted - snake_case for variables, PascalCase for classes."

User: "That's all for now"
AI agent: "I've stored these coding standards and will apply them in all future work on this project."
```

### Teaching Session with Research

**User-initiated research and storage:**
```
User: "Research current best practices for React performance optimization"
AI agent: [Searches and presents findings]
       "I found several key patterns:
        - Use React.memo for expensive components
        - Implement code splitting with lazy loading
        - Use useMemo and useCallback appropriately"

User: "Good, also check for 2024 updates"
AI agent: [Searches for recent updates]
       "Recent 2024 additions include:
        - React Compiler automatic optimizations
        - Server Components for better performance"

User: "Store the memo and callback patterns as our standards"
AI agent: "I'll store these React optimization standards for the project."
```

### Spontaneous Knowledge Addition

**After successful task completion:**
```
AI agent: [Successfully implements user authentication]

User: "Great work. Remember that we always hash passwords with bcrypt, cost factor 12"
AI agent: "I'll remember to always use bcrypt with cost factor 12 for password hashing."
```

### Learning from Failure

**When an error occurs:**
```
AI agent: [Implements data processing that fails due to memory error]
Error: "Out of memory processing large dataset"

AI agent: "I failed because I tried to load the entire dataset into memory at once. 
         Should I remember: 'Process large datasets in chunks of 10,000 records maximum'?"

User: "Yes, but make it 5,000 for safety"
AI agent: "Stored: 'Process large datasets in chunks of 5,000 records maximum'"
```

## Context Retrieval Behaviors

### Session Initialization

**Starting a new session:**
```
User: "Let's continue working on the API"
AI agent: [Retrieves context]
       "I see we're working on the fintech platform API. Last session we completed 
        the user authentication endpoints. The project uses Python/FastAPI with 
        PostgreSQL. Should I continue with the next planned feature - transaction 
        history endpoints?"

User: "Yes, go ahead"
AI agent: [Proceeds with full context awareness]
```

### Context Switching

**Moving between domains:**
```
Morning Session:
User: "Update the database schema for transactions"
AI agent: [Works with PostgreSQL, applies stored naming conventions]

Afternoon Session:
User: "Now update the mobile API for transactions"
AI agent: [Switches context, remembers:
        - Mobile team's 30-second timeout requirement
        - Need for pagination
        - Response size limits
        - The schema changes from morning session]
```

### Cross-Session Continuity

**Days apart:**
```
Monday:
User: "The payment webhook needs better error handling"
AI agent: [Implements improved error handling]
User: "Good, but remember that payment errors must always be logged to our audit system"
AI agent: "I'll remember that payment errors require audit system logging."

Friday:
User: "Add refund webhook handling"
AI agent: [Implements refund webhook with:
        - Idempotency (learned from previous webhook issues)
        - Audit logging for payment-related errors (remembered from Monday)
        - All standard webhook patterns]
```

## Conflict Resolution Behaviors

### Clear Precedence

**Project rule overrides general rule:**
```
General knowledge: "Use REST APIs"
Project knowledge: "Use GraphQL for this project"

User: "Create a new endpoint for user profiles"
AI agent: "I'll create a GraphQL query for user profiles (following project preference for GraphQL over REST)."
```

### Knowledge Updates (Last-Write-Wins)

**Simple overwrite behavior:**
```
Monday:
User: "Always use 2-space indentation"
AI agent: "Stored: 2-space indentation standard."

Wednesday:
User: "Actually, use 4-space indentation"
AI agent: "Updated: Now using 4-space indentation standard."
[Previous 2-space rule is overwritten]

Friday:
AI agent: [Uses 4-space indentation without mentioning the old rule]
```

### When Updates Happen

**Natural correction through usage:**
```
User: "Format all currency as $X.XX"
AI agent: "I'll format currency as $X.XX"
[Later, this causes issues with international currencies]

User: "We need to handle multiple currencies, use ISO codes"
AI agent: "I'll update to use ISO currency codes (EUR 10.50, USD 10.50, etc.)"
[Old rule naturally replaced through practical need]
```

## Progress Tracking Behaviors

### Status Awareness

**Understanding project state:**
```
User: "What's our progress on the authentication module?"
AI agent: "Based on our sessions:
         ✓ User registration endpoint - completed
         ✓ Login endpoint - completed  
         ✓ Password reset - completed yesterday
         ⧖ OAuth integration - in progress (GitHub done, Google pending)
         ○ Two-factor authentication - not started
         
         The GitHub OAuth issue with callback URLs is still open from Wednesday."

User: "Let's finish Google OAuth"
AI agent: [Continues exactly where left off]
```

### Task Continuity

**Resuming interrupted work:**
```
Wednesday:
User: "Start implementing the reporting dashboard"
AI agent: [Begins implementation, gets halfway]
User: "Actually, we need to handle the urgent bug first"
AI agent: "I'll pause the reporting dashboard implementation. I've completed the data 
         aggregation queries and the basic layout. The chart components and filters 
         still need to be implemented."

Friday:
User: "Continue with the reporting dashboard"
AI agent: "Resuming the reporting dashboard. I'll start with the chart components 
         since the data queries and layout are already complete."
```

## Knowledge Evolution Behaviors

### Pattern Refinement

**Improving based on experience:**
```
Week 1:
User: "Always validate email addresses"
AI agent: [Stores basic email validation rule]

Week 3:
[Email validation causes issue with internal addresses]
AI agent: "The email validation rejected internal @company.local addresses. 
         Should I update the rule to: 'Validate email addresses but allow 
         @company.local domain for internal users'?"
User: "Yes"
AI agent: [Updates knowledge with more nuanced rule]
```

### Accumulated Expertise

**Building comprehensive understanding:**
```
Month 1: Learns basic API patterns
Month 2: Adds security requirements  
Month 3: Incorporates performance optimizations

New endpoint request in Month 4:
AI agent: [Automatically includes:
        - Basic REST patterns (Month 1)
        - Authentication and rate limiting (Month 2)
        - Caching and query optimization (Month 3)
        - All accumulated knowledge applied seamlessly]
```

## Team Knowledge Behaviors

### Onboarding Support

**New team member joins:**
```
New Developer: "I'm new to the project. How does our deployment process work?"
AI agent: "Here's our deployment process:

1. All code must pass CI/CD checks (tests, linting, security scan)
2. Migrations run separately before application deployment
3. Deploy to staging first, monitor for 30 minutes
4. Production deployments only Monday-Thursday (never Friday)
5. The payment service must deploy before order service
6. Keep staging pods under 512MB (environment limitation)

Important: Always check the #deploys Slack channel first - if another team is 
          deploying, wait for confirmation before proceeding."

New Developer: "This is incredibly helpful!"
```

### Institutional Memory

**Recalling historical context:**
```
User: "Why do we have this weird check for negative transaction amounts?"
AI agent: "According to stored knowledge from 3 months ago: This check was added 
         after a critical bug where refunds were processed as positive amounts, 
         causing double charges. The fix requires all refunds to be negative 
         values with explicit validation. There's also a note that the mobile 
         team's code depends on this behavior, so it can't be changed without 
         coordinating with them."
```

## Error Prevention Behaviors

### Proactive Warning

**Before making changes:**
```
User: "Update the user table schema"
AI agent: "Before modifying the user table, I should mention:
         - This table has a stored warning about cascade deletes affecting 5 other tables
         - Last schema change required 2-hour maintenance window
         - Mobile app caches user data for 24 hours
         
         Should I proceed with planning the migration accordingly?"
```

### Pattern Application

**Applying learned lessons:**
```
User: "Add a bulk import feature"
AI agent: [Remembering previous bulk operation failure]
        "I'll implement the bulk import with:
         - Chunk processing (5,000 records max per chunk)
         - Progress tracking and resumability
         - Validation before processing
         - Rollback capability
         
         These patterns come from the stored lesson about bulk operations 
         causing memory issues."
```

## Group Knowledge Behaviors

### Working Within a Service Group

**In payment-gateway service (part of Payment Services group):**
```
User: "Implement the refund endpoint"
AI agent: [Accesses knowledge hierarchy:
        - payment-gateway rules
        - Payment Services Group standards
        - Product-wide conventions
        - General best practices]
        
        "I'll implement the refund endpoint following Payment Services standards:
         - Monetary values in integer cents
         - Idempotency with 24-hour keys
         - Audit logging for all transactions
         - Using payment-commons library
         
         Also applying product standards:
         - JWT authentication
         - Standard error responses"
```

### Cross-Group Knowledge Promotion

**Pattern emerges across groups:**
```
In Payment Services:
User: "Always include request_id in logs for tracing"
AI agent: "Stored for Payment Services group."

Two weeks later in Core Services:
User: "Add request_id to all log entries"
AI agent: "I notice both Payment and Core services now require request_id in logs. 
         Should this become a product-wide standard?"
User: "Yes, make it universal"
AI agent: "Promoted to product-wide logging standard."
```

## Long-Term Evolution

### 6-Month Knowledge Growth

**Day 1:**
```
User: "Create a simple REST endpoint"
AI agent: [Basic implementation]
```

**Month 6:**
```
User: "Create a new endpoint for order processing"
AI agent: [Implements with:
        - Standardized error responses (learned week 2)
        - Audit logging (learned week 3)
        - Rate limiting for financial endpoints (learned month 1)
        - Idempotency for critical operations (learned month 2)
        - Performance monitoring hooks (learned month 3)
        - Circuit breaker for external services (learned month 4)
        - Compliance requirements for financial data (learned month 5)
        
        All automatically applied without reminders]
```

## Summary

These examples demonstrate how the Project Kaizen enables:

1. **Natural knowledge accumulation** through teaching and experience
2. **Seamless context switching** across technical domains
3. **Intelligent conflict resolution** when instructions compete
4. **Continuous improvement** through failure analysis
5. **Team knowledge preservation** across personnel changes
6. **Proactive error prevention** using historical lessons
7. **Progressive expertise building** over project lifetime

The key is that the AI agent behaves like an experienced team member who remembers everything, learns from mistakes, and applies accumulated wisdom automatically.