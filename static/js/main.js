// React Components for Momentum Analysis

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
                            {Object.entries(stocks).map(([stock, value]) => (
                                <tr key={stock}>
                                    <td>{stock}</td>
                                    <td className={getStockColor(value, type)}>
                                        {formatPercentage(value)}
                                    </td>
                                </tr>
                            ))}
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

// Main App Component
function App() {
    const [data, setData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [activeTab, setActiveTab] = React.useState('5d');
    const [error, setError] = React.useState(null);
    
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
                // API is available, now fetch momentum data
                return fetch('/api/momentum-analysis');
            })
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
    
    return (
        <div>
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

// Render the React App
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
