from fastapi import APIRouter

from app.core.dependencies import AuthDep, DbDep, EmbeddingDep, LlmDep, VectorStoreDep
from app.core.module_guard import require_module
from app.modules.chat.schemas import ChatQueryRequest, ChatQueryResponse
from app.modules.chat.service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[require_module("chat")],
)


@router.post("/query", response_model=ChatQueryResponse)
async def query_chat(
    request: ChatQueryRequest,
    current: AuthDep,
    db: DbDep,
    embedding: EmbeddingDep,
    vector_store: VectorStoreDep,
    llm: LlmDep,
) -> ChatQueryResponse:
    service = ChatService(
        db,
        embedding_provider=embedding,
        vector_store_provider=vector_store,
        llm_provider=llm,
    )
    return await service.query(
        tenant_id=current.tenant_id,
        user_id=current.user.id,
        roles=current.roles,
        request=request,
    )
