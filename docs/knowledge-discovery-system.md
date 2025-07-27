# Knowledge Discovery System Design

## Core Principles

### Entity Structure
- **Three entities only:** namespace, scope, knowledge
- **No separate keyword/tag entities** - complexity without value
- **Lean architecture** - engineering elegance over feature bloat

### Knowledge Entry Structure
```json
{
  "id": "K7H9M2PQX8",
  "scope": "acme:mobile-app", 
  "content": "Complete implementation guide for Google Sign-In SDK...",
  "context": "react-native google oauth sso signin mobile ios android firebase sdk authentication"
}
```

## Search Intelligence

### AI Query Decomposition
**Complex tasks require multiple targeted queries, not artificial combinations.**

**Example: "commit and push all changes"**
```json
{
  "queries": [
    "git commit changes staged messages",
    "git push remote branch safety"
  ]
}
```

**Returns separate, focused knowledge entries:**
- Git commit conventions and practices
- Git push safety and workflows

**AI combines results intelligently** - system provides building blocks, not pre-built combinations.

### Multi-Query Support
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

Enables complex task support through parallel focused searches.

### Task Size Filtering
AI can specify task complexity to filter relevant knowledge:
- **XS** - quick fixes
- **S** - small features  
- **M** - medium projects
- **L** - large implementations
- **XL** - architectural changes

Knowledge entries should be tagged with appropriate complexity levels for effective filtering.

## Context Field Strategy

### Insert-Time Intelligence
**Knowledge authors must anticipate search patterns and term variations.**

**Example Context Field:**
```
"nodejs node.js express javascript jwt authentication middleware token validation security api"
```

**Covers:**
- **Term variations:** "nodejs" vs "node.js"
- **Technology stack:** "express", "javascript" 
- **Core concepts:** "jwt", "authentication", "middleware"
- **Use cases:** "token validation", "security", "api"

### Domain Expertise Required
- Authors need technical depth to anticipate search terms
- Context field requires understanding of how concepts interconnect
- Balance between comprehensive coverage and focused relevance

## PostgreSQL Implementation

### Schema
```sql
CREATE TABLE knowledge (
  id VARCHAR(10) PRIMARY KEY,
  scope VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  context TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX knowledge_search_idx ON knowledge USING gin(
  to_tsvector('english', content || ' ' || context)
);
```

### Search Query
```sql
SELECT *, ts_rank(search_vector, query) as relevance 
FROM knowledge 
WHERE search_vector @@ plainto_tsquery('english', $1)
AND scope IN (scope_hierarchy($2))
ORDER BY relevance DESC;
```

## Validation Scenarios

### Test Knowledge Entries
1. "Always use HTTPS for external API calls to prevent data interception"
2. "Google OAuth 2.0 setup: client registration, redirect URIs, scope configuration"  
3. "OAuth with PKCE for mobile apps: security best practices and implementation"
4. "Git commit message conventions: semantic versioning and clear descriptions"
5. "Git push safety: force push alternatives, branch protection, team workflows"
6. "Java code formatting: Checkstyle rules, indentation, naming conventions"
7. "React Native Google Sign-In: SDK integration, credential handling"
8. "JWT token authentication for database access and session management"
9. "API rate limiting: throttling strategies, Redis implementation, error responses"
10. "Mobile app security: certificate pinning, keychain storage, biometric auth"

### AI Query Validation
| AI Query | Expected Returns | Reasoning |
|----------|------------------|-----------|
| "implement Google OAuth for mobile app" | K2, K3, K7, K10 | Matches "google oauth", "oauth mobile", "mobile auth" |
| "commit and push code safely" (decomposed) | K4, K5 | Separate queries for commit and push |
| "Java code formatting rules" | K6 | Exact match "java formatting" |
| "secure API communication" | K1, K9 | Matches "API security", "HTTPS", "rate limiting" |
| "mobile authentication best practices" | K3, K7, K10 | Matches "mobile auth", "security practices" |

## Key Insights

### What Works
- **Context field** provides controlled concept expansion without separate entities
- **Multi-query support** handles complex tasks through decomposition
- **PostgreSQL full-text search** provides relevance ranking and performance
- **Lean architecture** - only 3 core entities

### What Doesn't Work
- Artificial knowledge combinations ("commit+push workflows")
- Separate keyword/tag entities (complexity without value)
- Single-query solutions for complex tasks
- Over-broad category systems

### Success Factors
- **Smart AI query decomposition** for complex tasks
- **Thoughtful context field authoring** at insert time
- **PostgreSQL native search** capabilities
- **Scope hierarchy** for result filtering

## Implementation Requirements

### Single Container
- PostgreSQL with full-text search extensions
- Custom functions for scope hierarchy resolution
- Materialized views for performance optimization

### MCP Server
- Standard MCP implementation
- Query parsing and decomposition logic
- Multi-query batch processing support
- Relevance scoring and result organization
