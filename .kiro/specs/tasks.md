- [x] 12. you have to do the next task that is Primary Goal (MVP) – Food & Grocery Ordering + Cart → Order JSON





Objective:
Build a voice agent that lets a user order food and groceries from a catalog, intelligently adds items to a cart (including bundled ingredients), keeps track of the order, and saves the final order to a JSON file when the user is done.

Tasks
Create a catalog JSON file

Design a JSON file (name of your choice) that describes your food and grocery catalog.
Include multiple categories, for example:
Groceries (bread, eggs, milk, etc.)
Snacks
Prepared food (pizzas, sandwiches, etc.)
Each item should have sensible fields, such as:
Item name
Category
Price
Optional attributes (brand, size, units, tags like “vegan”, “gluten-free”, etc.)
Keep it small but diverse enough (at least 10–20 items) to make the conversation interesting.
Set up the ordering assistant persona

Make the agent behave like a friendly food & grocery ordering assistant for a fictional brand or store.
It should:
Greet the user and explain what it can do (e.g. “I can help you order groceries and simple meal ingredients.”).
Ask for clarifications when needed (size, brand, quantity, etc.).
Implement cart management

Maintain a cart in scenario state that can store:
Items selected
Quantities
Any relevant notes or options (e.g. “whole wheat bread”, “large peanut butter”).
Support basic operations:
Adding items (with quantity).
Removing items.
Updating quantities.
Listing what’s currently in the cart when asked (“What’s in my cart?”).
Ensure the agent confirms key cart changes verbally so users know what’s happening.
Handle “ingredients for X” style requests intelligently

The agent should be able to understand higher-level intents, such as:
“I need ingredients for a peanut butter sandwich.”
“Get me what I need for making pasta for two people.”
For these requests:
Map the request to multiple items in your catalog (e.g. bread + peanut butter, or pasta + sauce, etc.).
Add all relevant items to the cart, and verbally confirm:
“I’ve added bread and peanut butter to your cart for your sandwich.”
You can:
Hard-code a small “recipes” mapping (dish → list of items).
Or infer items based on tags in your catalog.
This is the key “intelligent” behavior for the Day 7 primary goal.
Place the order and save it to a JSON file

Detect when the user is done ordering, for example when they say:
“That’s all.” / “Place my order.” / “I’m done.”
At that point:
Confirm the final cart contents and total in conversation.
Create an order object in memory containing:
Items (with quantities and prices).
Order total.
Timestamp.
Any simple customer info you choose to capture (e.g. name or address as text).
Save this order data to a JSON file:
You can choose the filename (for example, a single current_order.json or a new file per order).
After saving:
Let the user know the order has been placed and stored.
MVP Completion Checklist
You’ve completed the primary goal if:

You created a catalog JSON file with a variety of food and grocery items.
The agent can:
Add specific items and quantities to a cart.
Intelligently add multiple items for simple “ingredients for X” requests.
Show/list the cart when asked.
When the user is done:
The agent confirms the final order.
The order is written to a JSON file (representing “order placed”).
Note: You can use JSON or a database. You are not restricted to use database

Resources
https://docs.livekit.io/agents/build/prompting/
https://docs.livekit.io/agents/build/tools/
Advanced Goals (Optional, Higher Impact)
The main advanced goal for Day 7 is to build a mock order tracking solution: 


- [ ] 2. Create frontend for this and remove the unnecessary files from the project except all the agents , dont delete agents(coffee, health, tutor, sdr, fraud, food and grocery)