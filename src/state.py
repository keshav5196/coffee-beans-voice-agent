"""State management for the voice agent conversation."""

from typing import TypedDict, Annotated, List, Dict, Optional
import operator
from datetime import datetime


class ConversationState(TypedDict):
    """State schema for tracking conversation progress."""
    
    # Conversation metadata
    call_sid: str
    start_time: datetime
    phase: str  # greeting, qualify, present, handle_objection, close
    
    # Customer information
    customer_name: Optional[str]
    customer_context: Dict[str, str]
    
    # Conversation tracking
    messages: Annotated[List[Dict[str, str]], operator.add]
    interests: List[str]
    services_discussed: List[str]
    objections_raised: List[str]
    
    # Sentiment and engagement
    sentiment: str  # positive, neutral, negative
    engagement_level: str  # high, medium, low
    
    # Next actions
    next_action: Optional[str]
    scheduled_followup: Optional[datetime]
    
    # Technical
    audio_buffer: List[bytes]
    session_id: str


def create_initial_state(call_sid: str, session_id: str) -> ConversationState:
    """Create initial conversation state for a new call."""
    return ConversationState(
        call_sid=call_sid,
        start_time=datetime.now(),
        phase="greeting",
        customer_name=None,
        customer_context={},
        messages=[],
        interests=[],
        services_discussed=[],
        objections_raised=[],
        sentiment="neutral",
        engagement_level="medium",
        next_action=None,
        scheduled_followup=None,
        audio_buffer=[],
        session_id=session_id
    )