"""
Noise trader agent implementation.
"""
import numpy as np
from agents.base_agent import BaseAgent


class NoiseTrader(BaseAgent):
    """
    Noise trader agent that makes random trading decisions to add liquidity.
    
    Noise traders represent market participants who trade for reasons
    unrelated to fundamentals or technical analysis, such as liquidity
    needs, portfolio rebalancing, or behavioral biases.
    
    Attributes:
        trade_probability (float): Probability of initiating a trade in each step
        max_order_size (int): Maximum order size
        price_range (float): Maximum price deviation from current price (%)
    """
    
    def __init__(self, agent_id, initial_cash, initial_position=0,
                 trade_probability=0.3, max_order_size=10, price_range=0.01):
        """
        Initialize a noise trader agent.
        
        Args:
            agent_id (int): Unique identifier for the agent
            initial_cash (float): Initial cash amount
            initial_position (int): Initial position (number of shares)
            trade_probability (float): Probability of trading in each step (0-1)
            max_order_size (int): Maximum order size
            price_range (float): Maximum price deviation from current price (%)
        """
        super().__init__(agent_id, initial_cash, initial_position)
        self.trade_probability = trade_probability
        self.max_order_size = max_order_size
        self.price_range = price_range
    
    def decide_action(self, market):
        """
        Decide on trading action randomly.
        
        Args:
            market: The market environment
            
        Returns:
            tuple: (action_type, quantity, price)
        """
        # Get current market state
        current_price = market.current_price
        
        print(f"Agent {self.agent_id} (NoiseTrader): Current price: {current_price:.2f}")
        print(f"  Cash: {self.cash:.2f}, Position: {self.position}")
        
        # Randomly decide whether to trade
        if np.random.random() > self.trade_probability:
            print(f"  Decision: HOLD (random)")
            return 'hold', 0, None
        
        # Randomly decide to buy or sell
        action = np.random.choice(['buy', 'sell'])
        
        # Determine quantity (1 to max_order_size)
        quantity = np.random.randint(1, self.max_order_size + 1)
        
        # Generate price with small random deviation from current price
        price_deviation = np.random.uniform(-self.price_range, self.price_range)
        price = current_price * (1 + price_deviation)
        
        if action == 'buy':
            # Ensure agent has enough cash
            max_buy = int(self.cash / price * 0.9)  # Use at most 90% of cash
            if max_buy < 1:
                print(f"  Decision: HOLD (not enough cash)")
                return 'hold', 0, None
            
            # Adjust quantity based on available cash
            quantity = min(quantity, max_buy)
            print(f"  Decision: BUY {quantity} at {price:.2f}")
            return 'buy', quantity, price
        
        else:  # sell
            # Ensure agent has enough shares
            if self.position < 1:
                print(f"  Decision: HOLD (no shares to sell)")
                return 'hold', 0, None
            
            # Adjust quantity based on available shares
            quantity = min(quantity, self.position)
            print(f"  Decision: SELL {quantity} at {price:.2f}")
            return 'sell', quantity, price 