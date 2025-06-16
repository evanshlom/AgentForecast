from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime, timedelta
from models.rnn_model import ForecastRNN
from models.forecast_agent import ForecastAgent
from data_generator import generate_historical_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
rnn_model = ForecastRNN()
agent = ForecastAgent()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Generate initial data
    historical_data = generate_historical_data()
    base_forecast = rnn_model.predict(historical_data)
    adjusted_forecast = base_forecast.copy()
    
    # Send initial forecast
    await websocket.send_json({
        "type": "forecast",
        "historical": historical_data.to_dict('records'),
        "forecast": adjusted_forecast.to_dict('records')
    })
    
    try:
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            
            # Process with agent
            adjustments = agent.process_message(message, adjusted_forecast)
            
            # Apply adjustments
            if adjustments:
                adjusted_forecast = rnn_model.apply_adjustments(
                    base_forecast.copy(), 
                    adjustments
                )
            
            # Send response with updated forecast
            await websocket.send_json({
                "type": "response",
                "message": adjustments.get("response", "Forecast updated"),
                "historical": historical_data.to_dict('records'),
                "forecast": adjusted_forecast.to_dict('records')
            })
            
    except Exception as e:
        print(f"WebSocket error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8369)