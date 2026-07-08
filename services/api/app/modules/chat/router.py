from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.dependencies import (
    AuthDep,
    DbDep,
    EmbeddingDep,
    LlmDep,
    RerankerDep,
    VectorStoreDep,
)
from app.core.module_guard import require_module
from app.modules.chat.schemas import (
    ChatConversationCreate,
    ChatConversationDetailResponse,
    ChatConversationResponse,
    ChatConversationUpdate,
    ChatQueryRequest,
    ChatQueryResponse,
)
from app.modules.chat.service import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    dependencies=[require_module("chat")],
)


@router.post("/query-stream")
async def query_chat_stream(
    request: ChatQueryRequest,
    current: AuthDep,
    db: DbDep,
    embedding: EmbeddingDep,
    vector_store: VectorStoreDep,
    llm: LlmDep,
    reranker: RerankerDep,
) -> StreamingResponse:
    service = ChatService(
        db,
        embedding_provider=embedding,
        vector_store_provider=vector_store,
        llm_provider=llm,
        reranker_provider=reranker,
    )
    return StreamingResponse(
        service.query_stream(
            tenant_id=current.tenant_id,
            user_id=current.user.id,
            roles=current.roles,
            request=request,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/query", response_model=ChatQueryResponse)
async def query_chat(
    request: ChatQueryRequest,
    current: AuthDep,
    db: DbDep,
    embedding: EmbeddingDep,
    vector_store: VectorStoreDep,
    llm: LlmDep,
    reranker: RerankerDep,
) -> ChatQueryResponse:
    service = ChatService(
        db,
        embedding_provider=embedding,
        vector_store_provider=vector_store,
        llm_provider=llm,
        reranker_provider=reranker,
    )
    return await service.query(
        tenant_id=current.tenant_id,
        user_id=current.user.id,
        roles=current.roles,
        request=request,
    )


# --- Conversation CRUD ---


@router.get("/conversations", response_model=list[ChatConversationResponse])
async def list_conversations(
    current: AuthDep,
    db: DbDep,
) -> list[ChatConversationResponse]:
    service = ChatService(db)
    return await service.list_conversations(
        tenant_id=current.tenant_id,
        user_id=current.user.id,
    )


@router.post("/conversations", response_model=ChatConversationResponse, status_code=201)
async def create_conversation(
    request: ChatConversationCreate,
    current: AuthDep,
    db: DbDep,
) -> ChatConversationResponse:
    service = ChatService(db)
    return await service.create_conversation(
        tenant_id=current.tenant_id,
        user_id=current.user.id,
        title=request.title,
    )


@router.get("/conversations/{conversation_id}", response_model=ChatConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> ChatConversationDetailResponse:
    service = ChatService(db)
    result = await service.get_conversation(
        conversation_id=conversation_id,
        tenant_id=current.tenant_id,
        user_id=current.user.id,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router.patch("/conversations/{conversation_id}", response_model=ChatConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    request: ChatConversationUpdate,
    current: AuthDep,
    db: DbDep,
) -> ChatConversationResponse:
    service = ChatService(db)
    result = await service.update_conversation(
        conversation_id=conversation_id,
        tenant_id=current.tenant_id,
        user_id=current.user.id,
        title=request.title,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return result


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    current: AuthDep,
    db: DbDep,
) -> None:
    service = ChatService(db)
    deleted = await service.delete_conversation(
        conversation_id=conversation_id,
        tenant_id=current.tenant_id,
        user_id=current.user.id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
