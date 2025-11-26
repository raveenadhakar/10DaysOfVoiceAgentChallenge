# SDR Frontend Component Structure

## Component Hierarchy

```
App
└── ViewController
    ├── WelcomeView (mode="sdr")
    │   ├── PaymentIcon
    │   ├── Razorpay Header
    │   ├── Product Showcase (3 cards)
    │   ├── What to Expect Section
    │   └── Start Conversation Button
    │
    └── SDRSessionView
        ├── Left Sidebar (320px)
        │   ├── Branded Header
        │   │   ├── Company Name: "Razorpay SDR"
        │   │   └── Subtitle: "Sales Development Representative"
        │   │
        │   ├── Lead Progress Section
        │   │   ├── Completion Percentage
        │   │   ├── Progress Bar
        │   │   └── Call Complete Indicator
        │   │
        │   ├── Lead Information Panel
        │   │   ├── Name Card (required) ✓
        │   │   ├── Email Card (required) ✓
        │   │   ├── Company Card (optional)
        │   │   ├── Role Card (optional)
        │   │   ├── Use Case Card (required) ✓
        │   │   ├── Team Size Card (optional)
        │   │   └── Timeline Card (optional, color-coded)
        │   │
        │   ├── Missing Fields Alert (conditional)
        │   │   └── List of required fields not yet captured
        │   │
        │   └── Stats Section
        │       ├── Questions Asked Counter
        │       └── Last Update Timestamp
        │
        └── Main Area
            └── SessionView
                ├── Chat Transcript
                ├── Audio Controls
                └── Voice Interaction
```

## Data Flow Diagram

```
Backend SDR Agent
        │
        │ (LiveKit Data Channel: "sdr_session")
        │
        ▼
SDRSessionView Component
        │
        ├─► useDataChannel Hook
        │       │
        │       ▼
        │   Message Decoder
        │       │
        │       ├─► type: "lead_update"
        │       │       │
        │       │       ▼
        │       │   Update leadData State
        │       │       │
        │       │       ▼
        │       │   Trigger Re-render
        │       │       │
        │       │       ▼
        │       │   Update UI Components:
        │       │   - Progress Bar
        │       │   - Lead Cards
        │       │   - Missing Fields Alert
        │       │
        │       └─► type: "call_complete"
        │               │
        │               ▼
        │           Set callComplete Flag
        │               │
        │               ▼
        │           Show Completion Indicator
        │
        └─► Render Functions
                │
                ├─► getCompletionPercentage()
                │   - Calculates: (filled_required / total_required) × 100
                │
                └─► getMissingFields()
                    - Returns: Array of unfilled required fields
```

## State Management

```typescript
// Component State
const [leadData, setLeadData] = useState<LeadData>({})
const [callComplete, setCallComplete] = useState(false)
const [questionsAsked, setQuestionsAsked] = useState(0)
const [lastUpdate, setLastUpdate] = useState<string>('')

// Derived State
const completionPercentage = getCompletionPercentage()
const missingFields = getMissingFields()
```

## Styling Architecture

```
Tailwind CSS Classes
│
├── Layout
│   ├── flex, flex-col, flex-1
│   ├── w-80 (sidebar width)
│   ├── h-full
│   └── overflow-y-auto
│
├── Spacing
│   ├── p-4 (padding)
│   ├── mb-2, mb-3 (margins)
│   └── space-y-3 (vertical spacing)
│
├── Colors
│   ├── Blue Theme
│   │   ├── bg-blue-50, bg-blue-600
│   │   ├── text-blue-600, text-blue-700
│   │   └── border-blue-300
│   │
│   ├── Status Colors
│   │   ├── Green: Success/Complete
│   │   ├── Yellow: Warning/Missing
│   │   └── Red: Urgent
│   │
│   └── Gradients
│       └── from-blue-600 to-indigo-600
│
├── Typography
│   ├── text-xl, text-sm, text-xs
│   ├── font-bold, font-semibold, font-medium
│   └── text-gray-900, text-gray-600, text-gray-400
│
└── Interactive
    ├── rounded-lg (border radius)
    ├── border, border-gray-200
    ├── transition-all duration-300
    └── hover states
```

## Component Props Flow

```
App Config
    │
    ▼
ViewController
    │
    ├─► isSDRMode = (appConfig.companyName === 'Razorpay SDR')
    │
    ├─► WelcomeView
    │   ├── startButtonText: string
    │   ├── onStartCall: () => void
    │   └── mode: 'sdr' | 'tutor'
    │
    └─► SDRSessionView
        └── appConfig: AppConfig
            ├── companyName
            ├── pageTitle
            ├── accent colors
            └── other settings
```

## Event Handlers

```typescript
// Data Channel Message Handler
useEffect(() => {
  if (!message) return;
  
  const data = JSON.parse(decode(message.payload));
  
  switch(data.type) {
    case 'lead_update':
      setLeadData(prev => ({ ...prev, ...data.lead }));
      setLastUpdate(new Date().toLocaleTimeString());
      break;
      
    case 'call_complete':
      setCallComplete(true);
      setLeadData(prev => ({ ...prev, ...data.lead }));
      break;
  }
}, [message]);
```

## Responsive Behavior

```
Desktop (>768px)
├── Sidebar: 320px fixed width
├── Main Area: Flexible width
└── All features visible

Mobile (<768px)
├── Sidebar: Full width or collapsible
├── Main Area: Full width
└── Stacked layout
```

## Animation Timeline

```
Page Load
    │
    ▼
Welcome View Fade In (0.5s)
    │
    ▼
User Clicks "Start Conversation"
    │
    ▼
Welcome View Fade Out (0.5s)
    │
    ▼
SDR Session View Fade In (0.5s)
    │
    ▼
Real-time Updates
    ├─► Progress Bar: transition-all duration-300
    ├─► Field Cards: Instant update
    └─► Alerts: Conditional render
```

## Field Validation Logic

```typescript
// Required Fields
const requiredFields = ['name', 'email', 'use_case'];

// Completion Check
const isComplete = requiredFields.every(
  field => leadData[field]
);

// Progress Calculation
const progress = requiredFields.filter(
  field => leadData[field]
).length / requiredFields.length * 100;

// Missing Fields
const missing = requiredFields.filter(
  field => !leadData[field]
);
```

## Timeline Badge Logic

```typescript
// Timeline Color Mapping
const timelineColors = {
  'now': {
    bg: 'bg-red-100',
    text: 'text-red-700',
    label: 'NOW'
  },
  'soon': {
    bg: 'bg-yellow-100',
    text: 'text-yellow-700',
    label: 'SOON'
  },
  'later': {
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    label: 'LATER'
  }
};
```

## Integration Points

```
Frontend ←→ Backend
    │
    ├─► Data Channel: "sdr_session"
    │   ├── Topic-based messaging
    │   ├── JSON payload
    │   └── Real-time updates
    │
    ├─► Voice Session
    │   ├── Audio stream
    │   ├── STT/TTS
    │   └── Chat messages
    │
    └─► Session State
        ├── Connection status
        ├── Participant info
        └── Room metadata
```

## File Dependencies

```
sdr-session-view.tsx
    │
    ├── React (useState, useEffect)
    ├── @livekit/components-react (useDataChannel)
    ├── AppConfig (type definition)
    └── SessionView (child component)

view-controller.tsx
    │
    ├── motion/react (AnimatePresence, motion)
    ├── session-provider (useSession)
    ├── SDRSessionView
    ├── TutorSessionView
    └── WelcomeView

welcome-view.tsx
    │
    ├── React (ComponentProps)
    ├── Button (livekit component)
    ├── PaymentIcon (SVG component)
    └── BookIcon (SVG component)
```

## CSS Class Patterns

```css
/* Card Pattern */
.card {
  @apply rounded-lg border border-gray-200 p-3;
}

/* Status Badge Pattern */
.badge {
  @apply inline-block rounded px-2 py-1 text-xs font-semibold;
}

/* Progress Bar Pattern */
.progress-bar {
  @apply h-2 w-full rounded-full bg-gray-200;
}

.progress-fill {
  @apply h-2 rounded-full transition-all duration-300;
}

/* Header Pattern */
.section-header {
  @apply mb-3 font-semibold text-gray-900;
}
```

## Component Lifecycle

```
Mount
    │
    ├─► Initialize State
    │   ├── leadData: {}
    │   ├── callComplete: false
    │   ├── questionsAsked: 0
    │   └── lastUpdate: ''
    │
    ├─► Subscribe to Data Channel
    │   └── topic: "sdr_session"
    │
    └─► Render Initial UI
        └── Empty lead cards

Update (on message)
    │
    ├─► Decode Message
    ├─► Parse JSON
    ├─► Update State
    └─► Re-render UI

Unmount
    │
    └─► Cleanup subscriptions
```

This structure provides a clear, maintainable, and scalable architecture for the SDR frontend!
