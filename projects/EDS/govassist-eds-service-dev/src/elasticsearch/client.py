from loguru import logger

from elasticsearch import AsyncElasticsearch
from src.core.config import configs
from src.core.exceptions import InternalServerError

# Global client instance
_es_client = None


async def create_es_client() -> AsyncElasticsearch:
    """Create and return an Elasticsearch client instance."""
    global _es_client

    if _es_client is not None:
        try:
            # Test if the existing client is still working
            await _es_client.info()
            return _es_client
        except Exception:
            # If the client is not working, close it and create a new one
            await close_es_client(_es_client)
            _es_client = None

    try:
        _es_client = AsyncElasticsearch(
            hosts=[configs.ELASTICSEARCH_URL],
            basic_auth=(
                (configs.ELASTICSEARCH_USERNAME, configs.ELASTICSEARCH_PASSWORD)
                if configs.ELASTICSEARCH_USERNAME
                else None
            ),
            verify_certs=configs.ELASTICSEARCH_VERIFY_CERTS,
            ssl_show_warn=False,
            # api_key=configs.ELASTICSEARCH_API_KEY,
            headers={
                "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
                "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8",
            },
            maxsize=25,  # Connection pool size
            timeout=30,  # Connection timeout
            retry_on_timeout=True,
            max_retries=3,
        )
        # Test connection
        await _es_client.info()
        logger.info("✅ Connected to Elasticsearch successfully")
        return _es_client
    except Exception as e:
        logger.error(f"❌ Failed to connect to Elasticsearch: {str(e)}")
        raise InternalServerError(detail="Internal Server Error")


async def close_es_client(client: AsyncElasticsearch = None) -> None:
    """Safely close the Elasticsearch client connection."""
    global _es_client

    try:
        if client is None:
            client = _es_client
        if client is not None:
            await client.close()
            if client == _es_client:
                _es_client = None
            logger.info("✅ Elasticsearch connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing Elasticsearch connection: {str(e)}")
        raise InternalServerError(detail="Internal Server Error")
