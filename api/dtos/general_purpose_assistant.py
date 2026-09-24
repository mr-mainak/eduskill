from pydantic import BaseModel, Field


class GeneralPurposeAssistantInputModel(BaseModel):
    query: str = Field(..., description="Question from the user")
    project_id: str = Field(..., description="Specified project id")
    