def _prepare_par_budget_analysis_data(par_budget_analysis):
    return {
        "id": par_budget_analysis.id,
        "par_id": par_budget_analysis.par_id,
        "project_details_id": par_budget_analysis.project_details_id,
        "ce_rate": (
            float(par_budget_analysis.ce_rate)
            if par_budget_analysis.ce_rate is not None
            else None
        ),
        "part_rate": (
            float(par_budget_analysis.part_rate)
            if par_budget_analysis.part_rate is not None
            else None
        ),
        "fa_rate": (
            float(par_budget_analysis.fa_rate)
            if par_budget_analysis.fa_rate is not None
            else None
        ),
        "dc_rate": (
            float(par_budget_analysis.dc_rate)
            if par_budget_analysis.dc_rate is not None
            else None
        ),
        "justification": par_budget_analysis.justification,
        "created_at": (
            par_budget_analysis.created_at.isoformat()
            if par_budget_analysis.created_at
            else None
        ),
        "updated_at": (
            par_budget_analysis.updated_at.isoformat()
            if par_budget_analysis.updated_at
            else None
        ),
    }
