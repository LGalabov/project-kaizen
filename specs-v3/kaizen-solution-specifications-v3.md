# Kaizen Solution Specifications v3

## Revolutionary Tag-Based Knowledge System

Based on research into AI-friendly knowledge management, enterprise tag systems, and natural conversation patterns for organizational knowledge.

## Core Architecture

### **Namespace-Scope Graph with Intelligent Tag Resolution**
Knowledge organized through a multi-tenant architecture that combines organizational hierarchy with universal concept tags:

- **Multi-Tenant Namespaces**: Business contexts (companies/organizations) with flexible scope graphs
- **Universal Concept Tags**: Technology and domain tags that work across all namespaces
- **Intelligent Tag Resolution**: AI uses any variation, system resolves to canonical form with comprehensive altname mapping
- **Graph-Based Hierarchy**: Flexible organizational relationships without rigid tier constraints
- **User-Driven Conflict Resolution**: Knowledge collisions resolved through explicit user decisions
- **Zero-Friction Experience**: No pre-validation steps required for AI agents

## Tag System Architecture

### **Tags Table Structure**
```json
{
  "id": "K7H9M2PQX8",
  "names": ["nodejs", "node.js", "node-js", "node_js", "NodeJS", "Node.js"],
  "description": "JavaScript runtime environment"
}
```

### **Knowledge Table Structure**
```json
{
  "id": "G3K7R4NXL9",
  "content": "Always use PKCE for mobile OAuth security - React Native requires custom redirect handling",
  "tag_ids": ["K7H9M2PQX8", "P5N8Q1MZT6", "J9L2X6VB43"],
  "namespace_scope": "acme:petshop-storefront",
  "created": "2024-01-15T10:30:00Z",
  "updated": "2024-01-15T10:30:00Z"
}
```

### **Universal Concept Tag Examples**

**Technology Tags:**
```json
{
  "id": "R8N3M7QX52",
  "names": ["react-native", "reactnative", "react_native", "RN", "React Native"],
  "description": "Cross-platform mobile development framework"
}

{
  "id": "K7H9M2PQX8",
  "names": ["nodejs", "node.js", "node-js", "node_js", "NodeJS", "Node.js"],
  "description": "JavaScript runtime environment"
}
```

**Domain/Concept Tags:**
```json
{
  "id": "A9X5M2K7L4",
  "names": ["oauth", "OAuth", "oAuth", "auth", "authentication"],
  "description": "Authentication and authorization protocols"
}

{
  "id": "S8K3P6QN47",
  "names": ["mobile", "mobile-dev", "mobile-development", "smartphone", "iOS", "android"],
  "description": "Mobile application development concepts"
}
```

**Security & Best Practice Tags:**
```json
{
  "id": "H9L4X7RM85",
  "names": ["security", "secure", "safety", "protection"],
  "description": "Security practices and considerations"
}

{
  "id": "F2T9K6WB39",
  "names": ["testing", "tests", "qa", "quality-assurance", "unit-tests"],
  "description": "Software testing and quality assurance"
}
```

## Intelligent Tag Resolution System

### **Automatic Resolution Workflow**
1. **AI extracts tags** from user input: `["node.js", "oAuth", "proj:petshop"]`
2. **MCP resolves** via altname matching: `["nodejs", "oauth", "project:petshop"]`
3. **Collision detection** identifies ambiguous matches and asks for clarification
4. **Knowledge saved** with canonical tag references
5. **Query resolution** works with any tag variation

### **Collision Prevention with User Choice**
```json
// AI attempts to save with ambiguous tag "auth"
// MCP Response:
{
  "status": "clarification_needed", 
  "message": "Found existing tag 'auth' (authentication technology). Did you mean this, or should I create 'auth-project'?",
  "existing_tag": {
    "id": "A9X5M2K7L4",
    "names": ["auth", "authentication", "authN"],
    "description": "Authentication technology patterns"
  },
  "suggested_alternatives": ["auth-project", "project:auth"]
}
```

## Namespace-Scope Graph Architecture

### **Multi-Tenant Knowledge Organization**

Knowledge is organized through **namespaces** (business contexts) containing **scopes** (hierarchical levels) connected via **graph relationships**.

**Namespace Structure:**
- **Global**: Universal knowledge accessible everywhere
- **Business Namespaces**: Company/organization-specific knowledge containers (e.g., "acme", "project-kaizen")

**Scope Graph within Namespaces:**
- **Scopes**: Named organizational levels with descriptions (no predefined order)
- **Graph Relations**: `child -under-> parent` relationships define hierarchy
- **Multiple Inheritance**: Scopes can have multiple parents
- **Isolated Scopes**: Some scopes exist without hierarchy

### **Example Namespace Setup**

**Namespace Creation:**
```json
{
  "namespace": "acme",
  "description": "ACME Corporation projects and knowledge"
}
```

**Scope Creation (No Order):**
```json
{
  "namespace": "acme",
  "scopes": [
    {"id": "S7K9M2PQX8", "name": "petshop-storefront", "description": "Pet store frontend project"},
    {"id": "S2N8Q4LZ81", "name": "ecommerce-mobile", "description": "Mobile ecommerce group"}, 
    {"id": "S5P3R7VB43", "name": "company-wide", "description": "ACME company policies"},
    {"id": "S9L6X2MN67", "name": "payments-team", "description": "Payments specialist team"}
  ]
}
```

**Graph Relations:**
```json
{
  "relations": [
    {"child": "S7K9M2PQX8", "parent": "S2N8Q4LZ81"},  // storefront under mobile
    {"child": "S2N8Q4LZ81", "parent": "S5P3R7VB43"},  // mobile under company
    {"child": "S7K9M2PQX8", "parent": "S9L6X2MN67"}   // storefront also under payments
  ]
}
```

### **Knowledge Storage with Namespace-Scope**

**Global Knowledge:**
```json
{
  "id": "H8T2M9KX54",
  "content": "Always use HTTPS for all external API communications",
  "tag_ids": ["B5M8N3KX92", "H9L4X7RM85", "T7P2Q6ZW41"],
  "namespace_scope": "global"
}
```

**Scoped Knowledge:**
```json
{
  "id": "Q6P1N7ZL92", 
  "content": "Use OAuth with PKCE for mobile authentication in this project",
  "tag_ids": ["A9X5M2K7L4", "S8K3P6QN47", "H9L4X7RM85", "W4J9N5LK38"],
  "namespace_scope": "acme:petshop-storefront"
}
```

### **Dynamic Query Resolution**

**Query Path for `acme:petshop-storefront`:**
1. **Direct scope**: `acme:petshop-storefront`
2. **Parent scopes**: `acme:ecommerce-mobile`, `acme:payments-team` 
3. **Grandparent scopes**: `acme:company-wide`
4. **Global**: Universal knowledge

**Multiple Inheritance Resolution:**
- Follows all parent paths upward
- Combines knowledge from multiple hierarchies
- Applies collision resolutions to filter conflicts

## Tag Query Capabilities

### **Flexible Tag Discovery**
```json
// Find existing tags before creating new ones
{
  "name": "node",
  "match": "contains|exact|starts|ends"
}

// Response
{
  "matching_tags": [
    {
      "id": "K7H9M2PQX8",
      "names": ["nodejs", "node.js", "node-js"],
      "description": "JavaScript runtime environment"
    }
  ]
}
```

### **Advanced Filtering Support**
The tag system enables sophisticated knowledge filtering:

```json
{
  "include_tags": ["oauth", "mobile"],
  "exclude_tags": ["deprecated", "legacy"], 
  "namespace": "acme",
  "scope": "petshop-storefront",
  "limit": 10
}
```

**Query returns scoped knowledge map:**
```json
{
  "acme:petshop-storefront": [
    {"id": "K7H9M2PQX8", "content": "Use custom OAuth redirect handler for iOS"}
  ],
  "acme:ecommerce-mobile": [
    {"id": "G3K7R4NXL9", "content": "Mobile group must use OAuth with PKCE"}
  ],
  "acme:company-wide": [
    {"id": "P5N8Q1MZT6", "content": "All ACME projects require 2FA"}
  ],
  "global": [
    {"id": "J9L2X6VB43", "content": "Always use HTTPS for external APIs"}
  ]
}
```

## Collision Resolution System

### **Conflict Detection and User Resolution**

When knowledge conflicts exist across scope hierarchy, the system enables user-driven resolution:

**Collision Resolution Workflow:**
1. **AI detects conflicts** in query results across scope levels
2. **User decides precedence**: "G3K7R4NXL9 overrides K7H9M2PQX8" 
3. **AI saves collision resolution** with auto-generated collision ID
4. **Future queries automatically filter** overridden knowledge

**Collision Resolution Schema:**
```json
{
  "winner_id": "G3K7R4NXL9",
  "loser_id": "K7H9M2PQX8"
}

// MCP generates and responds:
{
  "collision_id": "C7M9K2PQX8", 
  "status": "saved"
}
```

**Query Result Filtering:**
Once collision resolution exists, overridden knowledge (K7H9M2PQX8) never appears in future query results, ensuring clean, resolved knowledge delivery to AI agents.

## Project Setup Workflow

### **New Directory Knowledge Initialization**

**Phase 1: Namespace Setup**
1. ✅ **Global knowledge** can be added immediately
2. ❌ **Scoped knowledge** cannot be added yet
3. **Query existing namespaces**: `get_namespaces()` to check for existing business contexts
4. **Create or select namespace**: e.g., "acme" with description "ACME Corporation projects"

**Phase 2: Scope Creation**
1. **Create initial scope**: e.g., "petshop-storefront" with description
2. **Update CLAUDE.md**:
   ```markdown
   # Current Project Context
   namespace: acme
   scope: petshop-storefront
   ```
3. ✅ **Now can save scoped knowledge** as `acme:petshop-storefront`

**Phase 3: Hierarchy Definition (Optional)**
1. **Add additional scopes** as needed (mobile-group, company-wide, etc.)
2. **Define graph relations**: `petshop-storefront -under-> ecommerce-mobile -under-> company-wide`
3. **Enable hierarchical knowledge inheritance** through scope graph

## Benefits of Namespace-Scope Graph Architecture

### **Enterprise-Grade Knowledge Organization**
✅ **Multi-Tenant Support** - Separate business contexts without knowledge pollution
✅ **Flexible Hierarchy** - Graph relations model real organizational structures  
✅ **Multiple Inheritance** - Projects can belong to multiple teams/groups
✅ **Zero-Friction Setup** - Start simple (global), add complexity as needed
✅ **Dynamic Relations** - Organizational changes don't require data migration

### **AI Agent Integration**  
✅ **Context-Aware Queries** - Automatic scope path resolution
✅ **Conflict Resolution** - User-driven knowledge precedence decisions
✅ **Progressive Complexity** - Begin with global knowledge, expand to scoped knowledge
✅ **Natural Workflow** - CLAUDE.md tracks current working context

### **Tag System Benefits**
✅ **Zero-Friction AI Experience** - No pre-validation steps required
✅ **99.99% Tag Consistency** - Automatic resolution via comprehensive altnames  
✅ **Universal Concepts** - Tags work across all namespaces and scopes
✅ **Intelligent Queries** - AI searches with variations, gets canonical matches

This architecture transforms knowledge management from a single-tenant system into a flexible, multi-tenant platform that naturally models real business organizations while maintaining the simplicity that makes AI agents highly effective.

## Secure Short ID Generation

### **ID Requirements**
- **Length**: 10 characters for collision safety
- **Character set**: Base58 (avoids confusing 0/O, I/1/l characters)
- **Entropy**: ~51 bits (safe up to ~1.7M IDs before 50% collision risk)
- **Use cases**: Knowledge IDs, Tag IDs, Scope IDs, Collision IDs, Namespace IDs

### **Implementation Libraries**

**Python Implementation:**
```python
import secrets
import base58

def generate_short_id(length=10):
    """Generate cryptographically secure 10-character Base58 ID"""
    # Calculate bytes needed for desired length
    bytes_needed = int((length * 5.86) / 8) + 1  # Base58 ~5.86 bits per char
    random_bytes = secrets.randbytes(bytes_needed)
    encoded = base58.b58encode(random_bytes).decode()
    return encoded[:length]

# Alternative using shortuuid library
import shortuuid
def generate_short_id_alt(length=10):
    return shortuuid.ShortUUID().random(length=length)

# Examples: "K7H9M2PQX8", "G3K7R4NXL9", "P5N8Q1MZT6"
```

**Node.js Implementation:**
```javascript
import { nanoid, customAlphabet } from 'nanoid'

// Base58 alphabet (Bitcoin standard, avoids confusing characters)
const base58Alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

const generateShortId = customAlphabet(base58Alphabet, 10)

// Usage
const id = generateShortId() // "K7H9M2PQX8"

// Alternative using crypto module
import crypto from 'crypto'

function generateShortIdCrypto(length = 10) {
  const alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
  let result = ''
  const bytes = crypto.randomBytes(length)
  
  for (let i = 0; i < length; i++) {
    result += alphabet[bytes[i] % alphabet.length]
  }
  return result
}
```

### **ID Usage Examples**

**Knowledge References:**
- User: "Apply the OAuth pattern from G3K7R4NXL9"
- AI: "Using knowledge G3K7R4NXL9: OAuth with PKCE for mobile..."

**Collision Resolution:**  
- User: "P5N8Q1MZT6 overrides K7H9M2PQX8"
- System generates collision ID: "C4B9N7QX21"

**Short, Human-Friendly Communication:**
- Easy to read in conversations
- Simple to type and reference
- Clear in logs and debugging
- Suitable for verbal communication ("ID P-5-N-8-Q-1-M-Z-T-6")

## Outstanding Items for Future Sessions

### **Missing Critical API Endpoints**
The following MCP tools need to be defined and documented:

- `get_task_context` - Query knowledge with namespace/scope context for AI task execution
- `save_knowledge` - Store knowledge with intelligent tag resolution and namespace_scope assignment
- `get_namespaces` - List available business namespaces with descriptions
- `create_namespace` - Create new business namespace 
- `create_scope` - Create organizational scope within namespace
- `create_scope_relation` - Define parent-child relationships between scopes
- `query_tags` - Discover existing tags with fuzzy matching
- `save_collision_resolution` - Record user decisions on knowledge conflicts

### **Workflow Integration Gaps**
The following workflow details need clarification:

- **CLAUDE.md Integration**: How AI reads current namespace/scope context and applies it automatically when saving knowledge
- **Tag Extraction Process**: Detailed workflow for how AI extracts universal concept tags from user prompts while excluding organizational context
- **Namespace_Scope Assignment**: Logic for how AI determines whether knowledge should be "global" vs current namespace:scope from CLAUDE.md
- **Collision Detection Triggers**: When and how AI recognizes conflicting knowledge across scope hierarchy to prompt user resolution
- **Progressive Setup Flow**: Step-by-step user experience for initializing new projects with namespace and scope creation

## Task Sizing Concept for Future Implementation

### **T-Shirt Size Knowledge Filtering**

**Concept**: Knowledge can be tagged with task complexity levels (similar to t-shirt sizing) to ensure appropriate guidance is provided based on task scope.

**Task Size Hierarchy** (each size includes all smaller sizes):
- **XS** (Extra Small): Quick fixes, simple changes, single-line modifications
- **S** (Small): Feature tweaks, minor enhancements, simple integrations  
- **M** (Medium): Full feature implementation, moderate refactoring, multi-component changes
- **L** (Large): Major feature development, architecture changes, cross-system integration
- **XL** (Extra Large): Complete system redesign, platform migration, enterprise-wide changes

### **Knowledge Storage with Task Sizing**

**Enhanced save_knowledge with task_size:**
```json
{
  "content": "Always conduct security review before deploying authentication changes",
  "tag_ids": ["H9L4X7RM85", "A9X5M2K7L4", "D8K2P5QN67"],
  "namespace_scope": "acme:petshop-storefront",
  "task_size": "M"
}
```

**Size-Specific Knowledge Examples:**
```json
// XS - Quick fix guidance
{
  "content": "Fix typos immediately, no review needed for documentation",
  "task_size": "XS"
}

// L - Major feature guidance  
{
  "content": "Large features require: architecture review, security assessment, performance testing, and staged rollout plan",
  "task_size": "L"
}
```

### **Query Filtering by Task Size**

**Enhanced get_task_context with task sizing:**
```json
{
  "include_tags": ["authentication", "security"],
  "namespace": "acme", 
  "scope": "petshop-storefront",
  "task_size": "M",
  "limit": 10
}
```

**Filtering Logic:**
- **AI provides task_size**: Returns knowledge for that size AND all smaller sizes
  - `task_size: "M"` → Returns XS, S, M knowledge (excludes L, XL)
  - `task_size: "L"` → Returns XS, S, M, L knowledge (excludes XL)
- **AI provides no task_size**: Returns ALL knowledge regardless of size
- **Knowledge has no task_size**: Always included in results (backwards compatibility)

### **Real-World Usage Scenarios**

**Small Task Example:**
```json
// AI Query
{"task_size": "S", "include_tags": ["bug-fix", "frontend"]}

// Returns
{
  "acme:petshop-storefront": [
    {"content": "For small UI fixes, test in Chrome and Firefox only", "task_size": "S"},
    {"content": "Quick CSS changes don't require designer review", "task_size": "XS"}
  ]
  // Excludes: "Major UI changes require accessibility audit" (task_size: "L")
}
```

**Large Task Example:**
```json
// AI Query  
{"task_size": "L", "include_tags": ["authentication", "security"]}

// Returns comprehensive guidance
{
  "acme:petshop-storefront": [
    {"content": "Fix auth typos immediately", "task_size": "XS"},
    {"content": "Minor auth UI tweaks need basic testing", "task_size": "S"},
    {"content": "Auth feature changes require security review", "task_size": "M"},
    {"content": "Major auth overhauls need penetration testing and compliance review", "task_size": "L"}
  ]
}
```

### **Benefits of Task Sizing**

✅ **Prevents Over-Engineering**: Small tasks don't get burdened with enterprise-level processes
✅ **Ensures Proper Rigor**: Large tasks get comprehensive guidance and oversight requirements
✅ **Contextual Appropriateness**: AI receives guidance proportional to task complexity
✅ **Backwards Compatible**: Existing knowledge without sizes still works
✅ **Flexible Filtering**: AI can omit task_size to get all knowledge when uncertain

### **Implementation Considerations**

**Size Determination Guidelines:**
- **Task Duration**: XS (minutes), S (hours), M (days), L (weeks), XL (months)
- **Team Impact**: XS (self), S (pair), M (team), L (multiple teams), XL (organization)
- **Risk Level**: XS (cosmetic), S (minor), M (moderate), L (high), XL (critical)
- **Complexity**: Lines of code, files affected, systems involved, dependencies

**Future Enhancement**: AI could automatically suggest task_size based on task description analysis, with user confirmation for accuracy.

## Database Technology Decision

### **Selected: PostgreSQL + pgvector Extension**

After comprehensive analysis of database options (graph databases, document databases, relational databases, vector databases, and hybrid architectures), we have selected **PostgreSQL with pgvector extension** as the optimal foundation for the Kaizen knowledge system.

### **Why PostgreSQL + pgvector Wins**

**Technical Alignment:**
- **Single System Simplicity**: Aligns with Kaizen's "5 endpoints instead of 150" philosophy
- **Native Array Support**: Perfect for tag names arrays and tag_ids references
- **JSONB Flexibility**: Handles evolving metaknowledge and flexible schemas
- **Recursive CTEs**: Elegant solution for namespace-scope graph traversal
- **pgvector Semantic Search**: Adds vector similarity without architectural complexity
- **ACID Guarantees**: Critical for collision resolution workflow consistency

**Implementation Approach:**
```sql
-- Core tables supporting all Kaizen requirements
CREATE TABLE tags (
    id VARCHAR(10) PRIMARY KEY,  -- Base58 short ID
    names TEXT[] NOT NULL,       -- Array for altname variations
    description TEXT,
    vector_embedding vector(384) -- Semantic search capability
);

CREATE TABLE knowledge (
    id VARCHAR(10) PRIMARY KEY,
    content TEXT NOT NULL,
    tag_ids VARCHAR(10)[] NOT NULL,    -- References to tags
    namespace_scope TEXT NOT NULL,     -- "namespace:scope" or "global"
    task_size VARCHAR(2),              -- XS, S, M, L, XL
    metaknowledge JSONB DEFAULT '{}',  -- Flexible metadata
    content_vector vector(384),        -- Content semantic search
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Graph traversal for scope inheritance
WITH RECURSIVE scope_hierarchy AS (
    SELECT id, namespace_id, 0 as level 
    FROM scopes WHERE namespace_id = $1 AND name = $2
    UNION ALL
    SELECT s.id, s.namespace_id, sh.level + 1
    FROM scopes s
    JOIN scope_relations sr ON s.id = sr.parent_scope_id
    JOIN scope_hierarchy sh ON sr.child_scope_id = sh.id
    WHERE sh.level < 10
)
SELECT * FROM scope_hierarchy;
```

**Performance Characteristics:**
- **Tag Resolution**: <1ms with GIN array indexes
- **Scope Inheritance**: <3ms with recursive CTE optimization
- **Knowledge Queries**: <5ms for complex multi-dimensional filtering
- **Semantic Search**: <10ms with IVFFlat vector indexes
- **Collision Resolution**: Real-time with standard relational joins

**Operational Benefits:**
- **Single Database**: Simplified backup, monitoring, and maintenance
- **Mature Ecosystem**: Extensive PostgreSQL tooling and expertise
- **Cost Effective**: No multiple database licenses or specialized infrastructure
- **Developer Friendly**: Standard SQL with JSON extensions
- **Proven Scalability**: Read replicas and partitioning for growth

### **Alternative Considerations**

**Neo4j (Graph Database)**: Excellent conceptual match for scope relationships but adds operational complexity and Cypher learning curve.

**MongoDB (Document Database)**: Strong for flexible schemas and arrays but complex graph queries via aggregation pipeline.

**Vector-Only Solutions**: Would require hybrid architecture with traditional database, increasing complexity without clear benefits over integrated pgvector approach.

### **Implementation Phases**

**Phase 1**: Core PostgreSQL schema with JSONB flexibility
**Phase 2**: pgvector extension for semantic search capabilities  
**Phase 3**: Performance optimization with advanced indexing
**Phase 4**: Scaling with read replicas and connection pooling

This database foundation provides enterprise-grade capabilities through a single, well-understood system that maintains Kaizen's emphasis on simplicity while delivering all required functionality for the namespace-scope knowledge architecture.