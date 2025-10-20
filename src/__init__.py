"""CoffeeBeans Voice Agent Package."""

__version__ = "2.0.0"
__author__ = "Your Name"

from .config import settings
from .state import ConversationState, create_initial_state
from .services import VoiceAIService, GroqService, GoogleSTTService, GoogleTTSService, TwilioService
from .handlers import CallHandler, call_handler
from .knowledge import KnowledgeBase, knowledge_base
from .prompts import PromptManager, prompt_manager
from .graph import (
    create_conversation_graph,
    supervisor_agent,
    analyze_sentiment,
    extract_interests,
    detect_objections,
    update_state_from_transcript
)

__all__ = [
    "settings",
    "ConversationState",
    "create_initial_state",
    "VoiceAIService",
    "GroqService",
    "GoogleSTTService",
    "GoogleTTSService",
    "TwilioService",
    "CallHandler",
    "call_handler",
    "KnowledgeBase",
    "knowledge_base",
    "PromptManager",
    "prompt_manager",
    "create_conversation_graph",
    "supervisor_agent",
    "analyze_sentiment",
    "extract_interests",
    "detect_objections",
    "update_state_from_transcript",
]