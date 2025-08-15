# FAHP/FHWA ALIGNMENT PLAN
## Federal-Aid Highway Program Compliance Strategy for EDS

*Document Version*: 1.0  
*Date*: August 14, 2025  
*Status*: Implementation Planning  
*Priority*: **CRITICAL - FEDERAL COMPLIANCE**

---

## 🎯 **EXECUTIVE SUMMARY**

This document provides a comprehensive alignment plan for the EDS system to achieve full compliance with Federal-Aid Highway Program (FAHP) requirements, FHWA policies, and federal regulations. The plan addresses validation, governance, integration, automation, documentation, and process requirements based on consolidated stakeholder feedback and federal guidance.

**Key Objective**: Ensure EDS PAR workflow aligns with FHWA Division expectations and federal compliance standards while maintaining system sophistication and user experience.

---

## 📋 **COMPLIANCE REQUIREMENTS MAPPING**

### **A. VALIDATION & COMPLIANCE REQUIREMENTS**

#### **A.1 IDCR (Indirect Cost Recovery) Validation**
**Federal Requirement**: Validate IDCR against fund availability and NICRA criteria  
**Current EDS Status**: ⚠️ **PARTIAL** - Budget validation exists, IDCR-specific logic missing

**Implementation Requirements**:
```python
# Required Implementation Components:
├── IDCR Validation Service
│   ├── NICRA rate retrieval from SharePoint ETL
│   ├── Direct cost base calculation
│   ├── IDCR percentage validation
│   └── Fund availability cross-check via SharePoint data
├── SharePoint Data Integration
│   ├── DIFS data synchronization (existing ETL pipeline)
│   ├── NICRA rate caching and validation
│   ├── Fund availability data processing
│   └── Data freshness validation
├── Trigger Point Integration
│   ├── Budget & Funding step validation
│   ├── Funding Source Selection validation
│   └── Workflow stop on mismatch
└── Error Handling & Reporting
    ├── Mismatch error flags
    ├── Validation failure notifications
    ├── SharePoint sync status monitoring
    └── Audit trail logging
```

**EDS Implementation Plan**:
- **Phase 1**: Create `IDCRValidationService` class with SharePoint data source
- **Phase 2**: Enhance SharePoint ETL pipeline for NICRA rate processing
- **Phase 3**: Add validation triggers to PAR workflow steps
- **Phase 4**: Implement error handling, sync monitoring, and audit logging

#### **A.2 Program Code Validation**
**Federal Requirement**: Auto-fetch valid codes from FMIS/M60, validate against project type  
**Current EDS Status**: ⚠️ **PARTIAL** - FHWA service exists, M60 validation missing

**FAHP/FAR Part 31 Compliance Requirements**:
```python
# Federal Compliance Requirements:
├── 2 CFR 200.210 Requirements
│   ├── CFDA number validation (15 uniform data sets)
│   ├── Performance end date tracking
│   ├── Indirect cost rate validation
│   └── Federal award identification
├── FAR 31.201-3 Cost Reasonableness
│   ├── Prudent person standard validation
│   ├── Competitive business practice checks
│   └── Burden of proof documentation
├── FAR 31.203 Indirect Cost Allocation
│   ├── Logical cost groupings validation
│   ├── Common allocation base requirements
│   └── Pro rata share calculations
└── M60 Table Integration
    ├── Program code cross-validation
    ├── Federal share percentage limits
    └── FMIS 37/60 report reconciliation
```

**Implementation Requirements**:
```python
# Required Implementation Components:
├── M60 Integration Service
│   ├── Valid program code retrieval
│   ├── Project type mapping
│   ├── Federal share percentage validation
│   ├── CFDA code cross-validation
│   └── Real-time validation workflow
├── FAR Part 31 Validation Engine
│   ├── Cost reasonableness checks
│   ├── Allocability validation
│   ├── Indirect cost allocation rules
│   └── Unallowable cost detection
├── FAHP Compliance Module
│   ├── 2 CFR 200.210 data set validation
│   ├── Performance reporting requirements
│   ├── NICRA rate compliance checks
│   └── Federal award data integrity
└── Multi-System Cross-Validation
    ├── FMIS 37 report integration
    ├── FMIS 60 fund availability checks
    ├── SharePoint ETL data validation
    └── Real-time compliance monitoring
```

**EDS Implementation Plan**:
- **Phase 1**: Enhance `FHWAService` with M60 integration and FAR Part 31 validation
- **Phase 2**: Implement FAHP compliance module with 2 CFR 200 requirements
- **Phase 3**: Add multi-system cross-validation (FMIS 37/60, SharePoint ETL)
- **Phase 4**: Deploy real-time compliance monitoring and audit trails

#### **A.3 Comprehensive FAHP Regulation Compliance**
**Federal Requirement**: Validate all FAHP regulations, not just financial  
**Current EDS Status**: ⚠️ **GAPS** - Financial validation strong, regulatory validation partial

**Regulatory Compliance Matrix**:
| **Regulation** | **Current Status** | **Implementation Needed** |
|----------------|-------------------|---------------------------|
| 2 CFR 200 | 70% | Enhanced grant compliance validation, CFDA validation, 15 uniform data sets |
| FAR Part 31 | 60% | Cost reasonableness validation, indirect cost allocation, unallowable cost detection |
| FHWA Program Code Guidance | 30% | M60 table integration, FMIS 37/60 cross-validation |
| NEPA Compliance | 40% | Environmental date validation, project impact assessment |
| STIP Compliance | 50% | Reference validation system, transportation plan alignment |

**Detailed FAHP/FAR Validation Requirements**:
```python
FAHP_VALIDATION_MATRIX = {
    '2_cfr_200': {
        'section_200_210': 'Federal award 15 uniform data sets validation',
        'section_200_301': 'Performance measurement and reporting',
        'section_200_414': 'Indirect cost rate validation against NICRA',
        'implementation': 'Real-time CFDA, performance tracking, NICRA integration'
    },
    'far_part_31': {
        'section_31_201_2': 'Cost allowability determination (reasonable, allocable)',
        'section_31_201_3': 'Cost reasonableness validation (prudent person standard)',
        'section_31_201_4': 'Cost allocability to government contracts',
        'section_31_203': 'Indirect cost allocation and G&A calculations',
        'implementation': 'Automated cost validation, allocation base verification'
    },
    'cross_validation': {
        'idcr_validation': 'Multi-source validation: SharePoint ETL + FMIS 37/60 + M60',
        'fund_availability': 'Real-time fund balance checks against program codes',
        'compliance_monitoring': 'Continuous validation across all federal requirements'
    }
}
```

**Implementation Requirements**:
```python
# Required Regulatory Validation Services:
├── CFR200ComplianceService
├── FARPart31ValidationService  
├── NEPAComplianceValidator
├── STIPReferenceValidator
└── FHWAProgramCodeValidator
```

#### **A.4 Multi-Validation Requirements**
**Federal Requirement**: Authorization dates, NEPA dates, improvement types, cost estimates  
**Current EDS Status**: ⚠️ **PARTIAL** - Date validation exists, comprehensive checks missing

**Implementation Requirements**:
- Authorization date validation against project timeline
- NEPA date compliance checking
- Improvement type validation against program codes
- Cost estimate reasonableness checks
- Match ratio validation for multi-funded projects

---

### **B. GOVERNANCE & SIGNATURES REQUIREMENTS**

#### **B.1 Signature Hierarchy Implementation (Updated with Stakeholder Feedback)**
**Federal Requirement**: Correct FMIS XML signature mapping with role-based hierarchy  
**Current EDS Status**: ⚠️ **CRITICAL GAP** - Manual email-based signature collection identified

**Stakeholder Feedback**: "I'm hoping that EDS can trigger that [signature emails]"
**Current Manual Process**: Budget analysts create emails requesting signatures manually

**Confirmed Signature Hierarchy (6 Total Signatures)**:
```yaml
State Level Signatures (3 Required):
  - Calvin & Kathryn (OCFO) - First signature line
  - Environmental Officer (TBD) - Second signature  
  - Chief Engineer (TBD) - Third signature

Federal Level Signatures (3 Required):
  - FHWA Reviewer (Initial Review)
  - FHWA Recommender (Technical Recommendation)  
  - FHWA Approver (Final Federal Approval)

Role Permissions:
  - PM: Initiate/Edit (No Budget Approval)
  - RAD: Resource Allocation Validation
  - OCFO Budget Analyst: Program Code & Budget Review
  - OCFO Financial Officer: Final Governance Checkpoint
```

**EDS Automation Implementation Plan**:
```python
# Required Signature Workflow Automation:
├── Automated Email Generation
│   ├── Signature request email templates
│   ├── Sequential signature routing
│   ├── Status tracking and notifications
│   └── Reminder email automation
├── Digital Signature Integration
│   ├── Secure signature collection
│   ├── Audit trail logging
│   ├── Anti-tampering validation
│   └── Real-time status updates
└── FMIS Status Monitoring
    ├── Automated FMIS polling
    ├── Federal approval notifications
    ├── Dashboard status updates
    └── Error handling and alerts
```

**Critical Manual Processes to Automate**:
- **FMIS Data Entry**: "They type in all the information from the PAR into FMIS"
- **Status Monitoring**: "We have to go in there and check to see if it's done manually"
- **No Notifications**: "We don't get an email stating that it's done"
├── SignatureHierarchyService
│   ├── Role-based signature mapping
│   ├── Signature sequence validation
│   ├── Combined 2nd/3rd level signer support
│   └── XML signature payload generation
├── RoleBasedAccessControl (Enhanced)
│   ├── Signature permission matrix
│   ├── Step-based access controls
│   ├── Edit lock post-approval
│   └── Audit trail for all signatures
└── FMISXMLGenerator (Enhanced)
    ├── Signature block generation
    ├── Multi-level approval tracking
    └── Federal submission formatting
```

#### **B.2 Azure Active Directory Integration**
**Federal Requirement**: Centralized authentication with role-based permissions  
**Current EDS Status**: ⚠️ **FRAMEWORK EXISTS** - AAD integration needed

**Implementation Requirements**:
- Full Azure AD federation
- Role-based group mapping
- MFA enforcement for financial roles
- Session management and timeout controls
- Audit logging for authentication events

---

### **C. INTEGRATION & AUTOMATION REQUIREMENTS**

#### **C.1 DIFS Integration Enhancement (Critical Manual Gap Identified)**
**Federal Requirement**: Real-time data sync for fund availability and NICRA rates  
**Current EDS Status**: ⚠️ **CRITICAL MANUAL GAP** - Post-approval updates require manual entry

**Current Manual Process Identified**:
- **Post-Approval Updates**: "If the budget analyst does not put it in DIFS, it doesn't go in DIFS period"
- **Manual Data Entry**: "They have to type everything on that PAR into DIFS"
- **Exception**: "Except for the GIS, the GIS is not in DIFS"

**SharePoint ETL Pipeline Status** (Read-Only):
- **Data Sources**: R-series reports, EDS extracts, master data tables 
- **Processing**: Azure Functions-based ETL with validation 
- **NICRA Integration**: Enhanced pipeline for federal compliance 
- **Critical Gap**: No API integration for PAR data updates to DIFS 

**Required DIFS API Integration**:
- Automated PAR data submission to DIFS post-FHWA approval
- Eliminate manual data entry by budget analysts
- API integration with DIFS team for bidirectional sync checkpoint support

#### **C.2 System Integration Enhancement**
**Federal Requirement**: Maintain push/pull sync with ProTrack+, DIFS, FMIS  
**Current EDS Status**:  **GOOD FOUNDATION** - Multi-system integration architecture exists

**Required Enhancements**:
```python
# Integration Service Enhancements:
├── ProTrackPlusService (Enhanced)
│   ├── Validation checkpoint support
│   ├── Status synchronization
│   └── Milestone tracking integration
├── SharePointETLService (Enhanced)
│   ├── DIFS data synchronization (existing pipeline)
│   ├── NICRA rate processing and caching
│   ├── Fund availability data extraction
│   ├── Data validation and quality checks
│   └── Sync status monitoring and alerts
├── FMISIntegrationService (New)
│   ├── M60 table synchronization
│   ├── Program code validation
│   ├── XML submission handling
│   └── Federal response processing
└── ValidationCheckpointService (New)
    ├── Multi-system validation coordination
    ├── SharePoint data freshness validation
    ├── Checkpoint status management
    └── Integration failure handling
```

#### **C.2 Automation Requirements**
**Federal Requirement**: Automate IDCR calculations, budget splits, XML generation  
**Current EDS Status**: ✅ **STRONG** - Automation framework with Celery exists

**Required Automation Enhancements**:
```python
# Automation Service Enhancements:
├── IDCRAutomationService (New)
│   ├── Automatic IDCR calculation
│   ├── Budget split automation
│   ├── Validation trigger automation
│   └── Error notification automation
├── XMLGenerationService (Enhanced)
│   ├── Composite XML for multi-funded projects
│   ├── Signature block automation
│   ├── Federal schema compliance
│   └── Submission queue management
└── WorkflowAutomationService (Enhanced)
    ├── Post-approval edit locking
    ├── Automatic status transitions
    ├── Notification automation
    └── Escalation procedures
```

---

### **D. DOCUMENTATION & PROCESS REQUIREMENTS**

#### **D.1 Approved Written Procedures**
**Federal Requirement**: Document leadership-approved roles, responsibilities, processes  
**Current EDS Status**: ⚠️ **GAPS** - Technical documentation strong, process documentation partial

**Required Documentation**:
```
Process Documentation Requirements:
├── Role & Responsibility Matrix
│   ├── Signature authority definitions
│   ├── Approval workflow procedures
│   ├── Escalation procedures
│   └── Exception handling processes
├── Validation Procedures
│   ├── IDCR validation procedures
│   ├── Program code validation procedures
│   ├── Multi-funding validation procedures
│   └── Federal compliance checklists
├── Integration Procedures
│   ├── System synchronization procedures
│   ├── Data validation procedures
│   ├── Error handling procedures
│   └── Audit trail procedures
└── Governance Procedures
    ├── Signature sequence procedures
    ├── Access control procedures
    ├── Change management procedures
    └── Compliance monitoring procedures
```

#### **D.2 Audit & Reporting Requirements**
**Federal Requirement**: 7+ year retention, audit-ready reporting  
**Current EDS Status**: ✅ **STRONG** - Comprehensive logging architecture exists

**Required Enhancements**:
- Federal-specific audit report generation
- Funding source breakdown reporting
- Match ratio historical analysis
- Compliance status dashboards
- Exception and error reporting

---

## 🚀 **IMPLEMENTATION REQUIREMENTS**

### **CRITICAL FEDERAL COMPLIANCE COMPONENTS**

#### **IDCR & Program Code Validation**
**Priority**: **CRITICAL**
```python
Required Components:
├── IDCRValidationService implementation
├── Enhanced SharePoint ETL for NICRA rate processing
├── M60 integration with FHWA service
├── Program code validation logic
├── SharePoint data freshness validation
├── Workflow trigger stops
└── Comprehensive testing framework
```

**Success Criteria**:
- IDCR validation functional with SharePoint data source
- NICRA rate processing via enhanced SharePoint ETL
- Program code validation against M60 tables
- SharePoint sync status monitoring operational
- Workflow stops on validation failures
- Audit logging for all validations

#### **Signature Hierarchy & RBAC**
**Priority**: **CRITICAL**
```python
Required Components:
├── Enhanced RBAC with signature permissions
├── Signature hierarchy service
├── Azure AD integration middleware
├── Role-based workflow controls
└── Signature audit trail
```

**Success Criteria**:
- Complete signature hierarchy implementation
- Role-based access controls functional
- Azure AD authentication integrated
- Signature sequence validation working

#### **FMIS XML Integration**
**Priority**: **CRITICAL**
```python
Required Components:
├── FMIS XML schema implementation
├── Signature block generation
├── Multi-funded project XML handling
├── Federal submission formatting
└── XML validation and testing
```

**Success Criteria**:
- FMIS 5.0 XML schema compliance
- Signature blocks properly formatted
- Multi-funding scenarios handled
- XML validation passing

### **COMPREHENSIVE VALIDATION COMPONENTS**

#### **Regulatory Compliance Services**
```python
Required Components:
├── CFR200ComplianceService
├── FARPart31ValidationService
├── NEPAComplianceValidator
├── STIPReferenceValidator
└── Comprehensive validation testing
```

#### **Integration & Automation Enhancement**
```python
Required Components:
├── Enhanced ProTrack+ integration
├── Advanced SharePoint ETL optimization
├── DIFS data quality monitoring
├── Automation service enhancements
├── Validation checkpoint coordination
└── Integration testing
```

### **DOCUMENTATION & TESTING COMPONENTS**

#### **Process Documentation**
```python
Required Components:
├── Role & responsibility documentation
├── Validation procedure documentation
├── Integration procedure documentation
├── Governance procedure documentation
└── User training materials
```

#### **Testing & Validation**
```python
Required Components:
├── FHWA sandbox testing
├── End-to-end validation testing
├── Performance testing
├── Implementation planning
└── Training delivery
```

---

## 📊 **COMPLIANCE SCORECARD**

### **Current State Assessment**
| **Compliance Area** | **Current** | **Target** | **Gap** | **Priority** |
|---------------------|-------------|------------|---------|--------------|
| IDCR Validation | 20% | 95% | 75% | **CRITICAL** |
| Program Code Validation | 30% | 95% | 65% | **CRITICAL** |
| Signature Hierarchy | 10% | 95% | 85% | **CRITICAL** |
| FMIS XML Integration | 25% | 95% | 70% | **CRITICAL** |
| Regulatory Compliance | 45% | 90% | 45% | **HIGH** |
| System Integration | 75% | 95% | 20% | **MEDIUM** |
| Automation | 80% | 95% | 15% | **MEDIUM** |
| Documentation | 40% | 90% | 50% | **HIGH** |

### **Target Compliance Levels**
- **Critical Federal Compliance**: 75% overall compliance
- **Comprehensive Validation**: 85% overall compliance
- **Full FAHP Alignment**: 95% overall compliance

---

## 🔗 **RESOURCE MAPPING**

### **A. Regulatory References Integration**
```python
# Required Resource Integration:
├── CFR200_COMPLIANCE_RULES = "2 CFR 200 validation rules"
├── FAR_PART31_PRINCIPLES = "FAR Part 31 cost principles"
├── FHWA_PROGRAM_CODES = "M60 table integration"
├── FHWA_GUIDANCE = "Federal-Aid Programs guide"
└── AASHTO_GUIDELINES = "Cost categorization standards"
```

### **B. System & Technical Resources**
```python
# System Integration Requirements:
├── SHAREPOINT_ETL = "DIFS data sync, NICRA rates, fund availability"
├── FMIS_5_SCHEMA = "XML tag definitions, submission"
├── PROTRACK_PLUS_API = "Project status, milestones"
├── AZURE_AD = "Authentication, role-based permissions"
└── M60_TABLES = "Program codes, federal share rates"
```

### **C. Stakeholder Role Integration**
```python
# Role-Based System Integration:
├── PROJECT_MANAGER = "Initiate PAR, verify scope"
├── RAD = "Resource allocation validation"
├── OCFO_BUDGET_ANALYST = "Program code & budget review"
├── OCFO_FINANCIAL_OFFICER = "Final governance checkpoint"
└── FHWA_DIVISION = "Federal approval/rejection"
```

---

## 🎯 **SUCCESS METRICS**

### **Technical Metrics**
- **IDCR Validation Accuracy**: 99.5%
- **Program Code Validation**: 100% against M60 tables
- **XML Schema Compliance**: 100% FMIS 5.0 compliance
- **Signature Hierarchy**: 100% role-based compliance
- **Integration Uptime**: 99.9% system availability

### **Process Metrics**
- **PAR Processing Time**: <2 hours average
- **Validation Error Rate**: <1% false positives
- **Federal Approval Rate**: >95% first-time approval
- **Audit Compliance**: 100% audit trail completeness
- **User Satisfaction**: >90% stakeholder approval

### **Compliance Metrics**
- **Federal Regulation Compliance**: 95% overall
- **FHWA Policy Alignment**: 95% policy compliance
- **Audit Readiness**: 100% audit trail availability
- **Documentation Completeness**: 90% procedure coverage

---

## 🚨 **CRITICAL SUCCESS FACTORS**

### **1. Federal Stakeholder Engagement**
- **FHWA Division Coordination**: Regular alignment meetings
- **Sandbox Testing**: Comprehensive end-to-end validation
- **Policy Clarification**: Ongoing guidance interpretation
- **Approval Process**: Clear federal approval criteria

### **2. Technical Implementation**
- **Incremental Delivery**: Phased implementation approach
- **Comprehensive Testing**: Multi-level validation testing
- **Integration Stability**: Robust system integration
- **Performance Optimization**: Efficient validation processing

### **3. Process Alignment**
- **Role Clarity**: Clear stakeholder responsibilities
- **Procedure Documentation**: Comprehensive process documentation
- **Training Delivery**: Effective user training programs
- **Change Management**: Smooth transition procedures

---

## 🔄 **CONTINUOUS IMPROVEMENT**

### **Monitoring & Feedback**
- **Weekly FHWA alignment reviews**
- **Monthly compliance assessments**
- **Quarterly stakeholder feedback sessions**
- **Annual federal policy updates**

### **Adaptation Strategy**
- **Policy change responsiveness**
- **Federal guidance integration**
- **Stakeholder feedback incorporation**
- **Continuous compliance enhancement**

---

## 📞 **IMPLEMENTATION SUPPORT**

### **For Questions About**:
- **Federal Requirements**: Reference this FAHP alignment plan
- **Technical Implementation**: Reference compliance assessment report
- **Security Requirements**: Reference python-security-requirements.md
- **Functional Requirements**: Reference functional-requirements.md

### **For Implementation Planning**:
- **Use the 3-phase roadmap** for sprint planning
- **Follow the compliance scorecard** for progress tracking
- **Reference the resource mapping** for integration requirements
- **Use success metrics** for validation criteria

---

## 🎉 **CONCLUSION**

This FAHP/FHWA alignment plan provides a comprehensive roadmap to achieve full federal compliance while leveraging EDS's sophisticated technical foundation. The plan addresses all critical federal requirements through a structured, phased approach that ensures stakeholder alignment and regulatory compliance.

**Key Message**: EDS has the technical sophistication to exceed federal requirements. Our focus is on aligning processes, validations, and integrations with FAHP policies to ensure seamless federal approval and long-term compliance success.

**Ready to achieve full FAHP alignment! 🚀**

---

*This plan represents comprehensive analysis of federal requirements and provides a clear path to full FAHP/FHWA compliance for the EDS system.*
