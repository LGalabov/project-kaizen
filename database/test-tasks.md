# MCP Knowledge System Test Cases

## Database Function Testing Scenarios

These test cases are designed to thoroughly test the `get_task_context()` function and related MCP operations against the PostgreSQL knowledge database, focusing on scope inheritance, full-text search, and edge cases.

## Core MCP Function Under Test

```sql
get_task_context(
    query_terms TEXT[],
    target_scope TEXT,
    filter_task_size task_size_enum DEFAULT NULL
) RETURNS TABLE (
    qualified_scope_name TEXT,
    knowledge_id BIGINT,
    content TEXT
)
```

## Test Case Categories

### 1. Scope Inheritance Chain Testing

#### Test 1.1: Multi-Level Inheritance Traversal
**MCP Call**: 
```sql
SELECT * FROM get_task_context(
    ARRAY['typescript', 'react', 'payment'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should retrieve knowledge from:
- `shopcraft:frontend-team` (direct scope)
- `shopcraft:backend-api` (parent scope)
- `shopcraft:default` (namespace default)
- `global:default` (ultimate parent)

**Edge Case**: Tests that scope inheritance follows the hierarchy correctly

#### Test 1.2: Orphaned Scope Access
**MCP Call**:
```sql  
SELECT * FROM get_task_context(
    ARRAY['security', 'api'], 
    'shopcraft:devops-deploy'
);
```
**Expected Behavior**: Should access knowledge from `devops-deploy` → `backend-api` → `shopcraft:default` → `global:default`

**Edge Case**: Tests indirect inheritance through multiple parent relationships

#### Test 1.3: Direct vs Inherited Knowledge Priority
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['database', 'optimization'], 
    'shopcraft:backend-api'
);
```
**Expected Behavior**: Should return results ranked by relevance, but scope-specific knowledge should have contextual priority

**Edge Case**: Tests ranking algorithm between direct and inherited knowledge

### 2. Full-Text Search Edge Cases

#### Test 2.1: Complex Multi-Term Search
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['javascript typescript async await', 'error handling exceptions'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should use `websearch_to_tsquery` to parse complex query terms and find relevant matches across multiple knowledge items

**Edge Case**: Tests full-text search parsing and multi-term relevance

#### Test 2.2: Search with Partial Matches
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['secur*', 'perform*'], 
    'global:default'
);
```
**Expected Behavior**: Should handle wildcard searches and partial matching in search vectors

**Edge Case**: Tests search flexibility and stemming

#### Test 2.3: Search Ranking with Context vs Content Weighting
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['git commit semantic'], 
    'shopcraft:default'
);
```
**Expected Behavior**: Should return results where context matches are weighted higher (A) than content matches (B)

**Edge Case**: Tests search vector weighting algorithm

### 3. Task Size Filtering

#### Test 3.1: Task Size Hierarchy Filtering
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['deployment', 'kubernetes'], 
    'shopcraft:devops-deploy',
    'M'::task_size_enum
);
```
**Expected Behavior**: Should return only tasks of size 'M', 'L', 'XL' (>= M) and NULL task sizes

**Edge Case**: Tests task size enum comparison logic

#### Test 3.2: Minimum Threshold Edge Case
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['naming', 'conventions'], 
    'global:default',
    'XS'::task_size_enum
);
```
**Expected Behavior**: Should return all knowledge items since XS is the minimum size

**Edge Case**: Tests lower bound filtering

#### Test 3.3: Maximum Threshold Edge Case
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['architecture', 'microservices'], 
    'shopcraft:default',
    'XL'::task_size_enum
);
```
**Expected Behavior**: Should return only XL tasks and NULL task sizes

**Edge Case**: Tests upper bound filtering and NULL handling

### 4. Knowledge Collision Resolution

#### Test 4.1: Active vs Suppressed Knowledge
**Setup**: Insert conflicting knowledge and create collision record
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['collision', 'test'], 
    'shopcraft:default'
);
```
**Expected Behavior**: Should only return active knowledge, not suppressed items

**Edge Case**: Tests materialized view collision filtering

#### Test 4.2: Collision Resolution Across Scopes
**Setup**: Create collisions at different scope levels
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['conflicted', 'knowledge'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should resolve collisions consistently across inheritance chain

**Edge Case**: Tests collision resolution in hierarchical contexts

### 5. Materialized View Performance

#### Test 5.1: Large Dataset Search Performance
**MCP Call**:
```sql 
SELECT * FROM get_task_context(
    ARRAY['performance', 'optimization', 'database', 'caching'], 
    'shopcraft:backend-api'
);
```
**Expected Behavior**: Should return results efficiently using GIN indexes on search vectors

**Edge Case**: Tests query performance with multiple terms and large datasets

#### Test 5.2: Scope Name Changes Propagation
**Setup**: Update scope or namespace names
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['updated', 'scope'], 
    'renamed-namespace:renamed-scope'
);
```
**Expected Behavior**: Should reflect updated names after materialized view refresh

**Edge Case**: Tests materialized view refresh triggers

### 6. Error Handling and Edge Cases

#### Test 6.1: Non-existent Scope
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['test'], 
    'nonexistent:scope'
);
```
**Expected Behavior**: Should raise exception 'Scope not found: nonexistent:scope'

**Edge Case**: Tests error handling for invalid scopes

#### Test 6.2: Empty Query Terms
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY[]::TEXT[], 
    'global:default'
);
```
**Expected Behavior**: Should handle empty query gracefully

**Edge Case**: Tests empty input handling

#### Test 6.3: Low Relevance Threshold
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['completely', 'unrelated', 'terms'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should return empty results if no matches exceed rank threshold (0.1)

**Edge Case**: Tests relevance filtering

### 7. Complex Real-World Scenarios

#### Test 7.1: Cross-Domain Architecture Query
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['solid principles', 'design patterns', 'order processing'], 
    'shopcraft:backend-api'
);
```
**Expected Behavior**: Should return architectural guidance from multiple knowledge domains

**Integration Test**: Tests knowledge integration across global patterns and domain specifics

#### Test 7.2: Security Compliance Multi-Scope Query
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['gdpr compliance', 'encryption', 'api security'], 
    'shopcraft:default'
);
```
**Expected Behavior**: Should aggregate security knowledge from global and ShopCraft-specific scopes

**Integration Test**: Tests compliance knowledge aggregation

#### Test 7.3: Full-Stack Development Query
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['react typescript', 'api integration', 'database transactions'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should return knowledge spanning frontend, backend, and database domains through inheritance

**Integration Test**: Tests comprehensive full-stack knowledge retrieval

## Expected Query Performance Patterns

### Optimal Queries (Fast)
- Queries with specific, indexed terms
- Queries against direct scopes with minimal inheritance
- Queries with appropriate task size filtering

### Complex Queries (Slower but Functional)
- Multi-term searches across deep inheritance chains
- Queries requiring extensive full-text search ranking
- Queries spanning multiple knowledge domains

### Edge Case Handling
- Invalid scopes should fail fast with clear errors
- Empty results should return gracefully
- Large result sets should be ranked appropriately

## Test Data Requirements

The sample data provides **100 knowledge items** across:
- **Global standards** (50+ items): Security, git, patterns, performance, testing, quality, APIs, monitoring, languages, DevOps, collaboration, maintenance
- **ShopCraft domain** (50+ items): Architecture, payments, inventory, customer data, frontend, backend, DevOps operations

This comprehensive dataset ensures thorough testing of all MCP knowledge retrieval scenarios and edge cases.

