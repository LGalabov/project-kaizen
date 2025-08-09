# Project Kaizen - TODO

## MCP Tools — Missing Functionality

### 1. Knowledge Conflict Visibility
**Priority: Medium**
- `list_knowledge_conflicts(scope?: str)` - View all conflicts or filter by scope
- `get_conflict_details(conflict_id: int)` - Get details of a specific conflict
- `unresolve_conflict(conflict_id: int)` - Revert a conflict resolution

**Description**: Currently we can only create conflicts via `resolve_knowledge_conflict()`. There's no way to view existing conflicts, understand what's been suppressed, or undo a resolution if it was incorrect.

### 2. Knowledge Export/Import
**Priority: Low**
- `export_scope_knowledge(scope: str, format: 'json'|'csv')` - Export knowledge from a scope
- `import_scope_knowledge(scope: str, data: str, format: 'json'|'csv')` - Import knowledge

**Description**: Enable backup, migration between environments, and integration with external knowledge management systems.

### 3. Knowledge Statistics and Analytics
**Priority: Low**
- `get_namespace_stats(namespace: str)` - Knowledge count, task size distribution, etc.
- `get_scope_stats(scope: str)` - Detailed statistics for a scope
- `get_search_analytics()` - Most searched terms, search performance metrics

**Description**: Provide insights into knowledge base usage, growth patterns, and search effectiveness to guide optimization efforts.
