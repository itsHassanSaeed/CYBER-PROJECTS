import socket
import os
import hashlib

log_file = "logfile.txt"
#Creating File is not existed
os.makedirs("files" , exist_ok=True)
file_path = os.path.join("files",log_file)
with open(file_path, "w") as f:
    f.write("hello i am here!!")
file_size = os.path.getsize(file_path)
#Hashing file before sending
def hash_file(path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(4096)  # Read 4 KB at a time
            if not chunk:
                break
            sha256.update(chunk)

    return sha256.hexdigest()
file_hash = hash_file(log_file)

#establishing Connection

Host = "127.0.0.1"
Port = 5000

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((Host,Port))

#sending name of file,size and hash

metadata = f"{log_file}|{file_size}|{file_hash}"
client.sendall(metadata.encode())
ack = client.recv(1024)  # ACK from server
print(ack.decode())
#sending content of file
with open(file_path, "rb") as f:
    while chunk := f.read(4096):
        client.sendall(chunk)

print("File sent successfully")
client.close()