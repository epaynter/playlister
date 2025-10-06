import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os

CONFIG_FILE = "config.json"

def get_spotify_client():
    """
    Creates and returns an authenticated Spotify client.
    Handles OAuth flow and token management.
    """
    scope = "user-read-currently-playing user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private user-library-read"

    # Load credentials from config
    client_id, client_secret = load_credentials()

    if not client_id or not client_secret:
        raise ValueError("Spotify credentials not configured. Please set them in config.json")

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:8888/callback",
        scope=scope,
        cache_path=".spotify_cache"
    )

    return spotipy.Spotify(auth_manager=auth_manager)

def load_credentials():
    """Load Spotify API credentials from config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('client_id', ''), config.get('client_secret', '')
    return '', ''

def save_credentials(client_id, client_secret):
    """Save Spotify API credentials to config file."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

    config['client_id'] = client_id
    config['client_secret'] = client_secret

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_config():
    """Load full configuration."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save full configuration."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
