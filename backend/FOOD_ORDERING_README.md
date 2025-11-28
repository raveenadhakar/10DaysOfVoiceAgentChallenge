# Food & Grocery Ordering Voice Agent

## Overview

This implementation provides a complete voice-enabled food and grocery ordering system that allows users to:

- Browse and order from a diverse catalog of food items
- Intelligently request ingredients for recipes (e.g., "I need ingredients for pasta")
- Manage their shopping cart with full CRUD operations
- Complete orders and save them to JSON files

## Features Implemented

### ✅ 1. Catalog Management
- **File**: `food_catalog.json`
- **Categories**: Groceries, Snacks, Prepared Food
- **Items**: 16 diverse items with complete metadata
- **Recipes**: 4 pre-defined recipe mappings

### ✅ 2. Cart Management
- Add items with quantities and notes
- Remove items from cart
- Update item quantities
- View cart contents and totals
- Calculate subtotals, tax, and final totals

### ✅ 3. Intelligent Recipe Handling
- "Ingredients for peanut butter sandwich" → adds bread + peanut butter
- "What I need for pasta for two" → adds pasta + sauce + cheese
- "Breakfast basics" → adds eggs + bread + butter
- "Grilled cheese ingredients" → adds bread + cheese + butter

### ✅ 4. Order Processing
- Collect customer information (name, address)
- Generate unique order IDs with timestamps
- Save complete orders to JSON files in `orders/` directory
- Include all order details, pricing, and customer info

### ✅ 5. Voice Agent Persona
- **Name**: Alex, FreshMart Assistant
- **Personality**: Friendly, helpful, knowledgeable about food
- **Capabilities**: Natural conversation, confirmations, clarifications

## Agent Functions

### Core Shopping Functions
- `search_products(query)` - Find items by name, category, or tags
- `add_item_to_cart(item_name, quantity, notes)` - Add items to cart
- `add_recipe_ingredients(recipe_or_dish)` - Add multiple items for recipes
- `show_cart()` - Display current cart contents and total
- `remove_item_from_cart(item_name)` - Remove items from cart
- `update_item_quantity(item_name, new_quantity)` - Update quantities

### Order Management Functions
- `get_customer_info(name, address)` - Collect customer details
- `complete_order()` - Process and save the final order

## Usage Examples

### Basic Item Search and Add
```
User: "I need some bread"
Agent: "I found Whole Wheat Bread by Nature's Own for $3.49 (20 oz). Would you like to add this to your cart?"

User: "Yes, add 2 loaves"
Agent: "Added 2x Whole Wheat Bread by Nature's Own to your cart for $6.98. Your cart total is now $6.98."
```

### Intelligent Recipe Requests
```
User: "I need ingredients for a peanut butter sandwich"
Agent: "I've added all the ingredients for peanut butter sandwich to your cart: Whole Wheat Bread, Creamy Peanut Butter. That's $9.48 added to your cart. Your total is now $9.48."
```

### Cart Management
```
User: "What's in my cart?"
Agent: "Here's what's in your cart (3 items):
• 2x Whole Wheat Bread - $6.98
• 1x Creamy Peanut Butter - $5.99
Total: $12.97"
```

### Order Completion
```
User: "I'm done, place my order"
Agent: "I need your name to complete the order. What's your name?"

User: "Alex Johnson"
Agent: "Perfect! Your order has been placed and saved as ORDER_20251128_183615_AlexJohnson.
Order Summary for Alex Johnson:
• 3 items
• Subtotal: $12.97
• Tax: $1.04
• Total: $14.01
Order for pickup - we'll have it ready soon!"
```

## Technical Implementation

### Classes
- **`FoodOrderingAgent`**: Main voice agent with LiveKit integration
- **`CartState`**: Manages shopping cart state and operations
- **`FoodCatalog`**: Handles catalog loading, searching, and recipe lookups

### Data Structures
- **Catalog Items**: Include id, name, category, price, brand, size, units, tags
- **Cart Items**: Include all catalog fields plus quantity, notes, subtotal
- **Orders**: Include order_id, timestamp, customer info, items, pricing summary

### File Structure
```
backend/
├── src/agent.py              # Main agent implementation
├── food_catalog.json         # Product catalog and recipes
├── orders/                   # Generated order files
│   └── ORDER_*.json         # Individual order files
└── FOOD_ORDERING_README.md  # This documentation
```

## Order File Format

Each completed order is saved as a JSON file with this structure:

```json
{
  "order_id": "ORDER_20251128_183615_Alex",
  "timestamp": "2025-11-28T18:36:15.233320",
  "date": "2025-11-28",
  "time": "18:36:15",
  "customer": {
    "name": "Alex",
    "address": "Pickup"
  },
  "items": [
    {
      "id": "bread_001",
      "name": "Whole Wheat Bread",
      "category": "groceries",
      "price": 3.49,
      "quantity": 2,
      "notes": "",
      "subtotal": 6.98
    }
  ],
  "summary": {
    "total_items": 2,
    "subtotal": 6.98,
    "tax": 0.56,
    "total": 7.54
  },
  "status": "confirmed"
}
```

## Running the Agent

To use the food ordering agent, set the room metadata to `"food"` when creating a LiveKit room, or it will default to the food ordering agent.

The agent integrates seamlessly with the existing voice pipeline and provides real-time cart updates via data channels to the frontend.

## MVP Completion Status: ✅ COMPLETE

All primary goal requirements have been successfully implemented:
- ✅ Diverse catalog with 16+ items across multiple categories
- ✅ Intelligent ingredient bundling for common recipes
- ✅ Full cart management (add, remove, update, list)
- ✅ Order completion with JSON file saving
- ✅ Friendly, helpful voice agent persona