#!/bin/bash

# Script to create a macOS app bundle for Spotify Playlist Adder

APP_NAME="Spotify Playlister"
APP_DIR="$HOME/Desktop/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Creating Spotify Playlister.app..."

# Remove old app if exists
if [ -d "$APP_DIR" ]; then
    echo "Removing old app..."
    rm -rf "$APP_DIR"
fi

# Create app bundle structure
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy Python files and dependencies
echo "Copying application files..."
cp "$SCRIPT_DIR/main.py" "$RESOURCES_DIR/"
cp "$SCRIPT_DIR/spotify_auth.py" "$RESOURCES_DIR/"
cp "$SCRIPT_DIR/setup_auth.py" "$RESOURCES_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$RESOURCES_DIR/"

# Copy config and cache if they exist
if [ -f "$SCRIPT_DIR/config.json" ]; then
    cp "$SCRIPT_DIR/config.json" "$RESOURCES_DIR/"
fi
if [ -f "$SCRIPT_DIR/.spotify_cache" ]; then
    cp "$SCRIPT_DIR/.spotify_cache" "$RESOURCES_DIR/"
fi

# Create launcher script
cat > "$MACOS_DIR/launcher.sh" << 'EOF'
#!/bin/bash

# Get the directory where the app is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$SCRIPT_DIR/../Resources"

# Change to resources directory
cd "$RESOURCES_DIR"

# Activate virtual environment from original location
VENV_PATH="$(dirname "$(dirname "$SCRIPT_DIR")")/Code/Spotify Playlister/venv"

if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    python main.py 2>&1 | logger -t "SpotifyPlaylister"
else
    # Fallback to system python3
    python3 main.py 2>&1 | logger -t "SpotifyPlaylister"
fi
EOF

chmod +x "$MACOS_DIR/launcher.sh"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher.sh</string>
    <key>CFBundleIdentifier</key>
    <string>com.spotify.playlister</string>
    <key>CFBundleName</key>
    <string>Spotify Playlister</string>
    <key>CFBundleDisplayName</key>
    <string>Spotify Playlister</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Make the app executable
chmod +x "$APP_DIR"

echo ""
echo "✅ Success! Spotify Playlister.app has been created on your Desktop!"
echo ""
echo "To use it:"
echo "  1. Double-click 'Spotify Playlister.app' on your Desktop"
echo "  2. You can drag it to your Applications folder if you want"
echo "  3. You can add it to your Dock for quick access"
echo ""
