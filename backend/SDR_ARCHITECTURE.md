# SDR Agent Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Frontend - Voice/Text)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LiveKit Room                               │
│                  (Real-time Communication)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Session                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     STT      │  │     LLM      │  │     TTS      │         │
│  │  (Deepgram)  │  │   (Gemini)   │  │    (Murf)    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        SDR Agent                                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Agent Instructions                       │ │
│  │  - Warm, professional SDR personality                     │ │
│  │  - Consultative approach                                  │ │
│  │  - Natural conversation flow                              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Function Tools                           │ │
│  │  • answer_company_question()                              │ │
│  │  • get_company_overview()                                 │ │
│  │  • record_lead_name()                                     │ │
│  │  • record_lead_company()                                  │ │
│  │  • record_lead_email()                                    │ │
│  │  • record_lead_role()                                     │ │
│  │  • record_use_case()                                      │ │
│  │  • record_team_size()                                     │ │
│  │  • record_timeline()                                      │ │
│  │  • check_lead_completeness()                              │ │
│  │  • complete_call_and_save_lead()                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │   LeadState      │         │   CompanyFAQ     │            │
│  │                  │         │                  │            │
│  │  • name          │         │  • company_info  │            │
│  │  • company       │         │  • products      │            │
│  │  • email         │         │  • faq_items     │            │
│  │  • role          │         │  • use_cases     │            │
│  │  • use_case      │         │                  │            │
│  │  • team_size     │         │  Methods:        │            │
│  │  • timeline      │         │  • search_faq()  │            │
│  │  • questions[]   │         │  • get_overview()│            │
│  │                  │         │                  │            │
│  └──────────────────┘         └──────────────────┘            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Storage                               │
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │  sdr_company_faq.json│         │     leads.json       │    │
│  │  (Input)             │         │     (Output)         │    │
│  │                      │         │                      │    │
│  │  • Company info      │         │  • Lead details      │    │
│  │  • Products          │         │  • Timestamp         │    │
│  │  • FAQ items         │         │  • Summary           │    │
│  │  • Use cases         │         │  • Questions asked   │    │
│  └──────────────────────┘         └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Conversation Flow

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  Agent: Warm Greeting           │
│  "Hi! I'm with Razorpay..."     │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  User: States Interest          │
│  "I need payment solution"      │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Agent: Discovery Questions     │
│  Uses: record_use_case()        │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  User: Asks Questions           │
│  "What are your fees?"          │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Agent: Answers from FAQ        │
│  Uses: answer_company_question()│
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Agent: Collects Lead Info      │
│  Uses: record_lead_*() tools    │
│  - Name                         │
│  - Email                        │
│  - Company                      │
│  - Role                         │
│  - Timeline                     │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  User: Signals End              │
│  "That's all, thanks"           │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│  Agent: Provides Summary        │
│  Uses: complete_call_and_save() │
│  - Recaps conversation          │
│  - Confirms details             │
│  - Saves to leads.json          │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│     END     │
└─────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│ User Speech  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ STT (Deepgram)   │
│ Voice → Text     │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────┐
│ LLM (Gemini)                     │
│ • Understands intent             │
│ • Decides which tool to call     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Function Tool Execution          │
│                                  │
│ If FAQ Question:                 │
│   → CompanyFAQ.search_faq()      │
│   → Return answer                │
│                                  │
│ If Lead Info:                    │
│   → LeadState.update()           │
│   → Send real-time update        │
│   → Return confirmation          │
│                                  │
│ If Call Complete:                │
│   → Generate summary             │
│   → Save to leads.json           │
│   → Return summary               │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────┐
│ TTS (Murf)       │
│ Text → Voice     │
└──────┬───────────┘
       │
       ▼
┌──────────────┐
│ User Hears   │
│ Response     │
└──────────────┘
```

## Component Interactions

### 1. FAQ Answering Flow
```
User Question
    ↓
answer_company_question(question)
    ↓
CompanyFAQ.search_faq(question)
    ↓
Keyword Matching Algorithm
    ↓
Best Match FAQ Item
    ↓
Return Answer + Follow-up
```

### 2. Lead Capture Flow
```
User Provides Info
    ↓
record_lead_*(value)
    ↓
LeadState.update(field, value)
    ↓
_send_lead_update()
    ↓
Frontend Real-time Update
    ↓
Return Confirmation
```

### 3. Call Completion Flow
```
User Signals End
    ↓
complete_call_and_save_lead()
    ↓
Check LeadState.is_complete()
    ↓
Generate Summary
    ↓
Save to leads.json
    ↓
Send completion notification
    ↓
Return Verbal Summary
```

## State Management

```
┌─────────────────────────────────────┐
│          LeadState                  │
├─────────────────────────────────────┤
│ Fields:                             │
│  • name: Optional[str]              │
│  • company: Optional[str]           │
│  • email: Optional[str]             │
│  • role: Optional[str]              │
│  • use_case: Optional[str]          │
│  • team_size: Optional[str]         │
│  • timeline: Optional[str]          │
│  • questions_asked: List[str]       │
│  • conversation_summary: str        │
│  • call_complete: bool              │
├─────────────────────────────────────┤
│ Methods:                            │
│  • to_dict() → Dict                 │
│  • is_complete() → bool             │
│  • get_missing_fields() → List[str] │
└─────────────────────────────────────┘
```

## FAQ Search Algorithm

```
Input: User Question
    ↓
Convert to lowercase
    ↓
For each FAQ item:
    ↓
    Score = 0
    ↓
    For each keyword in FAQ:
        If keyword in question:
            Score += 2
    ↓
    For each word in FAQ question:
        If word (>3 chars) in user question:
            Score += 1
    ↓
    Track best match
    ↓
Return FAQ item with highest score
(or None if score = 0)
```

## Real-time Updates

```
┌─────────────────────────────────────┐
│     Data Channel: "sdr_session"     │
├─────────────────────────────────────┤
│                                     │
│  Update Type: "lead_update"         │
│  {                                  │
│    "type": "lead_update",           │
│    "data": {                        │
│      "name": "...",                 │
│      "email": "...",                │
│      ...                            │
│    }                                │
│  }                                  │
│                                     │
│  Update Type: "call_complete"       │
│  {                                  │
│    "type": "call_complete",         │
│    "data": {                        │
│      ... full lead data ...         │
│      "timestamp": "...",            │
│      "questions_count": N           │
│    }                                │
│  }                                  │
└─────────────────────────────────────┘
```

## Error Handling

```
Try:
    Execute function tool
    Update state
    Save data
    Return success message
Except Exception as e:
    Log error
    Return graceful fallback message
    Continue conversation
```

## Testing Architecture

```
┌─────────────────────────────────────┐
│      test_sdr_agent.py              │
├─────────────────────────────────────┤
│                                     │
│  TestLeadState                      │
│    • Initialization                 │
│    • Completeness validation        │
│    • Dictionary conversion          │
│                                     │
│  TestCompanyFAQ                     │
│    • Data loading                   │
│    • FAQ search                     │
│    • Company overview               │
│                                     │
│  TestSDRAgent                       │
│    • Agent initialization           │
│    • Lead recording                 │
│    • Timeline normalization         │
│    • Question answering             │
│    • Completeness checking          │
│                                     │
│  Result: 15/15 tests passing ✅     │
└─────────────────────────────────────┘
```
