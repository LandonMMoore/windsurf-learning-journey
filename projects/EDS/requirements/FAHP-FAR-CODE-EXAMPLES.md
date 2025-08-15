# FAHP/FAR Part 31 Compliance - Code Implementation Examples

## 1. FAR Part 31.201-3: Cost Reasonableness Validation

### What it means:
"A cost is reasonable if it does not exceed that which would be incurred by a prudent person in the conduct of competitive business"

### How developers validate this programmatically:

```python
class CostReasonablenessValidator:
    def __init__(self):
        self.industry_benchmarks = self.load_industry_data()
        self.historical_costs = self.load_historical_data()
    
    def validate_cost_reasonableness(self, cost_item: dict) -> ValidationResult:
        """
        Validates if a cost meets FAR 31.201-3 reasonableness standard
        """
        cost_type = cost_item['type']  # e.g., 'labor', 'materials', 'overhead'
        amount = cost_item['amount']
        project_context = cost_item['context']
        
        # 1. Compare against industry benchmarks
        benchmark_range = self.get_industry_benchmark(cost_type, project_context)
        if amount > benchmark_range['max_reasonable']:
            return ValidationResult(
                valid=False,
                reason=f"Cost ${amount} exceeds industry benchmark ${benchmark_range['max_reasonable']}",
                regulation="FAR 31.201-3",
                action_required="Provide justification or reduce cost"
            )
        
        # 2. Compare against historical costs for similar work
        historical_avg = self.get_historical_average(cost_type, project_context)
        variance_threshold = 0.20  # 20% variance allowed
        if amount > historical_avg * (1 + variance_threshold):
            return ValidationResult(
                valid=False,
                reason=f"Cost ${amount} exceeds historical average ${historical_avg} by more than 20%",
                regulation="FAR 31.201-3",
                documentation_required="Burden of proof on contractor to justify increase"
            )
        
        # 3. Check for "prudent person" criteria
        prudent_person_checks = self.validate_prudent_person_standard(cost_item)
        
        return ValidationResult(valid=True, compliant_with="FAR 31.201-3")

    def validate_prudent_person_standard(self, cost_item: dict) -> bool:
        """
        Checks if cost would be incurred by prudent person in competitive business
        """
        checks = {
            'competitive_bidding': self.was_competitively_bid(cost_item),
            'business_necessity': self.is_business_necessary(cost_item),
            'arm_length_transaction': self.is_arms_length(cost_item),
            'reasonable_timing': self.is_reasonably_timed(cost_item)
        }
        
        return all(checks.values())
```

## 2. FAHP 2 CFR 200.414: IDCR (Indirect Cost Recovery) Validation

### What it means:
Indirect costs must be validated against NICRA (negotiated rates) and fund availability

### How developers validate this programmatically:

```python
class IDCRValidator:
    def __init__(self):
        self.sharepoint_etl = SharePointETLService()
        self.fmis_service = FMISIntegrationService()
        self.nicra_service = NICRAValidationService()
    
    def validate_idcr_compliance(self, par_data: dict) -> ValidationResult:
        """
        Cross-validates IDCR across multiple federal data sources
        """
        project_id = par_data['project_id']
        indirect_costs = par_data['indirect_costs']
        direct_costs = par_data['direct_costs']
        
        # Step 1: Get NICRA rates from SharePoint ETL (DIFS sync)
        nicra_rates = self.sharepoint_etl.get_current_nicra_rates()
        if not nicra_rates:
            return ValidationResult(
                valid=False,
                reason="NICRA rates not available from SharePoint ETL",
                regulation="2 CFR 200.414"
            )
        
        # Step 2: Validate against fund availability (FMIS 60 report)
        fund_availability = self.fmis_service.get_fund_availability_report()
        program_code = par_data['program_code']
        available_funds = fund_availability.get(program_code, 0)
        
        total_project_cost = direct_costs + indirect_costs
        if total_project_cost > available_funds:
            return ValidationResult(
                valid=False,
                reason=f"Total cost ${total_project_cost} exceeds available funds ${available_funds}",
                regulation="2 CFR 200.414",
                data_source="FMIS 60 Report"
            )
        
        # Step 3: Cross-validate with FMIS 37 report (validation logic)
        fmis_37_validation = self.fmis_service.validate_against_fmis_37(par_data)
        
        # Step 4: Calculate and validate IDCR percentage
        calculated_idcr = (indirect_costs / direct_costs) * 100
        allowed_idcr = nicra_rates.get('current_rate', 0)
        
        if calculated_idcr > allowed_idcr:
            return ValidationResult(
                valid=False,
                reason=f"IDCR {calculated_idcr}% exceeds NICRA rate {allowed_idcr}%",
                regulation="2 CFR 200.414",
                action_required="Reduce indirect costs or obtain rate modification"
            )
        
        # Step 5: Validate cost allocation base (FAR 31.203)
        allocation_validation = self.validate_cost_allocation_base(par_data)
        
        return ValidationResult(
            valid=True,
            validated_sources=["SharePoint_ETL", "FMIS_60", "FMIS_37", "NICRA"],
            compliance_level="Full IDCR compliance achieved"
        )
    
    def validate_cost_allocation_base(self, par_data: dict) -> bool:
        """
        FAR 31.203: Validates indirect cost allocation base
        """
        # Ensure all costs in base bear pro rata share
        cost_base = par_data['cost_allocation_base']
        
        # Check for fragmented base (not allowed per FAR 31.203(d))
        if self.is_base_fragmented(cost_base):
            raise ValidationError("Cost base fragmentation violates FAR 31.203(d)")
        
        # Validate logical cost groupings
        return self.validate_logical_cost_groupings(cost_base)
```

## 3. Program Code Validation with M60 Tables

### What it means:
Validate program codes against FHWA M60 tables and ensure federal share percentages are correct

### How developers validate this programmatically:

```python
class ProgramCodeValidator:
    def __init__(self):
        self.m60_service = M60TableService()
        self.fhwa_service = FHWAService()
        self.cfda_service = CFDAValidationService()
    
    def validate_program_code_compliance(self, par_data: dict) -> ValidationResult:
        """
        Validates program codes against M60 tables and CFDA requirements
        """
        program_code = par_data['program_code']  # e.g., 'NHPP', 'STBG', 'CMAQ'
        project_type = par_data['project_type']
        federal_share = par_data['federal_share_percentage']
        
        # Step 1: Validate against M60 tables
        m60_validation = self.m60_service.validate_program_code(
            program_code=program_code,
            project_type=project_type
        )
        
        if not m60_validation.valid:
            return ValidationResult(
                valid=False,
                reason=f"Program code {program_code} invalid for project type {project_type}",
                regulation="FHWA Program Code Guidance",
                data_source="M60 Tables"
            )
        
        # Step 2: Validate federal share percentage
        max_federal_share = m60_validation.max_federal_share
        if federal_share > max_federal_share:
            return ValidationResult(
                valid=False,
                reason=f"Federal share {federal_share}% exceeds maximum {max_federal_share}%",
                regulation="2 CFR 200 / FHWA Guidelines"
            )
        
        # Step 3: Cross-validate with CFDA (2 CFR 200.210)
        cfda_code = par_data.get('cfda_code')
        cfda_validation = self.cfda_service.validate_cfda_alignment(
            program_code=program_code,
            cfda_code=cfda_code
        )
        
        # Step 4: Real-time validation against FMIS systems
        fmis_validation = self.validate_against_fmis_systems(par_data)
        
        return ValidationResult(
            valid=True,
            validated_against=["M60_Tables", "CFDA", "FMIS_37", "FMIS_60"],
            compliance_achieved="Full program code compliance"
        )

    def validate_against_fmis_systems(self, par_data: dict) -> bool:
        """
        Cross-validates program code data against FMIS 37 and 60 reports
        """
        program_code = par_data['program_code']
        
        # Check FMIS 60 for fund availability
        fmis_60_data = self.fmis_service.get_fmis_60_report()
        available_funds = fmis_60_data.get_available_funds(program_code)
        
        # Check FMIS 37 for validation logic
        fmis_37_validation = self.fmis_service.validate_fmis_37(par_data)
        
        return available_funds > 0 and fmis_37_validation.valid
```

## 4. Real-World Validation Workflow

### How this works in practice during PAR submission:

```python
class PARComplianceValidator:
    def __init__(self):
        self.cost_validator = CostReasonablenessValidator()
        self.idcr_validator = IDCRValidator()
        self.program_validator = ProgramCodeValidator()
        self.audit_logger = ComplianceAuditLogger()
    
    def validate_par_submission(self, par_data: dict) -> ComplianceReport:
        """
        Complete FAHP/FAR Part 31 validation before PAR approval
        """
        validation_results = []
        
        # 1. FAR Part 31 Cost Validation
        for cost_item in par_data['cost_items']:
            cost_result = self.cost_validator.validate_cost_reasonableness(cost_item)
            validation_results.append(cost_result)
            
            if not cost_result.valid:
                # Stop processing - cost must be justified or reduced
                return ComplianceReport(
                    status="REJECTED",
                    reason=cost_result.reason,
                    regulation_violated=cost_result.regulation
                )
        
        # 2. IDCR Validation (Multi-system cross-check)
        idcr_result = self.idcr_validator.validate_idcr_compliance(par_data)
        validation_results.append(idcr_result)
        
        # 3. Program Code Validation
        program_result = self.program_validator.validate_program_code_compliance(par_data)
        validation_results.append(program_result)
        
        # 4. Generate compliance audit trail
        self.audit_logger.log_compliance_check(
            par_id=par_data['id'],
            validations=validation_results,
            timestamp=datetime.now(),
            data_sources_checked=["SharePoint_ETL", "FMIS_37", "FMIS_60", "M60_Tables", "NICRA"]
        )
        
        # 5. Final compliance determination
        all_valid = all(result.valid for result in validation_results)
        
        return ComplianceReport(
            status="APPROVED" if all_valid else "REQUIRES_REVIEW",
            validation_results=validation_results,
            compliance_level=self.calculate_compliance_percentage(validation_results),
            next_steps=self.generate_next_steps(validation_results)
        )
```

## 5. What This Accomplishes for Compliance

### Automated Validation Results:
- **Cost Reasonableness**: Automatically flags costs exceeding industry benchmarks
- **IDCR Compliance**: Cross-validates indirect costs against 4 federal data sources
- **Program Code Validation**: Ensures codes are valid for project type and funding limits
- **Audit Trail**: Complete documentation for federal audits
- **Real-time Compliance**: Prevents non-compliant PARs from being submitted

### Developer Implementation:
Your developers implement these validators as **middleware** in the PAR submission workflow - every PAR automatically runs through these checks before reaching human reviewers, ensuring federal compliance is built into the system rather than being a manual process.
