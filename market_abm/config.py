"""
Configuration parameters for the market ABM simulation.
"""

# Simulation Parameters
SIMULATION_STEPS = 1000  # Keeping at 1000 for full simulations
TIME_STEP = 1  # Time step in arbitrary units

# Market Parameters
INITIAL_PRICE = 100.0
INITIAL_FUNDAMENTAL_VALUE = 100.0
PRICE_VOLATILITY = 0.2  # Increased from 0.15 for more trading opportunities
SPREAD = 0.003  # Further reduced minimum bid-ask spread

# Agent Parameters
NUM_FUNDAMENTALISTS = 90  # Reduced from 100 to add noise traders
NUM_CHARTISTS = 90  # Reduced from 100 to add noise traders
NUM_NOISE_TRADERS = 20  # New noise traders for better liquidity
INITIAL_WEALTH = 10000.0
INITIAL_POSITION = 30  # Each agent starts with 30 shares to ensure they can sell if needed

# Fundamentalist Parameters
FUNDAMENTALIST_CONFIDENCE = 0.75  # Reduced from 0.8 to allow for more diverse estimates
FUNDAMENTALIST_REACTION_SPEED = 0.6  # Increased from 0.4 for significantly more aggressive trading

# Chartist Parameters
CHARTIST_MEMORY = 8  # Reduced from 10 to be even more responsive to recent trends
CHARTIST_SENSITIVITY = 0.4  # Increased from 0.3 for more aggressive trading
CHARTIST_CONFIDENCE = 0.8  # Increased from 0.7 for stronger signals

# Noise Trader Parameters
NOISE_TRADE_PROBABILITY = 0.5  # 50% chance of trading each step
NOISE_MAX_ORDER_SIZE = 12  # Slightly larger than fundamentalist/chartist
NOISE_PRICE_RANGE = 0.008  # Tighter price range to facilitate matching

# Trading Parameters
MIN_TRADE_SIZE = 1
MAX_TRADE_SIZE = 25  # Increased from 20
TRANSACTION_COST = 0.0003  # Further reduced from 0.0005 to encourage more trading

# Risk Management
MAX_POSITION = 150  # Increased from 100
STOP_LOSS = 0.1
TAKE_PROFIT = 0.2

# Random Seed for Reproducibility
RANDOM_SEED = 42 