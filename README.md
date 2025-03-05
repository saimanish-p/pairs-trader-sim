# Pairs Trading Simulator

## Contact info

Email: saimanishprabhakar2020@gmail.com

[Linkedin](https://www.linkedin.com/in/saimanish-prabhakar-3074351a0/)

## About the project

A basic pairs trading simulator implemented with a single asset pair (Aluminium and Lead) to showcase the concept 
of Statistical Arbitrage trading. 

The project allows user to customise several key parameters such as z-score threshold, lookback period, initial 
start and end index, lot sizes, stop loss, and take profit levels enabling flexible strategy testing. 

The user can analyse performance metrics of the strategy based on their inputs and visualise the results using a minimalistic dashboard and intuitive charts. 

Lastly, the project also provides the user a trade log covering all decisions made by the model during the trading data range (01/04/2014 - 01/07/2016) including BUY, SELL, and HOLD signals alongisde asset prices of both Aluminium and Lead, z-scores, buy and sell prices, MTM, PnL, and cointegration status. 

## Built with

- <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy">

- <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas">

- <img src="https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=python&logoColor=white" alt="Matplotlib">

- <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">

- <img src="https://img.shields.io/badge/Pathlib-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Pathlib">

- <img src="https://img.shields.io/badge/Statsmodels-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Statsmodels">

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your_username/pairs-trader-sim.git
cd pairs-trader-sim
```
### 2. Create Virtual Environment (Optional but Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required libraries
pip install -r requirements.txt

# When done working on the project
deactivate
```
### Alternative: Direct Installation
```bash
# If you prefer not to use a virtual environment, you can directly install dependencies
pip install -r requirements.txt
```
### 3. Change git remote url to avoid accidental pushes to base project
```bash
git remote set-url origin github_username/options-strat-payoff
git remote -v # confirm the changes
```
## Usage

### Video walkthrough of project

Here is a video explaining everything about the concept of the project, its features, and how to get the most 
out of it. Alternatively, you can read the written step-by-step walkthrough of the project alongside some images 
below if you can't stand my voice!

*** Video Tutorial - Coming soon ***

### Step-by-Step image walkthorugh of project

Adjust the parameters from default values to change strategy logic.

![Input Parameters](images/input_parameters.png)

If you are unsure what the variable represents, please hover over the question mark symbol beside the specific 
parameter for additional context. 

![Help Functionality](images/help_functionality_input_parameters.png)

A lot of the project's strategy/logic has been pre-validated and is contained within the code, the only message a user 
will see is if the initial start price (i.e. Starting point within the lookback period for initial z-score calculation)
is greater than the lookback period (Number of days used to calculate statistical relationships) which will result in the
following prompt being displayed. 

Note that future updates will allow user to check specified logs.

![Error handling](images/validation-error_handling.png)

The first thing you will see after customising the input parameters to your choosing is the performance metrics section
which essentially displays a top-level overview of the strategy's performance highlighting specific metrics such as 
Total Return, Sharpe Ratio, Number of Trades, Max Drawdown, Win Rate, Profit Factor, Average Win, and Average Loss.

Note that the results illustrated below are based on the 'best' default parameters. The performance drastically
varies upon customisation of parameters. For details on technical assumptions / limitations, refer to relevant sections
later in this file. 

![Performance Metrics](images/performance_metrics_example.png)

Following that section, you will be greeted by a series of figures, starting with PnL of the strategy over the trading period.

![Profit and Loss graph](images/Example_PnL_graph.png)

The second figure, and one of two static figures (i.e. not affected by user parameters) is the 'Close' prices of Aluminium and Lead respectively which make up our asset pair for this sim. 

![Aluminium and Lead Prices](images/Aluminium_and_Lead_Prices_graph.png)

The subsequent figure, illustrates the z-score line alongside the threshold lines (both +ve and -ve) which each represent the sell and buy zones respectively highlighted using appropriate red and green fill. This figure essentially visualises the signal generation logic of our pairs trader.

![Z-score Over Time](images/Z-score_graph.png)

Similar to the price figure of the asset pair, the spread between Aluminium and Lead is also a static figure. We visualise the log price ratio with the 30 day Moving Average.

![Price Spread](images/price_spread_graph.png)

Our final figure with multiple subplots, essentially visualises the same performance metrics from our mini-dashaboard in the first section, rounding up our visual analysis of the strategy.  

![Performance Visualisation](images/performance_viz_graph.png)

Lastly, we present a trade log allowing the user to analyse each trade entered, exited, or avoided based off their chosen parameters in a formatted table containing all the key variables relevant to this simple implementation of a pairs trading strategy. 

![Trade Log](images/trade_log_example_graph.png)

## Assumptions, Limitations, and Suggested Future Improvements

### Assumptions

- Statistical Model: Uses Augmented Dickey-Fuller (ADF) test for cointegration and static Z-score calculations
- Execution: Assumes perfect trade execution at closing prices.
- Position Sizing: Assumes fixed position sizing
- Risk Management: Relies on basic stop-loss and take-profit thresholds
- Technical Architecture: Assumes a sequential backtest without the capability for parallel or event-driven processing.

### Limitations

- Data Processing: Relies on static data sources and does not connect to live market feeds.
- Cointegration Testing: Missing more robust methods like Johansen test that would better capture long-term relationships between assets.
- Z-Score Calculation: Utilises a static, rolling window without considering changing market conditions or half-life analysis, limiting its ability to optimize entry/exit.
- Execution: Does not model slippage, transaction costs, or market impact, resulting in unrealistic profit assumptions.
- Position Sizing: Assumes fixed lot sizes instead of dynamic sizing based on volatility or risk parity, limiting risk management flexibility.
- Risk Management: Basic risk controls like stop-loss and take-profit do not account for more advanced techniques such as VaR or expected shortfall.
- Technical Architecture: The backtesting system is sequential, lacks parallel processing, and does not support real-time, event-driven trading. It also does not employ performance optimiaations like vectorized operations.

## Suggested Future Improvements

This implementation serves as a rudimentary educational tool and would require a more robust suite of methodological approaches to ensure it is suitable for live trading. 

A production-grade strategy should address the following:

- Real-Time Data Integration: Connect to live market feeds and enhance data cleaning
- Enhanced Statistical Modeling: Adopt more robust cointegration methods and adaptive Z-score calculations.
- Realistic Execution Modeling: Account for slippage, transaction costs, and market impact.
- Dynamic Position Sizing: Implement volatility and risk-based position sizing.
- Optimised Architecture: Enable parallel processing and event-driven design for faster, real-time execution.
- Regime Detection and ML Integration: Use regime detection and machine learning for parameter optimisation.
- Live Trading Infrastructure: Develop real-time monitoring, logging, and failover systems for operational resilience.



































