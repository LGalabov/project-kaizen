# Kaizen Solution Specifications

## Revolutionary 3-Endpoint Design

Based on research into minimal APIs, neural network-like knowledge systems, and AI-driven knowledge application patterns.

## Core Architecture

### **Tag-Based Organization (No Rigid Hierarchies)**
Knowledge organized through emergent tagging patterns:
- `#general` - Universal knowledge across all work
- `#project-{name}` - Project-specific knowledge  
- `#domain-{area}` - Cross-project domain knowledge (auth, mobile, backend)
- `#pattern-{type}` - Reusable patterns and solutions
- `#company` - Organization-wide knowledge

Tags create flexible, multi-dimensional relationships without hierarchy constraints.

### **Neural Network-Like Behavior**
- **Associative connections** between related knowledge
- **Strength-based relationships** that grow through usage
- **Emergent patterns** discovered through AI analysis
- **Context-aware retrieval** based on current work
- **Learning from outcomes** to improve future suggestions

## MCP Tool Specification - MVP v1

**Design Principles**: Single-purpose, AI-friendly, self-explanatory tools that eliminate the need for extensive documentation. Each tool name clearly indicates its function and expected behavior.

### **Final Agreed Endpoint: `get_task_context`**

**Purpose**: Provides AI agents with essential knowledge for 99% task success rate before execution.

**Workflow Integration**: 
1. AI receives task prompt
2. AI extracts essence and calls `get_task_context`
3. AI executes task with strict adherence to returned context
4. Cycle repeats for next task

**Input Schema**:
```json
{
  "keywords": ["authentication", "oauth", "mobile", "security"],
  "context": {
    "project": "ecommerce-mobile",
    "technology": ["react-native", "nodejs"]
  }
}
```

**Output Schema**:
```json
{
  "context": [
    "MUST use PKCE for mobile OAuth security in this project",
    "Handle deep linking for OAuth callback in React Native",
    "Test authentication flow on both iOS and Android platforms",
    "Use project's existing token storage pattern from /src/auth/tokens.js"
  ]
}
```

**Schema Design Decisions**:

**Keywords Definition**: Task domain concepts and actions extracted from user prompt
- Examples: `["authentication", "oauth", "mobile", "user-login", "database-migration"]`
- Rule: If it describes WHAT needs to be done → keywords

**Context Definition**: Execution environment that modifies task approach  
- `project`: Working directory name or user-provided project identifier
- `technology`: Tech stack array that fundamentally changes implementation approach
- Rule: If it describes WHERE/HOW task is executed → context

**Boundary Rules**:
- Technology stacks go in `context.technology`, not keywords
- Project names always go in `context.project` 
- Task-specific concerns go in keywords
- Environment details (dev/prod) go in keywords if relevant

**API Contract Principles**:
- **Bounded Schema**: Only predefined context keys accepted
- **Version Evolution**: New context fields require schema version updates
- **Strict Validation**: Invalid context keys rejected
- **Consistent Usage**: Clear rules prevent AI agent confusion

**Extension Strategy**: Future context fields added through deliberate schema versioning when proven necessary.

### **Final Agreed Endpoint: `save_knowledge`**

**Purpose**: User-governed knowledge storage with intelligent upsert capability for incremental knowledge building.

**User-Governance Workflow**:
1. AI suggests knowledge worth saving OR user explicitly provides knowledge
2. User approves/refines content 
3. AI extracts keywords and makes MCP call
4. Knowledge immediately available via `get_task_context`

**Input Schema**:
```json
{
  "content": "OAuth redirect fails on iOS simulator - fixed with custom URL scheme handler in AppDelegate",
  "keywords": ["oauth", "ios", "redirect", "bug-fix", "react-native"],
  "context": {
    "project": "ecommerce-mobile",
    "technology": ["react-native"]
  }
}
```

**Output Schema**:
```json
{
  "status": "created|updated|merged"
}
```

**Schema Design Decisions**:

**Content Field**: Simple string containing the knowledge statement after user approval/refinement
- Single facts: "Always use PKCE for mobile OAuth security"
- Complex knowledge: "Problem X occurred, fixed with solution Y, outcome was Z"
- User-refined content ready for storage

**Keywords/Context Reuse**: Same boundary rules as `get_task_context`
- Keywords: WHAT the knowledge is about
- Context: WHERE/HOW it applies (project + technology only)

**Intelligent Upsert Operation**: 
- Server checks if similar knowledge exists via semantic matching
- If exists: merges/updates intelligently based on keywords + content similarity
- If new: creates fresh knowledge with auto-generated relationships
- Returns status indicating what actually happened

**Incremental Knowledge Building**:
- Multiple `save_knowledge` calls for related information
- User provides knowledge when they remember it, not forced upfront structure
- Server connects related pieces through keyword matching and semantic analysis
- Example: Save problem → later save solution → later save outcome

**API Contract Principles**:
- **User-Controlled**: AI never saves without user approval/refinement
- **Immediate Availability**: Knowledge instantly accessible via `get_task_context`
- **Intelligent Merging**: Server handles relationship detection and duplicate prevention
- **Natural Information Flow**: Supports how humans actually provide knowledge

### **Core Knowledge Operations**

### **1. `store_knowledge` - Store New Knowledge**

**Purpose**: Capture new knowledge with contextual metadata and tags.

```json
{
  "content": "Mobile OAuth requires PKCE for security compliance",
  "tags": ["#mobile", "#oauth", "#security", "#project-mobile-app"],
  "context": "implementing authentication for mobile app",
  "project": "mobile-ecommerce",
  "source": "user|ai|documentation",
  "confidence": 0.9
}
```

### **2. `find_knowledge` - Search and Retrieve Knowledge**

**Purpose**: Semantic search across stored knowledge with optional filtering.

```json
{
  "query": "mobile authentication patterns",
  "tags": ["#mobile", "#auth"],
  "project": "mobile-ecommerce",
  "limit": 10,
  "include_related": true,
  "min_relevance": 0.7
}
```

### **3. `connect_knowledge` - Create Knowledge Relationships**

**Purpose**: Establish typed relationships between knowledge pieces.

```json
{
  "source_id": "mobile-oauth-123",
  "target_id": "pkce-implementation-456",
  "relationship_type": "requires|explains|contradicts|builds_on|similar_to",
  "strength": 0.9,
  "context": "PKCE is required for mobile OAuth security"
}
```

### **4. `update_knowledge` - Modify Existing Knowledge**

**Purpose**: Edit knowledge content, tags, or metadata without breaking relationships.

```json
{
  "knowledge_id": "mobile-oauth-123",
  "content": "Mobile OAuth requires PKCE for security. Note: React Native needs custom redirect handling.",
  "add_tags": ["#react-native", "#redirect-handling"],
  "remove_tags": ["#deprecated"],
  "update_confidence": 0.95
}
```

### **AI Intelligence Operations**

### **5. `get_suggestions` - Get Contextual AI Suggestions**

**Purpose**: Receive proactive recommendations based on current work context.

```json
{
  "current_task": "implementing user login for mobile app",
  "project": "mobile-ecommerce",
  "context_tags": ["#mobile", "#auth", "#react-native"],
  "include_reasoning": true,
  "max_suggestions": 5
}
```

**Response Example**:
```json
{
  "suggestions": [
    {
      "content": "Use PKCE for OAuth security in mobile apps",
      "relevance_score": 0.95,
      "reasoning": "Directly applies to mobile authentication",
      "supporting_knowledge": ["mobile-oauth-123"]
    }
  ]
}
```

### **6. `find_patterns` - Discover Reusable Patterns**

**Purpose**: Identify recurring successful patterns across projects and domains.

```json
{
  "domain": "mobile-authentication",
  "min_occurrences": 2,
  "include_success_rate": true,
  "project_scope": "all|current|similar"
}
```

### **7. `identify_gaps` - Find Knowledge Gaps**

**Purpose**: Detect missing knowledge for current context or project needs.

```json
{
  "current_context": "setting up mobile CI/CD pipeline",
  "project": "mobile-ecommerce",
  "priority_level": "high|medium|low",
  "gap_types": ["missing_knowledge", "outdated_info", "incomplete_patterns"]
}
```

### **Learning & Evolution Operations**

### **8. `record_outcome` - Capture Learning from Results**

**Purpose**: Record real-world outcomes to improve knowledge effectiveness.

```json
{
  "knowledge_ids": ["mobile-oauth-123", "pkce-implementation-456"],
  "outcome": "success|failure|partial",
  "result_description": "PKCE OAuth implementation worked perfectly",
  "lessons_learned": "Custom redirect handler needed for React Native",
  "effectiveness_score": 0.9,
  "context": "mobile-ecommerce project authentication"
}
```

### **9. `strengthen_connections` - Enhance Knowledge Relationships**

**Purpose**: Adjust relationship strength based on usage patterns and outcomes.

```json
{
  "source_id": "mobile-oauth-123",
  "target_id": "react-native-patterns-789",
  "strength_adjustment": 0.2,
  "usage_context": "successful mobile auth implementation",
  "reason": "proven effective combination in production"
}
```

## User Journey Examples

### **Simple Knowledge Storage**
```
User: "Save this: Always use environment variables for API keys, never hardcode them"

AI: Stored with tags #security, #general, #api-keys. Connected to security best practices.
```

### **Active Knowledge Application**
```
User: "I'm setting up API integration for the mobile app"

AI: Based on your knowledge:
- Use environment variables for API keys (you stored this rule)
- Consider rate limiting (successful pattern from backend-api project)
- Mobile apps need network timeout handling (pattern from 2 similar projects)

Should I apply the mobile-api-integration pattern?
```

### **Knowledge Evolution**
```
User: "The timeout handling approach worked great, but we needed 30 seconds instead of 10"

AI: Updated mobile timeout pattern with your learning. The 30-second timeout is now the recommended default for mobile API calls. Should I suggest this for similar future implementations?
```

## Technical Implementation

### **MCP HTTP Transport Protocol**

**Protocol Foundation**: MCP uses JSON-RPC 2.0 over HTTP (not REST APIs)

**Transport Architecture**:
- **Single Endpoint**: All operations via one MCP endpoint (e.g., `/mcp`)
- **Protocol**: JSON-RPC 2.0 with `jsonrpc`, `id`, `method`, `params` structure
- **HTTP Methods**: POST for client-to-server requests, optional GET for SSE streaming
- **Headers**: `MCP-Protocol-Version: 2025-03-26`, session management via `MCP-Session-Id`

**Message Flow Examples**:

*Client Request*:
```http
POST /mcp HTTP/1.1
Content-Type: application/json
MCP-Protocol-Version: 2025-03-26
Authorization: Bearer <token>

{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "knowledge",
    "arguments": {
      "action": "store",
      "content": "Mobile OAuth requires PKCE for security",
      "tags": ["#mobile", "#oauth", "#security"]
    }
  }
}
```

*Server Response*:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "knowledge_id": "mobile-oauth-123",
    "status": "stored",
    "relationships_created": 2
  }
}
```

*Initialization Flow*:
```json
// Client initializes session
{
  "jsonrpc": "2.0",
  "id": "init-1",
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {"listChanged": true}
    },
    "clientInfo": {
      "name": "kaizen-client",
      "version": "1.0.0"
    }
  }
}

// Server responds with capabilities
{
  "jsonrpc": "2.0",
  "id": "init-1", 
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {"listChanged": true}
    },
    "serverInfo": {
      "name": "kaizen-mcp-server",
      "version": "1.0.0"
    }
  }
}
```

**Security Requirements**:
- MUST validate `Origin` header (DNS rebinding protection)
- SHOULD bind to localhost (127.0.0.1) for local deployment
- SHOULD implement Bearer token authentication
- Uses session management for stateful connections

**MCP Server Implementation**:
- Transport-agnostic design (stdio, HTTP, SSE)
- Standard MCP tool calling interface
- JSON-RPC error handling for protocol errors
- HTTP status codes for transport errors

**Example MCP Server (MCP_DOCKER Reference)**:
- Python-based MCP server for Docker operations
- Provides tools: container management, compose stack deployment, log retrieval
- Standard configuration in Claude Desktop:
```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "uvx",
      "args": ["docker-mcp"]
    }
  }
}
```
- Follows MCP specification for HTTP transport
- Session-based communication with proper authentication

### **MVP Technology Stack**
- **MCP Server**: Python-based implementation with HTTP transport
- **Vector Database**: Pinecone/Weaviate for semantic search
- **Graph Database**: Neo4j Aura for relationships  
- **Embedding Model**: OpenAI text-embedding-3-small
- **AI Integration**: Claude/GPT-4 for insights and evolution

### **Data Models**

**Knowledge Node**:
```json
{
  "id": "uuid",
  "content": "string",
  "tags": ["array"],
  "embedding": [vector],
  "metadata": {
    "created": "timestamp",
    "updated": "timestamp", 
    "usage_count": "number",
    "success_rate": "number"
  }
}
```

**Relationship Edge**:
```json
{
  "source": "knowledge-id",
  "target": "knowledge-id",
  "type": "relationship-type",
  "strength": "0.0-1.0",
  "context": "when this relationship applies"
}
```

## Business Value

- **Institutional Memory**: Knowledge persists and grows across projects
- **AI Partner**: Proactive suggestions based on accumulated experience
- **Learning Organization**: System improves through usage and outcomes
- **Cross-Project Intelligence**: Patterns discovered and applied across work
- **Effortless Organization**: Natural emergence of structure through use

## Success Metrics

1. **Time to First Value**: < 5 minutes to store and retrieve useful knowledge
2. **Knowledge Reuse**: AI successfully suggests relevant knowledge 80%+ of time
3. **Learning Effectiveness**: Knowledge accuracy improves through usage feedback
4. **User Adoption**: Non-technical users successfully operate system
5. **Cross-Project Value**: Knowledge from one project helps in others

This solution achieves maximum power with minimum complexity - exactly the "sky is the limit" platform with elegant simplicity.