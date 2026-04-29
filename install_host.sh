#!/bin/bash

HOST_NAME="com.cudos.drive_to_mac"
PYTHON_PATH="/Users/ableuler/.local/bin/python3"
SCRIPT_PATH="/Users/ableuler/src/drive_to_mac/drive_to_mac_host.py"
# Pointing directly to the python script with the correct shebang is usually most stable
MANIFEST_PATH="/Users/ableuler/src/drive_to_mac/${HOST_NAME}.json"
TARGET_DIR="${HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts"
EXTENSION_ID="ahjlddpdcggpflpamdmofjfkhmdocpka"

# 1. Update the shebang in the host script to be absolute
echo "#!$PYTHON_PATH" > "$SCRIPT_PATH.tmp"
grep -v "^#!" "$SCRIPT_PATH" >> "$SCRIPT_PATH.tmp"
mv "$SCRIPT_PATH.tmp" "$SCRIPT_PATH"
chmod 755 "$SCRIPT_PATH"

# 2. Create the manifest pointing DIRECTLY to the python script
# and ensure the origin has the trailing slash.
cat <<EOF > "$MANIFEST_PATH"
{
  "name": "${HOST_NAME}",
  "description": "Reveal Google Drive files in macOS Finder",
  "path": "${SCRIPT_PATH}",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://${EXTENSION_ID}/"
  ]
}
EOF

# 3. Clean installation
rm -rf "$TARGET_DIR/${HOST_NAME}.json"
mkdir -p "$TARGET_DIR"
cp "$MANIFEST_PATH" "$TARGET_DIR/${HOST_NAME}.json"

echo "Re-installed Native Messaging host."
echo "Manifest: $TARGET_DIR/${HOST_NAME}.json"
echo "Target Script: $SCRIPT_PATH"
ls -l "$SCRIPT_PATH"
