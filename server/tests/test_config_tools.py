"""Tests for configuration MCP tools."""

from typing import Any

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

# ============================================================================
# 1. Config Query Tests
# ============================================================================

async def test_list_config_default_state(mcp_client: Client[Any]) -> None:
    """Lists all configuration settings in the default state.
    Verifies all expected config keys are present with correct types and defaults.
    Value: Baseline test for configuration system initialization."""
    async with mcp_client as client:
        result = await client.call_tool("list_config", {})
        
        configs = result.data.get("configs", {})
        assert len(configs) > 0
        
        # Verify essential config keys exist
        expected_keys = [
            "search.max_results",
            "search.content_weight",
            "search.context_weight"
        ]
        
        for key in expected_keys:
            assert key in configs
            config = configs[key]
            assert "value" in config
            assert "default" in config
            assert "type" in config
            assert "description" in config
            # Default state: value should equal default
            assert config["value"] == config["default"]


async def test_list_config_structure(mcp_client: Client[Any]) -> None:
    """Verifies the structure of configuration data returned.
    Checks all required fields are present and have expected types.
    Value: Validates API contract for config listing."""
    async with mcp_client as client:
        result = await client.call_tool("list_config", {})
        
        configs = result.data.get("configs", {})
        
        for key, config in configs.items():
            # Verify key format (should be dot-notation)
            assert "." in key or key in ["version", "environment"]
            
            # Verify all required fields
            assert isinstance(config["value"], str | int | float | bool | type(None))
            assert isinstance(config["default"], str | int | float | bool | type(None))
            assert config["type"] in ["string", "integer", "float", "boolean", "regconfig"]
            assert isinstance(config["description"], str)
            assert len(config["description"]) > 0


# ============================================================================
# 2. Config Update Tests
# ============================================================================

async def test_update_config_integer(mcp_client: Client[Any]) -> None:
    """Updates an integer configuration value.
    Verifies the value changes and returns old/new values.
    Value: Tests type validation and update mechanism for integers."""
    async with mcp_client as client:
        # Get initial value
        list_result = await client.call_tool("list_config", {})
        initial_value = list_result.data["configs"]["search.max_results"]["value"]
        
        # Update to new value
        new_value = "50"
        result = await client.call_tool("update_config", {
            "key": "search.max_results",
            "value": new_value
        })
        
        assert result.data["old_value"] == str(initial_value)
        assert result.data["new_value"] == new_value
        
        # Verify change persisted
        list_result = await client.call_tool("list_config", {})
        assert str(list_result.data["configs"]["search.max_results"]["value"]) == new_value


async def test_update_config_float(mcp_client: Client[Any]) -> None:
    """Updates a float configuration value.
    Verifies decimal values are handled correctly.
    Value: Tests type validation for floating-point numbers."""
    async with mcp_client as client:
        # Update content_weight to new float value
        new_value = "0.75"
        result = await client.call_tool("update_config", {
            "key": "search.content_weight",
            "value": new_value
        })
        
        assert result.data["new_value"] == new_value
        
        # Verify it was stored correctly
        list_result = await client.call_tool("list_config", {})
        assert str(list_result.data["configs"]["search.content_weight"]["value"]) == new_value



async def test_update_config_invalid_type(mcp_client: Client[Any]) -> None:
    """Attempts to update config with invalid type value.
    Value: Ensures type validation prevents corruption."""
    async with mcp_client as client:
        # Try to set integer config to a non-numeric value
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("update_config", {
                "key": "search.max_results",
                "value": "not-a-number"
            })
        assert "invalid" in str(exc_info.value).lower() or "type" in str(exc_info.value).lower()


async def test_update_config_nonexistent_key(mcp_client: Client[Any]) -> None:
    """Attempts to update non-existent configuration key.
    Value: Validates error handling for unknown keys."""
    async with mcp_client as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("update_config", {
                "key": "nonexistent.config.key",
                "value": "some-value"
            })
        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()


async def test_update_config_empty_key(mcp_client: Client[Any]) -> None:
    """Attempts to update config with empty key.
    Value: Validates input validation for required fields."""
    async with mcp_client as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("update_config", {
                "key": "",
                "value": "some-value"
            })
        assert "cannot be empty" in str(exc_info.value).lower()


async def test_update_config_null_value(mcp_client: Client[Any]) -> None:
    """Attempts to update config with null value.
    Value: Ensures null values are properly rejected."""
    async with mcp_client as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("update_config", {
                "key": "search.max_results",
                "value": None
            })
        # FastMCP validates that None is not a valid string type
        assert ("none is not of type" in str(exc_info.value).lower() or 
                "input validation error" in str(exc_info.value).lower())


# ============================================================================
# 3. Config Reset Tests
# ============================================================================

async def test_reset_config_to_default(mcp_client: Client[Any]) -> None:
    """Changes config value then resets to default.
    Verifies reset restores original default value.
    Value: Tests recovery mechanism for misconfigurations."""
    async with mcp_client as client:
        # Get default value
        list_result = await client.call_tool("list_config", {})
        default_value = list_result.data["configs"]["search.max_results"]["default"]
        
        # Change to a different value
        await client.call_tool("update_config", {
            "key": "search.max_results",
            "value": "999"
        })
        
        # Verify it changed
        list_result = await client.call_tool("list_config", {})
        assert str(list_result.data["configs"]["search.max_results"]["value"]) == "999"
        
        # Reset to default
        result = await client.call_tool("reset_config", {
            "key": "search.max_results"
        })
        
        assert str(result.data["value"]) == str(default_value)
        
        # Verify it's back to default
        list_result = await client.call_tool("list_config", {})
        assert list_result.data["configs"]["search.max_results"]["value"] == default_value


async def test_reset_config_already_default(mcp_client: Client[Any]) -> None:
    """Resets config that's already at default value.
    Value: Ensures idempotent behavior of reset operation."""
    async with mcp_client as client:
        # Get current (default) value
        list_result = await client.call_tool("list_config", {})
        default_value = list_result.data["configs"]["search.max_results"]["default"]
        
        # Reset when already at default
        result = await client.call_tool("reset_config", {
            "key": "search.max_results"
        })
        
        assert str(result.data["value"]) == str(default_value)
        
        # Should still be at default
        list_result = await client.call_tool("list_config", {})
        assert list_result.data["configs"]["search.max_results"]["value"] == default_value


async def test_reset_config_nonexistent_key(mcp_client: Client[Any]) -> None:
    """Attempts to reset non-existent configuration key.
    Value: Validates error handling for unknown keys."""
    async with mcp_client as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("reset_config", {
                "key": "nonexistent.config.key"
            })
        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()


async def test_reset_config_empty_key(mcp_client: Client[Any]) -> None:
    """Attempts to reset config with empty key.
    Value: Validates input validation for required fields."""
    async with mcp_client as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("reset_config", {
                "key": ""
            })
        assert "cannot be empty" in str(exc_info.value).lower()


# ============================================================================
# 4. Edge Case Tests
# ============================================================================

async def test_config_special_characters_in_values(mcp_client: Client[Any]) -> None:
    """Tests config values with special characters (if string configs exist).
    Value: Ensures proper escaping and storage."""
    async with mcp_client as client:
        # This test would apply if there are string-type configs
        # that accept arbitrary text
        list_result = await client.call_tool("list_config", {})
        
        # Find a string config if any
        string_configs = [
            key for key, cfg in list_result.data["configs"].items() 
            if cfg["type"] == "string"
        ]
        
        if string_configs:
            test_values = [
                "value with spaces",
                "value-with-hyphens",
                "value_with_underscores",
                "value.with.dots",
                "value/with/slashes"
            ]
            
            for value in test_values:
                try:
                    await client.call_tool("update_config", {
                        "key": string_configs[0],
                        "value": value
                    })
                    # If successful, verify it was stored
                    list_result = await client.call_tool("list_config", {})
                    assert list_result.data["configs"][string_configs[0]]["value"] == value
                except ToolError:
                    # Some values might be invalid based on config constraints
                    pass


# ============================================================================
# 5. Error Recovery Tests
# ============================================================================

async def test_config_recovery_from_invalid_update(mcp_client: Client[Any]) -> None:
    """Attempts invalid update, verifies config remains unchanged.
    Value: Ensures failed updates don't corrupt configuration."""
    async with mcp_client as client:
        # Get initial value
        list_result = await client.call_tool("list_config", {})
        initial_value = list_result.data["configs"]["search.max_results"]["value"]
        
        # Attempt invalid update
        with pytest.raises(Exception):  # noqa: B017
            await client.call_tool("update_config", {
                "key": "search.max_results",
                "value": "invalid-integer"
            })
        
        # Verify value unchanged
        list_result = await client.call_tool("list_config", {})
        assert list_result.data["configs"]["search.max_results"]["value"] == initial_value


async def test_config_validation_messages(mcp_client: Client[Any]) -> None:
    """Tests that validation errors provide helpful messages.
    Value: Ensures good developer experience with clear errors."""
    async with mcp_client as client:
        # Test various invalid scenarios
        test_cases = [
            ("", "some-value", "cannot be empty"),
            ("search.max_results", "not-a-number", "invalid"),
            ("fake.config", "value", "not found")
        ]
        
        for key, value, expected_message in test_cases:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool("update_config", {
                    "key": key,
                    "value": value
                })
            assert expected_message in str(exc_info.value).lower()
