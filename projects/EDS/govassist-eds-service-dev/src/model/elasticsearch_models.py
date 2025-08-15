from typing import Any, Dict, List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from src.core.config import configs
from src.core.exceptions import InternalServerError
from src.elasticsearch.client import create_es_client
from src.model.base_model import Base

DEFAULT_INDEX = configs.ELASTICSEARCH_DEFAULT_INDEX


class ElasticsearchModel:
    def __init__(self, index_name: str = DEFAULT_INDEX):
        self.index_name = index_name
        self._client = None

    async def _get_client(self) -> AsyncElasticsearch:
        if self._client is None:
            self._client = await create_es_client()
        return self._client

    async def create(
        self, data: Dict[str, Any], refresh: bool = False, doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a document in the specified index with an auto-generated ID."""
        client = await self._get_client()
        try:
            return await client.index(
                index=self.index_name, document=data, refresh=refresh, id=doc_id
            )
        except Exception as e:
            # If we get a connection error, try to reconnect once
            if "Connection error" in str(e):
                self._client = None
                client = await self._get_client()
                return await client.index(
                    index=self.index_name, document=data, refresh=refresh
                )
            raise InternalServerError(detail="Internal Server Error")

    async def read(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Read a document from the specified index by ID."""
        client = await self._get_client()
        try:
            return await client.get(index=self.index_name, id=doc_id)
        except NotFoundError:
            return None

    async def update(self, doc_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document in the specified index by ID with the given data."""
        client = await self._get_client()
        try:
            return await client.update(index=self.index_name, id=doc_id, doc=data)
        except Exception as e:
            # If we get a connection error, try to reconnect once
            if "Connection error" in str(e):
                self._client = None
                client = await self._get_client()
                return await client.update(index=self.index_name, id=doc_id, doc=data)
            raise InternalServerError(detail="Internal Server Error")

    async def delete(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Delete a document from the specified index by ID."""
        client = await self._get_client()
        try:
            return await client.delete(index=self.index_name, id=doc_id)
        except NotFoundError:
            return None

    async def patch(self, doc_id: str, partial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Patch (partially update) a document in the specified index by ID with the given partial data."""
        client = await self._get_client()
        return await client.update(index=self.index_name, id=doc_id, doc=partial_data)

    async def search_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        client = await self._get_client()
        query = {"query": {"match": {field: value}}}
        response = await client.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]

    async def get_by_model_id(self, model_id: int) -> Optional[Dict[str, Any]]:
        client = await self._get_client()
        query = {"query": {"term": {"id": model_id}}}
        response = await client.search(index=self.index_name, body=query)
        hits = response["hits"]["hits"]
        if hits:
            hit = hits[0]
            return {"_id": hit["_id"], **hit["_source"]}
        return None

    async def update_by_model_id(
        self, model_id: int, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        doc = await self.get_by_model_id(model_id)
        if not doc:
            raise ValueError(f"Document with model ID {model_id} not found")
        return await self.update(doc["_id"], data)

    async def delete_by_model_id(self, model_id: int) -> Optional[Dict[str, Any]]:
        doc = await self.get_by_model_id(model_id)
        if not doc:
            return None
        return await self.delete(doc["_id"])

    async def update_nested_field(
        self, model_id: int, field_path: str, value: Any
    ) -> Dict[str, Any]:
        doc = await self.get_by_model_id(model_id)
        if not doc:
            raise ValueError(f"Document with model ID {model_id} not found")
        client = await self._get_client()
        script = {
            "script": {
                "source": f"ctx._source.{field_path} = params.value",
                "lang": "painless",
                "params": {"value": value},
            }
        }
        return await client.update(index=self.index_name, id=doc["_id"], body=script)

    async def update_nested_array_item(
        self, model_id: int, array_field: str, item_id: int, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        doc = await self.get_by_model_id(model_id)
        if not doc:
            raise ValueError(f"Document with model ID {model_id} not found")
        client = await self._get_client()
        script = {
            "script": {
                "source": f"""
                    for (item in ctx._source.{array_field}) {{
                        if (item.id == params.item_id) {{
                            for (entry in params.updates.entrySet()) {{
                                item[entry.getKey()] = entry.getValue();
                            }}
                        }}
                    }}
                """,
                "lang": "painless",
                "params": {"item_id": item_id, "updates": updates},
            }
        }
        return await client.update(index=self.index_name, id=doc["_id"], body=script)


class ParModel(ElasticsearchModel):
    def __init__(self):
        super().__init__(DEFAULT_INDEX)

    async def create_par(
        self, par_id: int, data: Dict[str, Any], refresh: bool = False
    ) -> Dict[str, Any]:
        """Create a new PAR document"""
        return await self.create(data, refresh=refresh, doc_id=str(par_id))

    async def get_par(self, par_id: int) -> Optional[Dict[str, Any]]:
        """Get PAR by ID"""
        return await self.get_by_model_id(par_id)

    async def update_par(self, par_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update PAR details"""
        return await self.update(str(par_id), data)

    async def patch_par(
        self, par_id: int, partial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Partially update PAR details"""
        doc = await self.get_by_model_id(par_id)
        if not doc:
            raise ValueError(f"PAR with ID {par_id} not found")
        return await self.patch(doc["_id"], partial_data)

    async def delete_par(self, par_id: int) -> Optional[Dict[str, Any]]:
        """Delete PAR"""
        return await self.delete_by_model_id(par_id)

    async def update_project_details(
        self, par_id: int, project_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        doc = await self.get_by_model_id(par_id)
        if not doc:
            raise ValueError(f"PAR with ID {par_id} not found")
        client = await self._get_client()
        update_data = {"doc": project_details}
        return await client.update(
            index=self.index_name, id=doc["_id"], body=update_data
        )

    async def extend_par(self, par_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extend/update PAR document, merging new data with existing"""
        doc = await self.get_by_model_id(par_id)
        if not doc:
            raise ValueError(f"PAR with ID {par_id} not found")

        # Merge the existing document with new data
        merged_data = {**doc, **data}
        return await self.update(doc["_id"], merged_data)

    async def update_fhwa_and_award_info(
        self, par_id: int, fhwa_data: Dict[str, Any], award_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update FHWA and award information in PAR document"""
        doc = await self.get_by_model_id(par_id)
        if not doc:
            raise ValueError(f"PAR with ID {par_id} not found")

        # Prepare the update data
        update_data = {
            "fhwa_program_code": fhwa_data,
            "fhwa_project_number": fhwa_data,
            "fhwa_soar_grant": fhwa_data,
            "fhwa_soar_project_no": fhwa_data,
            "fhwa_stip_reference": fhwa_data,
            "fhwa_categories": fhwa_data,
            "award": award_data,
            "fhwa_program_code_id": fhwa_data.get("id"),
            "fhwa_project_number_id": fhwa_data.get("id"),
            "fhwa_soar_grant_id": fhwa_data.get("id"),
            "fhwa_soar_project_no_id": fhwa_data.get("id"),
            "fhwa_stip_reference_id": fhwa_data.get("id"),
            "fhwa_categories_id": fhwa_data.get("id"),
            "award_id": award_data.get("id"),
        }

        # Update the document
        return await self.update(doc["_id"], update_data)

    async def update_award_associations(
        self, par_id: int, award_associations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        return await self.update_nested_field(
            par_id, "award_associations", award_associations
        )

    def _get_clean_model_data(self, model: Base) -> Dict[str, Any]:
        """Get model data excluding foreign key fields."""
        data = {
            column.name: getattr(model, column.name)
            for column in model.__table__.columns
            if not column.foreign_keys
        }
        return data
