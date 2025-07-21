# Project Kaizen - Knowledge Protocol Specification

## Protocol Integration Instructions

### CLAUDE.md Integration
Add the following sections to `CLAUDE.md`:

```markdown
## Knowledge Protocol Behavior

### Session Initialization
Before starting any work session:
1. Call get_project_overview() for high-level context
2. Call get_session_history(limit=3) for recent work
3. Call get_progress_status() for current state
4. Synthesize into natural continuation

### Task Preparation  
Before starting any task:
1. Call get_categories() for relevant domains
2. Call get_keywords() for task context
3. Call get_knowledge() for all related keywords
4. Check content for risk indicators (WARNING:, DANGER:, LAST TIME:)
5. Present warnings to user before proceeding

### Knowledge Storage
- Teaching sessions: Use store_knowledge_if_missing() first, ask user for conflict resolution
- Failure learning: Propose rule after error, use store_knowledge_overwrite() with approval
- Spontaneous additions: Use store_knowledge_if_missing() for new insights

### Session End
- Call store_session_summary() with completed tasks
- Include domain context and next planned work
- Keep summaries concise but informative
```

### MCP Server Implementation
The MCP server must implement all operations defined in this protocol with exact signatures and return formats.

## Protocol Operations Overview

### Knowledge Retrieval Operations
```
get_categories(scope_id: str) -> List[Category]
get_keywords(scope_id: str, categories: List[str]) -> Dict[str, List[str]]
get_knowledge(scope_id: str, keywords: List[str]) -> List[Entry]
```

### Context & Session Operations
```
get_project_overview(project_id: str) -> ProjectContext
get_session_history(project_id: str, limit?: int) -> List[SessionSummary]
get_progress_status(project_id: str, domain?: str) -> TaskStatus
store_session_summary(project_id: str, summary: str, tasks_completed: List[str], domain?: str, next_planned?: str) -> Success
```

### Knowledge Storage Operations
```
store_knowledge_if_missing(target_scope_id: str, category: str, keyword: str, content: str, project_context: str, metaknowledge?: Dict[str, str]) -> Result
store_knowledge_overwrite(target_scope_id: str, category: str, keyword: str, content: str, project_context: str, metaknowledge?: Dict[str, str]) -> Result
delete_knowledge(target_scope_id: str, category: str, keyword: str) -> Success
```

## Detailed Operation Specifications

### Knowledge Retrieval Operations

#### get_categories
**Request:**
```
get_categories(scope_id: str) -> List[Category]
```

**Returns:**
```json
[
  {"name": "git", "subcategories": ["workflows", "branching"], "has_entries": true},
  {"name": "git.workflows", "subcategories": [], "has_entries": true},
  {"name": "api", "subcategories": ["auth", "versioning"], "has_entries": false}
]
```

**Notes:**
- Returns hierarchical categories merged from inheritance chain
- Dotted notation for subcategories (git.workflows)
- AI can request parent (git) or specific subcategories (git.workflows)
- `has_entries` indicates if category has direct knowledge entries

#### get_keywords
**Request:**
```
get_keywords(scope_id: str, categories: List[str]) -> Dict[str, List[str]]
```

**Returns:**
```json
{
  "git": ["commit", "push", "merge", "rebase"],
  "git.workflows": ["commit", "push"],
  "api.auth": ["tokens", "oauth"]
}
```

**Notes:**
- Keywords merged from inheritance chain for each category
- Supports both parent categories (git) and subcategories (git.workflows)
- Parent category keywords include all subcategory keywords
- Only requested categories returned

#### get_knowledge
**Request:**
```
get_knowledge(scope_id: str, keywords: List[str]) -> List[Entry]
```

**Returns:**
```json
[
  {
    "keyword": "commit",
    "content": "Include JIRA ticket in message",
    "source_tier": "PROJECT",
    "metaknowledge": {
      "REASON": "Required for audit compliance",
      "DATE_ADDED": "2024-01-10"
    }
  }
]
```

**Notes:**
- Each keyword appears ONCE with its most specific entry
- MCP has already resolved inheritance
- `source_tier` included for transparency
- `metaknowledge` contains 0+ labeled metadata entries

### Context & Session Operations

#### get_project_overview
**Request:**
```
get_project_overview(project_id: str) -> ProjectContext
```

**Returns:**
```json
{
  "project_id": "checkout-api",
  "purpose": "fintech platform API for small business loans",
  "tech_stack": ["Python", "FastAPI", "PostgreSQL", "React"],
  "compliance": ["SOC2", "PCI"],
  "current_phase": "MVP development",
  "key_constraints": ["30-second timeout for mobile", "512MB staging limit"]
}
```

#### get_session_history
**Request:**
```
get_session_history(project_id: str, limit?: int) -> List[SessionSummary]
```

**Returns:**
```json
[
  {
    "date": "2024-01-15",
    "duration_minutes": 45,
    "summary": "Completed user authentication endpoints",
    "tasks_completed": ["login endpoint", "register endpoint", "JWT middleware"],
    "domain": "backend-api",
    "next_planned": "password reset functionality"
  }
]
```

#### get_progress_status
**Request:**
```
get_progress_status(project_id: str, domain?: str) -> TaskStatus
```

**Returns:**
```json
{
  "overall_progress": "40% complete",
  "current_sprint": "Authentication & User Management",
  "completed_tasks": [
    {"name": "user registration", "domain": "backend", "date": "2024-01-10"}
  ],
  "in_progress_tasks": [
    {"name": "OAuth integration", "domain": "backend", "status": "GitHub done, Google pending"}
  ],
  "blocked_tasks": [
    {"name": "callback URL issue", "domain": "backend", "blocker": "waiting for DevOps"}
  ]
}
```

#### store_session_summary
**Request:**
```
store_session_summary(project_id: str, summary: str, tasks_completed: List[str], domain?: str, next_planned?: str) -> Success
```

**Example:**
```
store_session_summary(
  "checkout-api", 
  "Completed user authentication endpoints",
  ["login endpoint", "register endpoint", "JWT middleware"],
  "backend-api",
  "password reset functionality"
)
```

### Knowledge Storage Operations

#### store_knowledge_if_missing
**Request:**
```
store_knowledge_if_missing(target_scope_id: str, category: str, keyword: str, content: str, project_context: str, metaknowledge?: Dict[str, str]) -> Result
```

**Returns:**
```json
// Success case
{"success": true}

// Conflict case
{"success": false, "existing_content": "Use 2 spaces for indentation", "existing_metaknowledge": {"REASON": "Team preference"}}
```

#### store_knowledge_overwrite
**Request:**
```
store_knowledge_overwrite(target_scope_id: str, category: str, keyword: str, content: str, project_context: str, metaknowledge?: Dict[str, str]) -> Result
```

**Returns:**
```json
// New entry
{"success": true, "previous_content": null, "previous_metaknowledge": null}

// Overwritten entry
{"success": true, "previous_content": "Use 2 spaces for indentation", "previous_metaknowledge": {"REASON": "Old team preference"}}
```

**Storage Examples:**
```
// Safe storage (teaching new rule)
store_knowledge_if_missing("checkout-api", "coding", "indentation", "Use 4 spaces, never tabs", "checkout-api", {"REASON": "Team coding standard"})
→ {"success": false, "existing_content": "Use 2 spaces", "existing_metaknowledge": {"REASON": "Previous standard"}}
// AI can ask user how to proceed

// Force update (correcting rule)
store_knowledge_overwrite("checkout-api", "validation", "refund_amounts", "All refunds must be negative values", "checkout-api", {
  "REASON": "Added after double-charge bug", 
  "INCIDENT_ID": "REF-2024-003",
  "SEVERITY": "Critical"
})
→ {"success": true, "previous_content": null, "previous_metaknowledge": null}
// AI can explain: "Stored refund validation rule due to critical incident REF-2024-003"
```

#### delete_knowledge
**Request:**
```
delete_knowledge(target_scope_id: str, category: str, keyword: str) -> Success
```

## AI Behavior Patterns

### Proactive Knowledge Checking
**Before starting any task, AI must:**
1. `get_categories()` for relevant domains
2. `get_keywords()` for task context
3. `get_knowledge()` for all related keywords
4. Check content for risk indicators and present warnings

**Risk Indicator Conventions:**
- `WARNING:` prefix for important cautions
- `DANGER:` prefix for critical risks
- `LAST TIME:` prefix for historical context

**Example:**
```
User: "Update user table schema"
AI: [Retrieves knowledge]
Finds: "WARNING: Cascade deletes affect 5 tables. LAST TIME: Required 2-hour maintenance window."
AI: "Before modifying the user table, I should mention: [presents warnings]"
```

### Knowledge Storage Patterns
**Teaching Sessions:**
- Use `store_knowledge_if_missing()` first
- If conflict, ask user for resolution
- Use `store_knowledge_overwrite()` only with explicit user approval

**Failure Learning:**
- AI proposes rule after error
- User approves before storage
- Use `store_knowledge_overwrite()` to replace any existing incomplete rules

**Spontaneous Additions:**
- User provides insights after success
- Use `store_knowledge_if_missing()` as these are typically new patterns
- If conflict, user decides precedence

### Session Continuity Patterns
**Session Start:**
1. `get_project_overview()` for high-level context
2. `get_session_history(limit=3)` for recent work
3. `get_progress_status()` for current state
4. Synthesize into natural continuation

**Session End:**
- `store_session_summary()` with completed tasks
- Include domain context and next planned work
- Keep summaries concise but informative

## Terminology

- **Tier**: Hierarchical level (GENERAL, PRODUCT, GROUP, PROJECT)
- **Scope**: A specific named container at a tier (e.g., "checkout-api" at PROJECT tier)
- **Scope ID**: Unique identifier for a scope (e.g., "checkout-api", "webapp", "general")
- **Entry**: Individual piece of knowledge within a scope
- **Category**: Hierarchical grouping of knowledge (e.g., "git.workflows", "api.auth")
- **Inheritance Chain**: Variable-length path from specific scope up to GENERAL tier
- **Inheritance**: Entries from parent scopes are inherited by child scopes (most specific wins)
- **Metaknowledge**: Labeled metadata attached to knowledge entries (0+ key:value pairs)

## Inheritance Resolution

### Variable Chain Structure
- **GENERAL tier**: 0-1 scopes
- **PRODUCT tier**: 0-1 scopes  
- **GROUP tier**: 0+ scopes (projects can belong to multiple groups)
- **PROJECT tier**: 1 scope (always exists)

### Multiple Group Membership
A project can belong to multiple groups simultaneously, creating branching inheritance:
```
    checkout-api (PROJECT)
         |
   +-----+-----+-----+
   |     |     |     |
auth  mobile web  payments (GROUPS)
   \     |     |     /
    \    |     |    /
     \   |     |   /
      webapp-product
          |
        general
```

### Resolution Process
1. Traces from requested scope_id up through all parent scope paths
2. Builds inheritance tree with branching at GROUP tier
3. For each keyword, searches all paths for entries
4. Resolves conflicts using precedence rules
5. Returns single most specific entry per keyword
6. AI receives clean, resolved data with source_tier for transparency

### Conflict Resolution for Multiple Groups
When multiple groups contain entries for the same keyword:
1. **Tier precedence**: PROJECT > GROUP > PRODUCT > GENERAL
2. **Group precedence**: Lexicographic ordering of group names (deterministic)
3. **Example**: If `auth-group` and `web-group` both define "tokens", `auth-group` wins ("auth" < "web")

**Rationale:**
- Deterministic results (same query always returns same answer)
- No configuration required
- Predictable behavior for AI and developers

## Example Usage Flow

**Task:** "Create git commit"

1. **AI:** get_categories("checkout-api")  
   **Sees:** git (with workflows, branching subcategories), api, testing

2. **AI:** get_keywords("checkout-api", ["git.workflows"])  
   **Sees:** commit, push (workflow-specific keywords)

3. **AI:** get_knowledge("checkout-api", ["commit", "push"])  
   **Gets:** Most specific rules from inheritance chain

AI now has targeted knowledge and full context in <3ms.

**Multiple Group Inheritance Example:**

If `checkout-api` belongs to `[auth-group, payments-group]` and both groups define "tokens":
- `auth-group`: "tokens" → "Use JWT with 1h expiry"
- `payments-group`: "tokens" → "Use API keys for payment endpoints"

MCP returns: `auth-group` entry (lexicographic precedence: "auth" < "payments")

## Storage Strategy

- Categories and keywords stored normalized
- Entries linked via foreign keys
- Scope IDs must be unique across the system
- **Inheritance Relationships:**
  - PROJECT → PRODUCT: many-to-one
  - PROJECT → GROUP: many-to-many (junction table required)
  - GROUP → PRODUCT: many-to-one
  - PRODUCT → GENERAL: many-to-one
- Path resolution uses recursive queries or graph traversal
- Group precedence pre-computed and cached for performance

## Design Decisions

**Why Scope ID instead of Project Name?**
- Works for any tier (GENERAL, PRODUCT, GROUP, PROJECT)
- Handles variable hierarchy depths gracefully
- Prevents naming collisions across tiers
- MCP determines inheritance chain from any scope ID

**Why Hierarchical Categories?**
- Real knowledge is naturally hierarchical (git/workflows/commit)
- AI can choose granularity ("git" vs "git.workflows")
- Maintains 3-step protocol simplicity
- Dotted notation is familiar and intuitive

**Why Lexicographic Group Precedence?**
- Deterministic conflict resolution (same query = same result)
- No additional configuration required
- Predictable behavior for developers
- Alternative approaches (explicit precedence, timestamps) add complexity

**Why Metaknowledge?**
- Preserves institutional memory and decision context
- Flexible key:value structure adapts to different needs
- Enables rich explanations of WHY rules exist
- Optional field keeps simple cases simple