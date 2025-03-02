import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import logging

from src.data import read_price_data, validate_lookback_period
from src.user_inputs import get_params, validate_params


def cointegration_test(df1, df2, lookback_period, current_idx):
    
    # Calculate start index based on lookback period
    start_idx = max(0, current_idx - lookback_period)
    
    # Get window data
    x = df1.iloc[start_idx:current_idx]
    y = df2.iloc[start_idx:current_idx]
    
    # Run OLS regression
    result = sm.OLS(x['Close'], y['Close']).fit()
    
    # Test residuals for stationarity
    adf_result = adfuller(result.resid)
    
    # Check if cointegrated (ADF test statistic < critical value at 5% significance)
    is_cointegrated = adf_result[0] <= adf_result[4]['5%'] and adf_result[1] <= 0.05

    if not is_cointegrated:
        logging.warning(f"Assets are not cointegrated at current window (index {current_idx})")
        logging.warning(f"ADF test statistic: {adf_result[0]}, Critical value (5%): {adf_result[4]['5%']}, p-value: {adf_result[1]}")

    return adf_result, is_cointegrated

def calculate_zscore(df1, df2, zscore_start_idx, zscore_end_idx):
    
    # Get price series for the window
    s1 = df1['Close'].iloc[zscore_start_idx:zscore_end_idx]
    s2 = df2['Close'].iloc[zscore_start_idx:zscore_end_idx]
    
    # Calculate spread as log of price ratio
    spread = np.log(s1 / s2)
    
    # Calculate mean and standard deviation of the spread
    mean_spread = np.mean(spread)
    std_spread = np.std(spread)
    
    # Calculate current spread
    current_spread = np.log(df1['Close'].iloc[zscore_end_idx] / df2['Close'].iloc[zscore_end_idx])
    
    # Calculate z-score
    zscore = (current_spread - mean_spread) / std_spread if std_spread > 0 else 0
    
    return zscore

def generate_signal(zscore, threshold, is_cointegrated):

    # Validate inputs
    if zscore is None:
        logging.warning("Z-score calculation must be run before generating signals")
        return 0, "HOLD"
        
    # Check cointegration status first
    if not is_cointegrated:
        logging.warning("Assets are not cointegrated - no trading signal generated")
        return 0, "HOLD"
    
    # Generate signals based on z-score
    if zscore > threshold:
        logging.info(f"SELL signal generated: z-score ({zscore:.2f}) > threshold ({threshold})")
        return -1, "SELL"
    elif zscore < -threshold:
        logging.info(f"BUY signal generated: z-score ({zscore:.2f}) < -threshold ({-threshold})")
        return 1, "BUY"
    else:
        logging.info(f"HOLD signal: z-score ({zscore:.2f}) within threshold range ({-threshold} to {threshold})")
        return 0, "HOLD"

def update_status(prev_status, mtm, stop_loss, take_profit, signal, is_cointegrated):

    # Handle initial case or reset cases
    if prev_status is None or prev_status in ["HOLD", "SL", "TP", "CB"]:
        return signal
    
    # Check for cointegration break
    if not is_cointegrated:
        logging.info("Cointegration break detected - closing position")
        return "CB"  # Cointegration Break
    
    # Check for stop loss or take profit if MTM is available
    if mtm is not None:
        # Check for stop loss
        if mtm < stop_loss:
            logging.info(f"Stop loss triggered: MTM ({mtm}) < stop loss ({stop_loss})")
            return "SL"  # Stop Loss
        
        # Check for take profit
        if mtm > take_profit:
            logging.info(f"Take profit triggered: MTM ({mtm}) > take profit ({take_profit})")
            return "TP"  # Take Profit
    
    # If none of the above conditions are met, maintain previous status
    return prev_status
    
def calculate_buy_price(prev_status, prev_buy_price, signal, status, df1, df2, current_idx):

    # If status hasn't changed, maintain the previous buy price
    if status == prev_status:
        logging.info(f"Status unchanged ({status}), maintaining previous buy price: {prev_buy_price}")
        return prev_buy_price
    
    # No buy price needed for these statuses
    if status in ["SL", "TP", "CB", "HOLD"]:
        logging.info(f"No buy price needed for status: {status}")
        return None
    
    # Calculate buy price based on signal
    if signal == "BUY":
        buy_price = df1['Close'].iloc[current_idx]
        logging.info(f"BUY signal: Setting buy price to asset 1 close price: {buy_price}")
        return buy_price
    elif signal == "SELL":
        buy_price = df2['Close'].iloc[current_idx]
        logging.info(f"SELL signal: Setting buy price to asset 2 close price: {buy_price}")
        return buy_price
    else:
        logging.warning(f"Unrecognized signal: {signal}, cannot calculate buy price")
        return None
        
def calculate_sell_price(prev_status, prev_sell_price, signal, status, df1, df2, current_idx):

    # If status hasn't changed, maintain the previous sell price
    if status == prev_status:
        logging.info(f"Status unchanged ({status}), maintaining previous sell price: {prev_sell_price}")
        return prev_sell_price
    
    # No sell price needed for these statuses
    if status in ["SL", "TP", "CB", "HOLD"]:
        logging.info(f"No sell price needed for status: {status}")
        return None
    
    # Calculate sell price based on signal
    if signal == "BUY":
        sell_price = df2['Close'].iloc[current_idx]
        logging.info(f"BUY signal: Setting sell price to asset 2 close price: {sell_price}")
        return sell_price
    elif signal == "SELL":
        sell_price = df1['Close'].iloc[current_idx]
        logging.info(f"SELL signal: Setting sell price to asset 1 close price: {sell_price}")
        return sell_price
    else:
        logging.warning(f"Unrecognized signal: {signal}, cannot calculate sell price")
        return None
    
def calculate_mtm(df1, df2, prev_status, prev_sell_price, prev_buy_price, lot_size_1, lot_size_2, current_idx):

    # Validators to ensure accuracy of parameters before mtm calculation
    if current_idx < 0 or current_idx >= len(df1) or current_idx >= len(df2):
        logging.warning(f"Invalid index {current_idx} for calculating MTM")
        return None
        
    if prev_sell_price is None or prev_buy_price is None:
        logging.info("No previous prices available for MTM calculation")
        return None
    
    # Calculate MTM based on previous status
    if prev_status == "BUY":
        mtm = (prev_sell_price - df2['Close'].iloc[current_idx]) * lot_size_2 + \
              (df1['Close'].iloc[current_idx] - prev_buy_price) * lot_size_1
        logging.info(f"BUY position MTM: {mtm}")
        return mtm
    elif prev_status == "SELL":
        mtm = (prev_sell_price - df1['Close'].iloc[current_idx]) * lot_size_1 + \
              (df2['Close'].iloc[current_idx] - prev_buy_price) * lot_size_2
        logging.info(f"SELL position MTM: {mtm}")
        return mtm
    else:
        logging.info(f"No active position (status: {prev_status}), MTM not applicable")
        return None
    
def run_strategy():

    #Get user parameters
    params = get_params()
    
    # Read price data
    try:
        df1, df2 = read_price_data()
        logging.info(f"Successfully loaded data: Asset1 ({len(df1)} rows), Asset2 ({len(df2)} rows)")
    except Exception as e:
        logging.error(f"Failed to read price data: {e}")
        return None
    
    # Extract parameters
    threshold = params['threshold']
    lookback_period = params['lookback_period']
    initial_start = params['initial_start']
    initial_end = params['initial_end']
    lot_size_1 = params['lot_size_1']
    lot_size_2 = params['lot_size_2']
    stop_loss = params['stop_loss']
    take_profit = params['take_profit']

    # Validate parameters
    is_valid, error_message = validate_params(params)
    if not is_valid:
        logging.error(f"Parameter validation failed: {error_message}")
        return None

    # Validate lookback period against available data
    if not validate_lookback_period(df1, df2, lookback_period):
        logging.error(f"Lookback period {lookback_period} exceeds available data")
        return None
    
    # Initialize variables
    prev_status = None
    prev_buy_price = None
    prev_sell_price = None
    pnl = 0

    # Create results dataframe
    results = pd.DataFrame(columns=[
        'Date', 'Asset1_Price', 'Asset2_Price', 'Z-Score', 
        'Signal_Value', 'Signal', 'Status', 'Buy_Price', 
        'Sell_Price', 'MTM', 'PnL', 'Is_Cointegrated'
    ])

    # Set initial window indices
    start_idx = initial_start
    end_idx = initial_end

    # Run strategy for each day
    for current_idx in range(end_idx, len(df1)):
        logging.info(f"Processing day {current_idx}, date: {df1.index[current_idx]}")

        # Test for cointegration
        adf_result, is_cointegrated = cointegration_test(df1, df2, lookback_period, current_idx)
        
        # Calculate z-score
        zscore = calculate_zscore(df1, df2, start_idx, current_idx)

        # Generate signal
        signal_value, signal = generate_signal(zscore, threshold, is_cointegrated)
        
        # Calculate MTM
        mtm = calculate_mtm(df1, df2, prev_status, prev_sell_price, prev_buy_price, 
                           lot_size_1, lot_size_2, current_idx)
        
        # Update status
        status = update_status(prev_status, mtm, stop_loss, take_profit, signal, is_cointegrated)
        
        # Calculate buy and sell prices
        buy_price = calculate_buy_price(prev_status, prev_buy_price, signal, status, 
                                       df1, df2, current_idx)
        
        sell_price = calculate_sell_price(prev_status, prev_sell_price, signal, status, 
                                         df1, df2, current_idx)

        # Calculate PnL
        if status in ["TP", "SL", "CB"] and mtm is not None:
            pnl += mtm
            logging.info(f"Position closed: {status}, MTM: {mtm}, Total PnL: {pnl}")

        # Store results
        results.loc[current_idx] = [
            df1.index[current_idx],
            df1['Close'].iloc[current_idx],
            df2['Close'].iloc[current_idx],
            zscore,
            signal_value,
            signal,
            status,
            buy_price,
            sell_price,
            mtm,
            pnl,
            is_cointegrated
        ]

        # Update previous values for next iteration
        prev_status = status
        prev_buy_price = buy_price
        prev_sell_price = sell_price
        
        # Update window indices
        start_idx += 1
    
    # Set date as index
    results.set_index('Date', inplace=True)
    
    logging.info(f"Strategy completed with final PnL: {pnl}")
    
    # Save results to CSV
    try:
        results.to_csv('pairs_trading_results.csv')
        logging.info("Results saved to pairs_trading_results.csv")
    except Exception as e:
        logging.warning(f"Failed to save results to CSV: {e}")
    
    return results


