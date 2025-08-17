-- MCP Knowledge Base Structure for Python and KaizenMCP Development
-- depends: 001_initial_schema
-- Domain: Model Context Protocol (MCP) development with Python and FastMCP

-- Create python namespace
INSERT INTO namespaces (name, description) 
VALUES ('python', 'Python programming language development knowledge')
ON CONFLICT (name) DO NOTHING;

-- Create kaizen-mcp namespace  
INSERT INTO namespaces (name, description)
VALUES ('kaizen-mcp', 'KaizenMCP knowledge management system development')
ON CONFLICT (name) DO NOTHING;

-- Create scope hierarchy and inheritance relationships
DO $$
DECLARE
    global_ns_id BIGINT;
    python_ns_id BIGINT;
    kaizen_mcp_ns_id BIGINT;
    global_default_scope_id BIGINT;
    python_default_scope_id BIGINT;
    python_fastmcp_scope_id BIGINT;
    kaizen_mcp_default_scope_id BIGINT;
    kaizen_mcp_server_scope_id BIGINT;
    kaizen_mcp_database_scope_id BIGINT;
    kaizen_mcp_deployment_scope_id BIGINT;
BEGIN
    -- Get namespace IDs
    SELECT id INTO global_ns_id FROM namespaces WHERE name = 'global';
    SELECT id INTO python_ns_id FROM namespaces WHERE name = 'python';
    SELECT id INTO kaizen_mcp_ns_id FROM namespaces WHERE name = 'kaizen-mcp';
    
    -- Get global default scope ID
    SELECT id INTO global_default_scope_id FROM scopes WHERE namespace_id = global_ns_id AND name = 'default';
    
    -- Get python default scope ID (auto-created)
    SELECT id INTO python_default_scope_id FROM scopes WHERE namespace_id = python_ns_id AND name = 'default';
    
    -- Create python:fastmcp scope
    INSERT INTO scopes (namespace_id, name, description) VALUES
    (python_ns_id, 'fastmcp', 'FastMCP framework development for Python MCP servers')
    ON CONFLICT (namespace_id, name) DO NOTHING;
    
    SELECT id INTO python_fastmcp_scope_id FROM scopes WHERE namespace_id = python_ns_id AND name = 'fastmcp';
    
    -- Add inheritance: python:fastmcp inherits from python:default
    INSERT INTO scope_parents (child_scope_id, parent_scope_id) VALUES
    (python_fastmcp_scope_id, python_default_scope_id)
    ON CONFLICT (child_scope_id, parent_scope_id) DO NOTHING;
    
    -- Get kaizen-mcp default scope ID (auto-created)
    SELECT id INTO kaizen_mcp_default_scope_id FROM scopes WHERE namespace_id = kaizen_mcp_ns_id AND name = 'default';
    
    -- Create kaizen-mcp specialized scopes
    INSERT INTO scopes (namespace_id, name, description) VALUES
    (kaizen_mcp_ns_id, 'server', 'KaizenMCP MCP server implementation and tools'),
    (kaizen_mcp_ns_id, 'database', 'KaizenMCP database schema and knowledge storage'),
    (kaizen_mcp_ns_id, 'deployment', 'KaizenMCP production deployment and operations')
    ON CONFLICT (namespace_id, name) DO NOTHING;
    
    -- Get the new scope IDs
    SELECT id INTO kaizen_mcp_server_scope_id FROM scopes WHERE namespace_id = kaizen_mcp_ns_id AND name = 'server';
    SELECT id INTO kaizen_mcp_database_scope_id FROM scopes WHERE namespace_id = kaizen_mcp_ns_id AND name = 'database';
    SELECT id INTO kaizen_mcp_deployment_scope_id FROM scopes WHERE namespace_id = kaizen_mcp_ns_id AND name = 'deployment';
    
    -- Add inheritance hierarchy
    -- kaizen-mcp:server inherits from python:fastmcp (technical inheritance)
    INSERT INTO scope_parents (child_scope_id, parent_scope_id) VALUES
    (kaizen_mcp_server_scope_id, python_fastmcp_scope_id)
    ON CONFLICT (child_scope_id, parent_scope_id) DO NOTHING;
    
    -- All kaizen-mcp specialized scopes inherit from kaizen-mcp:default
    INSERT INTO scope_parents (child_scope_id, parent_scope_id) VALUES
    (kaizen_mcp_server_scope_id, kaizen_mcp_default_scope_id),
    (kaizen_mcp_database_scope_id, kaizen_mcp_default_scope_id),
    (kaizen_mcp_deployment_scope_id, kaizen_mcp_default_scope_id)
    ON CONFLICT (child_scope_id, parent_scope_id) DO NOTHING;

    -- =========================================================================
    -- GLOBAL KNOWLEDGE ENTRIES
    -- =========================================================================
    
    -- Insert global:default knowledge (Universal best practices)
    INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
    
    -- Modern Tooling  
    (global_default_scope_id,
     'Use modern development tooling for improved performance and developer experience. Evaluate newer alternatives to legacy tools when they provide measurable benefits.',
     'development tooling performance modern tools alternatives',
     NULL),

    -- SOLID Principles and Clean Code Architecture
    (global_default_scope_id,
     'Apply SOLID principles for maintainable code: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. Use clean code practices with meaningful names, small functions, and clear abstractions.',
     'clean code architecture solid principles design maintainable',
     'M'),

    -- Version Control and Git Best Practices
    (global_default_scope_id,
     'Use descriptive commit messages with conventional format. Create feature branches for development, use pull requests for code review. Keep repository history clean with meaningful commits and proper branching strategy.',
     'git version control workflow branching commit messages repository',
     'S'),

    -- Code Review and Quality Assurance
    (global_default_scope_id,
     'Implement mandatory code reviews with focus on logic, security, performance, and maintainability. Use static analysis tools for automated quality checks. Establish coding standards and style guides for consistency.',
     'code review quality assurance static analysis standards automation',
     'M'),


    -- Security Best Practices and Vulnerability Prevention
    (global_default_scope_id,
     'Implement defense-in-depth security: input validation, authentication, authorization, encryption at rest and in transit. Regular security audits, dependency scanning, and principle of least privilege access.',
     'security best practices vulnerability prevention authentication data protection',
     'L'),

    -- Performance Optimization and Monitoring
    (global_default_scope_id,
     'Monitor application performance with metrics, logging, and tracing. Identify bottlenecks through profiling and load testing. Implement caching strategies, optimize database queries, and use CDNs for static content.',
     'performance optimization monitoring metrics bottlenecks caching analysis',
     'M'),


    -- Documentation and Knowledge Management
    (global_default_scope_id,
     'Maintain comprehensive technical documentation: API specs, architecture decisions, deployment guides, troubleshooting runbooks. Use documentation-as-code practices with version control and automated generation.',
     'documentation technical writing knowledge management api standards sharing',
     'S'),

    -- CI/CD Pipeline Design and Automation
    (global_default_scope_id,
     'Design CI/CD pipelines with automated testing, security scanning, and deployment stages. Use infrastructure-as-code for reproducible environments. Implement blue-green or canary deployments for zero-downtime releases.',
     'cicd pipeline automation deployment build continuous integration',
     'L'),

    -- Dependency Management and Package Security
    (global_default_scope_id,
     'Lock dependency versions for reproducible builds. Regularly update packages and scan for security vulnerabilities. Use private package registries for internal libraries. Audit dependencies for licensing compliance.',
     'dependency management package security scanning version locking updates',
     'M'),

    -- API Design and Integration Patterns
    (global_default_scope_id,
     'Design RESTful APIs with consistent naming, proper HTTP methods, and clear error responses. Use API versioning strategies and comprehensive documentation. Implement rate limiting, authentication, and input validation.',
     'api design rest integration patterns versioning documentation',
     'M'),

    -- Development Environment and Tooling Standards
    (global_default_scope_id,
     'Standardize development environments with Docker containerization. Use consistent IDE configurations, linting rules, and formatting standards. Automate environment setup with docker-compose and configuration management.',
     'development environment setup docker containerization configuration standards ide',
     'S'),

    -- =========================================================================
    -- PYTHON KNOWLEDGE ENTRIES
    -- =========================================================================
    
    -- Insert python:default knowledge (Core Python development best practices)
    
    -- Package Management
    (python_default_scope_id,
     'Use uv instead of pip for Python package installation. uv provides faster dependency resolution and virtual environment management.',
     'python uv pip dependencies installation virtual environment',
     'S'),

    -- Database Async Programming
    (python_default_scope_id,
     'Use asyncpg for PostgreSQL connections in async Python applications. Provides native async support and better performance than psycopg2 for concurrent workloads.',
     'asyncpg postgresql async database connections psycopg2',
     'M'),

    -- Connection Management
    (python_default_scope_id,
     'Structure async applications with proper connection pooling and async context managers. Use async with statements for resource lifecycle management.',
     'async connection pooling context managers database management',
     NULL),

    -- Type Hints
    (python_default_scope_id,
     'Use modern type hints with built-in generics like list[str] instead of typing.List[str]. Enable strict mypy configuration for better type safety.',
     'python type hints mypy configuration typing generics',
     NULL),

    -- Pydantic Validation
    (python_default_scope_id,
     'Use Pydantic for input validation in MCP tools and APIs. Create custom validators with regex patterns and constraints for complex validation logic.',
     'pydantic validation custom validators regex patterns constraints',
     'S'),

    -- Testing with TestContainers
    (python_default_scope_id,
     'Use testcontainers for integration testing with real databases. Create pytest fixtures with proper container lifecycle management and async test support.',
     'pytest testcontainers async testing database integration fixtures',
     'L'),

    -- FastMCP Server Development
    (python_default_scope_id,
     'Build MCP servers with FastMCP decorators and proper context handling. Implement error handling and support both stdio and HTTP transports.',
     'fastmcp mcp tools decorators context error handling server stdio http',
     'M'),

    -- Development Workflow
    (python_default_scope_id,
     'Use Makefile for development workflow automation. Run ruff for linting, mypy for type checking, and pytest for testing in CI pipeline.',
     'make development ruff mypy linting ci pipeline testing workflow',
     'S'),


    -- Regular Expression Validation
    (python_default_scope_id,
     'Use regex patterns for input validation of namespaces, scopes, and context keywords. Compile patterns once and reuse for performance.',
     'regex patterns validation namespace scope context keywords matching',
     'S'),


    -- Module Organization and Imports
    (python_default_scope_id,
     'Structure Python modules with clear separation of concerns. Use absolute imports from kaizen_mcp package. Organize validation, utilities, and database operations in separate modules.',
     'python modules imports kaizen mcp organization structure',
     'S'),

    -- Docstring and Documentation Conventions
    (python_default_scope_id,
     'Write comprehensive docstrings for all MCP tools and functions. Include parameter descriptions, return value details, and usage examples following Google docstring format.',
     'python docstrings documentation mcp tools parameters conventions',
     'S'),

    -- Variable Naming and Code Style
    (python_default_scope_id,
     'Use descriptive variable names with snake_case convention. Choose meaningful parameter names that clearly indicate their purpose and data type.',
     'python variable naming conventions snake case descriptive meaningful',
     NULL),

    -- Async Database Transaction Patterns
    (python_default_scope_id,
     'Manage async database connections using asyncpg connection pools. Handle database transactions properly with connection lifecycle management and error handling.',
     'async database connections asyncpg pools transactions management',
     'L'),

    -- FastMCP Client Testing
    (python_default_scope_id,
     'Test MCP tools using FastMCP client with pytest. Use async context manager for client lifecycle and call_tool for testing MCP tool functionality.',
     'pytest fastmcp client mcp tools testing async',
     'M'),

    -- TestContainers Database Testing
    (python_default_scope_id,
     'Set up test databases using testcontainers with PostgreSQL. Create session-scoped pytest fixtures for database containers and schema loading.',
     'testcontainers postgresql pytest fixtures session database schema',
     'L'),

    -- Test Organization and Helper Functions
    (python_default_scope_id,
     'Organize tests by functionality with clear helper functions for validation. Structure test files by domain and create reusable verification functions.',
     'test organization helpers validation functions domain structure',
     'S'),

    -- Exception Testing with ToolError
    (python_default_scope_id,
     'Test MCP tool validation using pytest.raises with ToolError. Assert specific exception messages and validate input validation failure scenarios.',
     'pytest toolerror exception testing validation messages failures',
     'M'),

    -- Search Result Validation
    (python_default_scope_id,
     'Validate search results content and structure in knowledge discovery tests. Test search prompts and assert proper result formatting and content matching.',
     'search results validation knowledge prompts testing structure',
     'M'),

    -- Test Data Setup and Cleanup
    (python_default_scope_id,
     'Set up test data with namespace and scope creation for MCP testing. Implement database cleanup and reset between tests for test isolation.',
     'test data setup database cleanup reset namespaces mcp',
     'M'),

    -- =========================================================================
    -- PYTHON:FASTMCP KNOWLEDGE ENTRIES  
    -- =========================================================================
    
    -- Insert python:fastmcp knowledge (FastMCP framework development)
    
    -- FastMCP Installation and Setup
    (python_fastmcp_scope_id,
     'Install FastMCP with uv add fastmcp or uv pip install fastmcp. Verify installation with fastmcp version command. FastMCP 2.0 is actively maintained version with comprehensive features beyond MCP core protocol.',
     'fastmcp installation uv pip setup version verification',
     'S'),

    -- Basic FastMCP Server Creation
    (python_fastmcp_scope_id,
     'Create FastMCP server by instantiating FastMCP class and using @mcp.tool decorator for tools. Use mcp.run() in __main__ block to enable stdio transport execution with python server.py.',
     'fastmcp server creation tool decorator main block stdio transport',
     'S'),

    -- FastMCP Tool Implementation
    (python_fastmcp_scope_id,
     'Implement MCP tools using @mcp.tool decorator with type hints for parameters and return values. Docstrings become tool descriptions. FastMCP handles protocol boilerplate automatically.',
     'fastmcp tool implementation decorator type hints docstrings protocol',
     'M'),

    -- FastMCP Client Operations
    (python_fastmcp_scope_id,
     'Create FastMCP clients with Client(server_object) or Client("server.py"). Use async context manager (async with client) for client lifecycle and await client.call_tool() for tool execution.',
     'fastmcp client async context manager call tool lifecycle',
     'M'),

    -- FastMCP CLI Usage
    (python_fastmcp_scope_id,
     'Run FastMCP servers with fastmcp run server.py:mcp command. CLI auto-detects server objects named mcp, app, or server. Supports multiple transports including stdio, http, sse.',
     'fastmcp cli run command transports stdio http sse detection',
     'S'),

    -- FastMCP Advanced Features
    (python_fastmcp_scope_id,
     'FastMCP 2.0 provides comprehensive platform beyond MCP protocol: client libraries, authentication systems, deployment tools, integrations with AI platforms, testing frameworks, production infrastructure.',
     'fastmcp platform authentication deployment integrations testing production infrastructure',
     'L'),

    -- FastMCP Resources and Prompts
    (python_fastmcp_scope_id,
     'FastMCP supports Resources (data exposure like GET endpoints), Tools (functionality like POST endpoints), and Prompts (reusable LLM interaction templates). Use decorators @mcp.resource, @mcp.prompt.',
     'fastmcp resources tools prompts decorators data functionality templates',
     'M'),

    -- FastMCP Installation from MCP SDK Migration
    (python_fastmcp_scope_id,
     'Upgrade from official MCP SDK by changing import from mcp.server.fastmcp import FastMCP to from fastmcp import FastMCP. FastMCP 2.0 evolved beyond 1.0 SDK capabilities.',
     'fastmcp migration mcp sdk import upgrade compatibility',
     'S'),

    -- FastMCP Server Transports
    (python_fastmcp_scope_id,
     'FastMCP supports multiple transport protocols: stdio (default for CLI), http, sse (server-sent events), streamable-http. Configure transport with mcp.run() parameters or CLI flags.',
     'fastmcp transports stdio http sse streamable protocols configuration',
     'M'),

    -- FastMCP Context and State Management
    (python_fastmcp_scope_id,
     'FastMCP provides Context object with session_id property for data sharing across tool calls. Context.state dict enables persistent state management during client sessions.',
     'fastmcp context session state management data sharing persistent',
     'M'),

    -- FastMCP Output Schemas
    (python_fastmcp_scope_id,
     'Define structured output schemas for FastMCP tools to ensure responses conform to expected formats. Enables type-safe tool integration and predictable response structures.',
     'fastmcp output schemas structured responses type safe integration',
     'M'),

    -- FastMCP Elicitation Support
    (python_fastmcp_scope_id,
     'FastMCP supports elicitation for dynamic server-client communication. Servers can request additional information from clients during tool execution for interactive behavior.',
     'fastmcp elicitation dynamic communication interactive behavior requests',
     'M'),

    -- FastMCP Middleware System
    (python_fastmcp_scope_id,
     'Implement FastMCP middleware to intercept and modify requests/responses at protocol level. Enables logging, authentication, validation, rate limiting for production-ready servers.',
     'fastmcp middleware protocol logging authentication validation production',
     'L'),

    -- FastMCP Testing Framework
    (python_fastmcp_scope_id,
     'Test FastMCP tools using Client with async context managers and call_tool method. FastMCP provides built-in testing tools and pytest integration for MCP server validation.',
     'fastmcp testing client async pytest integration validation tools',
     'M'),

    -- FastMCP Authentication
    (python_fastmcp_scope_id,
     'FastMCP 2.11+ provides comprehensive OAuth 2.1 authentication with WorkOS AuthKit integration. Supports API keys, remote authentication, Dynamic Client Registration for enterprise identity systems.',
     'fastmcp authentication oauth workos authkit api keys enterprise identity',
     'L'),

    -- FastMCP OpenAPI Integration
    (python_fastmcp_scope_id,
     'Generate FastMCP servers from OpenAPI specifications with experimental parser. Supports parameter encoding, schema conversion, performance optimizations for REST API integration.',
     'fastmcp openapi specifications parser parameters schema rest api integration',
     'L'),

    -- FastMCP Development Workflow
    (python_fastmcp_scope_id,
     'FastMCP development uses uv for package management, pre-commit hooks for code quality, pytest for testing. Support factory functions, version parameter, comprehensive CLI commands.',
     'fastmcp development uv pre-commit pytest factory functions cli',
     'M'),

    -- FastMCP Proxy and Composition
    (python_fastmcp_scope_id,
     'FastMCP supports server proxying and composition for complex architectures. Enable advanced MCP features forwarding (logging, progress, elicitation) through proxy servers.',
     'fastmcp proxy composition architecture forwarding logging progress elicitation',
     'L'),

    -- FastMCP Integration Platforms
    (python_fastmcp_scope_id,
     'FastMCP integrates with major AI platforms: Anthropic API, ChatGPT, Claude Code, Claude Desktop, Cursor, Gemini SDK, OpenAI API. Supports FastAPI, Starlette/ASGI frameworks.',
     'fastmcp integrations anthropic chatgpt claude cursor gemini openai fastapi starlette',
     'M'),

    -- FastMCP Performance and Optimization
    (python_fastmcp_scope_id,
     'FastMCP 2.11+ includes experimental OpenAPI parser with single-pass schema processing and optimized memory usage. Significant performance improvements for OpenAPI integrations.',
     'fastmcp performance optimization experimental parser schema memory usage',
     'M'),

    -- FastMCP Component Management
    (python_fastmcp_scope_id,
     'FastMCP components (tools, resources, prompts) support meta dictionaries, title fields, prefixing for organization. Enable automatic list change notifications for dynamic updates.',
     'fastmcp components meta dictionaries title prefixing notifications dynamic',
     'M'),

    -- FastMCP Type System
    (python_fastmcp_scope_id,
     'FastMCP implements server-side type conversion for prompt arguments with proper validation. Supports modern type hints, string annotations, structured content generation.',
     'fastmcp type conversion validation hints annotations structured content',
     'M'),

    -- FastMCP Cloud and Deployment
    (python_fastmcp_scope_id,
     'FastMCP Cloud provides remote MCP hosting. FastMCP supports production deployment patterns, Docker integration, environment configuration, scalable infrastructure.',
     'fastmcp cloud deployment docker environment configuration infrastructure',
     'L'),

    -- FastMCP Error Handling and Logging
    (python_fastmcp_scope_id,
     'FastMCP provides structured error handling with proper exception propagation, client-side logging configuration, debugging capabilities for development and production troubleshooting.',
     'fastmcp error handling exception logging debugging troubleshooting development',
     'M'),

    -- FastMCP Server Components and Architecture
    (python_fastmcp_scope_id,
     'FastMCP servers expose Tools (functions for actions), Resources (data sources), Resource Templates (parameterized resources), and Prompts (LLM message templates). Use decorators @mcp.tool, @mcp.resource, @mcp.prompt.',
     'fastmcp server components tools resources templates prompts decorators functions',
     'M'),

    -- FastMCP Tag-Based Filtering
    (python_fastmcp_scope_id,
     'FastMCP supports tag-based component filtering with include_tags and exclude_tags parameters. Components can be tagged for selective exposure to different environments or users.',
     'fastmcp tag filtering include exclude components selective exposure environments',
     'M'),

    -- FastMCP Custom Routes and HTTP Integration
    (python_fastmcp_scope_id,
     'Add custom web routes to FastMCP HTTP servers using @mcp.custom_route decorator. Useful for health checks, status endpoints, webhooks alongside MCP endpoint.',
     'fastmcp custom routes http decorator health checks status webhooks endpoints',
     'M'),

    -- FastMCP Server Composition and Mounting
    (python_fastmcp_scope_id,
     'Compose multiple FastMCP servers using import_server (static copy) and mount (live link). Organize large applications into modular components with prefix support.',
     'fastmcp server composition mounting import modular components prefix organization',
     'L'),

    -- FastMCP Tool Transformation System
    (python_fastmcp_scope_id,
     'Transform existing tools with Tool.from_tool() to modify schemas, argument mappings, and behavior. Use ArgTransform for parameter modification, hiding, defaults, and type changes.',
     'fastmcp tool transformation argtransform schema modification parameters hiding defaults',
     'L'),

    -- FastMCP Client Architecture and Transports
    (python_fastmcp_scope_id,
     'FastMCP Client handles MCP protocol operations with automatic transport inference: FastMCP instance (memory), .py files (stdio), URLs (http), config dictionaries (multi-server).',
     'fastmcp client transport inference memory stdio http multi-server configuration',
     'M'),

    -- FastMCP Client Configuration and Callbacks
    (python_fastmcp_scope_id,
     'Configure FastMCP clients with log_handler, progress_handler, sampling_handler for advanced server interactions. Support roots for local context and timeout configuration.',
     'fastmcp client configuration callbacks handlers roots timeout context interactions',
     'M'),

    -- FastMCP Multi-Server Client Support
    (python_fastmcp_scope_id,
     'Create multi-server clients from MCP configuration dictionaries. Support both HTTP/SSE remote servers and local stdio servers with command, args, env, cwd configuration.',
     'fastmcp multi-server client configuration http sse stdio command args environment',
     'L'),

    -- FastMCP Resource Templates and URI Patterns
    (python_fastmcp_scope_id,
     'FastMCP Resource Templates use URI patterns with parameters like "users://{user_id}/profile". Parameters are extracted from URI and passed to template functions.',
     'fastmcp resource templates uri patterns parameters extraction functions',
     'M'),

    -- FastMCP Custom Tool Serialization
    (python_fastmcp_scope_id,
     'Customize FastMCP tool output serialization with tool_serializer function. Default JSON serialization can be replaced with YAML, custom formats, or transformations.',
     'fastmcp tool serialization custom yaml json formats transformation output',
     'S'),

    -- FastMCP Global Settings and Environment Variables
    (python_fastmcp_scope_id,
     'Configure FastMCP globally via environment variables prefixed with FASTMCP_: LOG_LEVEL, MASK_ERROR_DETAILS, RESOURCE_PREFIX_FORMAT, INCLUDE_FASTMCP_META.',
     'fastmcp global settings environment variables log mask prefix meta configuration',
     'M'),

    -- FastMCP Server Lifespan and Context Management
    (python_fastmcp_scope_id,
     'FastMCP supports async lifespan context managers for server startup/shutdown logic. Use lifespan parameter in FastMCP constructor for resource management.',
     'fastmcp lifespan context manager startup shutdown resource management async',
     'M'),

    -- FastMCP Component Metadata and Annotations
    (python_fastmcp_scope_id,
     'FastMCP components support meta dictionaries, title fields, annotations, and tags. Enable/disable FastMCP metadata inclusion with include_fastmcp_meta parameter.',
     'fastmcp component metadata annotations title tags fastmcp meta inclusion',
     'S'),

    -- FastMCP Duplicate Handling Strategies
    (python_fastmcp_scope_id,
     'Configure FastMCP duplicate component handling with on_duplicate_tools, on_duplicate_resources, on_duplicate_prompts: "error", "warn", "replace" strategies.',
     'fastmcp duplicate handling strategies error warn replace tools resources prompts',
     'S'),

    -- FastMCP Version and Dependencies Management
    (python_fastmcp_scope_id,
     'FastMCP supports version parameter in constructor and dependencies list with package specifications. Use fastmcp version command for installation verification.',
     'fastmcp version dependencies package specifications constructor verification command',
     'S'),

    -- FastMCP CLI Commands and Options
    (python_fastmcp_scope_id,
     'FastMCP CLI provides run, inspect, install commands. Support --python, --project, --with-requirements options. Auto-detects server objects: mcp, app, server.',
     'fastmcp cli commands run inspect install python project requirements detection',
     'M'),

    -- FastMCP Protocol-Level Middleware
    (python_fastmcp_scope_id,
     'Implement FastMCP middleware at protocol level for request/response interception. Enable logging, authentication, validation, rate limiting, and custom processing.',
     'fastmcp middleware protocol interception validation rate limiting custom processing',
     'L'),

    -- FastMCP Context State and Session Management
    (python_fastmcp_scope_id,
     'FastMCP Context provides session_id property and state dict for persistent data sharing across tool calls. Enable stateful behavior during client sessions.',
     'fastmcp context session state persistent data sharing stateful behavior sessions',
     'M'),

    -- FastMCP List Change Notifications
    (python_fastmcp_scope_id,
     'FastMCP automatically sends list change notifications to clients when tools, resources, or prompts are dynamically updated. Enable responsive client adaptations.',
     'fastmcp list change notifications dynamic updates responsive adaptations clients',
     'M'),

    -- FastMCP Elicitation and Interactive Behavior
    (python_fastmcp_scope_id,
     'FastMCP elicitation enables servers to request additional information from clients during tool execution. Support implicit acceptance and no-response elicitation patterns.',
     'fastmcp elicitation interactive servers request information implicit acceptance patterns',
     'M'),

    -- FastMCP Bearer Authentication and JWT
    (python_fastmcp_scope_id,
     'FastMCP supports bearer token authentication with JWT validation. Configure issuer validation, audience checking, and scopes claim support for OAuth integration.',
     'fastmcp bearer authentication jwt validation issuer audience scopes oauth integration',
     'M'),

    -- FastMCP Development and Testing Patterns
    (python_fastmcp_scope_id,
     'FastMCP testing uses in-memory transport with FastMCP instances for reliable testing. Prefer Client(server_object) over external processes for development.',
     'fastmcp testing memory transport instances reliable development processes patterns',
     'M'),

    -- =========================================================================
    -- DETAILED FASTMCP IMPLEMENTATION KNOWLEDGE
    -- =========================================================================

    -- FastMCP Server Constructor Parameters
    (python_fastmcp_scope_id,
     'FastMCP constructor accepts name, instructions, auth (OAuthProvider/TokenVerifier), lifespan (AsyncContextManager), tools list, dependencies, include_tags, exclude_tags, on_duplicate_* strategies, include_fastmcp_meta.',
     'fastmcp constructor parameters auth lifespan tools dependencies tags duplicate strategies',
     'M'),

    -- FastMCP Tool Implementation Details
    (python_fastmcp_scope_id,
     'FastMCP tools transform Python functions with @mcp.tool decorator. Use type annotations for parameter validation, docstrings for descriptions. Supports async/sync functions, exclude_args, enabled parameter, annotations (ToolAnnotations).',
     'fastmcp tools decorator type annotations docstrings async sync exclude enabled annotations',
     'M'),

    -- FastMCP Tool Parameter Types and Validation
    (python_fastmcp_scope_id,
     'FastMCP supports comprehensive parameter types: basic types (int, float, str, bool), binary data (bytes), datetime objects, collections (list, dict, set), optional types (Union, None), constrained types (Literal, Enum), Path, UUID, Pydantic models.',
     'fastmcp parameter types validation basic binary datetime collections optional constrained path uuid pydantic',
     'M'),

    -- FastMCP Tool Annotations and Metadata
    (python_fastmcp_scope_id,
     'FastMCP tool annotations include readOnlyHint, destructiveHint, idempotentHint, openWorldHint. Use Annotated[type, "description"] for simple parameter descriptions or Field() for advanced validation constraints.',
     'fastmcp annotations readonly destructive idempotent openworld annotated field validation constraints',
     'M'),

    -- FastMCP Resource URI Patterns and Templates
    (python_fastmcp_scope_id,
     'FastMCP resources use URI patterns like "data://config" for static resources and "users://{user_id}/profile" for templates. Resource templates extract parameters from URI patterns and pass to functions.',
     'fastmcp resources uri patterns templates static dynamic parameters extraction',
     'M'),

    -- FastMCP Resource Return Types and Content
    (python_fastmcp_scope_id,
     'FastMCP resource return types: str (TextResourceContents), dict/list/BaseModel (JSON serialized), bytes (Base64 BlobResourceContents), None (empty content). Specify mime_type for proper content handling.',
     'fastmcp resource return types text json blob base64 mime content handling',
     'M'),

    -- FastMCP Resource Classes and Static Resources
    (python_fastmcp_scope_id,
     'FastMCP provides resource classes: TextResource, BinaryResource, FileResource, HttpResource, DirectoryResource. Use mcp.add_resource() for static content with custom keys and direct file/URL access.',
     'fastmcp resource classes text binary file http directory add static custom keys',
     'M'),

    -- FastMCP Client Transport Inference and Configuration
    (python_fastmcp_scope_id,
     'FastMCP client automatically infers transport: FastMCP instance (memory), .py files (stdio), .js files (nodejs stdio), URLs (http), MCPConfig dictionaries (multi-server). Use async context managers for lifecycle.',
     'fastmcp client transport inference memory stdio nodejs http mcp config multi-server async context',
     'M'),

    -- FastMCP Client Tool Execution and Results
    (python_fastmcp_scope_id,
     'FastMCP client.call_tool() returns CallToolResult with .data property for fully hydrated Python objects, .content for standard MCP blocks, .structured_content for raw JSON, .is_error for failure detection.',
     'fastmcp client call tool result data hydrated content structured error detection',
     'M'),

    -- FastMCP Client Advanced Features and Callbacks
    (python_fastmcp_scope_id,
     'FastMCP client supports log_handler, progress_handler, sampling_handler for advanced interactions. Configure timeout, roots for local context, and call_tool_mcp() for raw MCP protocol access.',
     'fastmcp client handlers log progress sampling timeout roots mcp protocol raw access',
     'M'),

    -- FastMCP CLI Commands and Entrypoints
    (python_fastmcp_scope_id,
     'FastMCP CLI provides run, dev, install, inspect, version commands. Entrypoints: inferred server (mcp/app/server), explicit object (file.py:name), factory function (file.py:create_server), remote proxy (URL), MCP config (mcp.json).',
     'fastmcp cli commands run dev install inspect version entrypoints inferred explicit factory proxy config',
     'M'),

    -- FastMCP CLI Run Command Options
    (python_fastmcp_scope_id,
     'fastmcp run supports --transport (stdio/http/sse), --host, --port, --path, --log-level, --no-banner, --python version, --with packages, --project directory, --with-requirements file.',
     'fastmcp cli run transport host port path log level banner python packages project requirements',
     'M'),

    -- FastMCP CLI Install and IDE Integration
    (python_fastmcp_scope_id,
     'fastmcp install supports claude-code, claude-desktop, cursor, mcp-json targets. Options: --server-name, --with-editable, --with packages, --env variables, --env-file, --python version. Requires uv for dependency management.',
     'fastmcp cli install claude desktop cursor mcp json server name editable packages env variables python uv',
     'M'),

    -- FastMCP Method Decoration Patterns
    (python_fastmcp_scope_id,
     'FastMCP decorators should not be applied directly to instance/class methods. Register methods after class creation: instance (mcp.tool(obj.method)), class (mcp.tool(Class.method)), static (mcp.tool(Class.static_method)).',
     'fastmcp method decoration patterns instance class static registration bound methods',
     'M'),

    -- FastMCP Tool Transformation and ArgTransform
    (python_fastmcp_scope_id,
     'Tool.from_tool() creates transformed tools with modified schemas. ArgTransform modifies parameters: name, description, default, default_factory, hide, required, type. Use transform_fn for custom behavior, output_schema for structured outputs.',
     'fastmcp tool transformation argtransform name description default hide required type transform schema',
     'L'),

    -- FastMCP Authentication Providers and Security
    (python_fastmcp_scope_id,
     'FastMCP authentication supports OAuthProvider, TokenVerifier, BearerAuthProvider with JWT validation. Configure issuer, audience, scopes claims. WorkOS AuthKit integration for enterprise SSO and Dynamic Client Registration.',
     'fastmcp authentication oauth token bearer jwt issuer audience scopes workos authkit enterprise sso',
     'L'),

    -- FastMCP Middleware Implementation and Protocol
    (python_fastmcp_scope_id,
     'FastMCP middleware intercepts requests/responses at protocol level. Implement middleware functions with request/response parameters. Built-in middleware: error_handling, logging, rate_limiting, timing.',
     'fastmcp middleware protocol intercept request response error handling logging rate limiting timing',
     'L'),

    -- FastMCP Context Object and Capabilities
    (python_fastmcp_scope_id,
     'FastMCP Context provides session_id, state dict, request_id, logging (ctx.info/error), progress reporting (ctx.report_progress), elicitation (ctx.elicit), sampling (ctx.sample).',
     'fastmcp context session state request logging progress elicitation sampling capabilities',
     'M'),

    -- FastMCP Server Composition and Mounting
    (python_fastmcp_scope_id,
     'FastMCP server composition: import_server() for static copy, mount() for live link with prefix. Organize modular applications, reuse existing servers, handle component name conflicts with prefixing.',
     'fastmcp server composition import mount static live prefix modular reuse conflicts',
     'L'),

    -- FastMCP Proxy Servers and Transport Bridging
    (python_fastmcp_scope_id,
     'FastMCP.as_proxy() creates proxy servers for any MCP server (local/remote). Bridge transports, add frontend to existing servers. Automatic concurrent operations handling with fresh sessions for disconnected clients.',
     'fastmcp proxy servers transport bridging frontend concurrent operations sessions disconnected',
     'L'),

    -- FastMCP OpenAPI Integration and Code Generation
    (python_fastmcp_scope_id,
     'FastMCP.from_openapi() generates servers from OpenAPI specs. FastMCP.from_fastapi() converts FastAPI apps. Experimental parser with single-pass processing, parameter encoding, schema conversion, performance optimization.',
     'fastmcp openapi integration code generation fastapi experimental parser parameter encoding schema performance',
     'L'),

    -- FastMCP Global Settings and Environment Configuration
    (python_fastmcp_scope_id,
     'FastMCP global settings via FASTMCP_ environment variables: LOG_LEVEL, MASK_ERROR_DETAILS, RESOURCE_PREFIX_FORMAT (path/protocol), INCLUDE_FASTMCP_META. Configure .env files for development.',
     'fastmcp global settings environment variables log mask prefix meta env files development',
     'M'),

    -- FastMCP Custom Tool Serialization and Output Formats
    (python_fastmcp_scope_id,
     'FastMCP custom tool_serializer function replaces default JSON serialization. Use for YAML output, custom formats, data transformation. Applied to non-string return values, falls back to JSON on exceptions.',
     'fastmcp custom tool serializer yaml json formats transformation non-string fallback exceptions',
     'S'),

    -- FastMCP Component Lifecycle and Notifications
    (python_fastmcp_scope_id,
     'FastMCP automatically sends list_changed notifications when components are added/enabled/disabled. Supports component disable/enable methods, tag-based filtering with include/exclude logic, precedence rules.',
     'fastmcp component lifecycle notifications list changed enable disable tags filtering precedence',
     'M'),

    -- FastMCP Multi-Server Configuration and MCPConfig
    (python_fastmcp_scope_id,
     'FastMCP MCPConfig supports multiple servers: HTTP/SSE with url/headers/auth, stdio with command/args/env/cwd. Tool/resource names prefixed with server names for disambiguation.',
     'fastmcp multi-server mcp config http sse stdio command args env cwd prefixed names disambiguation',
     'L'),

    -- FastMCP Development Workflow and Debugging
    (python_fastmcp_scope_id,
     'FastMCP development workflow: uv for packages, pre-commit hooks, pytest testing, fastmcp dev with MCP Inspector, fastmcp inspect for server analysis. Use factory functions for setup code with CLI.',
     'fastmcp development workflow uv pre-commit pytest dev inspector inspect factory setup cli',
     'M'),

    -- FastMCP Error Handling and Exception Management
    (python_fastmcp_scope_id,
     'FastMCP error handling: ToolError exceptions, raise_on_error parameter, manual error checking with result.is_error, call_tool_mcp() for raw protocol access. Configure MASK_ERROR_DETAILS for production.',
     'fastmcp error handling tool error raise manual checking raw protocol mask details production',
     'M'),

    -- FastMCP Type Annotations and Schema Generation
    (python_fastmcp_scope_id,
     'FastMCP generates JSON schemas from type annotations for MCP protocol. Supports modern type hints (list[str] vs typing.List), Pydantic models, constraints with Field(), regex patterns, validation.',
     'fastmcp type annotations json schema generation modern hints pydantic constraints field regex validation',
     'M'),

    -- FastMCP Resource Templates and Dynamic Content
    (python_fastmcp_scope_id,
     'FastMCP resource templates use {parameter} placeholders in URIs. Parameters extracted and passed to functions. Support async resource functions, Context access, mime_type specification, lazy evaluation.',
     'fastmcp resource templates placeholders parameters async context mime type lazy evaluation',
     'M'),

    -- FastMCP Binary Data and File Handling
    (python_fastmcp_scope_id,
     'FastMCP binary data handling: bytes return type becomes Base64 BlobResourceContents, FileResource for local files, HttpResource for remote content, DirectoryResource for file listings.',
     'fastmcp binary data bytes base64 blob file resource http directory local remote listings',
     'M'),

    -- FastMCP Lifespan Management and Async Context
    (python_fastmcp_scope_id,
     'FastMCP lifespan parameter accepts AsyncContextManager for server startup/shutdown logic. Use for resource initialization, cleanup, database connections, external service setup.',
     'fastmcp lifespan async context manager startup shutdown resource initialization cleanup database connections',
     'M'),

    -- FastMCP Component Tags and Organization
    (python_fastmcp_scope_id,
     'FastMCP component tags for organization: include_tags (only matching), exclude_tags (filter out), precedence (exclude wins). Tags appear in meta._fastmcp.tags namespace for client filtering.',
     'fastmcp component tags organization include exclude precedence meta namespace client filtering',
     'M'),

    -- FastMCP Transport Configuration and Network Settings
    (python_fastmcp_scope_id,
     'FastMCP transport configuration: stdio (default), http with host/port/path, sse (deprecated), streamable-http. Configure CORS, custom routes with @custom_route decorator, health checks.',
     'fastmcp transport configuration stdio http host port path sse streamable cors custom routes health',
     'M'),

    -- FastMCP Inspector Integration and Development Testing
    (python_fastmcp_scope_id,
     'FastMCP Inspector integration via fastmcp dev command. Supports STDIO testing, requires explicit dependencies with --with/--with-editable. Use --inspector-version, --ui-port, --server-port for configuration.',
     'fastmcp inspector integration dev command stdio dependencies with editable version ui server port',
     'M'),

    -- FastMCP Dependencies Management and Package Specifications
    (python_fastmcp_scope_id,
     'FastMCP dependencies parameter accepts package specifications like "requests", "pandas>=2.0.0". CLI supports --with packages, --with-editable directories, --with-requirements files, --python version.',
     'fastmcp dependencies management package specifications requests pandas with editable requirements python version',
     'M'),

    -- FastMCP Output Schemas and Structured Responses
    (python_fastmcp_scope_id,
     'FastMCP output schemas enable structured tool responses. Define return type annotations, Pydantic models for complex data. Client .data property provides hydrated Python objects with datetime, UUID reconstruction.',
     'fastmcp output schemas structured responses annotations pydantic models data hydrated datetime uuid reconstruction',
     'M'),

    -- FastMCP Elicitation and Interactive User Input
    (python_fastmcp_scope_id,
     'FastMCP elicitation enables server-initiated user input requests during tool execution. Use ctx.elicit() with structured schemas, support implicit acceptance, no-response patterns for interactive workflows.',
     'fastmcp elicitation user input server initiated tool execution structured schemas implicit acceptance interactive',
     'M'),

    -- FastMCP Sampling and LLM Integration
    (python_fastmcp_scope_id,
     'FastMCP sampling requests client LLM text generation via ctx.sample(). Provide messages, parameters, include_context for request scope. Integrate with client sampling_handler for custom LLM services.',
     'fastmcp sampling llm integration sample messages parameters include context handler custom services',
     'M'),

    -- =========================================================================
    -- KAIZEN-MCP DEFAULT SCOPE KNOWLEDGE ENTRIES
    -- =========================================================================

    -- Insert kaizen-mcp:default knowledge (Core KaizenMCP system understanding)

    -- Core Product Vision & Philosophy
    (kaizen_mcp_default_scope_id,
     'KaizenMCP transforms AI assistants from stateless tools into persistent learning team members. Based on Japanese Kaizen philosophy of continuous improvement, AI accumulates project knowledge over time, remembering context, decisions, and lessons across sessions instead of starting fresh each time.',
     'kaizen continuous improvement ai memory persistent assistant team knowledge',
     NULL),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP solves critical AI limitations: context loss requiring re-explanation every session (15-30 min/day), repeated mistakes from inability to learn from failures, knowledge silos when team members leave, and inefficient onboarding. Solution provides persistent memory enabling AI to remember, learn, connect, evolve, and share knowledge.',
     'context loss repeated mistakes knowledge silos ai productivity error repetition',
     NULL),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP designed for individual developers and small trusted teams (2-10 people) in high-trust environments like startups. Uses simple trust-based access model - all database users have full read/write permissions with shared knowledge. NOT suitable for large enterprises requiring complex security controls.',
     'target users small teams trusted environment individual developers startup permissions',
     NULL),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP succeeds when developers forget AI wasn''t always on the team - it knows project context like a tenured member. Success indicators: new hires learn from AI instead of bothering seniors, mistakes become extinct after first occurrence, context switching feels seamless, knowledge compounds daily making AI more valuable.',
     'success criteria vision ai team member knowledge compounds seamless context productivity',
     NULL),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP uses three controlled knowledge acquisition mechanisms ensuring quality for small trusted teams: 1) User Teaching Sessions (explicit knowledge transfer), 2) Post-Success Voluntary Additions (optional capture after tasks), 3) Post-Failure Proposals (learning from errors with user approval). This controlled approach maintains system simplicity while ensuring knowledge quality.',
     'knowledge acquisition controlled mechanisms teaching post failure user approval voluntary quality',
     'M'),

    -- Architecture & Knowledge Management
    (kaizen_mcp_default_scope_id,
     'KaizenMCP organizes knowledge through namespace and scope hierarchy. Namespaces define organizational boundaries (e.g. ''acme'', ''payments''), scopes define teams/projects within namespaces (e.g. ''acme:frontend-team''). Knowledge inherits from specific scopes to broader scopes to global, ensuring AI has right context without information overload.',
     'namespace scope hierarchy organization boundaries inheritance global project specific',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP search system uses multi-query decomposition with full-text search capabilities and task-aware filtering (XS-XL complexity). Features context weighting (1.0) vs content weighting (0.4), relevance threshold of 0.4, and intelligent query decomposition for complex implementation tasks across multiple domains.',
     'search retrieval multi query decomposition full text task aware filtering relevance scoring',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP AI searches for relevant context when starting tasks using structured 5-step framework: 1) Group knowledge by functional area, 2) Order by criticality, 3) Determine implementation sequence, 4) Check contradictions, 5) Map to implementation steps. No-results scenarios provide guided options for proceeding.',
     'context retrieval patterns ai searches relevant implementation knowledge processing framework',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP handles contradictory knowledge through user-guided conflict resolution. When conflicting information exists, system presents conflicts to users for resolution. Users mark one entry as authoritative while others become superseded, maintaining knowledge integrity and preventing confusion.',
     'conflict resolution contradictory knowledge user guided authoritative superseded integrity',
     'M'),

    -- Database Schema & Data Model
    (kaizen_mcp_default_scope_id,
     'KaizenMCP uses PostgreSQL with dedicated kaizen_mcp schema containing all database functions. Database structure managed through Yoyo migrations with SQL organization under sql/ directory. Schema includes namespaces, scopes, knowledge tables with inheritance relationships and search optimization functions.',
     'postgresql schema kaizen mcp functions migrations yoyo database design',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP knowledge storage model includes: content field (actionable implementation details), context field (5-7 standardized technical keywords), task_size classification (XS-XL complexity). Context keywords use standardized vocabulary for optimal searchability, following patterns like ''technology + concept + action''.',
     'knowledge storage content context keywords task size classification standardized vocabulary',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP search optimization uses context_weight=1.0, content_weight=0.4, relevance_threshold=0.4. Each context keyword match = 1.0 relevance points, content matches = 0.4 points. Minimum 0.4 total needed to return results. Formula: 1 keyword match = 1.0 relevance guarantees results.',
     'search optimization context weight content weight relevance threshold keyword matching scoring',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP configuration system uses hierarchy: CLI args > environment variables > defaults. Runtime configuration includes search weights, relevance thresholds, max results, and database connection parameters. Configuration managed through config.py with validation and type checking.',
     'configuration system hierarchy cli args environment variables defaults runtime config validation',
     'M'),

    -- MCP Server Implementation
    (kaizen_mcp_default_scope_id,
     'KaizenMCP implements FastMCP server named "project-kaizen" with comprehensive MCP tools organized by function: namespace management, scope management, knowledge operations, configuration tools, and search/discovery tools. Server follows MCP protocol standards with structured error handling.',
     'fastmcp server project kaizen mcp tools namespace scope knowledge configuration search',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP MCP tools organized into atomic operations: list_namespaces, create_namespace, rename_namespace, delete_namespace for namespace management. Scope tools: create_scope, add_scope_parents, remove_scope_parents. Knowledge tools: write_knowledge, search_knowledge_base, resolve_knowledge_conflict.',
     'mcp tools atomic operations namespace scope knowledge management list create rename delete',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP validation patterns enforce data quality: context keywords use lowercase letters, digits, hyphens only (a-z, 0-9, -). Namespace and scope names follow same pattern. Content must be non-empty. Validators in validators.py provide comprehensive input validation with clear error messages.',
     'validation patterns context keywords lowercase letters digits hyphens namespace scope content',
     'S'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP search prompts provide structured AI guidance. With results: 5-step framework for processing knowledge items. Without results: guided options - proceed with default knowledge, add new entries, or retry with different terms. Prompts optimize AI task execution and knowledge utilization.',
     'search prompts structured guidance framework processing knowledge options retry guidance',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP error handling provides structured user feedback through MCP context. Tools use try-except blocks with ctx.error() for user communication. Database errors, validation failures, and constraint violations handled gracefully with informative messages and suggested resolutions.',
     'error handling structured feedback mcp context database validation constraint violations messages',
     'M'),

    -- Development Workflow & Tooling
    (kaizen_mcp_default_scope_id,
     'KaizenMCP development uses uv for package management and virtual environments. Project structure: server/ contains FastMCP implementation, database/ contains schema and migrations, docs/ contains specifications. Both server and database have independent pyproject.toml configurations.',
     'development uv package management virtual environments project structure server database docs',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP static analysis uses mypy for type checking (src/ and tests/), ruff for linting and formatting with auto-fix capability. Commands: python -m mypy src/, python -m ruff check src/ --fix. Pre-commit hooks ensure code quality before commits.',
     'static analysis mypy type checking ruff linting formatting auto fix pre-commit hooks',
     'S'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP testing uses pytest with comprehensive test coverage. Test organization: test_namespace_tools.py, test_scope_tools.py, test_knowledge_management_tools.py, test_config_tools.py. Tests use testcontainers for database integration testing with proper cleanup.',
     'testing pytest test coverage namespace scope knowledge config tools testcontainers database integration',
     'M'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP database operations managed through Makefile and Python scripts: migrate.py (run migrations), status.py (check status), reset.py (reset database), load_samples.py (load sample data). Scripts located in database/scripts/ directory.',
     'database operations makefile python scripts migrate status reset load samples directory',
     'S'),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP Docker configuration provides containerized development and production deployment. docker-compose.yml includes PostgreSQL service with optimized settings. Dockerfile in server/ directory for FastMCP server containerization with proper dependencies.',
     'docker configuration containerized development production deployment compose postgresql dockerfile',
     'M'),

    -- Business Value & Metrics
    (kaizen_mcp_default_scope_id,
     'KaizenMCP efficiency improvements: context explanation time reduced from 15 minutes to 0, task success rate increases from 40% to 95% over 2 months, error recurrence drops to 0%, new developer onboarding from 1 week to 1 day through AI knowledge transfer.',
     'efficiency improvements context explanation task success rate error recurrence onboarding time',
     NULL),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP quality metrics: 100% adherence to stored patterns and conventions, complete knowledge retention between sessions, accurate cross-domain context application. AI maintains consistency unlike human memory lapses, ensuring institutional knowledge preservation.',
     'quality metrics pattern adherence knowledge retention cross domain context consistency preservation',
     NULL),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP business impact: 2-3 hours saved per developer per day through eliminated context re-explanation, reduced debugging time by preventing known errors, team scalability through AI-assisted onboarding, knowledge preservation preventing brain drain from team changes.',
     'business impact developer productivity debugging prevention team scalability knowledge preservation brain drain',
     NULL),

    (kaizen_mcp_default_scope_id,
     'KaizenMCP ROI calculation: 15-30 minutes daily context explanation elimination × team size × hourly rate. Error prevention savings: hours to days of debugging time saved per prevented mistake. Onboarding acceleration: senior developer time freed from training new hires.',
     'roi calculation context elimination error prevention debugging savings onboarding acceleration senior developer time',
     NULL),

    -- =========================================================================
    -- KAIZEN-MCP:SERVER SCOPE KNOWLEDGE ENTRIES
    -- =========================================================================
    
    -- Insert kaizen-mcp:server knowledge (MCP server implementation specifics)

    -- FastMCP Server Setup and Tool Registration
    (kaizen_mcp_server_scope_id,
     'KaizenMCP server uses FastMCP("project-kaizen") with @mcp.tool decorators for all MCP tools. Tools organized into namespace operations, scope operations, knowledge operations, and configuration tools with structured error handling using ctx.error().',
     'fastmcp server setup mcp tool registration organization',
     'M'),

    -- MCP Tool Parameter Validation
    (kaizen_mcp_server_scope_id,
     'KaizenMCP validates all MCP tool parameters using validators.py functions: validate_namespace_name(), validate_canonical_scope_name(), validate_context(), validate_content(). Pydantic Field() provides parameter descriptions with character limits and format requirements.',
     'mcp validation parameters pydantic error handling rules',
     'S'),

    -- Knowledge Search Prompt System
    (kaizen_mcp_server_scope_id,
     'KaizenMCP provides structured AI guidance through search prompts: KNOWLEDGE_SEARCH_PROMPT_WITH_RESULTS uses 5-step framework for processing knowledge, KNOWLEDGE_SEARCH_PROMPT_NO_RESULTS offers guided options when no results found.',
     'search prompts guidance knowledge processing framework structured',
     'M'),

    -- AsyncPG Connection Pool Management
    (kaizen_mcp_server_scope_id,
     'KaizenMCP uses asyncpg.create_pool() with min_size/max_size configuration and 60-second command timeout. Global _pool variable with get_pool() accessor ensures single connection pool per server instance.',
     'asyncpg connection pool database configuration timeout management',
     'M'),

    -- MCP Context Logging and Error Handling
    (kaizen_mcp_server_scope_id,
     'KaizenMCP tools use FastMCP Context for structured logging: await ctx.info() for operations, await ctx.debug() for diagnostics, await ctx.error() for user feedback. All database errors caught and re-raised with user-friendly messages.',
     'mcp context logging error handling fastmcp debugging feedback',
     'S'),

    -- Regular Expression Validation Patterns
    (kaizen_mcp_server_scope_id,
     'KaizenMCP validation uses compiled regex patterns: NAMESPACE_PATTERN for a-z0-9-, CONTEXT_PATTERN for space-separated keywords, QUERY_PATTERN for search terms. MIN/MAX length constants centralize validation rules for easy modification.',
     'regex validation patterns namespace context input compiled',
     'S'),

    -- Database Transaction Management
    (kaizen_mcp_server_scope_id,
     'KaizenMCP database operations use async with conn.transaction() for ACID compliance. Pool.acquire() provides connection context management with automatic cleanup. Complex operations wrapped in try-except for error handling.',
     'asyncpg database transactions acid rollback connection management',
     'M'),

    -- MCP Tool Organization and Naming
    (kaizen_mcp_server_scope_id,
     'KaizenMCP organizes MCP tools by domain: namespace tools (list_namespaces, create_namespace), scope tools (create_scope, add_scope_parents), knowledge tools (write_knowledge, search_knowledge_base). Consistent naming with domain prefixes.',
     'mcp tool organization naming conventions domain structure',
     'S'),

    -- FastMCP Prompt Endpoints for Search Optimization
    (kaizen_mcp_server_scope_id,
     'KaizenMCP provides FastMCP prompt endpoints for search optimization: create_knowledge_entry_guidance() generates instructions for optimal knowledge entries with 6-step framework (task context analysis, AI query simulation, content structure, context keywords optimization, task size classification, relevance score optimization). construct_search_queries_guidance() provides multi-query decomposition strategies with 2-3 word phrases targeting different implementation aspects.',
     'prompt knowledge entry search optimization guidance query context keywords framework',
     'M'),

    -- =========================================================================
    -- KAIZEN-MCP:DATABASE SCOPE KNOWLEDGE ENTRIES
    -- =========================================================================
    
    -- Insert kaizen-mcp:database knowledge (Database schema and implementation specifics)

    -- PostgreSQL Schema Design
    (kaizen_mcp_database_scope_id,
     'KaizenMCP uses dedicated kaizen_mcp PostgreSQL schema with all functions prefixed. Schema includes namespaces, scopes, scope_parents, scope_hierarchy, knowledge tables with proper foreign keys and CASCADE constraints.',
     'postgresql schema design functions foreign keys constraints',
     'M'),

    -- Full-Text Search Implementation
    (kaizen_mcp_database_scope_id,
     'KaizenMCP generates tsvector with setweight(to_tsvector(''english'', context), ''A'') for context keywords and setweight(content, ''B'') for content. GIN index on search_vector enables fast full-text search with ts_rank scoring.',
     'postgresql fulltext search tsvector gin indexes ranking',
     'L'),

    -- Scope Hierarchy Materialization
    (kaizen_mcp_database_scope_id,
     'KaizenMCP scope_hierarchy table stores pre-calculated ancestor arrays for O(1) inheritance lookups. calculate_scope_ancestors() function uses recursive CTE to build complete ancestor chains including global:default.',
     'scope hierarchy inheritance materialized ancestors recursive cte',
     'L'),

    -- Multi-Query Search Function
    (kaizen_mcp_database_scope_id,
     'search_knowledge_base() function accepts query_terms[] array, target_scope, and optional task_size filter. Uses websearch_to_tsquery() for natural language parsing and ts_rank() with configurable weights for relevance scoring.',
     'search function knowledge multi query task filtering relevance',
     'L'),

    -- Materialized View for Search Optimization
    (kaizen_mcp_database_scope_id,
     'mv_active_knowledge_search materialized view pre-joins knowledge, scopes, namespaces while filtering suppressed knowledge from conflicts table. Refreshed automatically via triggers on base table changes.',
     'materialized view postgresql conflict resolution search triggers',
     'M'),

    -- Configuration Management System
    (kaizen_mcp_database_scope_id,
     'KaizenMCP config table stores typed configuration with config_type_enum validation. Helper functions get_config_text(), get_config_float(), get_config_integer() provide type-safe access with default fallbacks.',
     'configuration management type safety functions validation defaults',
     'M'),

    -- Trigger-Based Maintenance
    (kaizen_mcp_database_scope_id,
     'KaizenMCP uses PostgreSQL triggers for hierarchy maintenance: refresh_scope_hierarchy() updates ancestor cache, prevent_circular_inheritance() blocks cycles, enforce_default_parent() ensures namespace:default inheritance.',
     'triggers hierarchy maintenance constraint enforcement circular cache',
     'L'),

    -- Yoyo Migration System
    (kaizen_mcp_database_scope_id,
     'KaizenMCP uses Yoyo migration system with SQL files in database/sql/migrations/. Migration dependencies tracked, Python scripts in database/scripts/ provide migrate, status, reset operations with sample data loading.',
     'yoyo migration database sql organization management status',
     'M'),

    -- =========================================================================
    -- KAIZEN-MCP:DEPLOYMENT SCOPE KNOWLEDGE ENTRIES
    -- =========================================================================
    
    -- Insert kaizen-mcp:deployment knowledge (Production deployment and operations)

    -- Docker Compose Configuration
    (kaizen_mcp_deployment_scope_id,
     'KaizenMCP uses docker-compose.yml with PostgreSQL 17 service (port 5452) and FastMCP server service (port 5453). Health checks ensure database readiness before server startup with proper service dependencies.',
     'docker compose services dependencies postgresql health networking',
     'M'),

    -- UV-Based Container Build
    (kaizen_mcp_deployment_scope_id,
     'KaizenMCP Dockerfile uses ghcr.io/astral-sh/uv:python3.12-bookworm-slim base with uv sync --frozen for reproducible builds. Two-stage copy: dependencies first, then source code for optimal layer caching.',
     'docker build uv container layer caching reproducible',
     'M'),

    -- Environment Configuration Hierarchy
    (kaizen_mcp_deployment_scope_id,
     'KaizenMCP configuration follows CLI args > environment variables > defaults hierarchy. Key variables: DATABASE_URL, MCP_TRANSPORT, MCP_HTTP_HOST, DATABASE_POOL_MIN/MAX for production tuning.',
     'environment variables configuration database transport hierarchy',
     'S'),

    -- Database Pool Optimization
    (kaizen_mcp_deployment_scope_id,
     'KaizenMCP production deployment uses optimized connection pool settings: DATABASE_POOL_MIN=1, DATABASE_POOL_MAX=2 for small teams. Command timeout 60 seconds prevents long-running query locks.',
     'database pool optimization connection production timeout scaling',
     'S'),

    -- Health Monitoring and Restart Policies
    (kaizen_mcp_deployment_scope_id,
     'KaizenMCP services use restart: unless-stopped policy with PostgreSQL health checks via pg_isready. Health check intervals: 10s with 5s timeout and 5 retries before failure detection.',
     'container health monitoring docker restart policies postgresql checks',
     'M'),

    -- Volume and Data Persistence
    (kaizen_mcp_deployment_scope_id,
     'KaizenMCP uses named Docker volume kz_data for PostgreSQL persistence with PGDATA=/var/lib/postgresql/data/pgdata. Local driver ensures data survives container recreation.',
     'docker volume persistence postgresql data management backup',
     'S'),

    -- Network Security and Port Mapping
    (kaizen_mcp_deployment_scope_id,
     'KaizenMCP exposes PostgreSQL on localhost:5452 and FastMCP server on localhost:5453. Container-to-container communication uses internal network without exposing internal ports.',
     'docker network security port mapping container isolation configuration',
     'S'),

    -- Production Security Management
    (kaizen_mcp_deployment_scope_id,
     'KaizenMCP production deployment requires secure DATABASE_URL with strong passwords and proper network isolation. Environment variables should be managed through container orchestration secrets, not embedded in images.',
     'environment security credentials container secrets production passwords',
     'M'),

    -- =========================================================================
    -- GIT WORKFLOW AND COMMIT KNOWLEDGE ENTRIES
    -- =========================================================================
    
    -- Git Commit Message Format
    (global_default_scope_id,
     'Use semantic versioning format: <type>: <description>. Types: feat, fix, docs, style, refactor, test, chore. Present tense, max 5 lines, no empty lines, bullet points allowed.',
     'git commit message format semver semantic versioning types',
     'XS'),

    -- Pre-Commit Validation
    (global_default_scope_id,
     'Before git commit, verify all staged files end with trailing newline. Use git status/diff to identify changed files, then validate file termination standards.',
     'git commit validation newline file endings pre-commit',
     'S'),

    -- Commit Rules and Standards
    (global_default_scope_id,
     'Git commit rules: present tense verbs, no Claude signatures, concise descriptions, bullet points for multiple changes, maximum 5 lines total per message.',
     'git commit rules standards present tense signatures bullet points',
     'XS'),

    -- File Formatting Requirements
    (global_default_scope_id,
     'All files must end with newline character. Ensure proper file termination when creating or editing files before committing to repository.',
     'file formatting newline termination git commit requirements',
     'XS');

END $$;
