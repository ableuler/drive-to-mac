# Reveal in Finder for Google Drive (macOS)

This project provides a Chrome extension and a native messaging host that allows you to right-click a file or folder in the Google Drive web interface and "Reveal in Finder" on your Mac.

It bridges the gap between the Google Drive web UI and the local [Google Drive for Desktop](https://www.google.com/drive/download/) mount (typically located in `~/Library/CloudStorage`).

## How it Works

1.  **Chrome Extension**: Adds a context menu item to Google Drive. When clicked, it extracts the file/folder's web ID and sends it to the native messaging host.
2.  **Native Messaging Host (`drive_to_mac_host.py`)**:
    *   Queries the local Google Drive for Desktop metadata database (`metadata_sqlite_db`) to map the web ID to a local filename and its parent structure.
    *   Resolves the full path within the `~/Library/CloudStorage/GoogleDrive-email@example.com` directory.
    *   Uses the macOS `open -R` command to reveal the file in Finder.

## Project Structure

*   `extension/`: The Chrome extension source code.
    *   `manifest.json`: Extension configuration and permissions.
    *   `background.js`: Handles context menu creation and communication with the native host.
    *   `content_script.js`: (Optional/Injected) Assists in detecting selected items on the page.
    *   `icon.svg`: Extension icon.
*   `drive_to_mac_host.py`: The Python script acting as the native messaging host.
*   `install_host.sh`: Installation script to register the native messaging host with Chrome.

## Installation

### 1. Prerequisites
*   macOS
*   [Google Drive for Desktop](https://www.google.com/drive/download/) installed and signed in.
*   Python 3 installed.

### 2. Install the Native Messaging Host
The host needs to be registered so Chrome can execute it.

1.  Open `install_host.sh`.
2.  Update `PYTHON_PATH` and `SCRIPT_PATH` if they differ from your local setup.
3.  Run the script:
    ```bash
    ./install_host.sh
    ```
    This creates a JSON manifest in `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.cudos.drive_to_mac.json`.

### 3. Install the Chrome Extension
1.  Open Chrome and navigate to `chrome://extensions/`.
2.  Enable **Developer mode** (top right).
3.  Click **Load unpacked**.
4.  Select the `extension/` folder in this repository.
5.  Note the **Extension ID** and ensure it matches the `EXTENSION_ID` in `install_host.sh`. If it differs, update the script and run it again.

## Usage
1.  Go to [drive.google.com](https://drive.google.com).
2.  Right-click any file or folder.
3.  Select **Reveal in Finder**.
4.  The corresponding file should be highlighted in a new Finder window.

## Debugging
The native host logs errors to `/tmp/drive_to_mac_debug.log`. If the extension fails to reveal a file, check this log for database query errors or path resolution issues.

## Limitations
*   Only supports macOS (due to `CloudStorage` path logic and `open -R` command).
*   Relies on the internal structure of Google Drive for Desktop's SQLite database, which may change in future updates.
