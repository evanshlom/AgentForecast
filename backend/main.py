from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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

# Initialize models and data
print("Initializing models...")
rnn_model = ForecastRNN()
agent = ForecastAgent()

# Generate and train on historical data
print("Generating historical data...")
historical_data = generate_historical_data()
print("Training model...")
rnn_model.train(historical_data)
print("Model ready!")

# Generate initial forecast
base_forecast = rnn_model.predict(historical_data)
current_forecast = base_forecast.copy()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"New WebSocket connection attempt")
    await websocket.accept()
    print(f"WebSocket accepted")
    
    try:
        # Send initial forecast immediately on connection
        initial_data = {
            "type": "forecast",
            "historical": historical_data.tail(60).to_dict('records'),
            "forecast": current_forecast.to_dict('records'),
            "message": "Connected! I can help you adjust your supply chain forecast. Try saying things like \"Increase steel by 20% next week\" or \"We expect lower wood demand for 10 days\"."
        }
        
        # Convert dates to strings for JSON serialization
        for record in initial_data['historical']:
            record['date'] = str(record['date'])
        for record in initial_data['forecast']:
            record['date'] = str(record['date'])
            
        print(f"Sending initial data with {len(initial_data['historical'])} historical and {len(initial_data['forecast'])} forecast records")
        await websocket.send_json(initial_data)
        
        # Maintain state for this connection
        connection_base_forecast = base_forecast.copy()
        connection_current_forecast = current_forecast.copy()
        
        while True:
            # Receive message from client
            message = await websocket.receive_text()
            print(f"Received: {message}")
            
            # Process with agent
            adjustments = agent.process_message(message, connection_current_forecast)
            print(f"Adjustments: {adjustments}")
            
            # Apply adjustments to get new forecast
            if adjustments and adjustments.get('modifications'):
                connection_current_forecast = rnn_model.apply_adjustments(
                    connection_base_forecast.copy(), 
                    adjustments
                )
            
            # Send response with updated forecast
            response_data = {
                "type": "response",
                "message": adjustments.get("response", "I've updated the forecast based on your input."),
                "historical": historical_data.tail(60).to_dict('records'),
                "forecast": connection_current_forecast.to_dict('records'),
                "modifications": len(adjustments.get('modifications', []))
            }
            
            # Convert dates to strings for JSON serialization
            for record in response_data['historical']:
                record['date'] = str(record['date'])
            for record in response_data['forecast']:
                record['date'] = str(record['date'])
                
            await websocket.send_json(response_data)
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error processing request: {str(e)}"
            })
        except:
            pass

@app.get("/")
async def root():
    return {"message": "Supply Chain Forecast API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8369)