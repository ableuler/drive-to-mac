#!/bin/bash
set -euo pipefail

HOST_NAME="com.github.drive_to_mac"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="${SCRIPT_DIR}/drive_to_mac_host.py"
# Chrome starts native hosts with a minimal PATH, so pin the interpreter found now.
PYTHON_PATH="${PYTHON_PATH:-$(command -v python3)}"
WRAPPER_PATH="${SCRIPT_DIR}/drive_to_mac_host.sh"
TARGET_DIR="${HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts"
# Unpacked extensions get an ID derived from their folder path; check chrome://extensions.
EXTENSION_ID="${EXTENSION_ID:-ahjlddpdcggpflpamdmofjfkhmdocpka}"

# 1. Generate a wrapper that runs the host with the chosen interpreter
cat <<EOF > "$WRAPPER_PATH"
#!/bin/sh
exec "${PYTHON_PATH}" "${SCRIPT_PATH}" "\$@"
EOF
chmod 755 "$WRAPPER_PATH"

# 2. Install the manifest (the origin needs the trailing slash)
mkdir -p "$TARGET_DIR"
cat <<EOF > "$TARGET_DIR/${HOST_NAME}.json"
{
  "name": "${HOST_NAME}",
  "description": "Reveal Google Drive files in macOS Finder",
  "path": "${WRAPPER_PATH}",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://${EXTENSION_ID}/"
  ]
}
EOF

echo "Installed Native Messaging host."
echo "Manifest: $TARGET_DIR/${HOST_NAME}.json"
echo "Python:   $PYTHON_PATH"
echo "Wrapper:  $WRAPPER_PATH"
