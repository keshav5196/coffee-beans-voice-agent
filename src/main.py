"""Main FastAPI application for CoffeeBeans Voice Agent."""

import logging
from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from .config import settings
from .handlers import call_handler
from .services import TwilioService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CoffeeBeans Voice Agent",
    description="AI-powered voice agent for customer service",
    version="0.1.0"
)

# Initialize services
twilio_service = TwilioService()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CoffeeBeans Voice Agent",
        "version": "0.1.0"
    }


@app.post("/voice")
async def voice_webhook(request: Request) -> Response:
    """
    Twilio webhook endpoint for incoming/outgoing calls.
    Returns TwiML instructions to connect call to WebSocket.
    """
    logger.info("Received call webhook from Twilio")

    # Get the host from the request (this will be the ngrok URL when accessed via ngrok)
    host = request.headers.get("host", f"{settings.host}:{settings.port}")

    # Determine protocol (ws or wss)
    # If the request came via https (ngrok), use wss
    forwarded_proto = request.headers.get("x-forwarded-proto", "http")
    ws_protocol = "wss" if forwarded_proto == "https" else "ws"

    # Create TwiML response
    response = VoiceResponse()

    # Connect to WebSocket for streaming
    connect = Connect()
    websocket_url = f"{ws_protocol}://{host}{settings.websocket_path}"
    stream = Stream(url=websocket_url)
    connect.append(stream)
    response.append(connect)

    logger.info(f"Returning TwiML to connect to WebSocket: {websocket_url}")

    return Response(
        content=str(response),
        media_type="application/xml"
    )


@app.websocket(settings.websocket_path)
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for bidirectional audio streaming.
    Bridges Twilio Media Streams with OpenAI Realtime API.
    """
    # Extract call SID from query parameters or headers
    call_sid = websocket.query_params.get("callSid", "unknown")
    logger.info(f"WebSocket connection initiated for call: {call_sid}")
    
    try:
        await call_handler.handle_call(websocket, call_sid)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@app.post("/make-call")
async def make_call(phone_number: str, callback_url: str = None) -> dict:
    """
    Endpoint to initiate an outbound call.
    
    Args:
        phone_number: The phone number to call (E.164 format)
        callback_url: Optional callback URL (e.g., your ngrok URL + /voice)
                     If not provided, will use HOST and PORT from settings
    
    Returns:
        Call SID and status
    """
    try:
        # Use provided callback URL or construct from settings
        if callback_url:
            full_callback_url = callback_url
        else:
            # Note: This will only work if your server is publicly accessible
            full_callback_url = f"https://{settings.host}:{settings.port}/voice"
            logger.warning(
                "No callback_url provided. Using settings HOST/PORT. "
                "This will fail if server is not publicly accessible!"
            )
        
        logger.info(f"Using callback URL: {full_callback_url}")
        
        # Initiate call
        call_sid = twilio_service.initiate_call(phone_number, full_callback_url)
        
        return {
            "status": "success",
            "call_sid": call_sid,
            "message": f"Call initiated to {phone_number}",
            "callback_url": full_callback_url
        }
    except Exception as e:
        logger.error(f"Failed to make call: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/call-status/{call_sid}")
async def get_call_status(call_sid: str) -> dict:
    """Get the status of a specific call."""
    try:
        status = twilio_service.get_call_status(call_sid)
        return {
            "call_sid": call_sid,
            "status": status
        }
    except Exception as e:
        logger.error(f"Failed to get call status: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting CoffeeBeans Voice Agent on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=True
    )