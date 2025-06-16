const { useState, useEffect, useRef } = React;

function App() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [ws, setWs] = useState(null);
    const [chartData, setChartData] = useState(null);
    const chartRef = useRef(null);
    const chartInstance = useRef(null);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        // Connect to WebSocket
        const websocket = new WebSocket('ws://localhost:8369/ws');
        
        websocket.onopen = () => {
            console.log('Connected to server');
            setMessages([{
                type: 'ai',
                text: 'Connected! I can help you adjust your supply chain forecast. Try saying things like "Increase steel by 20% next week" or "We expect lower wood demand for 10 days".'
            }]);
        };

        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'forecast' || data.type === 'response') {
                if (data.message) {
                    setMessages(prev => [...prev, {
                        type: 'ai',
                        text: data.message
                    }]);
                }
                
                // Update chart data
                const historical = data.historical;
                const forecast = data.forecast;
                setChartData({ historical, forecast });
            }
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        setWs(websocket);

        return () => {
            websocket.close();
        };
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        if (!chartData || !chartRef.current) return;

        // Destroy existing chart
        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        // Combine historical and forecast data
        const allDates = [
            ...chartData.historical.slice(-60).map(d => d.date),
            ...chartData.forecast.map(d => d.date)
        ];
        
        const historicalLength = chartData.historical.slice(-60).length;

        // Create chart
        const ctx = chartRef.current.getContext('2d');
        chartInstance.current = new Chart(ctx, {
            type: 'line',
            data: {
                labels: allDates,
                datasets: [
                    {
                        label: 'Steel',
                        data: [
                            ...chartData.historical.slice(-60).map(d => d.steel),
                            ...chartData.forecast.map(d => d.steel)
                        ],
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        segment: {
                            borderDash: (ctx) => ctx.p0DataIndex >= historicalLength - 1 ? [5, 5] : undefined
                        }
                    },
                    {
                        label: 'Wood',
                        data: [
                            ...chartData.historical.slice(-60).map(d => d.wood),
                            ...chartData.forecast.map(d => d.wood)
                        ],
                        borderColor: '#8b4513',
                        backgroundColor: 'rgba(139, 69, 19, 0.1)',
                        segment: {
                            borderDash: (ctx) => ctx.p0DataIndex >= historicalLength - 1 ? [5, 5] : undefined
                        }
                    },
                    {
                        label: 'Glass',
                        data: [
                            ...chartData.historical.slice(-60).map(d => d.glass),
                            ...chartData.forecast.map(d => d.glass)
                        ],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        segment: {
                            borderDash: (ctx) => ctx.p0DataIndex >= historicalLength - 1 ? [5, 5] : undefined
                        }
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Supply Chain Forecast (Historical 60 days + Forecast 30 days)',
                        font: { size: 16 }
                    },
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                xMin: historicalLength - 1,
                                xMax: historicalLength - 1,
                                borderColor: 'rgb(75, 75, 75)',
                                borderWidth: 2,
                                borderDash: [10, 5],
                                label: {
                                    display: true,
                                    content: 'Today',
                                    position: 'start'
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        ticks: {
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Units'
                        }
                    }
                }
            }
        });
    }, [chartData]);

    const sendMessage = () => {
        if (!inputValue.trim() || !ws) return;

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
                    Supply Chain Forecast AI
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
                    />
                    <button onClick={sendMessage}>Send</button>
                </div>
            </div>
            <div className="chart-panel">
                <div className="chart-container">
                    <h2>Material Demand Forecast</h2>
                    <div style={{ height: '400px' }}>
                        <canvas ref={chartRef}></canvas>
                    </div>
                </div>
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));