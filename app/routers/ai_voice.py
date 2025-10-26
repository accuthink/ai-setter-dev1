import json
import logging
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.persona_service import persona_manager

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telnyx", tags=["voice", "telnyx"])


@router.get("/status")
async def telnyx_status():
    """Status endpoint to verify Telnyx webhook configuration."""
    return JSONResponse({
        "status": "ready",
        "service": "AI Appointment Setter",
        "endpoints": {
            "call_control": "/telnyx/call-control",
            "ai_webhook": "/telnyx/ai",
        },
        "configuration": {
            "persona": settings.PERSONA_NAME,
            "business": settings.BUSINESS_NAME,
            "model": settings.OPENAI_MODEL,
        }
    })


@router.post("/diagnostic")
async def diagnostic_endpoint(request: Request):
    """Diagnostic endpoint to log ALL incoming requests from Telnyx.
    
    This helps debug what Telnyx is actually sending and what we're responding with.
    """
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        logger.info("=" * 80)
        logger.info("🔍 DIAGNOSTIC REQUEST RECEIVED")
        logger.info(f"Method: {request.method}")
        logger.info(f"Path: {request.url.path}")
        logger.info(f"Headers: {json.dumps(headers, indent=2)}")
        logger.info(f"Body (raw): {body.decode('utf-8')}")
        
        try:
            json_body = json.loads(body)
            logger.info(f"Body (parsed JSON): {json.dumps(json_body, indent=2)}")
        except:
            logger.info("Body is not valid JSON")
        
        logger.info("=" * 80)
        
        return JSONResponse({
            "diagnostic": "received",
            "method": request.method,
            "path": str(request.url.path),
            "body_length": len(body),
        })
    except Exception as e:
        logger.error(f"Diagnostic endpoint error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@router.post("/ai")
async def telnyx_ai_webhook(request: Request):
    """Webhook endpoint for Telnyx AI Assistant events (Custom LLM mode).

    Notes
    -----
    - In "Custom LLM" configuration, Telnyx can be set to call an LLM endpoint.
      Some setups may forward conversational turns via a webhook style callback
      that resembles OpenAI's Responses API contract. Until finalized, we accept
      the payload and return a placeholder.
    - We'll validate signatures when TELNYX_SIGNING_SECRET is provided.
    """
    try:
        payload = await request.json()
        logger.info(f"Received Telnyx AI webhook event: {payload.get('event_type', 'unknown')}")
        logger.debug(f"Telnyx payload: {json.dumps(payload, indent=2)}")
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Invalid JSON in Telnyx webhook: {exc}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}")

    # TODO: verify Telnyx signature when signing secret is present
    # signing_secret = settings.TELNYX_SIGNING_SECRET
    # if signing_secret:
    #     verify_signature(request, signing_secret)

    # For now, respond with a simple instruction.
    return JSONResponse(
        {
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": "Hi! I can help you book, reschedule, or cancel an appointment. What service do you need and when?",
                }
            ],
        }
    )


@router.post("/call-control")
async def telnyx_call_control(request: Request):
    """Webhook endpoint for Telnyx Call Control events.
    
    IMPORTANT: If you're using Telnyx AI Assistant (Custom LLM):
    - Telnyx automatically answers calls and starts the AI
    - This webhook only logs events for monitoring
    - DO NOT manually answer or start AI - it causes conflicts
    
    If NOT using AI Assistant:
    - Uncomment the manual answer logic below
    """
    try:
        event = await request.json()
    except Exception as exc:
        logger.error(f"Invalid JSON in call control webhook: {exc}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}")
    
    event_type = event.get("data", {}).get("event_type", "unknown")
    payload = event.get("data", {}).get("payload", {})
    call_control_id = payload.get("call_control_id")
    call_leg_id = payload.get("call_leg_id")
    
    logger.info(f"📞 Telnyx Event: {event_type} | Call ID: {call_control_id}")
    logger.debug(f"Full event payload: {json.dumps(event, indent=2)}")
    
    # Log important call events
    if event_type == "call.initiated":
        from_number = payload.get("from")
        to_number = payload.get("to")
        direction = payload.get("direction")
        logger.info(f"📲 New {direction} call: {from_number} → {to_number}")
        
        # ⚠️ ONLY use manual answer if AI Assistant is NOT enabled in Telnyx Portal
        # Uncomment the block below ONLY if you're NOT using AI Assistant:
        
        # logger.info(f"Manually answering call: {call_control_id}")
        # async with httpx.AsyncClient(timeout=10.0) as client:
        #     try:
        #         answer_response = await client.post(
        #             f"https://api.telnyx.com/v2/calls/{call_control_id}/actions/answer",
        #             headers={
        #                 "Authorization": f"Bearer {settings.TELNYX_API_KEY}",
        #                 "Content-Type": "application/json",
        #             },
        #         )
        #         answer_response.raise_for_status()
        #         logger.info(f"✅ Successfully answered call: {call_control_id}")
        #     except Exception as e:
        #         logger.error(f"❌ Failed to answer call: {str(e)}")
    
    elif event_type == "call.answered":
        logger.info(f"✅ Call answered: {call_control_id}")
    
    elif event_type == "call.hangup":
        hangup_cause = payload.get("hangup_cause", "unknown")
        hangup_source = payload.get("hangup_source", "unknown")
        logger.info(f"📴 Call ended: {call_control_id} | Cause: {hangup_cause} | Source: {hangup_source}")
    
    elif event_type == "call.machine.detection.ended":
        result = payload.get("result", "unknown")
        logger.info(f"🤖 Machine detection: {result}")
    
    elif event_type in ["call.ai.started", "call.ai.ready"]:
        logger.info(f"🤖 AI Assistant activated for call: {call_control_id}")
    
    elif event_type == "call.ai.ended":
        reason = payload.get("reason", "unknown")
        logger.info(f"🤖 AI Assistant ended: {call_control_id} | Reason: {reason}")
    
    elif event_type == "call.ai.error":
        error_code = payload.get("error_code", "unknown")
        error_message = payload.get("error_message", "unknown")
        logger.error(f"❌ AI Assistant error: {error_code} - {error_message}")
    
    return JSONResponse({"received": True, "event_type": event_type})


# ========================================================================
# OpenAI Chat Completions Endpoint (for Telnyx Custom LLM)
# ========================================================================

# Pydantic models for OpenAI Chat Completions API
class ChatMessage(BaseModel):
    role: str
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    name: str | None = None


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-4o-mini"
    messages: list[ChatMessage]
    tools: list[dict[str, Any]] | None = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int | None = None
    stream: bool = False


# OpenAI-compatible router for Telnyx Custom LLM
chat_router = APIRouter(prefix="/v1", tags=["openai-compatible"])

# Additional router without prefix for direct /chat/completions calls
chat_router_no_prefix = APIRouter(tags=["openai-compatible"])


# Tool definitions for appointment booking
APPOINTMENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_available_slots",
            "description": "Search for available appointment time slots based on service, date range, and optional staff preference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "service_name": {
                        "type": "string",
                        "description": "The service or treatment name (e.g., 'haircut', 'checkup', 'massage')",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start of the date range to search (YYYY-MM-DD format)",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End of the date range to search (YYYY-MM-DD format)",
                    },
                    "staff_name": {
                        "type": "string",
                        "description": "Optional: preferred staff member or provider name",
                    },
                    "time_preference": {
                        "type": "string",
                        "enum": ["morning", "afternoon", "evening", "any"],
                        "description": "Optional: preferred time of day",
                    },
                },
                "required": ["service_name", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment at a specific date and time. Always confirm details with customer before calling this.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "Customer's full name (first and last)",
                    },
                    "customer_phone": {
                        "type": "string",
                        "description": "Customer's phone number for confirmation and reminders",
                    },
                    "service_name": {
                        "type": "string",
                        "description": "The service being booked",
                    },
                    "appointment_datetime": {
                        "type": "string",
                        "description": "Date and time of appointment (ISO format: YYYY-MM-DDTHH:MM:SS)",
                    },
                    "staff_name": {
                        "type": "string",
                        "description": "Optional: name of preferred staff member",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional: any special requests or notes",
                    },
                },
                "required": ["customer_name", "customer_phone", "service_name", "appointment_datetime"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment. Requires customer phone number for verification.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_phone": {
                        "type": "string",
                        "description": "Customer's phone number to lookup appointment",
                    },
                    "appointment_datetime": {
                        "type": "string",
                        "description": "Optional: specific appointment date/time to cancel if customer has multiple",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional: reason for cancellation",
                    },
                },
                "required": ["customer_phone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_appointment",
            "description": "Reschedule an existing appointment to a new date/time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_phone": {
                        "type": "string",
                        "description": "Customer's phone number to lookup appointment",
                    },
                    "current_datetime": {
                        "type": "string",
                        "description": "Current appointment date/time (ISO format)",
                    },
                    "new_datetime": {
                        "type": "string",
                        "description": "New desired appointment date/time (ISO format)",
                    },
                },
                "required": ["customer_phone", "current_datetime", "new_datetime"],
            },
        },
    },
]


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool call and return results.

    This is a mock implementation. Replace with real business logic.
    """
    if tool_name == "find_available_slots":
        # Mock: Return some fake available slots
        service = arguments.get("service_name", "service")
        start_date = arguments.get("start_date")
        return {
            "success": True,
            "slots": [
                {"datetime": f"{start_date}T09:00:00", "staff": "Sarah"},
                {"datetime": f"{start_date}T10:30:00", "staff": "Mike"},
                {"datetime": f"{start_date}T14:00:00", "staff": "Sarah"},
            ],
            "message": f"Found 3 available slots for {service}",
        }

    if tool_name == "book_appointment":
        # Mock: Confirm booking
        customer = arguments.get("customer_name")
        dt = arguments.get("appointment_datetime")
        service = arguments.get("service_name")
        return {
            "success": True,
            "appointment_id": "APT-12345",
            "message": f"Successfully booked {service} for {customer} on {dt}",
            "confirmation_sent": True,
        }

    if tool_name == "cancel_appointment":
        phone = arguments.get("customer_phone")
        return {
            "success": True,
            "message": f"Appointment for {phone} has been cancelled",
        }

    if tool_name == "reschedule_appointment":
        new_dt = arguments.get("new_datetime")
        return {
            "success": True,
            "message": f"Appointment rescheduled to {new_dt}",
        }

    return {"success": False, "error": f"Unknown tool: {tool_name}"}


@chat_router.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint for Telnyx Custom LLM.

    This endpoint:
    1. Receives conversation messages from Telnyx
    2. Injects the configured persona as system context
    3. Forwards to OpenAI with tool definitions
    4. Returns OpenAI's response (including tool calls if any)
    5. Telnyx handles the voice orchestration

    Configuration via environment variables:
    - OPENAI_API_KEY: Your OpenAI API key
    - OPENAI_MODEL: Model to use (default: gpt-4o-mini)
    - PERSONA_NAME: Which persona to load (default, medical_clinic, salon_spa)
    - BUSINESS_NAME: Your business name for context injection
    """
    logger.info(f"🎙️ Received chat completion request for model: {request.model}")
    logger.info(f"📝 Messages count: {len(request.messages)}")
    
    # Log all messages for debugging
    for i, msg in enumerate(request.messages):
        content_preview = msg.content[:100] if msg.content else "None"
        logger.info(f"   Message {i}: role={msg.role}, content={content_preview}")
    
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not configured")
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured. Please set it in your .env file.",
        )
    
    # CRITICAL: Detect if this is the first interaction that needs a greeting
    # Telnyx sends a system message with "Use external LLM only." before the user speaks
    # We need to provide a greeting when:
    # 1. There are NO user messages at all, OR
    # 2. There's only ONE message and it's the "Use external LLM only." system message
    # 3. This is the VERY FIRST user message (no prior assistant messages in history)
    
    user_messages = [msg for msg in request.messages if msg.role == "user" and msg.content and msg.content.strip()]
    assistant_messages = [msg for msg in request.messages if msg.role == "assistant"]
    has_only_system_instruction = (
        len(request.messages) == 1 
        and request.messages[0].role == "system" 
        and "Use external LLM only" in (request.messages[0].content or "")
    )
    
    # First interaction if: no user messages, or first user message with no prior assistant responses
    is_first_interaction = (
        len(user_messages) == 0 
        or has_only_system_instruction 
        or (len(user_messages) == 1 and len(assistant_messages) == 0)
    )
    
    if is_first_interaction:
        logger.info("🎬 FIRST INTERACTION DETECTED - Prepending greeting to response")
        
        # For the very first user message, we'll process it with OpenAI 
        # but prepend the greeting to the response
        if len(user_messages) == 1 and len(assistant_messages) == 0:
            logger.info("📞 First user message detected - will add greeting before response")
            # Continue to OpenAI but we'll prepend greeting later
        else:
            # No user message yet - just send greeting
            greeting_text = (
                f"Hello! Thank you for calling {settings.BUSINESS_NAME}. "
                f"This is Jordan, your appointment scheduling assistant. "
                f"How may I help you today?"
            )
            logger.info(f"🗣️ Greeting: {greeting_text}")
            
            response = {
                "id": f"chatcmpl-{int(datetime.now().timestamp())}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": greeting_text,
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 30,
                    "total_tokens": 80,
                },
            }
            logger.info("✅ Greeting response sent successfully")
            return response

    # Load and inject persona as system message
    try:
        system_prompt = persona_manager.get_system_prompt(
            persona_name=settings.PERSONA_NAME,
            business_name=settings.BUSINESS_NAME,
            business_info={
                "current_date": datetime.now().strftime("%A, %B %d, %Y"),
                "current_time": datetime.now().strftime("%I:%M %p"),
            },
        )
        logger.debug(f"Loaded persona: {settings.PERSONA_NAME} for {settings.BUSINESS_NAME}")
    except Exception as e:
        logger.error(f"Failed to load persona: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load persona configuration: {str(e)}",
        )

    # Build messages with persona injection
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history from request
    for msg in request.messages:
        message_dict = {"role": msg.role}

        if msg.content:
            message_dict["content"] = msg.content

        if msg.tool_calls:
            message_dict["tool_calls"] = msg.tool_calls

        if msg.tool_call_id:
            message_dict["tool_call_id"] = msg.tool_call_id

        if msg.name:
            message_dict["name"] = msg.name

        messages.append(message_dict)

    # Prepare OpenAI API request
    openai_payload = {
        "model": settings.OPENAI_MODEL,
        "messages": messages,
        "tools": APPOINTMENT_TOOLS,
        "temperature": request.temperature,
    }

    if request.max_tokens:
        openai_payload["max_tokens"] = request.max_tokens

    # Call OpenAI
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"Calling OpenAI API with model: {settings.OPENAI_MODEL}")
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=openai_payload,
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"OpenAI request successful. Usage: {result.get('usage', {})}")
            
            # Validate response structure
            if not result.get("choices") or len(result["choices"]) == 0:
                logger.error(f"❌ OpenAI returned no choices: {result}")
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI returned invalid response structure (no choices)"
                )
            
            # Get response content and validate
            choice = result["choices"][0]
            message = choice.get("message", {})
            response_content = message.get("content", "")
            
            if not response_content:
                logger.warning("⚠️ OpenAI returned empty content")
                # Check if there are tool calls instead
                if message.get("tool_calls"):
                    logger.info(f"🔧 Tool calls present: {message['tool_calls']}")
                else:
                    logger.error("❌ No content and no tool calls in response")
            else:
                logger.info(f"🤖 OpenAI Response Content ({len(response_content)} chars): {response_content[:200]}...")
            
            # If this is the first user interaction, prepend greeting to the response
            if len(user_messages) == 1 and len(assistant_messages) == 0:
                logger.info("🎬 Prepending greeting to first response")
                greeting = (
                    f"Hello! Thank you for calling {settings.BUSINESS_NAME}. "
                    f"This is Jordan, your appointment scheduling assistant. "
                )
                # Get the original response content
                original_content = result["choices"][0]["message"]["content"] or ""
                # Prepend greeting
                result["choices"][0]["message"]["content"] = greeting + original_content
                logger.info(f"✅ Greeting prepended. New length: {len(result['choices'][0]['message']['content'])} chars")
            
            # Log what we're sending back to Telnyx
            final_content = result["choices"][0]["message"]["content"]
            final_length = len(final_content) if final_content else 0
            logger.info(f"📤 Sending to Telnyx ({final_length} chars): {final_content[:200]}...")
            
            # Log the full response structure for debugging
            logger.debug(f"Full response structure: {json.dumps(result, indent=2)}")
            
            return result

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"OpenAI API error ({e.response.status_code}): {error_detail}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"OpenAI API error: {error_detail}",
            )
        except httpx.TimeoutException:
            logger.error("OpenAI API timeout")
            raise HTTPException(
                status_code=504,
                detail="OpenAI API request timed out",
            )
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error calling OpenAI: {str(e)}",
            )


@chat_router_no_prefix.post("/chat/completions")
async def chat_completions_no_prefix(request: ChatCompletionRequest):
    """Alternative endpoint for /chat/completions without /v1 prefix.
    
    This handles cases where Telnyx calls /chat/completions directly
    instead of /v1/chat/completions.
    """
    return await chat_completions(request)


@chat_router.get("/models")
async def list_models():
    """OpenAI-compatible /v1/models endpoint.
    
    Returns available models in OpenAI format. Telnyx uses this to validate
    the Custom LLM configuration and check which models are available.
    """
    current_time = int(datetime.now().timestamp())
    
    return {
        "object": "list",
        "data": [
            {
                "id": settings.OPENAI_MODEL,
                "object": "model",
                "created": current_time,
                "owned_by": "openai",
                "permission": [],
                "root": settings.OPENAI_MODEL,
                "parent": None,
            },
            # Include common fallback models
            {
                "id": "gpt-4o-mini",
                "object": "model",
                "created": current_time,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-4o-mini",
                "parent": None,
            },
            {
                "id": "gpt-4o",
                "object": "model",
                "created": current_time,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-4o",
                "parent": None,
            },
            {
                "id": "gpt-4",
                "object": "model",
                "created": current_time,
                "owned_by": "openai",
                "permission": [],
                "root": "gpt-4",
                "parent": None,
            },
        ],
    }


@chat_router_no_prefix.get("/models")
async def list_models_no_prefix():
    """Alternative endpoint for /models without /v1 prefix.
    
    This handles cases where Telnyx calls /models directly
    instead of /v1/models.
    """
    return await list_models()
