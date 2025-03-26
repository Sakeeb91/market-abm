# Market Agent-Based Model (ABM)

This project implements an Agent-Based Model for simulating market dynamics with different types of trading agents. The simulation includes fundamentalist and chartist agents, with plans to add market makers and learning agents.

## Features

- Two types of trading agents:
  - Fundamentalists: Base decisions on fundamental value
  - Chartists: Base decisions on price trends and technical indicators
- Market environment with price dynamics based on supply/demand
- Simulation engine for running market scenarios
- Analysis tools for studying market metrics and behaviors

## Project Structure

```
market_abm/
├── main.py             # Main simulation script
├── config.py           # Configuration parameters
├── agents/            # Agent implementations
├── market/            # Market environment
├── simulation/        # Simulation engine
├── analysis/          # Analysis tools
├── utils/             # Helper functions
├── data/              # Simulation data
└── results/           # Generated plots and reports
```

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main simulation:
```bash
python main.py
```

## Future Enhancements

- Market makers for liquidity provision
- Agent learning through reinforcement learning
- News shocks and fundamental changes
- Order book dynamics
- Advanced market metrics and analysis 