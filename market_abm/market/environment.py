"""
Market environment implementation.
"""
import numpy as np
from collections import defaultdict


class MarketEnvironment:
    """
    The market environment manages asset prices, order matching, and market dynamics.
    
    In this simple market model, price is updated based on supply/demand imbalance.
    
    Attributes:
        current_price (float): Current market price of the asset
        fundamental_value (float): Fundamental value of the asset
        price_history (list): History of market prices
        trading_volume (list): History of trading volumes
        bid_ask_spread (float): Current bid-ask spread
        max_position (int): Maximum position size allowed for agents
        volatility (float): Volatility parameter for price formation
        agents (list): List of all agents in the market
    """
    
    def __init__(self, initial_price=100.0, initial_fundamental_value=100.0,
                 volatility=0.1, max_position=100):
        """
        Initialize the market environment.
        
        Args:
            initial_price (float): Initial market price
            initial_fundamental_value (float): Initial fundamental value
            volatility (float): Volatility parameter for price formation
            max_position (int): Maximum position size allowed for agents
        """
        self.current_price = initial_price
        self.fundamental_value = initial_fundamental_value
        self.price_history = [initial_price]
        self.fundamental_history = [initial_fundamental_value]
        self.trading_volume = [0]
        self.bid_ask_spread = 0.01 * initial_price  # 1% initial spread
        self.max_position = max_position
        self.volatility = volatility
        self.agents = []
        
        # Order books (simplified)
        self.buy_orders = []  # (agent, quantity, price)
        self.sell_orders = []  # (agent, quantity, price)
        
        # Trading statistics
        self.stats = {
            'daily_returns': [],
            'total_volume': 0,
            'transactions': []
        }
    
    def add_agent(self, agent):
        """
        Add an agent to the market.
        
        Args:
            agent: The agent to add
        """
        self.agents.append(agent)
    
    def update_fundamental_value(self, random_shock=True, trend=0.0):
        """
        Update the fundamental value of the asset.
        
        Args:
            random_shock (bool): Whether to apply a random shock
            trend (float): Trend factor for the fundamental value
        """
        old_value = self.fundamental_value
        
        if random_shock:
            # Apply a random shock to the fundamental value
            # Increase volatility of fundamental value to create more trading opportunities
            shock = np.random.normal(0, self.volatility * 2 * self.fundamental_value)
            self.fundamental_value += shock
        
        # Apply trend if specified
        self.fundamental_value *= (1 + trend)
        
        # Ensure fundamental value doesn't go negative
        self.fundamental_value = max(0.01, self.fundamental_value)
        
        # Record the new fundamental value
        self.fundamental_history.append(self.fundamental_value)
        
        print(f"Fundamental value updated: {old_value:.2f} -> {self.fundamental_value:.2f}, Change: {(self.fundamental_value - old_value):.2f}")
    
    def collect_orders(self):
        """
        Collect orders from all agents in the market.
        """
        self.buy_orders = []
        self.sell_orders = []
        
        for agent in self.agents:
            action, quantity, price = agent.decide_action(self)
            
            if action == 'buy' and quantity > 0:
                self.buy_orders.append((agent, quantity, price))
            elif action == 'sell' and quantity > 0:
                self.sell_orders.append((agent, quantity, price))
    
    def match_orders(self):
        """
        Match buy and sell orders and execute trades.
        
        This is a simplified order matching mechanism.
        """
        # Sort buy orders by price (highest first)
        buy_orders = sorted(self.buy_orders, key=lambda x: x[2], reverse=True)
        
        # Sort sell orders by price (lowest first)
        sell_orders = sorted(self.sell_orders, key=lambda x: x[2])
        
        # Diagnostic information
        print(f"Number of buy orders: {len(buy_orders)}")
        print(f"Number of sell orders: {len(sell_orders)}")
        
        # Calculate total shares in system before trading (for validation)
        total_shares_before = sum(agent.position for agent in self.agents)
        fundamentalist_shares_before = sum(agent.position for agent in self.agents if agent.__class__.__name__ == 'Fundamentalist')
        chartist_shares_before = sum(agent.position for agent in self.agents if agent.__class__.__name__ == 'Chartist')
        
        print(f"Shares before trading - Total: {total_shares_before}, Fund: {fundamentalist_shares_before}, Chart: {chartist_shares_before}")
        
        if len(buy_orders) > 0:
            print(f"Top buy order: agent {buy_orders[0][0].agent_id}, quantity {buy_orders[0][1]}, price {buy_orders[0][2]:.2f}")
        
        if len(sell_orders) > 0:
            print(f"Top sell order: agent {sell_orders[0][0].agent_id}, quantity {sell_orders[0][1]}, price {sell_orders[0][2]:.2f}")
        
        # Match orders - this is the key matching logic
        total_volume = 0
        transactions = []
        
        # Try to match multiple orders in each step
        while buy_orders and sell_orders:
            # Allow a larger price tolerance to facilitate matching (1% price adjustment)
            adjustment_factor = 1.01
            
            buy_agent, buy_quantity, buy_price = buy_orders[0]
            sell_agent, sell_quantity, sell_price = sell_orders[0]
            
            # Adjust buy price up slightly for matching purposes
            adjusted_buy_price = buy_price * adjustment_factor
            
            print(f"Trying to match: Buy {buy_price:.2f} (adjusted: {adjusted_buy_price:.2f}) >= Sell {sell_price:.2f}?")
            
            # Check if the adjusted highest bid is greater than or equal to the lowest ask
            if adjusted_buy_price >= sell_price:
                # Determine the execution price as the midpoint
                execution_price = (buy_price + sell_price) / 2
                
                # Determine the matched quantity
                matched_quantity = min(buy_quantity, sell_quantity)
                
                print(f"Match found! Buy: {buy_price:.2f}, Sell: {sell_price:.2f}, Quantity: {matched_quantity}, Execution: {execution_price:.2f}")
                
                # Execute the trades
                buy_success = buy_agent.execute_trade('buy', matched_quantity, execution_price)
                sell_success = sell_agent.execute_trade('sell', matched_quantity, execution_price)
                
                if buy_success and sell_success:
                    print(f"Trade executed successfully!")
                    total_volume += matched_quantity
                    transactions.append((buy_agent, sell_agent, matched_quantity, execution_price))
                    
                    # Update the remaining quantities
                    if buy_quantity > matched_quantity:
                        buy_orders[0] = (buy_agent, buy_quantity - matched_quantity, buy_price)
                    else:
                        buy_orders.pop(0)
                        
                    if sell_quantity > matched_quantity:
                        sell_orders[0] = (sell_agent, sell_quantity - matched_quantity, sell_price)
                    else:
                        sell_orders.pop(0)
                else:
                    # If either trade fails, remove the failed order
                    print(f"Trade execution failed! Buy success: {buy_success}, Sell success: {sell_success}")
                    if not buy_success:
                        buy_orders.pop(0)
                    if not sell_success:
                        sell_orders.pop(0)
            else:
                print(f"No match! Best buy: {buy_price:.2f} (adjusted: {adjusted_buy_price:.2f}), Best sell: {sell_price:.2f}")
                # No more matches possible with current top orders, exit the loop
                break
        
        # Calculate total shares in system after trading (for validation)
        total_shares_after = sum(agent.position for agent in self.agents)
        fundamentalist_shares_after = sum(agent.position for agent in self.agents if agent.__class__.__name__ == 'Fundamentalist')
        chartist_shares_after = sum(agent.position for agent in self.agents if agent.__class__.__name__ == 'Chartist')
        
        print(f"Shares after trading - Total: {total_shares_after}, Fund: {fundamentalist_shares_after}, Chart: {chartist_shares_after}")
        
        # Verify share conservation
        if total_shares_before != total_shares_after:
            print(f"WARNING: Share conservation violated! Before: {total_shares_before}, After: {total_shares_after}")
        
        # Record trading statistics
        self.stats['total_volume'] += total_volume
        self.stats['transactions'].extend(transactions)
        
        print(f"Total matched volume in this step: {total_volume}")
        
        # Return more detailed info
        return total_volume, transactions
    
    def update_price(self, transactions):
        """
        Update the market price based on the executed transactions.
        
        Args:
            transactions (list): List of executed transactions
        
        Returns:
            float: The new market price
        """
        if not transactions:
            # If no transactions, apply a smaller random walk to reduce volatility
            random_change = np.random.normal(0, self.volatility * 0.5 * self.current_price)
            new_price = max(0.01, self.current_price + random_change)
            print(f"No transactions to update price. Using random walk: {self.current_price:.2f} -> {new_price:.2f}")
        else:
            # Calculate the volume-weighted average price
            total_value = sum(quantity * price for _, _, quantity, price in transactions)
            total_volume = sum(quantity for _, _, quantity, _ in transactions)
            vwap = total_value / total_volume
            
            # Apply more anchoring to the previous price to avoid rapid price adjustments
            # This allows mispricings to persist longer and encourages more trading
            new_price = 0.6 * vwap + 0.4 * self.current_price  # Changed from 0.8/0.2 to 0.6/0.4
            print(f"Price update based on {len(transactions)} transactions: {self.current_price:.2f} -> {new_price:.2f}")
            print(f"  VWAP: {vwap:.2f}, Total volume: {total_volume}")
        
        # Add a small amount of noise to create more trading opportunities
        noise = np.random.normal(0, self.volatility * 0.1 * self.current_price)
        new_price = max(0.01, new_price + noise)
        
        self.current_price = new_price
        self.price_history.append(new_price)
        
        # Calculate daily return
        if len(self.price_history) > 1:
            daily_return = (self.price_history[-1] / self.price_history[-2]) - 1
            self.stats['daily_returns'].append(daily_return)
        
        return new_price
    
    def step(self):
        """
        Advance the market simulation by one time step.
        
        Returns:
            dict: Summary of the step's activities
        """
        # Update fundamental value
        self.update_fundamental_value()
        
        # Collect orders from all agents
        self.collect_orders()
        
        # Match orders and execute trades
        volume, transactions = self.match_orders()
        self.trading_volume.append(volume)
        
        # Update market price
        new_price = self.update_price(transactions)
        
        # Update agents' wealth
        for agent in self.agents:
            agent.update_wealth(new_price)
        
        # Return summary of the step
        return {
            'price': new_price,
            'fundamental': self.fundamental_value,
            'volume': volume,
            'num_transactions': len(transactions)
        } 