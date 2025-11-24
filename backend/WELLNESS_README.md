# Health & Wellness Voice Companion

A supportive voice AI companion that conducts daily wellness check-ins to help users reflect on their mood, energy, and daily intentions.

## Features

### Core Functionality
- **Daily Check-ins**: Conducts supportive conversations about mood and energy
- **Goal Setting**: Helps identify 1-3 practical daily objectives
- **Self-care Planning**: Encourages simple self-care activities
- **Data Persistence**: Saves check-in data to `wellness_log.json`
- **Conversation Continuity**: References previous check-ins for ongoing support

### Agent Personality
- **Alex**: A warm, empathetic, and grounded wellness companion
- **Non-medical**: Provides support without medical advice or diagnosis
- **Practical**: Focuses on small, actionable steps and realistic goals
- **Supportive**: Non-judgmental and encouraging approach

## How It Works

### 1. Daily Check-in Flow
1. **Mood Assessment**: "How are you feeling today?"
2. **Energy Check**: "What's your energy like?"
3. **Stress Factors**: Gentle inquiry about current stressors
4. **Daily Goals**: "What are 1-3 things you'd like to get done today?"
5. **Self-care**: "Is there anything you want to do for yourself?"
6. **Recap & Confirmation**: Summarizes the check-in for confirmation

### 2. Data Structure
Each check-in saves the following to `wellness_log.json`:
```json
{
  "entries": [
    {
      "mood": "optimistic",
      "energy_level": "moderate", 
      "stress_factors": ["upcoming presentation"],
      "daily_objectives": ["prepare slides", "practice presentation", "go for a walk"],
      "self_care_intentions": ["take breaks every hour"],
      "date": "2024-11-24",
      "time": "09:15:00",
      "timestamp": "2024-11-24T09:15:00",
      "summary": "Feeling optimistic with moderate energy. Goals: prepare slides, practice presentation, go for a walk"
    }
  ]
}
```

### 3. Function Tools
- `record_mood()`: Captures current mood
- `record_energy_level()`: Records energy state
- `add_stress_factor()`: Notes current stressors
- `add_daily_objective()`: Sets daily goals
- `add_self_care_intention()`: Plans self-care activities
- `get_previous_context()`: Retrieves past check-in context
- `complete_checkin()`: Saves and summarizes the session

## Running the Wellness Companion

### Prerequisites
1. Activate the virtual environment:
   ```bash
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate   # Linux/Mac
   ```

2. Ensure environment variables are set in `.env`:
   ```
   LIVEKIT_URL=your_livekit_url
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   GOOGLE_API_KEY=your_google_api_key
   MURF_API_KEY=your_murf_api_key
   ```

### Start the Agent
```bash
python src/agent.py dev
```

### Connect via Frontend
1. Open the frontend application
2. Click "Start Call" to begin voice interaction
3. Say "Hi" or "I'd like to do a wellness check-in"
4. Follow Alex's gentle guidance through the check-in process

## Example Conversation

**Alex**: "Hello! I'm here for your daily wellness check-in. Last time we talked, you mentioned feeling optimistic with moderate energy. How are you feeling today?"

**User**: "I'm feeling a bit stressed today, but my energy is good."

**Alex**: "I hear that you're feeling stressed. Thank you for sharing that with me. Got it, your energy is good today. What's contributing to that stress you're experiencing?"

**User**: "I have a big presentation tomorrow and I'm worried about it."

**Alex**: "I understand that your presentation tomorrow is weighing on you right now. What are 1-3 things you'd like to get done today to help you feel more prepared?"

**User**: "I want to finish my slides, practice the presentation, and maybe take a walk to clear my head."

**Alex**: "That sounds like great goals: finish slides, practice presentation, take a walk. Those are really practical steps. Is there anything specific you want to do for self-care today?"

**User**: "Maybe some deep breathing exercises before bed."

**Alex**: "That's wonderful - deep breathing exercises sounds like great self-care. Let me give you a recap of our check-in: you're feeling stressed with good energy, and your main goals are finish slides, practice presentation, take a walk. I also noted that your presentation tomorrow is on your mind. For self-care, you're planning to do deep breathing exercises. Does this sound right?"

## Key Benefits

1. **Non-judgmental Support**: Creates a safe space for daily reflection
2. **Practical Focus**: Emphasizes actionable steps and realistic goals
3. **Continuity**: Builds on previous conversations for ongoing support
4. **Data Tracking**: Maintains a record for personal reflection and patterns
5. **Accessibility**: Voice-based interaction makes it easy to use anytime

## Safety & Limitations

- **Not Medical Advice**: Alex provides emotional support, not medical diagnosis or treatment
- **Crisis Support**: Not designed for crisis intervention - users should contact appropriate services
- **Privacy**: Check-in data is stored locally in JSON format
- **Boundaries**: Maintains appropriate boundaries as a supportive companion, not a therapist

## Testing

Run the test suite to verify functionality:
```bash
python test_wellness.py
```

This validates:
- WellnessState data structure
- JSON file creation and reading
- Expected log format and structure