from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration."""
    
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5453, description="Database port")
    database: str = Field(default="kaizen_knowledge", description="Database name")
    user: str = Field(default="kaizen_user", description="Database user")
    password: str = Field(default="kaizen_password", description="Database password")
    
    min_connections: int = Field(default=1, description="Minimum connection pool size")
    max_connections: int = Field(default=5, description="Maximum connection pool size")
    
    @property
    def dsn(self) -> str:
        """Get PostgreSQL connection DSN."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class MCPSettings(BaseSettings):
    """MCP server configuration."""
    
    name: str = Field(default="project-kaizen", description="MCP server name")
    version: str = Field(default="0.1.0", description="MCP server version")


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
    )
    
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Enable debug mode")


# Global settings instance
settings = Settings()
