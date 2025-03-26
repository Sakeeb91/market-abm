# Market ABM - Agent-Based Market Simulation

A flexible and customizable agent-based model of financial markets, simulating interactions between fundamentalists, chartists, and noise traders.

## Overview

This project implements an Agent-Based Model (ABM) to simulate the dynamics of a simplified financial market (a single stock). It aims to explore how interactions between heterogeneous agents with different trading strategies can lead to emergent, complex market phenomena like:

*   Price volatility
*   Bubbles and crashes
*   Fat-tailed return distributions
*   Volatility clustering

The model draws inspiration from concepts in **statistical mechanics** and **complex systems**, viewing the market as a system of interacting particles (agents) whose micro-level decisions aggregate into macro-level behavior.

## Core Concepts

*   **Agent-Based Modeling (ABM):** A computational method where autonomous agents interact within an environment according to predefined rules. System-level behavior emerges from these interactions.
*   **Heterogeneous Agents:** The market is populated by different types of traders:
    *   **Fundamentalists:** Base decisions on the perceived difference between the market price and a theoretical fundamental value.
    *   **Chartists (Technical Traders):** Base decisions on patterns and trends observed in past price history (e.g., using moving average crossovers).
    *   **Noise Traders:** Trade randomly, providing baseline liquidity and noise, often essential for market functioning in ABMs.
*   **Emergent Phenomena:** Market dynamics (like bubbles) are not explicitly programmed but arise naturally from the collective actions and interactions of the agents.
*   **Price Formation:** The asset price is updated based on the imbalance between buy and sell orders submitted by the agents in each time step.

## Features

*   Simulation of a single-asset market.
*   Multiple agent types: Fundamentalists, Chartists, Noise Traders.
*   Configurable agent parameters (e.g., number, aggressiveness, strategy parameters).
*   Market environment managing price updates based on order flow.
*   Simulation engine controlling time steps and agent activation.
*   Data logging for key metrics (price, volume, agent wealth, agent positions).
*   Visualization dashboard summarizing simulation results:
    *   Price and Fundamental Value History
    *   Trading Volume
    *   Agent Wealth Over Time
    *   Total Shares Held by Agent Type
    *   Returns Distribution
    *   (Planned/Partially Implemented) Rolling Volatility

## Setup and Installation

1. **Prerequisites:**
   * Python 3.7+
   * `pip` (Python package installer)

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/Sakeeb91/market-abm.git
   cd market-abm
   ```

3. **Create a Virtual Environment (Recommended):**
   * On macOS/Linux:
     ```bash
     python3 -m venv myenv
     source myenv/bin/activate
     ```
   * On Windows:
     ```bash
     python -m venv myenv
     .\myenv\Scripts\activate
     ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Simulation parameters can be easily modified in the `config.py` file. Key parameters include:

* `SIMULATION_STEPS`: Duration of the simulation.
* `INITIAL_PRICE`: Starting price of the asset.
* `INITIAL_FUNDAMENTAL_VALUE`: Starting fundamental value.
* `PRICE_VOLATILITY`: Volatility of the price process.
* Agent parameters:
  * `NUM_FUNDAMENTALISTS`, `NUM_CHARTISTS`, `NUM_NOISE_TRADERS`: Number of each agent type.
  * `INITIAL_WEALTH`: Starting cash for agents.
  * `INITIAL_POSITION`: Starting shares held by agents.
* Agent-specific behavior parameters:
  * `FUNDAMENTALIST_CONFIDENCE`, `FUNDAMENTALIST_REACTION_SPEED`
  * `CHARTIST_MEMORY`, `CHARTIST_SENSITIVITY`, `CHARTIST_CONFIDENCE`
  * `NOISE_TRADE_PROBABILITY`, `NOISE_MAX_ORDER_SIZE`, `NOISE_PRICE_RANGE`
* Risk management parameters:
  * `MAX_POSITION`: Maximum allowed position size.
  * `STOP_LOSS`, `TAKE_PROFIT`: Risk management parameters.

## Running the Simulation

Execute the main script from the project directory:

```bash
python run.py
```

For debugging with reduced agent numbers and steps:
```bash
python run.py --debug
```

For additional options:
```bash
python run.py --help
```

## Output

### Generated Plots
The simulation produces several plots saved in the `results/` directory:

* **Price History**: Shows the asset price evolution over time.
* **Returns Distribution**: Displays the distribution of returns with normal distribution comparison.
* **Agent Wealth**: Tracks the wealth of different agent types over time.
* **Trading Volume**: Shows trading volume over time.
* **Fundamental vs Price**: Compares the fundamental value to the market price.
* **Summary Dashboard**: A comprehensive overview including all key metrics, agent positions, and summary statistics.

### Data
The simulation data is stored in memory as a pandas DataFrame and can be saved to CSV using the appropriate flags.

## Current Status & Known Issues

* **Core Trading Loop**: The model successfully simulates trading between different agent types, with prices responding to supply and demand dynamics.

* **Fundamentalist Behavior**: Fundamentalists currently detect large mispricings between market price and fundamental value, causing them to want to sell when the price is too high. In most simulations, they deplete their initial positions and then remain inactive. This is a realistic response to extreme overpricing, but may require adjustment for more balanced simulations.

* **Chartist-NoiseTrader Dynamics**: Chartists respond to price trends and often engage in momentum trading, while Noise Traders provide liquidity through random trading. This interaction creates interesting market dynamics.

* **Position Conservation**: The system correctly maintains conservation of the total number of shares throughout the simulation.

* **Data Consistency**: Verification checks ensure that the data used for visualization matches the actual positions held by agents.

## Future Work & Extensions

This model provides a foundation for many extensions:

* **Market Makers**: Introduce agents who provide liquidity by posting bid/ask quotes and profit from the spread.

* **Adaptive Agents**: Implement learning mechanisms allowing agents to adapt their strategies based on past performance.

* **Realistic Fundamental Process**: Enhance the fundamental value process to better reflect realistic asset valuation changes.

* **Order Book Dynamics**: Replace simple price impact logic with a realistic limit order book.

* **Multiple Assets**: Extend the model to simulate trading across correlated assets.

* **Calibration**: Calibrate model parameters to reproduce stylized facts observed in real financial data.

* **Regulation Testing**: Evaluate impacts of different market regulations and circuit breakers.

## Project Structure

* `agents/`: Agent implementations (fundamentalist.py, chartist.py, noise_trader.py, base_agent.py)
* `market/`: Market environment implementation
* `simulation/`: Simulation engine
* `analysis/`: Analysis and visualization tools
* `config.py`: Configuration parameters
* `run.py`: Entry point for running simulations

## License

MIT License 