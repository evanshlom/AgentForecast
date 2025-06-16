import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_historical_data():
    # Generate data from Jan 1, 2024 to today
    start_date = datetime(2024, 1, 1).date()
    end_date = datetime.now().date()
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Generate synthetic data with seasonal patterns
    data = []
    for i, date in enumerate(dates):
        # Base values with seasonal variation
        steel_base = 100 + 20 * np.sin(2 * np.pi * i / 365)
        wood_base = 80 + 15 * np.sin(2 * np.pi * (i + 90) / 365)
        glass_base = 60 + 10 * np.sin(2 * np.pi * (i + 180) / 365)
        
        # Add weekly pattern
        day_of_week = date.weekday()
        weekly_factor = 1.0 if day_of_week < 5 else 0.7
        
        # Add noise
        steel = max(0, steel_base * weekly_factor + np.random.normal(0, 10))
        wood = max(0, wood_base * weekly_factor + np.random.normal(0, 8))
        glass = max(0, glass_base * weekly_factor + np.random.normal(0, 6))
        
        data.append({
            'date': date,
            'steel': steel,
            'wood': wood,
            'glass': glass
        })
    
    return pd.DataFrame(data)