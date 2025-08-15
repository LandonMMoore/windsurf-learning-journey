from src.elasticsearch.mappings.index_mappings import PAR_INDEX_MAPPING_LLM


def format_fields_for_display(input_data: any = None) -> str:
    """Format the fields for display in the prompt"""
    fields_display = "Available Fields:\n"
    get_fields = get_available_fields()
    if get_fields.get("status") == "success":
        fields = get_fields.get("fields", {})
        simple_fields = fields.get("simple_fields", {})
        nested_fields = fields.get("nested_fields", {})

        fields_display += "\nSimple Fields:\n"
        for field_name, field_info in simple_fields.items():
            fields_display += f"- {field_name} ({field_info.get('type', 'unknown')})\n"

        fields_display += "\nNested Fields:\n"
        for field_name, field_info in nested_fields.items():
            fields_display += f"- {field_name} ({field_info.get('type', 'unknown')})\n"
            if "fields" in field_info:
                for sub_field in field_info["fields"]:
                    fields_display += f"  - {sub_field}\n"

    return fields_display


def extract_nested_fields(properties, parent_path=""):
    """
    Recursively extract fields from nested and object type mappings.

    Args:
        properties: Dictionary containing field mappings
        parent_path: String representing the parent field path

    Returns:
        Tuple of (all_fields, nested_structure) where:
        - all_fields: Dictionary of all fields with their full path as key
        - nested_structure: Dictionary representing the nested structure
    """
    all_fields = {}
    nested_structure = {}

    for field_name, field_info in properties.items():
        current_path = f"{parent_path}.{field_name}" if parent_path else field_name

        # Handle basic field info
        field_data = {
            "name": field_name,
            "type": field_info.get("type", "unknown"),
            "format": field_info.get("format"),
            "fields": field_info.get("fields"),
        }
        all_fields[current_path] = field_data

        # Handle nested or object types
        if (
            field_info.get("type") in ["nested", "object"]
            and "properties" in field_info
        ):
            sub_fields, sub_structure = extract_nested_fields(
                field_info["properties"], current_path
            )
            all_fields.update(sub_fields)

            # Add nested structure information
            nested_structure[field_name] = {
                "type": field_info["type"],
                "fields": list(sub_fields.keys()),
                "properties": sub_structure,
            }

        # Handle multi-fields (like keyword fields)
        if "fields" in field_info:
            for sub_field, sub_info in field_info["fields"].items():
                sub_path = f"{current_path}.{sub_field}"
                all_fields[sub_path] = {
                    "name": f"{field_name}.{sub_field}",
                    "type": sub_info.get("type", "unknown"),
                    "format": sub_info.get("format"),
                    "fields": None,
                }

    return all_fields, nested_structure


def get_available_fields(input_data: any = None) -> dict:
    """
    Get available fields from Elasticsearch mapping.
    Args:
        input_data: Not used, included for tool compatibility
    Returns:
        Dictionary containing available fields and their types
    """
    try:
        # Get fields directly from PAR_MAPPING
        fields = PAR_INDEX_MAPPING_LLM["par"]["mappings"]["properties"]

        # Extract all fields including nested ones
        all_fields, nested_structure = extract_nested_fields(fields)

        # Separate simple and nested fields
        simple_fields = {
            name: info
            for name, info in all_fields.items()
            if "." not in name and info["type"] not in ["nested", "object"]
        }

        return {
            "status": "success",
            "fields": {
                "simple_fields": simple_fields,
                "nested_fields": nested_structure,
            },
            "total_fields": len(all_fields),
            "field_paths": list(
                all_fields.keys()
            ),  # Include all field paths for reference
        }
    except Exception:
        return {"status": "error", "error": "Failed to get available fields"}
