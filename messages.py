"""Message and animation registry loader"""

import json
from config import MESSAGE_REGISTRY_FILE, DEFAULT_DISPLAY_TIME


def load_registry():
    """Load message and animation registry from JSON file"""
    try:
        with open(MESSAGE_REGISTRY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return (
                data.get('messages', {}),
                data.get('animations', {}),
                data.get('defaults', {}).get('display_time', DEFAULT_DISPLAY_TIME)
            )
    except Exception as e:
        print(f"Error loading registry: {e}")
        return {}, {}, DEFAULT_DISPLAY_TIME


# Global registries
MESSAGE_REGISTRY, ANIMATION_REGISTRY, GLOBAL_DEFAULT_DISPLAY_TIME = load_registry()
