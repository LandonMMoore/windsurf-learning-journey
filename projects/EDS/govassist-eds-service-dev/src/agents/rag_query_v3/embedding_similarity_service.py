from abs_langchain_core.services import EmbeddingService
from azure.cosmos import CosmosClient
from loguru import logger

from src.core.config import configs


class EmbeddingSimilarityService:
    def __init__(self):
        self.cosmos_client = CosmosClient(
            configs.COSMOS_DB_ENDPOINT, configs.COSMOS_DB_KEY
        )
        self.db = self.cosmos_client.get_database_client(
            configs.COSMOS_DB_DATABASE_NAME
        )
        self.container = self.db.get_container_client(configs.COSMOS_DB_CONTAINER_NAME)
        self.embedding_service = EmbeddingService(
            provider="openai",
            model_name="text-embedding-3-small",
            api_key=configs.OPENAI_API_KEY,
        )

    async def find_similar_queries(
        self, user_query: str, top_k: int = 3, similarity_threshold: float = 0.5
    ) -> str:
        """
        Find similar queries in Cosmos DB using vector similarity search and return formatted string.
        """
        try:
            # Get embedding for the query
            query_embedding = await self.embedding_service.aembed_query(user_query)

            sql_query = """
                SELECT c.id, c.natural_language, c.es_query, c.query_type, 
                    c.index_name, c.description, c.tags, c.created_at,
                    VectorDistance(c.embedding, @queryEmbedding) as similarity_score
                FROM c
                WHERE IS_ARRAY(c.embedding) = true
                ORDER BY VectorDistance(c.embedding, @queryEmbedding)
                OFFSET 0 LIMIT @topK
            """

            parameters = [
                {"name": "@queryEmbedding", "value": query_embedding},
                {"name": "@topK", "value": top_k},
            ]

            results = list(
                self.container.query_items(
                    query={"query": sql_query, "parameters": parameters},
                    enable_cross_partition_query=True,
                )
            )

            if not results:
                return ""

            # Filter and format in one loop
            examples = []
            for item in results:
                distance = item.get("similarity_score", 1.0)
                similarity = max(0.0, 1.0 - distance)
                if similarity >= similarity_threshold:
                    example = f"""
                    Example:
                    - user_prompt: "{item.get('natural_language', 'N/A')}"
                    - index_name: {item.get('index_name', 'N/A')}
                    - es_query: {item.get('es_query', {})}
                    - description: {item.get('description', 'N/A')}
                    """
                    examples.append(example)

            if not examples:
                return ""

            return f"""
            ### SIMILAR QUERY EXAMPLES
            Here are similar examples:
            {''.join(examples)}
            Use these examples as reference for generating your Elasticsearch query, but adapt them to your specific requirements.
            """

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return ""
