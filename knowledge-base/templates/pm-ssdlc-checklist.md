# PM SSDLC Checklist - Security Guardrails

*Actionable checklist for Product Managers to ensure SSDLC compliance*

## Pre-Development Phase Checklist

### Requirements & Planning ✅
- [ ] **Security requirements defined** in PRD
  - Authentication/authorization requirements
  - Data protection requirements
  - Compliance requirements (GDPR, HIPAA, etc.)
  - Performance security requirements
- [ ] **Risk assessment completed**
  - Business impact analysis
  - Threat landscape review
  - Regulatory compliance check
- [ ] **Security resources allocated**
  - Security team involvement planned
  - Security testing budget allocated
  - Security training scheduled
- [ ] **Acceptance criteria include security**
  - Security test cases defined
  - Security performance criteria set
  - Compliance validation criteria

### Design Phase ✅
- [ ] **Threat modeling completed** ([Shostack methodology](https://shostack.org/resources/threat-modeling))
  - Data flow diagrams created
  - Threat scenarios identified
  - Mitigations documented
  - Risk ratings assigned
- [ ] **Security architecture reviewed**
  - Security controls identified
  - Attack surface minimized
  - Defense in depth implemented
- [ ] **Security design decisions documented**
  - Rationale for security choices
  - Trade-offs documented
  - Alternative approaches considered

## Development Phase Checklist

### Implementation Monitoring ✅
- [ ] **Secure coding standards enforced**
  - OWASP guidelines followed
  - Code review checklist used
  - Static analysis tools configured
- [ ] **Security progress tracked**
  - Security features implementation status
  - Security technical debt monitored
  - Security milestone completion
- [ ] **Security team collaboration**
  - Regular security consultations
  - Security expert code reviews
  - Security guidance documented

### Testing & Verification ✅
- [ ] **Security testing completed**
  - Static Application Security Testing (SAST)
  - Dynamic Application Security Testing (DAST)
  - Interactive Application Security Testing (IAST)
  - Dependency vulnerability scanning
- [ ] **Security test results reviewed**
  - Critical vulnerabilities addressed
  - Medium/low risk items triaged
  - False positives documented
- [ ] **Penetration testing conducted**
  - External security assessment
  - Results reviewed and addressed
  - Remediation plan created

## Pre-Release Phase Checklist

### Deployment Security ✅
- [ ] **Secure configuration validated**
  - Production security settings reviewed
  - Secrets management implemented
  - Access controls configured
- [ ] **Security monitoring setup**
  - Security logging enabled
  - Alerting configured
  - Incident response procedures ready
- [ ] **Security documentation complete**
  - Security runbook created
  - Incident response plan updated
  - Security contact information current

### Release Approval ✅
- [ ] **Security sign-off obtained**
  - Security team approval
  - Compliance team approval (if applicable)
  - Risk acceptance documented
- [ ] **Security metrics baseline established**
  - Security KPIs defined
  - Monitoring dashboards configured
  - Reporting schedule established

## Post-Release Phase Checklist

### Ongoing Security ✅
- [ ] **Security monitoring active**
  - Security alerts reviewed daily
  - Security metrics tracked weekly
  - Security reports generated monthly
- [ ] **Vulnerability management process**
  - Regular vulnerability scans
  - Patch management schedule
  - Emergency response procedures
- [ ] **Continuous improvement**
  - Security lessons learned captured
  - Process improvements identified
  - Team feedback incorporated

## Emergency Security Checklist

### Security Incident Response ⚠️
- [ ] **Immediate assessment**
  - Incident severity determined
  - Impact scope identified
  - Stakeholders notified
- [ ] **Response coordination**
  - Incident response team activated
  - Communication plan executed
  - Remediation actions initiated
- [ ] **Post-incident activities**
  - Root cause analysis completed
  - Process improvements identified
  - Documentation updated

## PM-Specific Security Responsibilities

### Daily Activities
- [ ] Review security alerts and metrics
- [ ] Monitor security feature development progress
- [ ] Ensure security considerations in feature decisions
- [ ] Maintain security stakeholder communication

### Weekly Activities
- [ ] Review security test results
- [ ] Update security risk register
- [ ] Check security milestone progress
- [ ] Coordinate with security team

### Monthly Activities
- [ ] Security metrics review and reporting
- [ ] Security process effectiveness assessment
- [ ] Security training needs evaluation
- [ ] Security roadmap updates

## Key Security Resources Quick Reference

### Threat Modeling
- **Process:** [Shostack Threat Modeling](https://shostack.org/resources/threat-modeling)
- **Tools:** Microsoft Threat Modeling Tool, OWASP Threat Dragon
- **Output:** Threat model document, risk register

### Security Standards
- **Verification:** [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- **Maturity:** [OWASP SAMM](https://owaspsamm.org/)
- **Process:** [OWASP Threat Modeling Process](https://owasp.org/www-community/Threat_Modeling_Process)

### Security Testing
- **Static Analysis:** SonarQube, Checkmarx, GitHub Advanced Security
- **Dynamic Testing:** OWASP ZAP, Burp Suite
- **Dependencies:** Snyk, GitHub Dependabot

## Escalation Procedures

### When to Escalate
- Critical security vulnerabilities found
- Security milestone delays
- Compliance requirement conflicts
- Security resource constraints

### Escalation Contacts
- **Security Team Lead:** [Contact Info]
- **Compliance Officer:** [Contact Info]
- **Engineering Manager:** [Contact Info]
- **Product Director:** [Contact Info]

## Documentation Templates

### Security Requirement Template
```markdown
**Security Requirement:** [Brief description]
**Rationale:** [Why this is needed]
**Acceptance Criteria:** [How to verify]
**Priority:** [Critical/High/Medium/Low]
**Compliance:** [Relevant standards/regulations]
```

### Security Decision Template
```markdown
**Decision:** [What was decided]
**Context:** [Situation requiring decision]
**Options Considered:** [Alternatives evaluated]
**Rationale:** [Why this option chosen]
**Risks:** [Identified risks and mitigations]
**Review Date:** [When to reassess]
```

---

*PM SSDLC checklist for daily security guardrails*
