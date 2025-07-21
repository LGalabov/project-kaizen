# Project Kaizen - Knowledge Protocol v2 Specification

## Protocol Integration Instructions

### CLAUDE.md Integration
Add the following sections to `CLAUDE.md`:

```markdown
## Knowledge Protocol v2 Behavior

### Session Initialization
At session start, call:
- init_session(project_id) - Gets complete context in one call

### Task Preparation  
Before any task:
- ask_knowledge(project_id, task_description) - Natural language query for relevant knowledge

### Knowledge Storage
- teach(project_id, knowledge_text) - Store any knowledge naturally
- learn_from_error(project_id, error_description, proposed_solution) - Capture failure lessons

### Session End
- end_session(project_id, work_summary) - Record session automatically
```

### MCP Server Implementation
The MCP server must implement all operations defined in this protocol with exact signatures and return formats.

## Protocol Operations Overview

### Core Operations (Most Used)
```
init_session(project_id: str) -> SessionContext
ask_knowledge(project_id: str, query: str) -> KnowledgeResponse
teach(project_id: str, knowledge: str, context?: str) -> TeachResult
end_session(project_id: str, summary: str) -> Success
```

### Learning Operations
```
learn_from_error(project_id: str, error_description: str, solution: str) -> LearnResult
update_knowledge(project_id: str, old_knowledge: str, new_knowledge: str) -> UpdateResult
```

### Management Operations
```
delete_knowledge(project_id: str, knowledge_pattern: str) -> DeleteResult
promote_knowledge(project_id: str, knowledge_pattern: str, to_scope: str) -> PromoteResult
```

### Project Hierarchy Operations
```
register_project(project_id: str, product_id?: str, group_ids?: List[str]) -> RegistrationResult
get_project_hierarchy(project_id: str) -> HierarchyInfo
update_project_hierarchy(project_id: str, new_product?: str, new_groups?: List[str]) -> UpdateResult
```

### Advanced Operations
```
get_project_knowledge(project_id: str, domain?: str) -> ProjectKnowledge
promote_knowledge(from_scope: str, to_scope: str, knowledge_id: str) -> PromoteResult
get_inheritance_chain(project_id: str) -> InheritanceInfo
```

### Simple Examples
```
// Start session with complete context
init_session("checkout-api") → {project_context, recent_sessions, current_progress, warnings}

// Continue previous work with detailed history
init_session("checkout-api", "continue_work", 5) → {detailed_session_history, incomplete_tasks, context}

// Quick status check
init_session("checkout-api", "status_only") → {current_progress, blocked_items, minimal_context}

// Natural knowledge query
ask_knowledge("checkout-api", "git commit rules") → {relevant_knowledge, warnings, suggestions}

// Store knowledge naturally
teach("checkout-api", "Always use 4 spaces for indentation, never tabs")

// Store at specific scope
teach("checkout-api", "Include request_id in all logs", "group")

// Learn from mistakes
learn_from_error("checkout-api", "Memory error processing dataset", "Process in chunks of 5000 records")

// Delete outdated knowledge
delete_knowledge("checkout-api", "2 spaces for indentation")
```

## Detailed Operation Specifications

### Core Operations

#### init_session
**Request:**
```
init_session(project_id: str, context_scope?: str, history_limit?: int) -> SessionContext
```

**Context Scope Options:**
- `"full"` (default) - Complete project context with 3 recent sessions
- `"continue_work"` - Detailed session history for task resumption
- `"status_only"` - Current progress and blockers only
- `"quick_start"` - Minimal context for simple tasks

**Returns (context_scope="full"):**
```json
{
  "project": {
    "id": "checkout-api",
    "purpose": "fintech platform API",
    "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
    "current_phase": "MVP development"
  },
  "recent_work": [
    {"date": "2024-01-15", "summary": "Completed auth endpoints", "next": "password reset"},
    {"date": "2024-01-14", "summary": "Database schema setup", "tasks": ["user table", "migrations"]}
  ],
  "current_status": {
    "in_progress": ["OAuth integration"],
    "blocked": ["callback URL issue"],
    "next_priorities": ["password reset", "user management"]
  },
  "warnings": [
    {"type": "database", "message": "User table changes require 2h maintenance"}
  ],
  "inheritance_info": {
    "scopes": ["checkout-api", "payments-group", "webapp-product", "general"],
    "active_groups": ["payments-group", "auth-group"]
  }
}
```

**Returns (context_scope="continue_work", history_limit=5):**
```json
{
  "project": {"id": "checkout-api", "purpose": "fintech platform API"},
  "session_history": [
    {
      "date": "2024-01-15",
      "duration_minutes": 45,
      "summary": "Started reporting dashboard implementation",
      "completed_tasks": ["data aggregation queries", "basic layout"],
      "incomplete_tasks": ["chart components", "filter UI"],
      "next_steps": "Implement chart components using D3.js",
      "context_notes": "Dashboard needs real-time updates, mobile responsive",
      "files_modified": ["dashboard.py", "templates/dashboard.html"],
      "dependencies": {"ready": ["data queries"], "blocked": []}
    },
    {
      "date": "2024-01-14",
      "summary": "OAuth integration progress",
      "completed_tasks": ["GitHub OAuth working"],
      "blocked_tasks": ["Google OAuth callback URL issue"],
      "blocker_details": "Waiting for DevOps to configure callback URLs"
    }
  ],
  "continuation_context": {
    "last_active_task": "reporting dashboard",
    "exact_stopping_point": "About to implement chart components",
    "relevant_files": ["dashboard.py", "charts.js", "dashboard.html"],
    "code_context": "Dashboard class created, data methods working, need UI components",
    "immediate_next_steps": ["Add D3.js charts", "Implement filters", "Test responsiveness"]
  }
}
```

**Returns (context_scope="status_only"):**
```json
{
  "project": {"id": "checkout-api", "current_phase": "MVP development"},
  "status_summary": {
    "overall_progress": "40% complete",
    "completed_this_week": 3,
    "in_progress": ["OAuth integration", "reporting dashboard"],
    "blocked": ["callback URL issue"],
    "urgent_items": ["password reset endpoint"],
    "health": "mostly_healthy"
  },
  "quick_warnings": ["Database maintenance required soon"]
}
```

**Notes:**
- Context scope determines response detail level and performance
- `"continue_work"` provides exact task resumption context with file-level details  
- `"status_only"` gives quick project health check for efficiency
- Flexible history limits (1-20) for different continuation needs
- Eliminates need for separate overview/history/progress calls
- Includes proactive warnings for immediate visibility

#### ask_knowledge
**Request:**
```
ask_knowledge(project_id: str, query: str) -> KnowledgeResponse
```

**Examples:**
```
ask_knowledge("checkout-api", "git commit rules")
ask_knowledge("checkout-api", "how to handle database migrations")
ask_knowledge("checkout-api", "payment processing guidelines")
```

**Returns:**
```json
{
  "query": "git commit rules",
  "relevant_knowledge": [
    {
      "rule": "Include JIRA ticket in commit message",
      "source": "PROJECT",
      "reason": "Required for audit compliance",
      "example": "CHECKOUT-123: Add user authentication"
    },
    {
      "rule": "Always push to feature branch first",
      "source": "PRODUCT",
      "reason": "Prevents direct main branch issues"
    }
  ],
  "warnings": [
    "LAST TIME: Direct commits to main caused production issue"
  ],
  "suggestions": [
    "Consider using conventional commit format for consistency"
  ],
  "related_topics": ["git workflows", "code review process"]
}
```

**Notes:**
- Natural language queries eliminate category/keyword complexity
- AI handles inheritance resolution internally
- Includes proactive warnings and suggestions
- Shows related topics for discovery

#### teach
**Request:**
```
teach(project_id: str, knowledge: str, context?: str) -> TeachResult
```

**Examples:**
```
teach("checkout-api", "Always use 4 spaces for indentation, never tabs")
teach("checkout-api", "Hash passwords with bcrypt cost factor 12", "security requirement")
teach("checkout-api", "Database queries must include user_id in WHERE clause", "data isolation")
```

**Returns:**
```json
{
  "status": "stored",
  "knowledge_id": "kb_12345",
  "extracted_rules": [
    {"category": "coding", "rule": "Use 4 spaces for indentation", "scope": "PROJECT"}
  ],
  "conflicts": [],
  "suggestions": {
    "promote_to_product": false,
    "related_existing": ["coding standards", "style guide"]
  }
}
```

**Alternative (conflict case):**
```json
{
  "status": "conflict",
  "knowledge_id": null,
  "conflicts": [
    {
      "existing_rule": "Use 2 spaces for indentation",
      "source": "PRODUCT",
      "reason": "Previous team standard"
    }
  ],
  "resolution_options": [
    "overwrite_project_only",
    "update_product_wide", 
    "create_exception"
  ]
}
```

**Notes:**
- Natural language input, AI extracts structure
- Automatic conflict detection
- Suggests promotion opportunities
- Provides resolution options for conflicts

### Learning Operations

#### learn_from_error
**Request:**
```
learn_from_error(project_id: str, error_description: str, solution: str) -> LearnResult
```

**Examples:**
```
learn_from_error("checkout-api", "Out of memory processing large dataset", "Process in chunks of 5000 records maximum")
learn_from_error("checkout-api", "Webhook timeout causing duplicate charges", "Implement idempotency with 24-hour keys")
```

**Returns:**
```json
{
  "status": "learned",
  "lesson_id": "lesson_789",
  "generated_rules": [
    {
      "category": "data-processing", 
      "rule": "Process large datasets in chunks of 5000 records maximum",
      "trigger": "bulk operations",
      "severity": "critical"
    }
  ],
  "prevention_patterns": [
    "Add memory usage monitoring for bulk operations",
    "Implement progress tracking for large datasets"
  ],
  "related_incidents": []
}
```

**Notes:**
- Captures failure context and prevention
- Generates multiple related rules
- Links to similar past incidents
- Creates proactive monitoring suggestions

#### update_knowledge
**Request:**
```
update_knowledge(project_id: str, old_knowledge: str, new_knowledge: str) -> UpdateResult
```

**Examples:**
```
update_knowledge("checkout-api", "Use 2 spaces for indentation", "Use 4 spaces for indentation")
update_knowledge("checkout-api", "Process in chunks of 10000 records", "Process in chunks of 5000 records")
```

**Returns:**
```json
{
  "status": "updated",
  "changes": [
    {
      "scope": "PROJECT",
      "category": "coding",
      "old_rule": "Use 2 spaces for indentation",
      "new_rule": "Use 4 spaces for indentation",
      "affected_contexts": ["python files", "javascript files"]
    }
  ],
  "cascade_effects": [
    "3 related rules in auth-group also updated",
    "Existing code review checklist needs updating"
  ]
}
```

**Notes:**
- Natural language matching for updates
- Shows cascade effects across inheritance
- Identifies affected systems/processes

### Advanced Operations

#### get_project_knowledge
**Request:**
```
get_project_knowledge(project_id: str, domain?: str) -> ProjectKnowledge
```

**Returns:**
```json
{
  "project_id": "checkout-api",
  "knowledge_summary": {
    "total_rules": 47,
    "categories": {
      "coding": 12,
      "security": 8,
      "database": 9,
      "api": 11,
      "deployment": 7
    },
    "recent_additions": [
      {"date": "2024-01-15", "rule": "Include JIRA tickets", "category": "coding"}
    ]
  },
  "inheritance_breakdown": {
    "PROJECT": 15,
    "payments-group": 12,
    "webapp-product": 13,
    "general": 7
  },
  "knowledge_health": {
    "conflicts": 0,
    "outdated_rules": 2,
    "missing_contexts": ["testing", "monitoring"]
  }
}
```

#### promote_knowledge
**Request:**
```
promote_knowledge(from_scope: str, to_scope: str, knowledge_id: str) -> PromoteResult
```

**Returns:**
```json
{
  "status": "promoted",
  "from_scope": "checkout-api",
  "to_scope": "payments-group", 
  "affected_projects": ["checkout-api", "payment-gateway", "billing-service"],
  "rule": "Always validate refund amounts as negative",
  "impact_analysis": {
    "projects_gaining_rule": 2,
    "potential_conflicts": 0,
    "estimated_benefit": "Prevents refund bugs across all payment services"
  }
}
```

### Project Hierarchy Operations

#### register_project
**Request:**
```
register_project(project_id: str, product_id?: str, group_ids?: List[str]) -> RegistrationResult
```

**Examples:**
```
// Register new project with full hierarchy
register_project("checkout-api", "webapp-product", ["payments-group", "auth-group"])

// Register project with just product (no groups)
register_project("mobile-app", "mobile-product")

// Register standalone project (inherits from general only)
register_project("utility-script")
```

**Returns:**
```json
{
  "status": "registered",
  "project_id": "checkout-api",
  "inheritance_chain": [
    {"scope": "checkout-api", "tier": "PROJECT"},
    {"scope": "payments-group", "tier": "GROUP"},
    {"scope": "auth-group", "tier": "GROUP"},
    {"scope": "webapp-product", "tier": "PRODUCT"},
    {"scope": "general", "tier": "GENERAL"}
  ],
  "validation": {
    "product_exists": true,
    "groups_exist": ["payments-group", "auth-group"],
    "auto_created": []
  }
}
```

#### get_project_hierarchy
**Request:**
```
get_project_hierarchy(project_id: str) -> HierarchyInfo
```

**Returns:**
```json
{
  "project_id": "checkout-api",
  "inheritance_chain": [
    {"scope_id": "checkout-api", "tier": "PROJECT", "knowledge_count": 15},
    {"scope_id": "payments-group", "tier": "GROUP", "knowledge_count": 8},
    {"scope_id": "auth-group", "tier": "GROUP", "knowledge_count": 6},
    {"scope_id": "webapp-product", "tier": "PRODUCT", "knowledge_count": 12},
    {"scope_id": "general", "tier": "GENERAL", "knowledge_count": 25}
  ],
  "direct_groups": ["payments-group", "auth-group"],
  "product": "webapp-product",
  "total_inherited_knowledge": 66,
  "hierarchy_health": {
    "missing_scopes": [],
    "knowledge_conflicts": 0,
    "last_updated": "2024-01-15"
  }
}
```

#### update_project_hierarchy
**Request:**
```
update_project_hierarchy(project_id: str, new_product?: str, new_groups?: List[str]) -> UpdateResult
```

**Examples:**
```
// Change product assignment
update_project_hierarchy("checkout-api", new_product="fintech-product")

// Update group memberships
update_project_hierarchy("checkout-api", new_groups=["payments-group", "core-group"])

// Complete hierarchy change
update_project_hierarchy("checkout-api", "new-product", ["different-group"])
```

**Returns:**
```json
{
  "status": "updated",
  "project_id": "checkout-api",
  "changes": {
    "product": {"from": "webapp-product", "to": "fintech-product"},
    "groups": {
      "removed": ["auth-group"],
      "added": ["core-group"],
      "unchanged": ["payments-group"]
    }
  },
  "impact_analysis": {
    "knowledge_changes": {
      "gained": 8,
      "lost": 3,
      "net_change": "+5 knowledge entries"
    },
    "affected_categories": ["authentication", "logging", "error-handling"],
    "potential_conflicts": [],
    "new_inheritance_chain": [
      "checkout-api", "payments-group", "core-group", "fintech-product", "general"
    ]
  }
}
```

**Notes:**
- Updates cascade to knowledge inheritance immediately
- Impact analysis shows what knowledge is gained/lost
- Validates new hierarchy before applying changes
- Can create new scopes if they don't exist

## AI Behavior Patterns

### Flexible Session Flows

**Quick Task Session:**
```
1. init_session("project", "quick_start") → Minimal context
2. ask_knowledge("project", "task info") → Relevant rules  
3. end_session("project", "completed X") → Record progress
```

**Continue Previous Work:**
```
1. init_session("project", "continue_work", 3) → Detailed task history
2. AI knows exactly where to resume from session context
3. Complete work and record progress
```

**Teaching Session:**
```
1. init_session("project") → Standard context
2. teach("project", "new knowledge", "scope") → Store with scope control
3. end_session("project", "taught standards") → Record session
```

**Status Check:**
```
1. init_session("project", "status_only") → Progress overview only
2. Quick assessment without full context loading
```

### Natural Language Processing
- All knowledge input/queries use natural language
- AI handles categorization, keyword extraction, scope determination
- Users never need to understand internal structure
- Conflicts presented in plain English with clear options

### Proactive Intelligence
- `init_session()` provides warnings immediately
- `ask_knowledge()` suggests related topics
- `teach()` detects promotion opportunities
- All operations include prevention/improvement suggestions

## Key Improvements Over v1

### Reduced Cognitive Load
- **v1**: 11 operations, complex parameters, manual categorization
- **v2**: 6 core operations, natural language, automatic classification

### Better User Experience
- **v1**: `get_categories() → get_keywords() → get_knowledge()`
- **v2**: `ask_knowledge("git commit rules")` - single natural query

### Fewer Errors
- **v1**: Manual scope_id, category, keyword specification
- **v2**: AI determines optimal storage location and structure

### Complete Context
- **v1**: Multiple calls for session context
- **v2**: `init_session()` provides everything in one call

### Intelligent Defaults
- **v1**: Explicit conflict handling required
- **v2**: Smart conflict resolution with clear options

## Protocol Architecture

### Smart Categorization
AI automatically extracts:
- Knowledge categories from natural language
- Appropriate scope for storage
- Related context and metadata
- Conflict detection and resolution options

### Unified Context
Single operations provide complete relevant information:
- Session context includes warnings
- Knowledge queries include suggestions
- Storage operations suggest improvements

### Natural Language Interface
Users interact in plain English:
- "git commit rules" vs `get_knowledge(scope_id, ["commit"])`
- "Always use 4 spaces" vs `store_knowledge_if_missing("checkout-api", "coding", "indentation", ...)`

### Proactive Intelligence
Every operation includes:
- Relevant warnings
- Improvement suggestions
- Related topic discovery
- Impact analysis

This v2 protocol maintains all functionality while being significantly more user-friendly and less error-prone.