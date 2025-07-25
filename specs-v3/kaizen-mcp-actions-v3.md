# Kaizen MCP Actions v1

## Definitions & Paradigms

### Knowledge Philosophy
- Hard facts only - no confidence scores needed
- Knowledge stands alone - source attribution irrelevant for execution  
- Smart internal filtering - deprecated knowledge not surfaced to AI
- Each knowledge entry is a separate, atomic fact

### Architecture Principles
- Scope names are complete identifiers using colon notation: `namespace:scope` or `global`
- Namespace names are globally unique across all namespaces
- Scope names within namespace are unique (can duplicate across namespaces)
- Renaming namespaces/scopes automatically updates all references
- Universal concept tags work across all namespaces
- Tag variations automatically resolve to canonical forms
- Multi-tenant isolation prevents knowledge pollution

### AI Integration
- Tags handle all context - no metadata fields needed
- Output optimized for execution, not explanation
- Zero-friction experience - AI extracts tags naturally
- Context from CLAUDE.md drives automatic scoping

## Business-Level Protocol

### Initial State
- Only `global:default` scope accepts knowledge immediately
- Project-specific namespaces require scopes before accepting knowledge
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

### get_task_context

**Purpose**: AI extracts keywords from task context, MCP returns relevant knowledge organized by scope hierarchy.

**Input**:
```json
{
  "include_tags": ["authentication", "security"],
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

**Value**: Context-aware knowledge retrieval with hierarchy traversal, conflict-resolved results, zero configuration.

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