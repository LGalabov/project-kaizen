-- Project Kaizen - PostgreSQL Schema for MCP Knowledge Management
-- Optimized for multi-tenant scope hierarchy with full-text search

CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE TYPE task_size_enum AS ENUM ('XS', 'S', 'M', 'L', 'XL');
CREATE TYPE config_type_enum AS ENUM ('text', 'integer', 'float', 'boolean', 'regconfig');

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
    
    -- Generated search vector with weighted ranking
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
CREATE TABLE knowledge_conflicts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    active_knowledge_id BIGINT NOT NULL REFERENCES knowledge(id) ON DELETE CASCADE,
    suppressed_knowledge_ids BIGINT[] NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conflicts_active ON knowledge_conflicts (active_knowledge_id);
CREATE INDEX idx_conflicts_suppressed ON knowledge_conflicts USING GIN (suppressed_knowledge_ids);

-- Global runtime configuration
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    default_value TEXT NOT NULL,
    value_type config_type_enum NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- MATERIALIZED VIEWS
-- =============================================================================

-- Pre-joined, conflict-filtered knowledge for fast search
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
    SELECT 1 FROM knowledge_conflicts kc 
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
CREATE OR REPLACE FUNCTION search_knowledge_base(
    query_terms TEXT[],
    target_scope TEXT,
    filter_task_size task_size_enum DEFAULT NULL
) RETURNS TABLE (
    qualified_scope_name TEXT,
    knowledge_id BIGINT,
    content TEXT,
    relevance_rank REAL
) AS $$
DECLARE
    ancestors_array BIGINT[];
    relevance_threshold DOUBLE PRECISION;
    search_language regconfig;
    max_results INTEGER;
    context_weight REAL;
    content_weight REAL;
BEGIN
    SELECT sh.ancestors INTO ancestors_array
    FROM scopes s
    JOIN namespaces n ON s.namespace_id = n.id
    JOIN scope_hierarchy sh ON s.id = sh.scope_id
    WHERE n.name || ':' || s.name = target_scope;
    
    IF ancestors_array IS NULL THEN
        RAISE EXCEPTION 'Scope "%" does not exist. Please verify the scope name format is "namespace:scope".', target_scope;
    END IF;
    
    -- Load configuration values
    relevance_threshold := get_config_float('search.relevance_threshold');
    search_language := get_config_regconfig('search.language');
    max_results := get_config_integer('search.max_results');
    context_weight := get_config_float('search.context_weight');
    content_weight := get_config_float('search.content_weight');
    
    RETURN QUERY
    WITH parsed_queries AS (
        SELECT 
            query_term,
            websearch_to_tsquery(search_language, query_term) as parsed_query
        FROM UNNEST(query_terms) as query_term
    ),
    ranked_results AS (
        SELECT 
            k.qualified_scope_name,
            k.id,
            k.content,
            ts_rank(ARRAY[0.1, 0.2, content_weight, context_weight], k.search_vector, pq.parsed_query) as rank
        FROM mv_active_knowledge_search k
        CROSS JOIN parsed_queries pq
        WHERE 
            k.scope_id = ANY(ancestors_array)
            AND k.search_vector @@ pq.parsed_query
            AND (filter_task_size IS NULL OR k.task_size IS NULL OR k.task_size >= filter_task_size)
    ),
    filtered_results AS (
        SELECT * FROM ranked_results WHERE rank >= relevance_threshold
    )
    SELECT 
        fr.qualified_scope_name,
        fr.id as knowledge_id,
        fr.content,
        MAX(fr.rank) as relevance_rank
    FROM filtered_results fr
    GROUP BY fr.qualified_scope_name, fr.id, fr.content
    ORDER BY MAX(fr.rank) DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CONFIGURATION FUNCTIONS
-- =============================================================================

-- Internal helper function to get config with type validation
CREATE OR REPLACE FUNCTION get_config_internal(
    config_key TEXT, 
    expected_type config_type_enum DEFAULT NULL
) RETURNS TEXT AS $$
DECLARE
    config_value TEXT;
    actual_type config_type_enum;
BEGIN
    SELECT value, value_type INTO config_value, actual_type 
    FROM config WHERE key = config_key;
    
    IF config_value IS NULL THEN
        RAISE EXCEPTION 'Configuration key "%" does not exist. Available keys can be found by querying the config table.', config_key;
    END IF;
    
    -- Type validation if expected_type is specified
    IF expected_type IS NOT NULL AND actual_type != expected_type THEN
        RAISE EXCEPTION 'Configuration key "%" is of type % but % was requested. Use get_config_%() function instead.', 
                       config_key, actual_type, expected_type, expected_type;
    END IF;
    
    RETURN config_value;
END;
$$ LANGUAGE plpgsql STABLE;

-- Public accessor functions
CREATE OR REPLACE FUNCTION get_config_text(config_key TEXT) 
RETURNS TEXT AS $$
BEGIN
    RETURN get_config_internal(config_key);
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION get_config_integer(config_key TEXT) 
RETURNS INTEGER AS $$
BEGIN
    RETURN get_config_internal(config_key, 'integer')::INTEGER;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION get_config_float(config_key TEXT) 
RETURNS DOUBLE PRECISION AS $$
BEGIN
    RETURN get_config_internal(config_key, 'float')::DOUBLE PRECISION;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION get_config_boolean(config_key TEXT) 
RETURNS BOOLEAN AS $$
BEGIN
    RETURN get_config_internal(config_key, 'boolean')::BOOLEAN;
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION get_config_regconfig(config_key TEXT) 
RETURNS regconfig AS $$
BEGIN
    RETURN get_config_internal(config_key, 'regconfig')::regconfig;
END;
$$ LANGUAGE plpgsql STABLE;

-- Update function
CREATE OR REPLACE FUNCTION update_config(config_key TEXT, config_value TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE config 
    SET value = config_value, updated_at = NOW()
    WHERE key = config_key;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Configuration key "%" does not exist and cannot be created. Only existing configuration values can be updated.', config_key;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Reset configuration to default value
CREATE OR REPLACE FUNCTION reset_config(config_key TEXT)
RETURNS TEXT AS $$
DECLARE
    default_val TEXT;
BEGIN
    UPDATE config 
    SET value = default_value, updated_at = NOW()
    WHERE key = config_key
    RETURNING default_value INTO default_val;
    
    IF default_val IS NULL THEN
        RAISE EXCEPTION 'Configuration key "%" does not exist', config_key;
    END IF;
    
    RETURN default_val;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- SCOPE HIERARCHY FUNCTIONS
-- =============================================================================

-- Returns default scope ID for any namespace
CREATE OR REPLACE FUNCTION get_default_scope_id(target_namespace TEXT) RETURNS BIGINT AS $$
BEGIN
    RETURN (
        SELECT s.id 
        FROM scopes s
        JOIN namespaces n ON s.namespace_id = n.id
        WHERE n.name = target_namespace AND s.name = 'default'
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- Returns global:default scope ID
CREATE OR REPLACE FUNCTION get_global_default_scope_id() RETURNS BIGINT AS $$
BEGIN
    RETURN get_default_scope_id('global');
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

-- Adds parent relationships to a scope (keeps existing parents)
CREATE OR REPLACE FUNCTION add_scope_parents(
    target_scope TEXT,
    parent_scope_names TEXT[]
) RETURNS TEXT[] AS $$
BEGIN
    -- Add new parent relationships directly using canonical names
    IF parent_scope_names IS NOT NULL AND array_length(parent_scope_names, 1) > 0 THEN
        INSERT INTO scope_parents (child_scope_id, parent_scope_id)
        SELECT cs.id, ps.id
        FROM scopes cs
        JOIN namespaces cn ON cs.namespace_id = cn.id
        CROSS JOIN unnest(parent_scope_names) AS parent_name
        JOIN scopes ps ON ps.id != cs.id
        JOIN namespaces pn ON ps.namespace_id = pn.id
        WHERE cn.name || ':' || cs.name = target_scope
          AND pn.name || ':' || ps.name = parent_name
        ON CONFLICT DO NOTHING;
    END IF;
    
    -- Return all current parents
    RETURN (
        SELECT array_agg(pn.name || ':' || ps.name ORDER BY pn.name || ':' || ps.name)
        FROM scope_parents sp
        JOIN scopes cs ON sp.child_scope_id = cs.id
        JOIN namespaces cn ON cs.namespace_id = cn.id
        JOIN scopes ps ON sp.parent_scope_id = ps.id
        JOIN namespaces pn ON ps.namespace_id = pn.id
        WHERE cn.name || ':' || cs.name = target_scope
    );
END;
$$ LANGUAGE plpgsql;

-- Removes a parent relationship from a scope
CREATE OR REPLACE FUNCTION remove_scope_parent(
    target_scope TEXT,
    parent_scope_name TEXT
) RETURNS TEXT[] AS $$
BEGIN
    -- Remove the parent relationship directly using canonical names
    DELETE FROM scope_parents
    WHERE (child_scope_id, parent_scope_id) IN (
        SELECT cs.id, ps.id
        FROM scopes cs
        JOIN namespaces cn ON cs.namespace_id = cn.id
        JOIN scopes ps ON ps.id != cs.id
        JOIN namespaces pn ON ps.namespace_id = pn.id
        WHERE cn.name || ':' || cs.name = target_scope
          AND pn.name || ':' || ps.name = parent_scope_name
    );
    
    -- Return remaining parents
    RETURN (
        SELECT array_agg(pn.name || ':' || ps.name ORDER BY pn.name || ':' || ps.name)
        FROM scope_parents sp
        JOIN scopes cs ON sp.child_scope_id = cs.id
        JOIN namespaces cn ON cs.namespace_id = cn.id
        JOIN scopes ps ON sp.parent_scope_id = ps.id
        JOIN namespaces pn ON ps.namespace_id = pn.id
        WHERE cn.name || ':' || cs.name = target_scope
    );
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGER FUNCTIONS
-- =============================================================================

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
    ),
    existing_affected_scopes AS (
        SELECT af.scope_id
        FROM affected_scopes af
        WHERE EXISTS (SELECT 1 FROM scopes s WHERE s.id = af.scope_id)
    )
    INSERT INTO scope_hierarchy (scope_id, ancestors)
    SELECT scope_id, calculate_scope_ancestors(scope_id)
    FROM existing_affected_scopes
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
DECLARE
    parent_ancestors BIGINT[];
BEGIN
    -- Get parent scope ancestors using ID directly
    parent_ancestors := calculate_scope_ancestors(NEW.parent_scope_id);
    
    -- Check if child would create circular reference
    IF NEW.child_scope_id = ANY(parent_ancestors) THEN
        RAISE EXCEPTION 'Cannot add parent scope % to child scope % - this would create a circular dependency in the scope hierarchy.', 
            NEW.parent_scope_id, NEW.child_scope_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Ensures all scopes inherit from their namespace default
CREATE OR REPLACE FUNCTION enforce_default_parent() RETURNS TRIGGER AS $$
DECLARE
    namespace_name TEXT;
    default_scope_id BIGINT;
BEGIN
    IF NEW.name = 'default' THEN
        RETURN NEW;
    END IF;
    
    -- Get namespace name for the new scope
    SELECT name INTO namespace_name FROM namespaces WHERE id = NEW.namespace_id;
    
    -- Get default scope ID using namespace name
    default_scope_id := get_default_scope_id(namespace_name);
    
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

-- Configuration validation and protection
CREATE OR REPLACE FUNCTION validate_config_type() RETURNS TRIGGER AS $$
BEGIN
    BEGIN
        CASE NEW.value_type
            WHEN 'text' THEN
                NULL;
            WHEN 'integer' THEN
                PERFORM NEW.value::INTEGER;
            WHEN 'float' THEN
                PERFORM NEW.value::DOUBLE PRECISION;
            WHEN 'boolean' THEN
                PERFORM NEW.value::BOOLEAN;
            WHEN 'regconfig' THEN
                PERFORM NEW.value::regconfig;
        END CASE;
    EXCEPTION
        WHEN invalid_text_representation THEN
            RAISE EXCEPTION 'Configuration value "%" is invalid for type %. Please provide a valid % value.', NEW.value, NEW.value_type, NEW.value_type;
        WHEN numeric_value_out_of_range THEN
            RAISE EXCEPTION 'Configuration value "%" is out of range for type %. Please provide a valid % value.', NEW.value, NEW.value_type, NEW.value_type;
    END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION prevent_config_changes() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        RAISE EXCEPTION 'Configuration keys cannot be inserted. Use update_config() to modify existing configuration values only.';
    ELSIF TG_OP = 'DELETE' THEN
        RAISE EXCEPTION 'Configuration keys cannot be deleted. Use update_config() to modify existing configuration values only.';
    ELSIF TG_OP = 'UPDATE' THEN
        -- Only allow changes to value and updated_at columns
        IF OLD.key != NEW.key THEN
            RAISE EXCEPTION 'Configuration key cannot be modified. Use update_config() to change the value only.';
        END IF;
        IF OLD.value_type != NEW.value_type THEN
            RAISE EXCEPTION 'Configuration value_type cannot be modified. Use update_config() to change the value only.';
        END IF;
        IF OLD.description != NEW.description THEN
            RAISE EXCEPTION 'Configuration description cannot be modified. Use update_config() to change the value only.';
        END IF;
        IF OLD.default_value != NEW.default_value THEN
            RAISE EXCEPTION 'Configuration default_value cannot be modified. Defaults are immutable.';
        END IF;
    END IF;
    RETURN NEW;
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

CREATE TRIGGER trigger_refresh_active_knowledge_conflict
    AFTER INSERT OR UPDATE OR DELETE ON knowledge_conflicts
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_active_knowledge_search();

-- Configuration protection
CREATE TRIGGER validate_config_type_trigger
    BEFORE INSERT OR UPDATE ON config
    FOR EACH ROW
    EXECUTE FUNCTION validate_config_type();

CREATE TRIGGER prevent_config_insert_delete_update
    BEFORE INSERT OR DELETE OR UPDATE ON config
    FOR EACH ROW
    EXECUTE FUNCTION prevent_config_changes();

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

-- Initial configuration values (disable protection trigger for initial data)
ALTER TABLE config DISABLE TRIGGER prevent_config_insert_delete_update;
INSERT INTO config (key, value, default_value, value_type, description) VALUES
('search.relevance_threshold', '0.4', '0.4', 'float', 'Minimum ts_rank score for search results'),
('search.language', 'english', 'english', 'regconfig', 'Full-text search language configuration'),
('search.max_results', '50', '50', 'integer', 'Maximum number of results per query'),
('search.context_weight', '1.0', '1.0', 'float', 'Weight for context field (A label) in search ranking'),
('search.content_weight', '0.4', '0.4', 'float', 'Weight for content field (B label) in search ranking');
ALTER TABLE config ENABLE TRIGGER prevent_config_insert_delete_update;

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
COMMENT ON TABLE knowledge_conflicts IS 'Conflict resolution audit trail for competing knowledge';
COMMENT ON TABLE config IS 'Global runtime configuration with type safety - only value updates allowed';

COMMENT ON MATERIALIZED VIEW mv_active_knowledge_search IS 'Pre-joined, conflict-filtered knowledge for fast search';

COMMENT ON FUNCTION get_default_scope_id IS 'Returns default scope ID for any namespace';
COMMENT ON FUNCTION get_global_default_scope_id IS 'Returns global:default scope ID';
COMMENT ON FUNCTION calculate_scope_ancestors IS 'Calculates complete ancestor chain including global:default for scope ID';
COMMENT ON FUNCTION add_scope_parents IS 'Adds parent relationships to a scope without removing existing ones';
COMMENT ON FUNCTION remove_scope_parent IS 'Removes a specific parent relationship from a scope';
COMMENT ON FUNCTION search_knowledge_base IS 'Multi-query knowledge retrieval with scope inheritance and relevance ranking';
COMMENT ON FUNCTION enforce_default_parent IS 'Ensures all scopes inherit from default scope';
COMMENT ON FUNCTION prevent_global_namespace_deletion IS 'Prevents deletion of the global namespace';
COMMENT ON FUNCTION prevent_default_scope_deletion IS 'Prevents direct deletion of default scopes while allowing cascade deletion';

COMMENT ON FUNCTION get_config_internal IS 'Internal helper for configuration retrieval with optional type validation';
COMMENT ON FUNCTION get_config_text IS 'Get configuration value as text - works for all types';
COMMENT ON FUNCTION get_config_integer IS 'Get configuration value as integer - validates type';
COMMENT ON FUNCTION get_config_float IS 'Get configuration value as float - validates type';
COMMENT ON FUNCTION get_config_boolean IS 'Get configuration value as boolean - validates type';
COMMENT ON FUNCTION get_config_regconfig IS 'Get configuration value as regconfig - validates type';
COMMENT ON FUNCTION update_config IS 'Update configuration value with type validation - only value changes allowed';
COMMENT ON FUNCTION reset_config IS 'Reset configuration value to its default';
COMMENT ON FUNCTION validate_config_type IS 'Validates configuration values match their declared types';
COMMENT ON FUNCTION prevent_config_changes IS 'Prevents insert/delete and protects key/type/description from changes';
