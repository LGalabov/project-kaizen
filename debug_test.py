#!/usr/bin/env python3

import asyncio
import os
import sys

# Add the server source directory to the path
sys.path.insert(0, '/Users/lyubomirgalabov/Workspace/misc/project-kaizen/server/src')

from kaizen_mcp import database

async def debug_cascade_test():
    """Debug the cascade test step by step."""
    print("Initializing database...")
    
    # Set up test database
    os.environ["POSTGRES_DB"] = "test"
    os.environ["POSTGRES_HOST"] = "localhost" 
    os.environ["POSTGRES_PORT"] = "62299"  # Use a test port
    
    try:
        await database.initialize(test_mode=True)
        print("✓ Database initialized")
        
        # Step 1: Create namespace
        print("\nStep 1: Creating namespace...")
        ns_result = await database.create_namespace("cascade-test", "Test namespace")
        print(f"Namespace result: {ns_result}")
        
        # Step 2: Create scope
        print("\nStep 2: Creating scope...")
        scope_result = await database.create_scope("cascade-test:test-scope", "Test scope", [])
        print(f"Scope result: {scope_result}")
        
        # Step 3: Write knowledge
        print("\nStep 3: Writing knowledge...")
        try:
            knowledge_result = await database.write_knowledge(
                "cascade-test:test-scope", 
                "Test knowledge content", 
                "test cascade context", 
                None
            )
            print(f"Knowledge result: {knowledge_result}")
        except Exception as e:
            print(f"❌ Knowledge creation failed: {e}")
            return
        
        # Step 4: Check what exists before deletion
        print("\nStep 4: Checking current state...")
        ns_details = await database.get_namespace_details("cascade-test")
        print(f"Namespace details: {ns_details}")
        
        # Step 5: Delete namespace and check counts
        print("\nStep 5: Deleting namespace...")
        delete_result = await database.delete_namespace("cascade-test")
        print(f"Delete result: {delete_result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await database.close()

if __name__ == "__main__":
    asyncio.run(debug_cascade_test())