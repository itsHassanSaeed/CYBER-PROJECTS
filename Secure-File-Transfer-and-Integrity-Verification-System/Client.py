import socket
import os
import hashlib
import logging
import time

# ================= CONFIG =================
HOST = "127.0.0.1"
PORT = 5000
AUTH_TOKEN = "SECURE_TOKEN_123"
BUFFER_SIZE = 4096
FILE_DIR = "clientFiles"
FILENAME = "logfile.txt"

os.makedirs(FILE_DIR, exist_ok=True)

# ================= LOGGING =================
logging.basicConfig(
    filename="client.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ================= FILE CREATION =================
file_path = os.path.join(FILE_DIR, FILENAME)

if not os.path.exists(file_path):
    with open(file_path, "w") as f:
        f.write("Hello from secure client.\n")
    logging.info("File created on client side")

file_size = os.path.getsize(file_path)

# ================= HASH FUNCTION =================
def hash_file(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(BUFFER_SIZE):
            sha.update(chunk)
    return sha.hexdigest()

file_hash = hash_file(file_path)

# ================= CLIENT CONNECTION =================
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(10)

try:
    client.connect((HOST, PORT))
    logging.info("Connected to server")

    # ---------- AUTH ----------
    client.send(AUTH_TOKEN.encode())
    response = client.recv(1024)

    if response != b"AUTH_OK":
        logging.error("Authentication failed")
        client.close()
        exit()

    # ---------- METADATA ----------
    metadata = f"{FILENAME}|{file_size}|{file_hash}"
    client.send(metadata.encode())

    ack = client.recv(1024)
    if ack != b"OK":
        logging.error("Server rejected metadata")
        client.close()
        exit()

    # ---------- SEND FILE ----------
    with open(file_path, "rb") as f:
        while chunk := f.read(BUFFER_SIZE):
            client.sendall(chunk)

    logging.info("File sent successfully")

    # ---------- SERVER RESPONSE ----------
    server_response = client.recv(1024).decode()
    logging.info(f"Server response: {server_response}")
    print("Server:", server_response)

except socket.timeout:
    logging.error("Connection timed out")
except Exception as e:
    logging.error(f"Client error: {e}")
finally:
    client.close()
    logging.info("Client connection closed")
