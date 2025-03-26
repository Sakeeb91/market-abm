# Market ABM - Agent-Based Market Simulation

A flexible and customizable agent-based model of financial markets, simulating interactions between fundamentalists, chartists, and noise traders.

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

Simulation parameters can be easily modified in the `market_abm/config.py` file. Key parameters include:

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
cd market_abm
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

* `market_abm/agents/`: Agent implementations (fundamentalist.py, chartist.py, noise_trader.py, base_agent.py)
* `market_abm/market/`: Market environment implementation
* `market_abm/simulation/`: Simulation engine
* `market_abm/analysis/`: Analysis and visualization tools
* `market_abm/config.py`: Configuration parameters
* `market_abm/run.py`: Entry point for running simulations

## License

MIT License 