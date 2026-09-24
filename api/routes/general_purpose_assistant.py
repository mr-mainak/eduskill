from typing import Annotated
from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from api.dtos.general_purpose_assistant import GeneralPurposeAssistantInputModel
from api.handlers.general_purpose_assistant import stream_general_purpose_assistant

general_purpose_assistant_router = APIRouter(
    prefix="/general-purpose-assistant"
)

@general_purpose_assistant_router.post("/")
async def stream_output(
    request: Request,
    query: str = Form(...),
    project_id: str = Form(...),
    image: UploadFile | None = File(None),
):
    data = GeneralPurposeAssistantInputModel(query=query,project_id=project_id,)

    return StreamingResponse(
        content=stream_general_purpose_assistant(request,data,image,),
    )