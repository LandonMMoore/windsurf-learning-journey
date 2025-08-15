# EDS Functional Requirements

## 1. Core System Functionality

### 1.1 ePAR (Electronic Program Action Request) Module
**Primary Function**: Electronic processing of Program Action Requests through a 6-stage workflow

#### Key Features:
- **4-Phase Workflow**: Internal EDS → ProTrack+ → FMIS → Finalization
- **Funding Type Support**: Both Federal and Local funding types
- **Integration Points**: ProTrack+, FMIS, DIFS via automated workflows
- **Validation Engine**: Automated validation at each stage
- **Audit Trail**: Complete history tracking for all changes
- **Automation Opportunities**: Signature collection, FMIS monitoring, DIFS integration

#### Workflow Types:
1. **Capital Project Budget Reallocation** (Federal/Local)
2. **Federal Project End Date Extensions**
3. **Obligation Requests** (Construction/Design)
4. **Local Capital Allocations**

#### Corrected Status Flow (Based on Stakeholder Feedback):
```
Phase 1 - Internal EDS:
PAR Creation → Engineering Review → Budget Analysis → Leadership Sign-off

Phase 2 - ProTrack+:
ProTrack+ Submission → PM Confirmation → RAD Review → OCFO Review

Phase 3 - Federal (FMIS):
FMIS Submission → State Signatures (3) → FHWA Approval → DIFS Update

Phase 4 - Finalization:
System Updates → Notifications → Archive
```

### 1.2 Budget Calculation Engine
**Purpose**: Handle complex funding calculations for federally funded projects

#### Features:
- **Rate Selection**: Support for 4 funding rate options
  - 100% (All FED Funds – NO MATCH)
  - 90/10 (F.A./D.C.)
  - 83.15/16.85 (F.A./D.C.)
  - 80/20 (Standard) (F.A./D.C.)
- **Program Code Management**: Integration with FMIS program codes
- **Automatic Calculations**: Real-time budget distribution calculations
- **Validation**: Cross-validation against available funding
- **Export Capability**: Excel export for budget summaries

### 1.3 Reporting & Analytics Module

#### 1.3.1 EDS Assistant (AI-Powered Query Interface)
- **Natural Language Processing**: Process financial queries in plain English
- **RAG-Based Responses**: Retrieve and generate contextual answers
- **Data Source Integration**: Query across multiple data sources
- **Citation Support**: Provide source references for responses

#### 1.3.2 Dynamic Dashboard System
- **Drag-and-Drop Interface**: ClickUp-style dashboard builder
- **Widget Types**: KPI Cards, Charts (Line, Bar, Pie, Area), Tables, Timelines
- **Real-time Data**: Live data refresh capabilities
- **Cross-widget Filtering**: Interactive filtering across dashboard components
- **Template Library**: Pre-configured dashboard templates
- **Export Functions**: PDF/Excel export capabilities

#### 1.3.3 AI Report Generator
- **5-Phase Process**: Structured report generation workflow
- **Template Support**: Multiple report templates
- **Formula Fields**: Support for calculated fields and formulas
- **Automated Insights**: AI-driven analysis and recommendations

### 1.4 Data Management System

#### Database Structure:
```
Master Projects → Projects → Tasks/Subtasks → Transactions
```

#### Key Features:
- **Hierarchical Data Model**: Multi-level project organization
- **Comprehensive Audit Logging**: All changes tracked with timestamps
- **7-Year Data Retention**: Compliance with federal requirements
- **Version History**: Complete change tracking for all records
- **Data Validation**: Multi-level validation controls

## 2. Integration Requirements

### 2.1 ProTrack+ Integration
**Status**: 70% Complete (API Working, Workflow Confirmed)

#### Integration Points:
1. **ePAR Field Integration**: Mandatory ePAR field for PAR-related requests
2. **Data Synchronization**: Pull ePAR information using project identifiers
3. **Bidirectional Updates**: Push Packet Tracker numbers back to EDS
4. **Status Monitoring**: Real-time status updates from ProTrack+ workflow
5. **Workflow Independence**: ProTrack+ handles PM, RAD, OCFO reviews independently

#### Confirmed Workflow Steps in ProTrack+:
- PM Confirmation of PAR details
- RAD Review (purpose alignment with DDOT goals)
- OCFO Review (compliance validation)
- Automatic progression to FHWA status (triggers EDS FMIS process)

### 2.2 FMIS Integration
**Status**: 25% Complete (Major Automation Opportunities Identified)

#### Current Manual Process (To Be Automated):
- **Manual Data Entry**: Budget analysts manually type all PAR data into FMIS
- **Manual Signature Collection**: Email-based signature requests and tracking
- **Manual Status Monitoring**: No automatic notifications from FHWA approval

#### EDS Automation Requirements:
- **XML Generation**: Automated FMIS XML creation from PAR data
- **Pre-populated Forms**: Eliminate manual data entry
- **Automated Signature Workflow**: Email triggers and status tracking
- **FMIS Status Monitoring**: Automated polling for federal approval status

#### Required State Signatures (3 Total):
1. **First Signature**: Calvin & Kathryn (OCFO)
2. **Second Signature**: Environmental Officer (TBD)
3. **Third Signature**: Chief Engineer (TBD)

#### Federal Process:
- **FHWA Signatures**: 3 additional signatures (total 6)
- **No Automatic Notifications**: EDS must monitor FMIS for completion

### 2.3 DIFS Integration
**Status**: In Progress (SharePoint ETL + Critical Manual Gap Identified)

#### Current ETL Pipeline:
- **Scheduled SharePoint Data Dumps**: Real-time integration not feasible
- **ETL Pipeline**: Azure Functions-based processing
- **NICRA Rate Processing**: Enhanced ETL for federal compliance
- **Data Quality Monitoring**: Validation and freshness checks

#### Critical Manual Process Identified:
- **Post-Approval Updates**: "If the budget analyst does not put it in DIFS, it doesn't go in DIFS period"
- **Manual Data Entry**: Budget analysts must manually type all PAR data into DIFS
- **Exception**: GIS data not included in DIFS
- **Automation Opportunity**: API integration with DIFS team for automated updates

#### Data Sources:
- R-series reports (R025, R051, R071, R085, R100, R238)
- EDS Extract files
- Master data tables (CoA, Projects, etc.)
- NICRA rates for IDCR validation

## 3. User Roles and Permissions

### 3.1 Primary Roles

#### Project Manager (PM)
- Create, view, and update PARs
- Submit PARs to ProTrack+
- Monitor PAR status
- Update ProTrack+ information

#### Financial Officer (FO)
- View and update PARs
- Validate submissions
- Edit 'Federal Budget Allocations Page'
- Perform RAD and OCFO reviews
- Submit to FHWA/FMIS
- Finalize approvals

#### Budget Analyst
- Select funding sources (Federal/Local)
- Set funding rates for federally funded projects
- Calculate program code distributions
- Manage FMIS program codes
- Validate budget calculations

### 3.2 External System Roles

#### ProTrack+
- Store project information
- Track project status
- Process project updates
- Serve as system of record for project approval stages

#### FHWA (Federal Highway Administration)
- Review and approve submitted PARs

#### FMIS (Financial Management Information System)
- Process approved PARs for funding
- Store program codes and funding data
- Generate FMIS 60 report (available funds by program code)
- Generate FMIS 37 report (for validation)

#### DIFS (Financial information system for DC funds)
- Source of DC contribution data
- Process DC matching funds

## 4. Performance Requirements

### 4.1 System Performance
- **Response Time**: < 3 seconds for standard operations
- **Concurrent Users**: Support for 100+ concurrent users
- **Data Processing**: Handle large Excel files (10MB+)
- **Report Generation**: < 30 seconds for complex reports
- **Dashboard Refresh**: Real-time updates within 5 seconds

### 4.2 Availability Requirements
- **Uptime**: 99.5% availability during business hours
- **Maintenance Windows**: Scheduled during off-hours
- **Disaster Recovery**: < 4 hour RTO, < 1 hour RPO

## 5. Data Requirements

### 5.1 Data Volume
- **Projects**: 10,000+ active projects
- **Transactions**: 1M+ financial transactions
- **Users**: 500+ system users
- **Reports**: 1,000+ generated reports per month

### 5.2 Data Quality
- **Validation Rules**: Multi-level data validation
- **Error Handling**: Comprehensive error reporting
- **Data Integrity**: Referential integrity enforcement
- **Audit Trail**: Complete change history

## 6. Compliance Requirements

### 6.1 Federal Compliance
- **FISMA**: Federal Information Security Management Act
- **NIST 800-53**: Security control implementation
- **FedRAMP**: Federal Risk and Authorization Management Program
- **Section 508**: Accessibility compliance

### 6.2 Data Retention
- **Financial Records**: 7-year retention requirement
- **Audit Logs**: 7-year retention requirement
- **System Logs**: 1-year retention requirement

---
*Document Version: 1.0*  
*Last Updated: August 14, 2025*  
*Next Review: September 14, 2025*
