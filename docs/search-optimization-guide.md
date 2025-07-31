# MCP Knowledge Search Optimization Guide

This guide provides best practices for creating searchable knowledge entries and forming effective AI queries to maximize relevant results while minimizing noise.

## Table of Contents
- [Knowledge Entry Best Practices](#knowledge-entry-best-practices)
- [AI Query Formation Strategy](#ai-query-formation-strategy)
- [Search Configuration](#search-configuration)
- [Testing and Validation](#testing-and-validation)

## Knowledge Entry Best Practices

### Content Structure

**Content Field**: Focus on actionable, specific implementation details
```
✅ GOOD: "ShopCraft inventory management uses real-time stock tracking with Redis. When stock falls below threshold, automatic purchase orders are created."

❌ BAD: "We use inventory stuff and it works with some database thing for tracking."
```

**Context Field**: Use standardized technical vocabulary for searchability
```
✅ GOOD: "shopcraft inventory stock tracking redis threshold purchase orders warehouse webhook"

❌ BAD: "shop craft stock stuff db redis thing ordering system"
```

### Technical Term Standardization

Always use canonical forms of technology names:

| Technology | ✅ Standard Form | ❌ Avoid |
|------------|------------------|----------|
| Node.js | `nodejs` | node, Node, node.js, nodeJS |
| React | `react` | React.js, reactjs, ReactJS |
| PostgreSQL | `postgresql` | postgres, psql, PostgreSQL |
| Kubernetes | `kubernetes` | k8s, kube, Kubernetes |
| JavaScript | `javascript` | js, JS, Javascript |
| TypeScript | `typescript` | ts, TS, Typescript |

### Context Keywords Strategy

**Use 6-12 relevant keywords** that developers might search for:

```sql
-- Example: Authentication knowledge
INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
(scope_id,
 'ShopCraft user authentication supports OAuth social login, two-factor authentication, password reset flows, and account verification. Use JWT with refresh tokens.',
 'shopcraft authentication oauth social login two-factor password reset jwt refresh tokens verification',
 'M');
```

**Keyword Selection Principles**:
1. **Technology stack**: `oauth`, `jwt`, `authentication`
2. **Feature names**: `social login`, `two-factor`, `password reset`
3. **Domain concepts**: `user`, `verification`, `tokens`
4. **Implementation details**: `refresh tokens`, `flows`

### Multi-Level Coverage

Structure knowledge to cover different abstraction levels:

```sql
-- Architecture Level
'microservices architecture react nodejs postgresql redis rest api jwt authentication'

-- Implementation Level  
'express helmet security headers compression middleware winston jwt authentication health checks'

-- Configuration Level
'connection pooling max connections read replicas transactions multi-table operations'
```

## AI Query Formation Strategy

### Multi-Query Approach

Use 3-4 distinct queries targeting different aspects of the implementation task:

```python
# Example: Real-time inventory feature
query_terms = [
    "inventory management stock tracking",    # Business domain
    "database transactions rollback",        # Data consistency  
    "redis caching session data",           # Technical implementation
    "backend api circuit breaker"           # Infrastructure patterns
]
```

### Query Term Patterns

**✅ Effective 2-3 Word Phrases**:
```python
[
    "authentication oauth",      # Technology + concept
    "database transactions",     # Domain + pattern
    "error handling",           # Cross-cutting concern
    "mobile app security"       # Platform + requirement
]
```

**❌ Ineffective Query Patterns**:
```python
[
    "oauth social login authentication flows with jwt",  # Too specific/long
    "auth",                                              # Too generic
    "nodejs",                                           # Technology only
    "how to implement user login system"                # Natural language
]
```

### Technical Term Normalization

AI should automatically normalize user input to standard technical vocabulary:

```python
def normalize_tech_terms(user_input: str) -> str:
    """
    Examples of AI normalization:
    - "noddeJS error handeling" → "nodejs error handling"
    - "React.js components" → "react components"  
    - "databse conectivity" → "database connectivity"
    - "k8s deployment" → "kubernetes deployment"
    """
    # Implementation handles typos and standardizes terms
    pass
```

### Query Formation by Task Type

**New Feature Implementation**:
```python
[
    "{feature} requirements",     # Business logic
    "{technology} patterns",      # Technical approach  
    "testing {domain}",          # Quality assurance
    "{scope} architecture"       # System design
]
```

**Bug Investigation**:
```python
[
    "error handling {domain}",   # Error patterns
    "debugging {technology}",    # Investigation tools
    "monitoring {service}",      # Observability
    "rollback procedures"        # Recovery
]
```

**Performance Optimization**:
```python
[
    "performance {technology}",  # Tech-specific optimizations
    "caching strategies",        # Speed improvements
    "database optimization",     # Data layer
    "monitoring metrics"         # Measurement
]
```

## Search Configuration

### Relevance Threshold Recommendations

**Default: 0.3-0.4** for AI-generated queries
- AI queries are consistent and typo-free
- Lower thresholds capture valuable peripheral knowledge
- Quality remains high due to standardized terminology

**Threshold by Use Case**:
- **Exploration**: 0.3 (broader results for learning)
- **Implementation**: 0.4 (focused, actionable results)  
- **Emergency**: 0.5 (highest confidence results only)

### Search Weights Configuration

Current optimal settings:
```sql
'search.context_weight': '1.0'    -- Context field importance
'search.content_weight': '0.4'    -- Content field importance  
'search.relevance_threshold': '0.4'
'search.max_results': '50'
```

**Why Context > Content**:
- Context uses standardized technical vocabulary
- Content may have natural language variations
- Context keywords are optimized for search

## Testing and Validation

### Query Effectiveness Testing

Test queries should return comprehensive results:

```sql
-- Test: Authentication implementation
SELECT qualified_scope_name, relevance_rank, LEFT(content, 80) as preview
FROM get_task_context(
    ARRAY['authentication oauth', 'security jwt', 'mobile app', 'error handling'],
    'shopcraft:frontend-team',
    'M'::task_size_enum
)
ORDER BY relevance_rank DESC;

-- Expected: 3-5 results covering:
-- ✅ Business requirements (ShopCraft auth specs)
-- ✅ Security standards (OAuth 2.0 patterns)  
-- ✅ Implementation details (API security, JWT)
-- ✅ Platform specifics (mobile considerations)
```

### Quality Metrics

**Good Search Results**:
- **Relevance scores**: 0.4+ for valuable results
- **Coverage**: Multiple scopes (global → domain → specific)
- **Actionability**: Concrete implementation guidance
- **Completeness**: End-to-end task coverage

**Warning Signs**:
- **Single result**: Query too specific or knowledge gaps
- **Low relevance**: Terms don't match knowledge vocabulary
- **Off-topic results**: Query too generic or context issues

### Knowledge Gap Detection

If queries return insufficient results:

1. **Check terminology alignment**: Do query terms match context keywords?
2. **Verify scope inheritance**: Is target scope getting expected knowledge?
3. **Review threshold settings**: Are valuable results being filtered out?
4. **Assess knowledge coverage**: Are there gaps in the knowledge base?

## Examples

### Complete Implementation Scenario

**Task**: Implement shopping cart persistence with Redis

**Knowledge Entry**:
```sql
INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
(shopcraft_scope_id,
 'ShopCraft shopping cart persists across devices using Redis with 30-day expiration. Support guest checkout, saved items, and cart abandonment email campaigns.',
 'shopcraft shopping cart persistence redis cross device guest checkout saved items abandonment email expiration',
 'M');
```

**AI Query**:
```python
query_terms = [
    "shopping cart persistence",  # Core functionality
    "redis caching expiration",   # Technical implementation  
    "cross device session",       # User experience
    "email campaigns automation"  # Business features
]
```

**Expected Results**:
- ShopCraft cart persistence architecture
- Global Redis caching best practices  
- Session management patterns
- Email automation systems

This approach ensures comprehensive knowledge retrieval for complete feature implementation.