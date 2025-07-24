# Save Knowledge Endpoint Discussion - Temp Notes

## Context
Working on second endpoint following successful `get_task_context` design. User provided feedback and raised critical design questions.

## User Feedback on Initial Proposal

**Approved Elements**:
- Endpoint name: `save_knowledge` ✓
- Input content field ✓  
- Input keywords field ✓
- Input context field ✓
- Output: status only, nothing else needed ✓

**Rejected Elements**:
- Input type field (pattern|pitfall|caveat|rule) - questioned purpose, adds no real value

## Critical Design Questions Raised

### 1. Knowledge Updates Problem
**Issue**: How do you update knowledge when you don't know if it exists?
**Insight**: This is actually an **upsert operation**
**Solution Direction**: Make `save_knowledge` intelligent upsert that:
- Checks if similar knowledge exists (semantic matching)
- If exists: merge/update intelligently
- If new: create fresh knowledge  
- Return what actually happened

### 2. Knowledge Relations API Design
**Question**: How do we make relations between knowledge in terms of API?
**Options Identified**:
- **Option A**: Auto-detection only (server handles all linking)
- **Option B**: Optional explicit relationships in save_knowledge

### 3. Meta-Knowledge Input Structure
**User's Vision**: Handle related pieces of information with relationships
**Example**: Bug description + Fix description + Outcome as separate but related pieces
**Proposed Structure**:
```json
{
  "content": {
    "bug": "OAuth redirect fails on iOS simulator",
    "fix": "Add custom URL scheme handler in AppDelegate", 
    "outcome": "Successful authentication flow on all iOS devices"
  },
  "keywords": ["oauth", "ios", "redirect", "bug-fix"],
  "context": {...}
}
```

## Open Questions for Resolution
1. **Relations**: Auto-detect only, or allow explicit relationship hints?
2. **Meta-knowledge**: Should content be object with predefined keys (bug/fix/outcome) or flexible structure?
3. **Upsert feedback**: Should output indicate if knowledge was merged vs created new?

## Current Schema Direction
```json
{
  "content": "string OR structured object for meta-knowledge",
  "keywords": ["array", "of", "keywords"],
  "context": {
    "project": "string",
    "technology": ["array"]
  }
}
```

## Design Principles Maintained
- Follow proven `get_task_context` patterns
- User-governed knowledge creation (AI suggests, user approves)
- Immediate availability via `get_task_context`
- Bounded schema with clear rules
- Simple API assuming governance work already done