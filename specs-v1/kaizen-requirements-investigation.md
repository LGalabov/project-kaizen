# Kaizen Requirements Investigation

## Core Problem Statement

"Kaizen is about evolution of the knowledge. The AI and the user should be able to put somewhere the knowledge they accumulate during work. Yet the system must be simple to use."

## Primary Requirements

### **Simplicity First**
- Simple concept that can be expanded
- Short time to market for real-life project use
- Simple concept to avoid thousands of edge cases
- Simple MVP definition, easy for users to use
- Ideally 5 endpoints instead of 150

### **Knowledge Usage, Not Just Storage**
- AI must be able to USE knowledge - not just read it, but make positive impact
- AI must present opportunities to update knowledge DB with:
  - Mistakes discovered
  - New findings
  - Meta-knowledge about existing knowledge
  - Bug fixes with reasoning and how the fix works
- Make it USEFUL, not just storage for thoughts (unlike memoire)

### **Unified API Design**
- Unified API through MCP server that is simple to use
- Simple interface for store/fetch/update/delete knowledge
- Powerful generic functions for structured information, relations, actions
- Platform that SCREAMS: "Sky is the limit!"

### **Neural Network-Like Knowledge**
- Knowledge should be like a neural network - like real information in the world
- Related, taggable, sortable, searchable
- Resembles human knowledge patterns
- Knowledge about general things crosses all projects and tasks
- Knowledge per project or task
- Knowledge that spans few projects/tasks (company-wide, mobile projects, backend projects, shared libs)

### **Project Awareness Without Complexity**
- Must have notion of project
- Avoid 4-tier structure that was too hard (requires dozens/hundreds of endpoints)
- Fear that complex hierarchies require extensive documentation
- Want simplistic yet elegant solution

### **Constraints**
- Don't require 100+ pages of manual
- Avoid overengineering
- Must be deliverable (not fail due to complexity)
- Unknown future direction - need flexibility

## Success Criteria

1. **Time to Market**: Can be used ASAP in real projects
2. **User Adoption**: Non-technical users can understand and use
3. **AI Integration**: AI actively applies knowledge to improve work
4. **Extensibility**: Simple foundation that can grow
5. **Knowledge Evolution**: System learns and improves through use
6. **Cross-Project Value**: Knowledge naturally spans projects without complex setup

## The Core AI Agent Problem

**Context**: AI agents work on multiple tasks across hours-long processes, changing between backend, frontend, database, devops work within the same project.

**The Dilemma**: 
- **Option A**: Drag old context everywhere → **Context Pollution** (irrelevant information clutters decision-making)
- **Option B**: Start fresh each task → **Context Gaps** (missing crucial knowledge, instructions, patterns)

**Current Failure Modes**:
- AI lacks sufficient context for 99% task success rate
- Instructions get buried in conversation history, becoming "miniscule and ignorable"
- Project-specific knowledge isn't AI-understandable in current format
- Complex tasks fail due to missing patterns/rules
- Simple tasks fail due to missing specific knowledge requirements

**The Vision**: 
AI agent calls MCP API before each task with task essence → receives "magical" context containing:
- Essential instructions for this type of work
- Project-specific rules and decisions
- General patterns and best practices  
- Past learnings and common pitfalls
- Success criteria and validation approaches

**Key Insight**: The API must intelligently synthesize task understanding, project context, and accumulated knowledge to provide everything the AI needs for 99% success rate.

## Key Insights from Requirements

- **Elegance over Features**: Simple, powerful foundation beats complex feature-rich system
- **Use-Driven Design**: Focus on knowledge application, not knowledge management
- **Natural Organization**: Let tagging and relationships emerge from usage
- **AI as Partner**: AI should proactively help, not just respond to queries
- **Flexible Boundaries**: Project context without rigid hierarchical constraints
- **Context-First Approach**: AI success depends on having the right context at the right time, not just access to knowledge