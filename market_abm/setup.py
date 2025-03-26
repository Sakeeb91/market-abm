from setuptools import setup, find_packages

setup(
    name="market_abm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "tqdm>=4.62.0",
    ],
    author="Market ABM Developers",
    author_email="your.email@example.com",
    description="Agent-Based Model for market dynamics simulation",
    keywords="abm, market, simulation, agent-based-model",
    python_requires=">=3.6",
) 