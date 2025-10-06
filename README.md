# Spotify Playlist Adder

A lightweight macOS app that floats on top of other windows and lets you quickly add currently playing Spotify tracks to your chosen playlist.

## Features

- 🎵 Shows currently playing track
- ➕ One-click add to your go-to playlist
- 🔝 Always-on-top floating window
- 📋 Easy playlist selection with saved preference
- 🔄 Auto-refreshes current track

## Setup Instructions

### 1. Create Virtual Environment and Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Create Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in app name (e.g., "Playlist Adder") and description
5. Accept terms and click "Create"
6. Click "Edit Settings"
7. Add `http://127.0.0.1:8888/callback` to the "Redirect URIs" field
8. Click "Save"
9. Copy your **Client ID** and **Client Secret** (click "Show Client Secret")

### 3. First Time Setup - Run Authentication

```bash
python setup_auth.py
```

This will:
- Prompt you to enter your Client ID and Client Secret
- Open a browser window for Spotify authentication (complete the login in the browser)
- Save your credentials for future use

### 4. Run the App

```bash
python main.py
```

The app window will appear and start showing your currently playing tracks!

### 5. Using the App

1. Select your target playlist from the dropdown
2. Play a song on Spotify
3. Click "➕ Add to Playlist" to add the current track
4. The button will briefly show "✓ Added!" for confirmation

The app will remember your selected playlist for next time!

## Files

- `main.py` - Main application with UI
- `setup_auth.py` - One-time authentication setup script
- `spotify_auth.py` - Spotify OAuth and config management
- `config.json` - Auto-generated file storing credentials and preferences
- `.spotify_cache` - Auto-generated token cache

## Troubleshooting

**"Failed to authenticate"**: Check that your Client ID and Client Secret are correct. Delete `config.json` and `.spotify_cache`, then run `python setup_auth.py` again.

**"No track playing"**: Make sure Spotify is open and actively playing music.

**Can't add to playlist**: Ensure you have permission to modify the playlist (you must be the owner or have edit rights).

## Notes

- The app checks for the currently playing track every 2 seconds
- The window is small (350x180px) and always stays on top
- Your selected playlist preference is saved automatically
