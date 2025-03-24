import yfinance as yf
import pandas as pd
import numpy as np

# Define symbols from the image
symbols = [
    "ABB.NS", "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    "ADANIPOWER.NS", "ATGL.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS",
    "ASIANPAINT.NS", "DMART.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "BAJAJHLDNG.NS", "BANKBARODA.NS",
    "BERGEPAINT.NS", "BEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BOSCHLTD.NS",
    "BRITANNIA.NS", "CANBK.NS", "CHOLAFIN.NS", "CIPLA.NS", "COALINDIA.NS",
    "COLPAL.NS", "DLF.NS", "DABUR.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GAIL.NS", "GODREJCP.NS", "GRASIM.NS", "HCLTECH.NS",
    "HDFCBANK.NS", "HDFCLIFE.NS", "HAVELLS.NS", "HEROMOTOCO.NS", "HINDALCO.NS",
    "HAL.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS",
    "ITC.NS", "IOC.NS", "IRCTC.NS", "IRFC.NS", "INDUSINDBK.NS", "NAUKRI.NS",
    "INFY.NS", "INDIGO.NS", "JSWSTEEL.NS", "JINDALSTEL.NS", "JIOFIN.NS",
    "KOTAKBANK.NS", "LTIM.NS", "LT.NS", "LICI.NS", "M&M.NS", "MARICO.NS",
    "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS", "PIDILITIND.NS",
    "PFC.NS", "POWERGRID.NS", "PNB.NS", "RECLTD.NS", "RELIANCE.NS",
    "SBICARD.NS", "SBILIFE.NS", "SRF.NS", "MOTHERSON.NS", "SHREECEM.NS",
    "SHRIRAMFIN.NS", "SIEMENS.NS", "SBIN.NS", "SUNPHARMA.NS", "TVSMOTOR.NS",
    "TCS.NS", "TATACONSUM.NS", "TATAMTRDVR.NS", "TATAMOTORS.NS",
    "TATAPOWER.NS", "TATASTEEL.NS", "TECHM.NS", "TITAN.NS", "TORNTPHARM.NS",
    "TRENT.NS", "ULTRACEMCO.NS", "MCDOWELL-N.NS", "VBL.NS", "VEDL.NS",
    "WIPRO.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
]

def get_momentum_data():
    results = {}
    
    durations = ["5d", "10d", "1mo", "3mo", "6mo", "1y"]
    
    # Get 5d and 3mo for comparison
    data_5d = yf.download(symbols, period="5d", interval="1d")["Adj Close"]
    change_5d = data_5d.pct_change()
    change2_5d = (change_5d + 1).prod() - 1
    top_10_5d = set(change2_5d.nlargest(10).index)
    
    data_3mo = yf.download(symbols, period="3mo", interval="1d")["Adj Close"]
    change_3mo = data_3mo.pct_change()
    change2_3mo = (change_3mo + 1).prod() - 1
    top_10_3mo = set(change2_3mo.nlargest(10).index)
    
    # Compare the sets
    dropped_off = list(top_10_5d - top_10_3mo)
    new_entries = list(top_10_3mo - top_10_5d)
    
    results["comparison"] = {
        "dropped_from_top_10": dropped_off,
        "entered_top_10": new_entries,
        "full_5d_top_10": list(top_10_5d),
        "full_3mo_top_10": list(top_10_3mo)
    }
    
    # Get all duration data
    for duration in durations:
        data = yf.download(symbols, period=duration, interval="1d")["Adj Close"]
        change = data.pct_change()
        change2 = (change + 1).prod() - 1
        top_performers = change2.nlargest(30)
        bottom_performers = change2.nsmallest(30)
        
        # Convert pandas Series to dictionary for JSON serialization
        results[duration] = {
            "top_performers": {stock: round(float(value) * 100, 2) for stock, value in top_performers.items()},
            "bottom_performers": {stock: round(float(value) * 100, 2) for stock, value in bottom_performers.items()}
        }
    
    return results

if __name__ == "__main__":
    results = get_momentum_data()
    print(results)