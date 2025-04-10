from microchain import Function
from prediction_market_agent_tooling.gtypes import USD
from prediction_market_agent_tooling.markets.markets import MarketType
from prediction_market_agent_tooling.markets.omen.data_models import (
    OMEN_BINARY_MARKET_OUTCOMES,
    TEST_CATEGORY,
)
from prediction_market_agent_tooling.markets.omen.omen import (
    omen_create_market_tx,
    redeem_from_all_user_positions,
)
from prediction_market_agent_tooling.tools.datetime_utc import DatetimeUTC

from prediction_market_agent.agents.microchain_agent.utils import get_balance
from prediction_market_agent.utils import APIKeys


class RedeemWinningBets(Function):
    @property
    def description(self) -> str:
        return "Use this function to redeem winnings from a position that you opened which has already been resolved. Use this to retrieve funds from a bet you placed in a market, after the market has been resolved. If you have outstanding winnings to be redeemed, your balance will be updated."

    @property
    def example_args(self) -> list[str]:
        return []

    def __call__(self) -> str:
        keys = APIKeys()
        prev_balance = get_balance(keys, market_type=MarketType.OMEN)
        redeem_from_all_user_positions(keys)
        new_balance = get_balance(keys, market_type=MarketType.OMEN)
        if redeemed_amount := new_balance - prev_balance > 0:
            return (
                f"Redeemed {redeemed_amount} USD in winnings. New "
                f"balance: {new_balance} USD."
            )
        return f"No winnings to redeem. Balance remains: {new_balance} USD."


class CreatePredictionMarket(Function):
    @property
    def description(self) -> str:
        return f"""Use this function to create a new prediction market on Omen.
Question of the prediction market can only be binary, in the Yes/No format.
Questions can not have violent nature.
Question must be explicit and as clear as possible.
You need to provide liquidity in USD to incentivize other users to participate in the market. The bigger the liquidity, the more likely the market will be successful.
"""

    @property
    def example_args(self) -> list[str | float]:
        return [
            "Will GNO hit $1000 dollars by the end of 2024?",
            1.0,
            "2024-12-31T23:59:59Z",
        ]

    def __call__(self, question: str, liquidity_usd: float, closing_time: str) -> str:
        keys = APIKeys()
        closing_time_date = DatetimeUTC.to_datetime_utc(closing_time)
        created_market = omen_create_market_tx(
            keys,
            initial_funds=USD(liquidity_usd),
            question=question,
            closing_time=closing_time_date,
            category=TEST_CATEGORY,  # Force test category to not show these markets on Presagio until we know it works fine.
            outcomes=OMEN_BINARY_MARKET_OUTCOMES,
            language="en",
            auto_deposit=True,
        )
        return f"Created prediction market with id {created_market.market_event.fixed_product_market_maker_checksummed} at url {created_market.url}."


# Functions that interact exclusively with Omen prediction markets
OMEN_FUNCTIONS: list[type[Function]] = [
    RedeemWinningBets,
    CreatePredictionMarket,
]
