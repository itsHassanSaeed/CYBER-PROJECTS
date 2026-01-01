import socket
import os
import hashlib
import shutil
import subprocess
import threading
import logging
import re

# ================= CONFIG =================
HOST = "127.0.0.1"
PORT = 5000
AUTH_TOKEN = "SECURE_TOKEN_123"
BUFFER_SIZE = 4096
SAVE_DIR = "incomingFiles"

os.makedirs(SAVE_DIR, exist_ok=True)

# ================= LOGGING =================
logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s"
)

# ================= HASH FUNCTION =================
def hash_file(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            sha.update(chunk)
    return sha.hexdigest()

# ================= CLIENT HANDLER =================
def handle_client(conn, addr):
    logging.info(f"Connection from {addr}")
    conn.settimeout(10)

    try:
        # ---------- AUTH ----------
        token = conn.recv(1024).decode()
        if token != AUTH_TOKEN:
            logging.warning(f"Auth failed from {addr}")
            conn.send(b"AUTH_FAILED")
            return

        conn.send(b"AUTH_OK")

        # ---------- METADATA ----------
        metadata = conn.recv(1024).decode()
        filename, filesize, client_hash = metadata.split("|")
        filesize = int(filesize)

        if not re.fullmatch(r"[a-zA-Z0-9_]+\.(txt|log)", filename):
            logging.warning(f"Invalid filename from {addr}: {filename}")
            conn.send(b"INVALID_FILENAME")
            return

        conn.send(b"OK")

        # ---------- RECEIVE FILE ----------
        file_path = os.path.join(SAVE_DIR, filename)
        received = 0

        with open(file_path, "wb") as f:
            while received < filesize:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                f.write(data)
                received += len(data)

        logging.info(f"File received: {filename} ({filesize} bytes)")

        # ---------- BACKUP ----------
        backup_path = os.path.join(SAVE_DIR, f"backup_{filename}")
        shutil.copy2(file_path, backup_path)
        logging.info(f"Backup created for {filename}")

        # ---------- SYSTEM COMMAND ----------
        subprocess.run(
            ["dir" if os.name == "nt" else "ls", SAVE_DIR],
            shell=True
        )

        # ---------- INTEGRITY CHECK ----------
        server_hash = hash_file(file_path)
        if server_hash == client_hash:
            logging.info(f"Integrity verified for {filename}")
            conn.send(b"TRANSFER_SUCCESS")
        else:
            logging.error(f"Hash mismatch for {filename}")
            conn.send(b"HASH_MISMATCH")

    except socket.timeout:
        logging.warning(f"Timeout from {addr}")
    except Exception as e:
        logging.error(f"Error with {addr}: {e}")
    finally:
        conn.close()
        logging.info(f"Connection closed: {addr}")

# ================= SERVER SETUP =================
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

logging.info(f"Server running on {HOST}:{PORT}")
print("Server is running...")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(
        target=handle_client,
        args=(conn, addr),
        daemon=True
    )
    thread.start()
    logging.info(f"Active connections: {threading.active_count() - 1}")