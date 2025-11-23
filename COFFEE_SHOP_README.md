# Coffee Shop Barista Agent - Day 2 Implementation

This implementation transforms the starter agent into Maya, a friendly coffee shop barista for "Brew & Bean Coffee Shop" that can take voice orders and maintain order state.

## Features Implemented

### ✅ Primary Goal (Required)
- **Barista Persona**: Maya, a friendly and enthusiastic barista at Brew & Bean Coffee Shop
- **Order State Management**: Maintains complete order state with all required fields:
  ```json
  {
    "drinkType": "string",
    "size": "string", 
    "milk": "string",
    "extras": ["string"],
    "name": "string"
  }
  ```
- **Conversational Order Taking**: Asks clarifying questions until all fields are filled
- **JSON Order Saving**: Saves completed orders to timestamped JSON files in `/backend/orders/`
- **Function Tools**: Uses LiveKit function tools for order state management

### 🎨 Frontend Enhancements
- **Coffee Shop Branding**: Updated welcome screen with coffee shop theme
- **Real-time Order Display**: Shows current order state in the UI
- **Visual Feedback**: Animated order completion indicators

## File Structure

```
backend/
├── src/
│   └── agent.py          # Main barista agent implementation
├── orders/               # Generated order JSON files
└── tests/
    └── test_agent.py     # Updated tests for barista functionality

frontend/
├── components/app/
│   ├── coffee-order-display.tsx  # Order state UI component
│   ├── welcome-view.tsx          # Updated coffee shop welcome
│   └── session-view.tsx          # Updated to include order display
```

## Key Implementation Details

### Backend Agent (`backend/src/agent.py`)
- **CoffeeShopBarista Class**: Replaces the generic Assistant
- **OrderState Class**: Manages order data structure and validation
- **Function Tools**: 
  - `update_drink_type()` - Sets the coffee drink type
  - `update_size()` - Sets drink size (small/medium/large)
  - `update_milk()` - Sets milk preference
  - `add_extra()` - Adds extras like syrups, shots, etc.
  - `update_name()` - Sets customer name
  - `check_order_status()` - Checks what info is still needed
  - `complete_order()` - Saves order to JSON and resets state

### Order Processing Flow
1. Customer greets Maya
2. Maya asks about drink preferences
3. Uses function tools to collect: drink type, size, milk, extras, name
4. Asks clarifying questions for missing information
5. Confirms complete order details
6. Saves order to JSON file with timestamp
7. Resets for next customer

### JSON Order Format
```json
{
  "drinkType": "latte",
  "size": "medium", 
  "milk": "oat milk",
  "extras": ["extra shot", "vanilla syrup"],
  "name": "Alex",
  "timestamp": "2025-11-23T09:46:15.123456",
  "order_id": "ORD-20251123_094615"
}
```

## Running the Application

### Backend
```bash
cd backend
uv run python src/agent.py download-files  # First time only
uv run python src/agent.py dev
```

### Frontend  
```bash
cd frontend
npm install
npm run dev
```

### Testing
```bash
cd backend
uv run pytest tests/test_agent.py
```

## Usage Instructions

1. **Start the Application**: Run both backend and frontend
2. **Open Browser**: Navigate to the frontend URL
3. **Click "Start Call"**: Begin voice interaction with Maya
4. **Place Your Order**: 
   - Say "Hi" or "I'd like to order a coffee"
   - Maya will guide you through the ordering process
   - Provide drink type, size, milk preference, any extras, and your name
5. **Order Completion**: Maya confirms and saves your order
6. **Check Orders**: View saved JSON files in `backend/orders/`

## Example Conversation Flow

```
User: "Hi there!"
Maya: "Hi! Welcome to Brew & Bean Coffee Shop! I'm Maya, your barista. What can I get started for you today?"

User: "I'd like a coffee please"
Maya: "Perfect! What type of coffee drink would you like? We have lattes, cappuccinos, americanos, mochas, and more!"

User: "I'll have a latte"
Maya: "Great choice! What size would you like - small, medium, or large?"

User: "Medium please"
Maya: "Got it! What's your milk preference? We have whole milk, oat milk, almond milk, soy milk, or coconut milk."

User: "Oat milk"
Maya: "Perfect! Any extras like an extra shot, syrups, or whipped cream?"

User: "Can I get an extra shot?"
Maya: "Added extra shot to your order! And what's your name for the order?"

User: "Alex"
Maya: "Thanks Alex! Perfect! I've got your order: medium latte with oat milk with extra shot for Alex. Your order has been saved and we'll have it ready shortly!"
```

## Advanced Challenge (Optional)

The current implementation focuses on the primary goal. The advanced HTML beverage visualization system could be added as an enhancement using:
- LiveKit data streams for real-time order updates
- HTML/CSS coffee cup visualizations that change based on order details
- RPC calls to update the frontend display

## Next Steps

1. **Test the Implementation**: Place a voice order and verify JSON file creation
2. **Record Demo Video**: Show the complete ordering process
3. **LinkedIn Post**: Share your Day 2 completion with the required hashtags and mentions

This implementation successfully completes the Day 2 Coffee Shop Barista Agent challenge! 🎉☕