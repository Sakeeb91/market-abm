#!/usr/bin/env python
"""
Main script to run the market ABM simulation.
"""
import os
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


def run_simulation(debug=True):
    """Run the market ABM simulation."""
    
    # Override simulation steps for debugging
    if debug:
        config.SIMULATION_STEPS = 50  # Increased from 20 for more complete patterns
        # Reduce number of agents for clearer debug output but keep enough for diverse behavior
        config.NUM_FUNDAMENTALISTS = 10
        config.NUM_CHARTISTS = 10
    else:
        # For full production runs
        config.SIMULATION_STEPS = 1000
        config.NUM_FUNDAMENTALISTS = 100
        config.NUM_CHARTISTS = 100
    
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
    
    print(f"Initializing agents ({config.NUM_FUNDAMENTALISTS} fundamentalists, "
          f"{config.NUM_CHARTISTS} chartists)...")
    
    fundamentalist_params = {
        'confidence': config.FUNDAMENTALIST_CONFIDENCE,
        'reaction_speed': config.FUNDAMENTALIST_REACTION_SPEED
    }
    
    chartist_params = {
        'memory': config.CHARTIST_MEMORY,
        'sensitivity': config.CHARTIST_SENSITIVITY,
        'confidence': config.CHARTIST_CONFIDENCE
    }
    
    # Print initialization parameters
    print(f"Initial wealth: {config.INITIAL_WEALTH}")
    print(f"Initial position: {config.INITIAL_POSITION}")
    print(f"Fundamentalist reaction speed: {config.FUNDAMENTALIST_REACTION_SPEED}")
    print(f"Chartist sensitivity: {config.CHARTIST_SENSITIVITY}")
    
    simulation.initialize_agents(
        num_fundamentalists=config.NUM_FUNDAMENTALISTS,
        num_chartists=config.NUM_CHARTISTS,
        initial_wealth=config.INITIAL_WEALTH,
        initial_position=config.INITIAL_POSITION,
        fundamentalist_params=fundamentalist_params,
        chartist_params=chartist_params
    )
    
    print("Running simulation...")
    sim_data = simulation.run(verbose=True)
    
    # Create timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')
    
    # Generate plots
    print("Generating plots...")
    
    # Price history plot
    fig1 = plot_price_history(sim_data)
    fig1.savefig(f'results/price_history_{timestamp}.png', dpi=300, bbox_inches='tight')
    
    # Returns distribution plot
    fig2 = plot_returns_distribution(sim_data)
    fig2.savefig(f'results/returns_distribution_{timestamp}.png', dpi=300, bbox_inches='tight')
    
    # Agent wealth plot
    fig3 = plot_agent_wealth(sim_data)
    fig3.savefig(f'results/agent_wealth_{timestamp}.png', dpi=300, bbox_inches='tight')
    
    # Trading volume plot
    fig4 = plot_trading_volume(sim_data)
    fig4.savefig(f'results/trading_volume_{timestamp}.png', dpi=300, bbox_inches='tight')
    
    # Fundamental vs price plot
    fig5 = plot_fundamental_vs_price(sim_data)
    fig5.savefig(f'results/fundamental_vs_price_{timestamp}.png', dpi=300, bbox_inches='tight')
    
    # Summary dashboard
    fig6 = plot_summary_dashboard(sim_data)
    fig6.savefig(f'results/summary_dashboard_{timestamp}.png', dpi=300, bbox_inches='tight')
    
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
    print(f"Final fundamentalist wealth: {stats['agent_performance']['fundamentalist_final_wealth']:.2f}")
    print(f"Final chartist wealth: {stats['agent_performance']['chartist_final_wealth']:.2f}")
    
    print("\nSimulation completed successfully.")
    print(f"Results saved to 'results/' directory with timestamp {timestamp}")
    
    plt.show()
    
    return simulation, sim_data, stats


if __name__ == "__main__":
    simulation, sim_data, stats = run_simulation(debug=True) 