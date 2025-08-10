# SSDLC Quick Reference Guide

*Fast lookup for security guardrails and responsibilities*

## Essential SSDLC Resources

### 🔗 Key External References
- **[Shostack Threat Modeling](https://shostack.org/resources/threat-modeling)** - Industry standard methodology
- **[OWASP SAMM](https://owaspsamm.org/)** - Software Assurance Maturity Model
- **[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)** - Security Verification Standard
- **[OWASP Threat Modeling Process](https://owasp.org/www-community/Threat_Modeling_Process)** - Implementation guide

### 📋 Internal Templates & Checklists
- **[SSDLC Overview](./ssdlc-overview.md)** - Comprehensive framework guide
- **[PM SSDLC Checklist](./pm-ssdlc-checklist.md)** - Your security guardrails
- **[Dev Team Checklist](./dev-team-ssdlc-checklist.md)** - Developer responsibilities
- **[Threat Modeling Template](./threat-modeling-template.md)** - Shostack-based template

## Phase-by-Phase Quick Checklist

### 📋 Requirements & Planning
**PM Must Do:**
- [ ] Define security requirements in PRD
- [ ] Identify compliance needs
- [ ] Allocate security resources
- [ ] Set security acceptance criteria

**Dev Team Must Do:**
- [ ] Review security requirements
- [ ] Assess technical feasibility
- [ ] Identify security dependencies
- [ ] Estimate security effort

### 🎨 Design Phase
**PM Must Do:**
- [ ] Ensure threat modeling completed
- [ ] Review security architecture
- [ ] Approve security design decisions
- [ ] Document security rationale

**Dev Team Must Do:**
- [ ] Create threat models (use [template](./threat-modeling-template.md))
- [ ] Design secure architecture
- [ ] Document security controls
- [ ] Get security team review

### 💻 Implementation Phase
**PM Must Do:**
- [ ] Monitor security implementation
- [ ] Track security technical debt
- [ ] Ensure coding standards followed
- [ ] Validate security features

**Dev Team Must Do:**
- [ ] Follow secure coding practices
- [ ] Run static analysis tools
- [ ] Conduct security code reviews
- [ ] Address vulnerability findings

### 🧪 Testing Phase
**PM Must Do:**
- [ ] Define security test criteria
- [ ] Review security test results
- [ ] Prioritize security fixes
- [ ] Validate requirements met

**Dev Team Must Do:**
- [ ] Execute security test cases
- [ ] Run DAST/SAST tools
- [ ] Fix security vulnerabilities
- [ ] Document test results

### 🚀 Deployment Phase
**PM Must Do:**
- [ ] Approve security configuration
- [ ] Ensure monitoring in place
- [ ] Validate incident procedures
- [ ] Document deployment decisions

**Dev Team Must Do:**
- [ ] Implement secure deployment
- [ ] Configure security monitoring
- [ ] Set up automated scanning
- [ ] Document procedures

## Critical Security Gates

### 🚫 Cannot Proceed Without:
1. **Design Gate:** Threat model completed and approved
2. **Code Gate:** Security code review passed
3. **Test Gate:** Security tests passed
4. **Release Gate:** Security sign-off obtained

### ⚠️ Immediate Escalation Triggers:
- Critical security vulnerability found
- Security milestone delays
- Compliance requirement conflicts
- Security resource constraints

## Emergency Contacts

### Security Team
- **Security Lead:** [Contact Info]
- **Security Architect:** [Contact Info]
- **Incident Response:** [Contact Info]

### Compliance
- **Compliance Officer:** [Contact Info]
- **Legal/Privacy:** [Contact Info]

## Daily Security Habits

### For PMs:
- [ ] Review security alerts/metrics (5 min)
- [ ] Check security milestone progress (5 min)
- [ ] Ensure security in feature decisions (ongoing)

### For Developers:
- [ ] Run security scans before commit (automated)
- [ ] Review security findings (10 min)
- [ ] Follow secure coding checklist (ongoing)

## Weekly Security Activities

### For PMs:
- [ ] Security metrics review (30 min)
- [ ] Security team sync (30 min)
- [ ] Risk register update (15 min)

### For Developers:
- [ ] Security test results review (30 min)
- [ ] Security technical debt assessment (30 min)
- [ ] Team security knowledge sharing (30 min)

## Common Security Tools

### Static Analysis (SAST)
- **SonarQube:** Code quality and security
- **GitHub Advanced Security:** Integrated scanning
- **Checkmarx:** Enterprise security testing

### Dynamic Analysis (DAST)
- **OWASP ZAP:** Free web app scanner
- **Burp Suite:** Professional security testing
- **Netsparker:** Automated web security

### Dependency Scanning
- **Snyk:** Vulnerability management
- **GitHub Dependabot:** Automated dependency updates
- **WhiteSource:** Open source security

### Threat Modeling
- **Microsoft Threat Modeling Tool:** Free desktop tool
- **OWASP Threat Dragon:** Web-based modeling
- **IriusRisk:** Enterprise threat modeling

## Security Metrics to Track

### Development Metrics
- Security defects per release
- Time to fix critical security issues
- Security test coverage percentage
- SAST/DAST scan frequency

### Process Metrics
- Threat model completion rate
- Security training completion
- Security review gate compliance
- Security tool adoption rate

## Risk Assessment Quick Guide

### Risk = Impact × Likelihood

**Impact Levels:**
- **Critical:** Business shutdown, data breach, legal issues
- **High:** Significant business impact, customer data at risk
- **Medium:** Moderate business impact, limited data exposure
- **Low:** Minimal business impact, no data exposure

**Likelihood Levels:**
- **High:** Very likely to occur (>70% chance)
- **Medium:** Moderately likely (30-70% chance)
- **Low:** Unlikely to occur (<30% chance)

**Risk Matrix:**
| Impact/Likelihood | High | Medium | Low |
|------------------|------|--------|-----|
| **Critical** | Critical | Critical | High |
| **High** | Critical | High | Medium |
| **Medium** | High | Medium | Low |
| **Low** | Medium | Low | Low |

## Security Incident Response

### Immediate Actions (First 30 minutes):
1. **Assess:** Determine if it's a real security incident
2. **Contain:** Stop the attack/limit damage
3. **Notify:** Alert security team and stakeholders
4. **Document:** Record all actions taken

### Follow-up Actions (First 24 hours):
1. **Investigate:** Determine root cause
2. **Remediate:** Fix the vulnerability
3. **Communicate:** Update stakeholders
4. **Learn:** Document lessons learned

## Compliance Quick Reference

### GDPR Requirements:
- Data protection by design
- Privacy impact assessments
- Data breach notification (72 hours)
- User consent management

### HIPAA Requirements:
- Administrative safeguards
- Physical safeguards
- Technical safeguards
- Business associate agreements

### SOC 2 Requirements:
- Security controls
- Availability controls
- Processing integrity
- Confidentiality controls

---

*Quick reference for daily SSDLC implementation*
