-- Sample data for KaizenMCP Knowledge System
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
     NULL),
    
    (global_default_scope_id,
     'Implement input validation on both client and server sides. Use parameterized queries to prevent SQL injection. Validate file uploads for type and size.',
     'input validation client server parameterized queries sql injection file uploads',
     'S'),
    
    (global_default_scope_id,
     'Environment variables should never be committed to version control. Use .env files locally and proper secret management in production. Always add .env to .gitignore.',
     'environment variables secrets gitignore env file security configuration',
     NULL),
    
    (global_default_scope_id,
     'API rate limiting should be implemented to prevent abuse: 100 requests per minute for authenticated users, 20 requests per minute for anonymous users. Use Redis for distributed rate limiting.',
     'api rate limiting redis abuse protection throttling requests per minute authentication',
     'M'),
    
    -- Git Workflow and Communication Standards
    (global_default_scope_id,
     'Git commit messages should follow semantic versioning: feat(scope): description for new features, fix(scope): description for bug fixes, docs: for documentation changes. Keep first line under 50 characters.',
     'git commit message semantic versioning feat fix docs scope changelog',
     NULL),
    
    (global_default_scope_id,
     'All pull requests must include: clear description, testing instructions, screenshots for UI changes, and link to related issues. Request review from at least one team member.',
     'pull request description testing instructions screenshots ui changes review team member',
     NULL),
    
    (global_default_scope_id,
     'Code comments should explain WHY, not WHAT. Focus on business logic, edge cases, and complex algorithms. Avoid obvious comments that repeat the code.',
     'code comments why not what business logic edge cases algorithms obvious',
     NULL),
    
    (global_default_scope_id,
     'Documentation should be written for the intended audience. Technical docs for developers, user guides for end users. Keep documentation up-to-date with code changes.',
     'documentation audience technical developers user guides up-to-date code changes',
     NULL),
    
    (global_default_scope_id,
     'Use semantic versioning (MAJOR.MINOR.PATCH) for releases. Increment MAJOR for breaking changes, MINOR for new features, PATCH for bug fixes. Tag releases in git.',
     'semantic versioning major minor patch releases breaking changes features bug fixes git tags',
     NULL),
    
    -- Design Patterns and Architecture
    (global_default_scope_id,
     'Follow SOLID principles: Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. Design classes with single, well-defined purposes.',
     'solid principles single responsibility open closed liskov substitution interface segregation dependency inversion',
     NULL),
    
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
     NULL),
    
    (global_default_scope_id,
     'Apply separation of concerns: keep business logic separate from presentation layer, data access layer separate from business logic. Use layered architecture.',
     'separation of concerns business logic presentation layer data access layered architecture',
     NULL),
    
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
     NULL),
    
    (global_default_scope_id,
     'Keep functions small and focused (max 20-30 lines). Extract complex logic into separate functions. Use early returns to reduce nesting.',
     'functions small focused max lines complex logic separate functions early returns reduce nesting',
     NULL),
    
    (global_default_scope_id,
     'Remove dead code and unused imports regularly. Use linters and formatters to maintain consistent code style. Set up pre-commit hooks.',
     'dead code unused imports linters formatters consistent style pre-commit hooks',
     NULL),
    
    (global_default_scope_id,
     'Use meaningful variable names that describe the data they hold. Avoid abbreviations and single-letter variables (except for loop counters).',
     'meaningful variable names describe data avoid abbreviations single letter loop counters',
     NULL),
    
    -- API Design Standards
    (global_default_scope_id,
     'RESTful APIs should use appropriate HTTP methods: GET for retrieval, POST for creation, PUT for updates, DELETE for removal. Use proper status codes.',
     'restful apis http methods get post put delete status codes retrieval creation updates removal',
     NULL),
    
    (global_default_scope_id,
     'API responses should be consistent in structure. Include metadata like pagination info, timestamps, and request IDs for debugging.',
     'api responses consistent structure metadata pagination timestamps request ids debugging',
     NULL),
    
    (global_default_scope_id,
     'Implement API versioning from the start. Use URL versioning (/api/v1/) or header versioning. Maintain backward compatibility when possible.',
     'api versioning url versioning header versioning backward compatibility',
     NULL),
    
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
     NULL),
    
    (global_default_scope_id,
     'Python: Follow PEP 8 style guide, use virtual environments, implement proper exception handling, use type hints for function parameters and return values.',
     'python pep 8 style guide virtual environments exception handling type hints function parameters return values',
     NULL),
    
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
     NULL),
    
    (global_default_scope_id,
     'Participate in daily standups, sprint planning, and retrospectives. Communicate blockers early and ask for help when needed.',
     'daily standups sprint planning retrospectives communicate blockers ask for help',
     NULL),
    
    (global_default_scope_id,
     'Document architectural decisions and their rationale. Share knowledge through team presentations, pair programming, and mentoring.',
     'document architectural decisions rationale share knowledge team presentations pair programming mentoring',
     NULL),
    
    -- Long-term Maintenance Standards
    (global_default_scope_id,
     'Regularly update dependencies to patch security vulnerabilities. Use automated dependency scanning tools. Test updates in staging first.',
     'update dependencies security vulnerabilities automated dependency scanning test updates staging',
     'M'),
    
    (global_default_scope_id,
     'Refactor code regularly to improve maintainability. Remove technical debt during feature development. Do not let code quality deteriorate over time.',
     'refactor code maintainability remove technical debt feature development code quality deteriorate',
     NULL),
    
    (global_default_scope_id,
     'Plan for scalability from the beginning. Design systems to handle growth in users, data, and features. Monitor performance trends.',
     'plan scalability beginning design systems handle growth users data features monitor performance trends',
     'L'),
    
    (global_default_scope_id,
     'Implement proper logging retention policies. Archive old logs, clean up temporary files, and manage disk space proactively.',
     'logging retention policies archive old logs clean temporary files manage disk space proactively',
     'S'),
    
    -- Cloud and AWS Standards
    (global_default_scope_id,
     'Use AWS IAM roles and policies for secure access control. Follow principle of least privilege. Rotate access keys regularly and use temporary credentials when possible.',
     'aws iam roles policies least privilege access keys rotation temporary credentials security',
     'M'),
    
    (global_default_scope_id,
     'Implement AWS CloudFormation or Terraform for infrastructure as code. Version control infrastructure templates. Use stack sets for multi-account deployments.',
     'aws cloudformation terraform infrastructure as code stack sets multi-account deployment templates',
     'L'),
    
    (global_default_scope_id,
     'Configure AWS CloudWatch alarms for critical metrics: CPU utilization, memory usage, disk space, application errors. Set up SNS notifications for alerts.',
     'aws cloudwatch alarms cpu memory disk application errors sns notifications critical metrics',
     'M'),
    
    -- Advanced Testing Strategies
    (global_default_scope_id,
     'Implement contract testing for microservices using tools like Pact. Test API contracts between services to catch breaking changes early.',
     'contract testing microservices pact api contracts breaking changes integration testing',
     'L'),
    
    (global_default_scope_id,
     'Use property-based testing for complex algorithms. Generate random test inputs to discover edge cases. Implement mutation testing to verify test quality.',
     'property based testing algorithms random inputs edge cases mutation testing test quality',
     'M'),
    
    (global_default_scope_id,
     'Implement visual regression testing for UI components. Use tools like Percy or Chromatic to catch visual changes. Include cross-browser testing.',
     'visual regression testing ui components percy chromatic cross browser testing visual changes',
     'M'),
    
    -- Accessibility Standards
    (global_default_scope_id,
     'Implement WCAG 2.1 AA accessibility standards. Use semantic HTML, proper ARIA labels, keyboard navigation support, and screen reader compatibility.',
     'wcag accessibility standards semantic html aria labels keyboard navigation screen reader compatibility',
     'M'),
    
    (global_default_scope_id,
     'Test with actual screen readers and keyboard-only navigation. Include alt text for images, captions for videos, and proper color contrast ratios.',
     'screen readers keyboard navigation alt text captions color contrast accessibility testing',
     'S'),
    
    -- Advanced Security Patterns
    (global_default_scope_id,
     'Implement OAuth 2.0 with PKCE for secure authentication flows. Use refresh tokens with proper rotation. Validate all redirect URLs against whitelist.',
     'oauth 2.0 pkce authentication flows refresh tokens rotation redirect urls whitelist security',
     'L'),
    
    (global_default_scope_id,
     'Use Content Security Policy (CSP) headers to prevent XSS attacks. Implement CSRF protection with tokens. Validate file uploads for malicious content.',
     'content security policy csp xss csrf protection tokens file uploads malicious content validation',
     'M'),
    
    -- Internationalization and Localization
    (global_default_scope_id,
     'Implement i18n with proper locale handling, currency formatting, date/time formats, and RTL language support. Use translation management systems.',
     'internationalization i18n locale currency date time rtl languages translation management systems',
     'L'),
    
    -- Advanced Async Patterns
    (global_default_scope_id,
     'Use message queues (RabbitMQ, Apache Kafka) for decoupled async processing. Implement dead letter queues for failed messages. Monitor queue metrics.',
     'message queues rabbitmq kafka async processing dead letter queues failed messages metrics monitoring',
     'L'),
    
    -- Additional Global Standards
    (global_default_scope_id,
     'Implement proper HTTP caching with Cache-Control headers, ETags, and Last-Modified timestamps. Use CDN for static assets and implement cache invalidation strategies.',
     'http caching cache control etags last modified cdn static assets cache invalidation strategies',
     'M'),
    
    (global_default_scope_id,
     'Use database connection pooling with appropriate limits. Implement connection health checks, timeout configurations, and graceful degradation for database failures.',
     'database connection pooling limits health checks timeout configurations graceful degradation failures',
     'M'),
    
    (global_default_scope_id,
     'Implement proper API documentation with OpenAPI/Swagger specifications. Include request/response examples, error codes, and authentication requirements.',
     'api documentation openapi swagger specifications request response examples error codes authentication requirements',
     'S'),
    
    (global_default_scope_id,
     'Use environment-specific configuration management. Implement feature toggles, A/B testing frameworks, and configuration validation with schemas.',
     'environment configuration management feature toggles ab testing frameworks configuration validation schemas',
     'M');
    
    -- Insert shopcraft:default knowledge
    INSERT INTO knowledge (scope_id, content, context, task_size) VALUES
    (shopcraft_default_scope_id,
     'ShopCraft uses microservices architecture with React frontend, Node.js backend services, PostgreSQL database, and Redis for caching. All services communicate via REST APIs with JWT authentication.',
     'shopcraft microservices react nodejs postgresql redis rest api jwt authentication architecture',
     NULL),
    
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
     NULL),
    
    -- Advanced ShopCraft Business Logic
    (shopcraft_default_scope_id,
     'ShopCraft order management implements complex workflows: order validation, fraud detection, inventory reservation, payment authorization, fulfillment routing, and shipment tracking.',
     'shopcraft order management workflow validation fraud detection inventory payment fulfillment shipping tracking',
     'XL'),
    
    (shopcraft_default_scope_id,
     'ShopCraft search uses Elasticsearch with faceted filtering, autocomplete, spell correction, and personalized ranking. Search analytics track query performance and user behavior.',
     'shopcraft search elasticsearch faceted filtering autocomplete spell correction personalized ranking analytics',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft recommendation engine uses collaborative filtering and content-based algorithms. Track user interactions, purchase history, and browsing patterns for personalization.',
     'shopcraft recommendation engine collaborative filtering content based algorithms user interactions personalization',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft shopping cart persists across devices using Redis with 30-day expiration. Support guest checkout, saved items, and cart abandonment email campaigns.',
     'shopcraft shopping cart persistence redis cross device guest checkout saved items abandonment email',
     'M'),
    
    (shopcraft_default_scope_id,
     'ShopCraft user authentication supports OAuth social login, two-factor authentication, password reset flows, and account verification. Use JWT with refresh tokens.',
     'shopcraft authentication oauth social login two factor password reset verification jwt refresh tokens',
     'M'),
    
    (shopcraft_default_scope_id,
     'ShopCraft email system uses SendGrid for transactional emails: order confirmations, shipping notifications, password resets. Implement template management and tracking.',
     'shopcraft email sendgrid transactional order confirmation shipping notification password reset template tracking',
     'M'),
    
    (shopcraft_default_scope_id,
     'ShopCraft analytics tracks user behavior, conversion funnels, A/B test results, and business metrics. Use Google Analytics 4 and custom event tracking.',
     'shopcraft analytics user behavior conversion funnels ab testing business metrics google analytics events',
     'M'),
    
    (shopcraft_default_scope_id,
     'ShopCraft A/B testing framework supports feature flags, traffic splitting, statistical significance testing, and conversion tracking for continuous optimization.',
     'shopcraft ab testing feature flags traffic splitting statistical significance conversion tracking optimization',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft mobile app uses React Native with shared business logic. Implement push notifications, offline support, and native payment integrations.',
     'shopcraft mobile react native shared logic push notifications offline support native payments',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft social media integration includes sharing buttons, social login, customer reviews syndication, and influencer partnership tracking.',
     'shopcraft social media sharing login reviews syndication influencer partnership tracking integration',
     'M'),
    
    (shopcraft_default_scope_id,
     'ShopCraft advanced payment flows support wallet payments, buy-now-pay-later, subscriptions, refunds, chargebacks, and multi-currency transactions.',
     'shopcraft payment wallet bnpl subscriptions refunds chargebacks multi currency advanced flows',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft customer support includes live chat, ticket system, FAQ bot, return processing, and escalation workflows. Integrate with CRM systems.',
     'shopcraft customer support live chat tickets faq bot returns escalation workflows crm integration',
     'M'),
    
    -- Additional ShopCraft Business Features
    (shopcraft_default_scope_id,
     'ShopCraft loyalty program tracks customer points, tier levels, reward redemption, and personalized offers. Integrate with email marketing and customer analytics.',
     'shopcraft loyalty program points tier levels reward redemption personalized offers email marketing customer analytics',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft multi-vendor marketplace supports seller onboarding, commission calculations, payout scheduling, and vendor analytics dashboards.',
     'shopcraft multi vendor marketplace seller onboarding commission calculations payout scheduling vendor analytics dashboards',
     'XL'),
    
    (shopcraft_default_scope_id,
     'ShopCraft international expansion requires currency conversion, tax calculation by region, shipping zone management, and localized payment methods.',
     'shopcraft international expansion currency conversion tax calculation region shipping zones localized payment methods',
     'L'),
    
    (shopcraft_default_scope_id,
     'ShopCraft business intelligence dashboard aggregates sales metrics, customer lifetime value, inventory turnover, and predictive analytics for demand forecasting.',
     'shopcraft business intelligence dashboard sales metrics customer lifetime value inventory turnover predictive analytics demand forecasting',
     'L'),
    
    -- Conflict Test Items - Multi-Level Conflicts
    (shopcraft_default_scope_id,
     'ShopCraft testing requires payment flow integration tests with PCI compliance validation and fraud detection scenario coverage.',
     'shopcraft testing payment flow integration pci compliance validation fraud detection scenario coverage',
     'M'),
    
    (shopcraft_default_scope_id,
     'ShopCraft errors use user-friendly messages without exposing system internals for security. Include helpful suggestions for user actions.',
     'shopcraft errors user friendly messages security system internals suggestions user actions',
     'S'),
    
    (shopcraft_default_scope_id,
     'ShopCraft deployments require customer notification and staging validation windows with rollback procedures for payment system updates.',
     'shopcraft deployments customer notification staging validation windows rollback procedures payment system updates',
     'M'),
    
    -- Conflict Test Items - Single-Level Conflicts  
    (shopcraft_default_scope_id,
     'ShopCraft API rate limiting: 1000 requests per minute for premium users, 100 for basic users, with Redis-based distributed throttling.',
     'shopcraft api rate limiting 1000 requests premium 100 basic redis distributed throttling',
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
     'M'),
    
    -- Multi-Level Conflict Winner: Frontend Testing
    (frontend_scope_id,
     'Frontend testing includes visual regression tests with Percy and accessibility audits for all components using axe-core and manual screen reader validation.',
     'frontend testing visual regression percy accessibility audits components axe-core screen reader validation',
     'M'),
    
    -- Single-Level Conflict: Frontend vs ShopCraft Default
    (frontend_scope_id,
     'Frontend components use styled-components with custom breakpoint system and mobile-first responsive design patterns for optimal performance.',
     'frontend components styled-components custom breakpoint mobile-first responsive design performance',
     'S');
    
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
     'M'),
    
    -- Multi-Level Conflict Winner: Backend Error Handling
    (backend_scope_id,
     'Backend API errors include correlation IDs, structured logging, and circuit breaker patterns for handling external service failures and timeouts.',
     'backend api errors correlation ids structured logging circuit breaker external service failures timeouts',
     'L'),
    
    -- Single-Level Conflict: Backend vs ShopCraft Default
    (backend_scope_id,
     'Backend API requires dedicated connection pools per service with circuit breaker patterns for database failures and automatic failover mechanisms.',
     'backend api dedicated connection pools service circuit breaker database failures automatic failover',
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
     'M'),
    
    -- Multi-Level Conflict Winner: DevOps Deployment
    (devops_scope_id,
     'DevOps uses canary deployments with 5% traffic splits and automated rollback triggers based on error rate thresholds and performance metrics.',
     'devops canary deployments 5 percent traffic splits automated rollback triggers error rate performance metrics',
     'XL'),
    
    -- Single-Level Conflict: DevOps vs Global Default
    (devops_scope_id,
     'DevOps log management uses centralized ELK stack with 90-day retention and automated cleanup workflows for compliance and storage optimization.',
     'devops log management centralized elk stack 90-day retention automated cleanup workflows compliance storage optimization',
     'L');
    
    
END $$;

-- =============================================================================
-- CONFLICT RESOLUTION TEST DATA
-- =============================================================================

-- Create conflict resolution records to test conflict system
-- Note: IDs will be determined after insertion, this is conceptual structure

DO $$
DECLARE
    -- Global scope knowledge IDs (will be resolved dynamically)
    global_testing_id BIGINT;
    global_error_handling_id BIGINT;
    global_deployment_id BIGINT;
    global_rate_limiting_id BIGINT;
    global_logging_id BIGINT;
    
    -- ShopCraft scope knowledge IDs  
    shopcraft_testing_id BIGINT;
    shopcraft_error_id BIGINT;
    shopcraft_deployment_id BIGINT;
    shopcraft_rate_limiting_id BIGINT;
    shopcraft_database_id BIGINT;
    shopcraft_mobile_id BIGINT;
    
    -- Project scope knowledge IDs (winners)
    frontend_testing_id BIGINT;
    frontend_mobile_id BIGINT;
    backend_error_id BIGINT;
    backend_connection_id BIGINT;
    devops_deployment_id BIGINT;
    devops_logging_id BIGINT;
    
BEGIN
    -- Find existing global knowledge items to be suppressed
    SELECT k.id INTO global_testing_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'global' AND s.name = 'default' 
    AND k.content LIKE 'Write tests first (TDD)%';
    
    SELECT k.id INTO global_error_handling_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'global' AND s.name = 'default' 
    AND k.content LIKE 'Implement proper error handling%';
    
    SELECT k.id INTO global_deployment_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'global' AND s.name = 'default' 
    AND k.content LIKE 'Use blue-green or rolling deployments%';
    
    SELECT k.id INTO global_rate_limiting_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'global' AND s.name = 'default' 
    AND k.content LIKE 'API rate limiting should be implemented%';
    
    SELECT k.id INTO global_logging_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'global' AND s.name = 'default' 
    AND k.content LIKE 'Implement proper logging retention%';
    
    -- Find new ShopCraft knowledge items
    SELECT k.id INTO shopcraft_testing_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'default' 
    AND k.content LIKE 'ShopCraft testing requires payment flow%';
    
    SELECT k.id INTO shopcraft_error_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'default' 
    AND k.content LIKE 'ShopCraft errors use user-friendly%';
    
    SELECT k.id INTO shopcraft_deployment_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'default' 
    AND k.content LIKE 'ShopCraft deployments require customer%';
    
    SELECT k.id INTO shopcraft_rate_limiting_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'default' 
    AND k.content LIKE 'ShopCraft API rate limiting: 1000%';
    
    -- Find existing ShopCraft items to be suppressed
    SELECT k.id INTO shopcraft_database_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'default' 
    AND k.content LIKE 'ShopCraft database uses PostgreSQL%';
    
    SELECT k.id INTO shopcraft_mobile_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'default' 
    AND k.content LIKE 'ShopCraft mobile responsiveness uses%';
    
    -- Find new project-level winner items
    SELECT k.id INTO frontend_testing_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'frontend-team' 
    AND k.content LIKE 'Frontend testing includes visual regression%';
    
    SELECT k.id INTO frontend_mobile_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'frontend-team' 
    AND k.content LIKE 'Frontend components use styled-components%';
    
    SELECT k.id INTO backend_error_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'backend-api' 
    AND k.content LIKE 'Backend API errors include correlation%';
    
    SELECT k.id INTO backend_connection_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'backend-api' 
    AND k.content LIKE 'Backend API requires dedicated connection%';
    
    SELECT k.id INTO devops_deployment_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'devops-deploy' 
    AND k.content LIKE 'DevOps uses canary deployments%';
    
    SELECT k.id INTO devops_logging_id FROM knowledge k 
    JOIN scopes s ON k.scope_id = s.id 
    JOIN namespaces n ON s.namespace_id = n.id 
    WHERE n.name = 'shopcraft' AND s.name = 'devops-deploy' 
    AND k.content LIKE 'DevOps log management uses centralized%';
    
    -- Create conflict resolution records
    -- Multi-Level Conflicts (3 scenarios)
    
    -- 1. Testing: Frontend wins over ShopCraft and Global
    INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids) 
    VALUES (frontend_testing_id, ARRAY[shopcraft_testing_id, global_testing_id]);
    
    -- 2. Error Handling: Backend wins over ShopCraft and Global  
    INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids)
    VALUES (backend_error_id, ARRAY[shopcraft_error_id, global_error_handling_id]);
    
    -- 3. Deployment: DevOps wins over ShopCraft and Global
    INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids)
    VALUES (devops_deployment_id, ARRAY[shopcraft_deployment_id, global_deployment_id]);
    
    -- Single-Level Conflicts (4 scenarios)
    
    -- 4. Rate Limiting: ShopCraft wins over Global
    INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids)
    VALUES (shopcraft_rate_limiting_id, ARRAY[global_rate_limiting_id]);
    
    -- 5. Database Connection: Backend wins over ShopCraft  
    INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids)
    VALUES (backend_connection_id, ARRAY[shopcraft_database_id]);
    
    -- 6. Logging: DevOps wins over Global
    INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids)
    VALUES (devops_logging_id, ARRAY[global_logging_id]);
    
    -- 7. Mobile Design: Frontend wins over ShopCraft
    INSERT INTO knowledge_conflicts (active_knowledge_id, suppressed_knowledge_ids)
    VALUES (frontend_mobile_id, ARRAY[shopcraft_mobile_id]);
    
END $$;
