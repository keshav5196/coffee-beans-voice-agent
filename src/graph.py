"""LangGraph implementation for conversation orchestration - Supervisor Pattern.

Supervisor agent with function calling to dynamically route conversation.
"""

import logging
from typing import Dict, Any, Literal, List
from langgraph.graph import StateGraph, END
from .state import ConversationState
from .knowledge import knowledge_base

logger = logging.getLogger(__name__)


# ============================================================================
# TOOL/FUNCTION DEFINITIONS FOR SUPERVISOR
# ============================================================================

# Tool schemas for Groq function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_company_info",
            "description": "Get information about CoffeeBeans company, services, and capabilities. Use this when customer asks about the company or what CoffeeBeans does.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "match_service_to_need",
            "description": "Match customer's pain point or business need to the most relevant CoffeeBeans service. Use this when customer mentions challenges, problems, or technology needs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_need": {
                        "type": "string",
                        "description": "Description of the customer's pain point or need (e.g., 'AI deployment issues', 'data quality problems')"
                    }
                },
                "required": ["customer_need"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_objection_response",
            "description": "Get a framework for handling customer objections professionally. Use when customer raises concerns about cost, timing, having internal team, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "objection_type": {
                        "type": "string",
                        "description": "Type of objection (e.g., 'cost', 'timing', 'internal_team', 'need_info', 'competitor')"
                    }
                },
                "required": ["objection_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_next_step",
            "description": "Handle scheduling or next steps with the customer to close the conversation. Use when customer is ready to move forward or wants more information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["schedule_call", "send_info", "callback", "not_interested"],
                        "description": "Type of next step to take"
                    },
                    "customer_email": {
                        "type": "string",
                        "description": "Customer's email address if sending information (optional)"
                    }
                },
                "required": ["action"]
            }
        }
    }
]


def get_company_info() -> Dict[str, Any]:
    """
    Get information about CoffeeBeans company.
    Use this when customer asks about the company, services, or capabilities.
    """
    return {
        "company": knowledge_base.company_info,
        "services_overview": {k: v["name"] for k, v in knowledge_base.services.items()},
        "elevator_pitch": knowledge_base.get_elevator_pitch("short")
    }


def match_service_to_need(customer_need: str) -> Dict[str, Any]:
    """
    Match customer's pain point or need to relevant CoffeeBeans service.
    
    Args:
        customer_need: Description of what customer needs (e.g., "AI deployment issues")
    
    Returns:
        Matched service details with talking points
    """
    service_key = knowledge_base.match_service_to_pain_point(customer_need)
    service_info = knowledge_base.get_service_talking_points(service_key)
    
    return {
        "matched_service": service_key,
        "service_name": service_info["name"],
        "description": service_info["description"],
        "benefits": service_info["key_benefits"][:3],
        "case_studies": service_info["relevant_cases"][:1]
    }


def get_objection_response(objection_type: str) -> Dict[str, str]:
    """
    Get framework for handling customer objection.
    
    Args:
        objection_type: Type of objection (cost, timing, internal_team, need_info, competitor)
    
    Returns:
        Response framework and key points
    """
    objection_map = {
        "cost": "too_expensive",
        "budget": "too_expensive",
        "expensive": "too_expensive",
        "timing": "not_right_time",
        "later": "not_right_time",
        "internal": "have_internal_team",
        "team": "have_internal_team",
        "think": "need_to_think",
        "consider": "need_to_think",
        "competitor": "working_with_competitor",
        "vendor": "working_with_competitor"
    }
    
    matched_key = None
    for key, value in objection_map.items():
        if key in objection_type.lower():
            matched_key = value
            break
    
    if not matched_key:
        matched_key = "need_to_think"
    
    objection_data = knowledge_base.objection_responses.get(matched_key, {})
    
    return {
        "response_framework": objection_data.get("response", ""),
        "key_points": objection_data.get("key_points", [])
    }


def schedule_next_step(action: str, customer_email: str = None) -> Dict[str, str]:
    """
    Handle scheduling or next steps with customer.

    Args:
        action: Type of next step (schedule_call, send_info, callback, not_interested)
        customer_email: Customer's email if providing resources

    Returns:
        Next step confirmation
    """
    actions = {
        "schedule_call": "Great! I'll have our team reach out to schedule a discovery call.",
        "send_info": f"Perfect! I'll send information to {customer_email or 'your email'}.",
        "callback": "No problem! When would be a good time to reach back out?",
        "not_interested": "I understand. Thanks for your time. Feel free to reach out if things change."
    }

    return {
        "action": action,
        "message": actions.get(action, actions["not_interested"])
    }


# Tool executor mapping
TOOL_FUNCTIONS = {
    "get_company_info": get_company_info,
    "match_service_to_need": match_service_to_need,
    "get_objection_response": get_objection_response,
    "schedule_next_step": schedule_next_step
}


def execute_tool_call(tool_name: str, arguments: dict) -> str:
    """
    Execute a tool function by name with given arguments.

    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments to pass to the tool

    Returns:
        JSON string of the tool result
    """
    import json

    try:
        if tool_name not in TOOL_FUNCTIONS:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        tool_func = TOOL_FUNCTIONS[tool_name]

        # Handle None or empty arguments
        if arguments is None or arguments == {}:
            result = tool_func()
        else:
            result = tool_func(**arguments)

        logger.info(f"Executed tool: {tool_name} with args: {arguments}")
        return json.dumps(result)

    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return json.dumps({"error": str(e)})


# ============================================================================
# SUPERVISOR AGENT NODE
# ============================================================================

def supervisor_agent(state: ConversationState) -> Dict[str, Any]:
    """
    Main supervisor agent that orchestrates the conversation.

    The supervisor has access to tools/functions and decides what to do based on context.
    """
    logger.info("Supervisor agent processing conversation state")
    
    # Build supervisor system prompt with available tools
    supervisor_prompt = """You are a professional sales agent calling on behalf of CoffeeBeans Consulting.

AVAILABLE TOOLS:
1. get_company_info() - Get CoffeeBeans company details and services
2. match_service_to_need(customer_need) - Match customer needs to our services
3. get_objection_response(objection_type) - Handle customer objections
4. schedule_next_step(action, email) - Close with next steps

YOUR ROLE:
- Have natural business conversations about CoffeeBeans services
- When customer mentions a problem/need, use match_service_to_need() to get relevant info
- When customer raises objection, use get_objection_response() to handle it
- When ready to close, use schedule_next_step() to wrap up

CONVERSATION APPROACH:
1. OPENING: Introduce yourself from CoffeeBeans, ask if they have a few minutes
2. DISCOVERY: When they share challenges, use tools to get relevant service info
3. PRESENTATION: Present CoffeeBeans solutions naturally (don't be pushy)
4. OBJECTIONS: Use objection handling tool when concerns arise
5. CLOSING: Use scheduling tool for next steps

CRITICAL RULES:
- You are SELLING CoffeeBeans services, not providing free consulting
- When customer describes a problem, connect it to what CoffeeBeans offers
- Use tools proactively when customer signals interest or objections
- Be consultative but remember you're here to secure next steps
- Keep responses concise (2-3 sentences max)

CoffeeBeans Quick Facts:
- Founded 2017, 168 employees
- Services: AI, Blockchain, Big Data, Technology Advisory
- Clients: The Quint, Ola, Salam Kisan
- Philosophy: "Beyond Features, We Deliver Value"

Now continue the conversation naturally. Use tools when appropriate."""
    
    # Update state with supervisor instructions
    return {
        **state,
        "messages": state.get("messages", []) + [{
            "role": "system",
            "content": supervisor_prompt
        }]
    }


# ============================================================================
# SIMPLE ROUTING (Supervisor makes all decisions)
# ============================================================================

def should_continue(state: ConversationState) -> Literal["supervisor", "end"]:
    """
    Simple routing: Keep going to supervisor or end conversation.
    
    Supervisor handles everything, we just check if conversation should end.
    """
    # Check for explicit end signals
    sentiment = state.get("sentiment", "neutral")
    messages = state.get("messages", [])
    
    # Count user messages
    user_messages = [m for m in messages if m.get("role") == "user"]
    
    # End conditions
    if sentiment == "negative" and len(user_messages) > 3:
        logger.info("Negative sentiment after multiple exchanges, ending")
        return "end"
    
    if state.get("next_action") == "call_ended":
        logger.info("Call ended signal received")
        return "end"
    
    # Continue conversation
    return "supervisor"


# ============================================================================
# ANALYSIS HELPERS
# ============================================================================

def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment from user text.
    
    Returns: "positive", "neutral", or "negative"
    """
    text_lower = text.lower()
    
    # Positive indicators
    positive_words = [
        "yes", "sure", "great", "sounds good", "interested", "definitely",
        "love", "perfect", "excellent", "absolutely", "looking forward",
        "want", "need", "help", "solution", "problem"
    ]
    
    # Negative indicators
    negative_words = [
        "no", "not interested", "busy", "not now", "maybe later",
        "don't need", "already have", "can't", "won't", "never"
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def extract_interests(text: str) -> list:
    """
    Extract technology interests from user text.
    
    Returns: List of identified interests/pain points
    """
    text_lower = text.lower()
    interests = []
    
    interest_keywords = {
        "ai": ["ai", "artificial intelligence", "machine learning", "ml", "predictive", "models"],
        "data": ["data quality", "data pipeline", "data warehouse", "big data", "analytics"],
        "blockchain": ["blockchain", "security", "transparency", "supply chain"],
        "cloud": ["cloud", "infrastructure", "deployment", "devops"],
        "legacy": ["legacy", "modernization", "outdated", "old system"],
        "scaling": ["scaling", "scale", "growth", "expand", "production"]
    }
    
    for interest, keywords in interest_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            interests.append(interest)
    
    return interests


def detect_objections(text: str) -> list:
    """
    Detect objections in user text.
    
    Returns: List of detected objection types
    """
    text_lower = text.lower()
    objections = []
    
    objection_patterns = {
        "cost": ["expensive", "cost", "budget", "price", "afford"],
        "timing": ["not now", "later", "timing", "not ready", "too soon"],
        "internal_team": ["internal team", "in-house", "already have"],
        "need_info": ["think about", "need to discuss", "get back to you"],
        "competitor": ["already working", "another vendor", "current partner"]
    }
    
    for objection_type, patterns in objection_patterns.items():
        if any(pattern in text_lower for pattern in patterns):
            objections.append(objection_type)
    
    return objections


def update_state_from_transcript(
    state: ConversationState,
    transcript: str,
    speaker: str = "user"
) -> ConversationState:
    """
    Update conversation state based on transcript analysis.
    
    Args:
        state: Current state
        transcript: Text to analyze
        speaker: "user" or "agent"
    
    Returns:
        Updated state
    """
    if speaker == "user":
        # Analyze user response
        sentiment = analyze_sentiment(transcript)
        interests = extract_interests(transcript)
        objections = detect_objections(transcript)
        
        # Update state
        state["sentiment"] = sentiment
        
        # Add new interests
        existing_interests = state.get("interests", [])
        state["interests"] = list(set(existing_interests + interests))
        
        # Add new objections
        existing_objections = state.get("objections_raised", [])
        state["objections_raised"] = list(set(existing_objections + objections))
        
        # Update engagement level based on response length and sentiment
        if len(transcript) > 100 and sentiment in ["positive", "neutral"]:
            state["engagement_level"] = "high"
        elif len(transcript) < 20 or sentiment == "negative":
            state["engagement_level"] = "low"
        else:
            state["engagement_level"] = "medium"
    
    return state


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================

def tool_company_info_node(state: ConversationState) -> Dict[str, Any]:
    """Tool node: Get company information."""
    info = get_company_info()
    logger.info("Tool called: get_company_info")
    return {**state, "last_tool_result": info}


def tool_match_service_node(state: ConversationState) -> Dict[str, Any]:
    """Tool node: Match service to customer need."""
    # Extract customer need from latest message
    messages = state.get("messages", [])
    customer_need = messages[-1].get("content", "") if messages else "general inquiry"
    result = match_service_to_need(customer_need)
    logger.info(f"Tool called: match_service_to_need - {result['matched_service']}")
    return {**state, "last_tool_result": result}


def tool_objection_handler_node(state: ConversationState) -> Dict[str, Any]:
    """Tool node: Handle customer objection."""
    objections = state.get("objections_raised", [])
    objection_type = objections[-1] if objections else "need_to_think"
    result = get_objection_response(objection_type)
    logger.info(f"Tool called: get_objection_response - {objection_type}")
    return {**state, "last_tool_result": result}


def tool_schedule_node(state: ConversationState) -> Dict[str, Any]:
    """Tool node: Schedule next step."""
    result = schedule_next_step("schedule_call")
    logger.info("Tool called: schedule_next_step")
    return {**state, "last_tool_result": result}


def create_conversation_graph() -> StateGraph:
    """
    Create the supervisor-based conversation graph.

    Architecture:
    - Supervisor orchestrates the conversation
    - Tools are called via Groq's function calling API (within supervisor node)
    - Graph shows simple flow: supervisor → should_continue → (supervisor or end)

    Note: Tool nodes are NOT part of the graph because tools are invoked
    via LLM function calling, not graph routing. This keeps the architecture
    simple while maintaining full tool functionality.
    """
    logger.info("Creating supervisor-based conversation graph")

    # Initialize the graph
    workflow = StateGraph(ConversationState)

    # Add supervisor node (main orchestration with embedded tool calling)
    workflow.add_node("supervisor", supervisor_agent)

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Main routing: supervisor decides whether to continue or end
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "supervisor": "supervisor",  # Continue conversation
            "end": END  # End conversation
        }
    )

    logger.info("Supervisor graph created successfully")
    logger.info("Tools available via function calling: get_company_info, match_service_to_need, get_objection_response, schedule_next_step")

    # Compile the graph
    return workflow.compile()


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "create_conversation_graph",
    "supervisor_agent",
    "analyze_sentiment",
    "extract_interests",
    "detect_objections",
    "update_state_from_transcript",
    "get_company_info",
    "match_service_to_need",
    "get_objection_response",
    "schedule_next_step",
    "TOOL_SCHEMAS",
    "TOOL_FUNCTIONS",
    "execute_tool_call"
]