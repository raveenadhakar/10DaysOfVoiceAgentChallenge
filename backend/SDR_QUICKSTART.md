# SDR Agent Quick Start Guide

## Prerequisites

- Python 3.8+
- Virtual environment set up
- LiveKit account and credentials
- Required dependencies installed

## Setup

### 1. Verify Installation

```bash
cd backend
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

### 2. Check Environment Variables

Ensure your `.env` file has:
```
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
DEEPGRAM_API_KEY=your_deepgram_key
GOOGLE_API_KEY=your_google_key
MURF_API_KEY=your_murf_key
```

### 3. Verify FAQ Data

Check that `shared-data/sdr_company_faq.json` exists and contains Razorpay data.

## Running the Agent

### Start the Backend

```bash
cd backend
python src/agent.py
```

You should see:
```
INFO   livekit.agents   registered worker
INFO   livekit.agents   received job request
INFO   livekit.agents   🚀 Agent session started successfully
```

### Start the Frontend

In a separate terminal:
```bash
cd frontend
npm run dev
```

### Connect

1. Open browser to `http://localhost:3000`
2. Click "Connect" or "Start Session"
3. Allow microphone permissions
4. Start talking!

## Testing the Agent

### Run Unit Tests

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests/test_sdr_agent.py -v
```

Expected output:
```
15 passed in ~26s
```

### Manual Testing Scenarios

#### Scenario 1: Basic Lead Capture
```
You: "Hi, I'm looking for a payment gateway"
Agent: [Greets and asks for details]
You: "My name is Rahul"
Agent: [Records name]
You: "My email is rahul@example.com"
Agent: [Records email]
You: "I want to use it for my ecommerce store"
Agent: [Records use case]
You: "That's all for now"
Agent: [Provides summary and saves lead]
```

Check `backend/leads.json` for the saved lead.

#### Scenario 2: FAQ Questions
```
You: "What does Razorpay do?"
Agent: [Answers from FAQ]
You: "What are your pricing fees?"
Agent: [Answers from FAQ]
You: "Do you support UPI?"
Agent: [Answers from FAQ]
```

#### Scenario 3: Complete Flow
```
You: "Hi"
Agent: "Hi! I'm with Razorpay..."
You: "I need payment solution for my SaaS product"
Agent: [Records use case, asks for name]
You: "I'm Priya from EduLearn"
Agent: [Records name and company]
You: "What's your pricing?"
Agent: [Answers from FAQ]
You: "My email is priya@edulearn.com"
Agent: [Records email]
You: "I'm the product manager"
Agent: [Records role]
You: "We need this next month"
Agent: [Records timeline as "soon"]
You: "Thanks, that's all"
Agent: [Provides summary, saves lead]
```

## Verifying Output

### Check Logs

Look for these log messages:
```
INFO   agent   Recorded lead name: Rahul
INFO   agent   Recorded email: rahul@example.com
INFO   agent   Recorded use case: ecommerce payments
INFO   agent   Lead saved to leads.json
```

### Check leads.json

```bash
cat backend/leads.json
```

Should contain:
```json
{
  "leads": [
    {
      "name": "Rahul",
      "email": "rahul@example.com",
      "use_case": "ecommerce payments",
      ...
    }
  ]
}
```

## Troubleshooting

### Agent Not Responding

1. **Check microphone permissions**
   - Browser should show microphone icon
   - Allow microphone access

2. **Check STT metrics**
   ```
   INFO   livekit.agents   STT metrics
   ```
   If you see this, STT is working

3. **Check function calls**
   ```
   INFO   agent   🔧 Function calls collected
   ```
   If you see this, LLM is calling tools

### FAQ Not Working

1. **Verify FAQ file exists**
   ```bash
   ls backend/shared-data/sdr_company_faq.json
   ```

2. **Check FAQ loading**
   ```
   INFO   agent   Found FAQ answer for: ...
   ```

3. **Try more specific questions**
   - "What are your fees?" instead of "Tell me about pricing"
   - "Do you support UPI?" instead of "Payment methods?"

### Lead Not Saving

1. **Check lead completeness**
   - Need: name, email, use_case
   - Agent will ask for missing fields

2. **Check file permissions**
   ```bash
   ls -l backend/leads.json
   ```

3. **Check logs for errors**
   ```
   ERROR  agent   Failed to save lead: ...
   ```

## Common Issues

### Issue: "No module named 'src'"

**Solution**: Run from backend directory
```bash
cd backend
python src/agent.py
```

### Issue: "Failed to load FAQ data"

**Solution**: Check file path
```bash
ls shared-data/sdr_company_faq.json
```

### Issue: Agent doesn't hear me

**Solution**: 
1. Check microphone permissions
2. Speak clearly and wait for response
3. Check STT logs for audio detection

### Issue: Agent makes up information

**Solution**: This shouldn't happen! The agent only uses FAQ data. If it does:
1. Check the FAQ file
2. Review agent instructions
3. Report as a bug

## Customization

### Change Company

1. Edit `shared-data/sdr_company_faq.json`
2. Update company info, products, FAQ
3. Update agent instructions in `SDRAgent.__init__()`
4. Restart agent

### Add More FAQ Items

Add to `faq` array in JSON:
```json
{
  "question": "New question?",
  "answer": "New answer.",
  "keywords": ["keyword1", "keyword2"]
}
```

### Modify Lead Fields

1. Update `LeadState` class
2. Add `record_*` function tool
3. Update `is_complete()` method
4. Restart agent

## Next Steps

### Test Different Scenarios

- Try different questions
- Test with incomplete information
- Test timeline variations (now/soon/later)
- Test with multiple leads

### Review Saved Leads

```bash
cat backend/leads.json | python -m json.tool
```

### Analyze Performance

- Check response times
- Review conversation quality
- Verify lead data accuracy

### Optional: Implement Advanced Goals

1. **Meeting Scheduler**
   - Add calendar integration
   - Offer time slots
   - Book meetings

2. **CRM Notes**
   - Generate qualification scores
   - Extract pain points
   - Assess urgency

## Support

### Documentation

- `SDR_README.md` - Comprehensive guide
- `SDR_ARCHITECTURE.md` - System design
- `SDR_IMPLEMENTATION_SUMMARY.md` - What was built

### Testing

- `tests/test_sdr_agent.py` - Unit tests
- `leads_sample.json` - Example output

### Logs

Check logs for debugging:
```bash
tail -f backend/logs/agent.log  # If logging to file
```

## Success Criteria

You've successfully set up the SDR agent when:

✅ Agent starts without errors
✅ Agent greets you warmly
✅ Agent answers FAQ questions correctly
✅ Agent collects lead information naturally
✅ Agent provides end-of-call summary
✅ Lead data saves to leads.json
✅ All unit tests pass

## Example Session

```
Terminal 1 (Backend):
$ cd backend
$ python src/agent.py
INFO   livekit.agents   🚀 Agent session started successfully

Terminal 2 (Frontend):
$ cd frontend
$ npm run dev
Ready on http://localhost:3000

Browser:
1. Open http://localhost:3000
2. Click "Connect"
3. Allow microphone
4. Say: "Hi, I need a payment gateway"
5. Have conversation
6. Say: "That's all, thanks"
7. Check backend/leads.json

Result:
✅ Lead captured and saved!
```

## Tips for Best Results

1. **Speak clearly** - Wait for agent to finish before responding
2. **Be natural** - Conversation should flow naturally
3. **Provide complete info** - Name, email, and use case are required
4. **Ask questions** - Test the FAQ system
5. **Signal end** - Say "that's all" or "thanks" to trigger summary

## Monitoring

Watch for these indicators of success:

```
✅ User speech committed
✅ Function calls collected
✅ Lead update sent
✅ Lead saved to leads.json
```

Happy testing! 🚀
