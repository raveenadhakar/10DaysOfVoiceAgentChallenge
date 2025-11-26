# SDR Agent - Sales Development Representative

## Overview
The SDR Agent is a voice-powered Sales Development Representative for Razorpay, India's leading payment gateway. It conducts natural conversations with prospects, answers questions using an FAQ knowledge base, and captures lead information.

## Features

### 1. Company FAQ System
- **Knowledge Base**: Loaded from `shared-data/sdr_company_faq.json`
- **Smart Search**: Keyword-based FAQ matching
- **Company Info**: Razorpay products, pricing, features, and use cases
- **Accurate Answers**: Only provides information from the FAQ, doesn't make up details

### 2. Lead Capture
The agent naturally collects the following information during conversation:
- **Name** (required)
- **Email** (required)
- **Company name**
- **Role/Position**
- **Use Case** (required) - What they want to use Razorpay for
- **Team Size** (optional)
- **Timeline** (now / soon / later)

### 3. Conversation Flow
1. **Greeting**: Warm welcome and introduction
2. **Discovery**: Understanding prospect's needs
3. **Q&A**: Answering questions using FAQ
4. **Lead Collection**: Naturally gathering information
5. **Summary**: Recap and confirmation
6. **Save**: Store lead data to `leads.json`

## Implementation Details

### Classes

#### `LeadState`
Manages the state of lead information during the conversation.
- Tracks all lead fields
- Validates completeness
- Converts to dictionary for storage

#### `CompanyFAQ`
Handles FAQ knowledge base operations.
- Loads FAQ data from JSON
- Searches for relevant answers
- Provides company overview

#### `SDRAgent`
Main agent class that orchestrates the SDR conversation.
- Inherits from `Agent` base class
- Uses function tools for lead capture
- Sends real-time updates to frontend
- Saves leads to JSON file

### Function Tools

The agent uses the following function tools:

1. **`answer_company_question(question)`** - Answer FAQ questions
2. **`get_company_overview()`** - Provide company overview
3. **`record_lead_name(name)`** - Capture prospect's name
4. **`record_lead_company(company)`** - Capture company name
5. **`record_lead_email(email)`** - Capture email address
6. **`record_lead_role(role)`** - Capture job title/role
7. **`record_use_case(use_case)`** - Capture intended use case
8. **`record_team_size(team_size)`** - Capture team size
9. **`record_timeline(timeline)`** - Capture timeline (normalized to now/soon/later)
10. **`check_lead_completeness()`** - Check what info is still needed
11. **`complete_call_and_save_lead()`** - Finalize and save the lead

## Data Files

### Input: `shared-data/sdr_company_faq.json`
Contains:
- Company information (name, tagline, description)
- Products list with features
- FAQ items with questions, answers, and keywords
- Use cases by industry

### Output: `leads.json`
Stores captured leads with:
- All lead fields
- Timestamp
- Conversation summary
- Questions asked count

## Usage

### Running the Agent

The agent is configured in `backend/src/agent.py`:

```python
# In entrypoint function
agent = SDRAgent()
agent.set_room(ctx.room)
```

### Testing

Run the test suite:
```bash
cd backend
.venv\Scripts\python.exe -m pytest tests/test_sdr_agent.py -v
```

## Agent Personality

The SDR agent is designed to be:
- **Warm and professional** - Makes prospects feel welcome
- **Consultative** - Focuses on understanding needs, not just selling
- **Knowledgeable** - Answers questions accurately using FAQ
- **Natural** - Collects information conversationally, not like a form
- **Helpful** - Genuinely tries to assist prospects

## Example Conversation Flow

```
Agent: "Hi! I'm with Razorpay, India's leading payment gateway. 
        What brought you here today?"

User: "I'm looking for a payment solution for my ecommerce store."

Agent: [Uses record_use_case tool]
       "That's a great use case! Ecommerce payments is something we 
        handle really well. Can I get your name?"

User: "I'm Rahul."

Agent: [Uses record_lead_name tool]
       "Great to meet you, Rahul! Tell me more about your store."

User: "What are your pricing fees?"

Agent: [Uses answer_company_question tool]
       "Our standard pricing is 2% per transaction for domestic payments...
        Is there anything else you'd like to know?"

User: "That sounds good. My email is rahul@example.com"

Agent: [Uses record_lead_email tool]
       "Perfect, I've got your email as rahul@example.com."

User: "I think that's all for now."

Agent: [Uses complete_call_and_save_lead tool]
       "Thank you so much for your time today, Rahul! Let me quickly recap:
        You're interested in using Razorpay for ecommerce payments..."
```

## Customization

### Changing the Company
To use a different company:
1. Update `shared-data/sdr_company_faq.json` with new company data
2. Update the agent instructions in `SDRAgent.__init__()` to reflect the new company

### Adding More FAQ Items
Simply add more entries to the `faq` array in `sdr_company_faq.json`:
```json
{
  "question": "Your question here?",
  "answer": "Your answer here.",
  "keywords": ["keyword1", "keyword2"]
}
```

### Modifying Lead Fields
To add/remove lead fields:
1. Update `LeadState` class
2. Add/remove corresponding `record_*` function tools
3. Update `is_complete()` and `get_missing_fields()` methods

## Real-time Updates

The agent sends real-time updates to the frontend via data channel:
- **Topic**: `sdr_session`
- **Update Types**:
  - `lead_update` - When lead information changes
  - `call_complete` - When call is finished and saved

## Future Enhancements

Potential improvements:
- Integration with CRM systems
- Meeting scheduler (Advanced Goal 1)
- Call notes and qualification scoring (Advanced Goal 2)
- Multi-language support
- Sentiment analysis
- Follow-up email automation
