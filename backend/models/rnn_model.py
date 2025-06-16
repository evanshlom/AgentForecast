import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class SimpleLSTM:
    """Mock LSTM for demo - no real torch needed"""
    pass

class ForecastRNN:
    def __init__(self):
        self.model = SimpleLSTM()
        self.materials = ['steel', 'wood', 'glass']
    
    def predict(self, historical_data, days=30):
        # Simple prediction: use last 30 days average + random walk
        last_30_days = historical_data.tail(30)
        
        forecast_dates = []
        today = datetime.now().date()
        
        for i in range(1, days + 1):
            forecast_dates.append(today + timedelta(days=i))
        
        # Generate simple forecast with trend
        forecast_data = []
        base_values = {
            'steel': last_30_days['steel'].mean(),
            'wood': last_30_days['wood'].mean(),
            'glass': last_30_days['glass'].mean()
        }
        
        for date in forecast_dates:
            row = {'date': date}
            for material in self.materials:
                # Add some random walk with slight upward trend
                trend = 1 + (0.001 * forecast_dates.index(date))
                noise = np.random.normal(0, 5)
                row[material] = max(0, base_values[material] * trend + noise)
            forecast_data.append(row)
        
        return pd.DataFrame(forecast_data)
    
    def apply_adjustments(self, forecast, adjustments):
        if not adjustments.get('modifications'):
            return forecast
        
        for mod in adjustments['modifications']:
            material = mod['material']
            start_date = mod['start_date']
            end_date = mod['end_date']
            adjustment_type = mod['type']
            value = mod['value']
            
            # Apply adjustment
            mask = (forecast['date'] >= start_date) & (forecast['date'] <= end_date)
            
            if adjustment_type == 'percentage':
                forecast.loc[mask, material] *= (1 + value / 100)
            elif adjustment_type == 'absolute':
                forecast.loc[mask, material] += value
            elif adjustment_type == 'set':
                forecast.loc[mask, material] = value
        
        # Ensure no negative values
        for material in self.materials:
            forecast[material] = forecast[material].clip(lower=0)
        
        return forecast