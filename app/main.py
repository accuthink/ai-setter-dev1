import logging
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers.ai_voice import chat_router, chat_router_no_prefix, router as telnyx_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Appointment Setter")


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with detailed logging."""
    logger.error(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": str(exc.body) if hasattr(exc, "body") else None,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unexpected errors."""
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc),
        },
    )


@app.get("/health")
async def health():
    return {"ok": True, "service": "AI Appointment Setter"}


# Log all incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming HTTP requests with detailed information."""
    start_time = datetime.now()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    
    # Log request body for important endpoints
    if request.url.path in ["/chat/completions", "/v1/chat/completions"]:
        try:
            body = await request.body()
            logger.debug(f"Request body: {body[:500].decode() if body else 'empty'}")
            # Create a new request with the body
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive
        except Exception as e:
            logger.warning(f"Could not log request body: {e}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s")
    
    return response


# Mount routers
app.include_router(telnyx_router)
app.include_router(chat_router)
app.include_router(chat_router_no_prefix)  # Support both /chat/completions and /v1/chat/completions
