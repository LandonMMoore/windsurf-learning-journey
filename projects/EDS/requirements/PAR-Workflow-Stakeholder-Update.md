# PAR Workflow Updates - Stakeholder Implementation Report

**Subject**: EDS PAR Workflow Updates Based on Your Feedback - Ready for Review

Dear Kathryn, Calvin, and Team,

Following our productive meeting and your detailed feedback, I've updated the PAR workflow documentation to accurately reflect the current process and EDS automation goals. Here's a comprehensive summary of the changes implemented based on your input:

## Key Changes Implemented

### 1. **Leadership Approval Repositioning**
**Your Feedback**: "Remove the leadership Phase 1 and move it to Phase 3 right after reviews PAR details and Clicks submit to FMIS"

**Implementation**: 
- Moved Kathryn/Calvin approval from Phase 1 to Phase 3 (after FMIS submission)
- Leadership approval now occurs as the first of three state signatures
- This aligns with the current process where you sign after the Budget Analyst enters information into FMIS

### 2. **Program Code Entry Addition**
**Your Feedback**: "Step 2 should be RAD Reviews in ProTrack+, add one more step in the process which is - Entering the program code for the federal PAR"

**Implementation**:
- Added program code entry as a specific step for Budget Analyst during federal PAR processing
- Noted that "who will enter and what" will be discussed in future meetings per your guidance

### 3. **Six-Signature Workflow Clarification**
**Your Feedback**: "Once the budget analyst enters the information into FMIS, Calvin/Kathryn signs first, second and third are with DDOT"

**Implementation**:
- **State Signatures (3)**: Kathryn/Calvin → 2nd DDOT → 3rd DDOT
- **Federal Signatures (3)**: FHWA handles their three signatures in FMIS
- **Total**: 6 signatures required for complete approval
- **Automation**: EDS will trigger automated emails to 2nd and 3rd signatures with cc to Tatiana Stevens

### 4. **FMIS Process Order Correction**
**Your Feedback**: "FHWA approval in FMIS, then OCFO loads the PAR back to DIFS"

**Implementation**:
- **Step 1**: OCFO submits to FMIS 
- **Step 2**: State signatures (Kathryn/Calvin first, then DDOT)
- **Step 3**: FHWA approval in FMIS (3 federal signatures)
- **Step 4**: OCFO loads approved PAR back to DIFS

### 5. **ProTrack+ Integration Refinement**
**Your Feedback**: "Kathryn was thinking — Engineer supervisor and DDOT leadership" and "RAD Reviews in ProTrack+ => we need to confirm with Nicole"

**Implementation**:
- Updated ProTrack+ workflow to include Engineer Supervisor and DDOT Leadership review
- Added note to confirm RAD review process with Nicole
- Clarified that "FHWA" step in ProTrack+ is a proxy status indicating readiness for FMIS submission

### 6. **Manual Process Automation Goals**
**Your Feedback**: Multiple references to current manual processes that need automation

**Implementation**:
- **FMIS Data Entry**: EDS will automatically generate and submit FMIS XML (eliminating manual typing)
- **DIFS Updates**: EDS will automatically push approved PAR data to DIFS via SharePoint ETL
- **Status Monitoring**: EDS will monitor FHWA approval status and provide real-time updates
- **Signature Workflow**: EDS will automate email triggers for signature approvals

## Current vs. Future State Summary

### **Current Manual Process** (What EDS Will Replace):
- Budget Analyst manually types all PAR information into FMIS
- Manual email creation for signature approvals
- Manual checking of FHWA approval status ("We have to go in there and check to see if it's done manually")
- Budget Analyst manually types everything from PAR into DIFS
- Risk of missing DIFS updates if Budget Analyst doesn't include them

### **EDS Automated Process** (What We're Building):
- Automatic FMIS XML generation and submission
- Automated signature workflow with email triggers
- Real-time FHWA approval monitoring
- Automatic DIFS synchronization via SharePoint ETL
- Complete audit trail and data integrity assurance

## Next Steps

1. **ProTrack+ Team Meeting**: I'll meet with the ProTrack+ team early next week to confirm workflow steps and integration points
2. **Nicole Confirmation**: Confirm RAD review process details with Nicole
3. **Calvin Discussion**: Schedule time for Calvin to review the updated workflow, particularly the leadership approval positioning
4. **Documentation Finalization**: Prepare final workflow documentation in Word format as requested

## Questions for Clarification

Based on your feedback, I have a few remaining questions:

1. **Signature Delegation**: Should there be delegation capabilities for Kathryn/Calvin approvals during absences?
2. **DIFS Integration**: What level of access will EDS need to automate DIFS updates via SharePoint ETL?
3. **Error Handling**: How should EDS handle FMIS rejection scenarios and resubmission workflows?

## Meeting Schedule

Per your suggestion, I've noted that Thursdays from 12:30-1:30 work well for our ongoing collaboration. I'll send calendar invites for our next review session once I have the ProTrack+ team input.

The updated PAR workflow documentation now accurately reflects your current process while clearly identifying the automation opportunities that EDS will deliver. This should provide a solid foundation for the development team to build the federal compliance and workflow automation features.

Thank you for your detailed feedback and patience as we work through these complex workflow requirements. The EDS module will significantly streamline your PAR processing while maintaining all necessary compliance and approval controls.

Best regards,

Landon Moore  
Product Manager, EDS Development  
GovAssist Platform

---

**Attachments**: 
- Updated PAR Workflow Steps Documentation
- FAHP/FAR Part 31 Compliance Requirements
- EDS Federal Compliance Implementation Plan
