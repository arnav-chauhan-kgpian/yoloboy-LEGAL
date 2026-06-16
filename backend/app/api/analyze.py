"""Analysis SSE endpoint."""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.database.neo4j_client import get_neo4j
from app.database.chroma_client import get_chroma
from app.agents.orchestrator import OrchestratorAgent
from app.schemas.analysis import AnalysisRequest

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze")
async def analyze(req: AnalysisRequest):
    neo4j = await get_neo4j()
    chroma = get_chroma()
    orchestrator = OrchestratorAgent(neo4j, chroma)

    async def event_stream():
        async for chunk in orchestrator.run(
            req.contract_id, req.query, req.framework_id
        ):
            yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
