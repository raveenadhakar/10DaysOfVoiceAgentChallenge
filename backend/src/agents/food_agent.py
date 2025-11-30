import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from livekit.agents import Agent, function_tool, RunContext

logger = logging.getLogger("food_agent")


# Food Ordering Cart State
class CartState:
    def __init__(self):
        self.items: List[Dict] = []
        self.customer_name: Optional[str] = None
        self.customer_address: Optional[str] = None
        self.order_complete: bool = False
    
    def add_item(self, item: Dict, quantity: int = 1, notes: str = ""):
        """Add an item to the cart."""
        # Check if item already exists in cart
        for cart_item in self.items:
            if cart_item["id"] == item["id"] and cart_item.get("notes", "") == notes:
                cart_item["quantity"] += quantity
                return
        
        # Add new item to cart
        cart_item = {
            **item,
            "quantity": quantity,
            "notes": notes,
            "subtotal": item["price"] * quantity
        }
        self.items.append(cart_item)
    
    def remove_item(self, item_id: str):
        """Remove an item from the cart."""
        self.items = [item for item in self.items if item["id"] != item_id]
    
    def update_quantity(self, item_id: str, new_quantity: int):
        """Update the quantity of an item in the cart."""
        for item in self.items:
            if item["id"] == item_id:
                if new_quantity <= 0:
                    self.remove_item(item_id)
                else:
                    item["quantity"] = new_quantity
                    item["subtotal"] = item["price"] * new_quantity
                break
    
    def get_total(self) -> float:
        """Calculate the total price of items in cart."""
        return sum(item["subtotal"] for item in self.items)
    
    def get_item_count(self) -> int:
        """Get total number of items in cart."""
        return sum(item["quantity"] for item in self.items)
    
    def clear(self):
        """Clear all items from cart."""
        self.items = []
    
    def to_dict(self) -> Dict:
        return {
            "items": self.items,
            "customer_name": self.customer_name,
            "customer_address": self.customer_address,
            "total": self.get_total(),
            "item_count": self.get_item_count(),
            "order_complete": self.order_complete
        }


# Food Catalog Manager
class FoodCatalog:
    def __init__(self, catalog_file: str = "shared-data/food_catalog.json"):
        self.catalog_file = catalog_file
        self.data = self._load_catalog()
        self.items = self._flatten_items()
        self.recipes = self.data.get("recipes", {})
    
    def _load_catalog(self) -> Dict:
        """Load catalog data from JSON file."""
        try:
            with open(self.catalog_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            return {"catalog": {}, "recipes": {}}
    
    def _flatten_items(self) -> Dict[str, Dict]:
        """Create a flat dictionary of all items by ID."""
        items = {}
        catalog = self.data.get("catalog", {})
        for category, category_items in catalog.items():
            for item in category_items:
                items[item["id"]] = item
        return items
    
    def search_items(self, query: str) -> List[Dict]:
        """Search for items by name, category, or tags."""
        query_lower = query.lower()
        matches = []
        
        for item in self.items.values():
            # Check name
            if query_lower in item["name"].lower():
                matches.append(item)
                continue
            
            # Check category
            if query_lower in item["category"].lower():
                matches.append(item)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in item.get("tags", [])):
                matches.append(item)
                continue
            
            # Check brand
            if query_lower in item.get("brand", "").lower():
                matches.append(item)
        
        return matches
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get an item by its ID."""
        return self.items.get(item_id)
    
    def get_recipe_ingredients(self, recipe_name: str) -> List[Dict]:
        """Get ingredients for a recipe."""
        recipe_key = recipe_name.lower().replace(" ", "_")
        recipe = self.recipes.get(recipe_key)
        
        if not recipe:
            return []
        
        ingredients = []
        for ingredient_id in recipe["ingredients"]:
            item = self.get_item_by_id(ingredient_id)
            if item:
                ingredients.append(item)
        
        return ingredients
    
    def search_recipes(self, query: str) -> List[str]:
        """Search for recipes by name."""
        query_lower = query.lower()
        matches = []
        
        for recipe_key, recipe in self.recipes.items():
            if query_lower in recipe["name"].lower() or query_lower in recipe_key:
                matches.append(recipe["name"])
        
        return matches


# Food Ordering Agent
class FoodOrderingAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are Alex, a friendly and helpful food & grocery ordering assistant for FreshMart, your neighborhood grocery store and deli.

            Your personality:
            - Warm, enthusiastic, and helpful
            - Knowledgeable about food and cooking
            - Patient with questions about products
            - Excited to help customers find what they need
            - Conversational and natural, not robotic

            Your role:
            1. Greet customers warmly and explain what you can help with
            2. Help customers find and add items to their cart
            3. Handle intelligent requests like "ingredients for pasta" or "what I need for a sandwich"
            4. Manage their cart (add, remove, update quantities)
            5. Provide information about products (price, size, brand, etc.)
            6. Confirm cart contents when asked
            7. Process orders when customers are ready to checkout
            8. Save completed orders to JSON files

            Key capabilities:
            - Search for items by name, category, or type
            - Add items with specific quantities and notes
            - Handle recipe-based requests intelligently
            - Show cart contents and totals
            - Remove or update items in cart
            - Complete orders and save them

            Guidelines:
            - Always confirm what you're adding to the cart
            - Ask for clarification on quantities, sizes, or brands when needed
            - Be helpful with suggestions for related items
            - Keep track of the running total
            - When customers say they're done, confirm the order and save it
            - Capture basic customer info (name, address) for delivery

            Remember: You're here to make grocery shopping easy and enjoyable!"""
        )
        self.cart = CartState()
        self.catalog = FoodCatalog()
        self._room = None
        self.orders_dir = "orders"
    
    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room
    
    async def _send_cart_update(self):
        """Send cart state update to frontend via data channel."""
        if self._room:
            try:
                cart_data = {
                    "type": "cart_update",
                    "data": self.cart.to_dict()
                }
                await self._room.local_participant.publish_data(
                    json.dumps(cart_data).encode('utf-8'),
                    topic="food_order"
                )
                logger.info(f"Sent cart update: {self.cart.get_item_count()} items, ${self.cart.get_total():.2f}")
            except Exception as e:
                logger.error(f"Failed to send cart update: {e}")
    
    @function_tool
    async def search_products(self, context: RunContext, query: str):
        """Search for food and grocery products.
        
        Args:
            query: What to search for (e.g., "bread", "snacks", "organic", "pasta")
        """
        matches = self.catalog.search_items(query)
        
        if not matches:
            return f"I couldn't find any items matching '{query}'. Try searching for categories like 'groceries', 'snacks', or 'prepared food', or specific items like 'bread', 'milk', or 'pizza'."
        
        if len(matches) == 1:
            item = matches[0]
            return f"I found {item['name']} by {item['brand']} for ${item['price']:.2f} ({item['size']}). Would you like to add this to your cart?"
        
        # Multiple matches - show options
        result = f"I found {len(matches)} items for '{query}':\n"
        for i, item in enumerate(matches[:5], 1):  # Show first 5 matches
            result += f"{i}. {item['name']} by {item['brand']} - ${item['price']:.2f} ({item['size']})\n"
        
        if len(matches) > 5:
            result += f"...and {len(matches) - 5} more items."
        
        result += "\nWhich one would you like to add to your cart?"
        return result
    
    @function_tool
    async def add_item_to_cart(self, context: RunContext, item_name: str, quantity: int = 1, notes: str = ""):
        """Add a specific item to the cart.
        
        Args:
            item_name: Name of the item to add
            quantity: How many to add (default: 1)
            notes: Any special notes (e.g., "large size", "whole wheat")
        """
        # Search for the item
        matches = self.catalog.search_items(item_name)
        
        if not matches:
            return f"I couldn't find '{item_name}' in our catalog. Try searching first to see what's available."
        
        if len(matches) > 1:
            # Multiple matches - ask for clarification
            result = f"I found multiple items for '{item_name}':\n"
            for i, item in enumerate(matches[:3], 1):
                result += f"{i}. {item['name']} by {item['brand']} - ${item['price']:.2f}\n"
            result += "Which one did you want?"
            return result
        
        # Single match - add to cart
        item = matches[0]
        self.cart.add_item(item, quantity, notes)
        await self._send_cart_update()
        
        subtotal = item["price"] * quantity
        notes_text = f" ({notes})" if notes else ""
        
        logger.info(f"Added to cart: {quantity}x {item['name']}{notes_text} = ${subtotal:.2f}")
        
        return f"Added {quantity}x {item['name']} by {item['brand']}{notes_text} to your cart for ${subtotal:.2f}. Your cart total is now ${self.cart.get_total():.2f}."
    
    @function_tool
    async def add_recipe_ingredients(self, context: RunContext, recipe_or_dish: str):
        """Add ingredients for a specific recipe or dish.
        
        Args:
            recipe_or_dish: The recipe or dish name (e.g., "peanut butter sandwich", "pasta for two", "breakfast")
        """
        # First try exact recipe match
        ingredients = self.catalog.get_recipe_ingredients(recipe_or_dish)
        
        if not ingredients:
            # Try searching recipes
            recipe_matches = self.catalog.search_recipes(recipe_or_dish)
            if recipe_matches:
                # Use first match
                ingredients = self.catalog.get_recipe_ingredients(recipe_matches[0])
        
        if not ingredients:
            return f"I don't have a specific recipe for '{recipe_or_dish}'. Try asking for specific ingredients like 'bread and peanut butter' or search for individual items."
        
        # Add all ingredients to cart
        added_items = []
        total_added = 0
        
        for ingredient in ingredients:
            self.cart.add_item(ingredient, 1)
            added_items.append(ingredient["name"])
            total_added += ingredient["price"]
        
        await self._send_cart_update()
        
        logger.info(f"Added recipe ingredients for {recipe_or_dish}: {', '.join(added_items)}")
        
        return f"I've added all the ingredients for {recipe_or_dish} to your cart: {', '.join(added_items)}. That's ${total_added:.2f} added to your cart. Your total is now ${self.cart.get_total():.2f}."
    
    @function_tool
    async def show_cart(self, context: RunContext):
        """Show the current contents of the shopping cart."""
        if not self.cart.items:
            return "Your cart is empty. What would you like to add?"
        
        result = f"Here's what's in your cart ({self.cart.get_item_count()} items):\n\n"
        
        for item in self.cart.items:
            notes_text = f" ({item['notes']})" if item.get('notes') else ""
            result += f"• {item['quantity']}x {item['name']}{notes_text} - ${item['subtotal']:.2f}\n"
        
        result += f"\nTotal: ${self.cart.get_total():.2f}"
        
        return result
    
    @function_tool
    async def remove_item_from_cart(self, context: RunContext, item_name: str):
        """Remove an item from the cart.
        
        Args:
            item_name: Name of the item to remove
        """
        # Find matching item in cart
        removed_item = None
        for item in self.cart.items:
            if item_name.lower() in item["name"].lower():
                removed_item = item
                break
        
        if not removed_item:
            return f"I couldn't find '{item_name}' in your cart. Your cart has: {', '.join([item['name'] for item in self.cart.items])}"
        
        self.cart.remove_item(removed_item["id"])
        await self._send_cart_update()
        
        logger.info(f"Removed from cart: {removed_item['name']}")
        
        return f"Removed {removed_item['name']} from your cart. Your new total is ${self.cart.get_total():.2f}."
    
    @function_tool
    async def update_item_quantity(self, context: RunContext, item_name: str, new_quantity: int):
        """Update the quantity of an item in the cart.
        
        Args:
            item_name: Name of the item to update
            new_quantity: New quantity (use 0 to remove)
        """
        # Find matching item in cart
        target_item = None
        for item in self.cart.items:
            if item_name.lower() in item["name"].lower():
                target_item = item
                break
        
        if not target_item:
            return f"I couldn't find '{item_name}' in your cart."
        
        old_quantity = target_item["quantity"]
        
        if new_quantity <= 0:
            self.cart.remove_item(target_item["id"])
            await self._send_cart_update()
            return f"Removed {target_item['name']} from your cart. Your new total is ${self.cart.get_total():.2f}."
        else:
            self.cart.update_quantity(target_item["id"], new_quantity)
            await self._send_cart_update()
            
            logger.info(f"Updated quantity: {target_item['name']} from {old_quantity} to {new_quantity}")
            
            return f"Updated {target_item['name']} quantity from {old_quantity} to {new_quantity}. Your new total is ${self.cart.get_total():.2f}."
    
    @function_tool
    async def get_customer_info(self, context: RunContext, name: str, address: str = ""):
        """Collect customer information for the order.
        
        Args:
            name: Customer's name
            address: Customer's delivery address (optional)
        """
        self.cart.customer_name = name
        if address:
            self.cart.customer_address = address
        
        await self._send_cart_update()
        
        logger.info(f"Customer info: {name}, {address}")
        
        if address:
            return f"Got it! Order for {name}, delivering to {address}."
        else:
            return f"Thanks {name}! If you need delivery, just let me know your address."
    
    @function_tool
    async def complete_order(self, context: RunContext):
        """Complete the order and save it to a JSON file."""
        if not self.cart.items:
            return "Your cart is empty! Add some items before placing your order."
        
        if not self.cart.customer_name:
            return "I need your name to complete the order. What's your name?"
        
        # Create order data
        timestamp = datetime.now()
        order_data = {
            "order_id": f"ORDER_{timestamp.strftime('%Y%m%d_%H%M%S')}_{self.cart.customer_name.replace(' ', '')}",
            "timestamp": timestamp.isoformat(),
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S"),
            "customer": {
                "name": self.cart.customer_name,
                "address": self.cart.customer_address or "Pickup"
            },
            "items": self.cart.items,
            "summary": {
                "total_items": self.cart.get_item_count(),
                "subtotal": self.cart.get_total(),
                "tax": round(self.cart.get_total() * 0.08, 2),  # 8% tax
                "total": round(self.cart.get_total() * 1.08, 2)
            },
            "status": "confirmed"
        }
        
        # Create orders directory if it doesn't exist
        os.makedirs(self.orders_dir, exist_ok=True)
        
        # Save order to JSON file
        order_filename = f"{self.orders_dir}/{order_data['order_id']}.json"
        try:
            with open(order_filename, 'w') as f:
                json.dump(order_data, f, indent=2)
            
            logger.info(f"Order saved: {order_filename}")
            
            # Send completion notification
            if self._room:
                completion_data = {
                    "type": "order_complete",
                    "data": order_data
                }
                await self._room.local_participant.publish_data(
                    json.dumps(completion_data).encode('utf-8'),
                    topic="food_order"
                )
            
            # Create confirmation message
            delivery_text = f"for delivery to {self.cart.customer_address}" if self.cart.customer_address else "for pickup"
            
            confirmation = f"Perfect! Your order has been placed and saved as {order_data['order_id']}.\n\n"
            confirmation += f"Order Summary for {self.cart.customer_name}:\n"
            confirmation += f"• {self.cart.get_item_count()} items\n"
            confirmation += f"• Subtotal: ${order_data['summary']['subtotal']:.2f}\n"
            confirmation += f"• Tax: ${order_data['summary']['tax']:.2f}\n"
            confirmation += f"• Total: ${order_data['summary']['total']:.2f}\n\n"
            confirmation += f"Order {delivery_text} - we'll have it ready soon! Is there anything else I can help you with?"
            
            # Mark order as complete and clear cart
            self.cart.order_complete = True
            await self._send_cart_update()
            
            # Clear cart for next order
            self.cart = CartState()
            
            return confirmation
            
        except Exception as e:
            logger.error(f"Failed to save order: {e}")
            return f"I've confirmed your order for {self.cart.customer_name}, but there was an issue saving it. Don't worry - we have all your details and will process it manually!"
