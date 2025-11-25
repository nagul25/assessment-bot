import time
from typing import List, Optional
from fastapi import APIRouter, Form, UploadFile
from fastapi.params import Query
from app.dummy.dummy import generate_string_with_query
from app.models.models import QueryPromptRequest
from app.services.process import QueryProcessorService

from app.log_config import logger

# logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    return {"data": {}, "message": "API is healthy", "status": 200}


@router.post("/query", tags=["Prompt"])
async def handle_query(
    query: str = Form(..., description="The prompt query string"),
    files: Optional[List[UploadFile]] = None
    ):
    try:
        # Placeholder for query handling logic
        request_data = QueryPromptRequest(prompt=query)
        query_processor = QueryProcessorService()
        response = await query_processor.process_query(request_data, files=files)
        logger.info(f"Query processed successfully: {response}")
        return {"data":response, "status":200, "message":"Query processed successfully"}
    except Exception as e:
        logger.error(f"Error in handle_query: {e}")
        return {"error": f"Failed to handle query: {e}"}
    

@router.post("/assess", tags=["Assessment"])
async def handle_assessment(prompt: str, files: Optional[List[UploadFile]] = None):
    logger.info(f"Received assessment request: {prompt}")
    try:
        request_data = QueryPromptRequest(prompt=prompt)
        logger.info(f"Assessment request received - {request_data}")
        response = await QueryProcessorService().process_assessment(request_data, files=files)
        logger.info(f"Assessment processed successfully: {response}")
        return {"data": response, "status": 200, "message": "Assessment handled successfully"}
    except Exception as e:
        logger.error(f"Error in handle_assessment: {e}")
        return {"error": f"Failed to handle assessment: {e}"}
    
@router.get("/test-sentry", tags=["Testing"])
def test_sentry_integration():
    try:
        1 / 0  # This will raise a ZeroDivisionError
    except ZeroDivisionError as e:
        logger.error("Testing Sentry integration: Division by zero error", exc_info=e)
        raise e  # Re-raise the exception to be captured by Sentry
    

@router.get("/options", tags=["Options"])
def get_options(query: str = Query(default="")):
    # Simulate network delay (optional, good for debounce testing)
    time.sleep(0.5)
    print('input query: ', query)
    if not query:
        return []

    results = [generate_string_with_query(query) for _ in range(5)]
    return results