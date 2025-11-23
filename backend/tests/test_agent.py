import pytest
from livekit.agents import AgentSession, inference, llm

from agent import CoffeeShopBarista


def _llm() -> llm.LLM:
    return inference.LLM(model="openai/gpt-4.1-mini")


@pytest.mark.asyncio
async def test_coffee_barista_greeting() -> None:
    """Evaluation of the coffee barista's friendly greeting."""
    async with (
        _llm() as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(CoffeeShopBarista())

        # Run an agent turn following the user's greeting
        result = await session.run(user_input="Hello")

        # Evaluate the agent's response for coffee shop greeting
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm,
                intent="""
                Greets the user as a friendly coffee shop barista would.

                Should include:
                - Friendly, welcoming greeting
                - Coffee shop context (mentions coffee, drinks, or ordering)
                - Barista personality (Rav from Brew & Bean Coffee Shop)
                - Offer to help with coffee order
                """,
            )
        )

        # Ensures there are no function calls or other unexpected events
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_coffee_order_taking() -> None:
    """Evaluation of the barista's ability to take coffee orders."""
    async with (
        _llm() as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(CoffeeShopBarista())

        # Run an agent turn following the user's coffee order request
        result = await session.run(user_input="I'd like to order a coffee")

        # Evaluate the agent's response for order taking behavior
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm,
                intent="""
                Responds as a coffee shop barista taking an order.

                Should include:
                - Acknowledgment of the order request
                - Questions about drink preferences (type, size, milk, etc.)
                - Friendly, helpful tone
                - Coffee shop context
                """,
            )
        )

        # May include function calls to update order state
        # result.expect.no_more_events()


@pytest.mark.asyncio
async def test_stays_in_coffee_context() -> None:
    """Evaluation of the barista's ability to stay focused on coffee orders."""
    async with (
        _llm() as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(CoffeeShopBarista())

        # Run an agent turn following an off-topic request
        result = await session.run(
            user_input="What's the weather like today?"
        )

        # Evaluate the agent's response for staying in coffee context
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm,
                intent="""
                Politely redirects conversation back to coffee orders while maintaining friendly barista persona.

                Should include:
                - Acknowledgment of the question
                - Gentle redirection to coffee/ordering
                - Maintains Maya's friendly barista personality
                - Offers to help with coffee order instead
                """,
            )
        )

        # Ensures there are no function calls or other unexpected events
        result.expect.no_more_events()
