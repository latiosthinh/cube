"""Pet state management and persistence"""

import json
import os
from datetime import datetime

from config import CONFIG_FILE


class PetState:
    """Manages pet stats and persistence"""
    
    def __init__(self):
        self.hunger = 50
        self.happiness = 70
        self.energy = 80
        self.health = 100
        self.age = 0
        self.is_sleeping = False
        self.is_eating = False
        self.last_fed = datetime.now()
        self.pet_type = "cube"
        self.position_x = 0
        self.name = ""
        
    def save(self, filename=CONFIG_FILE):
        """Save state to JSON file"""
        data = {
            'hunger': self.hunger,
            'happiness': self.happiness,
            'energy': self.energy,
            'health': self.health,
            'age': self.age,
            'is_sleeping': self.is_sleeping,
            'is_eating': self.is_eating,
            'last_fed': self.last_fed.isoformat(),
            'pet_type': self.pet_type,
            'position_x': self.position_x,
            'name': self.name
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filename=CONFIG_FILE):
        """Load state from JSON file"""
        state = cls()
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                state.hunger = data.get('hunger', 50)
                state.happiness = data.get('happiness', 70)
                state.energy = data.get('energy', 80)
                state.health = data.get('health', 100)
                state.age = data.get('age', 0)
                state.is_sleeping = data.get('is_sleeping', False)
                state.is_eating = data.get('is_eating', False)
                if 'last_fed' in data:
                    state.last_fed = datetime.fromisoformat(data['last_fed'])
                state.pet_type = data.get('pet_type', 'cube')
                state.position_x = data.get('position_x', 0)
                state.name = data.get('name', '')
                
                # Update stats based on time passed
                hours_passed = (datetime.now() - state.last_fed).total_seconds() / 3600
                state.hunger = min(100, state.hunger + int(hours_passed * 10))
                state.energy = max(0, state.energy - int(hours_passed * 5))
            except Exception as e:
                print(f"Error loading save: {e}")
        return state
