from typing import List, Optional
from fastapi import UploadFile
from pydantic import BaseModel

class QueryPromptRequest(BaseModel):
    prompt: str
    