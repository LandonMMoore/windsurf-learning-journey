# UPDATED PAR WORKFLOW - STAKEHOLDER CONFIRMED

*Based on Stakeholder Feedback - August 6, 2025*  
*Meeting with Kathryn Valentine & Email Responses*  
*Status: CORRECTED WORKFLOW - READY FOR IMPLEMENTATION*

---

## 🎯 **EXECUTIVE SUMMARY**

This document reflects the **corrected PAR workflow** based on stakeholder feedback, meeting transcript, and annotated responses. Key corrections include the proper FMIS process sequence, signature collection procedures, and manual processes that EDS can automate.

**Critical Insight**: Many current processes are manual and present automation opportunities for EDS.

---

## 📋 **CORRECTED PAR WORKFLOW PHASES**

### **Phase 1: Internal EDS Preparation (Steps 1-4)**
*All actions happen within EDS before any external system involvement*

#### **Step 1: PAR Creation**
**Role**: PM/Engineer (RAD)  
**Location**: EDS  
**Actions**: 
- Creates initial ePAR for existing projects
- Enters project details, selects packet type
- **Confirmed**: All PAR types (Federal, Local Capital, FMIS) start here

**EDS System Actions**:
- Validate project exists in DIFS cache from ETL sync
- Auto-populate available fields
- Save in draft status

**Integration**: DIFS ETL (read-only)

#### **Step 2: Engineering Review** *(NEW - Added from feedback)*
**Role**: Engineering Team  
**Location**: EDS  
**Actions**: 
- Reviews scope alignment with DDOT goals
- **Confirmed**: "Engineering reviews scope & passes to Finance"
- Ensures project scope aligns with intended purpose

**EDS System Actions**:
- Display project scope details
- Capture engineering review and comments
- Route to Finance upon approval

#### **Step 3: Budget Analysis**
**Role**: Budget Analyst (OCFO)  
**Location**: EDS  
**Actions**: 
- Reviews submission and creates budget split (federal projects)
- **Confirmed**: "Finance - budget alignment review"
- Validates fund availability against DIFS cache

**EDS System Actions**:
- Display budget panel for federal projects
- Validate split totals 100%
- Check fund availability via DIFS ETL data
- Capture budget analysis

#### **Step 4: Leadership Sign-off**
**Role**: Calvin (EDS Leadership)  
**Location**: EDS  
**Actions**: 
- **Confirmed**: "EDS Leadership approval - Calvin approval step"
- Final internal approval before external submission

**EDS System Actions**:
- Capture digital signature/approval
- Lock PAR from further edits
- Trigger ProTrack+ submission

---

### **Phase 2: ProTrack+ Workflow Management (Steps 5-8)**
*PAR is now in ProTrack+, EDS monitors status*

#### **Step 5: ProTrack+ Submission**
**Role**: System  
**Location**: ProTrack+  
**Actions**: 
- **Confirmed**: "PAR received into ProTrack+ - workflow starts within ProTrack+"
- PAR enters ProTrack+ workflow system

**EDS System Actions**:
- Send PAR data to ProTrack+ via API
- Receive ProTrack+ ID
- Begin status polling
- Display "Submitted to ProTrack+" status

#### **Step 6: PM Confirmation**
**Role**: PM  
**Location**: ProTrack+  
**Actions**: 
- **Confirmed**: PM reviews and confirms details in ProTrack+
- Validates submission accuracy

**EDS System Actions**:
- Receive status update from ProTrack+
- Log PM confirmation
- Update dashboard status

#### **Step 7: RAD Review**
**Role**: RAD  
**Location**: ProTrack+  
**Actions**: 
- **Confirmed**: "RAD approval primarily involves ensuring purpose aligns with DDOT goals"
- Reviews resource allocation aspects

**EDS System Actions**:
- Monitor ProTrack+ status updates
- Display "RAD Review" in dashboard
- Track approval/rejection status

#### **Step 8: OCFO Review in ProTrack+**
**Role**: OCFO  
**Location**: ProTrack+  
**Actions**: 
- **Confirmed**: OCFO performs compliance review in ProTrack+
- Validates PAR is ready for federal submission (if applicable)

**EDS System Actions**:
- Receive status updates
- Re-validate against latest DIFS ETL data
- Prepare for FMIS submission trigger

---

### **Phase 3: Federal (FMIS) Interaction (Steps 9-12)**
*CORRECTED SEQUENCE - Based on Meeting Transcript*

#### **Step 9: FMIS Submission by OCFO**
**Role**: Budget Analyst (OCFO)  
**Location**: FMIS (Manual Entry)  
**Actions**: 
- **CONFIRMED PROCESS**: "Budget analyst enters all PAR information into FMIS"
- **Current Reality**: "They type in all the information from the PAR into FMIS"

**EDS Automation Opportunity**:
- Generate FMIS XML with all required data
- Pre-populate FMIS submission form
- Eliminate manual data entry

**Current Manual Process**: Budget analyst manually types all PAR data into FMIS

#### **Step 10: State-Level Signature Collection**
**Role**: Calvin & Kathryn + 2 additional signers  
**Location**: Email-based process  
**Actions**: 
- **CONFIRMED PROCESS**: "Calvin and I sign the first line, then we have to send an email to the second and third signature"
- **Current Reality**: Manual email creation and signature tracking

**Required Signatures (State Side)**:
1. **First Signature**: Calvin & Kathryn (OCFO)
2. **Second Signature**: [To be confirmed - likely Environmental Officer]
3. **Third Signature**: [To be confirmed - likely Chief Engineer]

**EDS Automation Opportunity**:
- **CRITICAL**: "I'm hoping that EDS can trigger that"
- Automate signature request emails
- Track signature completion status
- Send notifications when signatures complete

**Current Manual Process**: 
1. Budget analyst creates email requesting signatures
2. Calvin & Kathryn sign first line
3. Email sent to second signature
4. Email sent to third signature
5. Manual tracking of completion

#### **Step 11: FHWA Approval in FMIS**
**Role**: FHWA (Federal)  
**Location**: FMIS System  
**Actions**: 
- **CONFIRMED**: "The actual federal approval happens in FMIS"
- Federal side processes submission (3 additional signatures)
- **Total signatures required**: 6 (3 state + 3 federal)

**EDS Monitoring Opportunity**:
- **Current Gap**: "We don't get an email stating that it's done"
- **Manual Reality**: "We have to go in there and check to see if it's done manually"

**EDS System Actions Needed**:
- Monitor FMIS for approval status
- Automated checking/polling
- Alert OCFO when federal approval complete

#### **Step 12: OCFO Loads PAR Back to DIFS**
**Role**: Budget Analyst (OCFO)  
**Location**: DIFS System  
**Actions**: 
- **CONFIRMED**: "OCFO loads the PAR back to DIFS"
- **Critical Reality**: "If the budget analyst does not put it in DIFS, it doesn't go in DIFS period"

**EDS Automation Opportunity**:
- **Current Manual Process**: "They have to type everything on that PAR into DIFS"
- **Exception**: "Except for the GIS, the GIS is not in DIFS"
- **Automation Goal**: Gather details from completed/update FMIS project data and identify easiest way for the Budget Analyst to upload to DIFS 

---

### **Phase 4: Finalization (Step 13)**
*EDS completes PAR across all systems*

#### **Step 13: System Finalization**
**Role**: EDS System  
**Location**: EDS  
**Actions**: 
- Send completion notifications to all stakeholders
- Update all dashboards with final status
- Archive PAR with complete audit trail
- Queue any remaining system updates

---

## 🔄 **LOCAL PROJECT WORKFLOWS**

### **Local Capital Projects**
**Confirmed Process**: 
- **Same internal EDS steps** (1-4)
- **ProTrack+ workflow** without FMIS submission
- **DIFS Updates**: "Budget analyst will have to manually put it in DIFS"

**EDS Automation Opportunity**: Same DIFS integration for local projects

---

## 🚨 **CRITICAL AUTOMATION OPPORTUNITIES**

### **1. Signature Collection Automation**
**Current Pain Point**: Manual email creation and tracking
**EDS Solution**: 
- Automated signature request emails
- Digital signature workflow
- Real-time signature status tracking
- Automatic progression to next signer

### **2. FMIS Status Monitoring**
**Current Pain Point**: Manual checking for federal approval
**EDS Solution**:
- Automated FMIS status polling
- Real-time approval notifications
- Dashboard status updates
- Alert system for OCFO

### **3. DIFS Integration**
**Current Pain Point**: Manual data entry into DIFS
**EDS Solution**:
- Automated DIFS updates via API integration
- Eliminate manual typing of PAR data
- Real-time synchronization
- Error handling and validation

### **4. FMIS Data Entry**
**Current Pain Point**: Manual typing of all PAR data into FMIS
**EDS Solution**:
- XML generation for FMIS submission
- Pre-populated forms
- Data validation before submission
- Eliminate manual data entry errors

---

## 📊 **INTEGRATION REQUIREMENTS MATRIX**

| System | Current Process | EDS Integration Opportunity | Priority |
|--------|----------------|---------------------------|----------|
| **ProTrack+** | API exists, status updates working | ✅ **IMPLEMENTED** | Complete |
| **FMIS** | Manual data entry, manual monitoring | 🔄 **XML GENERATION + MONITORING** | Critical |
| **DIFS** | Manual data entry for all updates | 🔄 **API INTEGRATION** | Critical |
| **Email/Signatures** | Manual email creation and tracking | 🔄 **AUTOMATED WORKFLOW** | High |

---

## 🎯 **IMPLEMENTATION PRIORITIES**

### **Phase 1: Critical Automation (30 days)**
1. **FMIS XML Generation**: Eliminate manual data entry
2. **Signature Workflow**: Automate email requests and tracking
3. **FMIS Status Monitoring**: Automated federal approval checking

### **Phase 2: DIFS Integration (60 days)**
1. **DIFS API Integration**: Work with DIFS team
2. **Automated PAR Updates**: Eliminate manual DIFS entry
3. **Real-time Synchronization**: Bidirectional data sync

### **Phase 3: Process Optimization (90 days)**
1. **End-to-end Automation**: Complete workflow automation
2. **Error Handling**: Comprehensive error recovery
3. **Performance Optimization**: System performance tuning

---

## 📋 **STAKEHOLDER CONFIRMATION CHECKLIST**

### **✅ Confirmed Understanding**
- [x] All PAR types start with internal EDS workflow (Steps 1-4)
- [x] Engineering review step added after RAD initial review
- [x] ProTrack+ handles workflow steps independently
- [x] FMIS submission requires manual data entry (automation opportunity)
- [x] 6 total signatures required (3 state + 3 federal)
- [x] DIFS updates are completely manual (automation opportunity)
- [x] No automatic notifications from FHWA (monitoring opportunity)

### **🔄 Requires Further Clarification**
- [ ] Specific roles for 2nd and 3rd state signatures
- [ ] ProTrack+ dynamic workgroup configuration (AD/DC assignments)
- [ ] GIS data synchronization requirements
- [ ] DIFS team integration capabilities
- [ ] FMIS API access possibilities

---

## 🎯 **SUCCESS METRICS**

### **Automation Goals**
- **Eliminate manual FMIS data entry**: 100% XML generation
- **Automate signature collection**: 95% email automation
- **FMIS monitoring**: Real-time status updates
- **DIFS integration**: 90% automated updates

### **Process Improvements**
- **Reduce PAR processing time**: 50% improvement
- **Eliminate data entry errors**: 95% reduction
- **Improve status visibility**: Real-time dashboards
- **Enhance audit trails**: Complete automation logging

---

This updated workflow reflects the **actual operational reality** and provides clear automation opportunities that will significantly improve the PAR process efficiency while maintaining compliance with federal requirements.
