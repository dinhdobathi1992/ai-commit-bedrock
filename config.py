import json
import os
import sys
from typing import Dict, Any

def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for development and PyInstaller bundle."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json or fallback to default."""
    # Default configuration (embedded in code as fallback)
    default_config = {
        "litellm_endpoint": "https://litellm.shared-services.adb.adi.tech/v1/chat/completions",
        "default_model": "gpt-4o-mini",
        "max_diff_length": 4000,
        "max_tokens": 150,
        "temperature": 0.3
    }
    
    # Try to load default config from file
    try:
        default_config_path = get_resource_path('config.default.json')
        with open(default_config_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load config.default.json ({e}), using embedded defaults")
        config = default_config.copy()
    
    # Try to load user config from current directory
    config_path = 'config.json'
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                config.update(user_config)
    except json.JSONDecodeError as e:
        print(f"Error loading user config: {e}")

    return config
