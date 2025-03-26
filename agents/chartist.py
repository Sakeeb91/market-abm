"""
Chartist agent implementation.
"""
import numpy as np
from agents.base_agent import BaseAgent


class Chartist(BaseAgent):
    """
    Chartist agent bases trading decisions on price trends and patterns.
    
    Chartists (also known as technical traders) believe that past price
    movements can predict future price movements. They buy when they
    identify upward trends and sell when they identify downward trends.
    
    Attributes:
        memory (int): Number of past prices to consider
        sensitivity (float): Sensitivity to price trends
        confidence (float): Confidence in technical signals
    """
    
    def __init__(self, agent_id, initial_cash, initial_position=0,
                 memory=20, sensitivity=0.1, confidence=0.7):
        """
        Initialize a chartist agent.
        
        Args:
            agent_id (int): Unique identifier for the agent
            initial_cash (float): Initial cash amount
            initial_position (int): Initial position (number of shares)
            memory (int): Length of price history to consider
            sensitivity (float): Sensitivity to price trends
            confidence (float): Confidence in technical signals
        """
        super().__init__(agent_id, initial_cash, initial_position)
        self.memory = memory
        self.sensitivity = sensitivity
        self.confidence = confidence
    
    def analyze_trend(self, price_history):
        """
        Analyze the price trend from recent history.
        
        Args:
            price_history (list): List of historical prices
            
        Returns:
            float: Trend signal (-1 to 1, negative for downtrend, positive for uptrend)
        """
        if len(price_history) < self.memory:
            return 0  # Not enough data
            
        # Get the most recent prices up to memory length
        recent_prices = price_history[-self.memory:]
        
        # Calculate short and long moving averages - use shorter windows to be more responsive
        short_window = max(2, self.memory // 5)  # Shorter window (was memory // 4)
        long_window = self.memory
        
        short_ma = np.mean(recent_prices[-short_window:])
        long_ma = np.mean(recent_prices)
        
        # Calculate momentum (rate of change) - use shorter lookback to be more responsive
        momentum_window = min(3, len(recent_prices))  # Was 5, now 3
        momentum = (recent_prices[-1] / recent_prices[-momentum_window] - 1)
        
        # Calculate volatility
        volatility = np.std(recent_prices) / np.mean(recent_prices)
        
        # Combine signals into a trend indicator - give more weight to momentum
        ma_signal = (short_ma - long_ma) / long_ma
        trend_signal = (ma_signal + 1.5 * momentum) * (1 - volatility)  # Increased momentum weight from 1 to 1.5
        
        # Apply confidence and sensitivity
        trend_signal = trend_signal * self.confidence * self.sensitivity
        
        # Clip to reasonable range
        return np.clip(trend_signal, -1.0, 1.0)
    
    def decide_action(self, market):
        """
        Decide on trading action based on identified price trends.
        
        Args:
            market: The market environment
            
        Returns:
            tuple: (action_type, quantity, price)
        """
        # Get current market state
        current_price = market.current_price
        price_history = market.price_history
        
        # Calculate trend signal
        trend = self.analyze_trend(price_history)
        
        print(f"Agent {self.agent_id} (Chartist): Current price: {current_price:.2f}, Trend signal: {trend:.4f}")
        print(f"  Cash: {self.cash:.2f}, Position: {self.position}")
        
        # Lower threshold even further for action to encourage more trading
        if abs(trend) < 0.02:  # Was 0.05, now 0.02
            print(f"  Decision: HOLD (no strong trend)")
            return 'hold', 0, None
        
        # Calculate position size based on trend strength and cash - more aggressive
        position_change = int(self.cash * abs(trend) * 3 / current_price)  # Increased from 2 to 3
        
        if trend > 0:
            # Bullish signal - buy
            max_new_position = min(
                int(self.cash / current_price * 0.7),  # Use at most 70% of cash, was 50%
                market.max_position - self.position  # Position limit
            )
            
            print(f"  Bullish signal. Desired position change: {position_change}, Max new position: {max_new_position}")
            
            # Ensure at least 1 share
            quantity = max(1, min(position_change, max_new_position))
            if self.cash < quantity * current_price:
                print(f"  Decision: HOLD (not enough cash)")
                return 'hold', 0, None
                
            # Calculate buy price with tighter spread to facilitate matching
            price = current_price * (1 + np.random.uniform(0, 0.002))
            print(f"  Decision: BUY {quantity} at {price:.2f}")
            return 'buy', quantity, price
            
        else:
            # Bearish signal - sell if we have shares
            if self.position > 0:
                # Ensure at least 1 share if we have shares - more aggressive selling
                quantity = max(1, min(abs(position_change), self.position))
                print(f"  Bearish signal. Desired sell quantity: {quantity}, Current position: {self.position}")
                
                # Calculate sell price with tighter spread to facilitate matching
                price = current_price * (1 - np.random.uniform(0, 0.002))
                print(f"  Decision: SELL {quantity} at {price:.2f}")
                return 'sell', quantity, price
            else:
                print(f"  Decision: HOLD (no shares to sell)")
                return 'hold', 0, None 