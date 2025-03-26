"""
Market metrics calculations.
"""
import numpy as np
import pandas as pd
from scipy import stats


def calculate_returns(prices):
    """
    Calculate log returns from a series of prices.
    
    Args:
        prices (array-like): Series of prices
        
    Returns:
        numpy.ndarray: Log returns
    """
    return np.diff(np.log(prices))


def calculate_volatility(returns, window=None):
    """
    Calculate return volatility.
    
    Args:
        returns (array-like): Series of returns
        window (int, optional): Rolling window for volatility calculation
            
    Returns:
        float or numpy.ndarray: Volatility or rolling volatility
    """
    if window:
        return pd.Series(returns).rolling(window).std() * np.sqrt(252)  # Annualized
    return np.std(returns) * np.sqrt(252)  # Annualized


def calculate_sharpe_ratio(returns, risk_free_rate=0):
    """
    Calculate Sharpe ratio.
    
    Args:
        returns (array-like): Series of returns
        risk_free_rate (float): Risk-free rate
            
    Returns:
        float: Sharpe ratio
    """
    return (np.mean(returns) - risk_free_rate) / np.std(returns) * np.sqrt(252)


def calculate_autocorrelation(returns, lags=1):
    """
    Calculate autocorrelation of returns.
    
    Args:
        returns (array-like): Series of returns
        lags (int): Number of lags
            
    Returns:
        numpy.ndarray: Autocorrelation values
    """
    return pd.Series(returns).autocorr(lag=lags)


def calculate_hurst_exponent(returns, max_lag=20):
    """
    Calculate Hurst exponent to detect long memory in time series.
    H < 0.5: mean-reverting
    H = 0.5: random walk
    H > 0.5: trending
    
    Args:
        returns (array-like): Series of returns
        max_lag (int): Maximum lag to consider
            
    Returns:
        float: Hurst exponent
    """
    lags = range(2, max_lag)
    tau = [np.sqrt(np.std(np.subtract(returns[lag:], returns[:-lag]))) for lag in lags]
    
    # Linear fit to double-log plot
    m = np.polyfit(np.log(lags), np.log(tau), 1)
    
    # Hurst exponent is the slope
    return m[0]


def calculate_metrics(sim_data):
    """
    Calculate various market metrics from simulation data.
    
    Args:
        sim_data (pandas.DataFrame): Simulation data
            
    Returns:
        dict: Dictionary with calculated metrics
    """
    # Extract price and returns data
    prices = sim_data['price'].values
    returns = np.diff(np.log(prices))
    
    # Calculate basic statistics
    metrics = {
        'price': {
            'mean': np.mean(prices),
            'std': np.std(prices),
            'min': np.min(prices),
            'max': np.max(prices),
            'final': prices[-1]
        },
        'returns': {
            'mean': np.mean(returns),
            'std': np.std(returns),
            'skewness': stats.skew(returns),
            'kurtosis': stats.kurtosis(returns),
            'sharpe_ratio': calculate_sharpe_ratio(returns),
            'hurst': calculate_hurst_exponent(returns)
        }
    }
    
    # Calculate autocorrelations
    metrics['returns']['autocorr_1'] = calculate_autocorrelation(returns, 1)
    metrics['returns']['autocorr_abs_1'] = calculate_autocorrelation(np.abs(returns), 1)
    
    # Calculate mispricing metrics
    if 'fundamental_value' in sim_data:
        fundamental = sim_data['fundamental_value'].values
        mispricing = prices - fundamental
        metrics['mispricing'] = {
            'mean': np.mean(mispricing),
            'mean_abs': np.mean(np.abs(mispricing)),
            'max_abs': np.max(np.abs(mispricing)),
            'final': mispricing[-1]
        }
    
    # Calculate agent performance metrics
    if 'fundamentalist_avg_wealth' in sim_data and 'chartist_avg_wealth' in sim_data:
        fund_wealth = sim_data['fundamentalist_avg_wealth'].values
        chart_wealth = sim_data['chartist_avg_wealth'].values
        
        metrics['agent_performance'] = {
            'fundamentalist_return': (fund_wealth[-1] / fund_wealth[0] - 1),
            'chartist_return': (chart_wealth[-1] / chart_wealth[0] - 1),
            'relative_performance': (fund_wealth[-1] / chart_wealth[-1] - 1)
        }
        
    return metrics 