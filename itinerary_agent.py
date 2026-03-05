import re
import json
from groq import Groq
from config import Config

class ItineraryAgent:
    def __init__(self):
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.itinerary_keywords = ['plan', 'trip', 'itinerary', 'day trip', 'days', 'visit for']
    
    def is_itinerary_query(self, query):
        """Detect if query is asking for an itinerary"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.itinerary_keywords)
    
    def extract_parameters(self, query):
        """Extract location, days, and budget from query"""
        query_lower = query.lower()
        
        # Extract number of days
        days = None
        day_patterns = [
            r'(\d+)\s*day',
            r'(\d+)\s*-\s*day',
            r'for\s*(\d+)\s*days'
        ]
        for pattern in day_patterns:
            match = re.search(pattern, query_lower)
            if match:
                days = int(match.group(1))
                break
        
        # Extract budget
        budget = None
        budget_patterns = [
            r'\$(\d+)',
            r'(\d+)\s*dollars',
            r'budget\s*of\s*(\d+)',
            r'(\d+)\s*rupees',
            r'₹(\d+)'
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, query_lower)
            if match:
                budget = int(match.group(1))
                break
        
        # Extract location - check for "focusing on" pattern first (from landmark detection)
        location = None
        
        # Priority 1: Check for enhanced query pattern "focusing on X in Y"
        focusing_pattern = r'focusing on ([^)]+) in ([^)]+)\)'
        match = re.search(focusing_pattern, query)
        if match:
            landmark = match.group(1)
            city = match.group(2)
            location = city  # Use the city as primary location
            print(f"Extracted location from landmark: {location}")
            return {
                'location': location,
                'days': days or 3,
                'budget': budget,
                'landmark': landmark
            }
        
        # Priority 2: Standard location patterns
        location_patterns = [
            r'(?:in|to|for|visit)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:trip|itinerary)'
        ]
        for pattern in location_patterns:
            match = re.search(pattern, query)
            if match:
                location = match.group(1)
                break
        
        if not location:
            words = query.split()
            for word in words:
                if word[0].isupper() and word.lower() not in ['plan', 'trip', 'day', 'days']:
                    location = word
                    break
        
        return {
            'location': location or 'the destination',
            'days': days or 3,
            'budget': budget
        }
    
    def generate_itinerary(self, query, retrieved_chunks, chat_history=""):
        """Generate premium structured itinerary with hotels, flights, and transportation"""
        
        params = self.extract_parameters(query)
        
        context = "\n\n".join([
            f"Activity/Place {i+1}:\n{chunk['text']}" 
            for i, chunk in enumerate(retrieved_chunks)
        ])
        
        budget_guidance = ""
        if params['budget']:
            daily_budget = params['budget'] / params['days']
            budget_guidance = f"""
Budget: ₹{params['budget']} total (₹{daily_budget:.2f}/day)
Distribute costs realistically across activities, accommodation, and transportation."""
        
        prompt = f"""Create a COMPLETE, PREMIUM {params['days']}-day travel package for {params['location']}.

{budget_guidance}

Available Activities & Information:
{context}

IMPORTANT: The user wants to visit {params['location']}. Focus ALL activities on {params['location']} and nearby areas.

MUST INCLUDE:
1. FLIGHTS - Suggest flight options with approximate costs
2. HOTELS - Recommend 2-3 hotels per budget category (budget/mid-range/luxury)
3. LOCAL TRANSPORTATION - Airport transfers, local travel options
4. DAILY ITINERARY - Detailed activities with themes
5. MEALS - Where to eat (breakfast/lunch/dinner suggestions)

RULES FOR ITINERARY:

1. DAILY THEMES - Each day needs a clear theme:
   - Adventure Day, Heritage Day, Beach Escape, Party Night, Island Day, Relaxation Day, Foodie Day

2. ACTIVITY FOCUS:
   - Main activities = experiences, sights, adventures
   - Include meal suggestions but don't make them the main focus

3. GEOGRAPHICAL CLUSTERING:
   - Group nearby locations together
   - Minimize travel time between activities

4. VARIETY (Required):
   - At least 1 Adventure activity
   - At least 1 Heritage/Cultural experience  
   - At least 1 Nightlife experience
   - At least 1 Unique experience
   - Mix of active and relaxing activities

5. REALISTIC TIMING and COSTS

JSON Format:
{{
  "flights": {{
    "outbound": {{
      "from": "Major city",
      "to": "{params['location']}",
      "cost_range": "₹5000-₹15000",
      "duration": "2-3 hours",
      "airlines": ["IndiGo", "Air India", "SpiceJet"]
    }},
    "return": {{
      "from": "{params['location']}",
      "to": "Major city",
      "cost_range": "₹5000-₹15000",
      "duration": "2-3 hours"
    }}
  }},
  "hotels": [
    {{
      "name": "Hotel Name",
      "category": "budget/mid-range/luxury",
      "location": "Area name",
      "cost_per_night": 2000,
      "amenities": ["WiFi", "Pool", "Breakfast"],
      "rating": 4.5
    }}
  ],
  "transportation": {{
    "airport_transfer": {{
      "options": ["Taxi (₹800)", "Prepaid Cab (₹600)", "Bus (₹100)"],
      "recommended": "Prepaid Cab"
    }},
    "local_transport": {{
      "options": ["Rent Scooter (₹300/day)", "Taxi", "Auto-rickshaw"],
      "recommended": "Rent Scooter for flexibility"
    }}
  }},
  "days": [
    {{
      "day": 1,
      "theme": "Arrival & Beach Day",
      "activities": [
        {{
          "time_slot": "Morning (9 AM - 12 PM)",
          "activity": "Activity description",
          "location": "Specific place",
          "cost": 50,
          "category": "adventure/heritage/beach/nightlife/unique/relaxation"
        }}
      ],
      "meals": {{
        "breakfast": "Restaurant name - ₹300",
        "lunch": "Restaurant name - ₹500",
        "dinner": "Restaurant name - ₹800"
      }},
      "daily_total": 2500
    }}
  ],
  "cost_breakdown": {{
    "flights": 20000,
    "accommodation": 15000,
    "activities": 8000,
    "meals": 6000,
    "transportation": 3000,
    "total": 52000
  }}
}}

Return ONLY valid JSON."""

        try:
            response = self.client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert travel planner creating COMPLETE travel packages.

Your packages include:
- Flight recommendations with realistic costs
- Hotel options across budget categories
- Transportation guidance
- Detailed daily itineraries with themes
- Meal suggestions
- Complete cost breakdown

Return only valid JSON, no markdown."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=3500
            )
            
            itinerary_json_text = response.choices[0].message.content.strip()
            
            # Clean markdown
            if itinerary_json_text.startswith('```json'):
                itinerary_json_text = itinerary_json_text[7:]
            if itinerary_json_text.startswith('```'):
                itinerary_json_text = itinerary_json_text[3:]
            if itinerary_json_text.endswith('```'):
                itinerary_json_text = itinerary_json_text[:-3]
            itinerary_json_text = itinerary_json_text.strip()
            
            try:
                itinerary_data = json.loads(itinerary_json_text)
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                itinerary_data = {'days': [], 'raw_text': itinerary_json_text}
            
            return {
                'location': params['location'],
                'days': params['days'],
                'budget': params['budget'],
                'daily_budget': params['budget'] / params['days'] if params['budget'] else None,
                'itinerary_json': itinerary_data,
                'response_type': 'Complete Travel Package'
            }
            
        except Exception as e:
            return {
                'error': f"Error: {str(e)}",
                'response_type': 'Complete Travel Package'
            }
    
    def format_itinerary_response(self, itinerary_data, retrieved_chunks):
        """Format complete travel package for display"""
        if 'error' in itinerary_data:
            return {
                'answer': itinerary_data['error'],
                'response_type': 'Complete Travel Package',
                'retrieved_sources': []
            }
        
        answer = f"""✈️ {itinerary_data['location'].upper()} - {itinerary_data['days']}-Day Complete Travel Package
"""
        
        if itinerary_data['budget']:
            answer += f"💰 Budget: ₹{itinerary_data['budget']} (₹{itinerary_data['daily_budget']:.2f}/day)\n"
        
        answer += f"\n{'='*70}\n\n"
        
        itinerary_json = itinerary_data.get('itinerary_json', {})
        
        if 'raw_text' in itinerary_json:
            answer += itinerary_json['raw_text']
        else:
            # FLIGHTS SECTION
            if 'flights' in itinerary_json:
                flights = itinerary_json['flights']
                answer += "✈️ FLIGHTS\n"
                answer += f"{'-'*70}\n"
                if 'outbound' in flights:
                    ob = flights['outbound']
                    answer += f"🛫 Outbound: {ob.get('from', 'Your City')} → {ob.get('to', itinerary_data['location'])}\n"
                    answer += f"   Cost: {ob.get('cost_range', '₹5000-₹15000')} | Duration: {ob.get('duration', '2-3 hours')}\n"
                    if 'airlines' in ob:
                        answer += f"   Airlines: {', '.join(ob['airlines'])}\n"
                if 'return' in flights:
                    ret = flights['return']
                    answer += f"🛬 Return: {ret.get('from', itinerary_data['location'])} → {ret.get('to', 'Your City')}\n"
                    answer += f"   Cost: {ret.get('cost_range', '₹5000-₹15000')} | Duration: {ret.get('duration', '2-3 hours')}\n"
                answer += f"\n{'='*70}\n\n"
            
            # HOTELS SECTION
            if 'hotels' in itinerary_json and itinerary_json['hotels']:
                answer += "🏨 RECOMMENDED HOTELS\n"
                answer += f"{'-'*70}\n"
                for hotel in itinerary_json['hotels']:
                    category_emoji = {'budget': '💵', 'mid-range': '💳', 'luxury': '💎'}.get(hotel.get('category', 'mid-range'), '🏨')
                    answer += f"{category_emoji} {hotel.get('name', 'Hotel')} ({hotel.get('category', 'mid-range').title()})\n"
                    answer += f"   📍 {hotel.get('location', 'Central location')}\n"
                    answer += f"   💰 ₹{hotel.get('cost_per_night', 2000)}/night\n"
                    if 'amenities' in hotel:
                        answer += f"   ✨ {', '.join(hotel['amenities'])}\n"
                    if 'rating' in hotel:
                        answer += f"   ⭐ {hotel['rating']}/5\n"
                    answer += "\n"
                answer += f"{'='*70}\n\n"
            
            # TRANSPORTATION SECTION
            if 'transportation' in itinerary_json:
                trans = itinerary_json['transportation']
                answer += "🚗 TRANSPORTATION\n"
                answer += f"{'-'*70}\n"
                if 'airport_transfer' in trans:
                    at = trans['airport_transfer']
                    answer += f"🛬 Airport Transfer:\n"
                    if 'options' in at:
                        for opt in at['options']:
                            answer += f"   • {opt}\n"
                    if 'recommended' in at:
                        answer += f"   ✅ Recommended: {at['recommended']}\n"
                    answer += "\n"
                if 'local_transport' in trans:
                    lt = trans['local_transport']
                    answer += f"🏍️ Local Transport:\n"
                    if 'options' in lt:
                        for opt in lt['options']:
                            answer += f"   • {opt}\n"
                    if 'recommended' in lt:
                        answer += f"   ✅ Recommended: {lt['recommended']}\n"
                answer += f"\n{'='*70}\n\n"
            
            # DAILY ITINERARY
            if 'days' in itinerary_json and itinerary_json['days']:
                answer += "📅 DAILY ITINERARY\n"
                answer += f"{'='*70}\n\n"
                
                for day_data in itinerary_json['days']:
                    theme = day_data.get('theme', day_data.get('title', 'Exploration'))
                    answer += f"DAY {day_data['day']}: {theme.upper()}\n"
                    answer += f"{'-'*70}\n\n"
                    
                    for activity in day_data.get('activities', []):
                        category_emoji = {
                            'adventure': '🏄',
                            'heritage': '🏛️',
                            'beach': '🏖️',
                            'nightlife': '🎉',
                            'unique': '✨',
                            'relaxation': '🧘',
                            'food': '🍽️',
                            'sightseeing': '👀',
                            'shopping': '🛍️'
                        }.get(activity.get('category', 'sightseeing'), '📍')
                        
                        answer += f"⏰ {activity['time_slot']}\n"
                        answer += f"{category_emoji} {activity['activity']}\n"
                        answer += f"📍 {activity['location']}\n"
                        answer += f"💵 ₹{activity['cost']}\n\n"
                    
                    # Meals
                    if 'meals' in day_data:
                        meals = day_data['meals']
                        answer += f"🍽️ MEALS:\n"
                        if 'breakfast' in meals:
                            answer += f"   Breakfast: {meals['breakfast']}\n"
                        if 'lunch' in meals:
                            answer += f"   Lunch: {meals['lunch']}\n"
                        if 'dinner' in meals:
                            answer += f"   Dinner: {meals['dinner']}\n"
                        answer += "\n"
                    
                    daily_total = day_data.get('daily_total', 0)
                    answer += f"💰 Day {day_data['day']} Total: ₹{daily_total}\n\n"
                    answer += f"{'='*70}\n\n"
            
            # COST BREAKDOWN
            if 'cost_breakdown' in itinerary_json:
                cb = itinerary_json['cost_breakdown']
                answer += "💎 COMPLETE COST BREAKDOWN\n"
                answer += f"{'-'*70}\n"
                answer += f"✈️  Flights:          ₹{cb.get('flights', 0):,}\n"
                answer += f"🏨 Accommodation:    ₹{cb.get('accommodation', 0):,}\n"
                answer += f"🎯 Activities:       ₹{cb.get('activities', 0):,}\n"
                answer += f"🍽️  Meals:            ₹{cb.get('meals', 0):,}\n"
                answer += f"🚗 Transportation:   ₹{cb.get('transportation', 0):,}\n"
                answer += f"{'-'*70}\n"
                answer += f"💰 TOTAL:            ₹{cb.get('total', 0):,}\n\n"
        
        return {
            'answer': answer,
            'response_type': 'Complete Travel Package',
            'itinerary_json': itinerary_json,
            'itinerary_metadata': {
                'location': itinerary_data['location'],
                'days': itinerary_data['days'],
                'budget': itinerary_data['budget']
            },
            'retrieved_sources': [
                {
                    'text': chunk['text'],
                    'score': chunk['score'],
                    'metadata': chunk['metadata']
                }
                for chunk in retrieved_chunks
            ]
        }
