import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class ForecastRNN:
    def __init__(self):
        self.materials = ['steel', 'wood', 'glass']
        self.model_trained = False
        self.base_trends = {}
    
    def train(self, historical_data):
        """Train model by calculating trends from historical data"""
        for material in self.materials:
            # Calculate 30-day moving average and trend
            data = historical_data[material].values
            ma30 = np.convolve(data, np.ones(30)/30, mode='valid')
            if len(ma30) > 1:
                trend = (ma30[-1] - ma30[0]) / len(ma30)
            else:
                trend = 0
            self.base_trends[material] = {
                'avg': historical_data[material].tail(30).mean(),
                'std': historical_data[material].tail(30).std(),
                'trend': trend,
                'last_value': historical_data[material].iloc[-1]
            }
        self.model_trained = True
    
    def predict(self, historical_data, days=30):
        """Generate forecast based on trained model"""
        if not self.model_trained:
            self.train(historical_data)
        
        forecast_dates = []
        today = datetime.now().date()
        
        for i in range(1, days + 1):
            forecast_dates.append(today + timedelta(days=i))
        
        forecast_data = []
        for i, date in enumerate(forecast_dates):
            row = {'date': date}
            for material in self.materials:
                base = self.base_trends[material]
                # Apply trend with some randomness
                trend_factor = 1 + (base['trend'] * 0.001 * i)
                seasonality = np.sin(2 * np.pi * i / 7) * base['std'] * 0.1
                noise = np.random.normal(0, base['std'] * 0.1)
                value = base['last_value'] * trend_factor + seasonality + noise
                row[material] = max(0, value)
            forecast_data.append(row)
        
        return pd.DataFrame(forecast_data)
    
    def apply_adjustments(self, forecast, adjustments):
        """Apply user adjustments to forecast"""
        if not adjustments.get('modifications'):
            return forecast
        
        forecast = forecast.copy()
        
        for mod in adjustments['modifications']:
            material = mod['material']
            start_date = mod['start_date']
            end_date = mod['end_date']
            adjustment_type = mod['type']
            value = mod['value']
            
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