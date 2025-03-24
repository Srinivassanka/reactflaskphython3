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
            </div>
        );
    }
    
    if (!data) {
        return (
            <div className="alert alert-warning">
                <h4 className="alert-heading">No Data Available</h4>
                <p>Could not retrieve momentum data. Please try again later.</p>
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
