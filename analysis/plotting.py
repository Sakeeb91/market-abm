"""
Plotting functions for visualizing market ABM simulation results.
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import pandas as pd


def plot_price_history(sim_data, figsize=(12, 6), save_path=None):
    """
    Plot price history over time with returns and volatility.
    
    Args:
        sim_data (pandas.DataFrame): Simulation data
        figsize (tuple): Figure size
        save_path (str, optional): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The figure object
    """
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(3, 1, height_ratios=[3, 1, 1], hspace=0.3)
    
    # Price subplot
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(sim_data['step'], sim_data['price'], label='Market Price')
    
    if 'fundamental_value' in sim_data.columns:
        ax1.plot(sim_data['step'], sim_data['fundamental_value'], 
                 label='Fundamental Value', linestyle='--', alpha=0.7)
    
    ax1.set_ylabel('Price')
    ax1.set_title('Price History')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Returns subplot
    returns = sim_data['return']
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.plot(sim_data['step'], returns, label='Returns', color='green', alpha=0.7)
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    ax2.set_ylabel('Returns')
    ax2.grid(True, alpha=0.3)
    
    # Volatility subplot - use smaller window for shorter simulations
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    
    # Dynamically adjust rolling window based on data size
    window_size = min(10, max(2, len(returns) // 5))
    
    # Only calculate rolling volatility if we have enough data
    if len(returns) > window_size:
        rolling_vol = returns.rolling(window=window_size).std()
        ax3.plot(sim_data['step'][window_size-1:], rolling_vol[window_size-1:], 
                 label=f'Volatility ({window_size}-period)', color='red')
        ax3.set_ylabel('Volatility')
        ax3.set_xlabel('Time Step')
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, "Not enough data for volatility calculation", 
                 horizontalalignment='center', verticalalignment='center')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_returns_distribution(sim_data, figsize=(12, 6), save_path=None):
    """
    Plot the distribution of returns with normal distribution comparison.
    
    Args:
        sim_data (pandas.DataFrame): Simulation data
        figsize (tuple): Figure size
        save_path (str, optional): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The figure object
    """
    returns = sim_data['return'].dropna().values
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Returns distribution
    sns.histplot(returns, kde=True, ax=ax1)
    ax1.set_title('Returns Distribution')
    ax1.set_xlabel('Return')
    ax1.set_ylabel('Frequency')
    
    # Normal distribution overlay
    x = np.linspace(min(returns), max(returns), 100)
    mean = np.mean(returns)
    std = np.std(returns)
    norm_dist = 1/(std * np.sqrt(2 * np.pi)) * np.exp(-(x - mean)**2 / (2 * std**2))
    ax1.plot(x, norm_dist * len(returns) * (max(returns) - min(returns)) / 50, 
             'r--', label='Normal Distribution')
    ax1.legend()
    
    # Q-Q plot
    from scipy import stats
    stats.probplot(returns, dist="norm", plot=ax2)
    ax2.set_title('Q-Q Plot vs. Normal Distribution')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_agent_wealth(sim_data, figsize=(12, 9), save_path=None):
    """
    Plot the evolution of agent wealth and positions over time.
    
    Args:
        sim_data (pandas.DataFrame): Simulation data
        figsize (tuple): Figure size
        save_path (str, optional): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The figure object
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize, sharex=True)
    
    # Wealth over time
    ax1.plot(sim_data['step'], sim_data['fundamentalist_avg_wealth'], 
             label='Fundamentalists', color='blue')
    ax1.plot(sim_data['step'], sim_data['chartist_avg_wealth'], 
             label='Chartists', color='red')
    ax1.set_ylabel('Average Wealth')  # Clarify this is per-agent average
    ax1.set_title('Average Agent Wealth Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Average position over time
    ax2.plot(sim_data['step'], sim_data['fundamentalist_avg_position'], 
             label='Fundamentalists', color='blue')
    ax2.plot(sim_data['step'], sim_data['chartist_avg_position'], 
             label='Chartists', color='red')
    ax2.set_ylabel('Average Position')  # Clarify this is per-agent average
    ax2.set_title('Average Position Per Agent Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Total position over time (calculated from averages * number of agents)
    # Check if we have the number of agents in the data
    if 'num_fundamentalists' in sim_data.columns and 'num_chartists' in sim_data.columns:
        total_fund_position = sim_data['fundamentalist_avg_position'] * sim_data['num_fundamentalists']
        total_chart_position = sim_data['chartist_avg_position'] * sim_data['num_chartists']
    else:
        # Use the number of agents from config if available, otherwise assume from latest run
        from config import NUM_FUNDAMENTALISTS, NUM_CHARTISTS
        total_fund_position = sim_data['fundamentalist_avg_position'] * NUM_FUNDAMENTALISTS
        total_chart_position = sim_data['chartist_avg_position'] * NUM_CHARTISTS
    
    # Plot total positions
    ax3.plot(sim_data['step'], total_fund_position, 
             label='Fundamentalists', color='blue')
    ax3.plot(sim_data['step'], total_chart_position, 
             label='Chartists', color='red')
    ax3.plot(sim_data['step'], total_fund_position + total_chart_position, 
             label='Total System', color='green', linestyle='--')
    ax3.set_ylabel('Total Shares')
    ax3.set_xlabel('Time Step')
    ax3.set_title('Total Shares Held By Agent Type')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_trading_volume(sim_data, figsize=(12, 6), save_path=None):
    """
    Plot trading volume and price over time.
    
    Args:
        sim_data (pandas.DataFrame): Simulation data
        figsize (tuple): Figure size
        save_path (str, optional): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The figure object
    """
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # Volume as bars
    ax1.bar(sim_data['step'], sim_data['volume'], alpha=0.5, color='gray', label='Volume')
    ax1.set_ylabel('Trading Volume', color='gray')
    ax1.tick_params(axis='y', labelcolor='gray')
    ax1.set_xlabel('Time Step')
    
    # Price on secondary y-axis
    ax2 = ax1.twinx()
    ax2.plot(sim_data['step'], sim_data['price'], color='blue', label='Price')
    ax2.set_ylabel('Price', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    # Title and legend
    plt.title('Trading Volume and Price Over Time')
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_fundamental_vs_price(sim_data, figsize=(12, 6), save_path=None):
    """
    Plot market price vs. fundamental value and mispricing.
    
    Args:
        sim_data (pandas.DataFrame): Simulation data
        figsize (tuple): Figure size
        save_path (str, optional): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The figure object
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True, 
                                  gridspec_kw={'height_ratios': [3, 1]})
    
    # Price and fundamental value
    ax1.plot(sim_data['step'], sim_data['price'], label='Market Price', color='blue')
    ax1.plot(sim_data['step'], sim_data['fundamental_value'], 
             label='Fundamental Value', linestyle='--', color='green')
    ax1.set_ylabel('Price')
    ax1.set_title('Market Price vs. Fundamental Value')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Mispricing (deviation from fundamental value)
    mispricing = sim_data['price'] - sim_data['fundamental_value']
    ax2.plot(sim_data['step'], mispricing, color='red')
    ax2.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    ax2.set_ylabel('Mispricing')
    ax2.set_xlabel('Time Step')
    ax2.set_title('Deviation from Fundamental Value')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig


def plot_summary_dashboard(sim_data, figsize=(15, 10), save_path=None):
    """
    Create a comprehensive dashboard of simulation results.
    
    Args:
        sim_data (pandas.DataFrame): Simulation data
        figsize (tuple): Figure size
        save_path (str, optional): Path to save the figure
        
    Returns:
        matplotlib.figure.Figure: The figure object
    """
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(3, 3, figure=fig)
    
    # Price and fundamental value
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(sim_data['step'], sim_data['price'], color='blue', label='Price')
    ax1.plot(sim_data['step'], sim_data['fundamental_value'], color='green', linestyle='--', label='Fundamental Value')
    ax1.set_title('Price vs Fundamental Value')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True)
    
    # Trading volume
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.bar(sim_data['step'], sim_data['volume'], color='purple', alpha=0.7)
    ax2.set_title('Trading Volume')
    ax2.set_ylabel('Volume')
    ax2.grid(True)
    
    # Agent wealth
    ax3 = fig.add_subplot(gs[1, :])
    ax3.plot(sim_data['step'], sim_data['fundamentalist_avg_wealth'], color='blue', label='Fundamentalist')
    ax3.plot(sim_data['step'], sim_data['chartist_avg_wealth'], color='red', label='Chartist')
    if 'noise_trader_avg_wealth' in sim_data.columns:
        ax3.plot(sim_data['step'], sim_data['noise_trader_avg_wealth'], color='green', label='Noise Trader')
    ax3.set_title('Agent Wealth Over Time')
    ax3.set_ylabel('Wealth')
    ax3.legend()
    ax3.grid(True)
    
    # Agent positions
    ax4 = fig.add_subplot(gs[2, :2])
    
    # Check if we have agent counts in data
    has_counts = all(col in sim_data.columns for col in ['num_fundamentalists', 'num_chartists'])
    
    # Create an area plot with stacked positions
    steps = sim_data['step']
    fund_pos = sim_data['fundamentalist_total_position']
    chart_pos = sim_data['chartist_total_position']
    
    # Initialize bottom for stacking
    bottom = np.zeros(len(steps))
    
    # Plot fundamentalist positions
    ax4.fill_between(steps, bottom, fund_pos, label='Fundamentalist', color='blue', alpha=0.5)
    
    # Update bottom for stacking
    bottom = fund_pos
    
    # Add chartist positions on top
    ax4.fill_between(steps, bottom, bottom + chart_pos, label='Chartist', color='red', alpha=0.5)
    
    # Update bottom again
    bottom = bottom + chart_pos
    
    # Add noise trader positions if available
    if 'noise_trader_total_position' in sim_data.columns:
        noise_pos = sim_data['noise_trader_total_position']
        ax4.fill_between(steps, bottom, bottom + noise_pos, label='Noise Trader', color='green', alpha=0.5)
        # Update bottom one more time
        bottom = bottom + noise_pos
    
    # Total system shares should be constant - add a horizontal line
    if 'total_system_position' in sim_data.columns:
        total_shares = sim_data['total_system_position'].iloc[0]
        ax4.axhline(total_shares, color='black', linestyle='--', label='Total Shares')
    
    ax4.set_title('Total Shares by Agent Type')
    ax4.set_ylabel('Shares')
    ax4.set_xlabel('Step')
    ax4.legend()
    ax4.grid(True)
    
    # Returns histogram
    ax5 = fig.add_subplot(gs[2, 2])
    if len(sim_data) > 1:  # Only if we have enough data
        returns = sim_data['return'].dropna() if 'return' in sim_data.columns else pd.Series([])
        if len(returns) > 0:
            ax5.hist(returns, bins=30, color='green', alpha=0.7)
            ax5.set_title('Returns Distribution')
            ax5.set_xlabel('Return')
            ax5.set_ylabel('Frequency')
            
            # Add mean and std to plot
            mean_return = returns.mean()
            std_return = returns.std()
            ax5.axvline(mean_return, color='red', linestyle='--')
            ax5.text(0.05, 0.95, f'Mean: {mean_return:.4f}\nStd: {std_return:.4f}', 
                   transform=ax5.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
            ax5.grid(True)
    
    # Add summary statistics as text
    # No separate subplot for this, just add text to figure
    if len(sim_data) > 0:
        # Calculate key statistics
        initial_price = sim_data['price'].iloc[0]
        final_price = sim_data['price'].iloc[-1]
        price_change = (final_price / initial_price - 1) * 100
        total_volume = sim_data['volume'].sum()
        avg_volume = sim_data['volume'].mean()
        
        # Calculate final positions for each agent type - Using the same data source as the plot
        fund_final = sim_data['fundamentalist_total_position'].iloc[-1]
        chart_final = sim_data['chartist_total_position'].iloc[-1]
        
        # Add position for noise traders if available
        noise_final = 0
        if 'noise_trader_total_position' in sim_data.columns:
            noise_final = sim_data['noise_trader_total_position'].iloc[-1]
        
        # Get agent counts if available
        num_fund = sim_data['num_fundamentalists'].iloc[0] if 'num_fundamentalists' in sim_data.columns else 'N/A'
        num_chart = sim_data['num_chartists'].iloc[0] if 'num_chartists' in sim_data.columns else 'N/A'
        num_noise = sim_data['num_noise_traders'].iloc[0] if 'num_noise_traders' in sim_data.columns else 'N/A'
        
        # Add verification for total position
        total_final = fund_final + chart_final + noise_final
        total_system = sim_data['total_system_position'].iloc[-1] if 'total_system_position' in sim_data.columns else 0
        
        # Construct the statistics text
        stats_text = (
            f"Summary Statistics\n"
            f"------------------------\n"
            f"Simulation steps: {len(sim_data)}\n"
            f"Initial price: {initial_price:.2f}\n"
            f"Final price: {final_price:.2f}\n"
            f"Price change: {price_change:.2f}%\n"
            f"Total volume: {total_volume:.0f}\n"
            f"Avg volume: {avg_volume:.2f}\n\n"
            f"Agent Counts:\n"
            f"Fundamentalists: {num_fund}\n"
            f"Chartists: {num_chart}\n"
            f"Noise Traders: {num_noise}\n\n"
            f"Final Positions:\n"
            f"Fundamentalists: {fund_final:.0f}\n"
            f"Chartists: {chart_final:.0f}\n"
            f"Noise Traders: {noise_final:.0f}\n"
            f"Total: {total_final:.0f} (System: {total_system:.0f})\n"
        )
        
        # Add text to the figure
        fig.text(0.02, 0.02, stats_text, fontsize=9, family='monospace',
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)  # Make room for the stats text
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
    return fig 