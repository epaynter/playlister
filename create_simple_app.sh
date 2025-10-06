#!/bin/bash

# Create a standalone app without Terminal dependency

APP_NAME="Spotify Playlister"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP="$HOME/Desktop"
APP_PATH="$DESKTOP/$APP_NAME.app"

echo "Creating Spotify Playlister app..."

# Remove old app if exists
if [ -d "$APP_PATH" ]; then
    rm -rf "$APP_PATH"
fi

# Create app bundle structure
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Create the launcher script that runs directly
cat > "$APP_PATH/Contents/MacOS/SpotifyPlaylister" << EOF
#!/bin/bash

# Change to the original project directory
cd "$SCRIPT_DIR"

# Activate venv and run
source venv/bin/activate
python main.py
EOF

# Make it executable
chmod +x "$APP_PATH/Contents/MacOS/SpotifyPlaylister"

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>SpotifyPlaylister</string>
    <key>CFBundleIdentifier</key>
    <string>com.spotify.playlister</string>
    <key>CFBundleName</key>
    <string>Spotify Playlister</string>
    <key>CFBundleDisplayName</key>
    <string>Spotify Playlister</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

echo ""
echo "✅ Successfully created '$APP_NAME.app' on your Desktop!"
echo ""
echo "To use:"
echo "  1. Double-click 'Spotify Playlister.app' to launch"
echo "  2. If you get a security warning, go to:"
echo "     System Preferences → Privacy & Security → Allow"
echo "  3. Drag to Applications folder or Dock for easy access"
echo ""
