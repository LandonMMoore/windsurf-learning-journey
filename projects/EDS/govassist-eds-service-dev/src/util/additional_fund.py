def serialize_fund(fund):
    return {
        "id": fund.id,
        "par_budget_analysis_id": fund.par_budget_analysis_id,
        "federal_fund_id": fund.federal_fund_id,
        "ce": fund.ce,
        "construction": fund.construction,
        "feasibility_studies": fund.feasibility_studies,
        "design": fund.design,
        "rights_of_way": fund.rights_of_way,
        "equipment": fund.equipment,
        "program_code": {
            "id": fund.federal_fund_id,
            "fund_code": fund.federal_fund.fund_code,
            "fund_available": fund.federal_fund.fund_available,
            "fund_obligations": fund.federal_fund.fund_obligations,
            "fund_unobligated_balance": fund.federal_fund.fund_unobligated_balance,
            "fund_pending_obligations": fund.federal_fund.fund_pending_obligations,
            "fund_pending_unobligated_balance": fund.federal_fund.fund_pending_unobligated_balance,
            "fund_advance_construction": fund.federal_fund.fund_advance_construction,
            "created_at": (
                fund.federal_fund.created_at.isoformat()
                if fund.federal_fund.created_at
                else None
            ),
            "updated_at": (
                fund.federal_fund.updated_at.isoformat()
                if fund.federal_fund.updated_at
                else None
            ),
        },
    }
