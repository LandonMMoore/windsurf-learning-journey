# EDS COMPREHENSIVE REQUIREMENTS & USER STORIES
*Generalized Version - Contextual Comments for Requirements Understanding*

*Consolidated Document - All Functional Requirements and User Stories*  
*Date: August 15, 2025*  
*Version: 2.0 - Generalized for Implementation Teams*

---

## 🎯 **EXECUTIVE SUMMARY**

This comprehensive document consolidates all EDS functional requirements and user stories based on stakeholder feedback, corrected PAR workflow understanding, and automation opportunities identified. The system architecture uses Python 3.13+, FastAPI, multi-database integration, and AI/ML capabilities.

**Key Corrections from Stakeholder Feedback:**
- PM/Engineer roles are interchangeable under RAD team
- Major manual processes identified requiring automation
- Corrected FMIS process sequence and signature collection
- 6-phase workflow: Internal EDS → ProTrack+ Submission → ProTrack+ Processing → EDS Trigger → FMIS (Conditional) → Finalization

---

## 📋 **CORRECTED PAR WORKFLOW**

### **Phase 1: Internal EDS (Steps 1-3)**
```
PAR Creation → RAD Team Review → Budget Analysis → Leadership Sign-off
(Note: PM/Engineer roles are interchangeable under RAD team)
```

### **Phase 2: EDS → ProTrack+ Submission (Step 4)**
```
EDS Auto-Submit to ProTrack+ → ProTrack+ Processing
```

### **Phase 3: ProTrack+ Internal Workflow (Steps 5-7)**
```
PM/Engineer Confirmation → RAD Review → OCFO Review
```

### **Phase 4: ProTrack+ → EDS Trigger (Step 8)**
```
ProTrack+ Completion → EDS Notification → Federal Funding Check
```

### **Phase 5: Federal FMIS (Steps 9-12) - CONDITIONAL**
```
[IF FEDERAL FUNDING] FMIS Submission → State Signatures (3) → FHWA Approval → DIFS Update
[IF LOCAL ONLY] Skip to Finalization
```

### **Phase 6: Finalization**
```
System Updates → Notifications → Archive
```

---

## 🚨 **CRITICAL AUTOMATION OPPORTUNITIES**

### **1. ProTrack+ Submission Automation**
- **Current State**: Manual submission from EDS to ProTrack+ after internal approval
- **Solution**: Automated API submission to ProTrack+ with status tracking

### **2. FMIS Integration Automation (Federal Projects Only)**
- **Current State**: Manual data entry from PAR to FMIS system creates inefficiency and error risk
- **Solution**: XML generation, automated data entry, status monitoring
- **Trigger Condition**: Only activated when ProTrack+ completion AND federal funding detected

### **3. Signature Collection Automation**
- **Business Need**: Automated signature workflow requested to eliminate manual email management
- **Current State**: Manual email creation and tracking for 6 signatures creates bottlenecks
- **Solution**: Automated email workflow with status tracking

### **4. FMIS Status Monitoring**
- **Current State**: Manual checking of FMIS system for completion status without notifications
- **Business Gap**: No automated notification system for federal approval completion
- **Solution**: Automated FMIS polling and notifications

### **5. DIFS Integration**
- **Current State**: Manual data entry dependency - no automation means no DIFS updates
- **Manual Process**: Complete re-typing of PAR information into DIFS system
- **Solution**: API integration for automated updates

---

## 👥 **USER PERSONAS**

### **Primary Users**
- **Project Manager/Engineer (RAD Team)**: Interchangeable roles - creates and manages PARs
- **Financial Officer (FO)**: Reviews financial data, approves budgets, validates compliance
- **Budget Analyst (BA)**: Analyzes budget data, creates reports, manages funding
- **FHWA Reviewer**: Reviews federal submissions, ensures compliance
- **System Administrator**: Manages system configuration, monitors performance

### **Secondary Users**
- **DDOT Leadership**: Executive oversight and strategic planning
- **OCFO Staff**: Financial compliance and audit support
- **External Auditors**: Compliance verification and audit trails

---

## 📋 **EPIC 1: PAR MANAGEMENT AND WORKFLOW**

### **Story 1.1: PAR Creation and Initial Setup**
**As a** Project Manager/Engineer (RAD Team)  
**I want to** create a new PAR for an existing project  
**So that** I can initiate the budget reallocation or project modification process

**Context**: PM and Engineer roles are functionally equivalent in DDOT organizational structure - both operate under RAD team umbrella

**Acceptance Criteria:**
- Select project from DIFS-synced project list
- Choose PAR type (Federal, Local Capital)
- Auto-populate project details from DIFS cache
- Save PAR in draft status
- Validate required fields before submission

**Technical Implementation:**
- **API Endpoint**: `POST /api/v1/par/create`
- **Database**: PAR model with project relationships
- **Validation**: Pydantic schemas for data validation
- **Integration**: DIFS ETL pipeline for project data

### **Story 1.2: PAR Review and Validation**
**As a** Project Manager/Engineer (RAD Team)  
**I want to** review and validate PAR details before submission  
**So that** I can ensure all project information is accurate before routing to Finance

**Acceptance Criteria:**
- Review all PAR details and project scope
- Validate project alignment with DDOT objectives
- Make any necessary corrections or updates
- Submit to Finance/Budget Analysis when ready
- Maintain audit trail of all changes

**Technical Implementation:**
- **API Endpoint**: `PUT /api/v1/par/{id}/review`
- **Workflow**: Internal RAD team review before Finance routing
- **Database**: Review status and change tracking
- **Integration**: Route to budget analysis after RAD approval

---

## 🚀 **EPIC 2: AUTOMATION OPPORTUNITIES (CRITICAL)**

### **Story 2.1: Automated ProTrack+ Submission**
**As a** Budget Analyst  
**I want** EDS to automatically submit approved PARs to ProTrack+  
**So that** I don't have to manually transfer PAR data to ProTrack+

**Context**: Current process requires manual submission from EDS to ProTrack+ after internal approval, creating workflow delays

**Acceptance Criteria:**
- Automatically submit PAR data to ProTrack+ after EDS internal approval
- Map EDS PAR fields to ProTrack+ required fields
- Provide submission confirmation and tracking
- Handle submission errors gracefully with retry logic
- Maintain audit trail of all ProTrack+ submissions

**Technical Implementation:**
- **API Endpoint**: `POST /api/v1/par/{id}/protrack-submit`
- **Service**: ProTrackIntegrationService with field mapping
- **Integration**: ProTrack+ API for automated submission
- **Database**: Submission status and tracking

### **Story 2.2: ProTrack+ Completion Trigger**
**As a** System Administrator  
**I want** EDS to be notified when ProTrack+ processing is complete  
**So that** EDS can automatically proceed to FMIS steps for federal projects

**Context**: System needs to detect ProTrack+ completion and conditionally trigger FMIS workflow based on funding type

**Acceptance Criteria:**
- Receive webhook notifications from ProTrack+ on completion
- Check PAR funding type (Federal vs Local)
- Automatically trigger FMIS workflow for federal projects
- Skip FMIS and proceed to finalization for local-only projects
- Log all workflow transitions

**Technical Implementation:**
- **API Endpoint**: `POST /api/v1/webhooks/protrack-completion`
- **Service**: WorkflowTriggerService with funding type logic
- **Integration**: ProTrack+ webhook integration
- **Conditional Logic**: Federal funding detection and routing

### **Story 2.3: Automated FMIS Data Entry (Federal Projects Only)**
**As a** Budget Analyst  
**I want** EDS to automatically generate and submit PAR data to FMIS  
**So that** I don't have to manually type all information into FMIS

**Context**: Current process requires complete manual data transcription from PAR to FMIS, creating inefficiency and error potential
**Trigger Condition**: Only activated after ProTrack+ completion AND federal funding detected

**Acceptance Criteria:**
- Generate FMIS XML from PAR data automatically
- Pre-populate FMIS submission forms
- Validate XML against FMIS 5.0 schema
- Submit data electronically to FMIS
- Provide confirmation of successful submission
- Skip entirely for local-only funding projects

**Technical Implementation:**
- **API Endpoint**: `POST /api/v1/par/{id}/fmis-submit`
- **Service**: FMISIntegrationService with XML generation
- **Validation**: FMIS 5.0 XML schema validation
- **Integration**: FMIS API for automated submission
- **Conditional Logic**: Federal funding requirement check

### **Story 2.4: Automated Signature Collection Workflow**
**As a** Budget Analyst  
**I want** EDS to automatically trigger signature request emails  
**So that** I don't have to manually create and track signature emails

**Context**: Business requirement for automated signature workflow to eliminate manual email management overhead

**Acceptance Criteria:**
- Automatically generate signature request emails
- Route signatures sequentially (3 state signatures)
- Track signature completion status in real-time
- Send reminder emails for pending signatures
- Notify when all signatures are completed

**Technical Implementation:**
- **API Endpoint**: `POST /api/v1/par/{id}/signature-workflow`
- **Service**: SignatureWorkflowService with email automation
- **Integration**: Email service (SMTP/Exchange) with templates
- **Database**: Signature status tracking and audit trail

### **Story 2.5: Automated FMIS Status Monitoring**
**As a** Budget Analyst  
**I want** EDS to automatically monitor FMIS for federal approval status  
**So that** I don't have to manually check FMIS for completion

**Context**: Current process requires manual FMIS system checking without automated completion notifications
**Business Gap**: No notification system exists for federal approval completion status

**Acceptance Criteria:**
- Poll FMIS system for PAR approval status
- Automatically detect federal approval completion
- Send notification emails when approval is received
- Update PAR status in EDS dashboard
- Log all status changes with timestamps

**Technical Implementation:**
- **API Endpoint**: `GET /api/v1/par/{id}/fmis-status`
- **Service**: FMISMonitoringService with polling mechanism
- **Integration**: FMIS API for status queries
- **Notifications**: Email service for approval notifications

### **Story 2.4: Automated DIFS Integration**
**As a** Budget Analyst  
**I want** EDS to automatically update DIFS with approved PAR data  
**So that** I don't have to manually type PAR information into DIFS

**Context**: Current dependency on manual data entry - without analyst input, DIFS updates don't occur
**Manual Reality**: Complete re-transcription of PAR data into DIFS system required

**Acceptance Criteria:**
- Automatically submit PAR data to DIFS post-FHWA approval
- Eliminate manual data entry into DIFS
- Handle data validation and error recovery
- Provide confirmation of successful DIFS update
- Maintain audit trail of all DIFS updates

**Technical Implementation:**
- **API Endpoint**: `POST /api/v1/par/{id}/difs-update`
- **Service**: DIFSIntegrationService with API connectivity
- **Integration**: DIFS team API for automated updates
- **Exception**: GIS data excluded (as confirmed by stakeholders)

---

## 🤖 **EPIC 3: AI ASSISTANT & INTELLIGENT QUERY PROCESSING**

### **Story 3.1: Chat with EDS Assistant**
**As a** Budget Analyst  
**I want to** ask natural language questions about financial data  
**So that** I can get quick insights without complex queries

**Acceptance Criteria:**
- Submit natural language queries
- System processes queries using RAG (Retrieval-Augmented Generation)
- AI provides contextual responses with data citations
- System maintains chat history for reference
- Receive streaming responses for better UX

**Technical Implementation:**
- **API Endpoint**: `POST /api/ai-assistant/v3`
- **Agent**: query_process_v3 (unstructured_agent.py)
- **Models**: OpenAI GPT-4, Anthropic Claude
- **Storage**: MongoDB chat history

---

## 📊 **EPIC 4: DYNAMIC DASHBOARD SYSTEM**

### **Story 4.1: Create Custom Dashboard**
**As a** Financial Officer  
**I want to** create custom dashboards  
**So that** I can visualize key financial metrics

**Acceptance Criteria:**
- Create new dashboard with custom name and description
- Associate dashboard with user account
- Set dashboard visibility (private/shared)
- Support multiple widget types
- Validate dashboard configuration

**Technical Implementation:**
- **API Endpoint**: `POST /api/dashboards`
- **Model**: Dashboard (dashboard_model.py)
- **Schema**: DashboardCreate
- **Service**: DashboardService.add()

---

## 📈 **EPIC 5: ADVANCED REPORT GENERATION**

### **Story 5.1: AI-Powered Report Generation**
**As a** Budget Analyst  
**I want to** generate reports using AI assistance  
**So that** I can create comprehensive analysis documents efficiently

**Acceptance Criteria:**
- Describe report requirements in natural language
- AI agent guides through 5-phase report creation process
- System suggests appropriate data sources and fields
- AI generates calculation methods and formulas
- Report includes automated insights and analysis

**Technical Implementation:**
- **API Endpoint**: `POST /api/report/chat`
- **Agent**: ReportGenerationManagerAgent
- **Models**: GPT-4 with specialized tools
- **Phases**: Requirements → Fields → Calculations → Generation → Review

---

## 🔄 **EPIC 6: WORKFLOW AND DATA MANAGEMENT**

### **Story 6.1: Workflow Data Access**
**As a** Project Manager  
**I want to** access workflow and project data  
**So that** I can track project progress and status

**Acceptance Criteria:**
- Search and filter workflow records
- Hierarchical data access (Master Projects → Projects → Tasks → Transactions)
- Get unique values for filtering options
- Include comprehensive project details
- Support pagination for large datasets

**Technical Implementation:**
- **API Endpoint**: `GET /api/workflows`
- **Repository**: WorkflowRepository with multiple master tables
- **Models**: WorkflowMaster* (funds, programs, cost centers, etc.)

---

## 🔐 **EPIC 7: SECURITY AND AUDIT**

### **Story 7.1: User Authentication and Session Management**
**As a** System User  
**I want to** securely authenticate and maintain my session  
**So that** I can access the system safely

**Acceptance Criteria:**
- Authenticate using secure protocols
- Maintain session securely across requests
- Track activity for audit purposes
- Access features based on role permissions
- Session expires after inactivity

**Technical Implementation:**
- **Middleware**: AuthMiddleware with dependency injection
- **Service**: get_current_user dependency
- **Security**: JWT tokens, session management

---

## 🔗 **EPIC 8: INTEGRATION AND DATA SYNCHRONIZATION**

### **Story 8.1: SharePoint Data Integration**
**As a** System Administrator  
**I want to** synchronize data with SharePoint  
**So that** the system has current financial information

**Acceptance Criteria:**
- Receive webhook notifications from SharePoint
- Run data synchronization on scheduled intervals
- Handle sync failures gracefully
- Validate data quality after synchronization

**Technical Implementation:**
- **API Endpoint**: `/api/integrations/webhook`
- **Service**: SharePoint ETL pipeline
- **Models**: Integration tracking and status

---

## 🎯 **SYSTEM REQUIREMENTS**

### **Core System Functionality**

#### **1.1 ePAR Module**
- **4-Phase Workflow**: Internal EDS → ProTrack+ → FMIS → Finalization
- **Funding Type Support**: Both Federal and Local funding types
- **Integration Points**: ProTrack+, FMIS, DIFS via automated workflows
- **Validation Engine**: Automated validation at each stage
- **Audit Trail**: Complete history tracking for all changes

#### **1.2 Budget Calculation Engine**
- **Rate Selection**: Support for 4 funding rate options (100%, 90/10, 83.15/16.85, 80/20)
- **Program Code Management**: Integration with FMIS program codes
- **Automatic Calculations**: Real-time budget distribution calculations
- **Validation**: Cross-validation against available funding

#### **1.3 Reporting & Analytics Module**
- **EDS Assistant**: AI-powered query interface with RAG
- **Dynamic Dashboard**: Drag-and-drop interface with real-time data
- **AI Report Generator**: 5-phase structured report generation

### **Integration Requirements**

#### **2.1 ProTrack+ Integration (70% Complete)**
- ePAR field integration with mandatory fields
- Bidirectional data synchronization
- Real-time status monitoring
- Workflow independence for PM, RAD, OCFO reviews

#### **2.2 FMIS Integration (25% Complete - Major Automation Needed)**
- **Current Manual Process**: Budget analysts manually type all PAR data
- **Required Automation**: XML generation, pre-populated forms, signature workflow
- **State Signatures**: 3 required (Calvin & Kathryn, Environmental Officer, Chief Engineer)
- **Federal Process**: 3 additional FHWA signatures

#### **2.3 DIFS Integration (In Progress - Critical Manual Gap)**
- **Current ETL Pipeline**: SharePoint data dumps with Azure Functions
- **Critical Gap**: Manual post-approval data entry required
- **Automation Opportunity**: API integration for automated PAR updates

### **Performance Requirements**
- **Response Time**: < 3 seconds for standard operations
- **Concurrent Users**: Support for 100+ concurrent users
- **Uptime**: 99.5% availability during business hours
- **Dashboard Updates**: Real-time updates within 5 seconds

### **Compliance Requirements**
- **FISMA**: Federal Information Security Management Act
- **NIST 800-53**: Security control implementation
- **FedRAMP**: Federal Risk and Authorization Management Program
- **Section 508**: Accessibility compliance
- **Data Retention**: 7-year retention for financial records

---

## 🚀 **IMPLEMENTATION PRIORITIES**

### **Phase 1: Critical Automation**
1. FMIS XML generation and automated data entry
2. Signature workflow automation with email triggers
3. FMIS status monitoring and notifications
4. RAD team workflow optimization

### **Phase 2: Integration Enhancement**
1. DIFS API integration for automated updates
2. Enhanced ProTrack+ bidirectional sync
3. Real-time dashboard improvements
4. Advanced audit logging

### **Phase 3: Advanced Features**
1. AI-powered report generation enhancements
2. Mobile responsiveness optimization
3. Performance tuning and scaling
4. Advanced analytics capabilities

