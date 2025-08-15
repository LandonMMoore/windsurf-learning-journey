import re
from typing import Callable, Optional, Union

from pydantic import validator

# Regex patterns
REGEX_NOT_ONLY_SPACES_WITH_TRIM = r"^(?!\s*$).+"  # Not empty or only whitespace
REGEX_PROJECT_ALPHANUMERICAL_NAME = r"^[A-Za-z0-9\-_.&()]+( +[A-Za-z0-9\-_.&()]+)*$"  # Allow only alphabets, numbers, dash, underscore with single spaces
REGEX_FUNDING_SOURCE = r"^(federal_grant|local)$"
REGEX_ALPHANUMERICAL_WITH_SPACES = r"^[A-Za-z0-9_-]+( +[A-Za-z0-9_-]+)*$"
REGEX_DAILY_FOLDER_NAME = r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-DAILY$"
REGEX_WEEKLY_FOLDER_NAME = r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-WEEKLY$"


def create_string_validator(field: str, condition: Callable[[str], bool], message: str):
    def _validator(cls, v):
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError(f"{field} must be a string")
        if not condition(v):
            raise ValueError(f"{field} {message}")
        return v

    return validator(field)(_validator)


def create_regex_validator(field: str, pattern: str, message: str):
    regex = re.compile(pattern)
    return create_string_validator(field, lambda v: bool(regex.fullmatch(v)), message)


def not_only_spaces_validator(
    message: str = "must not be empty or whitespace only",
) -> Callable:
    def _validator(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError("Value must be a string")
        if not re.fullmatch(REGEX_NOT_ONLY_SPACES_WITH_TRIM, v):
            raise ValueError(message)
        return v.strip()

    return _validator


# ---------- Number Field Validator (budget fields) ----------
def non_negative_number_validator(
    message: str = "must be a non-negative number",
) -> Callable:
    def _validator(cls, v: Optional[Union[int, float]]) -> Optional[Union[int, float]]:
        if v is None:
            return v
        if not isinstance(v, (int, float)):
            raise ValueError("Value must be a number")
        if v < 0:
            raise ValueError(message)
        return v

    return _validator


def validate_name_with_alphanumerical(
    field,
    message=" must contain only letters, numbers, dashes (-), and underscores (_) with single spaces between words",
):
    """
    Validates that the field contains only letters, numbers, dashes, and underscores,
    with single spaces between words.
    Returns None if the value is None.

    Args:
        field (str): The field name to be validated.
        message (str, optional): The error message shown when validation fails.

    Returns:
        Callable: A validator function.
    """
    return create_regex_validator(field, REGEX_PROJECT_ALPHANUMERICAL_NAME, message)


def validate_funding_source(
    field,
    message=" must be one of the following: federal_grant, local",
):
    return create_regex_validator(field, REGEX_FUNDING_SOURCE, message)


def validate_alphanumerical_with_spaces(
    field,
    message=" must contain only letters, numbers, dashes, and underscores with single spaces between words",
):
    return create_regex_validator(field, REGEX_ALPHANUMERICAL_WITH_SPACES, message)
