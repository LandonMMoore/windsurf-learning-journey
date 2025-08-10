# Threat Modeling Template

*Based on Shostack methodology and OWASP Threat Modeling Process*

## Project Information

**Project Name:** [Project/Feature Name]
**Date:** [Date]
**Threat Modeler:** [Name]
**Reviewers:** [Security Team, Architects, etc.]
**Version:** [Version Number]

## 1. What Are We Building?

### System Overview
**Description:** [Brief description of the system/feature]

**Business Purpose:** [Why this system exists]

**Key Stakeholders:**
- **Business Owner:** [Name/Role]
- **Technical Owner:** [Name/Role]
- **Security Contact:** [Name/Role]

### System Scope
**In Scope:**
- [ ] [Component 1]
- [ ] [Component 2]
- [ ] [Component 3]

**Out of Scope:**
- [ ] [Component A]
- [ ] [Component B]
- [ ] [Component C]

### Data Flow Diagram
```
[Create visual diagram showing:]
- External entities (users, systems)
- Processes (applications, services)
- Data stores (databases, files)
- Data flows (connections between components)
- Trust boundaries (security perimeters)
```

**Key Assets:**
1. **[Asset Name]** - [Description and sensitivity level]
2. **[Asset Name]** - [Description and sensitivity level]
3. **[Asset Name]** - [Description and sensitivity level]

## 2. What Can Go Wrong?

### STRIDE Analysis

For each component, analyze using STRIDE methodology:

#### Component: [Component Name]

**Spoofing (S)**
- **Threat:** [Description of spoofing threat]
- **Impact:** [Business/technical impact]
- **Likelihood:** [High/Medium/Low]
- **Existing Controls:** [Current mitigations]
- **Risk Rating:** [Critical/High/Medium/Low]

**Tampering (T)**
- **Threat:** [Description of tampering threat]
- **Impact:** [Business/technical impact]
- **Likelihood:** [High/Medium/Low]
- **Existing Controls:** [Current mitigations]
- **Risk Rating:** [Critical/High/Medium/Low]

**Repudiation (R)**
- **Threat:** [Description of repudiation threat]
- **Impact:** [Business/technical impact]
- **Likelihood:** [High/Medium/Low]
- **Existing Controls:** [Current mitigations]
- **Risk Rating:** [Critical/High/Medium/Low]

**Information Disclosure (I)**
- **Threat:** [Description of information disclosure threat]
- **Impact:** [Business/technical impact]
- **Likelihood:** [High/Medium/Low]
- **Existing Controls:** [Current mitigations]
- **Risk Rating:** [Critical/High/Medium/Low]

**Denial of Service (D)**
- **Threat:** [Description of DoS threat]
- **Impact:** [Business/technical impact]
- **Likelihood:** [High/Medium/Low]
- **Existing Controls:** [Current mitigations]
- **Risk Rating:** [Critical/High/Medium/Low]

**Elevation of Privilege (E)**
- **Threat:** [Description of privilege escalation threat]
- **Impact:** [Business/technical impact]
- **Likelihood:** [High/Medium/Low]
- **Existing Controls:** [Current mitigations]
- **Risk Rating:** [Critical/High/Medium/Low]

### Attack Scenarios

#### Scenario 1: [Attack Name]
**Description:** [Detailed attack scenario]
**Attacker Profile:** [Internal/External, Skill level, Motivation]
**Attack Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]
**Impact:** [What happens if successful]
**Likelihood:** [Probability of occurrence]

#### Scenario 2: [Attack Name]
**Description:** [Detailed attack scenario]
**Attacker Profile:** [Internal/External, Skill level, Motivation]
**Attack Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]
**Impact:** [What happens if successful]
**Likelihood:** [Probability of occurrence]

## 3. What Are We Going to Do About It?

### Risk Assessment Matrix

| Threat ID | Threat Description | Impact | Likelihood | Risk Level | Mitigation Strategy |
|-----------|-------------------|---------|------------|------------|-------------------|
| T001 | [Threat description] | High | Medium | High | [Mitigation approach] |
| T002 | [Threat description] | Medium | High | High | [Mitigation approach] |
| T003 | [Threat description] | Low | Low | Low | [Accept/Monitor] |

### Mitigation Strategies

#### High Priority Mitigations
1. **[Mitigation Name]**
   - **Threat Addressed:** [Threat ID(s)]
   - **Implementation:** [How to implement]
   - **Owner:** [Responsible team/person]
   - **Timeline:** [When to complete]
   - **Verification:** [How to verify effectiveness]

2. **[Mitigation Name]**
   - **Threat Addressed:** [Threat ID(s)]
   - **Implementation:** [How to implement]
   - **Owner:** [Responsible team/person]
   - **Timeline:** [When to complete]
   - **Verification:** [How to verify effectiveness]

#### Medium Priority Mitigations
1. **[Mitigation Name]**
   - **Threat Addressed:** [Threat ID(s)]
   - **Implementation:** [How to implement]
   - **Owner:** [Responsible team/person]
   - **Timeline:** [When to complete]
   - **Verification:** [How to verify effectiveness]

#### Accepted Risks
1. **[Risk Description]**
   - **Rationale:** [Why accepting this risk]
   - **Conditions:** [Under what conditions]
   - **Review Date:** [When to reassess]
   - **Approver:** [Who approved acceptance]

## 4. Did We Do a Good Job?

### Validation Checklist
- [ ] **Threat model covers all system components**
- [ ] **Data flow diagram is accurate and complete**
- [ ] **All trust boundaries identified**
- [ ] **STRIDE analysis completed for each component**
- [ ] **Attack scenarios are realistic and detailed**
- [ ] **Risk ratings are justified and consistent**
- [ ] **Mitigations are specific and actionable**
- [ ] **Implementation timeline is realistic**
- [ ] **Verification methods are defined**

### Review and Approval
- [ ] **Security team review completed**
- [ ] **Architecture team review completed**
- [ ] **Development team review completed**
- [ ] **Product team review completed**

**Approved by:**
- **Security Lead:** [Name] - [Date]
- **Technical Lead:** [Name] - [Date]
- **Product Manager:** [Name] - [Date]

### Follow-up Actions
- [ ] **Implementation tracking setup**
- [ ] **Regular review schedule established**
- [ ] **Metrics and monitoring defined**
- [ ] **Team training needs identified**

## Appendices

### A. Reference Materials
- [Shostack Threat Modeling](https://shostack.org/resources/threat-modeling)
- [OWASP Threat Modeling Process](https://owasp.org/www-community/Threat_Modeling_Process)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [STRIDE Methodology Guide](https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)

### B. Tools Used
- **Diagramming:** [Tool name and version]
- **Analysis:** [Tool name and version]
- **Documentation:** [Tool name and version]

### C. Assumptions and Constraints
**Assumptions:**
- [Assumption 1]
- [Assumption 2]
- [Assumption 3]

**Constraints:**
- [Constraint 1]
- [Constraint 2]
- [Constraint 3]

### D. Glossary
**[Term]:** [Definition]
**[Term]:** [Definition]
**[Term]:** [Definition]

---

**Document Control**
- **Created:** [Date]
- **Last Updated:** [Date]
- **Next Review:** [Date]
- **Document Owner:** [Name/Role]

*Threat modeling template based on industry best practices*
