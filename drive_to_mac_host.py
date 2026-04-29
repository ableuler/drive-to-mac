#!/Users/ableuler/.local/bin/python3
import sqlite3
import os
import sys
import struct
import json
import re
import subprocess

# DEBUG: Log errors to a file since we can't use stdout
DEBUG_LOG = "/tmp/drive_to_mac_debug.log"

def log_debug(msg):
    try:
        with open(DEBUG_LOG, "a") as f:
            f.write(str(msg) + "\n")
    except:
        pass

# --- Core Logic ---

def get_drive_accounts():
    base_dir = os.path.expanduser("~/Library/Application Support/Google/DriveFS")
    accounts = []
    if not os.path.exists(base_dir):
        return accounts
    
    for entry in os.listdir(base_dir):
        db_path = os.path.join(base_dir, entry, "metadata_sqlite_db")
        if os.path.exists(db_path):
            email = None
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM properties WHERE property = 'driveway_account'")
                row = cursor.fetchone()
                if row and row[0]:
                    val = row[0]
                    if isinstance(val, bytes):
                        match = re.search(rb'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', val)
                        if match:
                            email = match.group(0).decode('utf-8')
                conn.close()
            except Exception as e:
                log_debug(f"Error reading account {entry}: {e}")
            accounts.append({'id': entry, 'db_path': db_path, 'email': email})
    return accounts

def find_cloud_storage_path(email):
    base_dir = os.path.expanduser("~/Library/CloudStorage")
    if not os.path.exists(base_dir):
        return None
    
    if email:
        target = f"GoogleDrive-{email}"
        path = os.path.join(base_dir, target)
        if os.path.exists(path):
            return path
            
    for entry in os.listdir(base_dir):
        if entry.startswith("GoogleDrive-"):
            return os.path.join(base_dir, entry)
    return None

def get_path_from_web_id(web_id):
    accounts = get_drive_accounts()
    
    for acc in accounts:
        db_path = acc['db_path']
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT stable_id FROM stable_ids WHERE cloud_id = ?", (web_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                continue
            
            target_stable_id = row[0]
            base_path = find_cloud_storage_path(acc['email'])
            if not base_path:
                conn.close()
                continue

            cursor.execute("SELECT value FROM properties WHERE property = 'root_id'")
            row = cursor.fetchone()
            root_cloud_id = row[0] if row else None
            if isinstance(root_cloud_id, bytes):
                root_cloud_id = root_cloud_id.decode('utf-8')

            root_stable_id = None
            if root_cloud_id:
                cursor.execute("SELECT stable_id FROM stable_ids WHERE cloud_id = ?", (root_cloud_id,))
                row = cursor.fetchone()
                root_stable_id = row[0] if row else None

            current_stable_id = target_stable_id
            path_components = []

            while True:
                cursor.execute("SELECT local_title, team_drive_stable_id FROM items WHERE stable_id = ?", (current_stable_id,))
                item_row = cursor.fetchone()
                if not item_row:
                    break
                
                local_title, team_drive_stable_id = item_row
                
                if current_stable_id == root_stable_id:
                    path_components.insert(0, "My Drive")
                    break
                
                cursor.execute("SELECT parent_stable_id FROM stable_parents WHERE item_stable_id = ?", (current_stable_id,))
                parent_row = cursor.fetchone()
                
                if not parent_row:
                    if team_drive_stable_id:
                        path_components.insert(0, local_title)
                        path_components.insert(0, "Shared drives")
                    else:
                        path_components.insert(0, local_title)
                    break
                
                path_components.insert(0, local_title)
                current_stable_id = parent_row[0]

            conn.close()
            return os.path.join(base_path, *path_components)
        except Exception as e:
            log_debug(f"Error in DB traversal: {e}")
            continue
    
    return None

# --- Native Messaging Wrapper ---

def send_message(message):
    try:
        encoded_message = json.dumps(message).encode('utf-8')
        sys.stdout.buffer.write(struct.pack('<I', len(encoded_message)))
        sys.stdout.buffer.write(encoded_message)
        sys.stdout.buffer.flush()
    except Exception as e:
        log_debug(f"Failed to send message: {e}")

def read_message():
    try:
        text_length_bytes = sys.stdin.buffer.read(4)
        if not text_length_bytes:
            return None
        text_length = struct.unpack('<I', text_length_bytes)[0]
        message = sys.stdin.buffer.read(text_length).decode('utf-8')
        return json.loads(message)
    except Exception as e:
        log_debug(f"Failed to read message: {e}")
        return None

def main_native():
    log_debug("Native Host session started.")
    WEB_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]+$')

    while True:
        message = read_message()
        if message is None:
            break
        
        web_id = message.get("web_id")
        if not web_id or not isinstance(web_id, str) or not WEB_ID_PATTERN.match(web_id):
            send_message({"status": "error", "message": "Invalid or missing web_id"})
            continue

        full_path = get_path_from_web_id(web_id)
        if full_path:
            try:
                subprocess.run(["open", "-R", full_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                send_message({"status": "success", "path": full_path})
            except Exception as e:
                send_message({"status": "error", "message": str(e)})
        else:
            send_message({"status": "error", "message": "Path not found"})

if __name__ == "__main__":
    # Chrome Native Messaging passes the origin as an argument (e.g. chrome-extension://...)
    # We only enter CLI mode if exactly one argument is passed and it looks like a Google ID.
    if len(sys.argv) == 2 and not sys.argv[1].startswith("chrome-extension://"):
        web_id = sys.argv[1]
        full_path = get_path_from_web_id(web_id)
        if full_path:
            print(full_path)
            subprocess.run(["open", "-R", full_path])
        else:
            print(f"Error: Could not find path for Web ID {web_id}")
            sys.exit(1)
    else:
        # Standard Native Messaging mode
        main_native()
