// React Components for Momentum Analysis

// Helper function to format currency values
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2
    }).format(value);
}

// Helper function to show errors (outside React)
function showError(message) {
    const errorCard = document.getElementById('errorCard');
    const errorText = document.getElementById('errorText');
    
    errorText.textContent = message;
    errorCard.classList.remove('d-none');
    errorCard.scrollIntoView({ behavior: 'smooth' });
}

// Helper function to format percentage values
function formatPercentage(value) {
    if (typeof value === 'number') {
        return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
    }
    return value;
}

// Stock List Component
function StockList({ title, stocks, type }) {
    const getStockColor = (value, type) => {
        if (type === 'top') {
            return value > 0 ? 'text-success' : 'text-danger';
        } else {
            return value < 0 ? 'text-danger' : 'text-success';
        }
    };

    // Check if stocks is empty or doesn't exist
    if (!stocks || Object.keys(stocks).length === 0) {
        return (
            <div className="card mb-4">
                <div className="card-header">
                    <h5>{title}</h5>
                </div>
                <div className="card-body">
                    <div className="alert alert-warning mb-0">
                        <p className="mb-0">No data available for this time period</p>
                    </div>
                </div>
            </div>
        );
    }
    
    // Check if we have error or info indicators ("Error" or "Info" keys)
    if (stocks.hasOwnProperty("Error") || stocks.hasOwnProperty("Info")) {
        return (
            <div className="card mb-4">
                <div className="card-header">
                    <h5>{title}</h5>
                </div>
                <div className="card-body">
                    <div className="alert alert-warning mb-0">
                        <p className="mb-0">
                            <i className="fas fa-exclamation-triangle me-2"></i>
                            Unable to retrieve stock data for this time period
                        </p>
                        <p className="small mb-0 mt-2">
                            The Yahoo Finance API may be experiencing issues or rate limiting.
                            Please try again later or select a different time period.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="card mb-4">
            <div className="card-header">
                <h5>{title}</h5>
            </div>
            <div className="card-body p-0">
                <div className="table-responsive">
                    <table className="table table-hover mb-0">
                        <thead>
                            <tr>
                                <th>Stock</th>
                                <th>Return</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(stocks)
                                .sort((a, b) => {
                                    // For top performers, sort descending (highest first)
                                    if (type === 'top') {
                                        return b[1] - a[1]; // b[1] is the value (percentage)
                                    } 
                                    // For bottom performers, sort ascending (lowest first)
                                    else {
                                        return a[1] - b[1];
                                    }
                                })
                                .map(([stock, value]) => (
                                    <tr key={stock}>
                                        <td>{stock}</td>
                                        <td className={getStockColor(value, type)}>
                                            {formatPercentage(value)}
                                        </td>
                                    </tr>
                                ))
                            }
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

// Comparison Component
function ComparisonAnalysis({ comparison }) {
    if (!comparison) return null;
    
    // Check if comparison data is empty (all empty arrays)
    const isEmpty = 
        comparison.dropped_from_top_10.length === 0 && 
        comparison.entered_top_10.length === 0 &&
        comparison.full_5d_top_10.length === 0 && 
        comparison.full_3mo_top_10.length === 0;
    
    if (isEmpty) {
        return (
            <div className="card mb-4">
                <div className="card-header">
                    <h4>Momentum Comparison (5d vs 3mo)</h4>
                </div>
                <div className="card-body">
                    <div className="alert alert-warning mb-0">
                        <p className="mb-0">
                            <i className="fas fa-exclamation-triangle me-2"></i>
                            Unable to retrieve comparison data
                        </p>
                        <p className="small mb-0 mt-2">
                            The Yahoo Finance API may be experiencing issues. 
                            Data for the comparison period could not be loaded.
                        </p>
                    </div>
                </div>
            </div>
        );
    }
    
    return (
        <div className="card mb-4">
            <div className="card-header">
                <h4>Momentum Comparison (5d vs 3mo)</h4>
            </div>
            <div className="card-body">
                <div className="row">
                    <div className="col-md-6">
                        <h5>Dropped from top 10:</h5>
                        <ul className="list-group">
                            {comparison.dropped_from_top_10.length > 0 ? (
                                comparison.dropped_from_top_10.map((stock, index) => (
                                    <li key={index} className="list-group-item">
                                        <i className="fas fa-arrow-down text-danger me-2"></i>
                                        {stock}
                                    </li>
                                ))
                            ) : (
                                <li className="list-group-item">None</li>
                            )}
                        </ul>
                    </div>
                    <div className="col-md-6">
                        <h5>Entered top 10:</h5>
                        <ul className="list-group">
                            {comparison.entered_top_10.length > 0 ? (
                                comparison.entered_top_10.map((stock, index) => (
                                    <li key={index} className="list-group-item">
                                        <i className="fas fa-arrow-up text-success me-2"></i>
                                        {stock}
                                    </li>
                                ))
                            ) : (
                                <li className="list-group-item">None</li>
                            )}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Duration Tab Component
function DurationTab({ duration, data, activeTab, setActiveTab }) {
    if (!data) return null;
    
    const isActive = activeTab === duration;
    
    return (
        <li className="nav-item" role="presentation">
            <button 
                className={`nav-link ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(duration)}
                type="button" 
                role="tab" 
                aria-selected={isActive ? 'true' : 'false'}
            >
                {duration}
            </button>
        </li>
    );
}

// Duration Content Component
function DurationContent({ duration, data, isActive }) {
    if (!data || !isActive) return null;
    
    return (
        <div className={`tab-pane fade ${isActive ? 'show active' : ''}`}>
            <div className="row">
                <div className="col-md-6">
                    <StockList 
                        title={`Top Performers (${duration})`} 
                        stocks={data.top_performers} 
                        type="top"
                    />
                </div>
                <div className="col-md-6">
                    <StockList 
                        title={`Bottom Performers (${duration})`} 
                        stocks={data.bottom_performers} 
                        type="bottom"
                    />
                </div>
            </div>
        </div>
    );
}

// Backtest Form Component
function BacktestForm({ onRunBacktest, loading }) {
    const [initialInvestment, setInitialInvestment] = React.useState(500000);
    const [startDate, setStartDate] = React.useState('');
    const [endDate, setEndDate] = React.useState('');
    const [rebalancePeriod, setRebalancePeriod] = React.useState(14);

    // Calculate default dates (3 months ago to today)
    React.useEffect(() => {
        const today = new Date();
        const threeMonthsAgo = new Date();
        threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
        
        setEndDate(today.toISOString().split('T')[0]);
        setStartDate(threeMonthsAgo.toISOString().split('T')[0]);
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        
        onRunBacktest({
            initialInvestment,
            startDate,
            endDate,
            rebalancePeriod
        });
    };

    return (
        <div className="card mb-4">
            <div className="card-header bg-primary text-white">
                <h4 className="mb-0">Momentum Backtest Simulation</h4>
            </div>
            <div className="card-body">
                <p className="mb-3">
                    Simulate returns from investing in the top 10 momentum stocks with regular rebalancing.
                </p>
                <form onSubmit={handleSubmit}>
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <div className="form-group mb-3">
                                <label htmlFor="initialInvestment" className="form-label">Initial Investment (₹)</label>
                                <input
                                    type="number"
                                    className="form-control"
                                    id="initialInvestment"
                                    value={initialInvestment}
                                    onChange={(e) => setInitialInvestment(Number(e.target.value))}
                                    min="10000"
                                    max="10000000"
                                    step="10000"
                                    required
                                />
                                <small className="form-text text-muted">Amount will be divided equally among top 10 stocks</small>
                            </div>
                        </div>
                        <div className="col-md-6">
                            <div className="form-group mb-3">
                                <label htmlFor="rebalancePeriod" className="form-label">Rebalance Period (days)</label>
                                <select
                                    className="form-select"
                                    id="rebalancePeriod"
                                    value={rebalancePeriod}
                                    onChange={(e) => setRebalancePeriod(Number(e.target.value))}
                                    required
                                >
                                    <option value="7">Weekly (7 days)</option>
                                    <option value="14">Bi-weekly (14 days)</option>
                                    <option value="30">Monthly (30 days)</option>
                                </select>
                                <small className="form-text text-muted">How often to rebalance the portfolio</small>
                            </div>
                        </div>
                    </div>
                    <div className="row mb-3">
                        <div className="col-md-6">
                            <div className="form-group">
                                <label htmlFor="startDate" className="form-label">Start Date</label>
                                <input
                                    type="date"
                                    className="form-control"
                                    id="startDate"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    required
                                />
                            </div>
                        </div>
                        <div className="col-md-6">
                            <div className="form-group">
                                <label htmlFor="endDate" className="form-label">End Date</label>
                                <input
                                    type="date"
                                    className="form-control"
                                    id="endDate"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    required
                                />
                            </div>
                        </div>
                    </div>
                    <div className="d-grid">
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                    Running Simulation...
                                </>
                            ) : (
                                <>
                                    <i className="fas fa-chart-line me-2"></i>
                                    Run Backtest Simulation
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

// Backtest Results Component
function BacktestResults({ results, onClear }) {
    if (!results) return null;
    
    const { result, summary, portfolio_values, rebalance_dates } = results;
    
    // Format dates to be more readable
    const formatDate = (dateStr) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };
    
    // Extract holdings history if available
    const holdingsHistory = results.holdings_history || [];
    
    // State for displaying specific rebalance period
    const [activeRebalanceIndex, setActiveRebalanceIndex] = React.useState(0);
    
    return (
        <div className="card mb-4">
            <div className="card-header bg-success text-white">
                <h4 className="mb-0">Backtest Results</h4>
            </div>
            <div className="card-body">
                <div className="row mb-4">
                    <div className="col-md-6">
                        <div className="card">
                            <div className="card-header">
                                <h5 className="mb-0">Summary</h5>
                            </div>
                            <div className="card-body">
                                <table className="table table-striped">
                                    <tbody>
                                        {Object.entries(summary).map(([key, value]) => (
                                            <tr key={key}>
                                                <th>{key}</th>
                                                <td>{value}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-6">
                        <div className="card h-100">
                            <div className="card-header">
                                <h5 className="mb-0">Performance Details</h5>
                            </div>
                            <div className="card-body">
                                <div className="mb-3">
                                    <h6>Initial Investment</h6>
                                    <p className="lead">{result.initial_investment_formatted}</p>
                                </div>
                                <div className="mb-3">
                                    <h6>Final Value</h6>
                                    <p className={`lead ${result.total_return_pct >= 0 ? 'text-success' : 'text-danger'}`}>
                                        {result.final_value_formatted}
                                    </p>
                                </div>
                                <div className="mb-3">
                                    <h6>Total Return</h6>
                                    <p className={`lead ${result.total_return_pct >= 0 ? 'text-success' : 'text-danger'}`}>
                                        {result.total_return_rs_formatted} ({result.total_return_pct_formatted})
                                    </p>
                                </div>
                                <div>
                                    <h6>Annualized Return</h6>
                                    <p className={`lead ${result.annualized_return_pct >= 0 ? 'text-success' : 'text-danger'}`}>
                                        {result.annualized_return_pct_formatted}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* Portfolio Holdings By Rebalance Period Section */}
                {holdingsHistory.length > 0 && (
                    <div className="mb-4">
                        <h5>Portfolio Holdings By Rebalance Period</h5>
                        <p className="text-muted">
                            See how the top 10 momentum stocks change with each rebalance period.
                        </p>
                        
                        <div className="mb-3">
                            <div className="btn-group w-100">
                                {holdingsHistory.map((period, index) => (
                                    <button
                                        key={index}
                                        className={`btn ${activeRebalanceIndex === index ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => setActiveRebalanceIndex(index)}
                                    >
                                        {index === 0 ? 'Initial' : index + 1}
                                    </button>
                                ))}
                            </div>
                        </div>
                        
                        {holdingsHistory[activeRebalanceIndex] && (
                            <div className="card">
                                <div className="card-header">
                                    <h6 className="mb-0">
                                        Holdings on {formatDate(holdingsHistory[activeRebalanceIndex].date)}
                                    </h6>
                                </div>
                                <div className="card-body p-0">
                                    <div className="table-responsive">
                                        <table className="table table-striped table-hover mb-0">
                                            <thead>
                                                <tr>
                                                    <th>Stock</th>
                                                    <th>Shares</th>
                                                    <th>Price (₹)</th>
                                                    <th>Value (₹)</th>
                                                    <th>% of Portfolio</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {holdingsHistory[activeRebalanceIndex].holdings.map((stock, idx) => (
                                                    <tr key={idx}>
                                                        <td>
                                                            <strong>{stock.symbol.replace('.NS', '')}</strong>
                                                        </td>
                                                        <td>{stock.shares.toFixed(2)}</td>
                                                        <td>{formatCurrency(stock.price)}</td>
                                                        <td>{formatCurrency(stock.value)}</td>
                                                        <td>{stock.percentage.toFixed(2)}%</td>
                                                    </tr>
                                                ))}
                                                {holdingsHistory[activeRebalanceIndex].cash > 0 && (
                                                    <tr>
                                                        <td><strong>Cash</strong></td>
                                                        <td>-</td>
                                                        <td>-</td>
                                                        <td>{formatCurrency(holdingsHistory[activeRebalanceIndex].cash)}</td>
                                                        <td>
                                                            {(holdingsHistory[activeRebalanceIndex].cash / 
                                                                (holdingsHistory[activeRebalanceIndex].holdings.reduce((sum, stock) => sum + stock.value, 0) + 
                                                                holdingsHistory[activeRebalanceIndex].cash) * 100).toFixed(2)}%
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
                
                {/* Portfolio Value History Table */}
                <div className="mb-4">
                    <h5>Portfolio Value History</h5>
                    <div className="table-responsive">
                        <table className="table table-striped table-sm">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Portfolio Value</th>
                                    <th>Change</th>
                                </tr>
                            </thead>
                            <tbody>
                                {portfolio_values.map((entry, index) => {
                                    const prevValue = index > 0 ? portfolio_values[index - 1].value : result.initial_investment;
                                    const change = (entry.value - prevValue) / prevValue * 100;
                                    
                                    return (
                                        <tr key={index}>
                                            <td>{formatDate(entry.date)}</td>
                                            <td>{formatCurrency(entry.value)}</td>
                                            <td className={change >= 0 ? 'text-success' : 'text-danger'}>
                                                {formatPercentage(change)}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                {/* Holdings Comparison (First vs Last Period) */}
                {holdingsHistory.length >= 2 && (
                    <div className="mb-4">
                        <h5>Composition Change: Initial vs Final</h5>
                        <div className="row">
                            <div className="col-md-6">
                                <div className="card">
                                    <div className="card-header bg-primary text-white">
                                        <h6 className="mb-0">Initial Portfolio ({formatDate(holdingsHistory[0].date)})</h6>
                                    </div>
                                    <div className="card-body p-0">
                                        <div className="table-responsive">
                                            <table className="table table-striped table-sm mb-0">
                                                <thead>
                                                    <tr>
                                                        <th>Stock</th>
                                                        <th>% of Portfolio</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {holdingsHistory[0].holdings.map((stock, idx) => (
                                                        <tr key={idx}>
                                                            <td><strong>{stock.symbol.replace('.NS', '')}</strong></td>
                                                            <td>{stock.percentage.toFixed(2)}%</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-md-6">
                                <div className="card">
                                    <div className="card-header bg-success text-white">
                                        <h6 className="mb-0">Final Portfolio ({formatDate(holdingsHistory[holdingsHistory.length - 1].date)})</h6>
                                    </div>
                                    <div className="card-body p-0">
                                        <div className="table-responsive">
                                            <table className="table table-striped table-sm mb-0">
                                                <thead>
                                                    <tr>
                                                        <th>Stock</th>
                                                        <th>% of Portfolio</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {holdingsHistory[holdingsHistory.length - 1].holdings.map((stock, idx) => (
                                                        <tr key={idx}>
                                                            <td><strong>{stock.symbol.replace('.NS', '')}</strong></td>
                                                            <td>{stock.percentage.toFixed(2)}%</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                
                <div className="d-grid">
                    <button
                        onClick={onClear}
                        className="btn btn-outline-primary"
                    >
                        <i className="fas fa-redo me-2"></i>
                        Run Another Simulation
                    </button>
                </div>
            </div>
        </div>
    );
}

// Main App Component
function App() {
    const [data, setData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [activeTab, setActiveTab] = React.useState('5d');
    const [error, setError] = React.useState(null);
    const [backtestResults, setBacktestResults] = React.useState(null);
    const [backtestLoading, setBacktestLoading] = React.useState(false);
    const [activeSection, setActiveSection] = React.useState('analysis'); // 'analysis' or 'backtest'
    
    const durations = ["5d", "10d", "1mo", "3mo", "6mo", "1y"];
    
    React.useEffect(() => {
        // Check if API is available
        fetch('/api/health')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('API Health Check:', data);
                // Try to fetch real data first, but use test data as fallback
                try {
                    return fetch('/api/momentum-analysis')
                      .then(response => {
                          if (!response.ok) {
                              console.warn('Momentum analysis API failed, falling back to test data');
                              return fetch('/api/test-data');
                          }
                          return response;
                      })
                      .catch(error => {
                          console.warn('Momentum analysis API error, falling back to test data:', error);
                          return fetch('/api/test-data');
                      });
                } catch (error) {
                    console.warn('Error fetching momentum data, using test data:', error);
                    return fetch('/api/test-data');
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);
                setData(data);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error:', error);
                setError(error.message || 'An error occurred while fetching data.');
                setLoading(false);
                showError(error.message || 'An error occurred while fetching data.');
            });
    }, []);
    
    if (loading) {
        return (
            <div className="d-flex justify-content-center my-5">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
                <span className="ms-3">Loading Nifty 100 momentum data... This may take a moment</span>
            </div>
        );
    }
    
    if (error) {
        return (
            <div className="alert alert-danger">
                <h4 className="alert-heading">Error!</h4>
                <p>{error}</p>
                <div className="mt-3">
                    <button 
                        className="btn btn-primary"
                        onClick={() => {
                            setError(null);
                            setLoading(true);
                            fetch('/api/momentum-analysis')
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                                    }
                                    return response.json();
                                })
                                .then(data => {
                                    setData(data);
                                    setLoading(false);
                                })
                                .catch(error => {
                                    console.error('Error:', error);
                                    setError(error.message || 'An error occurred while fetching data.');
                                    setLoading(false);
                                });
                        }}
                    >
                        <i className="fas fa-sync-alt me-2"></i> Retry
                    </button>
                </div>
            </div>
        );
    }
    
    if (!data) {
        return (
            <div className="alert alert-warning">
                <h4 className="alert-heading">No Data Available</h4>
                <p>Could not retrieve momentum data. Please try again later.</p>
                <div className="mt-3">
                    <button 
                        className="btn btn-primary"
                        onClick={() => {
                            setLoading(true);
                            fetch('/api/momentum-analysis')
                                .then(response => {
                                    if (!response.ok) {
                                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                                    }
                                    return response.json();
                                })
                                .then(data => {
                                    setData(data);
                                    setLoading(false);
                                })
                                .catch(error => {
                                    console.error('Error:', error);
                                    setError(error.message || 'An error occurred while fetching data.');
                                    setLoading(false);
                                });
                        }}
                    >
                        <i className="fas fa-sync-alt me-2"></i> Retry
                    </button>
                </div>
            </div>
        );
    }
    
    // Handle case where there's an error message in the data
    if (data.error) {
        // Create fallback data for display to ensure we always show something
        const fallbackData = {
            "error": data.error || "Unknown error occurred",
            "comparison": data.comparison || {
                "dropped_from_top_10": [],
                "entered_top_10": [],
                "full_5d_top_10": [],
                "full_3mo_top_10": []
            }
        };
        
        // Ensure all duration data exists
        durations.forEach(duration => {
            if (!data[duration]) {
                data[duration] = {
                    "top_performers": {"Error": 0},
                    "bottom_performers": {"Error": 0}
                };
            }
        });
        
        return (
            <div>
                <div className="alert alert-warning mb-4">
                    <h4 className="alert-heading">Data Load Issue</h4>
                    <p>{data.error}</p>
                    <p>The Yahoo Finance API seems to be experiencing issues. Showing fallback data or partial results.</p>
                    <div className="mt-3">
                        <button 
                            className="btn btn-primary"
                            onClick={() => {
                                setLoading(true);
                                fetch('/api/momentum-analysis')
                                    .then(response => {
                                        if (!response.ok) {
                                            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                                        }
                                        return response.json();
                                    })
                                    .then(data => {
                                        setData(data);
                                        setLoading(false);
                                    })
                                    .catch(error => {
                                        console.error('Error:', error);
                                        setError(error.message || 'An error occurred while fetching data.');
                                        setLoading(false);
                                    });
                            }}
                        >
                            <i className="fas fa-sync-alt me-2"></i> Retry
                        </button>
                    </div>
                </div>
                
                <div className="alert alert-info mb-4">
                    <h4 className="alert-heading"><i className="fas fa-info-circle"></i> About This Tool</h4>
                    <p>This analysis tool shows momentum for Nifty 100 stocks across different time periods. It helps identify which stocks are trending up or down based on price movements.</p>
                </div>
                
                <ComparisonAnalysis comparison={data.comparison} />
                
                <div className="card mb-4">
                    <div className="card-header">
                        <h4><i className="fas fa-chart-line"></i> Momentum Analysis</h4>
                    </div>
                    <div className="card-body">
                        <ul className="nav nav-tabs" role="tablist">
                            {durations.map(duration => (
                                <DurationTab 
                                    key={duration} 
                                    duration={duration} 
                                    data={data[duration]} 
                                    activeTab={activeTab} 
                                    setActiveTab={setActiveTab} 
                                />
                            ))}
                        </ul>
                        
                        <div className="tab-content mt-3">
                            {durations.map(duration => (
                                <DurationContent 
                                    key={duration} 
                                    duration={duration} 
                                    data={data[duration]} 
                                    isActive={activeTab === duration} 
                                />
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    }
    
    // Function to handle running backtest
    const handleRunBacktest = (params) => {
        setBacktestLoading(true);
        
        // Construct query string for API call
        const queryParams = new URLSearchParams({
            initial_investment: params.initialInvestment,
            start_date: params.startDate,
            end_date: params.endDate,
            rebalance_period_days: params.rebalancePeriod
        });
        
        fetch(`/api/momentum-backtest?${queryParams.toString()}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(results => {
                console.log('Backtest results:', results);
                setBacktestResults(results);
                setBacktestLoading(false);
            })
            .catch(error => {
                console.error('Error running backtest:', error);
                setError(`Error running backtest: ${error.message}`);
                setBacktestLoading(false);
                showError(`Error running backtest: ${error.message}`);
            });
    };
    
    return (
        <div>
            <div className="alert alert-info mb-4">
                <h4 className="alert-heading"><i className="fas fa-info-circle"></i> About This Tool</h4>
                <p>This analysis tool shows momentum for Nifty 100 stocks across different time periods. It helps identify which stocks are trending up or down based on price movements.</p>
            </div>
            
            {/* Navigation tabs for switching between Analysis and Backtest */}
            <ul className="nav nav-pills mb-4">
                <li className="nav-item">
                    <button 
                        className={`nav-link ${activeSection === 'analysis' ? 'active' : ''}`}
                        onClick={() => setActiveSection('analysis')}
                    >
                        <i className="fas fa-chart-line me-2"></i>
                        Momentum Analysis
                    </button>
                </li>
                <li className="nav-item">
                    <button 
                        className={`nav-link ${activeSection === 'backtest' ? 'active' : ''}`}
                        onClick={() => setActiveSection('backtest')}
                    >
                        <i className="fas fa-calculator me-2"></i>
                        Backtest Simulation
                    </button>
                </li>
            </ul>
            
            {/* Analysis Section */}
            {activeSection === 'analysis' && (
                <>
                    <ComparisonAnalysis comparison={data.comparison} />
                    
                    <div className="card mb-4">
                        <div className="card-header">
                            <h4><i className="fas fa-chart-line"></i> Momentum Analysis</h4>
                        </div>
                        <div className="card-body">
                            <ul className="nav nav-tabs" role="tablist">
                                {durations.map(duration => (
                                    <DurationTab 
                                        key={duration} 
                                        duration={duration} 
                                        data={data[duration]} 
                                        activeTab={activeTab} 
                                        setActiveTab={setActiveTab} 
                                    />
                                ))}
                            </ul>
                            
                            <div className="tab-content mt-3">
                                {durations.map(duration => (
                                    <DurationContent 
                                        key={duration} 
                                        duration={duration} 
                                        data={data[duration]} 
                                        isActive={activeTab === duration} 
                                    />
                                ))}
                            </div>
                        </div>
                    </div>
                </>
            )}
            
            {/* Backtest Section */}
            {activeSection === 'backtest' && (
                <>
                    {backtestResults ? (
                        <BacktestResults 
                            results={backtestResults} 
                            onClear={() => setBacktestResults(null)}
                        />
                    ) : (
                        <BacktestForm 
                            onRunBacktest={handleRunBacktest}
                            loading={backtestLoading}
                        />
                    )}
                </>
            )}
        </div>
    );
}

// Render the React App
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
