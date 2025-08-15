from datetime import datetime
from typing import Any


def convert_to_dict(obj: Any) -> Any:
    """Convert SQLAlchemy model object to dictionary"""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, list):
        return [convert_to_dict(item) for item in obj]
    if hasattr(obj, "__dict__"):
        return {
            key: convert_to_dict(value)
            for key, value in obj.__dict__.items()
            if not key.startswith("_")
        }
    return str(obj)


def _format_award_associations(project_details):
    """Format award associations for Elasticsearch"""
    award_associations = []
    for assoc in project_details.par_award_associations:
        award_association = {
            "id": assoc.id,
            "uuid": str(assoc.uuid),
            "created_at": (assoc.created_at.isoformat() if assoc.created_at else None),
            "updated_at": (assoc.updated_at.isoformat() if assoc.updated_at else None),
            "project_details_id": assoc.project_details_id,
            "award_type_id": assoc.award_type_id,
            "award_type": (
                {
                    "id": assoc.award_type.id,
                    "uuid": str(assoc.award_type.uuid),
                    "created_at": (
                        assoc.award_type.created_at.isoformat()
                        if assoc.award_type.created_at
                        else None
                    ),
                    "updated_at": (
                        assoc.award_type.updated_at.isoformat()
                        if assoc.award_type.updated_at
                        else None
                    ),
                    "code": assoc.award_type.code,
                    "description": assoc.award_type.description,
                }
                if assoc.award_type
                else None
            ),
        }
        award_associations.append(award_association)
    return award_associations


def _prepare_project_details_data(project_details):
    """Prepare project details data for Elasticsearch"""
    return {
        "project_name": project_details.project_name,
        "project_number": project_details.project_number,
        "award_id": project_details.award_id,
        "cost_center_id": project_details.cost_center_id,
        "program_code": project_details.program_code,
        "account_group": project_details.account_group,
        "project_status": project_details.project_status,
        "account_detail": project_details.account_detail,
        "project_type": project_details.project_type,
        "icrs_exempt": project_details.icrs_exempt,
        "icrs_rate": project_details.icrs_rate,
        "fhwa_program_code_id": project_details.fhwa_program_code_id,
        "fhwa_project_number_id": project_details.fhwa_project_number_id,
        "fhwa_soar_grant_id": project_details.fhwa_soar_grant_id,
        "fhwa_soar_project_no_id": project_details.fhwa_soar_project_no_id,
        "fhwa_stip_reference_id": project_details.fhwa_stip_reference_id,
        "fhwa_categories_id": project_details.fhwa_categories_id,
        "master_project_id": project_details.master_project_id,
        "eds_organization_id": project_details.eds_organization_id,
        "fund_number": project_details.fund_number,
        "funding_source": project_details.funding_source,
        "current_project_end_date": project_details.current_project_end_date,
        "request_end_date": project_details.request_end_date,
        "project_location_id": project_details.project_location_id,
        "budget_analyst": project_details.budget_analyst,
        "reason_for_extension": project_details.reason_for_extension,
        "asset_type": project_details.asset_type,
        "improvement_type": project_details.improvement_type,
        "project_manager": project_details.project_manager,
        "recipient_project_number": project_details.recipient_project_number,
        "award_type": project_details.award_type,
        "contract_number": project_details.contract_number,
        "bridge_number": project_details.bridge_number,
        "gis_route_id": project_details.gis_route_id,
        "beginning_point": project_details.beginning_point,
        "end_point": project_details.end_point,
        "fap_number": project_details.fap_number,
        "project_details_id": project_details.id,
        "award": convert_to_dict(project_details.award),
        "cost_center": convert_to_dict(project_details.cost_center),
        "master_project": convert_to_dict(project_details.master_project),
        "organization": convert_to_dict(project_details.organization),
        "fhwa_categories": convert_to_dict(project_details.fhwa_categories),
        "fhwa_program_code": convert_to_dict(project_details.fhwa_program_code),
        "fhwa_project_number": convert_to_dict(project_details.fhwa_project_number),
        "fhwa_soar_grant": convert_to_dict(project_details.fhwa_soar_grant),
        "fhwa_soar_project_no": convert_to_dict(project_details.fhwa_soar_project_no),
        "fhwa_stip_reference": convert_to_dict(project_details.fhwa_stip_reference),
        "project_location": convert_to_dict(project_details.project_location),
        "award_associations": _format_award_associations(project_details),
    }
