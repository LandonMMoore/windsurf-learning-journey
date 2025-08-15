from src.elasticsearch.client import get_es_client

es = get_es_client()


# Counter config

COUNTER_INDEX = "id-counter"

COUNTER_DOC_ID = "next_id"


def get_next_id():
    es.update(
        index=COUNTER_INDEX,
        id=COUNTER_DOC_ID,
        body={
            "script": {"source": "ctx._source.value += 1", "lang": "painless"},
            "upsert": {"value": 1},
        },
        refresh=True,
    )
    res = es.get(index=COUNTER_INDEX, id=COUNTER_DOC_ID)

    return res["_source"]["value"]
