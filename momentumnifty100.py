import yfinance as yf
import pandas as pd
import numpy as np
import time
import logging
import sys
import traceback

logger = logging.getLogger(__name__)

# Define a smaller subset of symbols to reduce API load
symbols = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "HINDUNILVR.NS",
    "INFY.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
    "AXISBANK.NS", "LT.NS", "MARUTI.NS", "ASIANPAINT.NS", "HCLTECH.NS",
    "SUNPHARMA.NS", "BAJFINANCE.NS", "TATASTEEL.NS", "POWERGRID.NS", "TITAN.NS",
    "NTPC.NS", "JSWSTEEL.NS", "ADANIPORTS.NS", "ONGC.NS", "TATAMOTORS.NS"
]

def safe_download(symbol_list, period, interval, max_retries=3, sleep_time=2):
    """
    Safely download data with error handling and retries
    """
    # Reduce the batch size to avoid overwhelming the API
    batch_size = 5
    all_data = pd.DataFrame()
    
    # Create batches of symbols
    symbol_batches = [symbol_list[i:i + batch_size] for i in range(0, len(symbol_list), batch_size)]
    logger.info(f"Downloading data in {len(symbol_batches)} batches of size {batch_size}")
    
    for batch_idx, batch in enumerate(symbol_batches):
        logger.info(f"Processing batch {batch_idx+1}/{len(symbol_batches)}: {batch}")
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Downloading batch {batch_idx+1}, period={period}, attempt {attempt+1}")
                
                # Download data for this batch
                batch_data = yf.download(
                    batch, 
                    period=period, 
                    interval=interval,
                    progress=False,
                    group_by='ticker',
                    threads=False,  # Disable threading to avoid connection issues
                    timeout=30
                )
                
                # Handle different data structures based on batch size
                if len(batch) == 1:
                    # For single symbol, the structure is different
                    symbol = batch[0]
                    if "Adj Close" in batch_data.columns:
                        single_data = pd.DataFrame({symbol: batch_data["Adj Close"]})
                    else:
                        # If Adj Close not available, try Close
                        single_data = pd.DataFrame({symbol: batch_data["Close"] if "Close" in batch_data.columns else []})
                    
                    # Merge with existing data
                    if all_data.empty:
                        all_data = single_data
                    else:
                        all_data = pd.concat([all_data, single_data], axis=1)
                else:
                    # For multiple symbols, extract required data
                    try:
                        batch_price_data = batch_data.xs("Adj Close", axis=1, level=1, drop_level=True)
                    except Exception as e:
                        logger.warning(f"Could not extract Adj Close, trying Close: {str(e)}")
                        try:
                            batch_price_data = batch_data.xs("Close", axis=1, level=1, drop_level=True)
                        except Exception:
                            logger.error("Could not extract Close prices either, creating empty DataFrame")
                            batch_price_data = pd.DataFrame(columns=batch)
                    
                    # Merge with existing data
                    if all_data.empty:
                        all_data = batch_price_data
                    else:
                        all_data = pd.concat([all_data, batch_price_data], axis=1)
                
                # Successfully processed this batch
                break
                
            except Exception as e:
                logger.error(f"Error downloading batch {batch_idx+1} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.debug(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.warning(f"Max retries reached for batch {batch_idx+1}, skipping")
        
        # Very small delay between batches to avoid rate limiting
        time.sleep(0.1)
    
    logger.info(f"Download completed, final data shape: {all_data.shape}")
    
    # Fill any missing tickers with empty columns
    for symbol in symbol_list:
        if symbol not in all_data.columns:
            all_data[symbol] = np.nan
    
    return all_data

def get_momentum_data():
    """
    Calculate momentum data for different time periods
    """
    results = {}
    
    # Define time periods
    durations = ["5d", "10d", "1mo", "3mo", "6mo", "1y"]
    
    try:
        # Create sample data for the comparison section
        data_5d = safe_download(symbols, period="5d", interval="1d")
        if data_5d.empty:
            # Handle empty data
            raise ValueError("Unable to download 5-day data")
            
        # Calculate momentum (percentage change)
        # Check if we have enough data for calculation
        if data_5d.shape[0] <= 1:
            # Not enough data points for percentage change calculation
            logger.warning("Not enough data points for 5d calculation, using direct comparison")
            if data_5d.shape[0] == 0:
                # No data at all
                change2_5d = pd.Series(0, index=symbols)
            else:
                # Just one data point, calculate vs. first value
                first_values = data_5d.iloc[0]
                change2_5d = pd.Series(0, index=first_values.index)
        else:
            # Normal case - calculate percentage change
            change_5d = data_5d.pct_change().dropna()
            # Calculate total return over period
            change2_5d = (change_5d + 1).prod() - 1
            
        # Same for 3-month data
        data_3mo = safe_download(symbols, period="3mo", interval="1d")
        if data_3mo.empty:
            # Handle empty data
            raise ValueError("Unable to download 3-month data")
            
        # Calculate momentum (percentage change)
        # Check if we have enough data for calculation
        if data_3mo.shape[0] <= 1:
            # Not enough data points for percentage change calculation
            logger.warning("Not enough data points for 3mo calculation, using direct comparison")
            if data_3mo.shape[0] == 0:
                # No data at all
                change2_3mo = pd.Series(0, index=symbols)
            else:
                # Just one data point, calculate vs. first value
                first_values = data_3mo.iloc[0]
                change2_3mo = pd.Series(0, index=first_values.index)
        else:
            # Normal case - calculate percentage change
            change_3mo = data_3mo.pct_change().dropna()
            # Calculate total return over period
            change2_3mo = (change_3mo + 1).prod() - 1
            
        # Get top performers (handling empty or small datasets)
        if len(change2_5d) == 0:
            top_10_5d_series = pd.Series()
            top_10_5d = set()
        else:
            top_10_5d_series = change2_5d.nlargest(min(10, len(change2_5d)))
            top_10_5d = set(top_10_5d_series.index)
            
        if len(change2_3mo) == 0:
            top_10_3mo_series = pd.Series()
            top_10_3mo = set()
        else:
            top_10_3mo_series = change2_3mo.nlargest(min(10, len(change2_3mo)))
            top_10_3mo = set(top_10_3mo_series.index)
            
        # Find stocks that would appear in both datasets
        common_stocks = top_10_5d.intersection(top_10_3mo)
        
        # Remove any stocks that may be inconsistent across different timeframes
        # by ensuring no stock appears in top performers for one period and bottom performers for another
        if len(change2_5d) > 0 and len(change2_3mo) > 0:
            bottom_10_5d = set(change2_5d.nsmallest(min(10, len(change2_5d))).index)
            bottom_10_3mo = set(change2_3mo.nsmallest(min(10, len(change2_3mo))).index)
            
            # Find potential inconsistencies - stocks in top of one period but bottom of another
            inconsistent_5d = top_10_5d.intersection(bottom_10_3mo)
            inconsistent_3mo = top_10_3mo.intersection(bottom_10_5d)
            
            # Remove inconsistent stocks based on which period they have a more extreme value
            for stock in inconsistent_5d:
                if abs(change2_5d[stock]) < abs(change2_3mo[stock]):
                    top_10_5d.remove(stock)
            
            for stock in inconsistent_3mo:
                if abs(change2_3mo[stock]) < abs(change2_5d[stock]):
                    top_10_3mo.remove(stock)
        
        # Compare the sets after removing inconsistencies
        dropped_off = list(top_10_5d - top_10_3mo)
        new_entries = list(top_10_3mo - top_10_5d)
        
        results["comparison"] = {
            "dropped_from_top_10": dropped_off,
            "entered_top_10": new_entries,
            "full_5d_top_10": list(top_10_5d),
            "full_3mo_top_10": list(top_10_3mo)
        }
        
        # Process all duration data
        for duration in durations:
            logger.info(f"Processing {duration} data")
            try:
                data = safe_download(symbols, period=duration, interval="1d")
                if data.empty:
                    # Skip this duration if no data
                    logger.warning(f"No data available for {duration}")
                    results[duration] = {
                        "top_performers": {"Info": 0},
                        "bottom_performers": {"Info": 0}
                    }
                    continue
                    
                # Calculate momentum (percentage change)
                # Check if we have enough data for calculation
                if data.shape[0] <= 1:
                    # Not enough data points for percentage change calculation
                    logger.warning(f"Not enough data points for {duration} calculation, using direct comparison")
                    if data.shape[0] == 0:
                        # No data at all
                        change2 = pd.Series(0, index=symbols)
                    else:
                        # Just one data point, calculate vs. first value
                        first_values = data.iloc[0]
                        change2 = pd.Series(0, index=first_values.index)
                else:
                    # Normal case - calculate percentage change
                    change = data.pct_change().dropna()
                    # Calculate total return over period
                    change2 = (change + 1).prod() - 1
                
                # Get top and bottom performers (handling empty datasets)
                if change2.empty or len(change2) == 0:
                    top_performers = {"No Data": 0}
                    bottom_performers = {"No Data": 0}
                else:
                    # Limit to exactly 10 stocks (or fewer if not enough data)
                    max_performers = min(10, len(change2))  # Ensure we don't exceed array size
                    top_performers_series = change2.nlargest(max_performers)
                    bottom_performers_series = change2.nsmallest(max_performers)
                    
                    # Check for and eliminate duplicates between top and bottom performers
                    # Convert to sets for efficient lookup
                    top_symbols = set(top_performers_series.index)
                    bottom_symbols = set(bottom_performers_series.index)
                    
                    # Find overlap (stocks appearing in both lists)
                    overlap = top_symbols.intersection(bottom_symbols)
                    
                    # Remove overlapping stocks based on which list they are more extreme in
                    for stock in overlap:
                        # Check absolute value to determine which list the stock is more extreme in
                        top_value = abs(top_performers_series[stock])
                        bottom_value = abs(bottom_performers_series[stock])
                        
                        # Keep in the list where it's more extreme (higher absolute value)
                        if top_value >= bottom_value:
                            # Remove from bottom performers if it's more extreme in top
                            bottom_performers_series = bottom_performers_series.drop(stock)
                        else:
                            # Remove from top performers if it's more extreme in bottom
                            top_performers_series = top_performers_series.drop(stock)
                    
                    # Ensure we still have exactly 10 top and bottom performers after removing overlaps
                    # (if enough stocks are available)
                    if len(change2) > max_performers and len(top_performers_series) < max_performers:
                        remaining_stocks = change2.drop(top_performers_series.index).drop(bottom_performers_series.index)
                        if not remaining_stocks.empty:
                            additional_needed = max_performers - len(top_performers_series)
                            additional_top = remaining_stocks.nlargest(additional_needed)
                            top_performers_series = pd.concat([top_performers_series, additional_top])
                            
                    if len(change2) > max_performers and len(bottom_performers_series) < max_performers:
                        remaining_stocks = change2.drop(top_performers_series.index).drop(bottom_performers_series.index)
                        if not remaining_stocks.empty:
                            additional_needed = max_performers - len(bottom_performers_series) 
                            additional_bottom = remaining_stocks.nsmallest(additional_needed)
                            bottom_performers_series = pd.concat([bottom_performers_series, additional_bottom])
                    
                    # Sort by performance value to ensure correct order
                    top_performers_series = top_performers_series.sort_values(ascending=False)
                    bottom_performers_series = bottom_performers_series.sort_values(ascending=True)
                    
                    top_performers = top_performers_series
                    bottom_performers = bottom_performers_series
                
                # Convert pandas Series to dictionary for JSON serialization with percentage values
                # Use OrderedDict to maintain the sorted order
                results[duration] = {
                    "top_performers": {stock: round(float(value) * 100, 2) for stock, value in top_performers.items()},
                    "bottom_performers": {stock: round(float(value) * 100, 2) for stock, value in bottom_performers.items()}
                }
                
            except Exception as e:
                logger.error(f"Error processing {duration} data: {str(e)}")
                # Provide fallback data for this duration
                results[duration] = {
                    "top_performers": {"Error": 0},
                    "bottom_performers": {"Error": 0}
                }
    
    except Exception as e:
        # Handle any overall errors
        error_message = f"Error in momentum analysis: {str(e)}"
        logger.error(error_message)
        
        # Create a basic structure with error messages
        results = {
            "error": error_message,
            "comparison": {
                "dropped_from_top_10": [],
                "entered_top_10": [],
                "full_5d_top_10": [],
                "full_3mo_top_10": []
            }
        }
        
        # Add empty data for each duration
        for duration in durations:
            results[duration] = {
                "top_performers": {"Error": 0},
                "bottom_performers": {"Error": 0}
            }
    
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    results = get_momentum_data()
    print(results)