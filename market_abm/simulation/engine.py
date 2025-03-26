"""
Simulation engine implementation.
"""
import time
import numpy as np
import pandas as pd
from tqdm import tqdm


class SimulationEngine:
    """
    The simulation engine controls the market simulation process.
    
    It initializes the market and agents, runs the simulation for a specified
    number of steps, and collects data for analysis.
    
    Attributes:
        market: The market environment
        sim_steps (int): Number of simulation steps to run
        data (pandas.DataFrame): Collected simulation data
    """
    
    def __init__(self, market, sim_steps=1000):
        """
        Initialize the simulation engine.
        
        Args:
            market: The market environment
            sim_steps (int): Number of simulation steps to run
        """
        self.market = market
        self.sim_steps = sim_steps
        self.data = None
    
    def initialize_agents(self, num_fundamentalists, num_chartists, initial_wealth,
                         initial_position=0, fundamentalist_params=None, chartist_params=None, 
                         num_noise_traders=0, noise_trader_params=None):
        """
        Initialize agents and add them to the market.
        
        Args:
            num_fundamentalists (int): Number of fundamentalist agents
            num_chartists (int): Number of chartist agents
            initial_wealth (float): Initial wealth for each agent
            initial_position (int): Initial position (number of shares) for each agent
            fundamentalist_params (dict): Parameters for fundamentalist agents
            chartist_params (dict): Parameters for chartist agents
            num_noise_traders (int): Number of noise trader agents
            noise_trader_params (dict): Parameters for noise trader agents
        """
        # Import agent classes here to avoid circular imports
        from agents.fundamentalist import Fundamentalist
        from agents.chartist import Chartist
        from agents.noise_trader import NoiseTrader
        
        # Set default parameters if not provided
        if fundamentalist_params is None:
            fundamentalist_params = {}
        if chartist_params is None:
            chartist_params = {}
        if noise_trader_params is None:
            noise_trader_params = {}
        
        # Create fundamentalist agents
        for i in range(num_fundamentalists):
            agent = Fundamentalist(
                agent_id=i,
                initial_cash=initial_wealth,
                initial_position=initial_position,
                **fundamentalist_params
            )
            self.market.add_agent(agent)
        
        # Create chartist agents
        for i in range(num_chartists):
            agent = Chartist(
                agent_id=num_fundamentalists + i,
                initial_cash=initial_wealth,
                initial_position=initial_position,
                **chartist_params
            )
            self.market.add_agent(agent)
            
        # Create noise trader agents
        for i in range(num_noise_traders):
            agent = NoiseTrader(
                agent_id=num_fundamentalists + num_chartists + i,
                initial_cash=initial_wealth,
                initial_position=initial_position,
                **noise_trader_params
            )
            self.market.add_agent(agent)
    
    def run(self, verbose=True, save_data=True, data_file='data/simulation_data.csv'):
        """
        Run the simulation for the specified number of steps.
        
        Args:
            verbose (bool): Whether to display progress bar
            save_data (bool): Whether to save data to CSV
            data_file (str): Path to save data file
            
        Returns:
            pandas.DataFrame: Collected simulation data
        """
        # Prepare data collection
        data = []
        
        # Count agent types for tracking
        num_fundamentalists = sum(1 for agent in self.market.agents if agent.__class__.__name__ == 'Fundamentalist')
        num_chartists = sum(1 for agent in self.market.agents if agent.__class__.__name__ == 'Chartist')
        num_noise_traders = sum(1 for agent in self.market.agents if agent.__class__.__name__ == 'NoiseTrader')
        
        # Start timer
        start_time = time.time()
        
        # Print initial state
        if verbose:
            print("\n=== INITIAL STATE ===")
            print(f"Initial price: {self.market.current_price:.2f}")
            print(f"Initial fundamental value: {self.market.fundamental_value:.2f}")
            print(f"Number of agents: {len(self.market.agents)} "
                  f"({num_fundamentalists} fundamentalists, {num_chartists} chartists, {num_noise_traders} noise traders)")
            print(f"Average agent wealth: {sum(agent.wealth_history[0] for agent in self.market.agents) / len(self.market.agents):.2f}")
            print(f"Average agent position: {sum(agent.position for agent in self.market.agents) / len(self.market.agents):.2f}")
            print(f"Total shares in system: {sum(agent.position for agent in self.market.agents)}")
            print("====================\n")
        
        # Run simulation steps
        iterator = tqdm(range(self.sim_steps)) if verbose else range(self.sim_steps)
        for step in iterator:
            if verbose:
                print(f"\n=== STEP {step+1} ===")
                
            # Run one market step
            step_summary = self.market.step()
            
            # Collect data
            data_row = {
                'step': step,
                'price': step_summary['price'],
                'fundamental_value': step_summary['fundamental'],
                'volume': step_summary['volume'],
                'transactions': step_summary['num_transactions'],
                'num_fundamentalists': num_fundamentalists,
                'num_chartists': num_chartists,
                'num_noise_traders': num_noise_traders
            }
            
            # Add agent-specific data (aggregated by type)
            fundamentalist_wealth = 0
            chartist_wealth = 0
            noise_trader_wealth = 0
            fundamentalist_position = 0
            chartist_position = 0
            noise_trader_position = 0
            
            for agent in self.market.agents:
                if agent.__class__.__name__ == 'Fundamentalist':
                    fundamentalist_wealth += agent.wealth_history[-1]
                    fundamentalist_position += agent.position
                elif agent.__class__.__name__ == 'Chartist':
                    chartist_wealth += agent.wealth_history[-1]
                    chartist_position += agent.position
                elif agent.__class__.__name__ == 'NoiseTrader':
                    noise_trader_wealth += agent.wealth_history[-1]
                    noise_trader_position += agent.position
            
            # Calculate both average and total metrics
            if num_fundamentalists > 0:
                data_row['fundamentalist_avg_wealth'] = fundamentalist_wealth / num_fundamentalists
                data_row['fundamentalist_avg_position'] = fundamentalist_position / num_fundamentalists
                data_row['fundamentalist_total_position'] = fundamentalist_position
            else:
                data_row['fundamentalist_avg_wealth'] = 0
                data_row['fundamentalist_avg_position'] = 0
                data_row['fundamentalist_total_position'] = 0
                
            if num_chartists > 0:
                data_row['chartist_avg_wealth'] = chartist_wealth / num_chartists
                data_row['chartist_avg_position'] = chartist_position / num_chartists
                data_row['chartist_total_position'] = chartist_position
            else:
                data_row['chartist_avg_wealth'] = 0
                data_row['chartist_avg_position'] = 0
                data_row['chartist_total_position'] = 0
                
            if num_noise_traders > 0:
                data_row['noise_trader_avg_wealth'] = noise_trader_wealth / num_noise_traders
                data_row['noise_trader_avg_position'] = noise_trader_position / num_noise_traders
                data_row['noise_trader_total_position'] = noise_trader_position
            else:
                data_row['noise_trader_avg_wealth'] = 0
                data_row['noise_trader_avg_position'] = 0
                data_row['noise_trader_total_position'] = 0
            
            # Add total system position
            data_row['total_system_position'] = fundamentalist_position + chartist_position + noise_trader_position
            
            # Calculate metrics
            if len(self.market.price_history) > 1:
                data_row['return'] = self.market.price_history[-1] / self.market.price_history[-2] - 1
            else:
                data_row['return'] = 0
                
            # Store data row
            data.append(data_row)
            
            if verbose:
                print(f"  Price: {step_summary['price']:.2f}, Volume: {step_summary['volume']}")
                print(f"  Fundamentalist position: {data_row['fundamentalist_avg_position']:.2f} (avg), {data_row['fundamentalist_total_position']} (total)")
                print(f"  Chartist position: {data_row['chartist_avg_position']:.2f} (avg), {data_row['chartist_total_position']} (total)")
                if num_noise_traders > 0:
                    print(f"  Noise trader position: {data_row['noise_trader_avg_position']:.2f} (avg), {data_row['noise_trader_total_position']} (total)")
                print(f"  Total system shares: {data_row['total_system_position']}")
                print("=================")
        
        # End timer
        elapsed_time = time.time() - start_time
        
        # Convert to DataFrame
        self.data = pd.DataFrame(data)
        
        if verbose:
            print("\n=== FINAL STATE ===")
            print(f"Simulation completed in {elapsed_time:.2f} seconds")
            print(f"Final price: {self.market.current_price:.2f}")
            print(f"Final fundamental value: {self.market.fundamental_value:.2f}")
            print(f"Total volume: {self.market.stats['total_volume']}")
            print(f"Total transactions: {len(self.market.stats['transactions'])}")
            
            # Check if total shares remained constant
            if len(data) > 0:
                initial_shares = data[0]['total_system_position']
                final_shares = data[-1]['total_system_position']
                if initial_shares != final_shares:
                    print(f"\nWARNING: Total shares not conserved! Initial: {initial_shares}, Final: {final_shares}")
                else:
                    print(f"\nShare conservation verified: {initial_shares} shares throughout simulation")
            
            # Check if any trading occurred
            if self.market.stats['total_volume'] == 0:
                print("\nWARNING: No trading occurred during the simulation!")
                print("Possible issues:")
                print("1. Prices didn't match (bid-ask spread too wide)")
                print("2. Agents didn't have enough cash/shares")
                print("3. Agent decision criteria weren't met")
            
            # Calculate trade statistics
            if len(self.market.stats['transactions']) > 0:
                print("\nTrade statistics:")
                # Count unique buyers and sellers
                buyers = set(t[0].agent_id for t in self.market.stats['transactions'])
                sellers = set(t[1].agent_id for t in self.market.stats['transactions'])
                print(f"Unique buyers: {len(buyers)}")
                print(f"Unique sellers: {len(sellers)}")
                
                # Count fundamentalist vs chartist trades
                fund_buys = sum(1 for t in self.market.stats['transactions'] if t[0].__class__.__name__ == 'Fundamentalist')
                fund_sells = sum(1 for t in self.market.stats['transactions'] if t[1].__class__.__name__ == 'Fundamentalist')
                chart_buys = sum(1 for t in self.market.stats['transactions'] if t[0].__class__.__name__ == 'Chartist')
                chart_sells = sum(1 for t in self.market.stats['transactions'] if t[1].__class__.__name__ == 'Chartist')
                print(f"Fundamentalist buys: {fund_buys}, sells: {fund_sells}")
                print(f"Chartist buys: {chart_buys}, sells: {chart_sells}")
        
        # Save data to CSV if requested
        if save_data:
            self.data.to_csv(data_file, index=False)
            if verbose:
                print(f"\nData saved to {data_file}")
        
        return self.data
    
    def get_agent_data(self):
        """
        Extract detailed data for each individual agent.
        
        Returns:
            dict: Dictionary with agent data
        """
        agent_data = {}
        
        for agent in self.market.agents:
            agent_id = agent.agent_id
            agent_type = agent.__class__.__name__
            
            agent_data[agent_id] = {
                'type': agent_type,
                'final_wealth': agent.wealth_history[-1],
                'final_position': agent.position,
                'wealth_history': agent.wealth_history,
                'position_history': agent.position_history,
                'trades': len(agent.trade_history)
            }
        
        return agent_data
    
    def get_market_statistics(self):
        """
        Calculate various market statistics from the simulation data.
        
        Returns:
            dict: Dictionary with market statistics
        """
        if self.data is None:
            return None
        
        # Initialize statistics dictionary
        stats = {
            'price': {},
            'fundamental': {},
            'mispricing': {},
            'returns': {},
            'volume': {},
            'agent_performance': {}
        }
        
        # Price statistics
        stats['price']['initial'] = self.data['price'].iloc[0]
        stats['price']['final'] = self.data['price'].iloc[-1]
        stats['price']['mean'] = self.data['price'].mean()
        stats['price']['min'] = self.data['price'].min()
        stats['price']['max'] = self.data['price'].max()
        stats['price']['std'] = self.data['price'].std()
        
        # Fundamental value statistics
        stats['fundamental']['initial'] = self.data['fundamental_value'].iloc[0]
        stats['fundamental']['final'] = self.data['fundamental_value'].iloc[-1]
        stats['fundamental']['mean'] = self.data['fundamental_value'].mean()
        
        # Calculate mispricing statistics
        mispricing = self.data['fundamental_value'] - self.data['price']
        stats['mispricing']['initial'] = mispricing.iloc[0]
        stats['mispricing']['final'] = mispricing.iloc[-1]
        stats['mispricing']['mean'] = mispricing.mean()
        stats['mispricing']['std'] = mispricing.std()
        
        # Returns statistics
        if 'return' in self.data.columns:
            stats['returns']['mean'] = self.data['return'].mean()
            stats['returns']['std'] = self.data['return'].std()
            # Calculate annualized Sharpe ratio (assuming daily returns)
            if stats['returns']['std'] > 0:
                stats['returns']['sharpe'] = stats['returns']['mean'] / stats['returns']['std'] * np.sqrt(252)
            else:
                stats['returns']['sharpe'] = 0
        
        # Volume statistics
        stats['volume']['total'] = self.data['volume'].sum()
        stats['volume']['mean'] = self.data['volume'].mean()
        stats['volume']['max'] = self.data['volume'].max()
        stats['volume']['std'] = self.data['volume'].std()
        
        # Agent performance statistics
        if 'fundamentalist_avg_wealth' in self.data.columns:
            stats['agent_performance']['fundamentalist_initial_wealth'] = self.data['fundamentalist_avg_wealth'].iloc[0]
            stats['agent_performance']['fundamentalist_final_wealth'] = self.data['fundamentalist_avg_wealth'].iloc[-1]
            stats['agent_performance']['fundamentalist_return'] = (
                stats['agent_performance']['fundamentalist_final_wealth'] / 
                stats['agent_performance']['fundamentalist_initial_wealth'] - 1
            )
            
        if 'chartist_avg_wealth' in self.data.columns:
            stats['agent_performance']['chartist_initial_wealth'] = self.data['chartist_avg_wealth'].iloc[0]
            stats['agent_performance']['chartist_final_wealth'] = self.data['chartist_avg_wealth'].iloc[-1]
            stats['agent_performance']['chartist_return'] = (
                stats['agent_performance']['chartist_final_wealth'] / 
                stats['agent_performance']['chartist_initial_wealth'] - 1
            )
            
        # Add noise trader statistics if they exist
        if 'noise_trader_avg_wealth' in self.data.columns:
            stats['agent_performance']['noise_trader_initial_wealth'] = self.data['noise_trader_avg_wealth'].iloc[0]
            stats['agent_performance']['noise_trader_final_wealth'] = self.data['noise_trader_avg_wealth'].iloc[-1]
            stats['agent_performance']['noise_trader_return'] = (
                stats['agent_performance']['noise_trader_final_wealth'] / 
                stats['agent_performance']['noise_trader_initial_wealth'] - 1
            )
        
        # Add final positions for all agent types
        if 'fundamentalist_total_position' in self.data.columns:
            stats['agent_performance']['fundamentalist_final_position'] = self.data['fundamentalist_total_position'].iloc[-1]
            
        if 'chartist_total_position' in self.data.columns:
            stats['agent_performance']['chartist_final_position'] = self.data['chartist_total_position'].iloc[-1]
            
        if 'noise_trader_total_position' in self.data.columns:
            stats['agent_performance']['noise_trader_final_position'] = self.data['noise_trader_total_position'].iloc[-1]
            
        return stats 