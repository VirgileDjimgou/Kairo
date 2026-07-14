from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

from app.providers.vector_store.qdrant import QdrantVectorStoreProvider


def test_search_chunk_vectors_uses_query_points(monkeypatch) -> None:
    tenant_id = uuid4()
    captured: dict[str, object] = {}

    class FakeClient:
        def query_points(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                points=[
                    SimpleNamespace(
                        id="chunk-1",
                        score=0.91,
                        payload={"tenant_id": str(tenant_id), "document_id": "doc-1"},
                    )
                ]
            )

    provider = QdrantVectorStoreProvider()
    provider._client = FakeClient()
    provider._collection = "test_collection"

    results = provider.search_chunk_vectors(
        tenant_id=tenant_id,
        query_vector=[0.1, 0.2, 0.3],
        query_text="règlement intérieur",
        limit=4,
        hybrid=True,
    )

    assert captured["collection_name"] == "test_collection"
    assert captured["query"] == [0.1, 0.2, 0.3]
    assert captured["limit"] == 4
    assert captured["with_payload"] is True
    assert "sparse_query" not in captured
    assert results == [
        {
            "id": "chunk-1",
            "score": 0.91,
            "payload": {"tenant_id": str(tenant_id), "document_id": "doc-1"},
        }
    ]
