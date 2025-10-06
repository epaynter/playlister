#!/usr/bin/env python3
"""
Setup script to handle Spotify OAuth authentication before launching the main app.
This avoids tkinter blocking issues during the OAuth flow.
"""
import sys
from spotify_auth import get_spotify_client, load_config, save_credentials

def setup_authentication():
    """Setup Spotify authentication."""
    print("=" * 60)
    print("Spotify Playlist Adder - Authentication Setup")
    print("=" * 60)
    print()

    config = load_config()

    # Check if credentials exist
    if not config.get('client_id') or not config.get('client_secret'):
        print("Spotify API credentials required.")
        print()
        print("To get credentials:")
        print("1. Go to https://developer.spotify.com/dashboard")
        print("2. Create an app")
        print("3. Add 'http://127.0.0.1:8888/callback' as Redirect URI")
        print("4. Copy Client ID and Client Secret")
        print()

        client_id = input("Enter Client ID: ").strip()
        client_secret = input("Enter Client Secret: ").strip()

        if not client_id or not client_secret:
            print("Error: Both Client ID and Client Secret are required!")
            sys.exit(1)

        save_credentials(client_id, client_secret)
        print("\n✓ Credentials saved!")
        print()

    # Test authentication
    print("Authenticating with Spotify...")
    print("A browser window will open for authorization.")
    print("After authorizing, you can close the browser and return here.")
    print()

    try:
        sp = get_spotify_client()

        # Test the connection
        user = sp.current_user()
        print(f"\n✓ Successfully authenticated as: {user['display_name']}")
        print()
        print("Authentication complete! You can now run the app with:")
        print("  python main.py")
        print()
        return True

    except Exception as e:
        print(f"\n✗ Authentication failed: {str(e)}")
        print("\nPlease check your credentials and try again.")
        print("To re-enter credentials, delete config.json and run this script again.")
        return False

if __name__ == "__main__":
    success = setup_authentication()
    sys.exit(0 if success else 1)
