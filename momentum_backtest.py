import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MomentumBacktest:
    def __init__(self, symbols, start_date=None, end_date=None, initial_investment=500000.0, rebalance_period_days=14):
        """
        Initialize the backtest with parameters
        
        Args:
            symbols: List of stock symbols to consider
            start_date: Starting date for backtest (default: 3 months ago)
            end_date: Ending date for backtest (default: today)
            initial_investment: Starting capital in Rs
            rebalance_period_days: Number of days between rebalancing
        """
        self.symbols = symbols
        
        # Set default dates if not provided
        if end_date is None:
            self.end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            self.end_date = end_date
            
        if start_date is None:
            # Default to 3 months before end date
            end_date_obj = datetime.strptime(self.end_date, '%Y-%m-%d')
            start_date_obj = end_date_obj - timedelta(days=90)
            self.start_date = start_date_obj.strftime('%Y-%m-%d')
        else:
            self.start_date = start_date
        
        self.initial_investment = initial_investment
        self.rebalance_period_days = rebalance_period_days
        
        # Initialize results containers
        self.portfolio_values = []
        self.holdings_history = []
        self.rebalance_dates = []
        
        logger.info(f"Initializing backtest from {self.start_date} to {self.end_date}")
    
    def download_data(self):
        """Download historical data for all symbols"""
        logger.info(f"Downloading data for {len(self.symbols)} symbols")
        
        try:
            # Use a buffer period before start_date to calculate initial momentum
            buffer_start = (datetime.strptime(self.start_date, '%Y-%m-%d') - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Download data with buffer
            self.stock_data = yf.download(
                self.symbols,
                start=buffer_start,
                end=self.end_date,
                group_by='ticker',
                interval='1d',
                progress=False,
                threads=False,
                timeout=30
            )
            
            # Restructure the data for easier access
            self.prices = {}
            
            # Handle different return structures based on number of symbols
            if len(self.symbols) == 1:
                symbol = self.symbols[0]
                if 'Adj Close' in self.stock_data.columns:
                    self.prices[symbol] = self.stock_data['Adj Close']
                else:
                    self.prices[symbol] = self.stock_data['Close']
            else:
                for symbol in self.symbols:
                    try:
                        self.prices[symbol] = self.stock_data[(symbol, 'Adj Close')]
                    except KeyError:
                        try:
                            self.prices[symbol] = self.stock_data[(symbol, 'Close')]
                        except KeyError:
                            logger.warning(f"No price data for {symbol}, filling with NaN")
                            # Create a series of NaNs with the same index
                            sample_symbol = next(iter(self.prices))
                            self.prices[symbol] = pd.Series(np.nan, index=self.prices[sample_symbol].index)
            
            # Convert to DataFrame
            self.price_df = pd.DataFrame(self.prices)
            logger.info(f"Downloaded data shape: {self.price_df.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading data: {str(e)}")
            return False
    
    def calculate_momentum(self, current_date, lookback_days=20):
        """
        Calculate momentum for all stocks as of a specific date
        
        Args:
            current_date: The date to calculate momentum for
            lookback_days: Number of days to look back for momentum calculation
        
        Returns:
            Series of momentum values sorted from highest to lowest
        """
        try:
            # Get data up to current date
            mask = self.price_df.index <= current_date
            data_subset = self.price_df.loc[mask].copy()
            
            if len(data_subset) <= 1:
                logger.warning(f"Not enough data points for {current_date}")
                return pd.Series()
                
            # Calculate returns over the lookback period
            latest_prices = data_subset.iloc[-1]
            
            # Find the price lookback_days ago (or closest available)
            if len(data_subset) >= lookback_days:
                past_prices = data_subset.iloc[-lookback_days]
            else:
                past_prices = data_subset.iloc[0]
            
            # Calculate percentage change
            momentum = (latest_prices - past_prices) / past_prices
            
            # Sort by momentum (highest first)
            momentum = momentum.sort_values(ascending=False)
            
            # Remove NaNs
            momentum = momentum.dropna()
            
            return momentum
        
        except Exception as e:
            logger.error(f"Error calculating momentum for {current_date}: {str(e)}")
            return pd.Series()
    
    def run_backtest(self):
        """Run the backtest simulation"""
        logger.info("Starting backtest simulation")
        
        # Download the historical data
        if not self.download_data():
            logger.error("Failed to download data, cannot continue backtest")
            return False
        
        # Initialize portfolio
        portfolio_value = self.initial_investment
        cash = portfolio_value  # Start with all cash
        holdings = {}  # No initial holdings
        
        # Generate rebalance dates
        current_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
        
        # Ensure we only use market dates that exist in our data
        market_dates = self.price_df.index
        
        # Track results
        self.portfolio_values = []
        self.holdings_history = []
        self.rebalance_dates = []
        
        # Run simulation
        while current_date <= end_date:
            current_date_str = current_date.strftime('%Y-%m-%d')
            
            # Find the next closest market date
            next_market_date = self._find_closest_market_date(current_date_str, market_dates)
            
            if next_market_date is None:
                # No more market dates
                break
            
            logger.info(f"Rebalancing on {next_market_date}")
            self.rebalance_dates.append(next_market_date)
            
            # Get top momentum stocks
            momentum = self.calculate_momentum(next_market_date)
            
            if len(momentum) == 0:
                logger.warning(f"No momentum data for {next_market_date}, skipping")
                current_date += timedelta(days=self.rebalance_period_days)
                continue
            
            # Take top 10 or fewer if not enough stocks
            top_stocks = momentum.head(min(10, len(momentum)))
            
            # Calculate current portfolio value before rebalancing
            current_value = self._calculate_portfolio_value(holdings, next_market_date, cash)
            logger.info(f"Portfolio value before rebalancing: Rs {current_value:.2f}")
            
            # Sell all current holdings
            cash = current_value
            holdings = {}
            
            # Allocate equally to top momentum stocks
            amount_per_stock = cash / len(top_stocks)
            
            # Buy new portfolio
            for symbol in top_stocks.index:
                price = self._get_price(symbol, next_market_date)
                if not np.isnan(price) and price > 0:
                    shares = amount_per_stock / price
                    holdings[symbol] = shares
                    cash -= shares * price
                    logger.debug(f"Bought {shares:.2f} shares of {symbol} at Rs {price:.2f}")
            
            # Record holdings after rebalancing
            self.holdings_history.append({
                'date': next_market_date,
                'holdings': holdings.copy(),
                'cash': cash
            })
            
            # Record portfolio value after rebalancing
            portfolio_value = self._calculate_portfolio_value(holdings, next_market_date, cash)
            self.portfolio_values.append({
                'date': next_market_date,
                'value': portfolio_value
            })
            
            logger.info(f"Portfolio value after rebalancing: Rs {portfolio_value:.2f}")
            
            # Move to next rebalance date
            current_date += timedelta(days=self.rebalance_period_days)
        
        # Calculate final portfolio value using the most recent market date
        # and the final holdings
        final_market_date = None
        if self.portfolio_values:
            final_market_date = self.portfolio_values[-1]['date']
            final_value = self.portfolio_values[-1]['value']
        else:
            final_value = self.initial_investment
            
        # Calculate overall return
        total_return_pct = (final_value - self.initial_investment) / self.initial_investment * 100
        
        # Calculate holding period in days
        days_held = (datetime.strptime(self.end_date, '%Y-%m-%d') - 
                    datetime.strptime(self.start_date, '%Y-%m-%d')).days
        
        # Calculate annualized return (handle edge cases)
        if days_held > 0 and self.initial_investment > 0 and final_value > 0:
            annualized_return = (((final_value / self.initial_investment) ** (365 / days_held)) - 1) * 100
        else:
            annualized_return = 0
        
        result = {
            'initial_investment': float(self.initial_investment),
            'final_value': float(final_value),
            'total_return_rs': float(final_value - self.initial_investment),
            'total_return_pct': float(total_return_pct),
            'annualized_return_pct': float(annualized_return),
            'days_held': days_held,
            'number_of_rebalances': len(self.rebalance_dates)
        }
        
        logger.info(f"Backtest completed: {result}")
        return result
    
    def _find_closest_market_date(self, date_str, market_dates):
        """Find the closest market date on or after the given date"""
        date_obj = pd.Timestamp(date_str)
        
        # Find dates on or after the given date
        future_dates = market_dates[market_dates >= date_obj]
        
        if len(future_dates) == 0:
            return None
        
        return future_dates[0]
    
    def _get_price(self, symbol, date):
        """Get the price of a symbol on a specific date"""
        try:
            return self.price_df.loc[date, symbol]
        except (KeyError, ValueError):
            logger.warning(f"Price not found for {symbol} on {date}")
            return np.nan
    
    def _calculate_portfolio_value(self, holdings, date, cash):
        """Calculate the total portfolio value on a specific date"""
        value = cash
        
        for symbol, shares in holdings.items():
            price = self._get_price(symbol, date)
            if not np.isnan(price):
                value += shares * price
        
        return value
    
    def get_performance_summary(self):
        """Generate a summary of the backtest performance"""
        if not self.portfolio_values:
            return "Backtest has not been run yet."
        
        # Extract values and dates
        dates = [entry['date'] for entry in self.portfolio_values]
        values = [entry['value'] for entry in self.portfolio_values]
        
        # Ensure we have values to work with
        if not values:
            return {
                'Initial Investment': f"Rs {self.initial_investment:,.2f}",
                'Final Value': "Rs 0.00",
                'Absolute Return': f"Rs {-self.initial_investment:,.2f}",
                'Return (%)': "-100.00%",
                'Max Drawdown (%)': "100.00%",
                'Rebalancing Frequency': f"Every {self.rebalance_period_days} days",
                'Number of Rebalances': 0
            }
        
        df = pd.DataFrame({
            'Date': dates,
            'Portfolio Value': values
        })
        
        # Calculate daily returns
        df['Daily Return'] = df['Portfolio Value'].pct_change()
        
        # Calculate metrics - use the last available value
        final_value = values[-1]
        total_return = (final_value - self.initial_investment) / self.initial_investment
        
        # Find max drawdown
        df['Cumulative Return'] = (1 + df['Daily Return']).cumprod() - 1
        df['Running Max'] = df['Cumulative Return'].cummax()
        df['Drawdown'] = df['Running Max'] - df['Cumulative Return']
        max_drawdown = df['Drawdown'].max()
        
        # Summary stats
        summary = {
            'Initial Investment': f"Rs {self.initial_investment:,.2f}",
            'Final Value': f"Rs {final_value:,.2f}",
            'Absolute Return': f"Rs {final_value - self.initial_investment:,.2f}",
            'Return (%)': f"{total_return * 100:.2f}%",
            'Max Drawdown (%)': f"{max_drawdown * 100:.2f}%",
            'Rebalancing Frequency': f"Every {self.rebalance_period_days} days",
            'Number of Rebalances': len(self.rebalance_dates)
        }
        
        return summary

def run_momentum_backtest(
    symbols, 
    start_date=None, 
    end_date=None, 
    initial_investment=500000.0, 
    rebalance_period_days=14
):
    """
    Run a momentum backtest with the given parameters
    
    Args:
        symbols: List of stock symbols
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        initial_investment: Initial investment amount in Rs
        rebalance_period_days: Number of days between rebalances
    
    Returns:
        Dictionary with backtest results
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and run backtest
    backtest = MomentumBacktest(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_investment=initial_investment,
        rebalance_period_days=rebalance_period_days
    )
    
    result = backtest.run_backtest()
    summary = backtest.get_performance_summary()
    
    # Format the holdings history with readable details
    formatted_holdings_history = []
    for entry in backtest.holdings_history:
        date = entry['date']
        holdings = entry['holdings']
        cash = entry['cash']
        
        # Format detailed holdings with share count and value
        stock_details = []
        for symbol, shares in holdings.items():
            price = backtest._get_price(symbol, date)
            value = shares * price
            stock_details.append({
                'symbol': symbol,
                'shares': float(shares),
                'price': float(price),
                'value': float(value),
                'percentage': float(value / (backtest._calculate_portfolio_value(holdings, date, cash)) * 100)
            })
        
        # Sort by value (highest first)
        stock_details.sort(key=lambda x: x['value'], reverse=True)
        
        formatted_holdings_history.append({
            'date': date,
            'holdings': stock_details,
            'cash': float(cash)
        })
    
    return {
        'result': result,
        'summary': summary,
        'portfolio_values': backtest.portfolio_values,
        'rebalance_dates': backtest.rebalance_dates,
        'holdings_history': formatted_holdings_history
    }

if __name__ == "__main__":
    # If run directly, perform a test backtest
    from momentumnifty100 import symbols
    
    logging.basicConfig(level=logging.INFO)
    
    # Calculate 3 months ago
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date_obj = datetime.now() - timedelta(days=90)
    start_date = start_date_obj.strftime('%Y-%m-%d')
    
    print(f"Running backtest from {start_date} to {end_date}")
    
    results = run_momentum_backtest(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        initial_investment=500000,
        rebalance_period_days=14
    )
    
    print("\nBacktest Results:")
    print(f"Initial Investment: Rs {results['result']['initial_investment']:,.2f}")
    print(f"Final Value: Rs {results['result']['final_value']:,.2f}")
    print(f"Total Return: Rs {results['result']['total_return_rs']:,.2f} ({results['result']['total_return_pct']:.2f}%)")
    print(f"Annualized Return: {results['result']['annualized_return_pct']:.2f}%")
    print(f"Number of Rebalances: {results['result']['number_of_rebalances']}")