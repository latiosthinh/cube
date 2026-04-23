"""Message registry loader"""

import json
from config import MESSAGE_REGISTRY_FILE, DEFAULT_DISPLAY_TIME


def load_message_registry():
    """Load message registry from JSON file"""
    try:
        with open(MESSAGE_REGISTRY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('messages', {}), data.get('defaults', {}).get('display_time', DEFAULT_DISPLAY_TIME)
    except Exception as e:
        print(f"Error loading message registry: {e}")
        return {}, DEFAULT_DISPLAY_TIME


# Global message registry
MESSAGE_REGISTRY, GLOBAL_DEFAULT_DISPLAY_TIME = load_message_registry()
