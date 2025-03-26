#!/usr/bin/env python
"""
Run script for market ABM simulation with command line arguments.
"""
import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from market.environment import MarketEnvironment
from simulation.engine import SimulationEngine
from analysis.plotting import (
    plot_price_history, 
    plot_returns_distribution,
    plot_agent_wealth,
    plot_trading_volume,
    plot_fundamental_vs_price,
    plot_summary_dashboard
)
import config


def run_simulation(debug=False, steps=None, save_plots=True, show_plots=True):
    """
    Run the market ABM simulation with configurable parameters.
    
    Args:
        debug (bool): Whether to run in debug mode (fewer agents, potentially fewer steps)
        steps (int): Number of simulation steps to run (overrides config value)
        save_plots (bool): Whether to save plots to files
        show_plots (bool): Whether to display plots
        
    Returns:
        tuple: (simulation, sim_data, stats) - simulation engine, data and statistics
    """
    # Configure simulation parameters
    if steps is not None:
        config.SIMULATION_STEPS = steps
    
    # Debug mode uses fewer agents but keeps noise traders for liquidity
    if debug:
        if steps is None:  # Only override steps if not explicitly provided
            config.SIMULATION_STEPS = 100
        
        # Reduce number of agents for clearer debug output
        config.NUM_FUNDAMENTALISTS = 10
        config.NUM_CHARTISTS = 10
        config.NUM_NOISE_TRADERS = 5
        
        print(f"Running in DEBUG mode with {config.SIMULATION_STEPS} steps")
        print(f"Agents: {config.NUM_FUNDAMENTALISTS} fundamentalists, "
              f"{config.NUM_CHARTISTS} chartists, "
              f"{config.NUM_NOISE_TRADERS} noise traders")
    else:
        # For production runs, use the values from config.py
        print(f"Running PRODUCTION simulation with {config.SIMULATION_STEPS} steps")
        print(f"Agents: {config.NUM_FUNDAMENTALISTS} fundamentalists, "
              f"{config.NUM_CHARTISTS} chartists, "
              f"{config.NUM_NOISE_TRADERS} noise traders")
    
    # Set random seed for reproducibility
    np.random.seed(config.RANDOM_SEED)
    
    print("Initializing market environment...")
    market = MarketEnvironment(
        initial_price=config.INITIAL_PRICE,
        initial_fundamental_value=config.INITIAL_FUNDAMENTAL_VALUE, 
        volatility=config.PRICE_VOLATILITY,
        max_position=config.MAX_POSITION
    )
    
    print("Setting up simulation engine...")
    simulation = SimulationEngine(market, sim_steps=config.SIMULATION_STEPS)
    
    # Set up agent parameters
    fundamentalist_params = {
        'confidence': config.FUNDAMENTALIST_CONFIDENCE,
        'reaction_speed': config.FUNDAMENTALIST_REACTION_SPEED
    }
    
    chartist_params = {
        'memory': config.CHARTIST_MEMORY,
        'sensitivity': config.CHARTIST_SENSITIVITY,
        'confidence': config.CHARTIST_CONFIDENCE
    }
    
    noise_trader_params = {
        'trade_probability': config.NOISE_TRADE_PROBABILITY,
        'max_order_size': config.NOISE_MAX_ORDER_SIZE,
        'price_range': config.NOISE_PRICE_RANGE
    }
    
    # Print initialization parameters
    print(f"Initial wealth: {config.INITIAL_WEALTH}")
    print(f"Initial position: {config.INITIAL_POSITION}")
    
    # Initialize agents
    simulation.initialize_agents(
        num_fundamentalists=config.NUM_FUNDAMENTALISTS,
        num_chartists=config.NUM_CHARTISTS,
        initial_wealth=config.INITIAL_WEALTH,
        initial_position=config.INITIAL_POSITION,
        fundamentalist_params=fundamentalist_params,
        chartist_params=chartist_params,
        num_noise_traders=config.NUM_NOISE_TRADERS,
        noise_trader_params=noise_trader_params
    )
    
    print("Running simulation...")
    sim_data = simulation.run(verbose=True)
    
    # Create timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate plots
    if save_plots or show_plots:
        print("Generating plots...")
        
        # Create results directory if it doesn't exist
        if save_plots and not os.path.exists('results'):
            os.makedirs('results')
        
        # Price history plot
        fig1 = plot_price_history(sim_data)
        if save_plots:
            fig1.savefig(f'results/price_history_{timestamp}.png', dpi=300, bbox_inches='tight')
        
        # Returns distribution plot
        fig2 = plot_returns_distribution(sim_data)
        if save_plots:
            fig2.savefig(f'results/returns_distribution_{timestamp}.png', dpi=300, bbox_inches='tight')
        
        # Agent wealth plot
        fig3 = plot_agent_wealth(sim_data)
        if save_plots:
            fig3.savefig(f'results/agent_wealth_{timestamp}.png', dpi=300, bbox_inches='tight')
        
        # Trading volume plot
        fig4 = plot_trading_volume(sim_data)
        if save_plots:
            fig4.savefig(f'results/trading_volume_{timestamp}.png', dpi=300, bbox_inches='tight')
        
        # Fundamental vs price plot
        fig5 = plot_fundamental_vs_price(sim_data)
        if save_plots:
            fig5.savefig(f'results/fundamental_vs_price_{timestamp}.png', dpi=300, bbox_inches='tight')
        
        # Summary dashboard
        fig6 = plot_summary_dashboard(sim_data)
        if save_plots:
            fig6.savefig(f'results/summary_dashboard_{timestamp}.png', dpi=300, bbox_inches='tight')
        
        if show_plots:
            plt.show()
        else:
            plt.close('all')
    
    # Get market statistics
    stats = simulation.get_market_statistics()
    
    # Print summary statistics
    print("\n=== Simulation Results ===")
    print(f"Final price: {stats['price']['final']:.2f}")
    print(f"Final fundamental value: {stats['fundamental']['final']:.2f}")
    print(f"Final mispricing: {stats['mispricing']['final']:.2f}")
    print(f"Average return: {stats['returns']['mean']*100:.4f}%")
    print(f"Return volatility: {stats['returns']['std']*100:.4f}%")
    print(f"Sharpe ratio: {stats['returns']['sharpe']:.4f}")
    print(f"Average trading volume: {stats['volume']['mean']:.2f}")
    
    # Display agent statistics with noise traders included
    print("\n=== Agent Statistics ===")
    print(f"Fundamentalists: Final wealth: {stats['agent_performance']['fundamentalist_final_wealth']:.2f}, " 
          f"Final position: {stats['agent_performance'].get('fundamentalist_final_position', 'N/A')}")
    print(f"Chartists: Final wealth: {stats['agent_performance']['chartist_final_wealth']:.2f}, "
          f"Final position: {stats['agent_performance'].get('chartist_final_position', 'N/A')}")
    
    # Add noise trader statistics if they exist in the simulation
    if 'noise_trader_final_wealth' in stats['agent_performance']:
        print(f"Noise Traders: Final wealth: {stats['agent_performance']['noise_trader_final_wealth']:.2f}, "
              f"Final position: {stats['agent_performance'].get('noise_trader_final_position', 'N/A')}")
    
    # Calculate and display trade participation statistics
    if 'transactions' in simulation.market.stats and len(simulation.market.stats['transactions']) > 0:
        print("\n=== Trading Activity ===")
        fund_buys = sum(1 for t in simulation.market.stats['transactions'] if t[0].__class__.__name__ == 'Fundamentalist')
        fund_sells = sum(1 for t in simulation.market.stats['transactions'] if t[1].__class__.__name__ == 'Fundamentalist')
        chart_buys = sum(1 for t in simulation.market.stats['transactions'] if t[0].__class__.__name__ == 'Chartist')
        chart_sells = sum(1 for t in simulation.market.stats['transactions'] if t[1].__class__.__name__ == 'Chartist')
        noise_buys = sum(1 for t in simulation.market.stats['transactions'] if t[0].__class__.__name__ == 'NoiseTrader')
        noise_sells = sum(1 for t in simulation.market.stats['transactions'] if t[1].__class__.__name__ == 'NoiseTrader')
        
        total_trades = len(simulation.market.stats['transactions'])
        print(f"Total transactions: {total_trades}")
        print(f"Fundamentalist participation: {(fund_buys + fund_sells) / (2 * total_trades) * 100:.1f}% " 
              f"(Buy: {fund_buys}, Sell: {fund_sells})")
        print(f"Chartist participation: {(chart_buys + chart_sells) / (2 * total_trades) * 100:.1f}% "
              f"(Buy: {chart_buys}, Sell: {chart_sells})")
        print(f"Noise trader participation: {(noise_buys + noise_sells) / (2 * total_trades) * 100:.1f}% "
              f"(Buy: {noise_buys}, Sell: {noise_sells})")
    
    if save_plots:
        print(f"\nResults saved to 'results/' directory with timestamp {timestamp}")
    
    return simulation, sim_data, stats


def parse_arguments():
    """Parse command line arguments for the simulation."""
    parser = argparse.ArgumentParser(description='Run Market ABM Simulation')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode with fewer agents and steps')
    parser.add_argument('--steps', type=int, default=None, help='Number of simulation steps to run')
    parser.add_argument('--no-save', action='store_true', help='Do not save plots to files')
    parser.add_argument('--no-show', action='store_true', help='Do not display plots')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Run the simulation with provided arguments
    simulation, sim_data, stats = run_simulation(
        debug=args.debug,
        steps=args.steps,
        save_plots=not args.no_save,
        show_plots=not args.no_show
    ) 