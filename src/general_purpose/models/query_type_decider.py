from typing import Literal
from pydantic import BaseModel, Field


class QueryType(BaseModel):
    next_agent: Literal["semantic_search_agent", "normal_llm_agent"] = Field(..., description="Next agent decided by the query verifier agent")