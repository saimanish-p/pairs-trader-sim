import matplotlib.pyplot as plt
import numpy as np
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
        ax.set_title('Profit and Loss Over Time', fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('PnL', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Rotate x-axis dates for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        logging.error(f"Error plotting PnL: {e}")
        return None

def plot_asset_prices(results):
    if results is None or 'Asset1_Price' not in results.columns or 'Asset2_Price' not in results.columns:
        logging.warning("No valid results data for asset price plotting")
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Plot both asset prices
        ax.plot(results.index, results['Asset1_Price'], label='Aluminium', color='blue')
        ax.plot(results.index, results['Asset2_Price'], label='Lead', color='orange')
        
        # Format plot
        ax.set_title('Aluminium and Lead Prices Over Time', fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Rotate x-axis dates for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        logging.error(f"Error plotting asset prices: {e}")
        return None      
    
def plot_zscore(results):

    if results is None or 'Z-Score' not in results.columns:
        logging.warning("No valid results data for Z-Score plotting")
        return None
    
    try:
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Plot Z-Score
        ax.plot(results.index, results['Z-Score'], label='Z-Score', color='purple')
        
        # Add threshold lines
        threshold = results['Z-Score'].abs().max() * 0.5  # Estimate threshold from data
        if 'Signal' in results.columns:
            # Try to determine actual threshold from data
            buy_signals = results[results['Signal'] == 'BUY']
            sell_signals = results[results['Signal'] == 'SELL']
            
            if not buy_signals.empty and not sell_signals.empty:
                buy_threshold = buy_signals['Z-Score'].max()
                sell_threshold = sell_signals['Z-Score'].min()
                threshold = min(abs(buy_threshold), abs(sell_threshold))
        
        ax.axhline(y=threshold, color='r', linestyle='--', alpha=0.7, label=f'Threshold (+{threshold:.2f})')
        ax.axhline(y=-threshold, color='g', linestyle='--', alpha=0.7, label=f'Threshold (-{threshold:.2f})')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.2)
        
        # Highlight buy/sell regions
        ax.fill_between(results.index, results['Z-Score'], threshold, 
                        where=results['Z-Score'] > threshold, 
                        color='red', alpha=0.2, label='Sell Zone')
        ax.fill_between(results.index, results['Z-Score'], -threshold, 
                        where=results['Z-Score'] < -threshold, 
                        color='green', alpha=0.2, label='Buy Zone')
        
        # Format plot
        ax.set_title('Z-Score Over Time', fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Z-Score', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Rotate x-axis dates for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        logging.error(f"Error plotting Z-Score: {e}")
        return None

def plot_spread(results):

    if results is None or 'Asset1_Price' not in results.columns or 'Asset2_Price' not in results.columns:
        logging.warning("No valid results data for spread plotting")
        return None
    
    try:
        # Calculate spread as log of price ratio
        spread = np.log(results['Asset1_Price'] / results['Asset2_Price'])
        
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Plot spread
        ax.plot(results.index, spread, label='Log Price Ratio', color='blue')
        
        # Calculate and plot moving average of spread
        window = min(30, len(spread))
        if window > 0:
            ma = spread.rolling(window=window).mean()
            ax.plot(results.index, ma, label=f'{window}-day MA', color='red', linestyle='--')
        
        # Format plot
        ax.set_title('Spread Between Aluminium & Lead (Log Price Ratio)', fontsize=14)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Log(Asset1/Asset2)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Rotate x-axis dates for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        logging.error(f"Error plotting spread: {e}")
        return None

def calculate_performance_metrics(results):
    if results is None or 'PnL' not in results.columns:
        logging.warning("No valid results data for performance metrics calculation")
        return None
    
    try:
        # Extract PnL series
        pnl = results['PnL']
        
        # Calculate daily returns
        daily_returns = pnl.diff().fillna(0)
        
        # Calculate metrics
        total_return = pnl.iloc[-1] if not pnl.empty else 0
        
        # Calculate running maximum
        running_max = pnl.cummax()
        
        # Calculate absolute drawdown (in dollars)
        abs_drawdown = pnl - running_max
        max_drawdown = abs_drawdown.min()
                
        # Count trades
        status_changes = results['Status'].ne(results['Status'].shift()).cumsum()
        trades = status_changes.max() if not status_changes.empty else 0
        
        # Calculate win/loss ratio
        if 'MTM' in results.columns:
            wins = results[results['MTM'] > 0]['MTM'].count()
            losses = results[results['MTM'] < 0]['MTM'].count()
            win_rate = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
            
            # Average profit/loss
            avg_win = results[results['MTM'] > 0]['MTM'].mean() if wins > 0 else 0
            avg_loss = results[results['MTM'] < 0]['MTM'].mean() if losses > 0 else 0
            profit_factor = abs(avg_win * wins / (avg_loss * losses)) if losses > 0 and avg_loss != 0 else float('inf')
        else:
            wins, losses, win_rate, avg_win, avg_loss, profit_factor = 0, 0, 0, 0, 0, 0
        
        # Calculate Sharpe ratio (assuming risk-free rate of 0)
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252) if daily_returns.std() != 0 else 0
        
        # Create metrics dictionary
        metrics = {
            'Total Return': total_return,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio,
            'Number of Trades': trades,
            'Win Rate %': win_rate,
            'Profit Factor': profit_factor,
            'Average Win': avg_win,
            'Average Loss': avg_loss
        }
        
        return metrics
    
    except Exception as e:
        logging.error(f"Error calculating performance metrics: {e}")
        return None
        
def plot_performance_metrics(metrics):
    if metrics is None:
        logging.warning("No valid metrics data for performance metrics plotting")
        return None
    
    try:
        # Create figure with multiple subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Return vs Drawdown
        axs[0, 0].bar(['Total Return', 'Max Drawdown'], 
                     [metrics['Total Return'], metrics['Max Drawdown']], 
                     color=['green', 'red'])
        axs[0, 0].set_title('Return vs Max Drawdown')
        axs[0, 0].grid(axis='y', alpha=0.3)
        
        # Plot 2: Win Rate
        axs[0, 1].pie([metrics['Win Rate %'], 100 - metrics['Win Rate %']], 
                     labels=['Wins', 'Losses'], 
                     colors=['green', 'red'], 
                     autopct='%1.1f%%',
                     startangle=90)
        axs[0, 1].set_title('Win/Loss Ratio')
        
        # Plot 3: Average Win vs Average Loss
        axs[1, 0].bar(['Average Win', 'Average Loss'], 
                     [metrics['Average Win'], metrics['Average Loss']], 
                     color=['green', 'red'])
        axs[1, 0].set_title('Average Win vs Average Loss')
        axs[1, 0].grid(axis='y', alpha=0.3)
        
        # Plot 4: Key Metrics
        metrics_to_show = {
            'Sharpe Ratio': metrics['Sharpe Ratio'],
            'Profit Factor': min(metrics['Profit Factor'], 10),  # Cap at 10 for display
            'Number of Trades': metrics['Number of Trades']
        }
        axs[1, 1].bar(metrics_to_show.keys(), metrics_to_show.values(), color='blue')
        axs[1, 1].set_title('Key Performance Metrics')
        axs[1, 1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        return fig
    
    except Exception as e:
        logging.error(f"Error plotting performance metrics: {e}")
        return None

def display_results():

    st.title("Pairs Trading Strategy Results")
    
    st.markdown("---")
    
    st.caption("Note:")
    st.write("The following are the results of a rudimentary Pairs-Trader strategy implemented with Aluminium and Lead as our chosen asset pair with data ranging from 1st April 2014 to 1st July 2016. This strategy is not tradeable and is for education purposes ONLY.")
    st.write("Read the documentation (README.md file) highlighting all assumptions, limitations, and future improvements for this project.")
    
    st.markdown("---")
    
    results = run_strategy()
    
    if results is None:
        st.error("Strategy execution failed. Check logs for details.")
        return
    
    # Calculate performance metrics
    metrics = calculate_performance_metrics(results)
    
    # Display metrics in a nice format
    if metrics:
        st.subheader("Performance Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Return", f"${metrics['Total Return']:.2f}")
            st.metric("Sharpe Ratio", f"{metrics['Sharpe Ratio']:.2f}")
            st.metric("Number of Trades", f"{metrics['Number of Trades']}")
        
        with col2:
            st.metric("Max Drawdown", f"${metrics['Max Drawdown']:.2f}")
            st.metric("Win Rate", f"{metrics['Win Rate %']:.2f}%")
            st.metric("Profit Factor", f"{metrics['Profit Factor']:.2f}")
        
        with col3:
            st.metric("Average Win", f"${metrics['Average Win']:.2f}")
            st.metric("Average Loss", f"${metrics['Average Loss']:.2f}")
    
    st.markdown("---")

    # Display PnL chart
    st.subheader("Profit and Loss")
    pnl_fig = plot_pnl(results)
    if pnl_fig:
        st.pyplot(pnl_fig)
    
    st.markdown("---")

    # Display asset prices chart
    st.subheader("Aluminium and Lead Prices")
    prices_fig = plot_asset_prices(results)
    if prices_fig:
        st.pyplot(prices_fig)

    st.markdown("---")
        
    # Display Z-Score chart
    st.subheader("Z-Score")
    zscore_fig = plot_zscore(results)
    if zscore_fig:
        st.pyplot(zscore_fig)

    st.markdown("---")

    # Display spread chart
    st.subheader("Price Spread")
    spread_fig = plot_spread(results)
    if spread_fig:
        st.pyplot(spread_fig)

    st.markdown("---")
    
    # Display performance metrics visualisation
    if metrics:
        st.subheader("Performance Visualisation")
        metrics_fig = plot_performance_metrics(metrics)
        if metrics_fig:
            st.pyplot(metrics_fig)

    st.markdown("---")
    
    # Display results table
    st.subheader("Trade Log")
    st.dataframe(results)
