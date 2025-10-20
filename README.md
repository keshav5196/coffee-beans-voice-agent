# CoffeeBeans Voice Agent

An AI-powered voice agent for sales conversations, built with LangGraph, Groq LLM, and Google Cloud Speech services.

## Overview

This voice agent conducts natural business conversations over phone calls, intelligently using tools to retrieve company information, match services to customer needs, and handle objections.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CALL FLOW                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Caller ←→ Twilio ←→ WebSocket ←→ FastAPI Server           │
│                           ↓                                  │
│                    Call Handler                              │
│                           ↓                                  │
│              ┌────────────┴────────────┐                    │
│              ↓                         ↓                     │
│       Audio Processing          LangGraph State             │
│       (μ-law ↔ PCM16)          Machine                     │
│              ↓                         ↓                     │
│         Google STT              Conversation                 │
│              ↓                   Orchestrator               │
│         Text Input                     ↓                     │
│              ↓                   Phase Selection            │
│         Groq LLM                       ↓                     │
│       (llama-3.3-70b)           Dynamic Prompts             │
│              ↓                         ↓                     │
│       Text Response             Knowledge Base               │
│              ↓                  (Services, Cases)            │
│         Google TTS                                           │
│              ↓                                               │
│       Audio Response                                         │
│              ↓                                               │
│         Back to Caller                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Tech Stack:**
- **LLM**: Groq (Llama 3.3 70B) with function calling
- **Speech**: Google Cloud (STT/TTS)
- **Telephony**: Twilio Media Streams
- **Framework**: FastAPI + LangGraph

### Why LangGraph?

LangGraph provides the perfect framework for building stateful, multi-turn voice agents:

**🎯 Supervisor Pattern Made Easy**
- Single supervisor node orchestrates entire conversation flow
- No complex state machine transitions - supervisor handles routing dynamically
- Built-in state management across conversation turns

**🔧 Tool Integration**
- Seamless integration with Groq's function calling API
- Tools are executed automatically when the LLM decides they're needed
- Results flow back into conversation context naturally

**📊 Conversation State Tracking**
- Maintains conversation history, sentiment, interests, and objections
- State persists across audio chunks and turns
- Easy to add custom state fields (e.g., `engagement_level`, `pain_points`)

**🔄 Flexible Flow Control**
- Dynamic phase transitions (greeting → qualification → presentation → closing)
- Conditional routing based on conversation context
- Easy to modify conversation logic without restructuring code

**Example from our implementation:**
```python
# graph.py - Simple supervisor pattern
graph = StateGraph(ConversationState)
graph.add_node("supervisor", supervisor_agent)
graph.add_edge(START, "supervisor")
graph.add_conditional_edges("supervisor", should_continue)
```

The supervisor analyzes user input, calls tools when needed (e.g., `match_service_to_need()`), and generates contextual responses - all within a single node. This is much simpler than traditional multi-node state machines.

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Google Cloud API key with Speech-to-Text and Text-to-Speech enabled
- Twilio account (free trial works)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd coffeebeans-voice-agent

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Add to `.env`:
```bash
# Groq (LLM)
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.3-70b-versatile

# Google Cloud (STT/TTS)
GOOGLE_CLOUD_API_KEY=your_google_api_key
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_TTS_VOICE=en-US-Neural2-D

# Twilio (Telephony)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
```

## Testing

### Interactive Chat (Recommended)

Test the agent via text chat without phone calls:

```bash
uv run python tests/chat_with_agent.py
```

### Jupyter Notebook

For comprehensive testing with visualizations:

```bash
uv run jupyter notebook notebooks/test_agent.ipynb
```

The notebook includes:
- Interactive chat with the agent
- Tool function testing
- Knowledge base exploration
- Sentiment/interest analysis
- Full conversation scenarios

### Component Testing

**Test Text-to-Speech:**
```bash
uv run python tests/test_tts.py
```

**Test Speech-to-Text:**
```bash
uv run python tests/test_stt.py
```

### Full Voice Pipeline (Phone Calls)

**Step 1:** Start the server
```bash
uv run python -m src.main
```

**Step 2:** Expose with ngrok (in another terminal)
```bash
ngrok http 8000
```

**Step 3:** Make a test call (in another terminal)
```bash
uv run python tests/demo.py
```

## Project Structure

```
coffeebeans-voice-agent/
├── src/
│   ├── main.py           # FastAPI server & endpoints
│   ├── handlers.py       # WebSocket call handling
│   ├── services.py       # Groq, Google Cloud, Twilio services
│   ├── graph.py          # LangGraph supervisor + tools
│   ├── state.py          # Conversation state management
│   ├── knowledge.py      # Company info & knowledge base
│   ├── prompts.py        # System prompts
│   └── config.py         # Configuration & settings
├── tests/
│   ├── chat_with_agent.py    # Interactive text chat
│   ├── test_tts.py           # TTS testing
│   ├── test_stt.py           # STT testing
│   └── demo.py               # Phone call demo
├── notebooks/
│   └── test_agent.ipynb      # Jupyter testing notebook
├── docs/
│   └── CLAUDE.md             # Claude Code guidance
└── README.md
```

## How It Works

### Supervisor Pattern

The agent uses a single supervisor node that:
1. Receives user input (transcribed speech)
2. Analyzes sentiment, interests, and objections
3. Decides whether to call tools for information
4. Generates appropriate responses
5. Continues until conversation completes

### Tool Calling

The supervisor has access to 4 tools:

| Tool | Purpose |
|------|---------|
| `get_company_info()` | Retrieve CoffeeBeans company details |
| `match_service_to_need(need)` | Match customer pain points to services |
| `get_objection_response(type)` | Handle objections (cost, timing, etc.) |
| `schedule_next_step(action)` | Close with next steps |

Tools are called automatically by the LLM via Groq's function calling API.

### Conversation Flow

1. **Greeting**: Agent introduces CoffeeBeans
2. **Qualification**: Discovers customer pain points
3. **Presentation**: Presents relevant services with case studies
4. **Objection Handling**: Addresses concerns
5. **Closing**: Schedules discovery call or sends information

The supervisor handles phase transitions dynamically based on conversation context.

## Customization

### Update Company Information

Edit `src/knowledge.py`:
- Company details
- Services and capabilities
- Case studies
- Objection responses

### Modify Agent Behavior

Edit `src/prompts.py`:
- System prompts for each phase
- Agent personality and tone
- Conversation guidelines

### Add New Tools

Edit `src/graph.py`:
1. Create tool function
2. Add to `TOOL_SCHEMAS`
3. Add to `TOOL_FUNCTIONS` mapping

## Development

### Run with Hot Reload

```bash
uv run python -m src.main
```

Server runs on `http://localhost:8000` with automatic reload on code changes.

### View API Docs

```bash
# Start server, then visit:
http://localhost:8000/docs
```

## Production Deployment

1. **Set production environment variables**
2. **Use production Twilio account** (removes trial limitations)
3. **Deploy FastAPI server** to cloud platform
4. **Configure Twilio webhook** to point to your server
5. **Set up monitoring and logging**

## Troubleshooting

**Call disconnects after Twilio message:**
- Check server logs for errors
- Verify ngrok URL is correct and accessible
- Ensure WebSocket connection established

**Agent doesn't respond:**
- Check Google Cloud API key and quotas
- Verify Groq API key is valid
- Review server logs for STT/TTS errors

**High latency:**
- Reduce audio buffer size (default: 125ms)
- Check network latency to Google/Groq APIs
- Consider using streaming STT

## License

MIT

## Support

For issues and questions, see [GitHub Issues](https://github.com/your-repo/issues).
