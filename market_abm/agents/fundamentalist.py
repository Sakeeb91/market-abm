"""
Fundamentalist agent implementation.
"""
import numpy as np
from agents.base_agent import BaseAgent


class Fundamentalist(BaseAgent):
    """
    Fundamentalist agent bases trading decisions on the gap between 
    current market price and perceived fundamental value.
    
    Fundamentalists believe the price will eventually revert to the fundamental value.
    They buy when the price is below fundamental value and sell when it's above.
    
    Attributes:
        confidence (float): Confidence in the fundamental value (0-1)
        reaction_speed (float): How quickly to react to price-value gaps
    """
    
    def __init__(self, agent_id, initial_cash, initial_position=0, 
                 confidence=0.8, reaction_speed=0.1):
        """
        Initialize a fundamentalist agent.
        
        Args:
            agent_id (int): Unique identifier for the agent
            initial_cash (float): Initial cash amount
            initial_position (int): Initial position (number of shares)
            confidence (float): Confidence in fundamental value (0-1)
            reaction_speed (float): Speed of reaction to price-value gaps
        """
        super().__init__(agent_id, initial_cash, initial_position)
        self.confidence = confidence
        self.reaction_speed = reaction_speed
        
    def estimate_fundamental_value(self, market):
        """
        Estimate the fundamental value based on market's true fundamental value
        with some noise to represent imperfect information.
        
        Args:
            market: The market environment
            
        Returns:
            float: Estimated fundamental value
        """
        # Add noise to the true fundamental value
        noise = np.random.normal(0, 0.05 * market.fundamental_value * (1 - self.confidence))
        return market.fundamental_value + noise
        
    def decide_action(self, market):
        """
        Decide on trading action based on the gap between market price
        and fundamental value.
        
        Args:
            market: The market environment
            
        Returns:
            tuple: (action_type, quantity, price)
        """
        # Get current market state
        current_price = market.current_price
        
        # Estimate fundamental value
        estimated_value = self.estimate_fundamental_value(market)
        
        # Calculate the mispricing signal
        mispricing = estimated_value - current_price
        
        print(f"Agent {self.agent_id} (Fundamentalist): Current price: {current_price:.2f}, Est. value: {estimated_value:.2f}, Mispricing: {mispricing:.2f}")
        print(f"  Cash: {self.cash:.2f}, Position: {self.position}")
        
        # Further lower threshold to 0.2% to encourage even more trading
        if abs(mispricing) < 0.002 * current_price:
            # If price is very close to fundamental value, hold
            print(f"  Decision: HOLD (mispricing too small)")
            return 'hold', 0, None
            
        # Calculate the desired position change based on mispricing - even more aggressive
        position_change = int(self.reaction_speed * 3 * mispricing * self.cash / current_price)
        
        # Apply position limits - allow using more cash per trade
        max_new_position = min(
            int(self.cash / current_price * 0.7),  # Use at most 70% of cash for a single trade
            market.max_position - self.position  # Position limit
        )
        
        print(f"  Desired position change: {position_change}, Max new position: {max_new_position}")
        
        if mispricing > 0:  # Underpriced - buy
            # Buy signal - ensure at least 1 share if positive signal
            quantity = max(1, min(position_change, max_new_position))
            if self.cash < quantity * current_price:
                print(f"  Decision: HOLD (not enough cash)")
                return 'hold', 0, None
                
            # Calculate buy price with tighter spread to facilitate matching
            price = current_price * (1 + np.random.uniform(0, 0.002))
            print(f"  Decision: BUY {quantity} at {price:.2f}")
            return 'buy', quantity, price
            
        else:  # Overpriced - sell
            # Sell signal - ensure at least 1 share if negative signal and have shares
            if self.position > 0:
                # More aggressive selling - willing to sell a larger portion of position
                quantity = max(1, min(abs(position_change), self.position))
                
                # Calculate sell price with tighter spread to facilitate matching
                price = current_price * (1 - np.random.uniform(0, 0.002))
                print(f"  Decision: SELL {quantity} at {price:.2f}")
                return 'sell', quantity, price
            else:
                print(f"  Decision: HOLD (no shares to sell)")
                return 'hold', 0, None 