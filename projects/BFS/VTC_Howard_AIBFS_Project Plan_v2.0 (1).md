|<p></p><p>**AI Budget Platform**</p>|

Howard County Government (HCG) 

Budgeting Office (OB) 



Artificial Intelligence Budgeting & Forecasting System (BFS) 





AI BFS Project Plan









Document Created by 

Visionary Technology Consultants (VTC) 






Project Plan for Howard County AI BFS Solution

\
Introduction

Howard County’s annual budgeting process is a critical function that ensures the alignment of public resources with community priorities, strategic goals, and legally mandated fiscal requirements. The process begins with revenue forecasting and culminates in the submission, review, adjustment, and adoption of both the operating and capital budgets through a tightly constrained legislative timeline defined by the County Charter. Each year, departments submit funding requests via decentralized methods, the Planning Board evaluates capital projects, the County Executive holds hearings and formulates a comprehensive budget proposal, and the County Council conducts hearings and work sessions before adopting the final budget no later than June 1st.

Despite the importance of this cycle, the current budgeting process remains highly manual, fragmented, and time-intensive, relying on spreadsheets, email communication, disconnected data systems, and repeated document handling. This results in:

- Delayed submissions and inconsistent formatting from departments
- Difficulty enforcing budget constraints (e.g., balanced budget, expenditure reduction rules)
- Inefficient review processes across the Planning Board, Executive Office, and Council
- Limited visibility into real-time budget status and public sentiment
- Redundant effort in generating and formatting legislative bills, resolutions, and transparency reports

\
The Proposed Solution: Howard County Budget Automation Module

To modernize this process, the GovAssist platform will be enhanced with a tailored Budget Automation Module specifically designed to meet the legal, fiscal, and operational requirements of Howard County. This module will introduce a centralized, AI-powered workflow that spans the entire budget lifecycle, from department-level submissions to legislative adoption and public reporting.

Key innovations of the module include:

- A role-based portal for departments to enter and track budget submissions with automated validation
- A revenue forecasting engine that uses historical data and economic indicators to ensure proposed expenditures are aligned with actual funding capacity
- Structured workflows for Planning Board review, Executive adjustments, and Council reductions in compliance with Charter restrictions
- An NLP-driven public comment engine to capture, classify, and summarize resident feedback from hearings and online submissions
- A powerful scenario modeling tool for what-if analysis of revenues, capital project phasing, and expenditure reallocations
- Real-time dashboards and compliance alerts for leadership, tracking fund balances, legal compliance, and workflow progress
- Automated generation of all legislative outputs and public-facing documents, including ADA-compliant digital formats

By digitizing, integrating, and streamlining Howard County’s budget process, this module will reduce administrative burden, improve transparency and accountability, and accelerate the delivery of accurate, compliant, and responsive budgets that reflect the county’s priorities and fiscal realities.\
\
I. Project Summary

Objective

Design, develop, and deploy a secure, AI-powered budgeting module within the GovAssist platform to fully automate Howard County’s annual budget lifecycle, from departmental submission to legislative approval and public transparency.

Scope

The system will centralize budget planning, automate workflows, enforce compliance with County Charter rules, facilitate public participation, and provide scenario modeling and real-time dashboards for executive-level insights.
## II. Module Description
### Module Name: Howard County Budget Automation Module
### Functionality Overview:

|Function|Description|
| :-: | :-: |
|1\. Department Budget Submission|Department-specific portals for capital and operating requests with smart forms, auto-fill of prior-year data, and workflow tracking|
|2\. Revenue Forecasting|Predictive model using historical tax data, economic indicators, and constraint rules for balanced budget enforcement|
|3\. Capital & Operating Budget Separation|Tracks different budget types and aligns them with funding sources (PAYGO, Bonds, Taxes, Special Funds)|
|4\. Planning Board Workflow|Collects, displays, and tracks comments and approvals on new/modified capital projects|
|5\. County Executive Portal|Approves/rejects submissions, integrates public hearing input, and finalizes legislative budget bills|
|6\. Council Review & Restriction Enforcement|Allows reductions only, auto-enforces no-increase rule, and auto-generates modified resolutions|
|7\. Public Comment Engine|Allows citizen input, auto-tags content by department/topic, performs sentiment analysis|
|8\. Scenario Modeling|Allows stakeholders to model alternative revenue/expenditure plans and test funding changes|
|9\. Executive Dashboards|Real-time visualization of revenue vs expenditure, submission progress, legal compliance, and fund performance|
|10\. Document Generation & Transparency Portal|Auto-generates legislative packets, citizen budget summaries, and publishes to public site with full ADA compliance|

III. Benefits & Current Manual Pain Points Solved

|Problem|Current Manual Process|Benefit of Automation|
| :-: | :-: | :-: |
|Department Budget Collection|Spreadsheets, email chains, PDF uploads|Centralized portal with real-time validation and deadlines|
|Revenue Forecasting|Manual economic assumption tables|AI-powered forecast engine with alerts for imbalance|
|Capital/Operating Split|Excel tracking and narrative coordination|Automated separation with dynamic fund mapping|
|Planning Board Review|Document circulation via email; no structured input|Workflow engine with structured feedback and compliance tracking|
|Council Review|Manual redlining of legislative packages|Role-based portal with version control, redlining, and automation of allowed reductions only|
|Public Engagement|Disconnected surveys, email input, and physical hearings|Unified public portal with auto-tagging and sentiment dashboards|
|Scenario Modeling|Manual Excel models with limited variables|Interactive what-if engine with fund impact visualization|
|Dashboards|Siloed reports across departments|Centralized, real-time compliance, trend, and performance dashboards|
|Document Generation|Repetitive drafting of budget ordinances and summaries|One-click automated generation of legislative documents and public-facing formats|

IV. 4-Month Delivery Plan (120 Days)

Month 1: Discovery & Architecture (Days 1–30)

Goals:

- Fully document county processes, legal requirements, data sources
- Finalize architecture, workflows, and UX prototypes

Activities:

- Kickoff meeting with County Executive Office, Budget Office, Council Admin, and Planning Board
- Stakeholder interviews (Departments, Budget Officers, Planning, Council Analysts)
- Review of Charter rules, previous years’ budget documents, and ERP integration needs
- Workflow diagrams for department intake, Planning Board, Executive, and Council processes
- Architecture plan: Azure deployment, API integrations, authentication (AAD), RBAC setup
- UX mockups of dashboards, portals, and public engagement module

Deliverables:

- Requirements Traceability Matrix (RTM)
- Architecture & Integration Blueprint
- UX Prototypes
- Data Dictionary
- Sprint Plan for Months 2–4
### Month 2: Core Module Development (Days 31–60)
#### Goals:
- Build backend logic and frontend components for key budgeting functions
- Begin internal testing with synthetic and prior-year data
#### Activities:
- Develop:
  - Budget Submission Portal (capital & operating forms, status tracking)
  - Forecast Engine (tax data ingestion, projection models)
  - Capital/Operating Manager (fund tagging, compliance checks)
  - Planning Board Review module
- Integrate with:
  - County’s ERP financial system and tax data sources
  - SharePoint for document storage (if applicable)
- Implement authentication (Azure AD), RBAC, and audit logging
#### Deliverables:
- Working demo of submission → Planning Board workflow
- Integration with ERP test environment
- Initial data upload: last 3 years' budget data
- Test case library and QA protocols

Month 3: Advanced Workflow & Analytics Layer (Days 61–90)
#### Goals:
- Complete workflows for Executive and Council
- Implement public comment NLP engine and dashboard analytics
#### Activities:
- Develop:
  - Council workflow engine (reduction-only logic, resolution generation)
  - Executive review portal (approval, adjustment routing)
  - Public Comment Portal (tagging engine, topic classification, sentiment scoring)
  - Executive Dashboard Suite (budget status, variance heatmaps, historical trends)
  - Scenario Modeling Engine (adjust revenue, delay projects, reallocate funds)
- Run mock “April to June” budget simulation using last year’s budget
- Begin staff training on usage and administration
#### Deliverables:
- Full module walkthrough (submission to Council resolution)
- Sentiment analysis reports from prior year hearings
- User manuals and training decks
- Public portal prototype

Month 4: Testing, Deployment & Go-Live (Days 91–120)
#### Goals:
- Full UAT, performance tuning, security testing
- Deploy to Howard County’s Azure environment
#### Activities:
- Conduct:
  - User Acceptance Testing (UAT) with Budget Office, Departments, Council
  - Load testing for peak submission windows
  - Security review (MFA, access controls, data encryption)
  - Accessibility and ADA compliance check
- Deploy:
  - GovAssist container with budget module to County’s Azure tenant
  - Live public portal and dashboard access
- Final training workshops (Department users, Council staff, Executive aides)
#### Deliverables:
- Production-ready deployment
- UAT sign-off documentation
- Training completion certification
- Final module report (metrics, open issues, roadmap)
- Go-Live Support Plan (30-day stabilization period)

V. Key Roles & Responsibilities

|Role|Team|Responsibility|
| :-: | :-: | :-: |
|Product Manager|VTC|SOW delivery, stakeholder alignment|
|Technical Lead|AutoBridge|Architecture, integrations, security|
|UI/UX Designer|AutoBridge|Portal design, dashboard layout|
|NLP Engineer|AutoBridge|Public comment tagging, modeling|
|QA Lead|VTC|Test cases, regression, UAT|
|Budget Office Liaison|Howard County|Process alignment, requirements validation|
|IT Liaison|Howard County|ERP & Azure support, user access management|

VI. Acceptance Criteria

- 100% of departments successfully submit budgets through portal
- Budget passes forecast engine validation and balance check
- Council able to reduce but not increase expenditures via system logic
- Planning Board and public comments are fully captured, tagged, and summarized
- System auto-generates final legislative package for adoption
- Executive dashboards reflect real-time performance and compliance
- All workflows leave an immutable audit trail
- Public transparency portal is ADA compliant and displays current and past budgets

2

