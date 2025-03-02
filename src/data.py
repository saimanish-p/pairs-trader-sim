import pandas as pd
from pathlib import Path
import logging

def read_price_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    try:
        # Define paths relative to data directory
        data_dir = Path("data")
        path1 = data_dir / "Aluminium_Price_Data.csv"
        path2 = data_dir / "Lead_Price_Data.csv"
        
        # Read CSV files
        df1 = pd.read_csv(path1)
        df2 = pd.read_csv(path2)
        
        # Validate required columns exist
        required_cols = ['Date', 'Close']
        if not all(col in df1.columns for col in required_cols):
            raise ValueError(f"Missing required columns in {path1}")
        if not all(col in df2.columns for col in required_cols):
            raise ValueError(f"Missing required columns in {path2}")
            
        # Set index and sort by date
        for df in [df1, df2]:
            df.set_index('Date', inplace=True)
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            
        # Get common dates
        common_dates = df1.index.intersection(df2.index)
        df1 = df1.loc[common_dates]
        df2 = df2.loc[common_dates]

        # Check for missing values before dropping
        missing_count1 = df1['Close'].isna().sum()
        missing_count2 = df2['Close'].isna().sum()
        
        if missing_count1 > 0 or missing_count2 > 0:
            logging.warning(f"Found missing values in Asset1: {missing_count1}, Asset2: {missing_count2}. These will be dropped.")
                
        # Remove any rows with missing values
        df1 = df1.dropna(subset=['Close'])
        df2 = df2.dropna(subset=['Close'])
        
        return df1, df2
        
    except Exception as e:
        logging.error(f"Error reading price data: {e}")
        raise

def validate_lookback_period(df1: pd.DataFrame, df2: pd.DataFrame, lookback_period: int) -> bool:

    return len(df1) >= lookback_period and len(df2) >= lookback_period


