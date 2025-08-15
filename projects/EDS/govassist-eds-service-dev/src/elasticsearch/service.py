import json
from typing import Any, Dict, List, Optional

from loguru import logger

from elasticsearch import AsyncElasticsearch, NotFoundError
from src.core.exceptions import InternalServerError, ValidationError
from src.elasticsearch.client import close_es_client, create_es_client
from src.elasticsearch.mappings.index_mappings import INDEX_MAPPINGS
from src.schema.report_schema import FilterGroup, SearchPayload, SortCondition


class ElasticsearchService:
    def __init__(self):
        self.client: Optional[AsyncElasticsearch] = None

    async def initialize(self) -> None:
        """Initialize the Elasticsearch client."""
        if not self.client:
            self.client = await create_es_client()

    async def cleanup(self) -> None:
        """Clean up Elasticsearch client resources."""
        if self.client:
            await close_es_client(self.client)
            self.client = None

    async def create_index(self, index_name: str) -> None:
        """Create an index with predefined mapping if it doesn't exist."""
        await self.initialize()
        try:
            if not await self.client.indices.exists(index=index_name):
                mapping = INDEX_MAPPINGS.get(index_name)
                if not mapping:
                    raise ValueError(f"No mapping found for index {index_name}")
                await self.client.indices.create(index=index_name, body=mapping)
                logger.info(f"✅ Created index {index_name}")
            else:
                logger.info(f"Index {index_name} already exists")
        except Exception:
            logger.error(f"❌ Error creating index {index_name}")
            raise InternalServerError(detail="Internal Server Error")

    async def delete_index(self, index_name: str) -> None:
        """Delete an index if it exists."""
        await self.initialize()
        try:
            if await self.client.indices.exists(index=index_name):
                await self.client.indices.delete(index=index_name)
                logger.info(f"✅ Deleted index {index_name}")
        except Exception:
            logger.error(f"❌ Error deleting index {index_name}")
            raise InternalServerError(detail="Internal Server Error")

    async def index_document(
        self, index_name: str, document: Dict[str, Any], doc_id: str
    ) -> None:
        """Index a document with the given ID."""
        await self.initialize()
        try:
            await self.client.index(index=index_name, id=doc_id, document=document)
            logger.debug(f"Indexed document {doc_id} in {index_name}")
        except Exception:
            logger.error(f"❌ Error indexing document {doc_id}")
            raise InternalServerError(detail="Internal Server Error")

    async def bulk_index_documents(
        self, index_name: str, documents: List[Dict[str, Any]]
    ) -> None:
        """Bulk index multiple documents."""
        await self.initialize()
        try:
            operations = []
            for doc in documents:
                doc_id = str(doc.get("id"))
                operations.extend(
                    [{"index": {"_index": index_name, "_id": doc_id}}, doc]
                )
            if operations:
                await self.client.bulk(operations=operations)
                logger.info(
                    f"✅ Bulk indexed {len(documents)} documents in {index_name}"
                )
        except Exception:
            logger.error("❌ Error during bulk indexing")
            raise InternalServerError(detail="Internal Server Error")

    async def get_document(
        self, index_name: str, doc_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        await self.initialize()
        try:
            result = await self.client.get(index=index_name, id=doc_id)
            return result["_source"]
        except NotFoundError:
            logger.debug(f"Document {doc_id} not found in {index_name}")
            return None
        except Exception:
            logger.error(f"❌ Error getting document {doc_id}")
            raise InternalServerError(detail="Internal Server Error")

    async def update_document(
        self, index_name: str, doc_id: str, update_fields: Dict[str, Any]
    ) -> None:
        """Update specific fields of a document."""
        await self.initialize()
        try:
            await self.client.update(index=index_name, id=doc_id, doc=update_fields)
            logger.debug(f"Updated document {doc_id} in {index_name}")
        except Exception:
            logger.error(f"❌ Error updating document {doc_id}")
            raise InternalServerError(detail="Internal Server Error")

    async def delete_document(self, index_name: str, doc_id: str) -> None:
        """Delete a document by ID."""
        await self.initialize()
        try:
            await self.client.delete(index=index_name, id=doc_id)
            logger.debug(f"Deleted document {doc_id} from {index_name}")
        except NotFoundError:
            logger.debug(f"Document {doc_id} not found in {index_name} for deletion")
        except Exception:
            logger.error(f"❌ Error deleting document {doc_id}")
            raise InternalServerError(detail="Internal Server Error")

    async def search(self, index_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a search query."""
        await self.initialize()
        try:
            result = await self.client.search(index=index_name, body=query)
            return result
        except Exception:
            logger.error(f"❌ Error performing search in {index_name}")
            raise InternalServerError(detail="Internal Server Error")

    def _get_field_type(self, mapping: dict, field: str) -> str:
        """
        Walks the mapping to get the type of the field.
        Returns the type as a string, or None if not found.
        """
        # Handle .keyword fields specially
        if field.endswith(".keyword"):
            return "keyword"

        parts = field.split(".")
        current = mapping.get("properties", {})
        for part in parts:
            if part in current:
                if "type" in current[part]:
                    field_type = current[part]["type"]
                else:
                    field_type = None
                current = current[part].get("properties", {})
            else:
                return None
        return field_type

    async def get_unique_values(
        self,
        index: str,
        field: str,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        order: str = "asc",
    ) -> Dict[str, Any]:
        """
        Get unique values from a field using Elasticsearch terms aggregation.
        Supports all data types and dynamically determines the correct nested path and search filter.
        """
        await self.initialize()
        mapping = await self.client.indices.get_mapping(index=index)
        mapping_info = mapping[index]["mappings"]
        field_type = self._get_field_type(mapping_info, field)
        nested_path = self._find_nested_path(mapping_info, field)

        # Try different approaches for handling the field
        approaches = []
        if nested_path:
            approaches.append(
                lambda *args, **kwargs: self._try_nested_aggregation(
                    *args,
                    **kwargs,
                    nested_path=nested_path,
                    field_type=field_type,
                    mapping_info=mapping_info,
                )
            )
            approaches.append(
                lambda *args, **kwargs: self._try_nested_keyword_aggregation(
                    *args,
                    **kwargs,
                    nested_path=nested_path,
                    field_type=field_type,
                    mapping_info=mapping_info,
                )
            )
        approaches.append(
            lambda *args, **kwargs: self._try_regular_aggregation(
                *args, **kwargs, field_type=field_type, mapping_info=mapping_info
            )
        )
        approaches.append(
            lambda *args, **kwargs: self._try_keyword_aggregation(
                *args, **kwargs, field_type=field_type, mapping_info=mapping_info
            )
        )

        last_error = None
        for approach in approaches:
            try:
                result = await approach(index, field, page, size, search, order)
                return result
            except Exception as e:
                last_error = e
                continue

        error_msg = str(last_error) if last_error else "Unknown error"
        if "fielddata is disabled" in error_msg.lower():
            raise ValidationError(
                f"Field '{field}' is a text field and cannot be used for aggregations. "
                f"Please use the keyword version '{field}.keyword' or ensure the field is mapped as keyword type."
            )
        elif "index_not_found_exception" in error_msg:
            raise ValidationError("Index not found")
        elif "field_not_found_exception" in error_msg:
            raise ValidationError("Field not found")
        else:
            raise ValidationError("Failed to retrieve unique values")

    def _build_search_filter(self, field: str, field_type: str, search: str) -> dict:
        if not search or not search.strip():
            return None
        search = search.strip()
        if field_type == "text":
            return {
                "match_phrase_prefix": {field: {"query": search, "max_expansions": 50}}
            }
        elif field_type == "keyword":
            return {
                "bool": {
                    "should": [
                        {
                            "wildcard": {
                                field: {
                                    "value": f"*{search}*",
                                    "case_insensitive": True,
                                }
                            }
                        }
                    ]
                }
            }
        elif field_type in ("long", "integer", "float", "double", "date", "boolean"):
            try:
                if field_type in ("long", "integer"):
                    value = int(search)
                elif field_type in ("float", "double"):
                    value = float(search)
                elif field_type == "boolean":
                    value = search.lower() in ("true", "1", "yes")
                elif field_type == "date":
                    value = search
                else:
                    value = search
                return {"term": {field: value}}
            except Exception:
                return {"prefix": {field: search}}
        else:
            return {"term": {field: search}}

    async def _try_regular_aggregation(
        self,
        index: str,
        field: str,
        page: int,
        size: int,
        search: Optional[str],
        order: str,
        field_type: str,
        mapping_info: dict,
    ) -> Dict[str, Any]:
        query = {
            "size": 0,
            "aggs": {
                "unique_values": {
                    "terms": {"field": field, "size": 10000, "order": {"_key": order}}
                }
            },
        }
        search_filter = self._build_search_filter(field, field_type, search)
        if search_filter:
            query["query"] = search_filter
        logger.info(f"ES Query (regular): {json.dumps(query, indent=2)}")
        result = await self.client.search(index=index, body=query)
        buckets = result["aggregations"]["unique_values"]["buckets"]
        all_values = [str(bucket["key"]) for bucket in buckets]
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_values = all_values[start_idx:end_idx]
        return {"values": paginated_values, "total": len(all_values)}

    async def _try_keyword_aggregation(
        self,
        index: str,
        field: str,
        page: int,
        size: int,
        search: Optional[str],
        order: str,
        field_type: str,
        mapping_info: dict,
    ) -> Dict[str, Any]:
        keyword_field = field if field.endswith(".keyword") else f"{field}.keyword"
        query = {
            "size": 0,
            "aggs": {
                "unique_values": {
                    "terms": {
                        "field": keyword_field,
                        "size": 10000,
                        "order": {"_key": order},
                    }
                }
            },
        }
        search_filter = self._build_search_filter(keyword_field, field_type, search)
        if search_filter:
            query["query"] = search_filter
        logger.info(f"ES Query (keyword): {json.dumps(query, indent=2)}")
        result = await self.client.search(index=index, body=query)
        buckets = result["aggregations"]["unique_values"]["buckets"]
        all_values = [str(bucket["key"]) for bucket in buckets]
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_values = all_values[start_idx:end_idx]
        return {"values": paginated_values, "total": len(all_values)}

    async def _try_nested_aggregation(
        self,
        index: str,
        field: str,
        page: int,
        size: int,
        search: Optional[str],
        order: str,
        nested_path: str,
        field_type: str,
        mapping_info: dict,
    ) -> Dict[str, Any]:
        search_filter = self._build_search_filter(field, field_type, search)
        if search_filter:
            query = {
                "size": 0,
                "aggs": {
                    "nested_agg": {
                        "nested": {"path": nested_path},
                        "aggs": {
                            "filtered_values": {
                                "filter": search_filter,
                                "aggs": {
                                    "unique_values": {
                                        "terms": {
                                            "field": field,
                                            "size": 10000,
                                            "order": {"_key": order},
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
            }
            logger.info(f"ES Query (nested): {json.dumps(query, indent=2)}")
            result = await self.client.search(index=index, body=query)
            buckets = result["aggregations"]["nested_agg"]["filtered_values"][
                "unique_values"
            ]["buckets"]
        else:
            query = {
                "size": 0,
                "aggs": {
                    "nested_agg": {
                        "nested": {"path": nested_path},
                        "aggs": {
                            "unique_values": {
                                "terms": {
                                    "field": field,
                                    "size": 10000,
                                    "order": {"_key": order},
                                }
                            }
                        },
                    }
                },
            }
            logger.info(f"ES Query (nested): {json.dumps(query, indent=2)}")
            result = await self.client.search(index=index, body=query)
            buckets = result["aggregations"]["nested_agg"]["unique_values"]["buckets"]
        all_values = [str(bucket["key"]) for bucket in buckets]
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_values = all_values[start_idx:end_idx]
        return {"values": paginated_values, "total": len(all_values)}

    async def _try_nested_keyword_aggregation(
        self,
        index: str,
        field: str,
        page: int,
        size: int,
        search: Optional[str],
        order: str,
        nested_path: str,
        field_type: str,
        mapping_info: dict,
    ) -> Dict[str, Any]:
        keyword_field = f"{field}.keyword"
        search_filter = self._build_search_filter(field, field_type, search)
        if search_filter:
            query = {
                "size": 0,
                "aggs": {
                    "nested_agg": {
                        "nested": {"path": nested_path},
                        "aggs": {
                            "filtered_values": {
                                "filter": search_filter,
                                "aggs": {
                                    "unique_values": {
                                        "terms": {
                                            "field": keyword_field,
                                            "size": 10000,
                                            "order": {"_key": order},
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
            }
            logger.info(f"ES Query (nested keyword): {json.dumps(query, indent=2)}")
            result = await self.client.search(index=index, body=query)
            buckets = result["aggregations"]["nested_agg"]["filtered_values"][
                "unique_values"
            ]["buckets"]
        else:
            query = {
                "size": 0,
                "aggs": {
                    "nested_agg": {
                        "nested": {"path": nested_path},
                        "aggs": {
                            "unique_values": {
                                "terms": {
                                    "field": keyword_field,
                                    "size": 10000,
                                    "order": {"_key": order},
                                }
                            }
                        },
                    }
                },
            }
            logger.info(f"ES Query (nested keyword): {json.dumps(query, indent=2)}")
            result = await self.client.search(index=index, body=query)
            buckets = result["aggregations"]["nested_agg"]["unique_values"]["buckets"]
        all_values = [str(bucket["key"]) for bucket in buckets]
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_values = all_values[start_idx:end_idx]
        return {"values": paginated_values, "total": len(all_values)}

    async def setup_indices(self) -> None:
        """Create all indices with their mappings."""
        await self.initialize()
        try:
            for index_name in INDEX_MAPPINGS.keys():
                await self.create_index(index_name)
            logger.info("✅ All indices setup completed")
        except Exception as e:
            logger.error(f"Error setting up indices: {str(e)}")
            raise InternalServerError(detail="Internal Server Error")

    async def get_index_mapping(self, index_name: str) -> dict:
        """Get the mapping for a specific index."""
        await self.initialize()
        try:
            mapping = await self.client.indices.get_mapping(index=index_name)
            return mapping[index_name]["mappings"]
        except Exception as e:
            logger.error(f"Error getting mapping for index {index_name}: {str(e)}")
            raise InternalServerError(detail="Failed to get index mapping")

    def _find_nested_path(self, mapping: dict, field: str) -> Optional[str]:
        """
        Walks the mapping to find the correct nested path for a field.
        Returns the path up to and including the first nested type, or None if not nested.
        """
        parts = field.split(".")
        path = []
        current = mapping.get("properties", {})
        for part in parts:
            if part in current:
                path.append(part)
                if current[part].get("type") == "nested":
                    return ".".join(path)
                current = current[part].get("properties", {})
            else:
                break
        return None

    def map_operator_to_query(
        self, field: str, details: dict, index: str = None, mapping_info: dict = None
    ) -> dict:
        operator = details["operator"]

        keyword_required_operators = [
            "equals",
            "not_equals",
            "in",
            "not_in",
            "starts_with",
        ]
        if operator in keyword_required_operators and not field.endswith(".keyword"):
            if mapping_info:
                field_type = self._get_field_type(mapping_info, field)
                if field_type == "text":
                    field = f"{field}.keyword"

        if operator == "equals":
            value = details["value"]
            return {"term": {field: value}}

        elif operator == "not_equals":
            value = details["value"]
            return {"bool": {"must_not": [{"term": {field: value}}]}}

        elif operator == "in":
            value = details["value"]
            return {"terms": {field: value}}

        elif operator == "not_in":
            value = details["value"]
            return {"bool": {"must_not": [{"terms": {field: value}}]}}

        elif operator == "range":
            range_query = {}
            range_query["gte"] = details["start"]
            range_query["lte"] = details["end"]

            return {"range": {field: range_query}}

        elif operator == "contains":
            value = details["value"]
            return {"wildcard": {field: f"*{value}*"}}

        elif operator == "starts_with":
            value = details["value"]
            return {"prefix": {field: value}}

        elif operator == "ends_with":
            value = details["value"]
            return {"wildcard": {field: f"*{value}"}}

        elif operator == "is_null":
            return {"bool": {"must_not": [{"exists": {"field": field}}]}}

        elif operator == "is_not_null":
            return {"exists": {"field": field}}

        else:
            raise ValueError(f"Unsupported operator: {operator}")

    def build_filter_clause(
        self, filter_payload: FilterGroup, index: str = None, mapping_info: dict = None
    ) -> dict:
        if not filter_payload:
            return {}

        if hasattr(filter_payload, "model_dump"):
            filter_payload = filter_payload.model_dump()

        operator = filter_payload["operator"].upper()
        bool_key = "must" if operator == "AND" else "should"
        conditions = []

        for condition in filter_payload["conditions"]:
            if "operator" in condition and "conditions" in condition:
                nested_clause = self.build_filter_clause(condition, index, mapping_info)
                conditions.append(nested_clause)

            elif "field" in condition and "operator" in condition:
                field = condition["field"]
                if field:
                    clause = self.map_operator_to_query(
                        field, condition, index, mapping_info
                    )
                    conditions.append(clause)

        return {"bool": {bool_key: conditions}} if conditions else {}

    def build_search_clause(
        self, search: SearchPayload, mapping_info: dict = None
    ) -> dict:
        if not search:
            return {}

        if not search.value:
            return {}

        fields = search.fields
        value = search.value

        if not fields:
            return {}

        queries = []
        for field in fields:
            # Handle keyword fields for text fields if mapping info is available
            search_field = field
            if mapping_info and not field.endswith(".keyword"):
                field_type = self._get_field_type(mapping_info, field)
                if field_type == "text":
                    search_field = f"{field}.keyword"

            queries.append({"wildcard": {search_field: f"*{value}*"}})

        return {"bool": {"should": queries, "minimum_should_match": 1}}

    def build_sort_clause(
        self, sort: list[SortCondition], index: str = None, mapping_info: dict = None
    ) -> list:
        if not sort:
            return []

        sort_clauses = []
        for item in sort:
            field = item.field
            order = item.order.lower()

            if not field:
                continue

            if not field.endswith(".keyword"):
                if mapping_info:
                    field_type = self._get_field_type(mapping_info, field)
                    if field_type in (
                        "scaled_float",
                        "integer",
                        "float",
                        "double",
                        "keyword",
                    ):
                        sort_field = field
                    else:
                        sort_field = f"{field}.keyword"
                else:
                    sort_field = field
            else:
                sort_field = field

            sort_clauses.append({sort_field: {"order": order}})

        return sort_clauses

    def build_es_query(
        self,
        filters: dict,
        search: dict,
        sort: list,
        page: int,
        page_size: int,
        index: str = None,
    ) -> dict:
        query_clauses = []
        if search:
            query_clauses.append(search)
        if filters:
            query_clauses.append(filters)

        query = {
            "from": (page - 1) * page_size,
            "size": page_size,
        }

        # Only add query if we have search or filter clauses
        if query_clauses:
            query["query"] = {"bool": {"must": query_clauses}}
        else:
            # If no search or filter, match all documents
            query["query"] = {"match_all": {}}

        if sort:
            query["sort"] = sort
        return query

    async def es_query_executor(self, index: str, query: dict) -> dict:
        """Execute an Elasticsearch query and return the results."""
        await self.initialize()
        try:
            logger.info(
                f"Executing ES query on index {index}: {json.dumps(query, indent=2)}"
            )
            result = await self.client.search(index=index, body=query)
            logger.info(
                f"ES query executed successfully. Found {result['hits']['total']['value']} documents"
            )
            return result
        except Exception as e:
            logger.error(f"Error executing ES query: {str(e)}")
            return {}


# Create a singleton instance
es_service = ElasticsearchService()
