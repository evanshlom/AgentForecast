const { useState, useEffect, useRef } = React;

function App() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [ws, setWs] = useState(null);
    const [connected, setConnected] = useState(false);
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        // Connect to WebSocket
        const websocket = new WebSocket('ws://localhost:8369/ws');
        
        websocket.onopen = () => {
            console.log('WebSocket connected');
            setConnected(true);
        };

        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received:', data);
            
            if (data.message) {
                setMessages(prev => [...prev, {
                    type: 'ai',
                    text: data.message
                }]);
            }
            
            // Update chart
            if (data.historical && data.forecast) {
                updateChart(data.historical, data.forecast);
            }
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            setMessages(prev => [...prev, {
                type: 'ai',
                text: 'Connection error. Please refresh the page.'
            }]);
        };

        websocket.onclose = () => {
            console.log('WebSocket disconnected');
            setConnected(false);
        };

        setWs(websocket);

        return () => {
            websocket.close();
        };
    }, []);

    const updateChart = (historical, forecast) => {
        if (!chartRef.current) return;

        // Destroy existing chart
        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        const ctx = chartRef.current.getContext('2d');
        
        // Prepare data
        const historicalData = historical.slice(-60);
        const allDates = [...historicalData.map(d => d.date), ...forecast.map(d => d.date)];
        const steelData = [...historicalData.map(d => d.steel), ...forecast.map(d => d.steel)];
        const woodData = [...historicalData.map(d => d.wood), ...forecast.map(d => d.wood)];
        const glassData = [...historicalData.map(d => d.glass), ...forecast.map(d => d.glass)];

        // Create chart
        chartInstance.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: allDates,
                datasets: [
                    {
                        label: 'Steel',
                        data: steelData,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        borderDash: (ctx) => ctx.dataIndex >= historicalData.length ? [5, 5] : []
                    },
                    {
                        label: 'Wood',
                        data: woodData,
                        borderColor: '#8b4513',
                        backgroundColor: 'rgba(139, 69, 19, 0.1)',
                        borderDash: (ctx) => ctx.dataIndex >= historicalData.length ? [5, 5] : []
                    },
                    {
                        label: 'Glass',
                        data: glassData,
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderDash: (ctx) => ctx.dataIndex >= historicalData.length ? [5, 5] : []
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Supply Chain Forecast'
                    }
                },
                scales: {
                    x: {
                        ticks: { maxTicksLimit: 10 }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Units'
                        }
                    }
                }
            }
        });
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = () => {
        if (!inputValue.trim() || !ws || !connected) return;

        setMessages(prev => [...prev, {
            type: 'user',
            text: inputValue
        }]);

        ws.send(inputValue);
        setInputValue('');
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    };

    return (
        <div className="container">
            <div className="chat-panel">
                <div className="chat-header">
                    Supply Chain Forecast AI {connected ? '✓' : '✗'}
                </div>
                <div className="chat-messages">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message ${msg.type}-message`}>
                            {msg.text}
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
                <div className="chat-input">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about forecast adjustments..."
                        disabled={!connected}
                    />
                    <button onClick={sendMessage} disabled={!connected}>
                        Send
                    </button>
                </div>
            </div>
            <div className="chart-panel">
                <div className="chart-container">
                    <h2>Material Demand Forecast</h2>
                    <div style={{ height: '400px', position: 'relative' }}>
                        <canvas ref={chartRef}></canvas>
                    </div>
                </div>
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));