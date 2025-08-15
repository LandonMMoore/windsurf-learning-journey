# EDS GitHub Integration Guide

## 1. Repository Structure Recommendation

### 1.1 Recommended Repository Organization
Based on the architecture analysis and current development practices, the EDS project should follow a multi-repository structure:

```
EDS Project Organization:
├── eds-backend/                 # Main backend repository
│   ├── src/
│   │   ├── EDS.API/            # Web API project
│   │   ├── EDS.Core/           # Business logic
│   │   ├── EDS.Data/           # Data access layer
│   │   ├── EDS.Integration/    # External system integrations
│   │   └── EDS.Tests/          # Unit and integration tests
│   ├── docs/                   # Technical documentation
│   ├── scripts/                # Database scripts and utilities
│   └── .github/                # GitHub workflows and templates
│
├── eds-frontend/               # Frontend repository
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── utils/              # Utility functions
│   │   └── tests/              # Frontend tests
│   ├── public/                 # Static assets
│   └── .github/                # Frontend-specific workflows
│
└── eds-infrastructure/         # Infrastructure as Code
    ├── terraform/              # Terraform configurations
    ├── azure-pipelines/        # CI/CD pipeline definitions
    ├── docker/                 # Docker configurations
    └── monitoring/             # Monitoring and alerting configs
```

### 1.2 Repository Naming Convention
- **Main Backend**: `eds-backend` or `ddot-eds-backend`
- **Frontend**: `eds-frontend` or `ddot-eds-frontend`
- **Infrastructure**: `eds-infrastructure` or `ddot-eds-infrastructure`
- **Documentation**: `eds-docs` (optional, if separate from main repos)

## 2. GitHub Integration with ClickUp

### 2.1 Branch Naming Strategy
Link GitHub branches to ClickUp tasks using the following naming convention:

```
Branch Naming Format:
feature/CU-{task_id}-{brief-description}
bugfix/CU-{task_id}-{brief-description}
hotfix/CU-{task_id}-{brief-description}

Examples:
feature/CU-868f3depd-add-llm-token-usage-logs
bugfix/CU-868f5m76a-dashboard-widget-api-update
hotfix/CU-868f65rh2-excel-invalid-rows-utility
```

### 2.2 Commit Message Convention
Include ClickUp task references in commit messages:

```
Commit Message Format:
<type>(<scope>): <description> [CU-{task_id}]

Examples:
feat(api): add queries and user_id logs to llm_token_usage table [CU-868f3depd]
fix(dashboard): update widget API for generic chart payload [CU-868f5m76a]
refactor(excel): implement utility for invalid rows retention [CU-868f65rh2]
```

### 2.3 Pull Request Templates
Create PR templates that automatically link to ClickUp tasks:

```markdown
## Pull Request Template

### ClickUp Task
- **Task ID**: CU-{task_id}
- **Task URL**: https://app.clickup.com/t/{task_id}
- **Task Status**: [to do/in progress/peer review/qa/done]

### Description
Brief description of changes made.

### Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

### Security Checklist
- [ ] Security review completed
- [ ] No sensitive data exposed
- [ ] Authentication/authorization properly implemented
- [ ] Input validation implemented
- [ ] OWASP guidelines followed

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Security testing completed

### Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] Architecture documentation updated
```

## 3. CI/CD Integration

### 3.1 GitHub Actions Workflow
Implement automated workflows that update ClickUp task status:

```yaml
# .github/workflows/ci-cd.yml
name: EDS CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Security Scan
        run: |
          # SAST scanning
          # Dependency scanning
          # Container scanning
      
      - name: Update ClickUp Task
        if: always()
        uses: clickup/github-action@v1
        with:
          clickup-token: ${{ secrets.CLICKUP_TOKEN }}
          task-id: ${{ env.CLICKUP_TASK_ID }}
          status: ${{ job.status == 'success' && 'qa' || 'blocked' }}

  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '6.0.x'
      
      - name: Build
        run: dotnet build --configuration Release
      
      - name: Test
        run: dotnet test --configuration Release --collect:"XPlat Code Coverage"
      
      - name: Security Tests
        run: |
          # Run security-specific tests
          # OWASP ZAP scanning
          # Penetration testing automation

  deploy:
    needs: [security-scan, build-and-test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Staging
        run: |
          # Deployment steps
      
      - name: Update ClickUp on Success
        uses: clickup/github-action@v1
        with:
          clickup-token: ${{ secrets.CLICKUP_TOKEN }}
          task-id: ${{ env.CLICKUP_TASK_ID }}
          status: 'done'
```

### 3.2 Security-First CI/CD Pipeline
Implement security gates at every stage:

```yaml
# Security-focused pipeline stages
stages:
  1. Code Quality & Security Scan (SAST)
  2. Dependency Vulnerability Scan
  3. Build & Unit Tests
  4. Integration Tests
  5. Security Tests (DAST)
  6. Infrastructure Security Scan
  7. Deploy to Staging
  8. Penetration Testing
  9. Deploy to Production
  10. Post-deployment Security Validation
```

## 4. Repository Security Configuration

### 4.1 Branch Protection Rules
Configure branch protection for main branches:

```yaml
Branch Protection Settings:
- Require pull request reviews (minimum 2 reviewers)
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Require conversation resolution before merging
- Restrict pushes that create files larger than 100MB
- Require signed commits
- Include administrators in restrictions
```

### 4.2 Security Policies
Implement GitHub security features:

```yaml
Security Configuration:
- Enable Dependabot alerts
- Enable Dependabot security updates
- Enable Dependabot version updates
- Configure code scanning (CodeQL)
- Enable secret scanning
- Configure private vulnerability reporting
- Set up security advisories
```

### 4.3 Repository Secrets Management
Configure necessary secrets for CI/CD:

```yaml
Required Secrets:
- CLICKUP_TOKEN: ClickUp API token for task updates
- AZURE_CREDENTIALS: Azure service principal for deployment
- SONAR_TOKEN: SonarQube token for code quality
- DOCKER_HUB_TOKEN: Docker registry access
- SECURITY_SCAN_TOKEN: Security scanning service token
```

## 5. Documentation Integration

### 5.1 Repository Documentation Structure
Each repository should include comprehensive documentation:

```
Repository Documentation:
├── README.md                   # Project overview and quick start
├── CONTRIBUTING.md             # Contribution guidelines
├── SECURITY.md                 # Security policies and reporting
├── CODE_OF_CONDUCT.md          # Code of conduct
├── CHANGELOG.md                # Version history and changes
├── docs/
│   ├── architecture/           # Architecture documentation
│   ├── api/                    # API documentation
│   ├── deployment/             # Deployment guides
│   ├── security/               # Security documentation
│   └── development/            # Development guides
└── .github/
    ├── ISSUE_TEMPLATE/         # Issue templates
    ├── PULL_REQUEST_TEMPLATE/  # PR templates
    └── workflows/              # GitHub Actions workflows
```

### 5.2 Cross-Reference Documentation
Link GitHub repositories to project documentation:

```markdown
# Repository Links in Project Documentation

## EDS Project Repositories
- **Backend Repository**: [eds-backend](https://github.com/organization/eds-backend)
- **Frontend Repository**: [eds-frontend](https://github.com/organization/eds-frontend)
- **Infrastructure Repository**: [eds-infrastructure](https://github.com/organization/eds-infrastructure)

## Key Documentation Links
- **Project Documentation**: [Current Location]
- **API Documentation**: [GitHub Pages/Repository Wiki]
- **Architecture Diagrams**: [Repository docs/architecture/]
- **Security Documentation**: [Repository docs/security/]
```

## 6. Issue and Project Management

### 6.1 GitHub Issues Integration
Configure GitHub Issues to sync with ClickUp:

```yaml
Issue Labels:
- type/bug: Bug reports
- type/feature: Feature requests
- type/security: Security-related issues
- priority/critical: Critical priority
- priority/high: High priority
- priority/medium: Medium priority
- priority/low: Low priority
- component/backend: Backend-related
- component/frontend: Frontend-related
- component/integration: Integration-related
- status/blocked: Blocked issues
- security/review-required: Requires security review
```

### 6.2 GitHub Projects Integration
Use GitHub Projects to mirror ClickUp workflow:

```yaml
Project Boards:
- EDS Development Board
  - Columns: Backlog, To Do, In Progress, Peer Review, QA, Done
  - Automation: Move cards based on PR status
  - Integration: Sync with ClickUp task status

- Security Review Board
  - Columns: Security Review Queue, In Review, Approved, Blocked
  - Automation: Auto-assign security reviewers
  - Integration: Link to security requirements checklist
```

## 7. Code Quality and Security Integration

### 7.1 Pre-commit Hooks
Implement security-focused pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/Yelp/detect-secrets
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/PyCQA/bandit
    hooks:
      - id: bandit
        args: ['-r', '.']

  - repo: local
    hooks:
      - id: security-scan
        name: Security Scan
        entry: ./scripts/security-scan.sh
        language: script
```

### 7.2 Code Review Automation
Implement automated code review checks:

```yaml
Code Review Automation:
- Security-focused review checklist
- Automated security scanning results
- OWASP compliance checking
- Dependency vulnerability assessment
- Code quality metrics integration
- Performance impact analysis
```

## 8. Monitoring and Alerting Integration

### 8.1 GitHub Integration Monitoring
Monitor GitHub integration health:

```yaml
Monitoring Metrics:
- CI/CD pipeline success rate
- Security scan pass rate
- Code review completion time
- Deployment frequency
- Lead time for changes
- Mean time to recovery
- Change failure rate
```

### 8.2 Alert Configuration
Configure alerts for critical events:

```yaml
Alert Triggers:
- Security scan failures
- Failed deployments
- Critical vulnerabilities detected
- Unauthorized repository access
- Large file commits
- Secrets detected in commits
- Branch protection rule violations
```

## 9. Migration and Setup Plan

### 9.1 Repository Setup Checklist
- [ ] Create repository structure according to recommendations
- [ ] Configure branch protection rules
- [ ] Set up security scanning and policies
- [ ] Configure CI/CD pipelines with security gates
- [ ] Implement ClickUp integration
- [ ] Set up monitoring and alerting
- [ ] Create documentation templates
- [ ] Configure pre-commit hooks
- [ ] Set up code review automation
- [ ] Test integration workflows

### 9.2 Team Onboarding
- [ ] Train team on new GitHub workflows
- [ ] Provide security-focused development guidelines
- [ ] Set up development environment templates
- [ ] Create troubleshooting guides
- [ ] Establish code review processes
- [ ] Configure IDE security plugins
- [ ] Set up local security scanning

## 10. Compliance and Audit Trail

### 10.1 Audit Requirements
Maintain comprehensive audit trails:

```yaml
Audit Trail Components:
- All code changes with author attribution
- Security review approvals
- Deployment history and rollbacks
- Access control changes
- Security scan results
- Vulnerability remediation tracking
- Compliance validation records
```

### 10.2 Compliance Reporting
Generate compliance reports from GitHub data:

```yaml
Compliance Reports:
- SSDLC phase gate completions
- Security review coverage
- Vulnerability management metrics
- Code quality trends
- Deployment success rates
- Incident response tracking
```

---
*Document Version: 1.0*  
*Last Updated: August 14, 2025*  
*Next Review: September 14, 2025*  
*Owner: Development Team*  
*Integration Status: Ready for Implementation*
