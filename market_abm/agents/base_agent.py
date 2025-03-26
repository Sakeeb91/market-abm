"""
Base agent class for the market ABM.
"""
from abc import ABC, abstractmethod
import numpy as np


class BaseAgent(ABC):
    """
    Abstract base class for all trading agents.
    
    Attributes:
        agent_id (int): Unique identifier for the agent
        cash (float): Amount of cash held by the agent
        position (int): Number of shares held by the agent
        wealth_history (list): History of agent's total wealth
        position_history (list): History of agent's positions
        trade_history (list): History of agent's trades
    """
    
    def __init__(self, agent_id, initial_cash, initial_position=0):
        """
        Initialize the agent.
        
        Args:
            agent_id (int): Unique identifier for the agent
            initial_cash (float): Initial cash amount
            initial_position (int): Initial position (number of shares)
        """
        self.agent_id = agent_id
        self.cash = initial_cash
        self.position = initial_position
        
        # For tracking performance and behavior
        self.wealth_history = [initial_cash]
        self.position_history = [initial_position]
        self.trade_history = []
    
    @abstractmethod
    def decide_action(self, market):
        """
        Decide what action to take based on market conditions.
        
        Args:
            market: The market environment
            
        Returns:
            tuple: (action_type, quantity, price)
                action_type: 'buy', 'sell', or 'hold'
                quantity: Number of shares to buy/sell
                price: Price willing to pay/accept (or None for market orders)
        """
        pass
    
    def update_wealth(self, current_price):
        """
        Update the agent's wealth based on the current market price.
        
        Args:
            current_price (float): Current market price
        """
        total_wealth = self.cash + self.position * current_price
        self.wealth_history.append(total_wealth)
        self.position_history.append(self.position)
        print(f"Agent {self.agent_id} updating wealth - Position: {self.position}, Total wealth: {total_wealth:.2f}")
    
    def execute_trade(self, action_type, quantity, execution_price, transaction_cost_rate=0.001):
        """
        Execute a trade and update the agent's state.
        
        Args:
            action_type (str): 'buy' or 'sell'
            quantity (int): Number of shares traded
            execution_price (float): Price at which the trade was executed
            transaction_cost_rate (float): Transaction cost as a fraction of trade value
            
        Returns:
            bool: True if trade was successful, False otherwise
        """
        print(f"Agent {self.agent_id} executing {action_type} trade: {quantity} @ {execution_price:.2f}")
        print(f"  Before trade - Cash: {self.cash:.2f}, Position: {self.position}")
        
        if action_type == 'buy':
            # Calculate trade value and transaction cost
            trade_value = quantity * execution_price
            transaction_cost = trade_value * transaction_cost_rate
            total_cost = trade_value + transaction_cost
            
            # Check if agent has enough cash
            if self.cash >= total_cost:
                self.cash -= total_cost
                self.position += quantity
                self.trade_history.append((action_type, quantity, execution_price))
                print(f"  After trade - Cash: {self.cash:.2f}, Position: {self.position}")
                return True
            print(f"  Trade failed - Not enough cash. Need {total_cost:.2f}, have {self.cash:.2f}")
            return False
            
        elif action_type == 'sell':
            # Check if agent has enough shares
            if self.position >= quantity:
                # Calculate trade value and transaction cost
                trade_value = quantity * execution_price
                transaction_cost = trade_value * transaction_cost_rate
                net_proceeds = trade_value - transaction_cost
                
                self.cash += net_proceeds
                self.position -= quantity
                self.trade_history.append((action_type, quantity, execution_price))
                print(f"  After trade - Cash: {self.cash:.2f}, Position: {self.position}")
                return True
            print(f"  Trade failed - Not enough shares. Need {quantity}, have {self.position}")
            return False
            
        return False  # Invalid action_type 