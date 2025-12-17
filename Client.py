import socket
import os

log_file = "logfile.txt"

os.makedirs("files" , exist_ok=True)
file_path = os.path.join("files",log_file)

Host = "192.168.1.1"
Port = 5000
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(Host,Port)