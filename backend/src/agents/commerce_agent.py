import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from livekit.agents import Agent, function_tool, RunContext

logger = logging.getLogger("commerce_agent")


# Product Catalog Manager (ACP-inspired merchant layer)
class ProductCatalog:
    def __init__(self, catalog_file: str = "shared-data/commerce_catalog.json"):
        # Ensure we use the correct path relative to where the agent runs
        import os
        if not os.path.isabs(catalog_file) and not os.path.exists(catalog_file):
            # Try from backend directory
            catalog_file = os.path.join(os.path.dirname(__file__), "..", "..", catalog_file)
        self.catalog_file = catalog_file
        self.products = self._load_catalog()
    
    def _load_catalog(self) -> Dict[str, Dict]:
        """Load product catalog from JSON file."""
        try:
            with open(self.catalog_file, 'r') as f:
                data = json.load(f)
                # Create a dictionary indexed by product ID
                return {p["id"]: p for p in data.get("products", [])}
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            return {}
    
    def list_products(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List products with optional filtering.
        
        Args:
            filters: Optional dict with keys like 'category', 'max_price', 'color', etc.
        """
        products = list(self.products.values())
        
        if not filters:
            return products
        
        filtered = []
        for product in products:
            match = True
            
            # Filter by category
            if "category" in filters:
                if product["category"].lower() != filters["category"].lower():
                    match = False
            
            # Filter by max price
            if "max_price" in filters:
                if product["price"] > filters["max_price"]:
                    match = False
            
            # Filter by color (in attributes)
            if "color" in filters:
                product_color = product.get("attributes", {}).get("color", "")
                if product_color.lower() != filters["color"].lower():
                    match = False
            
            # Filter by search term (name or description)
            if "search" in filters:
                search_term = filters["search"].lower()
                if (search_term not in product["name"].lower() and 
                    search_term not in product["description"].lower()):
                    match = False
            
            if match:
                filtered.append(product)
        
        return filtered
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get a specific product by ID."""
        return self.products.get(product_id)


# Order Manager (ACP-inspired order creation)
class OrderManager:
    def __init__(self, orders_dir: str = "orders"):
        self.orders_dir = orders_dir
        self.orders = []  # In-memory orders for current session
        os.makedirs(orders_dir, exist_ok=True)
    
    def create_order(self, line_items: List[Dict], customer_info: Optional[Dict] = None) -> Dict:
        """Create an order from line items.
        
        Args:
            line_items: List of dicts with 'product_id', 'quantity', and optional 'size'
            customer_info: Optional customer information
        
        Returns:
            Order dict with id, items, total, currency, created_at
        """
        order_id = f"ORD-{uuid4().hex[:8].upper()}"
        timestamp = datetime.now()
        
        # Calculate total and build order items
        order_items = []
        total = 0
        
        for item in line_items:
            product_id = item["product_id"]
            quantity = item.get("quantity", 1)
            size = item.get("size")
            
            # This would normally fetch from catalog
            # For now, we'll include the product info in the item
            order_item = {
                "product_id": product_id,
                "quantity": quantity,
                "price": item.get("price", 0),
                "subtotal": item.get("price", 0) * quantity
            }
            
            if size:
                order_item["size"] = size
            
            order_items.append(order_item)
            total += order_item["subtotal"]
        
        order = {
            "id": order_id,
            "items": order_items,
            "total": total,
            "currency": "INR",
            "created_at": timestamp.isoformat(),
            "status": "pending",
            "customer": customer_info or {}
        }
        
        # Store in memory
        self.orders.append(order)
        
        # Persist to file
        self._save_order(order)
        
        return order
    
    def _save_order(self, order: Dict):
        """Save order to JSON file."""
        try:
            filename = f"{self.orders_dir}/{order['id']}.json"
            with open(filename, 'w') as f:
                json.dump(order, f, indent=2)
            logger.info(f"Order saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save order: {e}")
    
    def get_last_order(self) -> Optional[Dict]:
        """Get the most recent order."""
        if self.orders:
            return self.orders[-1]
        return None


# E-commerce Agent (ACP-inspired)
class CommerceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are Sam, a friendly and helpful voice shopping assistant following the Agentic Commerce Protocol.

            Your personality:
            - Warm, enthusiastic, and professional
            - Knowledgeable about products
            - Patient and helpful with browsing
            - Clear about pricing and availability
            - Efficient at processing orders

            Your role:
            1. Help customers browse the product catalog
            2. Answer questions about products (price, colors, sizes, materials)
            3. Add items to their shopping cart
            4. Process orders and confirm details
            5. Provide order summaries

            Product categories available:
            - Mugs and drinkware
            - Clothing (t-shirts, hoodies)
            - Stationery (notebooks, pens)
            - Bags and backpacks
            - Accessories (water bottles, etc.)

            Guidelines:
            - When customers ask to browse, use search_catalog to find relevant products
            - Always mention price and key attributes when describing products
            - For clothing, ask about size preferences
            - Confirm items before adding to cart
            - Keep track of what's been discussed in the conversation
            - When ready to order, use create_order to process it
            - Provide clear order confirmations with order ID

            Remember: You're making online shopping easy and conversational!"""
        )
        self.catalog = ProductCatalog()
        self.order_manager = OrderManager()
        self._room = None
        self.cart_items = []  # Track items customer wants to buy
        self.last_shown_products = []  # Track recently shown products for reference
    
    def set_room(self, room):
        """Set the room for sending data updates."""
        self._room = room
    
    async def _send_cart_update(self):
        """Send cart update to frontend."""
        if self._room:
            try:
                cart_data = {
                    "type": "cart_update",
                    "data": {
                        "items": self.cart_items,
                        "count": len(self.cart_items),
                        "total": sum(item.get("subtotal", 0) for item in self.cart_items)
                    }
                }
                await self._room.local_participant.publish_data(
                    json.dumps(cart_data).encode('utf-8'),
                    topic="commerce"
                )
            except Exception as e:
                logger.error(f"Failed to send cart update: {e}")
    
    @function_tool
    async def search_catalog(
        self, 
        context: RunContext, 
        search_term: str = "", 
        category: str = "", 
        max_price: int = 0,
        color: str = ""
    ):
        """Search the product catalog with filters.
        
        Args:
            search_term: Search in product names and descriptions
            category: Filter by category (mug, clothing, stationery, bags, accessories)
            max_price: Maximum price in INR (0 for no limit)
            color: Filter by color
        """
        filters = {}
        
        if search_term:
            filters["search"] = search_term
        if category:
            filters["category"] = category
        if max_price > 0:
            filters["max_price"] = max_price
        if color:
            filters["color"] = color
        
        products = self.catalog.list_products(filters if filters else None)
        
        if not products:
            return f"I couldn't find any products matching your criteria. Try browsing our categories: mugs, clothing, stationery, bags, or accessories."
        
        # Store for reference
        self.last_shown_products = products[:5]
        
        if len(products) == 1:
            p = products[0]
            attrs = p.get("attributes", {})
            attr_text = ", ".join([f"{k}: {v}" for k, v in attrs.items() if k != "sizes"])
            return f"I found the {p['name']} for ₹{p['price']}. {p['description']}. {attr_text}. Would you like to add this to your cart?"
        
        # Multiple products
        result = f"I found {len(products)} products"
        if filters:
            result += f" matching your search"
        result += ":\n\n"
        
        for i, p in enumerate(products[:5], 1):
            attrs = p.get("attributes", {})
            color_text = f" ({attrs.get('color')})" if attrs.get('color') else ""
            result += f"{i}. {p['name']}{color_text} - ₹{p['price']}\n"
        
        if len(products) > 5:
            result += f"\n...and {len(products) - 5} more items."
        
        result += "\n\nWhich one interests you?"
        
        return result
    
    @function_tool
    async def get_product_details(self, context: RunContext, product_reference: str):
        """Get detailed information about a specific product.
        
        Args:
            product_reference: Product name, number from list, or product ID
        """
        # Try to match from recently shown products
        product = None
        
        # Check if it's a number reference (e.g., "second one", "number 2")
        try:
            # Extract number from reference
            num = None
            if "first" in product_reference.lower() or product_reference == "1":
                num = 0
            elif "second" in product_reference.lower() or product_reference == "2":
                num = 1
            elif "third" in product_reference.lower() or product_reference == "3":
                num = 2
            elif product_reference.isdigit():
                num = int(product_reference) - 1
            
            if num is not None and 0 <= num < len(self.last_shown_products):
                product = self.last_shown_products[num]
        except:
            pass
        
        # Try searching by name
        if not product:
            products = self.catalog.list_products({"search": product_reference})
            if products:
                product = products[0]
        
        if not product:
            return f"I couldn't find that product. Could you be more specific or search again?"
        
        attrs = product.get("attributes", {})
        result = f"{product['name']} - ₹{product['price']}\n\n"
        result += f"{product['description']}\n\n"
        result += "Details:\n"
        for key, value in attrs.items():
            if key == "sizes":
                result += f"• Available sizes: {', '.join(value)}\n"
            else:
                result += f"• {key.capitalize()}: {value}\n"
        
        return result
    
    @function_tool
    async def add_to_cart(
        self, 
        context: RunContext, 
        product_reference: str, 
        quantity: int = 1,
        size: str = ""
    ):
        """Add a product to the shopping cart.
        
        Args:
            product_reference: Product name, number from list, or product ID
            quantity: How many to add (default: 1)
            size: Size for clothing items (S, M, L, XL)
        """
        # Find the product
        product = None
        
        # Check if it's a number reference
        try:
            num = None
            if "first" in product_reference.lower() or product_reference == "1":
                num = 0
            elif "second" in product_reference.lower() or product_reference == "2":
                num = 1
            elif "third" in product_reference.lower() or product_reference == "3":
                num = 2
            elif product_reference.isdigit():
                num = int(product_reference) - 1
            
            if num is not None and 0 <= num < len(self.last_shown_products):
                product = self.last_shown_products[num]
        except:
            pass
        
        # Try searching by name
        if not product:
            products = self.catalog.list_products({"search": product_reference})
            if products:
                product = products[0]
        
        if not product:
            return f"I couldn't find that product. Could you search for it first?"
        
        # Check if size is needed
        if product["category"] == "clothing" and not size:
            sizes = product.get("attributes", {}).get("sizes", [])
            if sizes:
                return f"What size would you like for the {product['name']}? Available sizes: {', '.join(sizes)}"
        
        # Add to cart
        cart_item = {
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "subtotal": product["price"] * quantity
        }
        
        if size:
            cart_item["size"] = size
        
        self.cart_items.append(cart_item)
        await self._send_cart_update()
        
        size_text = f" in size {size}" if size else ""
        logger.info(f"Added to cart: {quantity}x {product['name']}{size_text}")
        
        total = sum(item.get("subtotal", 0) for item in self.cart_items)
        return f"Added {quantity}x {product['name']}{size_text} to your cart for ₹{cart_item['subtotal']}. Your cart total is now ₹{total}."
    
    @function_tool
    async def view_cart(self, context: RunContext):
        """View the current shopping cart."""
        if not self.cart_items:
            return "Your cart is empty. What would you like to shop for?"
        
        result = f"Your cart ({len(self.cart_items)} items):\n\n"
        
        for item in self.cart_items:
            size_text = f" (Size: {item['size']})" if item.get('size') else ""
            result += f"• {item['quantity']}x {item['name']}{size_text} - ₹{item['subtotal']}\n"
        
        total = sum(item.get("subtotal", 0) for item in self.cart_items)
        result += f"\nTotal: ₹{total}"
        
        return result
    
    @function_tool
    async def place_order(self, context: RunContext, customer_name: str = "", customer_address: str = ""):
        """Place the order and complete the purchase.
        
        Args:
            customer_name: Customer's name
            customer_address: Delivery address
        """
        if not self.cart_items:
            return "Your cart is empty! Add some items before placing an order."
        
        # Prepare line items for order
        line_items = []
        for item in self.cart_items:
            line_item = {
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "price": item["price"]
            }
            if item.get("size"):
                line_item["size"] = item["size"]
            line_items.append(line_item)
        
        # Customer info
        customer_info = {}
        if customer_name:
            customer_info["name"] = customer_name
        if customer_address:
            customer_info["address"] = customer_address
        
        # Create order
        order = self.order_manager.create_order(line_items, customer_info)
        
        # Send order confirmation
        if self._room:
            try:
                order_data = {
                    "type": "order_complete",
                    "data": order
                }
                await self._room.local_participant.publish_data(
                    json.dumps(order_data).encode('utf-8'),
                    topic="commerce"
                )
            except Exception as e:
                logger.error(f"Failed to send order confirmation: {e}")
        
        # Build confirmation message
        confirmation = f"Order placed successfully! Your order ID is {order['id']}.\n\n"
        confirmation += f"Order Summary:\n"
        
        for item in self.cart_items:
            size_text = f" (Size: {item['size']})" if item.get('size') else ""
            confirmation += f"• {item['quantity']}x {item['name']}{size_text} - ₹{item['subtotal']}\n"
        
        confirmation += f"\nTotal: ₹{order['total']}\n"
        
        if customer_name:
            confirmation += f"\nOrder for: {customer_name}"
        if customer_address:
            confirmation += f"\nDelivering to: {customer_address}"
        
        confirmation += "\n\nThank you for shopping with us! Is there anything else I can help you with?"
        
        # Clear cart
        self.cart_items = []
        await self._send_cart_update()
        
        return confirmation
    
    @function_tool
    async def get_last_order(self, context: RunContext):
        """Get information about the most recent order."""
        order = self.order_manager.get_last_order()
        
        if not order:
            return "You haven't placed any orders yet."
        
        result = f"Your last order ({order['id']}):\n\n"
        
        for item in order["items"]:
            size_text = f" (Size: {item['size']})" if item.get('size') else ""
            result += f"• {item['quantity']}x Product {item['product_id']}{size_text} - ₹{item['subtotal']}\n"
        
        result += f"\nTotal: ₹{order['total']}\n"
        result += f"Status: {order['status']}\n"
        result += f"Ordered at: {order['created_at']}"
        
        return result
