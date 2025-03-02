import matplotlib.pyplot as plt
import logging
import streamlit as st

from src.trader import run_strategy

def plot_pnl(results):

    if results is None or 'PnL' not in results.columns:
        logging.warning("No valid results data for PnL plotting")
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Plot PnL curve
        ax.plot(results.index, results['PnL'], label='PnL', color='blue')
        
        # Format plot
        ax.set_title('PnL', fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('PnL', fontsize=12)
        ax.grid(True)
        ax.legend()
        
        # Rotate x-axis dates for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        logging.error(f"Error plotting PnL: {e}")
        return None

def display_results():

    st.title("Pairs Trading Strategy Results")
    
    results = run_strategy()
    
    if results is None:
        st.error("Strategy execution failed. Check logs for details.")
        return
    
    # Display PnL chart
    st.subheader("Profit and Loss")
    pnl_fig = plot_pnl(results)
    if pnl_fig:
        st.pyplot(pnl_fig)
    
    # Display results table
    st.subheader("Strategy Results")
    st.dataframe(results)
    
    # Download link for CSV
    st.download_button(
        label="Download Results as CSV",
        data=results.to_csv().encode('utf-8'),
        file_name='pairs_trading_results.csv',
        mime='text/csv',
    )