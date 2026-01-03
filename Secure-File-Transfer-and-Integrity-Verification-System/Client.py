import socket
import os
import hashlib
import argparse
import logging

# ---------------- ARGPARSE ----------------
parser = argparse.ArgumentParser(description="Secure File Transfer Client")
parser.add_argument("--host", required=True, help="Server address")
parser.add_argument("--port", type=int, required=True, help="Server port")
parser.add_argument("--file", required=True, help="File to send")
parser.add_argument("--token", required=True, help="Authentication token")

args = parser.parse_args()

HOST = args.host
PORT = args.port
FILE = args.file
TOKEN = args.token
FILE_DIR = "clientFiles"
os.makedirs(FILE_DIR, exist_ok=True)

# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="client.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
# ================= FILE CREATION =================
file_path = os.path.join(FILE_DIR, FILE)

if not os.path.exists(file_path):
    with open(file_path, "w") as f:
        f.write("Hello from secure client.\n")
    logging.info("File created on client side")

file_size = os.path.getsize(file_path)


# ---------------- HASHING ----------------
def hash_file(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            sha.update(chunk)
    return sha.hexdigest()

filesize = os.path.getsize(file_path)
filehash = hash_file(file_path)
filename = os.path.basename(file_path)

# ---------------- CLIENT CONNECT ----------------
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

#----------------  Send token first ----------------
client.sendall(TOKEN.encode())
response = client.recv(1024)
if response != b"AUTH_OK":
    print("Auth failed")
    client.close()
    exit()

metadata = f"{filename}|{filesize}|{filehash}"
client.sendall(metadata.encode())

response = client.recv(1024)
if response != b"OK":
    logging.error("Authentication failed")
    client.close()
    exit()

with open(file_path, "rb") as f:
    while chunk := f.read(4096):
        client.sendall(chunk)

logging.info(f"File sent successfully: {filename}")
client.close()
