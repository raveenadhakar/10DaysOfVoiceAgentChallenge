# SDR Frontend Implementation

## Overview
This document describes the frontend implementation for the Razorpay SDR (Sales Development Representative) voice agent.

## Components Created

### 1. SDR Session View (`sdr-session-view.tsx`)
A dedicated session view component for the SDR agent that displays:

#### Left Sidebar Features:
- **Header**: Razorpay branding with gradient background
- **Lead Capture Progress**: 
  - Visual progress bar showing completion percentage
  - Based on required fields: name, email, and use case
  - "Call Complete" indicator when conversation ends

- **Lead Information Panel**: Real-time display of captured lead data
  - Name (required) ✓
  - Email (required) ✓
  - Company (optional)
  - Role (optional)
  - Use Case (required) ✓
  - Team Size (optional)
  - Timeline (optional) - with color-coded badges:
    - NOW: Red badge (urgent)
    - SOON: Yellow badge (near-term)
    - LATER: Gray badge (future)

- **Missing Fields Alert**: 
  - Yellow alert box showing what information is still needed
  - Only visible when call is not complete

- **Stats Section**:
  - Questions asked counter
  - Last update timestamp

#### Main Area:
- Standard SessionView component for voice interaction
- Chat transcript
- Audio controls

### 2. Updated Welcome View (`welcome-view.tsx`)
Enhanced to support both SDR and Tutor modes:

#### SDR Mode Features:
- **Razorpay Branding**: Payment icon and company name
- **Product Showcase**: Three key products displayed:
  - Payment Gateway (100+ payment modes)
  - Subscriptions (recurring billing)
  - Marketplace (split payments)
- **What to Expect Section**: Clear expectations for the conversation
- **Call-to-Action**: "Start Conversation" button
- **Footer**: Razorpay website link

#### Tutor Mode Features:
- Original tutor interface preserved
- Book icon and learning modes display

### 3. Updated View Controller (`view-controller.tsx`)
Enhanced routing logic:
- Detects mode based on `appConfig.companyName`
- Routes to SDRSessionView when in SDR mode
- Routes to TutorSessionView when in Tutor mode
- Passes appropriate mode prop to WelcomeView

### 4. Updated App Config (`app-config.ts`)
Default configuration set for SDR mode:
- Company name: "Razorpay SDR"
- Page title: "AI Sales Development Representative"
- Accent colors: Blue theme (#2563eb, #3b82f6)
- Start button text: "Start Conversation"

## Data Flow

### Real-time Updates via Data Channel
The SDR session view listens to the `sdr_session` data channel for updates:

```typescript
interface SDRData {
  type: string;
  lead?: LeadData;
  call_complete?: boolean;
  questions_asked?: number;
  timestamp?: string;
}
```

### Update Types:
1. **`lead_update`**: Partial lead data updates
   - Merges new data with existing lead state
   - Updates timestamp
   - Triggers progress bar recalculation

2. **`call_complete`**: Call completion signal
   - Sets call complete flag
   - Final lead data update
   - Shows completion indicator

### Lead Data Structure:
```typescript
interface LeadData {
  name?: string;
  email?: string;
  company?: string;
  role?: string;
  use_case?: string;
  team_size?: string;
  timeline?: string; // "now" | "soon" | "later"
}
```

## Visual Design

### Color Scheme:
- **Primary**: Blue (#2563eb) - Trust and professionalism
- **Secondary**: Indigo (#4f46e5) - Modern and tech-forward
- **Success**: Green - Completed fields
- **Warning**: Yellow - Missing information
- **Urgent**: Red - "Now" timeline

### Layout:
- **Sidebar Width**: 320px (80 Tailwind units)
- **Responsive**: Sidebar scrolls independently
- **Progress Indicators**: Visual feedback for all state changes

### Typography:
- **Headers**: Bold, clear hierarchy
- **Labels**: Uppercase, small, gray
- **Values**: Medium weight, larger, dark
- **Placeholders**: Italic, light gray

## Integration with Backend

The frontend expects the backend SDR agent to send updates via the LiveKit data channel:

### Example Backend Update:
```python
# In SDRAgent class
await self.room.local_participant.publish_data(
    json.dumps({
        "type": "lead_update",
        "lead": {
            "name": "Rahul Kumar",
            "email": "rahul@example.com",
            "use_case": "ecommerce payments"
        },
        "questions_asked": 3
    }),
    topic="sdr_session"
)
```

### Call Completion:
```python
await self.room.local_participant.publish_data(
    json.dumps({
        "type": "call_complete",
        "lead": complete_lead_data,
        "questions_asked": total_questions
    }),
    topic="sdr_session"
)
```

## User Experience Flow

1. **Landing Page**: 
   - User sees Razorpay branding and product information
   - Clear explanation of what to expect
   - Single "Start Conversation" button

2. **Active Session**:
   - Voice interaction in main area
   - Real-time lead capture progress in sidebar
   - Visual feedback as information is collected
   - Missing fields clearly indicated

3. **Call Completion**:
   - Green "Call Complete" indicator
   - All captured information displayed
   - Final stats shown

## Switching Between Modes

To switch between SDR and Tutor modes, update `app-config.ts`:

### For SDR Mode:
```typescript
export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Razorpay SDR',
  pageTitle: 'AI Sales Development Representative',
  // ... SDR config
};
```

### For Tutor Mode:
```typescript
export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Teach-the-Tutor',
  pageTitle: 'AI Active Recall Coach',
  // ... Tutor config
};
```

## Future Enhancements

Potential improvements for the SDR frontend:

1. **Meeting Scheduler UI**: 
   - Calendar view for booking demos
   - Available time slots display

2. **Call Notes Display**:
   - Show AI-generated call summary
   - Display qualification score

3. **Multi-language Support**:
   - Language selector
   - Localized content

4. **Analytics Dashboard**:
   - Conversation metrics
   - Lead quality indicators

5. **CRM Integration**:
   - Export lead to CRM button
   - Integration status indicators

6. **Chat History**:
   - Previous conversations
   - Lead interaction timeline

## Testing

To test the SDR frontend:

1. Ensure backend SDR agent is running
2. Start the frontend: `npm run dev`
3. Click "Start Conversation"
4. Speak or type to interact with the agent
5. Watch the sidebar update in real-time as information is captured

## Customization

### Changing the Company:
1. Update `app-config.ts` with new company name and branding
2. Update `welcome-view.tsx` with new product information
3. Update `sdr-session-view.tsx` header with new branding
4. Update backend FAQ data in `shared-data/sdr_company_faq.json`

### Modifying Lead Fields:
1. Update `LeadData` interface in `sdr-session-view.tsx`
2. Add/remove field display components in the Lead Information section
3. Update `getCompletionPercentage()` and `getMissingFields()` functions
4. Update backend `LeadState` class to match

## Dependencies

- React 18+
- Next.js 14+
- LiveKit Components React
- Tailwind CSS
- Motion (Framer Motion)

## File Structure

```
frontend/
├── components/
│   └── app/
│       ├── sdr-session-view.tsx      # New SDR session component
│       ├── view-controller.tsx        # Updated routing logic
│       └── welcome-view.tsx           # Updated with SDR mode
├── app-config.ts                      # Updated default config
└── SDR_FRONTEND_README.md            # This file
```

## Conclusion

The SDR frontend provides a professional, real-time interface for lead capture conversations. It seamlessly integrates with the backend SDR agent and provides clear visual feedback throughout the sales conversation process.
