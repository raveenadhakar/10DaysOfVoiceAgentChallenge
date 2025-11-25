# Day 4 - Teach-the-Tutor: Active Recall Coach

## Overview

This implementation creates an AI-powered active recall coach that helps users learn programming concepts through three different learning modes. The system uses different voices for each mode to create distinct learning experiences.

## Features

### Three Learning Modes

1. **LEARN Mode (Matthew's voice)**
   - Agent explains programming concepts clearly
   - Uses analogies and real-world examples
   - Provides comprehensive explanations

2. **QUIZ Mode (Alicia's voice)**
   - Agent tests understanding with questions
   - Evaluates answers and provides feedback
   - Offers hints when needed

3. **TEACH_BACK Mode (Ken's voice)**
   - User explains concepts back to the agent
   - Agent listens and provides constructive feedback
   - Helps identify knowledge gaps

### Available Concepts

- **Variables**: Data containers and storage
- **Loops**: Repetitive code execution
- **Functions**: Reusable code blocks
- **Conditionals**: Decision-making in code

## Implementation Details

### Backend (`backend/src/agent.py`)

- **TutorCoordinatorAgent**: Main agent that handles all three modes
- **TutorContent**: Manages the concept content from JSON file
- **Function Tools**: Separate tools for each mode's functionality
- **Data Communication**: Sends mode updates to frontend via data channels

### Frontend (`frontend/components/app/`)

- **TutorSessionView**: Main tutor interface with mode indicators
- **Updated WelcomeView**: Shows the three learning modes
- **Real-time Updates**: Displays current mode and concept information

### Content File (`backend/shared-data/day4_tutor_content.json`)

Contains structured data for each programming concept:
- ID and title
- Detailed summary explanation
- Sample questions for quizzing

## Usage

1. **Start the Application**
   ```bash
   # Backend
   cd backend
   uv run python src/agent.py dev
   
   # Frontend
   cd frontend
   npm run dev
   ```

2. **Access the Interface**
   - Open http://localhost:3000
   - Click "Start Learning Session"

3. **Interact with the Tutor**
   - Say "explain the learning modes" to get started
   - Switch modes: "switch to learn", "switch to quiz", "switch to teach back"
   - Request concepts: "explain variables", "quiz me on loops", "I want to teach back functions"

## Voice Configuration

The system is designed to use different Murf voices for each mode:
- **Matthew** (Learn mode): Clear, methodical explanations
- **Alicia** (Quiz mode): Encouraging, supportive questioning
- **Ken** (Teach back mode): Attentive, patient listening

## Testing

Run the test suite to verify functionality:
```bash
cd backend
uv run pytest tests/test_tutor_agent.py -v
```

## Key Functions

### Learn Mode
- `explain_concept(concept_id)`: Explains a specific concept
- `list_available_concepts()`: Shows all available topics

### Quiz Mode
- `ask_question_about_concept(concept_id)`: Asks quiz questions
- `evaluate_answer(user_answer)`: Evaluates and provides feedback

### Teach Back Mode
- `request_explanation(concept_id)`: Asks user to explain concept
- `provide_feedback(user_explanation)`: Analyzes and responds to explanations

### Mode Management
- `switch_to_learn_mode()`: Switches to explanation mode
- `switch_to_quiz_mode()`: Switches to questioning mode
- `switch_to_teach_back_mode()`: Switches to listening mode
- `explain_learning_modes()`: Describes all available modes

## Architecture

The implementation uses a single coordinator agent that handles all three modes internally, rather than separate agents. This simplifies the architecture while still providing distinct personalities and behaviors for each mode.

The frontend provides visual feedback about the current mode and concept, making it easy for users to understand which learning mode they're in and what topic they're working on.