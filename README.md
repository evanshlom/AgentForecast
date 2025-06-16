# Supply Chain Forecast AI Agent

AI-powered time series forecasting demo using Claude Sonnet 3.5 to modify supply chain forecasts through natural language. Track steel, wood, and glass demand with real-time adjustments via chat.

## Demo Instructions

Terminal 1 (Backend):
```bash
cd backend
docker build -t forecast-backend .
docker run -p 8369:8369 -e ANTHROPIC_API_KEY="your_api_key_here" forecast-backend
```

Terminal 2 (Frontend):
```bash
cd frontend
docker build -t forecast-frontend .
docker run -p 3369:3369 forecast-frontend
```

Open browser: `http://localhost:3369`

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