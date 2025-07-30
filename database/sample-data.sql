-- Sample data for Project Kaizen MCP Knowledge System
-- Domain: E-commerce Platform Development

-- Create shopcraft namespace with default scope
INSERT INTO namespaces (name, description) 
VALUES ('shopcraft', 'ShopCraft e-commerce platform development');

-- Get namespace and scope IDs for references
DO $$
DECLARE
    global_ns_id BIGINT;
    shopcraft_ns_id BIGINT;
    global_default_scope_id BIGINT;
    shopcraft_default_scope_id BIGINT;
    frontend_scope_id BIGINT;
    backend_scope_id BIGINT;
    devops_scope_id BIGINT;
BEGIN
    -- Get namespace IDs
    SELECT id INTO global_ns_id FROM namespaces WHERE name = 'global';
    SELECT id INTO shopcraft_ns_id FROM namespaces WHERE name = 'shopcraft';
    
    -- Get default scope IDs
    SELECT id INTO global_default_scope_id FROM scopes WHERE namespace_id = global_ns_id AND name = 'default';
    SELECT id INTO shopcraft_default_scope_id FROM scopes WHERE namespace_id = shopcraft_ns_id AND name = 'default';
    
    -- Create additional scopes for shopcraft
    INSERT INTO scopes (namespace_id, name, description) VALUES
    (shopcraft_ns_id, 'frontend-team', 'Frontend development team knowledge'),
    (shopcraft_ns_id, 'backend-api', 'Backend API development knowledge'),
    (shopcraft_ns_id, 'devops-deploy', 'DevOps and deployment knowledge');
    
    -- Get the new scope IDs
    SELECT id INTO frontend_scope_id FROM scopes WHERE namespace_id = shopcraft_ns_id AND name = 'frontend-team';
    SELECT id INTO backend_scope_id FROM scopes WHERE namespace_id = shopcraft_ns_id AND name = 'backend-api';
    SELECT id INTO devops_scope_id FROM scopes WHERE namespace_id = shopcraft_ns_id AND name = 'devops-deploy';
    
    -- Add scope inheritance (all inherit from shopcraft:default, which inherits from global:default via triggers)
    INSERT INTO scope_parents (child_scope_id, parent_scope_id) VALUES
    (frontend_scope_id, backend_scope_id),  -- Frontend team learns from backend patterns
    (devops_scope_id, backend_scope_id);   -- DevOps needs backend deployment knowledge
    
    -- Insert global:default knowledge (Universal best practices and standards)
    INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
    
    -- Security Standards
    (global_default_scope_id, 
     'Always use HTTPS for external API communications to prevent man-in-the-middle attacks. Configure SSL certificates properly and use TLS 1.2 or higher.',
     'https ssl tls security api external communication certificates encryption',
     'XS'),
    
    (global_default_scope_id,
     'Never log sensitive data like passwords, API keys, or personal information. Use structured logging with appropriate log levels. Sanitize all log outputs.',
     'logging sensitive data passwords api keys personal information structured sanitize',
     'XS'),
    
    (global_default_scope_id,
     'Implement input validation on both client and server sides. Use parameterized queries to prevent SQL injection. Validate file uploads for type and size.',
     'input validation client server parameterized queries sql injection file uploads',
     'S'),
    
    (global_default_scope_id,
     'Environment variables should never be committed to version control. Use .env files locally and proper secret management in production. Always add .env to .gitignore.',
     'environment variables secrets gitignore env file security configuration',
     'S'),
    
    (global_default_scope_id,
     'API rate limiting should be implemented to prevent abuse: 100 requests per minute for authenticated users, 20 requests per minute for anonymous users. Use Redis for distributed rate limiting.',
     'api rate limiting redis abuse protection throttling requests per minute authentication',
     'M'),
    
    -- Git Workflow and Communication Standards
    (global_default_scope_id,
     'Git commit messages should follow semantic versioning: feat(scope): description for new features, fix(scope): description for bug fixes, docs: for documentation changes. Keep first line under 50 characters.',
     'git commit message semantic versioning feat fix docs scope changelog',
     'XS'),
    
    (global_default_scope_id,
     'All pull requests must include: clear description, testing instructions, screenshots for UI changes, and link to related issues. Request review from at least one team member.',
     'pull request description testing instructions screenshots ui changes review team member',
     'XS'),
    
    (global_default_scope_id,
     'Code comments should explain WHY, not WHAT. Focus on business logic, edge cases, and complex algorithms. Avoid obvious comments that repeat the code.',
     'code comments why not what business logic edge cases algorithms obvious',
     'XS'),
    
    (global_default_scope_id,
     'Documentation should be written for the intended audience. Technical docs for developers, user guides for end users. Keep documentation up-to-date with code changes.',
     'documentation audience technical developers user guides up-to-date code changes',
     'S'),
    
    (global_default_scope_id,
     'Use semantic versioning (MAJOR.MINOR.PATCH) for releases. Increment MAJOR for breaking changes, MINOR for new features, PATCH for bug fixes. Tag releases in git.',
     'semantic versioning major minor patch releases breaking changes features bug fixes git tags',
     'S'),
    
    -- Design Patterns and Architecture
    (global_default_scope_id,
     'Follow SOLID principles: Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. Design classes with single, well-defined purposes.',
     'solid principles single responsibility open closed liskov substitution interface segregation dependency inversion',
     'M'),
    
    (global_default_scope_id,
     'Use dependency injection for loose coupling. Inject dependencies through constructors or setters rather than creating them internally. Makes testing easier.',
     'dependency injection loose coupling constructors setters testing dependencies',
     'M'),
    
    (global_default_scope_id,
     'Implement proper error handling with specific exception types. Fail fast and provide meaningful error messages. Log errors with sufficient context for debugging.',
     'error handling exception types fail fast meaningful messages logging context debugging',
     'S'),
    
    (global_default_scope_id,
     'Use design patterns appropriately: Factory for object creation, Observer for event handling, Strategy for algorithm selection, Repository for data access.',
     'design patterns factory observer strategy repository object creation event handling algorithm selection data access',
     'M'),
    
    (global_default_scope_id,
     'Apply separation of concerns: keep business logic separate from presentation layer, data access layer separate from business logic. Use layered architecture.',
     'separation of concerns business logic presentation layer data access layered architecture',
     'M'),
    
    -- Performance and Scalability
    (global_default_scope_id,
     'Optimize database queries: use indexes appropriately, avoid N+1 queries, implement pagination for large datasets. Monitor query performance regularly.',
     'database optimization indexes n+1 queries pagination large datasets performance monitoring',
     'M'),
    
    (global_default_scope_id,
     'Implement caching strategies: use Redis for session data, cache frequently accessed data, implement cache invalidation policies. Monitor cache hit rates.',
     'caching strategies redis session data frequently accessed cache invalidation hit rates',
     'M'),
    
    (global_default_scope_id,
     'Use asynchronous processing for long-running tasks. Implement job queues for background processing. Provide status updates for long operations.',
     'asynchronous processing long-running tasks job queues background processing status updates',
     'L'),
    
    (global_default_scope_id,
     'Database migrations should be reversible with proper down() methods. Test migrations on staging before production. Never edit existing migrations after they are merged.',
     'database migration reversible down staging production schema changes',
     'M'),
    
    -- Testing Standards
    (global_default_scope_id,
     'Write tests first (TDD) or immediately after implementation. Maintain 80 percent or higher code coverage. Test edge cases, error conditions, and boundary values.',
     'test driven development tdd code coverage edge cases error conditions boundary values',
     'S'),
    
    (global_default_scope_id,
     'Use appropriate test types: unit tests for individual functions, integration tests for component interactions, end-to-end tests for user workflows.',
     'test types unit tests integration tests end-to-end tests functions component interactions user workflows',
     'S'),
    
    (global_default_scope_id,
     'Mock external dependencies in unit tests. Use test doubles (stubs, mocks, fakes) appropriately. Keep tests isolated and deterministic.',
     'mock external dependencies unit tests test doubles stubs mocks fakes isolated deterministic',
     'S'),
    
    -- Code Quality Standards
    (global_default_scope_id,
     'Use consistent naming conventions: PascalCase for classes, camelCase for functions/variables, UPPER_CASE for constants. Be descriptive but concise.',
     'naming conventions pascalcase classes camelcase functions variables upper case constants descriptive concise',
     'XS'),
    
    (global_default_scope_id,
     'Keep functions small and focused (max 20-30 lines). Extract complex logic into separate functions. Use early returns to reduce nesting.',
     'functions small focused max lines complex logic separate functions early returns reduce nesting',
     'S'),
    
    (global_default_scope_id,
     'Remove dead code and unused imports regularly. Use linters and formatters to maintain consistent code style. Set up pre-commit hooks.',
     'dead code unused imports linters formatters consistent style pre-commit hooks',
     'XS'),
    
    (global_default_scope_id,
     'Use meaningful variable names that describe the data they hold. Avoid abbreviations and single-letter variables (except for loop counters).',
     'meaningful variable names describe data avoid abbreviations single letter loop counters',
     'XS'),
    
    -- API Design Standards
    (global_default_scope_id,
     'RESTful APIs should use appropriate HTTP methods: GET for retrieval, POST for creation, PUT for updates, DELETE for removal. Use proper status codes.',
     'restful apis http methods get post put delete status codes retrieval creation updates removal',
     'S'),
    
    (global_default_scope_id,
     'API responses should be consistent in structure. Include metadata like pagination info, timestamps, and request IDs for debugging.',
     'api responses consistent structure metadata pagination timestamps request ids debugging',
     'S'),
    
    (global_default_scope_id,
     'Implement API versioning from the start. Use URL versioning (/api/v1/) or header versioning. Maintain backward compatibility when possible.',
     'api versioning url versioning header versioning backward compatibility',
     'S'),
    
    (global_default_scope_id,
     'Validate all API inputs: required fields, data types, format constraints. Return clear error messages with field-specific validation failures.',
     'api validation inputs required fields data types format constraints error messages field specific',
     'S'),
    
    -- Data Management
    (global_default_scope_id,
     'Implement proper data backup and recovery procedures. Test restore processes regularly. Use database replication for high availability.',
     'data backup recovery procedures test restore database replication high availability',
     'L'),
    
    (global_default_scope_id,
     'Use database transactions for operations that modify multiple tables. Implement proper rollback mechanisms for failed operations.',
     'database transactions multiple tables rollback mechanisms failed operations',
     'M'),
    
    (global_default_scope_id,
     'Implement soft deletes for important data instead of hard deletes. Add deleted_at timestamps and filter deleted records in queries.',
     'soft deletes hard deletes deleted_at timestamps filter deleted records queries',
     'S'),
    
    -- Monitoring and Observability
    (global_default_scope_id,
     'Implement comprehensive logging: application logs, access logs, error logs. Use structured logging formats like JSON for better parsing.',
     'comprehensive logging application access error structured logging json parsing',
     'S'),
    
    (global_default_scope_id,
     'Set up monitoring for key metrics: response times, error rates, resource usage. Create alerts for threshold violations. Use dashboards for visualization.',
     'monitoring key metrics response times error rates resource usage alerts threshold dashboards visualization',
     'M'),
    
    (global_default_scope_id,
     'Implement health check endpoints for all services. Include dependency checks (database, external APIs). Use for load balancer health monitoring.',
     'health check endpoints services dependency checks database external apis load balancer monitoring',
     'S'),
    
    -- Configuration and Environment Management
    (global_default_scope_id,
     'Use configuration files for environment-specific settings. Support multiple environments (development, staging, production) with appropriate configurations.',
     'configuration files environment specific settings multiple environments development staging production',
     'S'),
    
    (global_default_scope_id,
     'Implement feature flags for gradual rollouts and A/B testing. Use external flag management systems for dynamic configuration changes.',
     'feature flags gradual rollouts ab testing external flag management dynamic configuration',
     'M'),
    
    -- Language-Specific Standards
    (global_default_scope_id,
     'JavaScript/TypeScript: Use strict mode, prefer const over let, use async/await over callbacks, implement proper type definitions in TypeScript.',
     'javascript typescript strict mode const let async await callbacks type definitions',
     'S'),
    
    (global_default_scope_id,
     'Python: Follow PEP 8 style guide, use virtual environments, implement proper exception handling, use type hints for function parameters and return values.',
     'python pep 8 style guide virtual environments exception handling type hints function parameters return values',
     'S'),
    
    (global_default_scope_id,
     'Java: Follow Oracle naming conventions, use proper access modifiers, implement equals() and hashCode() together, use try-with-resources for resource management.',
     'java oracle naming conventions access modifiers equals hashcode try with resources resource management',
     'S'),
    
    (global_default_scope_id,
     'React: Use functional components with hooks, implement proper key props for lists, use React.memo for performance optimization, handle loading and error states.',
     'react functional components hooks key props lists react memo performance optimization loading error states',
     'S'),
    
    -- DevOps and Deployment Standards
    (global_default_scope_id,
     'Use Infrastructure as Code (IaC) tools like Terraform or CloudFormation. Version control infrastructure definitions. Implement automated deployments.',
     'infrastructure as code iac terraform cloudformation version control infrastructure definitions automated deployments',
     'L'),
    
    (global_default_scope_id,
     'Implement blue-green or rolling deployments for zero-downtime updates. Use feature toggles to control new feature activation.',
     'blue green rolling deployments zero downtime updates feature toggles feature activation',
     'L'),
    
    (global_default_scope_id,
     'Use containerization (Docker) for consistent environments. Implement proper container security practices: non-root users, minimal base images.',
     'containerization docker consistent environments container security non-root users minimal base images',
     'M'),
    
    -- Team Collaboration Standards
    (global_default_scope_id,
     'Conduct regular code reviews focusing on logic, security, performance, and maintainability. Provide constructive feedback and learn from others.',
     'code reviews logic security performance maintainability constructive feedback learn from others',
     'S'),
    
    (global_default_scope_id,
     'Participate in daily standups, sprint planning, and retrospectives. Communicate blockers early and ask for help when needed.',
     'daily standups sprint planning retrospectives communicate blockers ask for help',
     'XS'),
    
    (global_default_scope_id,
     'Document architectural decisions and their rationale. Share knowledge through team presentations, pair programming, and mentoring.',
     'document architectural decisions rationale share knowledge team presentations pair programming mentoring',
     'S'),
    
    -- Long-term Maintenance Standards
    (global_default_scope_id,
     'Regularly update dependencies to patch security vulnerabilities. Use automated dependency scanning tools. Test updates in staging first.',
     'update dependencies security vulnerabilities automated dependency scanning test updates staging',
     'M'),
    
    (global_default_scope_id,
     'Refactor code regularly to improve maintainability. Remove technical debt during feature development. Do not let code quality deteriorate over time.',
     'refactor code maintainability remove technical debt feature development code quality deteriorate',
     'M'),
    
    (global_default_scope_id,
     'Plan for scalability from the beginning. Design systems to handle growth in users, data, and features. Monitor performance trends.',
     'plan scalability beginning design systems handle growth users data features monitor performance trends',
     'L'),
    
    (global_default_scope_id,
     'Implement proper logging retention policies. Archive old logs, clean up temporary files, and manage disk space proactively.',
     'logging retention policies archive old logs clean temporary files manage disk space proactively',
     'S');
    
    -- Insert shopcraft:default knowledge
    INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
    (shopcraft_default_scope_id,
     'ShopCraft uses microservices architecture with React frontend, Node.js backend services, PostgreSQL database, and Redis for caching. All services communicate via REST APIs with JWT authentication.',
     'shopcraft microservices react nodejs postgresql redis rest api jwt authentication architecture',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft payment processing integrates with Stripe for credit cards and PayPal for alternative payments. All payment data must be PCI DSS compliant. Use webhooks for payment status updates.',
     'shopcraft payment stripe paypal pci dss compliant webhooks credit card processing',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft inventory management uses real-time stock tracking with Redis. When stock falls below threshold, automatic purchase orders are created. Stock levels are updated via webhook from warehouse system.',
     'shopcraft inventory stock tracking redis threshold purchase orders warehouse webhook',
     'M'),
    
    (shopcraft_default_scope_id,
     'ShopCraft customer data includes personal information, purchase history, and preferences. All customer data must be encrypted at rest and in transit. GDPR compliance required for EU customers.',
     'shopcraft customer data personal information purchase history gdpr encryption privacy',
     'M');
    
    -- Insert frontend-team knowledge
    INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
    (frontend_scope_id,
     'ShopCraft frontend uses React 18 with TypeScript, Material-UI components, and React Query for server state management. All components must be fully typed and include unit tests with Jest and React Testing Library.',
     'shopcraft frontend react typescript material-ui react-query jest testing library components',
     'M'),
    
    (frontend_scope_id,
     'ShopCraft product catalog page implements infinite scrolling with virtualization for performance. Use React Window for large product lists. Implement skeleton loading states and error boundaries.',
     'shopcraft product catalog infinite scrolling virtualization react window skeleton loading error boundaries',
     'L'),
    
    (frontend_scope_id,
     'ShopCraft checkout flow is a multi-step process: Cart Review → Shipping Info → Payment Method → Order Confirmation. Each step validates input and persists data to prevent loss on page refresh.',
     'shopcraft checkout multi-step cart review shipping payment confirmation validation persistence',
     'L'),
    
    (frontend_scope_id,
     'ShopCraft mobile responsiveness uses CSS Grid and Flexbox with breakpoints at 768 pixels and 1024 pixels. Touch targets must be minimum 44 pixels. Test on iOS Safari and Android Chrome.',
     'shopcraft mobile responsive css grid flexbox breakpoints touch targets ios safari android chrome',
     'M');
    
    -- Insert backend-api knowledge  
    INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
    (backend_scope_id,
     'ShopCraft API uses Express.js with Helmet for security headers, compression middleware, and request logging with Winston. All endpoints require JWT authentication except health checks.',
     'shopcraft api express helmet security compression winston jwt authentication middleware',
     'M'),
    
    (backend_scope_id,
     'ShopCraft database uses PostgreSQL with connection pooling (max 20 connections). Implement read replicas for reporting queries. Use database transactions for multi-table operations.',
     'shopcraft database postgresql connection pooling read replicas transactions multi-table operations',
     'M'),
    
    (backend_scope_id,
     'ShopCraft order processing workflow: Validate Payment → Reserve Inventory → Create Order → Send Confirmation Email → Update Analytics. If any step fails, rollback previous steps.',
     'shopcraft order processing workflow payment validation inventory reservation email confirmation analytics rollback',
     'L'),
    
    (backend_scope_id,
     'ShopCraft API testing uses Jest for unit tests, Supertest for integration tests, and Postman collections for manual testing. Maintain 80 percent or higher code coverage. Mock external services in tests.',
     'shopcraft api testing jest supertest postman code coverage mock external services integration',
     'M');
    
    -- Insert devops-deploy knowledge
    INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
    (devops_scope_id,
     'ShopCraft deployment uses Docker containers orchestrated with Kubernetes on AWS EKS. Implement rolling deployments with health checks. Use Helm charts for configuration management.',
     'shopcraft deployment docker kubernetes aws eks rolling deployments health checks helm charts',
     'L'),
    
    (devops_scope_id,
     'ShopCraft monitoring uses Prometheus for metrics, Grafana for dashboards, and CloudWatch for AWS resources. Set up alerts for high CPU, memory usage, and API response times over 500 milliseconds.',
     'shopcraft monitoring prometheus grafana cloudwatch alerts cpu memory api response time',
     'M'),
    
    (devops_scope_id,
     'ShopCraft CI/CD pipeline: GitHub Actions → Build Docker Images → Run Tests → Security Scanning → Deploy to Staging → Manual Approval → Deploy to Production.',
     'shopcraft cicd github actions docker build tests security scanning staging production approval',
     'L'),
    
    (devops_scope_id,
     'ShopCraft backup strategy: PostgreSQL automated backups every 6 hours with 30-day retention. Redis persistence enabled. Application logs stored in CloudWatch with 90-day retention.',
     'shopcraft backup postgresql redis cloudwatch logs retention automated 6 hours 30 days 90 days',
     'M');
    
    
END $$;