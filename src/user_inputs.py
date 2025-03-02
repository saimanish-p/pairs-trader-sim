import streamlit as st

def get_params():

    st.sidebar.header("Strategy Parameters")
    
    params = {
        'threshold': st.sidebar.slider("Z-score Threshold", 1.0, 3.0, 1.25),
        'lookback_period': st.sidebar.slider("Lookback Period", 40, 120, 40),
        'initial_start': st.sidebar.number_input("Initial Start Index", min_value=0, max_value=100, value=10, help="Starting index for the initial z-score calculation window"),
        'initial_end': st.sidebar.number_input("Initial End Index", min_value=10, max_value=110, value=30, help="Ending index for the initial z-score calculation window"),
        'lot_size_1': st.sidebar.number_input("Lot Size Asset 1", 1000, 10000, 5000),
        'lot_size_2': st.sidebar.number_input("Lot Size Asset 2", 1000, 10000, 5000),
        'stop_loss': st.sidebar.number_input("Stop Loss", -20000, 0, -10000),
        'take_profit': st.sidebar.number_input("Take Profit", 0, 50000, 20000)
    }
    
    return params

def validate_params(params: dict) -> tuple[bool, str]:

    # Check that initial_end > initial_start
    if params['initial_end'] <= params['initial_start']:
        return False, "Initial End Index must be greater than Initial Start Index"
    
    # Check that initial window size is reasonable
    window_size = params['initial_end'] - params['initial_start']
    if window_size < 5:
        return False, f"Z-score window size ({window_size}) is too small, should be at least 5"
    if window_size > 30:
        return False, f"Z-score window size ({window_size}) is too large, should be at most 30"
    
    # Check that initial window fits within lookback period
    if params['initial_end'] > params['lookback_period']:
        return False, "Initial End Index cannot exceed Lookback Period"
    
    # Check that threshold is reasonable
    if params['threshold'] < 1.0:
        return False, "Z-score threshold is too small, should be at least 1.0"
    if params['threshold'] > 3.0:
        return False, "Z-score threshold is too large, should be at most 3.0"
    
    # Check that stop loss is negative and take profit is positive
    if params['stop_loss'] >= 0:
        return False, "Stop Loss should be negative"
    if params['take_profit'] <= 0:
        return False, "Take Profit should be positive"
    
    # All checks passed
    return True, ""    