# Project Kaizen MCP Server - Integration Test Plan

## Current Status: PHASE 1 COMPLETE ✅

**Integration test framework is fully operational:**
- ✅ **7 tests passing** (PostgreSQL + MCP client + framework validation)
- ✅ **MCP server connection verified** via FastMCP STDIO transport
- ✅ **All 12 MCP tools discoverable** via `list_tools()` protocol
- ✅ **Database isolation working** (clean database per test)
- ✅ **Architecture fixed** (proper `__main__.py` entry point)

**Ready for Phase 2:** Real MCP tool functionality testing with database validation.

## Overview

Complete integration test suite for all 12 MCP actions using **FastMCP Client** with real JSON-RPC protocol communication over STDIO transport. Tests PostgreSQL database integration, constraint validation, and MCP protocol compliance.

## Test Architecture (ACTUAL IMPLEMENTATION)

```
tests/
├── conftest.py                          # PostgreSQL + FastMCP fixtures ✅
└── test_framework_verification.py      # Framework validation tests ✅

# FUTURE STRUCTURE:
# tests/integration/
#     ├── test_mcp_namespace_tools.py   # 4 namespace MCP tools
#     ├── test_mcp_scope_tools.py       # 3 scope MCP tools  
#     ├── test_mcp_knowledge_tools.py   # 5 knowledge MCP tools
#     └── test_mcp_edge_cases.py        # Error handling & validation
```

## Dependencies

```toml
[tool.uv]
dev-dependencies = [
    "pytest>=8.3.5",
    "pytest-asyncio>=1.1.0",   # Updated to latest version
    "testcontainers[postgres]>=4.12.0",
    # fastmcp>=2.1.0 already in main dependencies
    # asyncpg>=0.30.0 already in main dependencies
]
```

## Implementation Steps

### Phase 1: Setup ✅ COMPLETED
- [x] Add test dependencies to `pyproject.toml` (pytest-asyncio 1.1.0, testcontainers[postgres] 4.12.0)
- [x] Create `conftest.py` with PostgreSQL container + FastMCP client fixtures
- [x] Schema loading implemented directly in conftest.py (no copy needed)
- [x] Database triggers create global namespace automatically (no test_data.sql needed)
- [x] Fix MCP server entry point (create `__main__.py`, refactor CLI logic from `__init__.py`)
- [x] Verify MCP client connection works (FastMCP STDIO transport with real protocol)
- [x] Verify test framework: **7 tests passing, 0 skipped, 0 failed**
- [x] Verify MCP tool discovery: All 12 tools discoverable via `list_tools()`

### Phase 2: MCP Tool Integration Tests 🔄 READY TO START
**Current Status: MCP server connection verified, all 12 tools discoverable**

#### Next Immediate Actions:
- [ ] Create first integration test: `test_create_namespace` with real MCP protocol
- [ ] Create second integration test: `test_get_namespaces` with database validation  
- [ ] Verify end-to-end flow: MCP call → Database changes → MCP response
- [ ] Test error scenarios (duplicates, invalid names, constraints)

### Phase 3: Scope Tools (Day 3)  
- [ ] Implement `test_mcp_scope_tools.py` with all 3 scope test cases
- [ ] Test scope hierarchy and parent relationships
- [ ] Test same-name scopes across different namespaces
- [ ] Test scope constraint violations

### Phase 4: Knowledge Tools (Day 4)
- [ ] Implement `test_mcp_knowledge_tools.py` with all 5 knowledge test cases
- [ ] Test complete CRUD workflow via MCP
- [ ] Test task context retrieval with multi-query
- [ ] Test knowledge conflict resolution

### Phase 5: Edge Cases & Validation (Day 5)
- [ ] Implement `test_mcp_edge_cases.py` with parameter validation
- [ ] Test MCP tool discovery (all 12 tools)
- [ ] Test error handling and exception propagation
- [ ] Run full test suite and verify coverage

---

## Complete Test Case Specifications

## 1. Namespace Management Tools (4 tools)

### get_namespaces

**Success Cases:**
```python
# Test Case 1.1: Get all namespaces (default style)
Input:  await mcp_client.call_tool("get_namespaces", {})
Output: {"namespaces": {"global": {"description": "..."}}}

# Test Case 1.2: Get namespaces with specific style
Input:  await mcp_client.call_tool("get_namespaces", {"style": "details"})
Output: {"namespaces": {"global": {"description": "...", "scopes": {"default": {"description": "...", "parents": []}}}}}

# Test Case 1.3: Filter by specific namespace
Input:  await mcp_client.call_tool("get_namespaces", {"namespace": "global"})
Output: {"namespaces": {"global": {"description": "..."}}}

# Test Case 1.4: Filter by non-existent namespace
Input:  await mcp_client.call_tool("get_namespaces", {"namespace": "does-not-exist"})
Output: {"namespaces": {}}
```

**Error Cases:**
```python
# Test Case 1.5: Invalid style parameter
Input:  await mcp_client.call_tool("get_namespaces", {"style": "invalid"})
Error:  ToolError - Invalid style parameter
```

### create_namespace

**Success Cases:**
```python
# Test Case 2.1: Create basic namespace
Input:  await mcp_client.call_tool("create_namespace", {"name": "test-project", "description": "Test project namespace"})
Output: {"name": "test-project", "description": "Test project namespace", "scopes": {"default": {"description": "..."}}}

# Test Case 2.2: Create namespace with special characters (allowed)
Input:  await mcp_client.call_tool("create_namespace", {"name": "test-project_v2", "description": "Test project v2"})
Output: {"name": "test-project_v2", "description": "Test project v2", "scopes": {"default": {"description": "..."}}}
```

**Error Cases:**
```python
# Test Case 2.3: Duplicate namespace creation
Input:  await mcp_client.call_tool("create_namespace", {"name": "duplicate", "description": "First"})
        await mcp_client.call_tool("create_namespace", {"name": "duplicate", "description": "Second"})
Error:  ToolError - Namespace already exists

# Test Case 2.4: Invalid namespace name (uppercase)
Input:  await mcp_client.call_tool("create_namespace", {"name": "InvalidName", "description": "Bad name"})
Error:  ToolError - Invalid namespace name format

# Test Case 2.5: Invalid namespace name (spaces)
Input:  await mcp_client.call_tool("create_namespace", {"name": "invalid name", "description": "Bad name"})
Error:  ToolError - Invalid namespace name format

# Test Case 2.6: Empty name
Input:  await mcp_client.call_tool("create_namespace", {"name": "", "description": "Empty name"})
Error:  ToolError - Name cannot be empty

# Test Case 2.7: Too long name (>100 chars)
Input:  await mcp_client.call_tool("create_namespace", {"name": "a" * 101, "description": "Too long"})
Error:  ToolError - Name too long
```

### update_namespace

**Success Cases:**
```python
# Test Case 3.1: Update namespace description only
Input:  await mcp_client.call_tool("update_namespace", {"name": "test-project", "description": "Updated description"})
Output: {"name": "test-project", "description": "Updated description", "scopes": {...}}

# Test Case 3.2: Update namespace name only
Input:  await mcp_client.call_tool("update_namespace", {"name": "test-project", "new_name": "renamed-project"})
Output: {"name": "renamed-project", "description": "...", "scopes": {...}}

# Test Case 3.3: Update both name and description
Input:  await mcp_client.call_tool("update_namespace", {"name": "test-project", "new_name": "new-project", "description": "New description"})
Output: {"name": "new-project", "description": "New description", "scopes": {...}}
```

**Error Cases:**
```python
# Test Case 3.4: Update non-existent namespace
Input:  await mcp_client.call_tool("update_namespace", {"name": "does-not-exist", "description": "Update"})
Error:  ToolError - Namespace not found

# Test Case 3.5: Rename to existing namespace
Input:  await mcp_client.call_tool("update_namespace", {"name": "project1", "new_name": "project2"})  # project2 exists
Error:  ToolError - Namespace name already exists

# Test Case 3.6: Invalid new name format
Input:  await mcp_client.call_tool("update_namespace", {"name": "test-project", "new_name": "Invalid Name!"})
Error:  ToolError - Invalid namespace name format
```

### delete_namespace

**Success Cases:**
```python
# Test Case 4.1: Delete namespace with only default scope
Input:  await mcp_client.call_tool("delete_namespace", {"name": "empty-namespace"})
Output: {"name": "empty-namespace", "scopes_count": 1, "knowledge_count": 0}

# Test Case 4.2: Delete namespace with multiple scopes and knowledge (cascade)
Input:  await mcp_client.call_tool("delete_namespace", {"name": "complex-namespace"})
Output: {"name": "complex-namespace", "scopes_count": 3, "knowledge_count": 5}
```

**Error Cases:**
```python
# Test Case 4.3: Delete non-existent namespace
Input:  await mcp_client.call_tool("delete_namespace", {"name": "does-not-exist"})
Error:  ToolError - Namespace not found

# Test Case 4.4: Delete global namespace (protected)
Input:  await mcp_client.call_tool("delete_namespace", {"name": "global"})
Error:  ToolError - Cannot delete global namespace
```

## 2. Scope Management Tools (3 tools)

### create_scope

**Success Cases:**
```python
# Test Case 5.1: Create scope with default parent only
Input:  await mcp_client.call_tool("create_scope", {"scope": "test-ns:frontend", "description": "Frontend team scope", "parents": None})
Output: {"scope": "test-ns:frontend", "description": "Frontend team scope", "parents": ["test-ns:default"]}

# Test Case 5.2: Create scope with explicit parents
Input:  await mcp_client.call_tool("create_scope", {"scope": "test-ns:mobile-frontend", "description": "Mobile frontend", "parents": ["test-ns:frontend", "test-ns:mobile"]})
Output: {"scope": "test-ns:mobile-frontend", "description": "Mobile frontend", "parents": ["test-ns:frontend", "test-ns:mobile", "test-ns:default"]}

# Test Case 5.3: Same scope name in different namespaces (should work)
Input:  await mcp_client.call_tool("create_scope", {"scope": "ns1:frontend", "description": "NS1 Frontend", "parents": None})
        await mcp_client.call_tool("create_scope", {"scope": "ns2:frontend", "description": "NS2 Frontend", "parents": None})
Output: Both succeed with different fully-qualified scope names
```

**Error Cases:**
```python
# Test Case 5.4: Duplicate scope in same namespace
Input:  await mcp_client.call_tool("create_scope", {"scope": "test-ns:duplicate", "description": "First", "parents": None})
        await mcp_client.call_tool("create_scope", {"scope": "test-ns:duplicate", "description": "Second", "parents": None})
Error:  ToolError - Scope already exists in namespace

# Test Case 5.5: Invalid scope format (no colon)
Input:  await mcp_client.call_tool("create_scope", {"scope": "invalid-format", "description": "Bad format", "parents": None})
Error:  ToolError - Invalid scope format, must be namespace:scope

# Test Case 5.6: Non-existent namespace
Input:  await mcp_client.call_tool("create_scope", {"scope": "does-not-exist:scope", "description": "No namespace", "parents": None})
Error:  ToolError - Namespace does not exist

# Test Case 5.7: Non-existent parent scope
Input:  await mcp_client.call_tool("create_scope", {"scope": "test-ns:child", "description": "Child scope", "parents": ["test-ns:non-existent"]})
Error:  ToolError - Parent scope does not exist

# Test Case 5.8: Circular dependency in parents
Input:  await mcp_client.call_tool("create_scope", {"scope": "test-ns:parent", "description": "Parent", "parents": ["test-ns:child"]})
Error:  ToolError - Circular dependency detected
```

### update_scope

**Success Cases:**
```python
# Test Case 6.1: Update scope description only
Input:  await mcp_client.call_tool("update_scope", {"scope": "test-ns:frontend", "description": "Updated frontend description"})
Output: {"scope": "test-ns:frontend", "description": "Updated frontend description", "parents": [...]}

# Test Case 6.2: Update scope name
Input:  await mcp_client.call_tool("update_scope", {"scope": "test-ns:frontend", "new_scope": "test-ns:ui-team"})
Output: {"scope": "test-ns:ui-team", "description": "...", "parents": [...]}

# Test Case 6.3: Update parent relationships
Input:  await mcp_client.call_tool("update_scope", {"scope": "test-ns:frontend", "parents": ["test-ns:engineering"]})
Output: {"scope": "test-ns:frontend", "description": "...", "parents": ["test-ns:engineering", "test-ns:default"]}
```

**Error Cases:**
```python
# Test Case 6.4: Update non-existent scope
Input:  await mcp_client.call_tool("update_scope", {"scope": "test-ns:does-not-exist", "description": "Update"})
Error:  ToolError - Scope not found

# Test Case 6.5: Rename to existing scope
Input:  await mcp_client.call_tool("update_scope", {"scope": "test-ns:scope1", "new_scope": "test-ns:scope2"})  # scope2 exists
Error:  ToolError - Scope name already exists

# Test Case 6.6: Update default scope (protected)
Input:  await mcp_client.call_tool("update_scope", {"scope": "test-ns:default", "new_scope": "test-ns:renamed-default"})
Error:  ToolError - Cannot rename default scope
```

### delete_scope

**Success Cases:**
```python
# Test Case 7.1: Delete scope with no knowledge entries
Input:  await mcp_client.call_tool("delete_scope", {"scope": "test-ns:empty-scope"})
Output: {"scope": "test-ns:empty-scope", "knowledge_deleted": 0}

# Test Case 7.2: Delete scope with knowledge entries (cascade)
Input:  await mcp_client.call_tool("delete_scope", {"scope": "test-ns:scope-with-knowledge"})
Output: {"scope": "test-ns:scope-with-knowledge", "knowledge_deleted": 3}
```

**Error Cases:**
```python
# Test Case 7.3: Delete non-existent scope
Input:  await mcp_client.call_tool("delete_scope", {"scope": "test-ns:does-not-exist"})
Error:  ToolError - Scope not found

# Test Case 7.4: Delete default scope (protected)
Input:  await mcp_client.call_tool("delete_scope", {"scope": "test-ns:default"})
Error:  ToolError - Cannot delete default scope

# Test Case 7.5: Delete scope that is a parent of other scopes
Input:  await mcp_client.call_tool("delete_scope", {"scope": "test-ns:parent-scope"})  # has children
Error:  ToolError - Cannot delete scope with child scopes
```

## 3. Knowledge Management Tools (5 tools)

### write_knowledge

**Success Cases:**
```python
# Test Case 8.1: Write knowledge to default scope
Input:  await mcp_client.call_tool("write_knowledge", {"scope": "test-ns:default", "content": "Test knowledge content", "context": "test context tags"})
Output: {"id": "K7H9M2PQX8", "scope": "test-ns:default"}

# Test Case 8.2: Write knowledge to custom scope
Input:  await mcp_client.call_tool("write_knowledge", {"scope": "test-ns:frontend", "content": "Frontend specific knowledge", "context": "frontend react javascript"})
Output: {"id": "K9L2X6VB43", "scope": "test-ns:frontend"}

# Test Case 8.3: Write knowledge with rich context
Input:  await mcp_client.call_tool("write_knowledge", {"scope": "test-ns:backend", "content": "API authentication patterns", "context": "api auth jwt oauth security backend nodejs express"})
Output: {"id": "G3K7R4NXL9", "scope": "test-ns:backend"}
```

**Error Cases:**
```python
# Test Case 8.4: Write to non-existent scope
Input:  await mcp_client.call_tool("write_knowledge", {"scope": "does-not-exist:scope", "content": "Content", "context": "context"})
Error:  ToolError - Scope does not exist

# Test Case 8.5: Empty content
Input:  await mcp_client.call_tool("write_knowledge", {"scope": "test-ns:default", "content": "", "context": "empty content"})
Error:  ToolError - Content cannot be empty

# Test Case 8.6: Empty context
Input:  await mcp_client.call_tool("write_knowledge", {"scope": "test-ns:default", "content": "Some content", "context": ""})
Error:  ToolError - Context cannot be empty
```

### update_knowledge

**Success Cases:**
```python
# Test Case 9.1: Update content only
Input:  await mcp_client.call_tool("update_knowledge", {"id": "K7H9M2PQX8", "content": "Updated knowledge content"})
Output: {"id": "K7H9M2PQX8", "scope": "test-ns:default"}

# Test Case 9.2: Update context only
Input:  await mcp_client.call_tool("update_knowledge", {"id": "K7H9M2PQX8", "context": "updated context tags"})
Output: {"id": "K7H9M2PQX8", "scope": "test-ns:default"}

# Test Case 9.3: Move knowledge to different scope
Input:  await mcp_client.call_tool("update_knowledge", {"id": "K7H9M2PQX8", "scope": "test-ns:frontend"})
Output: {"id": "K7H9M2PQX8", "scope": "test-ns:frontend"}

# Test Case 9.4: Update all fields
Input:  await mcp_client.call_tool("update_knowledge", {"id": "K7H9M2PQX8", "content": "New content", "context": "new context", "scope": "test-ns:backend"})
Output: {"id": "K7H9M2PQX8", "scope": "test-ns:backend"}
```

**Error Cases:**
```python
# Test Case 9.5: Update non-existent knowledge
Input:  await mcp_client.call_tool("update_knowledge", {"id": "DOES-NOT-EXIST", "content": "Update"})
Error:  ToolError - Knowledge entry not found

# Test Case 9.6: Move to non-existent scope
Input:  await mcp_client.call_tool("update_knowledge", {"id": "K7H9M2PQX8", "scope": "does-not-exist:scope"})
Error:  ToolError - Target scope does not exist

# Test Case 9.7: Invalid knowledge ID format
Input:  await mcp_client.call_tool("update_knowledge", {"id": "invalid-id", "content": "Update"})
Error:  ToolError - Invalid knowledge ID format
```

### delete_knowledge

**Success Cases:**
```python
# Test Case 10.1: Delete existing knowledge
Input:  await mcp_client.call_tool("delete_knowledge", {"id": "K7H9M2PQX8"})
Output: {"id": "K7H9M2PQX8"}
```

**Error Cases:**
```python
# Test Case 10.2: Delete non-existent knowledge
Input:  await mcp_client.call_tool("delete_knowledge", {"id": "DOES-NOT-EXIST"})
Error:  ToolError - Knowledge entry not found

# Test Case 10.3: Invalid knowledge ID format
Input:  await mcp_client.call_tool("delete_knowledge", {"id": "invalid-id"})
Error:  ToolError - Invalid knowledge ID format
```

### resolve_knowledge_conflict

**Success Cases:**
```python
# Test Case 11.1: Resolve conflict with single suppressed entry
Input:  await mcp_client.call_tool("resolve_knowledge_conflict", {"active_id": "K7H9M2PQX8", "suppressed_ids": ["G3K7R4NXL9"]})
Output: {"active_id": "K7H9M2PQX8", "suppressed_ids": ["G3K7R4NXL9"]}

# Test Case 11.2: Resolve conflict with multiple suppressed entries
Input:  await mcp_client.call_tool("resolve_knowledge_conflict", {"active_id": "K7H9M2PQX8", "suppressed_ids": ["G3K7R4NXL9", "J9L2X6VB43"]})
Output: {"active_id": "K7H9M2PQX8", "suppressed_ids": ["G3K7R4NXL9", "J9L2X6VB43"]}
```

**Error Cases:**
```python
# Test Case 11.3: Non-existent active knowledge
Input:  await mcp_client.call_tool("resolve_knowledge_conflict", {"active_id": "DOES-NOT-EXIST", "suppressed_ids": ["G3K7R4NXL9"]})
Error:  ToolError - Active knowledge entry not found

# Test Case 11.4: Non-existent suppressed knowledge
Input:  await mcp_client.call_tool("resolve_knowledge_conflict", {"active_id": "K7H9M2PQX8", "suppressed_ids": ["DOES-NOT-EXIST"]})
Error:  ToolError - Suppressed knowledge entry not found

# Test Case 11.5: Empty suppressed list
Input:  await mcp_client.call_tool("resolve_knowledge_conflict", {"active_id": "K7H9M2PQX8", "suppressed_ids": []})
Error:  ToolError - Must specify at least one suppressed entry

# Test Case 11.6: Active ID in suppressed list
Input:  await mcp_client.call_tool("resolve_knowledge_conflict", {"active_id": "K7H9M2PQX8", "suppressed_ids": ["K7H9M2PQX8"]})
Error:  ToolError - Active ID cannot be in suppressed list
```

### get_task_context

**Success Cases:**
```python
# Test Case 12.1: Single query with scope
Input:  await mcp_client.call_tool("get_task_context", {"queries": ["API authentication"], "scope": "test-ns:backend", "task_size": "medium"})
Output: {"results": {"test-ns:backend": {"K7H9M2PQX8": "API auth knowledge..."}, "test-ns:default": {...}, "global:default": {...}}}

# Test Case 12.2: Multiple queries with scope hierarchy
Input:  await mcp_client.call_tool("get_task_context", {"queries": ["react components", "state management"], "scope": "test-ns:frontend", "task_size": "large"})
Output: {"results": {"test-ns:frontend": {...}, "test-ns:default": {...}, "global:default": {...}}}

# Test Case 12.3: Queries without scope (defaults to global:default)
Input:  await mcp_client.call_tool("get_task_context", {"queries": ["git workflow"], "task_size": "small"})
Output: {"results": {"global:default": {"G3K7R4NXL9": "Git workflow knowledge..."}}}

# Test Case 12.4: No matching knowledge
Input:  await mcp_client.call_tool("get_task_context", {"queries": ["non-existent-topic"], "scope": "test-ns:default"})
Output: {"results": {}}
```

**Error Cases:**
```python
# Test Case 12.5: Empty queries list
Input:  await mcp_client.call_tool("get_task_context", {"queries": [], "scope": "test-ns:default"})
Error:  ToolError - Must provide at least one query

# Test Case 12.6: Non-existent scope
Input:  await mcp_client.call_tool("get_task_context", {"queries": ["test"], "scope": "does-not-exist:scope"})
Error:  ToolError - Scope does not exist

# Test Case 12.7: Invalid task size
Input:  await mcp_client.call_tool("get_task_context", {"queries": ["test"], "task_size": "invalid"})
Error:  ToolError - Invalid task size, must be XS, S, M, L, or XL
```

## 4. Edge Cases and Validation

### MCP Protocol Validation

**Test Cases:**
```python
# Test Case 13.1: Tool Discovery
Input:  tools = await mcp_client.list_tools()
Output: 12 tools with correct names and annotations

# Test Case 13.2: Missing required parameters
Input:  await mcp_client.call_tool("create_namespace", {"description": "Missing name"})
Error:  ToolError - Missing required parameter: name

# Test Case 13.3: Extra unexpected parameters
Input:  await mcp_client.call_tool("create_namespace", {"name": "test", "description": "test", "extra": "unexpected"})
Output: Success (extra parameters ignored)

# Test Case 13.4: Wrong parameter types
Input:  await mcp_client.call_tool("create_namespace", {"name": 123, "description": "test"})
Error:  ToolError - Parameter type error
```

### Database Constraint Validation

**Test Cases:**
```python
# Test Case 14.1: Unique constraints work correctly
# Test Case 14.2: Foreign key constraints prevent orphaned data
# Test Case 14.3: NOT NULL constraints enforced
# Test Case 14.4: Check constraints validate data format
# Test Case 14.5: Cascade deletes work correctly
```

### Error Handling

**Test Cases:**
```python
# Test Case 15.1: Database connection failures
# Test Case 15.2: Transaction rollback on errors
# Test Case 15.3: Proper error messages and codes
# Test Case 15.4: Exception propagation through MCP protocol
```

## What NOT to Test (Avoid Witch Hunts)

### ❌ Skip These Over-Complicated Tests:
1. **Performance benchmarking** - Not needed for correctness
2. **Load testing** - Not integration test scope
3. **Security penetration testing** - Different test category
4. **Cross-browser compatibility** - Not applicable to MCP server
5. **Memory leak testing** - Different test category
6. **Stress testing with thousands of entries** - Different test scope
7. **Testing every possible parameter combination** - Focus on key scenarios
8. **Mocking FastMCP internals** - We want real protocol testing
9. **Testing PostgreSQL's internal functionality** - Trust the database
10. **UI/UX testing** - No UI in MCP server

### ✅ Focus on These Essential Tests:
1. **Real MCP protocol communication** via FastMCP Client
2. **Database constraint validation** (unique, foreign key, cascade)
3. **Business logic correctness** for all 12 tools
4. **Error handling and validation** for edge cases
5. **Tool discovery and parameter validation**
6. **Scope hierarchy and inheritance** behavior
7. **Knowledge conflict resolution** mechanics

## Success Criteria

- ✅ All 12 MCP tools tested via real JSON-RPC protocol
- ✅ 85+ test cases covering success and error scenarios
- ✅ PostgreSQL constraints and cascade behaviors validated
- ✅ Error handling and exception propagation verified
- ✅ Complete test suite runs in under 60 seconds
- ✅ 100% confidence in MCP protocol compliance
- ✅ Ready for CI/CD integration

---

**Total Estimated Effort: 5 days**
**Expected Test Count: ~85 test cases**
**Coverage: All 12 MCP tools + edge cases + validation**