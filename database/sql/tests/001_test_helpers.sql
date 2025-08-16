-- Test helper functions for resetting database to clean state
-- depends: 001_initial_schema
-- This file is only loaded during test setup, not in production

CREATE OR REPLACE FUNCTION reset_test_database() RETURNS void AS $$
BEGIN
    -- Disable protection triggers
    ALTER TABLE namespaces DISABLE TRIGGER trigger_prevent_global_namespace_deletion;
    ALTER TABLE scopes DISABLE TRIGGER trigger_prevent_default_scope_deletion;
    
    -- Clean all data (CASCADE handles everything)
    DELETE FROM namespaces;
    
    -- Re-insert global namespace (trigger creates default scope automatically)
    INSERT INTO namespaces (name, description) 
    VALUES ('global', 'Universal knowledge accessible everywhere');
    
    -- Re-enable protection triggers
    ALTER TABLE namespaces ENABLE TRIGGER trigger_prevent_global_namespace_deletion;
    ALTER TABLE scopes ENABLE TRIGGER trigger_prevent_default_scope_deletion;
    
    -- Reset all config values to defaults
    UPDATE config SET value = default_value, updated_at = NOW();
    
    -- Refresh materialized view
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_knowledge_search;
END;
$$ LANGUAGE plpgsql;
