from typing import Dict, List, Optional, Union

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from src.core.exceptions import (
    AuthError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
)
from src.elasticsearch.constants import AggregationType, ChartType, FieldType
from src.elasticsearch.models import ChartConfig, ChartFieldConfig, ChartFieldsResponse
from src.schema.widget_config_schema import IndexType
from src.services.widget_config_service import (
    get_available_chart_fields_data,
    get_chart_config_data,
    get_field_aggregations_data,
    get_field_config_data,
    get_field_stats_data,
    get_field_values_data,
    get_fields_by_data_types_data,
)

# ================ API Router ================

router = APIRouter(prefix="/widgets-config", tags=["Widgets Configuration"])

# ========== Core Chart Configuration Endpoints ==========


@router.get("/types", response_model=List[ChartType])
async def get_chart_types():
    """Get all available chart types"""
    return list(ChartType)


@router.get("/config/{chart_type}", response_model=ChartConfig)
async def get_chart_config(chart_type: ChartType, index_name: IndexType) -> ChartConfig:
    """Get configuration options for a specific chart type"""
    try:
        return await get_chart_config_data(chart_type, index_name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Chart config not found")
    except Exception as e:
        logger.error(f"Error getting chart config: {str(e)}")
        raise InternalServerError(detail="Error fetching chart config")


@router.get(
    "/chart-fields/{chart_type}",
    response_model=ChartFieldsResponse,
    summary="Get available fields for a chart type",
)
async def get_available_chart_fields(
    chart_type: ChartType,
    index_name: IndexType = Query(..., description="Name of the Elasticsearch index"),
) -> ChartFieldsResponse:
    """Get available fields for different components of a chart type"""
    try:
        return await get_available_chart_fields_data(chart_type, index_name)
    except Exception as e:
        logger.error(f"Error getting available chart fields: {str(e)}")
        raise InternalServerError(detail="Error fetching available chart fields")


@router.get("/fields-by-data-types", response_model=Dict[FieldType, List[str]])
async def get_fields_by_data_types(
    index_name: IndexType,
    data_types: List[FieldType] = Query(
        None, description="List of data types to filter fields by"
    ),
) -> Dict[FieldType, List[str]]:
    """Get fields from an index filtered by specific data types"""
    try:
        return await get_fields_by_data_types_data(index_name, data_types)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Field not found")
    except Exception as e:
        logger.error(f"Error getting fields by data types: {str(e)}")
        raise InternalServerError(detail="Error fetching fields by data types")


@router.get("/field-config/{field_name}", response_model=ChartFieldConfig)
async def get_field_config(field_name: str, index_name: IndexType) -> ChartFieldConfig:
    """Get configuration and metadata for a specific field"""
    try:
        return await get_field_config_data(field_name, index_name)
    except ValueError as e:
        if "not approved" in str(e):
            raise HTTPException(status_code=403, detail="Field not approved")
        raise HTTPException(status_code=404, detail="Field not found")
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Field {field_name} not found")
    except Exception as e:
        logger.error(f"Error getting field config: {str(e)}")
        raise InternalServerError(detail="Error fetching field config")


@router.get("/field-aggregations/{field_type}", response_model=List[AggregationType])
async def get_field_aggregations(
    field_type: FieldType,
) -> List[AggregationType]:
    """Get available aggregations for a field type"""
    try:
        return await get_field_aggregations_data(field_type)
    except BadRequestError:
        raise
    except Exception:
        logger.error("Error getting field aggregations")
        raise InternalServerError(detail="Error fetching field aggregations")


@router.get(
    "/field-values/{field_name}", response_model=List[Union[str, int, float, bool]]
)
async def get_field_values_endpoint(
    field_name: str, index_name: IndexType, limit: Optional[int] = 100
) -> List[Union[str, int, float, bool]]:
    """Get possible values for a field with optional limit"""
    try:
        return await get_field_values_data(field_name, index_name, limit)
    except Exception:
        raise InternalServerError(detail="Error fetching field values")


@router.get(
    "/field-stats/{field_name}",
    response_model=Dict[str, Union[int, float, str, List[Union[int, float, str]]]],
)
async def get_field_stats_endpoint(field_name: str, index_name: IndexType):
    """Get statistical information about a field"""
    try:
        return await get_field_stats_data(field_name, index_name)
    except ValueError as e:
        if "not approved" in str(e):
            raise AuthError(detail="Field not approved")
        raise NotFoundError(detail="Field not found")
    except Exception:
        raise InternalServerError(detail="Error fetching field stats")
