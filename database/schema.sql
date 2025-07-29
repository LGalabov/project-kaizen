-- Project Kaizen - PostgreSQL Schema for MCP Knowledge Management
-- Optimized for multi-tenant scope hierarchy with full-text search

CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE TYPE task_size_enum AS ENUM ('XS', 'S', 'M', 'L', 'XL');

-- =============================================================================
-- CORE SCHEMA
-- =============================================================================

-- Global organizational containers
CREATE TABLE namespaces (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_namespaces_name ON namespaces (name);

-- Project boundaries within namespaces
CREATE TABLE scopes (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    namespace_id BIGINT NOT NULL REFERENCES namespaces(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(namespace_id, name)
);

-- Multiple inheritance relationships between scopes
CREATE TABLE scope_parents (
    child_scope_id BIGINT NOT NULL REFERENCES scopes(id) ON DELETE CASCADE,
    parent_scope_id BIGINT NOT NULL REFERENCES scopes(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (child_scope_id, parent_scope_id),
    CONSTRAINT no_self_reference CHECK (child_scope_id != parent_scope_id)
);

CREATE INDEX idx_scope_parents_child ON scope_parents (child_scope_id);
CREATE INDEX idx_scope_parents_parent ON scope_parents (parent_scope_id);

-- Flattened ancestor arrays for O(1) hierarchy lookups
CREATE TABLE scope_hierarchy (
    scope_id BIGINT PRIMARY KEY REFERENCES scopes(id) ON DELETE CASCADE,
    ancestors BIGINT[] NOT NULL
);

CREATE INDEX idx_scope_hierarchy_ancestors ON scope_hierarchy USING GIN (ancestors);

-- Searchable content with pre-computed full-text vectors
CREATE TABLE knowledge (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    scope_id BIGINT NOT NULL REFERENCES scopes(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    context TEXT NOT NULL,
    task_size task_size_enum,
    
    -- Generated search vectors with weighted ranking
    content_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    context_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', context)) STORED,
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', context), 'A') || 
        setweight(to_tsvector('english', content), 'B')
    ) STORED,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_knowledge_scope_task ON knowledge (scope_id, task_size);
CREATE INDEX idx_knowledge_search_gin ON knowledge USING GIN (search_vector);

-- Conflict resolution with audit trail
CREATE TABLE knowledge_collisions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    active_knowledge_id BIGINT NOT NULL REFERENCES knowledge(id) ON DELETE CASCADE,
    suppressed_knowledge_ids BIGINT[] NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_collisions_active ON knowledge_collisions (active_knowledge_id);
CREATE INDEX idx_collisions_suppressed ON knowledge_collisions USING GIN (suppressed_knowledge_ids);

-- =============================================================================
-- MATERIALIZED VIEWS
-- =============================================================================

-- Pre-joined, collision-filtered knowledge for fast search
CREATE MATERIALIZED VIEW mv_active_knowledge_search AS
SELECT 
    k.id,
    k.scope_id,
    k.content,
    k.context,
    k.task_size,
    k.search_vector,
    s.name as scope_name,
    n.name as namespace_name,
    n.name || ':' || s.name as qualified_scope_name
FROM knowledge k
JOIN scopes s ON k.scope_id = s.id
JOIN namespaces n ON s.namespace_id = n.id
WHERE NOT EXISTS (
    SELECT 1 FROM knowledge_collisions kc 
    WHERE k.id = ANY(kc.suppressed_knowledge_ids)
);

CREATE UNIQUE INDEX idx_mv_active_knowledge_id ON mv_active_knowledge_search (id);
CREATE INDEX idx_mv_active_search_gin ON mv_active_knowledge_search USING GIN (search_vector);
CREATE INDEX idx_mv_active_scope_task ON mv_active_knowledge_search (scope_id, task_size);
CREATE INDEX idx_mv_active_qualified_scope ON mv_active_knowledge_search (qualified_scope_name);

-- =============================================================================
-- MCP ACTION FUNCTIONS
-- =============================================================================

-- Multi-query knowledge retrieval with scope inheritance
CREATE OR REPLACE FUNCTION get_task_context(
    query_terms TEXT[],
    target_scope TEXT,
    filter_task_size task_size_enum DEFAULT NULL
) RETURNS TABLE (
    qualified_scope_name TEXT,
    knowledge_id BIGINT,
    content TEXT
) AS $$
DECLARE
    ancestors_array BIGINT[];
BEGIN
    SELECT sh.ancestors INTO ancestors_array
    FROM scopes s
    JOIN namespaces n ON s.namespace_id = n.id
    JOIN scope_hierarchy sh ON s.id = sh.scope_id
    WHERE n.name || ':' || s.name = target_scope;
    
    IF ancestors_array IS NULL THEN
        RAISE EXCEPTION 'Scope not found: %', target_scope;
    END IF;
    
    RETURN QUERY
    WITH parsed_queries AS (
        SELECT 
            query_term,
            websearch_to_tsquery('english', query_term) as parsed_query
        FROM UNNEST(query_terms) as query_term
    ),
    ranked_results AS (
        SELECT 
            k.qualified_scope_name,
            k.id,
            k.content,
            ts_rank(k.search_vector, pq.parsed_query) as rank
        FROM mv_active_knowledge_search k
        CROSS JOIN parsed_queries pq
        WHERE 
            k.scope_id = ANY(ancestors_array)
            AND k.search_vector @@ pq.parsed_query
            AND (filter_task_size IS NULL OR k.task_size IS NULL OR k.task_size >= filter_task_size)
    ),
    filtered_results AS (
        SELECT * FROM ranked_results WHERE rank >= 0.1
    )
    SELECT 
        fr.qualified_scope_name,
        fr.id as knowledge_id,
        fr.content
    FROM filtered_results fr
    GROUP BY fr.qualified_scope_name, fr.id, fr.content
    ORDER BY MAX(fr.rank) DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- SCOPE HIERARCHY FUNCTIONS
-- =============================================================================

-- Returns default scope ID for any namespace
CREATE OR REPLACE FUNCTION get_default_scope_id(target_namespace_id BIGINT) RETURNS BIGINT AS $$
BEGIN
    RETURN (
        SELECT id 
        FROM scopes
        WHERE namespace_id = target_namespace_id AND name = 'default'
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- Returns global:default scope ID
CREATE OR REPLACE FUNCTION get_global_default_scope_id() RETURNS BIGINT AS $$
BEGIN
    RETURN get_default_scope_id((SELECT id FROM namespaces WHERE name = 'global'));
END;
$$ LANGUAGE plpgsql STABLE;

-- Calculates complete ancestor chain including global:default
CREATE OR REPLACE FUNCTION calculate_scope_ancestors(scope_id BIGINT) RETURNS BIGINT[] AS $$
DECLARE
    max_depth INTEGER;
BEGIN
    SELECT COUNT(*) INTO max_depth
    FROM scopes s
    WHERE s.namespace_id = (
        SELECT namespace_id FROM scopes WHERE id = scope_id
    );
    
    RETURN (
        WITH RECURSIVE ancestor_tree AS (
            SELECT scope_id as current_scope_id, 0 as level
            UNION ALL
            SELECT sp.parent_scope_id as current_scope_id, at.level + 1
            FROM ancestor_tree at
            JOIN scope_parents sp ON at.current_scope_id = sp.child_scope_id
            WHERE at.level < max_depth
        ),
        all_ancestors AS (
            SELECT current_scope_id FROM ancestor_tree
            UNION
            SELECT get_global_default_scope_id()
        )
        SELECT array_agg(current_scope_id) FROM all_ancestors
    );
END;
$$ LANGUAGE plpgsql;

-- Refreshes hierarchy cache for affected scopes and descendants
CREATE OR REPLACE FUNCTION refresh_scope_hierarchy() RETURNS TRIGGER AS $$
DECLARE
    target_child_id BIGINT;
BEGIN
    target_child_id := COALESCE(NEW.child_scope_id, OLD.child_scope_id);
    
    WITH RECURSIVE affected_scopes AS (
        SELECT target_child_id as scope_id
        UNION ALL
        SELECT sp.child_scope_id
        FROM affected_scopes af
        JOIN scope_parents sp ON af.scope_id = sp.parent_scope_id
    )
    INSERT INTO scope_hierarchy (scope_id, ancestors)
    SELECT scope_id, calculate_scope_ancestors(scope_id)
    FROM affected_scopes
    ON CONFLICT (scope_id) 
    DO UPDATE SET ancestors = calculate_scope_ancestors(scope_hierarchy.scope_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Creates hierarchy entry for new scopes
CREATE OR REPLACE FUNCTION create_scope_hierarchy_entry() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO scope_hierarchy (scope_id, ancestors)
    VALUES (NEW.id, calculate_scope_ancestors(NEW.id));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Creates default scope when namespace is created
CREATE OR REPLACE FUNCTION create_default_scope_on_namespace() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO scopes (namespace_id, name, description)
    VALUES (NEW.id, 'default', NEW.description || ' - default scope');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CONSTRAINT ENFORCEMENT FUNCTIONS
-- =============================================================================

-- Prevents circular dependencies in scope hierarchy
CREATE OR REPLACE FUNCTION prevent_circular_inheritance() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.child_scope_id = ANY(calculate_scope_ancestors(NEW.parent_scope_id)) THEN
        RAISE EXCEPTION 'Circular dependency detected: adding parent % to child % would create a cycle',
            NEW.parent_scope_id, NEW.child_scope_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Ensures all scopes inherit from their namespace default
CREATE OR REPLACE FUNCTION enforce_default_parent() RETURNS TRIGGER AS $$
DECLARE
    default_scope_id BIGINT;
BEGIN
    IF NEW.name = 'default' THEN
        RETURN NEW;
    END IF;
    
    default_scope_id := get_default_scope_id(NEW.namespace_id);
    
    IF default_scope_id IS NULL THEN
        RAISE EXCEPTION 'Default scope must exist before creating custom scopes';
    END IF;
    
    INSERT INTO scope_parents (child_scope_id, parent_scope_id)
    VALUES (NEW.id, default_scope_id)
    ON CONFLICT DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Prevents deletion of global namespace
CREATE OR REPLACE FUNCTION prevent_global_namespace_deletion() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.name = 'global' THEN
        RAISE EXCEPTION 'Cannot delete the global namespace';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Prevents direct deletion of default scopes (allows cascade)
CREATE OR REPLACE FUNCTION prevent_default_scope_deletion() RETURNS TRIGGER AS $$
BEGIN
    IF OLD.name = 'default' THEN
        IF EXISTS (SELECT 1 FROM namespaces WHERE id = OLD.namespace_id) THEN
            RAISE EXCEPTION 'Cannot delete the default scope directly';
        END IF;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Refreshes materialized view when base data changes
CREATE OR REPLACE FUNCTION refresh_active_knowledge_search() RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_knowledge_search;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Scope hierarchy maintenance
CREATE TRIGGER trigger_refresh_scope_hierarchy_parents
    AFTER INSERT OR UPDATE OR DELETE ON scope_parents
    FOR EACH ROW
    EXECUTE FUNCTION refresh_scope_hierarchy();

CREATE TRIGGER trigger_create_scope_hierarchy
    AFTER INSERT ON scopes
    FOR EACH ROW
    EXECUTE FUNCTION create_scope_hierarchy_entry();

CREATE TRIGGER trigger_create_default_scope
    AFTER INSERT ON namespaces
    FOR EACH ROW
    EXECUTE FUNCTION create_default_scope_on_namespace();

-- Constraint enforcement
CREATE TRIGGER trigger_prevent_circular_inheritance
    BEFORE INSERT OR UPDATE ON scope_parents
    FOR EACH ROW
    EXECUTE FUNCTION prevent_circular_inheritance();

CREATE TRIGGER trigger_enforce_default_parent
    AFTER INSERT ON scopes
    FOR EACH ROW
    EXECUTE FUNCTION enforce_default_parent();

CREATE TRIGGER trigger_prevent_global_namespace_deletion
    BEFORE DELETE ON namespaces
    FOR EACH ROW
    EXECUTE FUNCTION prevent_global_namespace_deletion();

CREATE TRIGGER trigger_prevent_default_scope_deletion
    BEFORE DELETE ON scopes
    FOR EACH ROW
    EXECUTE FUNCTION prevent_default_scope_deletion();

-- Materialized view refresh
CREATE TRIGGER trigger_refresh_active_knowledge
    AFTER INSERT OR UPDATE OR DELETE ON knowledge
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_active_knowledge_search();

CREATE TRIGGER trigger_refresh_active_knowledge_collision
    AFTER INSERT OR UPDATE OR DELETE ON knowledge_collisions
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_active_knowledge_search();

CREATE TRIGGER trigger_refresh_active_knowledge_scope_name
    AFTER UPDATE OF name ON scopes
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_active_knowledge_search();

CREATE TRIGGER trigger_refresh_active_knowledge_namespace_name
    AFTER UPDATE OF name ON namespaces
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_active_knowledge_search();

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

INSERT INTO namespaces (name, description) 
VALUES ('global', 'Universal knowledge accessible everywhere')
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- PERFORMANCE TUNING
-- =============================================================================

-- Aggressive autovacuum for frequently refreshed materialized view
ALTER MATERIALIZED VIEW mv_active_knowledge_search SET (
    autovacuum_enabled = true,
    autovacuum_vacuum_scale_factor = 0.1
);

-- =============================================================================
-- DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE namespaces IS 'Global organizational containers (e.g., acme, payments)';
COMMENT ON TABLE scopes IS 'Project boundaries within namespaces';
COMMENT ON TABLE scope_parents IS 'Multiple inheritance relationships between scopes';
COMMENT ON TABLE scope_hierarchy IS 'Flattened ancestor arrays for fast knowledge retrieval';
COMMENT ON TABLE knowledge IS 'Searchable content with pre-computed full-text search vectors';
COMMENT ON TABLE knowledge_collisions IS 'Conflict resolution audit trail for competing knowledge';

COMMENT ON MATERIALIZED VIEW mv_active_knowledge_search IS 'Pre-joined, collision-filtered knowledge for fast search';

COMMENT ON FUNCTION get_default_scope_id IS 'Returns default scope ID for any namespace';
COMMENT ON FUNCTION get_global_default_scope_id IS 'Returns global:default scope ID';
COMMENT ON FUNCTION get_task_context IS 'Multi-query knowledge retrieval with scope inheritance for MCP get_task_context action';
COMMENT ON FUNCTION enforce_default_parent IS 'Ensures all scopes inherit from default scope';
COMMENT ON FUNCTION prevent_global_namespace_deletion IS 'Prevents deletion of the global namespace';
COMMENT ON FUNCTION prevent_default_scope_deletion IS 'Prevents direct deletion of default scopes while allowing cascade deletion';