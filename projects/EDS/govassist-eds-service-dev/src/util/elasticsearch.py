from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException
from loguru import logger

from src.core.exceptions import InternalServerError
from src.elasticsearch.constants import FieldType
from src.elasticsearch.service import es_service


async def get_field_mapping(index_name: str, field_name: str) -> Optional[Dict]:
    """Get field mapping from Elasticsearch"""
    try:
        if not es_service.client:
            raise HTTPException(
                status_code=503,
                detail="Elasticsearch service is not available. Please try again later.",
            )

        if not field_name:
            logger.warning("Field name is empty or None")
            return None

        # Get complete mapping and extract the specific field
        # This is compatible with Elasticsearch serverless mode
        mapping = await es_service.client.indices.get_mapping(index=index_name)

        if not mapping or index_name not in mapping:
            logger.warning(f"Index {index_name} not found in mapping response")
            raise HTTPException(status_code=404, detail=f"Index {index_name} not found")

        # Navigate through the mapping to find the field
        mappings = mapping[index_name]["mappings"]["properties"]

        # Handle nested fields
        field_path = field_name.split(".")
        current_mapping = mappings
        full_path = []

        for path_part in field_path:
            if path_part not in current_mapping:
                logger.warning(f"Field part {path_part} not found in mappings")
                return None

            current_mapping = current_mapping[path_part]
            full_path.append(path_part)

            # If we encounter a nested object with properties, go one level deeper
            if "properties" in current_mapping:
                current_mapping = current_mapping["properties"]
            # If we encounter a nested field, we need to get its properties
            elif (
                current_mapping.get("type") == "nested"
                and "properties" in current_mapping
            ):
                current_mapping = current_mapping["properties"]

        # Format the result in the same structure as get_field_mapping would return
        result = {"mapping": {field_name: current_mapping}}
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting field mapping: {str(e)}")
        return None


async def get_field_type(mapping: Dict) -> FieldType:
    """Convert Elasticsearch field type to our FieldType enum"""
    # Get the field type from the updated mapping structure
    field_name = list(mapping["mapping"].keys())[0]
    es_type = mapping["mapping"][field_name].get("type")

    type_mapping = {
        "text": FieldType.TEXT,
        "keyword": FieldType.KEYWORD,
        "long": FieldType.NUMERIC,
        "integer": FieldType.NUMERIC,
        "short": FieldType.NUMERIC,
        "byte": FieldType.NUMERIC,
        "double": FieldType.NUMERIC,
        "float": FieldType.NUMERIC,
        "half_float": FieldType.NUMERIC,
        "scaled_float": FieldType.NUMERIC,
        "date": FieldType.DATE,
        "boolean": FieldType.BOOLEAN,
    }
    return type_mapping.get(es_type, FieldType.TEXT)


async def get_index_mappings(index_name: str) -> Dict:
    """Get complete mapping for an index"""
    try:
        # Ensure the Elasticsearch service is initialized
        if not es_service.client:
            await es_service.initialize()

        if not es_service.client:
            raise HTTPException(
                status_code=503, detail="Elasticsearch service is not available"
            )

        mapping = await es_service.client.indices.get_mapping(index=index_name)
        if not mapping or index_name not in mapping:
            raise HTTPException(status_code=404, detail=f"Index {index_name} not found")

        return mapping[index_name]["mappings"]["properties"]

    except Exception as e:
        logger.error(f"Error getting index mappings: {str(e)}")
        raise InternalServerError(detail="Error retrieving index mappings")


async def categorize_fields(mappings: Dict) -> Dict[str, List[str]]:
    """Categorize fields based on their type"""
    result = {"numeric": [], "text": [], "keyword": [], "date": [], "boolean": []}

    def process_field(field_name: str, field_info: Dict, prefix: str = ""):
        es_type = field_info.get("type")
        full_field_name = f"{prefix}{field_name}" if prefix else field_name

        # Always recurse into any field with 'properties', regardless of type
        if "properties" in field_info:
            for sub_field, sub_info in field_info["properties"].items():
                process_field(sub_field, sub_info, f"{full_field_name}.")
            # If the parent is not a nested/object, don't categorize it itself
            if es_type not in ["nested", "object"]:
                return

        if es_type == "nested":
            # Already handled above
            pass
        elif es_type in [
            "long",
            "integer",
            "short",
            "byte",
            "double",
            "float",
            "scaled_float",
        ]:
            result["numeric"].append(full_field_name)
        elif es_type == "text":
            # Only add to text category if no keyword mapping exists
            if "fields" not in field_info or "keyword" not in field_info["fields"]:
                result["text"].append(full_field_name)
            # Always add the keyword version if it exists
            if "fields" in field_info and "keyword" in field_info["fields"]:
                result["keyword"].append(f"{full_field_name}.keyword")
        elif es_type == "keyword":
            result["keyword"].append(full_field_name)
        elif es_type == "date":
            result["date"].append(full_field_name)
        elif es_type == "boolean":
            result["boolean"].append(full_field_name)
        # Do not skip fields with 'object' type, just recurse into their properties
        # Do not skip fields with unknown type, just recurse if they have properties

    # Process all fields
    if "properties" in mappings:
        for field_name, field_info in mappings["properties"].items():
            process_field(field_name, field_info)
    else:
        for field_name, field_info in mappings.items():
            process_field(field_name, field_info)

    # Remove any duplicate entries
    for category in result:
        result[category] = list(dict.fromkeys(result[category]))

    return result


async def get_aggregation_field_name(
    index_name: str, field_name: str, field_mapping: Dict
) -> Union[str, Dict[str, Any]]:
    """
    Get appropriate field name for aggregation
    For text fields, this might return the .keyword variant

    Returns:
        - Field name string if successful
        - Dict with error information if field is not suitable for aggregation
    """
    field_info = field_mapping.get("mapping", {}).get(field_name, {})
    es_type = field_info.get("type")

    # For text fields, try to use .keyword if available
    if es_type == "text":
        if "fields" in field_info and "keyword" in field_info["fields"]:
            return f"{field_name}.keyword"
        else:
            # Check if fielddata is enabled
            if not field_info.get("fielddata", False):
                return {
                    "error": True,
                    "status_code": 400,
                    "message": (
                        f"Field '{field_name}' is a text field without keyword mapping. "
                        "For aggregations, either: "
                        "1. Use a keyword field instead "
                        "2. Add a keyword sub-field to this field "
                        "3. Enable fielddata (not recommended for production)"
                    ),
                }

    return field_name


async def get_field_stats_from_es(
    index_name: str, field_name: str, field_type: FieldType
) -> Dict:
    """Get field statistics from Elasticsearch"""
    try:
        # Get field mapping to check field configuration
        mapping = await get_field_mapping(index_name, field_name)
        if not mapping:
            raise HTTPException(
                status_code=404,
                detail=f"Field {field_name} not found in index {index_name}",
            )

        # Get appropriate field name for aggregation
        agg_field_name = await get_aggregation_field_name(
            index_name, field_name, mapping
        )

        # Check if get_aggregation_field_name returned an error
        if isinstance(agg_field_name, dict) and agg_field_name.get("error"):
            # For text fields without keyword, return empty stats to avoid errors
            if field_type == FieldType.TEXT:
                return {
                    "distinct_count": {"value": 0},
                    "common_values": {"buckets": []},
                    "error": agg_field_name.get(
                        "message", "Unable to aggregate text field"
                    ),
                }
            else:
                # For other field types, raise the error
                raise HTTPException(
                    status_code=agg_field_name.get("status_code", 400),
                    detail=agg_field_name.get(
                        "message", "Field not suitable for aggregation"
                    ),
                )

        # Build appropriate query based on field type
        if field_type == FieldType.NUMERIC:
            stats_query = {
                "aggs": {
                    "field_stats": {"stats": {"field": agg_field_name}},
                    "common_values": {"terms": {"field": agg_field_name, "size": 5}},
                },
                "size": 0,
            }
        elif field_type == FieldType.DATE:
            stats_query = {
                "aggs": {
                    "min_date": {"min": {"field": agg_field_name}},
                    "max_date": {"max": {"field": agg_field_name}},
                    "distinct_count": {"cardinality": {"field": agg_field_name}},
                },
                "size": 0,
            }
        else:  # TEXT or other types
            stats_query = {
                "aggs": {
                    "distinct_count": {"cardinality": {"field": agg_field_name}},
                    "common_values": {"terms": {"field": agg_field_name, "size": 5}},
                },
                "size": 0,
            }

        try:
            result = await es_service.search(index_name, stats_query)
            return result["aggregations"]
        except Exception as e:
            error_msg = str(e)
            if "fielddata is disabled" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Field '{field_name}' is not configured for aggregations. "
                        "Options: "
                        "1. Use the .keyword version of the field "
                        "2. Add a keyword mapping to the field "
                        "3. Enable fielddata (warning: high memory usage)"
                    ),
                )
            elif "field data type is unsupported" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{field_name}' type does not support the requested operation",
                )
            else:
                logger.error(f"Error getting field stats: {error_msg}")
                raise InternalServerError(detail="Error retrieving field statistics")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_field_stats_from_es: {str(e)}")
        raise InternalServerError(detail="Error retrieving field statistics")


async def get_sample_values(
    index_name: str, field_name: str, limit: int = 5
) -> List[Any]:
    """Get sample values for a field"""
    try:
        sample_query = {
            "size": limit,
            "sort": [{field_name: "desc"}],
            "_source": [field_name],
        }
        samples = await es_service.search(index_name, sample_query)

        # Extract values, handling possibly missing fields
        result = []
        for doc in samples["hits"]["hits"]:
            if field_name in doc.get("_source", {}):
                result.append(doc["_source"][field_name])

        return result

    except Exception as e:
        logger.warning(f"Failed to get sample values for {field_name}: {str(e)}")
        return []


async def build_terms_aggregation_query(field_name: str, size: int = 10) -> Dict:
    """Build a terms aggregation query for a field"""
    agg = {
        "size": 0,
        "aggs": {"values": {"terms": {"field": field_name, "size": size}}},
    }

    return agg


async def build_field_stats_query(field_name: str, field_type: str) -> Dict:
    """Build an appropriate stats query based on field type"""

    if field_type == FieldType.NUMERIC:
        return {
            "aggs": {
                "field_stats": {"stats": {"field": field_name}},
                "common_values": {"terms": {"field": field_name, "size": 5}},
            },
            "size": 0,
        }
    elif field_type == FieldType.DATE:
        return {
            "aggs": {
                "min_date": {"min": {"field": field_name}},
                "max_date": {"max": {"field": field_name}},
                "distinct_count": {"cardinality": {"field": field_name}},
            },
            "size": 0,
        }
    else:  # TEXT or other types
        return {
            "aggs": {
                "distinct_count": {"cardinality": {"field": field_name}},
                "common_values": {"terms": {"field": field_name, "size": 5}},
            },
            "size": 0,
        }


async def build_range_query(field_name: str, value, operator: str = "gte") -> Dict:
    """Build a range query for a field"""
    return {"query": {"range": {field_name: {operator: value}}}}


async def get_field_examples(
    index_name: str, field_name: str, field_type: str, limit: int = 5
) -> List[Any]:
    """Get example values for a field based on its type"""

    if field_type == FieldType.NUMERIC or field_type == FieldType.DATE:
        # For numeric and date fields, get a sample of values
        query = {"size": limit, "sort": [{field_name: "desc"}], "_source": [field_name]}
        result = await es_service.search(index_name, query)
        return [
            doc["_source"].get(field_name)
            for doc in result["hits"]["hits"]
            if field_name in doc["_source"]
        ]

    else:  # TEXT or other types
        try:
            # First check if this text field has a keyword mapping
            mapping = await get_field_mapping(index_name, field_name)
            if not mapping:
                logger.warning(f"Field {field_name} not found in mapping")
                return []

            field_info = mapping.get("mapping", {}).get(field_name, {})
            has_keyword = "fields" in field_info and "keyword" in field_info["fields"]
            has_fielddata = field_info.get("fielddata", False)

            # If it's a text field without keyword or fielddata, return empty list
            if field_type == FieldType.TEXT and not has_keyword and not has_fielddata:
                logger.warning(
                    f"Field {field_name} is a text field without keyword mapping or fielddata. Skipping aggregation."
                )
                return []

            # Use keyword field for aggregation if available
            agg_field_name = (
                f"{field_name}.keyword"
                if has_keyword and field_type == FieldType.TEXT
                else field_name
            )

            # For text fields, get the most common values
            query = await build_terms_aggregation_query(agg_field_name, limit)
            try:
                result = await es_service.search(index_name, query)
                return [
                    bucket["key"]
                    for bucket in result["aggregations"]["values"]["buckets"]
                ]
            except Exception as e:
                if (
                    "fielddata is disabled" in str(e).lower()
                    or "field data" in str(e).lower()
                ):
                    logger.warning(
                        f"Field {field_name} doesn't support aggregations: {str(e)}"
                    )
                    return []
                raise InternalServerError(detail="Internal Server Error")
        except Exception as e:
            logger.error(f"Error getting field examples for {field_name}: {str(e)}")
            return []
