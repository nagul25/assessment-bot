from pydantic import BaseModel, Field

class QueryPromptRequest(BaseModel):
    prompt: str = Field(..., description="The prompt text submitted by the user")
    