#!/bin/bash

# Simple script to create a launchable app for Spotify Playlister

APP_NAME="Spotify Playlister"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP="$HOME/Desktop"

echo "Creating launcher for Spotify Playlister..."

# Create the AppleScript application
cat > "/tmp/spotify_playlister.scpt" << EOF
#!/usr/bin/osascript

tell application "Terminal"
    activate
    set currentTab to do script "cd '$SCRIPT_DIR' && source venv/bin/activate && python main.py; exit"
end tell

-- Wait a moment for the window to appear
delay 0.5

-- Minimize or hide the terminal window
tell application "System Events"
    tell process "Terminal"
        set visible to false
    end tell
end tell
EOF

# Compile the AppleScript into an application
osacompile -o "$DESKTOP/$APP_NAME.app" "/tmp/spotify_playlister.scpt"

# Clean up temp file
rm "/tmp/spotify_playlister.scpt"

# Make it stay open
defaults write "$DESKTOP/$APP_NAME.app/Contents/Info" LSUIElement -bool YES

echo ""
echo "✅ '$APP_NAME.app' has been created on your Desktop!"
echo ""
echo "To use:"
echo "  • Double-click the app to launch"
echo "  • Drag it to your Applications folder if you want"
echo "  • Right-click → Options → Keep in Dock for quick access"
echo ""
