# Project Kaizen - Multi-Project Product Architecture

## The Challenge

Modern software products aren't single repositories - they're ecosystems:
- E-commerce platform: Web frontend, mobile apps, backend services, admin portal, data pipeline
- SaaS product: Marketing site, web app, API, mobile apps, DevOps infrastructure, data warehouse
- Enterprise system: Multiple microservices, shared libraries, deployment configs, monitoring stack

Each repository has unique concerns, yet they share common patterns, standards, and business context.

This architecture is designed for small trusted teams and individual developers who need powerful organization without enterprise complexity. All users with access are trusted collaborators.

## Four-Tier Knowledge Architecture

### Tier 1: General Knowledge
Universal best practices that apply across all projects:
- "Always handle null/undefined checks in JavaScript"
- "Use dependency injection for better testability"
- "API endpoints should return consistent error formats"

### Tier 2: Product Knowledge (via Product Hub)
Shared knowledge for all projects within a product:
- "Our design system uses 8px grid spacing"
- "All APIs use JWT tokens with 1-hour expiry"
- "Customer IDs are UUIDs in format 'cust_[uuid]'"
- "Deploy order: database → backend → frontend"

### Tier 3: Group Knowledge (via Group Hubs)
Shared knowledge for related projects within a product:
- Payment Services Group: "All payment operations require audit logging"
- Core Services Group: "Use event sourcing for state changes"
- Data Pipeline Group: "Process files in 1GB chunks maximum"
- Frontend Group: "Share React component library"

### Tier 4: Project Knowledge
Repository-specific information:
- "This React app uses Redux Toolkit for state"
- "The payment service requires PCI compliance"
- "Mobile app must support iOS 14+"

## Hierarchy Example: Large Enterprise Platform

```
General Knowledge (Industry Best Practices)
└── Product: ACME Platform (Product Hub)
    ├── Group: Core Services (Group Hub)
    │   ├── user-service
    │   ├── auth-service
    │   ├── notification-service
    │   └── audit-service
    ├── Group: Payment Services (Group Hub)
    │   ├── payment-gateway
    │   ├── billing-service
    │   ├── invoice-service
    │   ├── refund-processor
    │   └── payment-reconciliation
    ├── Group: Data Services (Group Hub)
    │   ├── etl-pipeline
    │   ├── analytics-engine
    │   ├── reporting-service
    │   └── data-warehouse
    ├── Group: Frontend Apps (Group Hub)
    │   ├── customer-web-app
    │   ├── admin-portal
    │   ├── mobile-ios
    │   └── mobile-android
    └── Standalone Projects
        ├── api-gateway
        ├── monitoring-stack
        └── deployment-configs
```

## Group Hub Concept

### What It Is
A knowledge repository for closely related projects that share domain-specific patterns, constraints, and decisions beyond product-wide standards.

### When To Use Group Hubs
- **Microservice Domains**: Payment, shipping, inventory services sharing domain logic
- **Technology Stacks**: All React apps sharing component patterns
- **Compliance Boundaries**: Services handling PII with special requirements
- **Team Boundaries**: Projects owned by same team with shared practices

### Example: Payment Services Group

**Group-Specific Knowledge:**
- "All monetary values stored as integers in cents"
- "Payment operations must be idempotent with 24-hour keys"
- "PCI compliance requires field-level encryption"
- "Use payment-commons library for currency handling"
- "Webhook retries: 1min, 5min, 30min, 2hr, 6hr"

**Why Not Product-Wide?**
These rules are irrelevant to frontend apps or data services, would create noise if stored at product level.

## Knowledge Access Hierarchy

When the AI agent works on a project, it accesses knowledge in this order:

1. **Project Knowledge** (most specific)
2. **Group Knowledge** (if project belongs to a group)
3. **Product Knowledge** (product-wide standards)
4. **General Knowledge** (industry best practices)

### Example: Working on payment-gateway service

the AI agent accesses:
1. payment-gateway specific rules
2. Payment Services Group standards
3. ACME Platform conventions
4. General microservice best practices

## Real-World Scenarios

### Scenario 1: Creating New Payment Service
```
Architect: "Create a new subscription-billing service"
the AI agent: "I'll create this as part of the Payment Services group. It will inherit:
        
From Payment Group:
- Integer cents for money
- PCI compliance patterns
- Payment webhook standards
- Common payment library usage

From Product Hub:
- JWT authentication
- Logging standards
- Deployment process

Should I proceed with this knowledge context?"
```

### Scenario 2: Cross-Group Pattern Recognition
```
Week 1 - In Payment Services:
Architect: "All payment events need correlation IDs"

Week 3 - In Core Services:
Architect: "Add correlation IDs to all user events"

the AI agent: "I notice correlation IDs are being added in multiple groups. 
         Should this be promoted to a product-wide standard?"
Architect: "Yes, good observation"

Result: Pattern moves from group level to product level
```

### Scenario 3: Group-Specific Technology
```
Working on data-warehouse project:

the AI agent: [Checks Data Services Group knowledge]
        "I see this group uses Apache Spark for processing. 
         The group standard is Spark 3.2 with these optimizations:
         - Adaptive query execution enabled
         - Dynamic partition pruning
         - 4GB executor memory default"

Architect: "Perfect, apply those standards"
```

## Configuration Examples

### Setting Up Groups
```
Architect: "I need to organize our 40 microservices"
the AI agent: "Let's create logical groups. What are the main domains?"

Architect: "Payment processing, core business logic, data analytics, and customer-facing apps"

the AI agent: "I'll create this structure:
Product Hub: acme-platform-hub
Groups:
- payment-services-group (payment domain)
- core-services-group (business logic)
- data-services-group (analytics)
- frontend-apps-group (customer UIs)

Which repositories belong to each group?"

[Architect assigns repos to groups]
```

### Knowledge Promotion Flow
```
Project Level → Group Level → Product Level → General Level
     ↑              ↑              ↑              ↑
   Specific    Domain-wide    Company-wide    Universal
```

Each promotion requires approval and consideration of applicability.

## Advanced Use Cases

### Use Case 1: Compliance Boundaries
```
Group: GDPR Services (handles EU customer data)
├── eu-user-service
├── eu-analytics
└── eu-data-export

Group Knowledge:
- "Data retention maximum 2 years"
- "Right-to-deletion within 30 days"
- "Encryption at rest required"
- "Data residency: EU regions only"
```

### Use Case 2: Technology Migration
```
Group: Legacy Services (being modernized)
├── old-inventory-system
├── legacy-order-processor
└── classic-reporting

Group Knowledge:
- "Maintaining compatibility with SOAP APIs"
- "Database: Oracle 11g limitations"
- "No async/await (Node.js 8)"
- "Migration path documented in..."
```

### Use Case 3: Shared Libraries
```
Group: Common Libraries
├── company-auth-lib
├── company-logging-lib
├── company-metrics-lib
└── company-testing-utils

Group Knowledge:
- "Semantic versioning required"
- "Breaking changes need 6-month deprecation"
- "All libraries publish to internal npm"
- "Documentation required for public APIs"
```

## Benefits of Group Hubs

### For Large Organizations
- **Manageable Complexity**: 100+ repos organized into logical groups
- **Domain Expertise**: Payment team knowledge stays with payment services
- **Reduced Noise**: Frontend devs don't see data pipeline conventions
- **Flexible Structure**: Groups can be created/modified as architecture evolves

### For Development Teams
- **Relevant Context**: Only see knowledge that applies to your work
- **Faster Onboarding**: New dev on payment team learns payment patterns
- **Clear Boundaries**: Understand which rules apply at which level
- **Technology Freedom**: Groups can use different tech stacks

### For Knowledge Management
- **Natural Organization**: Matches actual team/domain structure
- **Controlled Scope**: Knowledge doesn't leak across unrelated services
- **Evolution Path**: Patterns can promote from group → product → general
- **Maintainability**: Easier to update group-specific rules

## Edge Cases and Considerations

### Case 1: Project in Multiple Groups
```
Scenario: analytics-api serves both Payment and Data groups
Solution: Primary group assignment with secondary access
the AI agent: "analytics-api primarily belongs to Data Services but also 
         accesses Payment Services patterns for billing analytics"
```

### Case 2: Group Reorganization
```
Scenario: Company restructures, payment split into regions
Solution: Create new groups, migrate knowledge
- payment-services-na (North America)
- payment-services-eu (Europe)
- payment-services-apac (Asia-Pacific)
Shared payment knowledge promoted to product level
```

### Case 3: Temporary Groups
```
Scenario: Migration project with temporary services
Solution: Time-bounded group
Group: migration-2024 (expires: 2024-12-31)
Knowledge: "Temporary dual-write patterns"
           "Legacy system compatibility"
           "Will be deleted after migration"
```

## Summary

The four-tier architecture (General → Product → Group → Project) provides:

1. **Scalability** for large products with dozens or hundreds of repositories
2. **Domain Isolation** keeping specialized knowledge where it belongs
3. **Flexible Organization** matching real organizational structures
4. **Progressive Generalization** as patterns prove widely applicable
5. **Reduced Cognitive Load** by filtering irrelevant knowledge

This mirrors how large engineering organizations actually operate - with company standards, product decisions, team practices, and project specifics all coexisting in a logical hierarchy.
