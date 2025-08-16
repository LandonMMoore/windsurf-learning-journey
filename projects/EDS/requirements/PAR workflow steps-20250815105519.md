# PAR

# PAR Workflow Overview
## Complete Federal PAR Workflow Explanation
### Phase 1: Internal EDS Preparation (Steps 1-3)
**All actions happen within EDS before ProTrack+ involvement**
*   **PM/Engineer creates the initial PAR in EDS**
    *   Enters project details, selects packet type, and saves draft
    *   EDS validates project exists using cached DIFS data from last ETL sync
    *   No budget details entered yet - just high-level project info
*   **Budget Analyst receives notification and opens PAR in EDS**
    *   Reviews the PM's submission
    *   For federal projects, completes the budget split panel
    *   **NEW**: Enters program code for federal PARs (per Kathryn's feedback)
    *   EDS validates fund availability against cached DIFS data
    *   Ensures splits total 100% and match requirements are met
*   **Financial Manager reviews in EDS**
    *   Checks budget analyst's work for accuracy
    *   Can add comments but doesn't change data
    *   Approves or sends back for corrections
    *   **Upon approval, EDS automatically submits to ProTrack+**
### Phase 2: ProTrack+ Workflow Management (Steps 4-6)
**PAR is now in ProTrack+, but EDS continuously monitors**
*   **ProTrack+ receives the PAR submission**
    *   EDS gets back a ProTrack+ ID and starts polling for status updates
    *   **Engineer Supervisor and DDOT Leadership review** (per Kathryn's feedback)
    *   EDS dashboard shows current ProTrack+ status
*   **RAD reviews in ProTrack+** (to be confirmed with Nicole)
    *   Reviews resource allocation aspects
    *   ProTrack+ notifies EDS of status change
    *   EDS updates dashboard and sends notifications
*   **ProTrack+ reaches "FHWA" step - triggers EDS action**
    *   ProTrack+ shows "FHWA" status (proxy step)
    *   **This means PAR is ready for FMIS submission**
    *   EDS detects this status and notifies OCFO users
    *   OCFO now works in EDS to begin federal submission
### Phase 3: Federal (FMIS) Interaction (Steps 7-10)
**OCFO manages entire federal process from within EDS**
*   **OCFO initiates FMIS submission in EDS**
    *   OCFO user logs into EDS (not ProTrack+)
    *   Reviews PAR details and clicks "Submit to FMIS"
    *   **EDS automatically generates and submits FMIS XML** with all required PAR data
    *   **EDS eliminates manual data entry** - replaces current process where Budget Analyst manually types everything
    *   EDS begins polling FMIS for response and signature status
*   **Leadership Approval - Kathryn/Calvin sign first (State Signatures 1-3)**
    *   **After FMIS submission, Kathryn and Calvin approve first signature line**
    *   **EDS triggers email to second signature (DDOT)** with cc to Tatiana Stevens
    *   **EDS triggers email to third signature (DDOT)** after second approval
    *   **All three state signatures completed via automated email workflow**
*   **FHWA approval in FMIS (Federal Signatures 1-3)**
    *   **PAR sits with Federal Highway waiting for their three signatures**
    *   **Total of 6 signatures required: 3 state + 3 federal**
    *   FMIS validates the federal submission
    *   May take hours or days to process
    *   **Currently no status updates - manual checking required**
*   **EDS automatically updates DIFS after FHWA approval**
    *   **EDS monitors FMIS for FHWA approval completion** (replaces manual checking)
    *   **EDS automatically pushes approved PAR data to DIFS** via SharePoint ETL
    *   **EDS eliminates manual DIFS entry** - replaces current process where Budget Analyst manually types everything
    *   **EDS ensures data integrity** - no risk of missing updates due to human error
### Phase 4: Finalization (Step 11)
**EDS completes the PAR across all systems**
*   **EDS finalizes the PAR**
    *   **EDS automatically sends notifications** to PM and all stakeholders when FHWA approval is complete
    *   **EDS updates all dashboards** with real-time completion status
    *   **EDS archives the PAR** with complete audit trail including all signatures and approvals
    *   **EDS provides automated DIFS synchronization** - eliminating all manual data entry
    *   **EDS provides real-time FHWA status monitoring** - eliminating manual status checking
* * *

# PAR Workflows
Reference:

![](https://t9011890231.p.clickup-attachments.com/t9011890231/843f375c-a5cc-4ec7-a159-72ab1901538f/image.png)
## Internal EDS Workflow (ALL PAR Types Start Here)

| Step | Stage | Role | Location | Actions | EDS System Actions | Integration |
| ---| ---| ---| ---| ---| ---| --- |
| 1 | PAR Creation | PM/Engineer (RAD) | EDS | Creates initial ePAR, enters project details | • Validate project exists in DIFS cache<br>• Auto-populate fields<br>• Save draft status | DIFS ETL (read) |
| 2 | Budget Summary | Budget Analyst (OCFO) | EDS | Reviews submission, creates budget split | • Display budget panel (federal only)<br>• Validate split = 100%<br>• Check fund availability | DIFS ETL (read) |
| 3 | Financial Review | Financial Manager (OCFO) | EDS | Reviews for accuracy | • Log review completion<br>• Capture comments<br>• Update status | Internal only |
| 4 | Leadership Sign-off | Budget Officer (Catherine/Calvin) | EDS | Final internal approval | • Capture digital signature<br>• Lock PAR from edits<br>• Trigger ProTrack+ submission | ProTrack+ API |

* * *
## Federal Workflows - After Internal Approval
### Capital Project Budget Reallocation (Federal/FHWA)

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | PAR enters ProTrack+ | • Send PAR data to ProTrack+<br>• Receive ProTrack+ ID<br>• Start status polling | "Submitted to ProTrack+" |
| 6 | PM Confirmation | PM | ProTrack+ | Confirms details | • Receive status update<br>• Log PM confirmation | "PM Review in ProTrack+" |
| 7 | RAD Review | RAD | ProTrack+ | Reviews allocation | • Receive status update<br>• Display in dashboard | "RAD Review" |
| 8 | OCFO Review | OCFO | ProTrack+ | Financial compliance | • Receive status update<br>• Re-validate against latest DIFS ETL | "OCFO Review" |
| 9 | FHWA Prep | OCFO | EDS | Prepare & submit federal | • OCFO triggers FMIS submission in EDS<br>• EDS generates FMIS XML<br>• EDS submits to FMIS<br>• EDS polls for response | "Submitting to FMIS" |
| 10 | FHWA Review | FHWA | FMIS | Federal approval | • FMIS processes submission<br>• EDS displays status to OCFO<br>• OCFO monitors response in EDS | "Under Federal Review" |
| 11 | OCFO Final | OCFO | EDS | Process federal decision | • OCFO reviews FMIS response in EDS<br>• OCFO approves/rejects based on FMIS<br>• EDS updates ProTrack+ status<br>• EDS queues DIFS update | "Processing Approval" |
| 12 | Completion | System | EDS | Close PAR | • Send notifications<br>• Update dashboards<<br>• Archive PAR<br>• Sync with next DIFS ETL | "Approved - Complete" |

### Federal Project End Date

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | PAR enters ProTrack+ | • Send end date extension request<br>• Include justification | "Submitted to ProTrack+" |
| 6 | PM Confirmation | PM | ProTrack+ | Initiates request | • Log confirmation | "PM Review in ProTrack+" |
| 7 | RAD Review | RAD | ProTrack+ | Reviews extension | • Track review progress | "RAD Review" |
| 8 | OCFO Review | OCFO | ProTrack+ | Financial impact | • Validate no budget impact | "OCFO Review" |
| 9 | FHWA Submission | System | EDS → FMIS | Submit to federal | • Generate date change XML<br>• Submit to FMIS | "Federal Review" |
| 10 | PM Notification | System | EDS | Notify completion | • Update project end date<br>• Send notifications<br>• Queue DIFS sync | "Approved - Complete" |

### Federal Project Close-Out

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Enter closeout workflow | • Send closeout request<br>• Include final accounting | "Closeout Initiated" |
| 6 | PM Confirmation | PM | ProTrack+ | Initiates closeout | • Log initiation | "PM Review" |
| 7 | AD Review | AD | ProTrack+ | Division approval | • Track AD assignment (dynamic) | "AD Review" |
| 8 | RAD Review | RAD | ProTrack+ | Resource reconciliation | • Display expenditure summary | "RAD Reconciliation" |
| 9 | CO Review | CO | ProTrack+ | Administration approval | • Track CO assignment (dynamic) | "CO Review" |
| 10 | OCFO Review | OCFO | ProTrack+ | Financial closeout | • Validate zero balance<br>• Check all invoices paid | "OCFO Closeout Review" |
| 11 | FMIS Closeout | System | EDS → FMIS | Federal closeout | • Generate closeout XML<br>• Submit to FMIS<br>• Await confirmation | "Federal Closeout" |
| 12 | RAD Final | RAD | ProTrack+ | Complete process | • Archive project<br>• Lock all records<br>• Final DIFS sync | "Closed" |

### FHWA Project De-obligation

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Enter de-obligation flow | • Send de-obligation request<br>• Include amount/reason | "De-obligation Initiated" |
| 6 | RAD Initiation | RAD | ProTrack+ | Starts process | • Validate fund details | "RAD Initiated" |
| 7 | AD Review | AD | ProTrack+ | Division approval | • Track approval | "AD Review" |
| 8 | CAO Review | CAO | ProTrack+ | Admin approval | • Log CAO decision | "CAO Review" |
| 9 | OCFO Review | OCFO | ProTrack+ | Financial validation | • Confirm funds available to remove | "OCFO Review" |
| 10 | FMIS De-obligation | System | EDS → FMIS | Federal removal | • Generate de-obligation XML<br>• Submit to FMIS | "Federal Processing" |
| 11 | OCFO Final | OCFO | ProTrack+ | Process completion | • Update budget records<br>• Queue DIFS sync | "Completing De-obligation" |
| 12 | Completion | System | EDS | Update all systems | • Reduce project budget<br>• Send notifications<br>• Archive transaction | "De-obligated" |

### FHWA Project Withdraw

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Enter withdrawal flow | • Send withdrawal request<br>• Include justification | "Withdrawal Initiated" |
| 6 | RAD Initiation | RAD | ProTrack+ | Starts withdrawal | • Display project history | "RAD Initiated" |
| 7 | AD Review | AD | ProTrack+ | Division approval | • Track approval | "AD Review" |
| 8 | CAO Review | CAO | ProTrack+ | Policy compliance | • Validate compliance | "CAO Review" |
| 9 | OCFO Review | OCFO | ProTrack+ | Financial impact | • Calculate total impact<br>• Show obligations | "OCFO Review" |
| 10 | FMIS Withdrawal | System | EDS → FMIS | Federal withdrawal | • Generate withdrawal XML<br>• Include all phases | "Federal Processing" |
| 11 | OCFO Final | OCFO | ProTrack+ | Complete withdrawal | • Zero out budgets<br>• Queue DIFS update | "Completing Withdrawal" |
| 12 | Completion | System | EDS | Close project | • Mark project withdrawn<br>• Archive all records<br>• Final notifications | "Withdrawn" |

### Obligation - Construction

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Request construction funds | • Send obligation request<br>• Include scope/amount | "Obligation Requested" |
| 6 | PM Confirmation | PM | ProTrack+ | Confirms request | • Log confirmation | "PM Review" |
| 7 | AD Review | AD | ProTrack+ | Division approval | • Track approval | "AD Review" |
| 8 | CO Review | CO | ProTrack+ | Admin approval | • Policy validation | "CO Review" |
| 9 | RAD Review | RAD | ProTrack+ | Resource allocation | • Check capacity | "RAD Review" |
| 10 | OCFO Review | OCFO | ProTrack+ | Financial review | • Validate funding sources | "OCFO Review" |
| 11 | FMIS Obligation | System | EDS → FMIS | Federal obligation | • Generate obligation XML<br>• Submit construction request | "Federal Review" |
| 12 | OCFO Process | OCFO | ProTrack+ | Process funds | • Allocate approved funds<br>• Update budgets | "Processing Obligation" |
| 13 | PM Notification | System | EDS | Notify approval | • Update project budget<br>• Enable construction phase<br>• Send notifications | "Obligated - Active" |

### Obligation - Design

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Request design funds | • Send obligation request<br>• Include design scope | "Obligation Requested" |
| 6 | PM Confirmation | PM | ProTrack+ | Confirms request | • Log confirmation | "PM Review" |
| 7 | AD Review | AD | ProTrack+ | Division approval | • Track approval | "AD Review" |
| 8 | CO Review | CO | ProTrack+ | Admin approval | • Policy validation | "CO Review" |
| 9 | RAD Review | RAD | ProTrack+ | Resource allocation | • Check capacity | "RAD Review" |
| 10 | OCFO Review | OCFO | ProTrack+ | Financial review | • Validate funding sources | "OCFO Review" |
| 11 | FMIS Obligation | System | EDS → FMIS | Federal obligation | • Generate obligation XML<br>• Submit design request | "Federal Review" |
| 12 | OCFO Process | OCFO | ProTrack+ | Process funds | • Allocate approved funds<br>• Update budgets | "Processing Obligation" |
| 13 | PM Notification | System | EDS | Notify approval | • Update project budget<br>• Enable design phase<br>• Send notifications | "Obligated - Active" |

* * *
## Local Workflows - After Internal Approval
### Capital Project Budget Reallocation (Local/CIP)

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Enter local workflow | • Send reallocation request<br>\>• No FMIS fields needed | "In ProTrack+ Review" |
| 6 | PM Confirmation | PM | ProTrack+ | Confirms request | • Log confirmation | "PM Review" |
| 7 | RAD Review | RAD | ProTrack+ | Resource review | • Validate local funds only | "RAD Review" |
| 8 | OCFO Approval | OCFO | ProTrack+ | Final approval | • Approve reallocation | "OCFO Final Review" |
| 9 | Completion | System | EDS | Update systems | • Update budgets<br>• Queue DIFS sync<br>• Send notifications | "Approved - Complete" |

### Local Capital - Allocation

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Request allocation | • Send allocation request | "Allocation Requested" |
| 6 | PM Confirmation | PM | ProTrack+ | Confirms need | • Log confirmation | "PM Review" |
| 7 | AD Review | AD | ProTrack+ | Division approval | • Track approval | "AD Review" |
| 8 | RAD Review | RAD | ProTrack+ | Resource allocation | • Check local capacity | "RAD Review" |
| 9 | OCFO Approval | OCFO | ProTrack+ | Approve funds | • Allocate local funds<br>• Queue DIFS update | "OCFO Approval" |
| 10 | Completion | System | EDS | Finalize | • Update project<br>• Send notifications | "Allocated" |

### Local Capital - Post Allocation

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Remove allocation | • Send removal request | "Removal Initiated" |
| 6 | RAD Initiation | RAD | ProTrack+ | Start removal | • Display current allocations | "RAD Initiated" |
| 7 | CAO Review | CAO | ProTrack+ | Admin approval | • Policy check | "CAO Review" |
| 8 | OCFO Process | OCFO | ProTrack+ | Process removal | • Remove funds<br>• Update records | "OCFO Processing" |
| 9 | Completion | System | EDS | Finalize | • Update budgets<br>• Queue DIFS sync | "Funds Removed" |

### Local Capital Close-Out

| Step | Stage | Role | Location | Actions | EDS System Actions | Status in EDS |
| ---| ---| ---| ---| ---| ---| --- |
| 5 | ProTrack+ Submission | System | ProTrack+ | Initiate closeout | • Send closeout request | "Closeout Initiated" |
| 6 | PM Initiation | PM | ProTrack+ | Start process | • Log initiation | "PM Review" |
| 7 | AD Review | AD | ProTrack+ | Division approval | • Validate completion | "AD Review" |
| 8 | RAD Review | RAD | ProTrack+ | Reconciliation | • Check expenditures | "RAD Reconciliation" |
| 9 | CO Review | CO | ProTrack+ | Admin approval | • Policy compliance | "CO Review" |
| 10 | OCP Review | OCP | ProTrack+ | Technical closeout | • Validate deliverables | "OCP Review" |
| 11 | OCFO Review | OCFO | ProTrack+ | Financial closeout | • Confirm zero balance | "OCFO Closeout" |
| 12 | RAD Final | RAD | ProTrack+ | Archive | • Complete closeout | "RAD Finalizing" |
| 13 | Completion | System | EDS | Close project | • Archive project<br>• Lock records|• Final DIFS sync | "Closed" |

* * *
## EDS Status Tracking & Actions Summary

| ProTrack+ Event | EDS Action | User Visibility |
| ---| ---| --- |
| Status Change | • Poll ProTrack+ API<br>• Update PAR status<br>• Log timestamp | Dashboard shows current stage |
| Approval at Step | • Capture approval details<br>• Store comments<br>• Update progress | Email notification sent |
| Rejection at Step | • Capture rejection reason<br>• Route back to originator<br>• Enable corrections | Alert in dashboard, email sent |
| FMIS Submission Needed | • Generate XML with all data<br>• Submit via HTTPS<br>• Track submission ID | Status: "Submitting to FMIS" |
| FMIS Response | • Parse response<br>• Update status<br>• Handle errors | Show federal decision |
| Final Approval | • Queue DIFS update<br>• Lock PAR<br>• Archive | Status: "Complete" |

* * *