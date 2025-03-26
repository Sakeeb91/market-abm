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
    
    if 'agent_performance' in stats:
        print(f"Final fundamentalist wealth: {stats['agent_performance']['fundamentalist_final_wealth']:.2f}")
        print(f"Final chartist wealth: {stats['agent_performance']['chartist_final_wealth']:.2f}")
        if 'noise_trader_final_wealth' in stats['agent_performance']:
            print(f"Final noise trader wealth: {stats['agent_performance']['noise_trader_final_wealth']:.2f}")
    
    # Verify position consistency
    print("\n=== Position Verification ===")
    # First, get the ground truth from agent objects
    fund_position = 0
    chart_position = 0
    noise_position = 0
    
    for agent in simulation.market.agents:
        if agent.__class__.__name__ == 'Fundamentalist':
            fund_position += agent.position
        elif agent.__class__.__name__ == 'Chartist':
            chart_position += agent.position
        elif agent.__class__.__name__ == 'NoiseTrader':
            noise_position += agent.position
    
    print("Ground truth positions from agent objects:")
    print(f"Fundamentalists: {fund_position}")
    print(f"Chartists: {chart_position}")
    print(f"Noise traders: {noise_position}")
    print(f"Total system shares: {fund_position + chart_position + noise_position}")
    
    # Then check sim_data values for the final step
    if not sim_data.empty:
        last_row = sim_data.iloc[-1]
        print("\nPositions from simulation data (final step):")
        print(f"Fundamentalists: {last_row['fundamentalist_total_position']}")
        print(f"Chartists: {last_row['chartist_total_position']}")
        if 'noise_trader_total_position' in last_row:
            print(f"Noise traders: {last_row['noise_trader_total_position']}")
        print(f"Total system shares: {last_row['total_system_position']}")
    
    print("\nSimulation completed successfully.")
    if save_plots:
        print(f"Results saved to 'results/' directory with timestamp {timestamp}")
    
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