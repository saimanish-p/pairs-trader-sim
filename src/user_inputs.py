import streamlit as st

def get_params():
    st.sidebar.header("Strategy Parameters")
    
    params = {
        'threshold': st.sidebar.slider(
            "Z-score Threshold", 
            1.0, 3.0, 1.25, 
            help="Determines when to enter/exit trades. Higher values (e.g., 2.0) are more conservative, requiring larger divergences. Lower values (e.g., 1.0) generate more frequent trades but may include false signals."
        ),
        
        'lookback_period': st.sidebar.slider(
            "Lookback Period", 
            40, 120, 40, 
            help="Number of days used to calculate statistical relationships. Shorter periods (40-60 days) adapt quickly to changing markets but may be less stable. Longer periods (80-120 days) provide more statistical robustness but react slower to market changes."
        ),
        
        'initial_start': st.sidebar.number_input(
            "Initial Start Index", 
            min_value=0, 
            max_value=100, 
            value=10, 
            help="Starting point within the lookback period for initial z-score calculation. This creates a 'training window' for establishing the baseline relationship between assets."
        ),
        
        'initial_end': st.sidebar.number_input(
            "Initial End Index", 
            min_value=10, 
            max_value=110, 
            value=30, 
            help="Ending point within the lookback period for initial z-score calculation. The difference between end and start indices determines the size of the training window."
        ),
        
        'lot_size_1': st.sidebar.number_input(
            "Lot Size (Aluminium)", 
            1000, 10000, 5000, 
            help="Trading quantity for Aluminium in USD. Larger lot sizes increase potential profit/loss and affect the capital efficiency of the strategy."
        ),
        
        'lot_size_2': st.sidebar.number_input(
            "Lot Size (Lead)", 
            1000, 10000, 5000, 
            help="Trading quantity for Lead in USD. Ideally balanced with Aluminium lot size to create a market-neutral position that hedges against overall market movements."
        ),
        
        'stop_loss': st.sidebar.number_input(
            "Stop Loss", 
            -20000, 0, -10000, 
            help="Maximum acceptable loss in USD before automatically exiting a trade. More negative values allow more room for the strategy to work through temporary adverse movements."
        ),
        
        'take_profit': st.sidebar.number_input(
            "Take Profit", 
            0, 50000, 20000, 
            help="Target profit in USD at which the strategy automatically exits a profitable trade. Higher values allow trades to capture more profit from strong convergence moves."
        )
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