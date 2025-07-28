-- Project Kaizen - Complete PostgreSQL Schema Definition
-- Optimized for MCP Knowledge Management System
-- Includes performance optimizations and data integrity enhancements

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- Required for BIGINT array GIN indexing

-- Create task size enumeration
CREATE TYPE task_size_enum AS ENUM ('XS', 'S', 'M', 'L', 'XL');

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Namespaces: Global organizational containers
CREATE TABLE namespaces (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes for namespaces
CREATE INDEX idx_namespaces_name ON namespaces (name);
CREATE INDEX idx_namespaces_created_at ON namespaces (created_at);

-- Scopes: Project boundaries within namespaces with hierarchy support
CREATE TABLE scopes (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    namespace_id BIGINT NOT NULL REFERENCES namespaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(namespace_id, name)
);

-- Performance indexes for scopes
CREATE INDEX idx_scopes_namespace_name ON scopes (namespace_id, name);

-- Scope Parents: Multiple inheritance relationships
CREATE TABLE scope_parents (
    child_scope_id BIGINT NOT NULL REFERENCES scopes(id) ON DELETE CASCADE,
    parent_scope_id BIGINT NOT NULL REFERENCES scopes(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    PRIMARY KEY (child_scope_id, parent_scope_id),
    CONSTRAINT no_self_reference CHECK (child_scope_id != parent_scope_id)
);

-- Performance indexes for scope parents
CREATE INDEX idx_scope_parents_child ON scope_parents (child_scope_id);
CREATE INDEX idx_scope_parents_parent ON scope_parents (parent_scope_id);

-- Scope Hierarchy: Flattened ancestry for fast knowledge retrieval
CREATE TABLE scope_hierarchy (
    scope_id BIGINT PRIMARY KEY REFERENCES scopes(id) ON DELETE CASCADE,
    ancestors BIGINT[] NOT NULL -- includes self + all parent scopes up to global:default
);

-- Performance index for ancestor lookups
CREATE INDEX idx_scope_hierarchy_ancestors ON scope_hierarchy USING GIN (ancestors);

-- Knowledge: Searchable content with full-text search optimization
CREATE TABLE knowledge (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    scope_id BIGINT NOT NULL REFERENCES scopes(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    context TEXT NOT NULL, -- Space-separated search terms
    task_size task_size_enum, -- NULL = universal (matches all task sizes)
    
    -- Pre-computed search vectors for performance
    content_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    context_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', context)) STORED,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', context), 'A') || 
        setweight(to_tsvector('english', content), 'B')
    ) STORED,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Critical performance indexes for knowledge
CREATE INDEX idx_knowledge_scope_task ON knowledge (scope_id, task_size);
CREATE INDEX idx_knowledge_search_gin ON knowledge USING GIN (search_vector);
CREATE INDEX idx_knowledge_context_gin ON knowledge USING GIN (context_vector);
CREATE INDEX idx_knowledge_content_gin ON knowledge USING GIN (content_vector);

-- Knowledge Collisions: Conflict resolution with audit trail
CREATE TABLE knowledge_collisions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    collision_group_id BIGINT NOT NULL,
    active_knowledge_id BIGINT NOT NULL REFERENCES knowledge(id) ON DELETE CASCADE,
    suppressed_knowledge_ids BIGINT[] NOT NULL,
    resolution_method TEXT NOT NULL CHECK (resolution_method IN ('scope_precedence', 'user_choice')), -- How collision was resolved: automatically by scope hierarchy or user decision
    resolved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_by TEXT, -- User ID or system identifier that made the resolution decision
    metadata JSONB DEFAULT '{}', -- Additional context: conflict reason, decision rationale, etc.
    
    UNIQUE(collision_group_id, active_knowledge_id)
);

-- Performance indexes for knowledge collisions
CREATE INDEX idx_collisions_active ON knowledge_collisions (active_knowledge_id);
CREATE INDEX idx_collisions_group ON knowledge_collisions (collision_group_id);
CREATE INDEX idx_collisions_suppressed ON knowledge_collisions USING GIN (suppressed_knowledge_ids);

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Active Knowledge Search: Pre-joined, collision-filtered knowledge
CREATE MATERIALIZED VIEW mv_active_knowledge_search AS
SELECT 
    k.id,
    k.scope_id,
    k.content,
    k.context,
    k.task_size,
    k.search_vector,
    k.created_at,
    k.updated_at,
    -- Denormalized scope information for fast access
    s.name as scope_name,
    n.name as namespace_name,
    n.name || ':' || s.name as qualified_scope_name
FROM knowledge k
JOIN scopes s ON k.scope_id = s.id
JOIN namespaces n ON s.namespace_id = n.id
LEFT JOIN knowledge_collisions kc ON k.id = ANY(kc.suppressed_knowledge_ids)
WHERE kc.id IS NULL; -- Exclude collision-suppressed knowledge

-- Optimized indexes for search operations
CREATE UNIQUE INDEX idx_mv_active_knowledge_id ON mv_active_knowledge_search (id);
CREATE INDEX idx_mv_active_search_gin ON mv_active_knowledge_search USING GIN (search_vector);
CREATE INDEX idx_mv_active_scope_task ON mv_active_knowledge_search (scope_id, task_size);
CREATE INDEX idx_mv_active_qualified_scope ON mv_active_knowledge_search (qualified_scope_name);


-- ============================================================================
-- CORE FUNCTIONS FOR MCP ACTIONS
-- ============================================================================

-- Get Task Context: Multi-query knowledge retrieval with scope inheritance
CREATE OR REPLACE FUNCTION get_task_context(
    query_terms TEXT[],
    target_scope TEXT,
    filter_task_size task_size_enum DEFAULT NULL
) RETURNS TABLE (
    qualified_scope_name TEXT,
    knowledge_id TEXT,
    content TEXT
) AS $$
DECLARE
    target_scope_id BIGINT;
BEGIN
    -- Get the scope_id from target_scope string (format: "namespace:scope")
    SELECT s.id INTO target_scope_id
    FROM scopes s
    JOIN namespaces n ON s.namespace_id = n.id
    WHERE n.name || ':' || s.name = target_scope;
    
    IF target_scope_id IS NULL THEN
        RAISE EXCEPTION 'Scope not found: %', target_scope;
    END IF;
    
    RETURN QUERY
    WITH multi_query_results AS (
        SELECT 
            k.qualified_scope_name,
            k.id::TEXT as knowledge_id,
            k.content,
            ts_rank(k.search_vector, websearch_to_tsquery('english', query_term)) as rank,
            ROW_NUMBER() OVER (
                PARTITION BY query_term 
                ORDER BY ts_rank(k.search_vector, websearch_to_tsquery('english', query_term)) DESC
            ) as rank_position
        FROM mv_active_knowledge_search k
        JOIN scope_hierarchy sh ON k.scope_id = ANY(sh.ancestors)
        CROSS JOIN UNNEST(query_terms) as query_term
        WHERE 
            sh.scope_id = target_scope_id
            AND k.search_vector @@ websearch_to_tsquery('english', query_term)
            AND (filter_task_size IS NULL OR k.task_size IS NULL OR k.task_size >= filter_task_size)
    )
    SELECT 
        mqr.qualified_scope_name,
        mqr.knowledge_id,
        mqr.content
    FROM multi_query_results mqr
    WHERE mqr.rank >= 0.1 -- Minimum relevance threshold (0.0-1.0 scale)
    ORDER BY mqr.rank DESC, mqr.qualified_scope_name;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- SCOPE HIERARCHY MAINTENANCE
-- ============================================================================

-- Function to calculate all ancestors for a given scope
CREATE OR REPLACE FUNCTION calculate_scope_ancestors(scope_id_param BIGINT) RETURNS BIGINT[] AS $$
DECLARE
    result BIGINT[] := ARRAY[]::BIGINT[];
    global_default_id BIGINT;
BEGIN
    -- Get global:default scope id
    SELECT s.id INTO global_default_id
    FROM scopes s
    JOIN namespaces n ON s.namespace_id = n.id
    WHERE n.name = 'global' AND s.name = 'default';
    
    -- Calculate ancestors using recursive CTE
    WITH RECURSIVE ancestor_tree AS (
        -- Base case: the scope itself
        SELECT scope_id_param as current_scope, 0 as level
        
        UNION ALL
        
        -- Recursive case: find parents
        SELECT sp.parent_scope_id, at.level + 1
        FROM ancestor_tree at
        JOIN scope_parents sp ON at.current_scope = sp.child_scope_id
        WHERE at.level < 10 -- Prevent infinite recursion
    )
    SELECT array_agg(DISTINCT current_scope ORDER BY current_scope) INTO result
    FROM ancestor_tree;
    
    -- Always include global:default if not already included
    IF global_default_id IS NOT NULL AND NOT (global_default_id = ANY(result)) THEN
        result := result || global_default_id;
    END IF;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to refresh scope hierarchy for affected scopes
CREATE OR REPLACE FUNCTION refresh_scope_hierarchy() RETURNS TRIGGER AS $$
DECLARE
    affected_scope_id BIGINT;
    affected_scopes BIGINT[] := ARRAY[]::BIGINT[];
BEGIN
    -- Determine which scopes need hierarchy refresh based on trigger type
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        affected_scopes := ARRAY[NEW.child_scope_id];
        
        -- Also refresh any scopes that have NEW.child_scope_id as ancestor
        WITH RECURSIVE descendant_tree AS (
            SELECT NEW.child_scope_id as current_scope
            UNION ALL
            SELECT sp.child_scope_id
            FROM descendant_tree dt
            JOIN scope_parents sp ON dt.current_scope = sp.parent_scope_id
        )
        SELECT array_agg(DISTINCT current_scope) INTO affected_scopes
        FROM descendant_tree;
        
    ELSIF TG_OP = 'DELETE' THEN
        affected_scopes := ARRAY[OLD.child_scope_id];
        
        -- Also refresh any scopes that had OLD.child_scope_id as ancestor
        WITH RECURSIVE descendant_tree AS (
            SELECT OLD.child_scope_id as current_scope
            UNION ALL
            SELECT sp.child_scope_id
            FROM descendant_tree dt
            JOIN scope_parents sp ON dt.current_scope = sp.parent_scope_id
        )
        SELECT array_agg(DISTINCT current_scope) INTO affected_scopes
        FROM descendant_tree;
    END IF;
    
    -- Update hierarchy for all affected scopes
    FOREACH affected_scope_id IN ARRAY affected_scopes
    LOOP
        INSERT INTO scope_hierarchy (scope_id, ancestors)
        VALUES (affected_scope_id, calculate_scope_ancestors(affected_scope_id))
        ON CONFLICT (scope_id) 
        DO UPDATE SET ancestors = calculate_scope_ancestors(affected_scope_id);
    END LOOP;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger for scope_parents changes
CREATE TRIGGER trigger_refresh_scope_hierarchy_parents
    AFTER INSERT OR UPDATE OR DELETE ON scope_parents
    FOR EACH ROW
    EXECUTE FUNCTION refresh_scope_hierarchy();

-- Function to create hierarchy entry for new scopes
CREATE OR REPLACE FUNCTION create_scope_hierarchy_entry() RETURNS TRIGGER AS $$
BEGIN
    -- Create hierarchy entry for the new scope
    INSERT INTO scope_hierarchy (scope_id, ancestors)
    VALUES (NEW.id, calculate_scope_ancestors(NEW.id));
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for new scopes
CREATE TRIGGER trigger_create_scope_hierarchy
    AFTER INSERT ON scopes
    FOR EACH ROW
    EXECUTE FUNCTION create_scope_hierarchy_entry();

-- Function to create default scope when namespace is created
CREATE OR REPLACE FUNCTION create_default_scope_on_namespace() RETURNS TRIGGER AS $$
BEGIN
    -- Automatically create default scope for new namespace
    INSERT INTO scopes (
        namespace_id, 
        name, 
        description
    ) VALUES (
        NEW.id,
        'default',
        NEW.description || ' - default scope'
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for new namespaces
CREATE TRIGGER trigger_create_default_scope
    AFTER INSERT ON namespaces
    FOR EACH ROW
    EXECUTE FUNCTION create_default_scope_on_namespace();

-- ============================================================================
-- ENHANCEMENT: CIRCULAR DEPENDENCY PREVENTION
-- ============================================================================

-- Function to detect circular dependencies in scope hierarchy
CREATE OR REPLACE FUNCTION detect_circular_dependency(
    new_child_scope_id BIGINT,
    new_parent_scope_id BIGINT
) RETURNS BOOLEAN AS $$
DECLARE
    parent_ancestors BIGINT[];
BEGIN
    -- Get ancestors of the proposed parent
    SELECT ancestors INTO parent_ancestors
    FROM scope_hierarchy
    WHERE scope_id = new_parent_scope_id;
    
    -- If parent's ancestors include the child, we have a cycle
    RETURN (parent_ancestors IS NOT NULL AND new_child_scope_id = ANY(parent_ancestors));
END;
$$ LANGUAGE plpgsql;

-- Trigger function to prevent circular dependencies
CREATE OR REPLACE FUNCTION prevent_circular_inheritance() RETURNS TRIGGER AS $$
BEGIN
    -- Check for circular dependency
    IF detect_circular_dependency(NEW.child_scope_id, NEW.parent_scope_id) THEN
        RAISE EXCEPTION 'Circular dependency detected: adding parent % to child % would create a cycle',
            NEW.parent_scope_id, NEW.child_scope_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply circular dependency prevention trigger
CREATE TRIGGER trigger_prevent_circular_inheritance
    BEFORE INSERT OR UPDATE ON scope_parents
    FOR EACH ROW
    EXECUTE FUNCTION prevent_circular_inheritance();

-- ============================================================================
-- ENHANCEMENT: AUTOMATIC DEFAULT PARENT ENFORCEMENT
-- ============================================================================

-- Function to ensure default parent is always added
CREATE OR REPLACE FUNCTION enforce_default_parent() RETURNS TRIGGER AS $$
DECLARE
    default_scope_id BIGINT;
    namespace_name TEXT;
BEGIN
    -- Get namespace name for the scope
    SELECT n.name INTO namespace_name
    FROM namespaces n
    WHERE n.id = NEW.namespace_id;
    
    -- Find the default scope for this namespace
    SELECT s.id INTO default_scope_id
    FROM scopes s
    WHERE s.namespace_id = NEW.namespace_id
    AND s.name = 'default';
    
    -- If this is not the default scope itself, ensure it has default as parent
    IF NEW.name != 'default' AND default_scope_id IS NOT NULL THEN
        -- Check if default parent relationship already exists
        IF NOT EXISTS (
            SELECT 1 FROM scope_parents 
            WHERE child_scope_id = NEW.id 
            AND parent_scope_id = default_scope_id
        ) THEN
            -- Add default parent relationship
            INSERT INTO scope_parents (child_scope_id, parent_scope_id)
            VALUES (NEW.id, default_scope_id);
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply default parent enforcement trigger
CREATE TRIGGER trigger_enforce_default_parent
    AFTER INSERT ON scopes
    FOR EACH ROW
    EXECUTE FUNCTION enforce_default_parent();

-- ============================================================================
-- TRIGGERS FOR CONSISTENCY AND PERFORMANCE
-- ============================================================================



-- Materialized View Refresh Triggers
CREATE OR REPLACE FUNCTION refresh_active_knowledge_search() RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_knowledge_search;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Refresh on knowledge changes
CREATE TRIGGER trigger_refresh_active_knowledge_insert
    AFTER INSERT ON knowledge
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_active_knowledge_search();

-- Refresh on collision resolution
CREATE TRIGGER trigger_refresh_active_knowledge_collision
    AFTER INSERT OR UPDATE OR DELETE ON knowledge_collisions
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_active_knowledge_search();


-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Create global namespace (default scope created automatically by trigger)
INSERT INTO namespaces (name, description) 
VALUES ('global', 'Universal knowledge accessible everywhere')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- PERFORMANCE OPTIMIZATION SETTINGS
-- ============================================================================

-- Enable auto-vacuum for materialized views
ALTER MATERIALIZED VIEW mv_active_knowledge_search SET (
    autovacuum_enabled = true,
    autovacuum_vacuum_scale_factor = 0.1
);


-- Create statistics for query optimization
CREATE STATISTICS stats_knowledge_search_scope ON scope_id, task_size FROM knowledge;
CREATE STATISTICS stats_scope_namespace ON namespace_id FROM scopes;

-- ============================================================================
-- COMMENTS AND DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE namespaces IS 'Global organizational containers (e.g., acme, payments)';
COMMENT ON TABLE scopes IS 'Project boundaries within namespaces';
COMMENT ON TABLE scope_parents IS 'Multiple inheritance relationships between scopes';
COMMENT ON TABLE scope_hierarchy IS 'Flattened ancestor arrays for fast knowledge retrieval';
COMMENT ON TABLE knowledge IS 'Searchable content with pre-computed full-text search vectors';
COMMENT ON TABLE knowledge_collisions IS 'Conflict resolution audit trail for competing knowledge';

COMMENT ON MATERIALIZED VIEW mv_active_knowledge_search IS 'Pre-joined, collision-filtered knowledge for fast search';

COMMENT ON FUNCTION get_task_context IS 'Multi-query knowledge retrieval with scope inheritance for MCP get_task_context action';
COMMENT ON FUNCTION detect_circular_dependency IS 'Prevents circular dependencies in scope hierarchy';
COMMENT ON FUNCTION enforce_default_parent IS 'Ensures all scopes inherit from default scope';
