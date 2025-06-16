import os
from datetime import datetime, timedelta
import anthropic
import json
import re

class ForecastAgent:
    def __init__(self):
        self.client = anthropic.Client(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    
    def process_message(self, message, current_forecast):
        # Create a simple prompt for Claude
        prompt = f"""You are a supply chain forecast assistant. The user wants to modify a forecast for steel, wood, and glass.

Current message: "{message}"
Today's date: {datetime.now().date()}
Forecast period: Next 30 days starting tomorrow

Parse the user's intent and return a JSON with modifications. Examples:
- "Increase steel by 20% starting next Monday" 
- "We need 50 more units of wood daily for 2 weeks"
- "Glass demand will drop by 30% from the 25th"

Return ONLY valid JSON in this format:
{{
    "response": "Brief confirmation of the changes",
    "modifications": [
        {{
            "material": "steel|wood|glass",
            "type": "percentage|absolute|set",
            "value": number,
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        }}
    ]
}}

If no modifications needed, return empty modifications array."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract JSON from response
            text = response.content[0].text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                
                # Convert date strings to date objects
                for mod in result.get('modifications', []):
                    mod['start_date'] = datetime.strptime(mod['start_date'], '%Y-%m-%d').date()
                    mod['end_date'] = datetime.strptime(mod['end_date'], '%Y-%m-%d').date()
                
                return result
            
        except Exception as e:
            print(f"Agent error: {e}")
        
        return {
            "response": "I understood your request but couldn't process it. Please try rephrasing.",
            "modifications": []
        }