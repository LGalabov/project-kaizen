# MCP Knowledge Protocol Specification

## Overview
Three-step discovery protocol for AI agents to retrieve hierarchical knowledge with inheritance resolution.

## Terminology
- **Tier**: Hierarchical level (GENERAL, PRODUCT, GROUP, PROJECT)
- **Scope**: A specific named container at a tier (e.g., "checkout-api" at PROJECT tier)
- **Scope ID**: Unique identifier for a scope (e.g., "checkout-api", "webapp", "general")
- **Entry**: Individual piece of knowledge within a scope
- **Inheritance**: Entries from parent scopes are inherited by child scopes

## Protocol Steps

### Step 1: Category Discovery
**Request:**
```
get_categories(project_name: str) -> List[Category]
```

**Returns:**
```json
[
  {"name": "git", "tier": "PROJECT", "description": "Git workflow rules"},
  {"name": "git", "tier": "GENERAL", "description": "Base git practices"},
  {"name": "api", "tier": "PRODUCT", "description": "API standards"}
]
```

**Notes:**
- Returns merged categories from all inherited scopes
- Categories from more specific scopes override general ones
- AI sees final merged view, not duplicates

### Step 2: Keyword Discovery
**Request:**
```
get_keywords(project_name: str, categories: List[str]) -> Dict[str, List[str]]
```

**Returns:**
```json
{
  "git": ["commit", "push", "merge", "rebase"],
  "api": ["versioning", "auth", "rate-limiting"]
}
```

**Notes:**
- Keywords are merged across tiers (union of all)
- Only requested categories returned
- Lightweight payload

### Step 3: Knowledge Retrieval
**Request:**
```
get_knowledge(scope_id: str, keywords: List[str]) -> List[Entry]
```
**Note:** Returns only the most specific entry for each keyword - inheritance already resolved.

**Returns:**
```json
[
  {
    "keyword": "commit",
    "content": "Include JIRA ticket in message",
    "source_tier": "PROJECT"
  },
  {
    "keyword": "push", 
    "content": "Always push to feature branch first",
    "source_tier": "PRODUCT"
  }
]
```

**Notes:**
- Each keyword appears ONCE with its most specific entry
- MCP has already resolved inheritance
- `source_tier` included for transparency

## Inheritance Resolution

**Rule:** Most specific scope wins
- PROJECT > GROUP > PRODUCT > GENERAL

**MCP handles this internally:**
- Traces from requested scope up through parent scopes
- Returns only the most specific entry per keyword
- AI receives clean, resolved data

## Performance Characteristics

- Local Docker deployment: ~0.5ms per query
- Total retrieval time: <2ms for all three steps
- Indexed on: project paths, categories, keywords

## Storage Strategy

- Categories and keywords stored normalized
- Entries linked via foreign keys
- Path-based inheritance (PostgreSQL ltree or similar)
- Scope IDs must be unique across the system

## Example Usage Flow

**Task:** "Create git commit"

1. **AI:** get_categories("checkout-api")  
   **Sees:** git, api, testing, security categories

2. **AI:** get_keywords("checkout-api", ["git"])  
   **Sees:** commit, push, merge, rebase

3. **AI:** get_knowledge("checkout-api", ["commit", "push"])  
   **Gets:** Specific rules with inheritance pre-computed

AI now has all applicable knowledge in <2ms.

## Design Decisions

**Why Scope ID instead of Project Name?**
- Scope ID works for all tiers, not just projects
- Prevents naming collisions (e.g., "api" could be a project name AND a category)
- MCP determines inheritance chain from any scope ID

