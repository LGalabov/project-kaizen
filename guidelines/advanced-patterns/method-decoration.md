# FastMCP Method Decoration Guidelines

## Critical Decoration Rules

### ❌ NEVER Decorate Methods Directly in Class Definition
```python
# WRONG - Do not do this
class MyClass:
    @mcp.tool  # This will not work correctly
    def add(self, x, y):
        return x + y
```

### ✅ ALWAYS Register Methods After Instance Creation
```python
# CORRECT - Register bound methods
class Calculator:
    def add(self, x, y):
        return x + y
    
    def multiply(self, x, y):
        return x * y

# Create instance then register methods
calc = Calculator()
mcp.tool(calc.add)
mcp.tool(calc.multiply)
```

## Instance Method Patterns

### Standard Instance Method Registration
```python
class DataProcessor:
    def __init__(self, config: dict):
        self.config = config
    
    def process_data(self, data: list[float]) -> dict:
        """Process data using instance configuration."""
        threshold = self.config.get("threshold", 0)
        filtered = [x for x in data if x > threshold]
        return {
            "original_count": len(data),
            "filtered_count": len(filtered),
            "average": sum(filtered) / len(filtered) if filtered else 0
        }

# Proper registration
processor = DataProcessor({"threshold": 10})
mcp.tool(processor.process_data)
```

### Multiple Instance Pattern
```python
class APIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
    
    def get_data(self, endpoint: str) -> dict:
        """Fetch data from API endpoint."""
        return self._make_request(f"{self.base_url}/{endpoint}")
    
    def post_data(self, endpoint: str, data: dict) -> dict:
        """Post data to API endpoint."""
        return self._make_request(f"{self.base_url}/{endpoint}", method="POST", data=data)

# Register multiple instances for different services
prod_client = APIClient("https://api.prod.com", "prod_key")
dev_client = APIClient("https://api.dev.com", "dev_key")

mcp.tool(prod_client.get_data, name="prod_get_data")
mcp.tool(dev_client.get_data, name="dev_get_data")
```

## Class Method Patterns

### ❌ Avoid Direct Class Method Decoration
```python
# PROBLEMATIC - Avoid this pattern
class MyClass:
    @mcp.tool  # This may cause issues
    @classmethod
    def from_string(cls, s):
        return cls(s)
```

### ✅ Register Class Methods After Definition
```python
class ConfigurableService:
    def __init__(self, setting: str):
        self.setting = setting
    
    @classmethod
    def from_config_file(cls, config_path: str):
        """Create service instance from configuration file."""
        with open(config_path, 'r') as f:
            config = json.load(f)
        return cls(config['setting'])
    
    @classmethod
    def get_default_config(cls) -> dict:
        """Get default configuration."""
        return {"setting": "default", "timeout": 30}

# Proper class method registration
mcp.tool(ConfigurableService.from_config_file)
mcp.tool(ConfigurableService.get_default_config)
```

### Class Method Factory Pattern
```python
class DatabaseConnection:
    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database
    
    @classmethod
    def postgres_connection(cls, host: str, database: str):
        """Create PostgreSQL connection."""
        return cls(host, 5432, database)
    
    @classmethod
    def mysql_connection(cls, host: str, database: str):
        """Create MySQL connection."""
        return cls(host, 3306, database)
    
    def execute_query(self, query: str) -> list:
        """Execute database query."""
        # Implementation here
        return []

# Register factory methods
mcp.tool(DatabaseConnection.postgres_connection)
mcp.tool(DatabaseConnection.mysql_connection)

# Also register instance methods if needed
# (after creating instances)
```

## Static Method Patterns

### Static Method Registration
```python
class MathUtils:
    @staticmethod
    def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate Euclidean distance between two points."""
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convert degrees to radians."""
        return degrees * 3.14159 / 180

# Register static methods (can be done directly)
mcp.tool(MathUtils.calculate_distance)
mcp.tool(MathUtils.degrees_to_radians)
```

### Utility Class Pattern
```python
class StringUtils:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        return text.strip().lower().replace("  ", " ")
    
    @staticmethod
    def extract_emails(text: str) -> list[str]:
        """Extract email addresses from text."""
        import re
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)

# Register all utility methods
mcp.tool(StringUtils.clean_text)
mcp.tool(StringUtils.extract_emails)
```

## Complex Decoration Patterns

### Service Class with Multiple Methods
```python
class FileService:
    def __init__(self, base_directory: str):
        self.base_dir = Path(base_directory)
    
    def read_file(self, filename: str) -> str:
        """Read file contents."""
        file_path = self.base_dir / filename
        return file_path.read_text()
    
    def write_file(self, filename: str, content: str) -> bool:
        """Write content to file."""
        file_path = self.base_dir / filename
        file_path.write_text(content)
        return True
    
    def list_files(self) -> list[str]:
        """List all files in directory."""
        return [f.name for f in self.base_dir.iterdir() if f.is_file()]
    
    @classmethod
    def temp_service(cls):
        """Create service for temporary directory."""
        import tempfile
        return cls(tempfile.gettempdir())

# Comprehensive registration
temp_service = FileService.temp_service()
user_service = FileService("/home/user/documents")

# Register instance methods with descriptive names
mcp.tool(temp_service.read_file, name="read_temp_file")
mcp.tool(temp_service.write_file, name="write_temp_file")
mcp.tool(user_service.read_file, name="read_user_file")
mcp.tool(user_service.write_file, name="write_user_file")

# Register shared methods
mcp.tool(temp_service.list_files, name="list_temp_files")
mcp.tool(user_service.list_files, name="list_user_files")
```

### Decorator Order Considerations
```python
class DecoratedService:
    def __init__(self, name: str):
        self.name = name
    
    def process_with_retry(self, data: str) -> str:
        """Process data with retry logic."""
        # Implementation with retry logic
        return f"Processed: {data}"
    
    @classmethod
    def create_default(cls):
        """Create service with default settings."""
        return cls("default")

# When combining with other decorators, register AFTER all decorations
service = DecoratedService.create_default()
mcp.tool(service.process_with_retry)
```

## Standards for AI Method Decoration

### Parameter Exposure Guidelines
- Never expose `self` parameter to LLM
- Never expose `cls` parameter to LLM
- Ensure method binding happens before registration
- Use descriptive tool names when registering multiple instances

### Best Practices
```python
class BestPracticeExample:
    def __init__(self, config: dict):
        self.config = config
        self._internal_state = {}
    
    def public_method(self, user_input: str) -> str:
        """Method that should be exposed to LLM."""
        return self._process_safely(user_input)
    
    def _private_method(self, data: str) -> str:
        """Private method - should NOT be registered."""
        return data.upper()

# Only register public methods
example = BestPracticeExample({"setting": "value"})
mcp.tool(example.public_method)
# DON'T register private methods: mcp.tool(example._private_method)
```

### Error Prevention
- Always create instances before registering methods
- Test method registration in isolation
- Verify that method signatures are properly exposed
- Ensure proper error handling within methods
- Use meaningful names for multiple instance registrations

### Testing Method Registration
```python
# Test that methods are properly registered
def test_method_registration():
    calc = Calculator()
    mcp.tool(calc.add, name="test_add")
    
    # Verify the tool is available
    tools = mcp.list_tools()
    assert "test_add" in [tool.name for tool in tools]
```