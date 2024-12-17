import json
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json or fallback to default."""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to load user config
    config_path = os.path.join(script_dir, 'config.json')
    default_config_path = os.path.join(script_dir, 'config.default.json')
    
    # Load default config first
    try:
        with open(default_config_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading default config: {e}")
        return {}

    # Override with user config if it exists
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                config.update(user_config)
    except json.JSONDecodeError as e:
        print(f"Error loading user config: {e}")

    return config
