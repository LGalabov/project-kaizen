# Knowledge Protocol v2 - Complete Example Coverage

This document shows how every documented scenario from the Project Kaizen specification can be handled using the v2 protocol operations.

## Project Setup & Hierarchy Management

### Initial Project Registration
**New Scenario: Setting up a project in the knowledge system**

**v2 Protocol Solution:**
```
# Register new project with complete hierarchy
register_project("checkout-api", "webapp-product", ["payments-group", "auth-group"])
→ Returns inheritance chain and validates all scopes exist

# Verify hierarchy is set up correctly
get_project_hierarchy("checkout-api")
→ Shows complete inheritance: checkout-api → [payments-group, auth-group] → webapp-product → general

# Start first session with full context
init_session("checkout-api")
→ Now has access to all inherited knowledge from groups, product, and general tiers
```

### Project Hierarchy Updates
**Scenario: Project moves between teams or changes scope**

**v2 Protocol Solution:**
```
# Project moves from webapp to fintech product line
update_project_hierarchy("checkout-api", new_product="fintech-product")
→ Returns impact analysis showing gained/lost knowledge

# Add project to additional group for shared services
update_project_hierarchy("checkout-api", new_groups=["payments-group", "auth-group", "core-services-group"])
→ Project now inherits from 3 groups instead of 2

# Verify changes
get_project_hierarchy("checkout-api")
→ Shows updated inheritance chain with new knowledge counts
```

## Teaching Session Examples

### Basic Teaching Session
**Original Scenario (behavior-examples.md lines 12-27):**
```
User: "I need to teach you about our coding standards"
User: "We use 4 spaces for indentation, never tabs"
User: "All functions must have docstrings explaining parameters and return values"
User: "Variable names use snake_case, class names use PascalCase"
User: "That's all for now"
```

**v2 Protocol Solution:**
```
# Session start
init_session("checkout-api") 
→ Gets project context, recent work, current status

# Teaching knowledge
teach("checkout-api", "Use 4 spaces for indentation, never tabs")
teach("checkout-api", "All functions must have docstrings explaining parameters and return values")  
teach("checkout-api", "Variable names use snake_case, class names use PascalCase")

# Session end
end_session("checkout-api", "Taught coding standards: indentation, docstrings, naming conventions")
```

### Teaching Session with Research
**Original Scenario (behavior-examples.md lines 31-48):**
```
User: "Research current best practices for React performance optimization"
AI: [Searches and presents findings about React.memo, code splitting, useMemo]
User: "Store the memo and callback patterns as our standards"
```

**v2 Protocol Solution:**
```
# AI conducts research (external to protocol)
# Then stores findings
teach("checkout-api", "Use React.memo for expensive components to prevent unnecessary re-renders")
teach("checkout-api", "Implement code splitting with lazy loading for better performance")
teach("checkout-api", "Use useMemo and useCallback appropriately for optimization")
```

## Spontaneous Knowledge Addition

**Original Scenario (behavior-examples.md lines 52-58):**
```
User: "Great work. Remember that we always hash passwords with bcrypt, cost factor 12"
AI: "I'll remember to always use bcrypt with cost factor 12 for password hashing."
```

**v2 Protocol Solution:**
```
teach("checkout-api", "Always hash passwords with bcrypt, cost factor 12", "group")
# Stores at group level since security applies to all services
```

## Learning from Failure

**Original Scenario (behavior-examples.md lines 64-72):**
```
AI: [Implements data processing that fails due to memory error]
Error: "Out of memory processing large dataset"
AI: "Should I remember: 'Process large datasets in chunks of 10,000 records maximum'?"
User: "Yes, but make it 5,000 for safety"
```

**v2 Protocol Solution:**
```
learn_from_error("checkout-api", 
  "Out of memory processing large dataset", 
  "Process large datasets in chunks of 5,000 records maximum for safety")
```

## Session Initialization & Context Retrieval

**Original Scenario (behavior-examples.md lines 78-89):**
```
User: "Let's continue working on the API"
AI: "I see we're working on the fintech platform API. Last session we completed 
     the user authentication endpoints. Should I continue with transaction history endpoints?"
```

**v2 Protocol Solution:**
```
init_session("checkout-api")
→ Returns complete context including:
  - Project purpose: "fintech platform API"
  - Recent work: "completed user authentication endpoints"  
  - Next planned: "transaction history endpoints"
  - Current status and warnings
```

## Context Switching Between Domains

**Original Scenario (behavior-examples.md lines 94-106):**
```
Morning: "Update the database schema for transactions"
Afternoon: "Now update the mobile API for transactions"
AI: [Switches context, remembers mobile team's requirements and schema changes]
```

**v2 Protocol Solution:**
```
# Morning session
init_session("checkout-api") # Gets database context
ask_knowledge("checkout-api", "database schema guidelines")
# ... work on schema
end_session("checkout-api", "Updated transaction table schema")

# Afternoon session  
init_session("checkout-api") # Gets full context including morning's schema work
ask_knowledge("checkout-api", "mobile API requirements")
# AI gets both database changes and mobile constraints automatically
```

## Cross-Session Continuity

**Original Scenario (behavior-examples.md lines 112-124):**
```
Monday: "Payment errors must always be logged to our audit system"
Friday: AI implements refund webhook with audit logging automatically
```

**v2 Protocol Solution:**
```
# Monday
teach("checkout-api", "Payment errors must always be logged to audit system", "group")

# Friday  
init_session("checkout-api") # Retrieves all stored knowledge including Monday's rule
ask_knowledge("checkout-api", "payment error handling") 
→ Returns audit logging requirement
# AI applies automatically
```

## Knowledge Updates & Corrections

**Original Scenario (behavior-examples.md lines 144-154):**
```
Monday: "Always use 2-space indentation" 
Wednesday: "Actually, use 4-space indentation"
AI: [Uses 4-space indentation without mentioning the old rule]
```

**v2 Protocol Solution:**
```
# Monday
teach("checkout-api", "Always use 2-space indentation")

# Wednesday  
update_knowledge("checkout-api", "Always use 2-space indentation", "Always use 4-space indentation")
# Old rule cleanly replaced
```

## Progress Tracking & Status Awareness

**Original Scenario (behavior-examples.md lines 174-187):**
```
User: "What's our progress on the authentication module?"
AI: Lists completed tasks, in-progress items, and blocked issues
```

**v2 Protocol Solution:**
```
init_session("checkout-api")
→ Automatically includes progress status:
  - Completed: user registration, login endpoints
  - In progress: OAuth integration  
  - Blocked: callback URL issue
```

## Task Continuity & Resumption

**Original Scenario (behavior-examples.md lines 192-205):**
```
Wednesday: [Starts reporting dashboard, gets halfway]
Friday: "Continue with the reporting dashboard"
AI: "Resuming... I'll start with chart components since data queries are complete"
```

**v2 Protocol Solution:**
```
# Wednesday - End with detailed context
end_session("checkout-api", "Started reporting dashboard: completed data queries and basic layout. Next: implement chart components using D3.js. Files: dashboard.py (class created), dashboard.html (layout done)")

# Friday - Resume with continuation context
init_session("checkout-api", "continue_work", 3)
→ Returns detailed session history with:
  - incomplete_tasks: ["chart components", "filter UI"]  
  - exact_stopping_point: "About to implement chart components"
  - relevant_files: ["dashboard.py", "charts.js", "dashboard.html"]
  - code_context: "Dashboard class created, data methods working, need UI components"
  - immediate_next_steps: ["Add D3.js charts", "Implement filters"]

# AI knows exactly where to resume - no additional queries needed
```

## Proactive Warning System

**Original Scenario (behavior-examples.md lines 282-290):**
```
User: "Update the user table schema"
AI: "Before modifying the user table, I should mention:
     - This table has cascade deletes affecting 5 other tables
     - Last schema change required 2-hour maintenance window"
```

**v2 Protocol Solution:**
```
ask_knowledge("checkout-api", "user table modification")
→ Returns warnings:
  - "WARNING: Cascade deletes affect 5 tables"  
  - "LAST TIME: Required 2-hour maintenance window"
# AI presents warnings before proceeding
```

## Group Knowledge Management

**Original Scenario (behavior-examples.md lines 313-330):**
```
In payment-gateway service (part of Payment Services group):
AI applies Payment Services standards AND product-wide conventions automatically
```

**v2 Protocol Solution:**
```
init_session("payment-gateway")
→ Retrieves inheritance hierarchy:
  - payment-gateway (PROJECT) rules
  - Payment Services group rules  
  - Product-wide conventions
  - General best practices

ask_knowledge("payment-gateway", "refund endpoint implementation")
→ Returns merged knowledge from all relevant scopes
```

## Cross-Group Knowledge Promotion

**Original Scenario (behavior-examples.md lines 332-346):**
```
Payment Services: "Always include request_id in logs"
Core Services: "Add request_id to all log entries"  
AI: "Should this become a product-wide standard?"
User: "Yes, make it universal"
```

**v2 Protocol Solution:**
```
# Initial storage in Payment Services
teach("payment-service", "Always include request_id in logs for tracing", "group")

# Later, in Core Services
teach("core-service", "Add request_id to all log entries", "group")

# AI detects pattern and suggests promotion
promote_knowledge("core-service", "Include request_id in logs", "product")
# Promotes to product-wide standard
```

## Long-Term Knowledge Evolution

**Original Scenario (behavior-examples.md lines 352-371):**
```
Month 1: Basic patterns
Month 6: AI automatically applies all accumulated expertise
```

**v2 Protocol Solution:**
```
# Month 6 - New endpoint request
init_session("checkout-api") # Gets 6 months of accumulated knowledge
ask_knowledge("checkout-api", "creating new endpoints")
→ Returns all patterns learned over 6 months:
  - Basic REST patterns (Month 1)
  - Security requirements (Month 2)  
  - Performance optimizations (Month 3)
  - All accumulated expertise automatically applied
```

## Team Onboarding Support

**Original Scenario (behavior-examples.md lines 248-262):**
```
New Developer: "I'm new to the project. How does our deployment process work?"
AI: Provides comprehensive deployment guide from accumulated knowledge
```

**v2 Protocol Solution:**
```
# New team member session
init_session("checkout-api") # System detects new user context
ask_knowledge("checkout-api", "complete deployment process")
→ Returns comprehensive guide synthesized from all stored deployment knowledge:
  - CI/CD requirements
  - Migration procedures  
  - Environment constraints
  - Team coordination protocols
```

## Institutional Memory & Historical Context

**Original Scenario (behavior-examples.md lines 267-275):**
```
User: "Why do we have this weird check for negative transaction amounts?"
AI: Explains historical context from 3 months ago about critical bug
```

**v2 Protocol Solution:**
```
ask_knowledge("checkout-api", "negative transaction amount validation")
→ Returns rule with metaknowledge:
  - Rule: "Validate refunds as negative values"
  - REASON: "Critical bug where refunds processed as positive, causing double charges"
  - INCIDENT_ID: "REF-2024-003"
  - DATE_ADDED: "3 months ago"
```

## Knowledge Deletion & Cleanup

**Original Scenario (project-kaizen-product-specification.md lines 375-381):**
```
When a project ends:
- System identifies generalizable knowledge
- User approves what to preserve  
- Project-specific information removed
```

**v2 Protocol Solution:**
```
# Project cleanup
ask_knowledge("old-project", "generalizable patterns")
→ AI identifies knowledge worth preserving

# Promote valuable patterns
promote_knowledge("old-project", "authentication patterns", "product")
promote_knowledge("old-project", "database optimization", "general")

# Clean up project-specific knowledge
delete_knowledge("old-project", "project-specific configurations")
delete_knowledge("old-project", "temporary workarounds")
```

## Summary

The v2 protocol's 11 operations cleanly handle all documented scenarios:

### **Core Operations:**
1. **`init_session()`** - Complete context retrieval with flexible detail levels
2. **`ask_knowledge()`** - Natural language queries, warnings, institutional memory
3. **`teach()`** - All knowledge storage with scope control
4. **`end_session()`** - Automatic session recording

### **Learning Operations:**
5. **`learn_from_error()`** - Failure learning and prevention  
6. **`update_knowledge()`** - Knowledge corrections and evolution

### **Management Operations:**
7. **`delete_knowledge()`** - Cleanup and knowledge management
8. **`promote_knowledge()`** - Cross-scope knowledge promotion

### **Project Hierarchy Operations:**
9. **`register_project()`** - Initial project setup with hierarchy
10. **`get_project_hierarchy()`** - Hierarchy discovery and validation
11. **`update_project_hierarchy()`** - Hierarchy changes with impact analysis

Every complex scenario from the original specification can be implemented naturally without forcing users to understand technical details of inheritance, categorization, or storage mechanics. The hierarchy operations solve the fundamental question of "how does the system know project scope relationships?"