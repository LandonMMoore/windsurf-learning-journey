from typing import Dict, List, Set

from src.core.exceptions import ValidationError


def validate_fund_types(fund_type_map: Dict[int, Set[str]], part_rate: float) -> None:
    """Validate fund types based on part rate."""
    for fund_id, fund_types in fund_type_map.items():
        if part_rate == 100 and fund_types != {"F.A."}:
            raise ValidationError(
                detail="Fund type must have only 'F.A.' when part rate is 100%."
            )
        elif part_rate < 100 and fund_types != {"F.A.", "DC Match"}:
            raise ValidationError(
                detail="Each fund code must have one 'F.A.' and one 'DC Match'."
            )


def validate_fund_duplicates(funds: List[dict]) -> None:
    """Validate that there are no duplicate fund types for the same fund ID."""
    fund_type_counts: Dict[int, Dict[str, int]] = {}

    for fund in funds:
        fund_id = fund["fund_id"]
        fund_type = fund["fund_type"]

        if fund_id not in fund_type_counts:
            fund_type_counts[fund_id] = {}

        fund_type_counts[fund_id][fund_type] = (
            fund_type_counts[fund_id].get(fund_type, 0) + 1
        )

        if fund_type_counts[fund_id][fund_type] > 1:
            raise ValidationError(
                detail=f"Duplicate fund type '{fund_type}' found for fund ID {fund_id}"
            )


def validate_part_rate_and_splits(part_rate: float, fa: float, dc: float) -> None:
    """Validate part rate and FA/DC splits."""
    tolerance = 1e-6

    if part_rate > 100:
        raise ValidationError(detail="Part Rate can't be greater than 100%")

    if not (abs(fa + dc - 1.0) < tolerance):
        raise ValidationError(detail="FA and DC must sum up to 1.0")

    expected_fa = part_rate / 100
    expected_dc = 1 - expected_fa
    if not (abs(fa - expected_fa) < tolerance and abs(dc - expected_dc) < tolerance):
        raise ValidationError(detail="FA and DC splits are incorrect")


def validate_fund_availability(
    fund_id: int, fund_type: str, total_deduction: float, federal_fund_available: float
) -> None:
    """Validate if there are sufficient funds available."""
    if fund_type == "F.A." and total_deduction > federal_fund_available:
        raise ValidationError(
            detail=f"Insufficient FHWA funds available for fund ID: {fund_id}"
        )


def serialize_fund(fund):
    return {
        "id": fund.id,
        "federal_fund_id": fund.federal_fund_id,
        "fund_type": fund.fund_type,
        "fund_code": fund.federal_fund.fund_code,
        "ce": fund.ce,
        "construction": fund.construction,
        "feasibility_studies": fund.feasibility_studies,
        "design": fund.design,
        "rights_of_way": fund.rights_of_way,
        "equipment": fund.equipment,
        "is_requested_fund": fund.is_requested_fund,
    }
