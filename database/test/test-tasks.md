# MCP Knowledge System Test Cases

## Database Function Testing Scenarios

These test cases are designed to thoroughly test the `get_task_context()` function and related MCP operations against the PostgreSQL knowledge database, focusing on scope inheritance, conflict resolution, NULL task_size handling, full-text search, and edge cases.

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

## Test Database Statistics
- **Total Knowledge Items**: 110 (100 original + 10 conflict items)
- **Active Knowledge Items**: 103 (7 suppressed by conflicts)
- **Conflict Records**: 7 (3 multi-level, 4 single-level)
- **NULL Task Size Items**: 25 (principles, guidelines, standards)
- **Sized Task Size Items**: 75 (actionable tasks)

## Test Case Categories

### 1. Enhanced Conflict Resolution Testing

#### Test 1.1: Multi-Level Conflict Resolution
**MCP Call**: 
```sql
SELECT * FROM get_task_context(
    ARRAY['testing', 'visual regression', 'percy'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should return only frontend-specific testing knowledge, with both ShopCraft default and global testing knowledge suppressed by conflict resolution.

**Expected Results (AI Agent Priority)**:
- `shopcraft:frontend-team`: "Frontend testing includes visual regression tests with Percy and accessibility audits for all components using axe-core and manual screen reader validation." (PRIORITY 1: Exact match for Percy visual regression)
- `global:default`: "Implement visual regression testing for UI components. Use tools like Percy or Chromatic to catch visual changes. Include cross-browser testing." (PRIORITY 2: Tool-specific guidance)
- `shopcraft:frontend-team`: "ShopCraft frontend uses React 18 with TypeScript, Material-UI components, and React Query for server state management. All components must be fully typed and include unit tests with Jest and React Testing Library." (PRIORITY 3: Testing framework context)
- `global:default`: "Test with actual screen readers and keyboard-only navigation. Include alt text for images, captions for videos, and proper color contrast ratios." (PRIORITY 4: Accessibility testing details)
- **Suppressed by conflict**: ShopCraft payment testing, Global TDD - correctly hidden
- **Not needed**: General testing principles, backend testing, unrelated coverage metrics

**Edge Case**: Tests 3-level conflict hierarchy where leaf scope wins over intermediate and root scopes

#### Test 1.2: Single-Level Conflict Verification
**MCP Call**:
```sql  
SELECT * FROM get_task_context(
    ARRAY['api', 'rate limiting', 'throttling'], 
    'shopcraft:default'
);
```
**Expected Behavior**: Should return ShopCraft-specific rate limiting (1000 req/min for premium) instead of global rate limiting (100 req/min), demonstrating namespace-level conflict resolution.

**Expected Results (AI Agent Priority)**:
- `shopcraft:default`: "ShopCraft API rate limiting: 1000 requests per minute for premium users, 100 for basic users, with Redis-based distributed throttling." (PRIORITY 1: Specific rate limits for implementation)
- `shopcraft:default`: "ShopCraft uses microservices architecture with React frontend, Node.js backend services, PostgreSQL database, and Redis for caching. All services communicate via REST APIs with JWT authentication." (PRIORITY 2: API architecture context)
- `shopcraft:backend-api`: "ShopCraft API uses Express.js with Helmet for security headers, compression middleware, and request logging with Winston. All endpoints require JWT authentication except health checks." (PRIORITY 3: Implementation details via inheritance)
- **Suppressed by conflict**: Global rate limiting (100/20 req/min) - correctly hidden
- **Implementation ready**: Specific numbers, Redis setup, authentication flow

**Edge Case**: Tests namespace vs global conflict resolution

#### Test 1.3: Suppressed Knowledge Exclusion
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['error handling', 'exceptions', 'correlation'], 
    'shopcraft:backend-api'
);
```
**Expected Behavior**: Should return backend-specific error handling with correlation IDs, while both ShopCraft default and global error handling remain suppressed.

**Expected Results (AI Agent Priority)**:
- `shopcraft:backend-api`: "Backend API errors include correlation IDs, structured logging, and circuit breaker patterns for handling external service failures and timeouts." (PRIORITY 1: Specific error handling patterns)
- `shopcraft:backend-api`: "ShopCraft API uses Express.js with Helmet for security headers, compression middleware, and request logging with Winston. All endpoints require JWT authentication except health checks." (PRIORITY 2: Related logging setup)
- `global:default`: "Never log sensitive data like passwords, API keys, or personal information. Use structured logging with appropriate log levels. Sanitize all log outputs." (PRIORITY 3: Security constraints)
- **Suppressed by conflict**: ShopCraft friendly errors, Global generic error handling
- **Implementation ready**: Correlation ID pattern, Winston logging, circuit breakers

**Edge Case**: Tests materialized view conflict filtering ensures suppressed items never appear

#### Test 1.4: Cross-Scope Conflict Resolution
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['deployment', 'canary', 'rollback'], 
    'shopcraft:devops-deploy'
);
```
**Expected Behavior**: Should return DevOps canary deployment strategy, with both ShopCraft default and global deployment strategies suppressed.

**Expected Results (AI Agent Priority)**:
- `shopcraft:devops-deploy`: "DevOps uses canary deployments with 5% traffic splits and automated rollback triggers based on error rate thresholds and performance metrics." (PRIORITY 1: Specific deployment strategy)
- `shopcraft:devops-deploy`: "ShopCraft monitoring uses Prometheus for metrics, Grafana for dashboards, and CloudWatch for AWS resources. Set up alerts for high CPU, memory usage, and API response times over 500 milliseconds." (PRIORITY 2: Monitoring for rollback triggers)
- `shopcraft:devops-deploy`: "ShopCraft CI/CD pipeline: GitHub Actions → Build Docker Images → Run Tests → Security Scanning → Deploy to Staging → Manual Approval → Deploy to Production." (PRIORITY 3: Deployment pipeline)
- **Suppressed by conflict**: ShopCraft customer notifications, Global blue-green deployments
- **Implementation ready**: 5% traffic split, error rate thresholds, automation triggers

**Edge Case**: Tests conflict resolution across different scope relationship types

#### Test 1.5: Conflict-Free Knowledge Coexistence
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['caching', 'redis', 'session'], 
    'shopcraft:default'
);
```
**Expected Behavior**: Should return both global caching strategies and ShopCraft-specific caching (with GDPR compliance), as they have been resolved to coexist without conflict.

**Expected Results**:
- `global:default`: "Implement caching strategies: use Redis for session data, cache frequently accessed data, implement cache invalidation policies. Monitor cache hit rates."
- `shopcraft:default`: "ShopCraft shopping cart persists across devices using Redis with 30-day expiration. Support guest checkout, saved items, and cart abandonment email campaigns."
- `shopcraft:default`: "ShopCraft inventory management uses real-time stock tracking with Redis. When stock falls below threshold, automatic purchase orders are created."
- **Additional context**: Related Redis usage in authentication, API architecture

**Edge Case**: Tests scenarios where similar knowledge coexists without conflict

### 2. Enhanced Task Size with NULL Handling

#### Test 2.1: NULL Inclusion with Minimum Filter
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['naming', 'conventions', 'variables'], 
    'global:default',
    'XS'::task_size_enum
);
```
**Expected Behavior**: Should return all knowledge items including NULL task_size items (principles) and all sized items, since XS is the minimum threshold.

**Expected Results (AI Agent Priority)**:
- `global:default`: "Use consistent naming conventions: PascalCase for classes, camelCase for functions/variables, UPPER_CASE for constants. Be descriptive but concise." (PRIORITY 1: Direct naming convention principles - NULL task_size included)
- `global:default`: "Use meaningful variable names that describe the data they hold. Avoid abbreviations and single-letter variables (except for loop counters)." (PRIORITY 2: Variable naming specifics - NULL task_size included)
- `global:default`: "JavaScript/TypeScript: Use strict mode, prefer const over let, use async/await over callbacks, implement proper type definitions in TypeScript." (PRIORITY 3: Language-specific conventions - NULL task_size)
- `global:default`: "Always use HTTPS for external API communications to prevent man-in-the-middle attacks. Configure SSL certificates properly and use TLS 1.2 or higher." (PRIORITY 4: XS task matches filter)
- **All task sizes included**: XS filter includes ALL sized tasks + NULL principles
- **Implementation ready**: Specific naming patterns, TypeScript practices, security requirements

**Edge Case**: Tests NULL task_size inclusion with lowest threshold filter

#### Test 2.2: NULL Inclusion with Maximum Filter
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['architecture', 'microservices', 'scalability'], 
    'shopcraft:default',
    'XL'::task_size_enum
);
```
**Expected Behavior**: Should return only XL tasks and NULL task_size items (architectural principles), excluding S, M, L tasks.

**Expected Results (AI Agent Priority)**:
- `shopcraft:default`: "ShopCraft uses microservices architecture with React frontend, Node.js backend services, PostgreSQL database, and Redis for caching. All services communicate via REST APIs with JWT authentication." (PRIORITY 1: Core architecture principle - NULL task_size included)
- `shopcraft:default`: "ShopCraft order management implements complex workflows: order validation, fraud detection, inventory reservation, payment authorization, fulfillment routing, and shipment tracking." (PRIORITY 2: XL complexity matches filter)
- `shopcraft:default`: "ShopCraft multi-vendor marketplace supports seller onboarding, commission calculations, payout scheduling, and vendor analytics dashboards." (PRIORITY 3: XL marketplace complexity)
- `global:default`: "Plan for scalability from the beginning. Design systems to handle growth in users, data, and features. Monitor performance trends." (PRIORITY 4: Architectural scalability principle - NULL task_size)
- **XL filter working**: Only XL tasks + NULL principles included, S/M/L tasks excluded
- **Implementation ready**: Architecture decisions, complex workflow patterns, scalability planning

**Edge Case**: Tests NULL task_size inclusion with highest threshold filter

#### Test 2.3: Mixed Results NULL and Sized Items
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['solid', 'principles', 'dependency injection'], 
    'shopcraft:backend-api',
    'M'::task_size_enum
);
```
**Expected Behavior**: Should return both NULL task_size principles (SOLID principles) and M/L/XL sized implementation tasks, demonstrating mixed result handling.

**Expected Results**:
- `global:default`: "Follow SOLID principles: Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. Design classes with single, well-defined purposes." (NULL task_size - principle)
- `global:default`: "Use dependency injection for loose coupling. Inject dependencies through constructors or setters rather than creating them internally. Makes testing easier." (M task_size)
- `shopcraft:backend-api`: "ShopCraft API uses Express.js with Helmet for security headers, compression middleware, and request logging with Winston. All endpoints require JWT authentication except health checks." (M task_size - matches "principles" via architecture principles)
- **Excluded**: Any S or XS tasks that might match the search terms

**Edge Case**: Tests mixture of principle-based (NULL) and implementation-based (sized) knowledge

#### Test 2.4: NULL vs Sized Conflict Resolution
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['design patterns', 'factory', 'strategy'], 
    'shopcraft:default'
);
```
**Expected Behavior**: Should handle conflicts between NULL task_size principles and sized implementation tasks appropriately based on scope hierarchy.

**Expected Results**:
- `global:default`: "Use design patterns appropriately: Factory for object creation, Observer for event handling, Strategy for algorithm selection, Repository for data access." (NULL task_size - principle)
- `global:default`: "Apply separation of concerns: keep business logic separate from presentation layer, data access layer separate from business logic. Use layered architecture." (NULL task_size - principle)
- `shopcraft:default`: Related architectural patterns in ShopCraft's microservices design and order processing workflows
- **No conflicts**: These design pattern principles coexist without conflict in the current sample data

**Edge Case**: Tests conflict resolution when NULL and sized items conflict

### 3. Scope Inheritance with Conflict Awareness

#### Test 3.1: Conflict-Aware Inheritance Traversal
**MCP Call**: 
```sql
SELECT * FROM get_task_context(
    ARRAY['database', 'connection', 'pooling'], 
    'shopcraft:backend-api'
);
```
**Expected Behavior**: Should traverse inheritance hierarchy but respect conflict resolution, returning backend-specific connection pooling while suppressing conflicting ShopCraft default database configuration.

**Expected Results**:
- `shopcraft:backend-api`: "Backend API requires dedicated connection pools per service with circuit breaker patterns for database failures and automatic failover mechanisms." (Winner in conflict)
- `shopcraft:backend-api`: "ShopCraft database uses PostgreSQL with connection pooling (max 20 connections). Implement read replicas for reporting queries. Use database transactions for multi-table operations."
- `global:default`: "Use database connection pooling with appropriate limits. Implement connection health checks, timeout configurations, and graceful degradation for database failures."
- **Suppressed by conflict**: ShopCraft default database configuration (general PostgreSQL setup) loses to backend-specific connection handling

**Edge Case**: Tests inheritance traversal with conflict filtering

#### Test 3.2: Multi-Scope Knowledge Aggregation
**MCP Call**:
```sql  
SELECT * FROM get_task_context(
    ARRAY['security', 'authentication', 'oauth'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should aggregate security knowledge from multiple scopes in inheritance chain while respecting conflict resolution and scope-specific specializations.

**Expected Results**:
- `shopcraft:default`: "ShopCraft user authentication supports OAuth social login, two-factor authentication, password reset flows, and account verification. Use JWT with refresh tokens."
- `shopcraft:default`: "ShopCraft social media integration includes sharing buttons, social login, customer reviews syndication, and influencer partnership tracking."
- `global:default`: "Implement OAuth 2.0 with PKCE for secure authentication flows. Use refresh tokens with proper rotation. Validate all redirect URLs against whitelist."
- `global:default`: "Always use HTTPS for external API communications to prevent man-in-the-middle attacks. Configure SSL certificates properly and use TLS 1.2 or higher."
- **Inheritance chain**: frontend-team → backend-api → default → global:default provides comprehensive security knowledge

**Edge Case**: Tests knowledge aggregation across inheritance with conflict awareness

#### Test 3.3: Scope Hierarchy with Suppressed Parents
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['logging', 'retention', 'cleanup'], 
    'shopcraft:devops-deploy'
);
```
**Expected Behavior**: Should return DevOps-specific logging strategy while ensuring suppressed global logging policies don't interfere with inheritance chain.

**Expected Results**:
- `shopcraft:devops-deploy`: "DevOps log management uses centralized ELK stack with 90-day retention and automated cleanup workflows for compliance and storage optimization." (Winner in conflict)
- `shopcraft:devops-deploy`: "ShopCraft backup strategy: PostgreSQL automated backups every 6 hours with 30-day retention. Redis persistence enabled. Application logs stored in CloudWatch with 90-day retention."
- `global:default`: "Implement comprehensive logging: application logs, access logs, error logs. Use structured logging formats like JSON for better parsing."
- **Suppressed by conflict**: Global logging retention policies (archive old logs, clean temporary files)

**Edge Case**: Tests inheritance when parent scope knowledge is suppressed by conflict

### 4. Full-Text Search Intelligence

#### Test 4.1: Conflict-Aware Multi-Term Search
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['javascript typescript async await', 'error handling exceptions'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should parse complex query terms and return conflict-resolved results, ensuring suppressed items don't appear even if they match search terms.

**Expected Results (AI Agent Priority)**:
- `global:default`: "JavaScript/TypeScript: Use strict mode, prefer const over let, use async/await over callbacks, implement proper type definitions in TypeScript." (PRIORITY 1: Exact match for "javascript typescript async await")
- `shopcraft:frontend-team`: "ShopCraft frontend uses React 18 with TypeScript, Material-UI components, and React Query for server state management. All components must be fully typed and include unit tests with Jest and React Testing Library." (PRIORITY 2: TypeScript + testing context)
- `global:default`: "React: Use functional components with hooks, implement proper key props for lists, use React.memo for performance optimization, handle loading and error states." (PRIORITY 3: Error handling in React context)
- `shopcraft:frontend-team`: "ShopCraft product catalog page implements infinite scrolling with virtualization for performance. Use React Window for large product lists. Implement skeleton loading states and error boundaries." (PRIORITY 4: Error boundaries implementation)
- **Conflict correctly applied**: Backend error handling suppressed, frontend error patterns prioritized
- **Multi-term matching**: JavaScript/TypeScript + async/await + error handling patterns combined

**Edge Case**: Tests full-text search with conflict filtering

#### Test 4.2: Context vs Content Weighting with Conflicts
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['git commit semantic versioning'], 
    'shopcraft:default'
);
```
**Expected Behavior**: Should weight context matches higher than content matches while ensuring conflict-suppressed items don't affect ranking.

**Expected Results**:
- `global:default`: "Git commit messages should follow semantic versioning: feat(scope): description for new features, fix(scope): description for bug fixes, docs: for documentation changes. Keep first line under 50 characters." (exact context match for "git commit semantic versioning")
- `global:default`: "Use semantic versioning (MAJOR.MINOR.PATCH) for releases. Increment MAJOR for breaking changes, MINOR for new features, PATCH for bug fixes. Tag releases in git." (matches "semantic versioning" and "git")
- **Ranking**: Context field matches should rank higher than content matches due to search vector weighting (context='A', content='B')

**Edge Case**: Tests search vector weighting algorithm with conflict awareness

#### Test 4.3: Search Ranking with Suppressed Items
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['mobile responsive design'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should return frontend-specific mobile design patterns while ensuring suppressed ShopCraft default mobile responsiveness doesn't appear in results.

**Expected Results**:
- `shopcraft:frontend-team`: "Frontend components use styled-components with custom breakpoint system and mobile-first responsive design patterns for optimal performance." (Winner in conflict - exact match for "mobile responsive design")
- `shopcraft:frontend-team`: "ShopCraft mobile responsiveness uses CSS Grid and Flexbox with breakpoints at 768 pixels and 1024 pixels. Touch targets must be minimum 44 pixels. Test on iOS Safari and Android Chrome." (matches "mobile responsive")
- `shopcraft:default`: "ShopCraft mobile app uses React Native with shared business logic. Implement push notifications, offline support, and native payment integrations." (matches "mobile")
- **Suppressed by conflict**: Any ShopCraft default mobile responsiveness knowledge that conflicts with frontend-specific patterns

**Edge Case**: Tests search result ranking when highly relevant items are suppressed

### 5. Error Handling and Edge Cases

#### Test 5.1: Non-existent Scope
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['test'], 
    'nonexistent:scope'
);
```
**Expected Behavior**: Should raise exception 'Scope not found: nonexistent:scope'

**Expected Results (AI Agent Priority)**:
- **ERROR**: PostgreSQL exception raised: "Scope not found: nonexistent:scope"
- **Fast failure**: Function immediately stops execution with clear diagnostic
- **AI-friendly error**: Specific scope name included for debugging
- **No partial results**: Clean failure state, no confusing mixed responses

**Edge Case**: Tests error handling for invalid scopes

#### Test 5.2: Empty Query Terms with Conflicts
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY[]::TEXT[], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should handle empty queries gracefully while maintaining conflict filtering

**Expected Results (AI Agent Priority)**:
- **Empty result set**: No knowledge returned (correct behavior for empty query)
- **No errors**: Function completes successfully without exceptions
- **Conflict system intact**: Materialized view filtering remains active for future queries
- **AI-friendly**: Clear empty response, not confusing partial matches

**Edge Case**: Tests empty input handling with conflict system active

#### Test 5.3: Low Relevance with Conflict Filtering
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['completely', 'unrelated', 'terminology'], 
    'shopcraft:backend-api'
);
```
**Expected Behavior**: Should return empty results if no active (non-suppressed) matches exceed relevance threshold

**Expected Results**:
- **Empty result set**: No knowledge items have sufficient relevance (rank >= 0.1) for these unrelated terms
- **Search attempted**: Full-text search executes but finds no meaningful matches
- **Conflict filtering bypassed**: No relevant items to filter, so conflict resolution doesn't apply
- **Threshold filtering**: PostgreSQL websearch_to_tsquery processes terms but no content matches sufficiently

**Edge Case**: Tests relevance filtering combined with conflict filtering

### 6. Advanced Real-World Scenarios

#### Test 6.1: Full-Stack Development with Conflicts
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['react components', 'api validation', 'database transactions'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should return conflict-resolved knowledge spanning frontend, backend, and database domains through inheritance, with specialized knowledge taking precedence.

**Expected Results (AI Agent Priority)**:
- `shopcraft:frontend-team`: "ShopCraft frontend uses React 18 with TypeScript, Material-UI components, and React Query for server state management. All components must be fully typed and include unit tests with Jest and React Testing Library." (PRIORITY 1: React components + testing)
- `global:default`: "React: Use functional components with hooks, implement proper key props for lists, use React.memo for performance optimization, handle loading and error states." (PRIORITY 2: React component patterns)
- `global:default`: "Validate all API inputs: required fields, data types, format constraints. Return clear error messages with field-specific validation failures." (PRIORITY 3: API validation for frontend-backend integration)
- `shopcraft:backend-api`: "ShopCraft database uses PostgreSQL with connection pooling (max 20 connections). Implement read replicas for reporting queries. Use database transactions for multi-table operations." (PRIORITY 4: Database transactions via inheritance)
- `global:default`: "Use database transactions for operations that modify multiple tables. Implement proper rollback mechanisms for failed operations." (PRIORITY 5: Transaction patterns)
- **Full-stack integration**: Frontend inherits backend/database knowledge for complete implementation context

**Integration Test**: Tests comprehensive knowledge retrieval with conflict resolution

#### Test 6.2: Security Compliance Multi-Scope Resolution
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['gdpr compliance', 'data encryption', 'audit logging'], 
    'shopcraft:backend-api'
);
```
**Expected Behavior**: Should aggregate security knowledge from global and ShopCraft scopes while respecting conflict resolution for conflicting guidance.

**Expected Results (AI Agent Priority)**:
- `shopcraft:default`: "ShopCraft customer data includes personal information, purchase history, and preferences. All customer data must be encrypted at rest and in transit. GDPR compliance required for EU customers." (PRIORITY 1: Direct GDPR + encryption requirements)
- `shopcraft:backend-api`: "Backend API errors include correlation IDs, structured logging, and circuit breaker patterns for handling external service failures and timeouts." (PRIORITY 2: Audit logging implementation)
- `global:default`: "Never log sensitive data like passwords, API keys, or personal information. Use structured logging with appropriate log levels. Sanitize all log outputs." (PRIORITY 3: Logging compliance constraints)
- `global:default`: "Always use HTTPS for external API communications to prevent man-in-the-middle attacks. Configure SSL certificates properly and use TLS 1.2 or higher." (PRIORITY 4: Data encryption in transit)
- `global:default`: "Use Content Security Policy (CSP) headers to prevent XSS attacks. Implement CSRF protection with tokens. Validate file uploads for malicious content." (PRIORITY 5: Additional security compliance)
- **Compliance-ready**: GDPR requirements, encryption standards, audit logging patterns, security headers

**Integration Test**: Tests compliance knowledge aggregation with conflict awareness

#### Test 6.3: Performance Optimization Hierarchy
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['performance optimization', 'caching strategies', 'database indexing'], 
    'shopcraft:backend-api'
);
```
**Expected Behavior**: Should return performance knowledge from inheritance hierarchy, with backend-specific optimizations taking precedence over general patterns.

**Expected Results**:
- `shopcraft:backend-api`: "ShopCraft database uses PostgreSQL with connection pooling (max 20 connections). Implement read replicas for reporting queries. Use database transactions for multi-table operations." (matches "database" optimization)
- `shopcraft:default`: "ShopCraft inventory management uses real-time stock tracking with Redis. When stock falls below threshold, automatic purchase orders are created. Stock levels are updated via webhook from warehouse system." (matches "caching strategies" through Redis)
- `shopcraft:default`: "ShopCraft shopping cart persists across devices using Redis with 30-day expiration. Support guest checkout, saved items, and cart abandonment email campaigns." (matches "caching strategies")
- `global:default`: "Optimize database queries: use indexes appropriately, avoid N+1 queries, implement pagination for large datasets. Monitor query performance regularly." (exact match for "database indexing")
- `global:default`: "Implement caching strategies: use Redis for session data, cache frequently accessed data, implement cache invalidation policies. Monitor cache hit rates." (exact match for "caching strategies")

**Integration Test**: Tests performance knowledge with scope specialization

### 7. Advanced Edge Cases

#### Test 7.1: Complex Conflict Chain Resolution
**MCP Call**:
```sql 
SELECT * FROM get_task_context(
    ARRAY['testing strategies', 'code coverage', 'integration tests'], 
    'shopcraft:frontend-team'
);
```
**Expected Behavior**: Should handle complex conflict chain where frontend testing overrides both ShopCraft and global testing strategies, returning only the most specific active knowledge.

**Expected Results**:
- `shopcraft:frontend-team`: "Frontend testing includes visual regression tests with Percy and accessibility audits for all components using axe-core and manual screen reader validation." (Winner in multi-level conflict chain)
- `shopcraft:frontend-team`: "ShopCraft frontend uses React 18 with TypeScript, Material-UI components, and React Query for server state management. All components must be fully typed and include unit tests with Jest and React Testing Library." (matches "testing strategies", "integration tests")
- **Suppressed by conflict**: 
  - ShopCraft default testing (payment flow integration tests with PCI compliance)
  - Global testing strategies (TDD, 80% code coverage, unit/integration/e2e test types)
- **Conflict chain**: Frontend → ShopCraft → Global, with frontend winning across all levels

**Edge Case**: Tests multi-level conflict chain resolution

#### Test 7.2: Mixed Task Size with Conflict Boundaries
**MCP Call**:
```sql
SELECT * FROM get_task_context(
    ARRAY['api design', 'rest', 'versioning'], 
    'shopcraft:default',
    'M'::task_size_enum
);
```
**Expected Behavior**: Should return M/L/XL tasks and NULL task_size items while respecting conflict boundaries, ensuring suppressed items don't appear regardless of task size match.

**Expected Results (AI Agent Priority)**:
- `shopcraft:default`: "ShopCraft API rate limiting: 1000 requests per minute for premium users, 100 for basic users, with Redis-based distributed throttling." (PRIORITY 1: M task_size, conflict winner, specific implementation details)
- `global:default`: "RESTful APIs should use appropriate HTTP methods: GET for retrieval, POST for creation, PUT for updates, DELETE for removal. Use proper status codes." (PRIORITY 2: NULL principle, REST design fundamentals)
- `global:default`: "Implement API versioning from the start. Use URL versioning (/api/v1/) or header versioning. Maintain backward compatibility when possible." (PRIORITY 3: NULL principle, versioning strategy)
- `global:default`: "API responses should be consistent in structure. Include metadata like pagination info, timestamps, and request IDs for debugging." (PRIORITY 4: NULL principle, response design)
- `shopcraft:default`: "ShopCraft uses microservices architecture with React frontend, Node.js backend services, PostgreSQL database, and Redis for caching. All services communicate via REST APIs with JWT authentication." (PRIORITY 5: NULL principle, API architecture context)
- **Task size filter working**: M/L/XL tasks + NULL principles included, XS/S excluded
- **Conflict boundaries respected**: Global rate limiting suppressed, ShopCraft rate limiting active
- **Implementation ready**: Specific rate limits, HTTP methods, versioning strategy, response structure

**Edge Case**: Tests task size filtering combined with conflict resolution

## Expected Query Performance Patterns

### Optimal Queries (Fast)
- Queries with specific, indexed terms on direct scopes
- Queries with appropriate task size filtering
- Queries against scopes with minimal conflict complexity

### Complex Queries (Functional but Slower)
- Multi-term searches across deep inheritance chains with conflicts
- Queries requiring extensive full-text search ranking with conflict filtering
- Queries spanning multiple knowledge domains with conflict resolution

### Edge Case Handling
- Invalid scopes should fail fast with clear errors
- Empty results should return gracefully with conflict filtering active
- Large result sets should be ranked appropriately with conflict resolution applied
- Conflict resolution should be transparent to query performance

## Test Data Coverage Verification

### Conflict Resolution Coverage
- **Multi-Level Conflicts**: 3 scenarios (frontend, backend, devops winners)
- **Single-Level Conflicts**: 4 scenarios (various scope relationships)
- **Suppressed Items**: 7 total items properly excluded from results
- **Active Items**: 103 items available for search and retrieval

### Task Size Distribution Coverage
- **NULL task_size**: 25 items (principles, guidelines, standards)
- **XS**: 1 item, **S**: 15 items, **M**: 33 items, **L**: 24 items, **XL**: 2 items
- **Size Filtering**: All thresholds tested with NULL inclusion verification

### Scope Hierarchy Coverage
- **Global Scope**: 68 active items (some suppressed by conflicts)
- **Namespace Scope**: 20 ShopCraft default items (some suppressed)
- **Project Scopes**: Frontend (6), Backend (6), DevOps (6) items each
- **Inheritance Chains**: All scope relationships tested with conflict awareness

This comprehensive test suite ensures thorough validation of the MCP knowledge system with conflict resolution, NULL task_size handling, and enhanced scope inheritance capabilities.
