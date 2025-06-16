# Supply Chain Forecast AI Agent

AI-powered time series forecasting demo using Claude Sonnet 3.5 to modify RNN-based supply chain forecasts through natural language. Track steel, wood, and glass demand with real-time adjustments via chat.

## Demo Instructions

```bash
export ANTHROPIC_API_KEY=your_api_key_here
docker-compose up --build
```

Open browser: `http://localhost:3000`

Example commands:
- "Increase steel by 20% starting next Monday"
- "We're expecting a wood shortage, reduce by 30% for 2 weeks"
- "Double glass orders from the 25th to month end"

## Project Structure

```
supply-chain-forecast/
├── docker-compose.yml
├── .devcontainer/
│   └── devcontainer.json
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── models/
│   │   ├── rnn_model.py
│   │   └── forecast_agent.py
│   └── data_generator.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── index.html
    └── app.jsx
```

## License

MIT License