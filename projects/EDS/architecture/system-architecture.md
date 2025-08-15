# EDS System Architecture

## 1. Architecture Overview

### 1.1 High-Level Architecture
The EDS system follows a multi-tier architecture pattern with clear separation of concerns, designed for scalability, security, and federal compliance.

```
External Systems Layer
├── ProTrack+ (API)
├── FMIS (XML)
├── DIFS (SharePoint)
└── FHWA (Submit)

Integration Layer
├── ProTrack+ Connector
├── FMIS Connector
├── DIFS Connector
└── External API Gateway

Application Layer
├── ePAR Module
├── Reporting Engine
├── Dashboard Builder
└── AI Assistant (RAG)

Business Logic Layer
├── Workflow Engine
├── Budget Calculator
├── User Management
└── Security Services

Data Access Layer
├── Entity Framework
├── Audit Logger
├── Cache Manager
└── Search Engine

Data Layer
├── SQL Server (Primary)
├── Redis (Cache)
├── Elasticsearch (Search)
└── File Storage (Azure)
```

### 1.2 Technology Stack

#### Frontend Tier
- **Framework**: React.js with TypeScript
- **State Management**: Redux Toolkit
- **UI Components**: Material-UI / Custom component library
- **Build Tools**: Webpack, Vite
- **Testing**: Jest, React Testing Library

#### Application Tier
- **Runtime**: .NET Core 6.0+
- **Framework**: ASP.NET Core Web API
- **Authentication**: Azure AD / OAuth 2.0
- **Authorization**: Policy-based authorization
- **API Documentation**: Swagger/OpenAPI

#### Data Tier
- **Primary Database**: SQL Server 2022
- **Caching**: Redis
- **Search Engine**: Elasticsearch
- **File Storage**: Azure Blob Storage
- **Message Queue**: Azure Service Bus

#### Infrastructure
- **Cloud Platform**: Microsoft Azure
- **Container Platform**: Docker (optional)
- **Load Balancer**: Azure Load Balancer
- **CDN**: Azure CDN
- **Monitoring**: Azure Monitor, Application Insights

## 2. Core Components

### 2.1 ePAR Module Architecture

The ePAR module handles the complete lifecycle of Program Action Requests:

#### Workflow States
1. **Draft/Unsubmitted** → Initial PAR creation
2. **Submitted** → PAR submitted for processing
3. **In Progress** → Active development/editing
4. **Pending OCFO Budget Validation** → Federal funding validation
5. **Ready for Review** → Completed and ready for external review
6. **Submitted to ProTrack+** → External system processing
7. **ProTrack+ Approved** → External approval received
8. **Pending RAD Review** → Internal financial review
9. **RAD Approved** → RAD team approval
10. **Pending OCFO Review** → OCFO team review
11. **OCFO Approved** → Final internal approval
12. **Submitted to FHWA** → Federal submission
13. **FHWA Approved** → Federal approval
14. **Completed** → Final state

#### Key Components
- **Workflow Engine**: 6-stage process management
- **Budget Calculator**: Rate selection and program code management
- **Validation Engine**: Business rules and data integrity
- **Integration Manager**: ProTrack+ sync and FMIS submission

### 2.2 Reporting & Analytics Architecture

#### EDS Assistant (AI-Powered Query Interface)
- **RAG Pipeline**: Retrieval-augmented generation
- **NLP Query Processing**: Natural language understanding
- **Knowledge Base**: Indexed financial documents and data
- **Citation Support**: Source reference tracking

#### Dashboard Builder
- **Drag & Drop UI**: ClickUp-style interface
- **Widget Library**: Pre-configured components
- **Real-time Data**: Live data refresh
- **Export Functions**: PDF/Excel capabilities

#### Report Generator
- **AI-Driven Reports**: Automated report creation
- **Template Engine**: Multiple report formats
- **Formula Support**: Calculated fields
- **Data Pipeline**: ETL processes

### 2.3 Integration Architecture

#### ProTrack+ Integration
- **Protocol**: REST API
- **Authentication**: Mutual TLS
- **Data Exchange**: JSON format
- **Features**: Bidirectional sync, webhook support

#### FMIS Integration
- **Protocol**: XML/SOAP
- **Authentication**: PKI certificates
- **Security**: Digital signatures
- **Processing**: Batch operations

#### DIFS Integration
- **Platform**: SharePoint
- **Authentication**: Azure AD
- **Method**: ETL pipeline
- **Schedule**: Automated sync

## 3. Data Architecture

### 3.1 Database Schema Overview

```sql
-- Core Project Hierarchy
Master_Projects (1) → (M) Projects (1) → (M) Tasks (1) → (M) Subtasks
                                │
                                └→ (M) Financial_Transactions

-- PAR Processing
PAR (1) → (M) PAR_Details
    │
    ├→ (M) PAR_Approvals
    ├→ (M) PAR_Comments
    ├→ (M) PAR_Attachments
    └→ (M) PAR_Audit_Log

-- Financial Data
Budget_Info (1) → (M) Budget_Line_Items
Financial_Balances (1) → (M) Balance_History
Program_Codes (1) → (M) Funding_Allocations
```

### 3.2 Key Database Tables

#### Core Tables
- **projects**: Project master data with financial tracking
- **master_projects**: Project grouping and hierarchy
- **work_breakdown_structure**: Task and subtask organization
- **financial_balances**: Current financial positions
- **budget_info**: Budget planning and allocations

#### PAR Processing Tables
- **par**: Main PAR records with status tracking
- **par_detail**: Detailed PAR information and calculations
- **par_approvals**: Approval workflow tracking
- **par_audit_log**: Complete change history

#### Integration Tables
- **integration_log**: External system communication log
- **sync_status**: Data synchronization tracking
- **error_log**: Integration error tracking

## 4. Security Architecture

### 4.1 Security Layers

#### Network Security
- Firewall protection with next-gen IPS
- VPN access for remote users
- Network segmentation by security zones
- DDoS protection and monitoring

#### Application Security
- Web Application Firewall (WAF)
- Input validation and output encoding
- CSRF protection and secure headers
- Session management and timeout controls

#### Data Security
- Transparent Data Encryption (TDE)
- Column-level encryption for sensitive fields
- Azure Key Vault for key management
- Encrypted backups and secure disposal

#### Identity Management
- Azure AD integration with SSO
- Multi-factor authentication (MFA)
- Role-based access control (RBAC)
- Conditional access policies

### 4.2 Authentication Flow

```
User Browser → Azure AD → EDS App → External Systems
     │            │         │           │
     ▼            ▼         ▼           ▼
1. Login    2. MFA     3. JWT Token  4. Service
   Request     Challenge   Validation    Account
                                        Auth
```

## 5. Performance Architecture

### 5.1 Scalability Design

#### Load Balancing
- Azure Load Balancer for traffic distribution
- Auto-scaling based on CPU and memory usage
- Health checks and failover mechanisms
- Geographic load distribution

#### Caching Strategy
1. **Browser Cache**: Static assets (CSS, JS, images)
2. **CDN Cache**: Global content distribution
3. **Application Cache**: Frequently accessed data
4. **Database Cache**: Query result caching
5. **Redis Cache**: Session and temporary data

#### Database Performance
- SQL Server Always On availability groups
- Read replicas for reporting queries
- Index optimization and query tuning
- Partitioning for large tables

### 5.2 Performance Targets

- **Response Time**: < 3 seconds for 95% of requests
- **Throughput**: 1000+ concurrent users
- **Availability**: 99.5% uptime SLA
- **Database Performance**: < 100ms query response
- **Integration Performance**: < 5 seconds for external calls

## 6. Deployment Architecture

### 6.1 Environment Strategy

#### Development Environment
- Local development with mock APIs
- Unit testing and code quality checks
- Sample data for development
- Security scanning integration

#### Staging Environment
- Integration testing environment
- User acceptance testing (UAT)
- Performance and security testing
- Production-like configuration

#### Production Environment
- Live system with real data
- Full security implementation
- Monitoring and alerting
- Backup and disaster recovery

### 6.2 CI/CD Pipeline

#### Build Process
- Code compilation and packaging
- Security scanning (SAST/DAST)
- Quality gates and code coverage
- Artifact creation and signing

#### Test Suite
- Unit tests with high coverage
- Integration tests for APIs
- Security tests for vulnerabilities
- Performance tests for scalability

#### Deployment Process
- Blue/green deployment strategy
- Health checks and validation
- Rollback capabilities
- Configuration management

## 7. Monitoring and Observability

### 7.1 Monitoring Stack

#### Application Monitoring
- Azure Application Insights
- Real-time performance metrics
- Error tracking and alerting
- User experience monitoring

#### Infrastructure Monitoring
- Azure Monitor for infrastructure
- Resource utilization tracking
- Network performance monitoring
- Security event monitoring

#### Business Monitoring
- PAR processing metrics
- Integration success rates
- User activity analytics
- Financial data accuracy

### 7.2 Alerting Strategy

#### Critical Alerts
- System downtime or failures
- Security incidents or breaches
- Data integrity issues
- Integration failures

#### Warning Alerts
- Performance degradation
- High resource utilization
- Failed authentication attempts
- Unusual user activity

## 8. Disaster Recovery and Business Continuity

### 8.1 Backup Strategy

#### Data Backup
- Full backups weekly
- Incremental backups daily
- Transaction log backups every 15 minutes
- Geographic backup distribution

#### Recovery Objectives
- **RTO (Recovery Time Objective)**: < 4 hours
- **RPO (Recovery Point Objective)**: < 1 hour
- **Data Integrity**: 100% consistency
- **Testing**: Monthly recovery testing

### 8.2 High Availability

#### Database High Availability
- SQL Server Always On availability groups
- Automatic failover capabilities
- Read-only replicas for reporting
- Cross-region replication

#### Application High Availability
- Multiple application instances
- Load balancer health checks
- Auto-scaling capabilities
- Session state management

## 9. Integration Patterns

### 9.1 API Design Patterns

#### RESTful APIs
- Resource-based URL structure
- HTTP methods for operations
- JSON data format
- Stateless communication

#### Error Handling
- Consistent error response format
- HTTP status codes
- Error logging and tracking
- User-friendly error messages

#### Versioning Strategy
- URL-based versioning
- Backward compatibility
- Deprecation policies
- Migration support

### 9.2 Data Integration Patterns

#### Extract, Transform, Load (ETL)
- Scheduled data extraction
- Data transformation and validation
- Error handling and retry logic
- Data quality monitoring

#### Real-time Integration
- Event-driven architecture
- Message queues for reliability
- Circuit breaker patterns
- Monitoring and alerting

---
*Document Version: 1.0*  
*Last Updated: August 14, 2025*  
*Next Review: September 14, 2025*  
*Owner: Architecture Team*
