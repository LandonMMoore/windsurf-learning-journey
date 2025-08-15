from elasticsearch import Elasticsearch
from src.core.config import configs

es_client = Elasticsearch(
    hosts=[configs.ELASTICSEARCH_URL],
    basic_auth=(configs.ELASTICSEARCH_USERNAME, configs.ELASTICSEARCH_PASSWORD),
    verify_certs=configs.ELASTICSEARCH_VERIFY_CERTS,
    ssl_show_warn=False,
)


def es_query_tool(query_input: any) -> dict:
    """
    Execute an Elasticsearch query and return the results.

    Args:
        query_input: ESQuery object containing the Elasticsearch query
        Example:
        {
            "query": {
                "size": 100,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "nested": {
                                    "path": "budget_info",
                                    "query": {
                                        "match_all": {}
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }

    Returns:
        Dictionary containing the results of the Elasticsearch query
    """
    try:
        # Extract the query from the input
        query = query_input

        # Execute search with the full query body
        resp = es_client.search(index=configs.ELASTICSEARCH_DEFAULT_INDEX, body=query)

        # Convert response to dictionary and extract hits
        hits = resp.get("hits", {}).get("hits", [])

        return {"status": "success", "data": [hit["_source"] for hit in hits]}
    except Exception:
        return {"status": "error", "error": "Internal Server Error"}
