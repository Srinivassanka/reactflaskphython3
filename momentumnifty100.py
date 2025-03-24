import yfinance as yf
import pandas as pd
import numpy as np
import time
import logging

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
    for attempt in range(max_retries):
        try:
            logger.debug(f"Downloading data for {len(symbol_list)} symbols, period={period}, attempt {attempt+1}")
            data = yf.download(
                symbol_list, 
                period=period, 
                interval=interval,
                progress=False,
                group_by='ticker',
                threads=False,  # Disable threading to avoid connection issues
                timeout=30
            )
            
            # For single symbol, the structure is different
            if len(symbol_list) == 1:
                symbol = symbol_list[0]
                data = pd.DataFrame({symbol: data["Adj Close"]})
            else:
                # Extract only the Adj Close column from the multi-level DataFrame
                data = data.xs("Adj Close", axis=1, level=1, drop_level=True)
            
            logger.debug(f"Successfully downloaded data, shape: {data.shape}")
            return data
            
        except Exception as e:
            logger.error(f"Error downloading data (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                logger.debug(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.warning("Max retries reached, returning empty dataframe")
                # Return an empty dataframe with the expected columns
                return pd.DataFrame(columns=symbol_list)

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
        change_5d = data_5d.pct_change().dropna()
        # Calculate total return over period
        change2_5d = (change_5d + 1).prod() - 1
        top_10_5d = set(change2_5d.nlargest(min(10, len(change2_5d))).index)
        
        # Same for 3-month data
        data_3mo = safe_download(symbols, period="3mo", interval="1d")
        if data_3mo.empty:
            # Handle empty data
            raise ValueError("Unable to download 3-month data")
            
        change_3mo = data_3mo.pct_change().dropna()
        change2_3mo = (change_3mo + 1).prod() - 1
        top_10_3mo = set(change2_3mo.nlargest(min(10, len(change2_3mo))).index)
        
        # Compare the sets
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
                    
                # Calculate change percentages
                change = data.pct_change().dropna()
                change2 = (change + 1).prod() - 1
                
                # Get top and bottom performers
                max_performers = min(20, len(change2))  # Ensure we don't exceed array size
                top_performers = change2.nlargest(max_performers)
                bottom_performers = change2.nsmallest(max_performers)
                
                # Convert pandas Series to dictionary for JSON serialization with percentage values
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