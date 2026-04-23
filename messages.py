"""Unified registry loader for animations and messages"""

import json
from config import MESSAGE_REGISTRY_FILE, DEFAULT_DISPLAY_TIME


def load_registry():
    """Load unified registry from JSON file"""
    try:
        with open(MESSAGE_REGISTRY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return (
                data.get('registry', {}),
                data.get('defaults', {})
            )
    except Exception as e:
        print(f"Error loading registry: {e}")
        return {}, {}


# Global registry and defaults
REGISTRY, DEFAULTS = load_registry()
