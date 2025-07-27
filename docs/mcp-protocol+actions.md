# MCP Protocol and Actions

## Definitions & Paradigms

### Knowledge Philosophy
- Hard facts only - no confidence scores needed
- Knowledge stands alone - source attribution irrelevant for execution  
- Smart internal filtering - deprecated knowledge not surfaced to AI
- Knowledge entries are packed - complete information per query, not artificially split

### Architecture Principles
- Scope names are complete identifiers using colon notation: `namespace:scope` or `global:default`
- Namespace names are globally unique across all namespaces
- Scope names within namespace are unique (can duplicate across namespaces)
- Renaming namespaces/scopes automatically updates all references
- Context fields within knowledge entries enable precise searchability
- Multi-tenant isolation prevents knowledge pollution

### AI Integration
- Context field handles all searchability - no separate tag entities needed
- Output optimized for execution, not explanation
- Zero-friction experience - AI uses natural language queries
- Context from CLAUDE.md drives automatic scoping
- Task size filtering: XS (quick fixes), S (small features), M (medium projects), L (large implementations), XL (architectural changes)

## Business-Level Protocol

### Initial State
- Only `global:default` scope accepts knowledge immediately
- Project namespaces auto-create "default" scope for immediate use
- AI starts with no knowledge of existing namespaces/scopes

### Progressive Setup Flow
- Phase 1: Query existing namespaces with `get_namespaces()`
- Phase 2: Create/select namespace (automatically creates "default" scope)
- Phase 3: Create additional scopes within namespace (auto-inherit from "default")
- Phase 4: Update CLAUDE.md with scope context (enables auto-assignment)

### Namespace Structure Rules
- Every created namespace automatically gets a "default" top-level scope
- All custom scopes must have "default" as a parent (explicitly listed)
- "default" scope cannot be deleted
- Multiple inheritance supported (scopes can have multiple parents + default)

### Operational State
- AI reads CLAUDE.md for current scope context: `scope: acme:petshop-storefront`
- Knowledge inheritance: current scope → all parents → global:default
- Full functionality enabled

## Endpoints

## Namespace Management

### get_namespaces

**Purpose**: AI discovers existing namespaces and scopes to decide whether to create new or reuse existing organizational structures.

**Input**:
```json
{
  "namespace": "acme",          // optional - exact match filter
  "style": "short"              // short|long|details (default: short)
}
```

**Output - style: "short"**:
```json
{
  "namespaces": {
    "global": {
      "description": "Universal knowledge accessible everywhere"
    },
    "acme": {
      "description": "ACME Corporation projects"
    }
  }
}
```

**Output - style: "long"**:
```json
{
  "namespaces": {
    "global": {
      "description": "Universal knowledge accessible everywhere",
      "scopes": {
        "default": {
          "description": "Universal knowledge accessible everywhere"
        }
      }
    },
    "acme": {
      "description": "ACME Corporation projects",
      "scopes": {
        "default": {
          "description": "ACME organization-wide knowledge"
        },
        "petshop-storefront": {
          "description": "Pet store frontend project"
        },
        "ecommerce-mobile": {
          "description": "Mobile ecommerce group"
        }
      }
    }
  }
}
```

**Output - style: "details"**:
```json
{
  "namespaces": {
    "global": {
      "description": "Universal knowledge accessible everywhere",
      "scopes": {
        "default": {
          "description": "Universal knowledge accessible everywhere",
          "parents": []
        }
      }
    },
    "acme": {
      "description": "ACME Corporation projects",
      "scopes": {
        "default": {
          "description": "ACME organization-wide knowledge",
          "parents": []
        },
        "petshop-storefront": {
          "description": "Pet store frontend project",
          "parents": ["ecommerce-mobile", "payments-team", "default"]
        },
        "ecommerce-mobile": {
          "description": "Mobile ecommerce group",
          "parents": ["default"]
        },
        "payments-team": {
          "description": "Payments specialist team",
          "parents": ["default"]
        }
      }
    }
  }
}
```

**Value**: Single endpoint for namespace discovery, progressive detail levels, enables create/reuse decisions.

### create_namespace

**Purpose**: Create new namespace with automatic "default" scope for immediate knowledge storage.

**Input**:
```json
{
  "name": "acme",
  "description": "ACME Corporation projects"
}
```

**Output**:
```json
{
  "name": "acme",
  "description": "ACME Corporation projects",
  "scopes": {
    "default": {
      "description": "ACME organization-wide knowledge"
    }
  }
}
```

**Value**: Single call creates namespace with ready-to-use default scope, enables immediate knowledge storage.

### update_namespace

**Purpose**: Update namespace name and/or description with automatic reference updating.

**Input**:
```json
{
  "name": "acme",
  "new_name": "acme-corp",           // optional
  "description": "ACME Corporation"  // optional
}
```

**Output**:
```json
{
  "name": "acme-corp",
  "description": "ACME Corporation",
  "scopes": {
    "default": {
      "description": "ACME organization-wide knowledge"
    }
  }
}
```

**Value**: Atomic updates with automatic reference resolution across all scopes and knowledge entries.

### delete_namespace

**Purpose**: Remove namespace and all associated scopes and knowledge entries.

**Input**:
```json
{
  "name": "acme"
}
```

**Output**:
```json
{
  "name": "acme",
  "scopes_count": 3,
  "knowledge_count": 47
}
```

**Value**: Complete cleanup with deletion statistics for confirmation.

## Scope Management

### create_scope

**Purpose**: Create new scope within namespace with automatic "default" parent inheritance.

**Input**:
```json
{
  "scope": "acme:mobile-payments",
  "description": "Mobile payment processing team",
  "parents": ["acme:ecommerce-mobile", "acme:payments-team"]    // optional - "acme:default" auto-added
}
```

**Output**:
```json
{
  "scope": "acme:mobile-payments",
  "description": "Mobile payment processing team", 
  "parents": ["acme:ecommerce-mobile", "acme:payments-team", "acme:default"]
}
```

**Value**: Automatic parent inheritance from "default", immediate knowledge inheritance from parent scopes.

### update_scope

**Purpose**: Update scope name, description, and parent relationships with automatic reference updating.

**Input**:
```json
{
  "scope": "acme:mobile-payments",
  "new_scope": "acme:mobile-commerce",           // optional
  "description": "Mobile commerce team",         // optional
  "parents": ["acme:ecommerce-mobile"]          // optional - "acme:default" always preserved
}
```

**Output**:
```json
{
  "scope": "acme:mobile-commerce",
  "description": "Mobile commerce team",
  "parents": ["acme:ecommerce-mobile", "acme:default"]
}
```

**Value**: Atomic updates with automatic reference resolution, "default" parent always preserved.

### delete_scope

**Purpose**: Remove scope and all associated knowledge entries.

**Input**:
```json
{
  "scope": "acme:mobile-payments"
}
```

**Output**:
```json
{
  "scope": "acme:mobile-payments",
  "knowledge_deleted": 12
}
```

**Value**: Complete cleanup with deletion statistics, cannot delete "default" scope.

## Knowledge Management

### write_knowledge

**Purpose**: Store new knowledge entry with automatic scope assignment and context tagging.

**Input**:
```json
{
  "content": "Complete implementation guide for Google Sign-In SDK in React Native applications...",
  "context": "react-native google oauth sso signin mobile ios android firebase sdk authentication",
  "scope": "acme:mobile-app"
}
```

**Output**:
```json
{
  "id": "K7H9M2PQX8",
  "scope": "acme:mobile-app"
}
```

**Value**: Automatic ID generation, context-driven discoverability, immediate availability for searches.

### update_knowledge

**Purpose**: Update knowledge entry content, context, or scope assignment.

**Input**:
```json
{
  "id": "K7H9M2PQX8",
  "content": "Updated implementation guide...",       // optional
  "context": "react-native google oauth mobile",     // optional
  "scope": "acme:mobile-payments"                    // optional
}
```

**Output**:
```json
{
  "id": "K7H9M2PQX8",
  "scope": "acme:mobile-payments"
}
```

**Value**: Atomic updates with search index refresh, scope migration support.

### delete_knowledge

**Purpose**: Remove knowledge entry from system.

**Input**:
```json
{
  "id": "K7H9M2PQX8"
}
```

**Output**:
```json
{
  "id": "K7H9M2PQX8"
}
```

**Value**: Immediate removal from search index and scope hierarchy.

### resolve_knowledge_collision

**Purpose**: Mark knowledge entries for collision resolution when contradictory information exists.

**Input**:
```json
{
  "active_id": "K7H9M2PQX8",
  "suppressed_ids": ["G3K7R4NXL9", "J9L2X6VB43"]
}
```

**Output**:
```json
{
  "active_id": "K7H9M2PQX8",
  "suppressed_ids": ["G3K7R4NXL9", "J9L2X6VB43"]
}
```

**Value**: Conflict resolution with audit trail, suppressed entries hidden from future searches.

## Knowledge Retrieval

### get_task_context

**Purpose**: AI provides multiple targeted queries for complex tasks, MCP returns relevant knowledge organized by scope hierarchy.

**Input**:
```json
{
  "queries": [
    "google oauth frontend integration", 
    "oauth backend validation security",
    "sso login ui components"
  ],
  "scope": "acme:petshop-storefront",
  "task_size": "M"
}
```

**Output**:
```json
{
  "acme:petshop-storefront": {
    "K7H9M2PQX8": "Use custom OAuth redirect handler for iOS"
  },
  "acme:ecommerce-mobile": {
    "G3K7R4NXL9": "Mobile group must use OAuth with PKCE"
  },
  "global:default": {
    "J9L2X6VB43": "Always use HTTPS for external APIs"
  }
}
```

**Value**: Multi-query decomposition for complex tasks, PostgreSQL full-text search, scope hierarchy traversal with collision detection support.
