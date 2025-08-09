-- Test helper functions for resetting database to clean state
-- This file is only loaded during test setup, not in production

CREATE OR REPLACE FUNCTION reset_test_database() RETURNS void AS $$
BEGIN
    -- Disable protection triggers
    ALTER TABLE namespaces DISABLE TRIGGER trigger_prevent_global_namespace_deletion;
    ALTER TABLE scopes DISABLE TRIGGER trigger_prevent_default_scope_deletion;
    ALTER TABLE config DISABLE TRIGGER prevent_config_insert_delete_update;
    
    -- Clean all data (CASCADE handles everything)
    DELETE FROM namespaces;
    
    -- Re-insert global namespace (trigger creates default scope automatically)
    INSERT INTO namespaces (name, description) 
    VALUES ('global', 'Universal knowledge accessible everywhere');
    
    -- Re-enable protection triggers
    ALTER TABLE namespaces ENABLE TRIGGER trigger_prevent_global_namespace_deletion;
    ALTER TABLE scopes ENABLE TRIGGER trigger_prevent_default_scope_deletion;
    ALTER TABLE config ENABLE TRIGGER prevent_config_insert_delete_update;
    
    -- Reset all config values to defaults
    PERFORM reset_config('search.relevance_threshold');
    PERFORM reset_config('search.language');
    PERFORM reset_config('search.max_results');
    PERFORM reset_config('search.context_weight');
    PERFORM reset_config('search.content_weight');
    
    -- Refresh materialized view
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_knowledge_search;
END;
$$ LANGUAGE plpgsql;
