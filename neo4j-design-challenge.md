# Neo4j Design Challenge

## Problem Statement
Design a graph structure that enables single-query resolution of 4-tier knowledge inheritance with "most specific wins" precedence.

## Requirements
1. **4-Tier Hierarchy**: GENERAL → PRODUCT → GROUP → PROJECT
2. **Single Query**: Must resolve inheritance and return most specific knowledge in one go
3. **Missing Tiers**: Handle cases where GROUP (or other tiers) might not exist
4. **Project Isolation**: Each project has its own tier chain
5. **Task-Based Retrieval**: Query by keywords (e.g., "git", "commit") and get applicable knowledge

## Test Scenario
- AI is in directory X (project identified from CLAUDE.md)
- Task: "commit in Git"
- Query should return:
  - Most specific git knowledge from PROJECT (if exists)
  - Otherwise from GROUP (if exists)
  - Otherwise from PRODUCT (if exists)
  - Otherwise from GENERAL (if exists)
  - All in single query with precedence resolved

## Success Criteria
- One Cypher query handles entire inheritance resolution
- No post-processing needed - query returns final knowledge
- Scales to many projects without performance degradation

