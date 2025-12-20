import socket
import re
import hashlib
import shutil
import os
Host = "127.0.0.1"
Port = 5000

def hash_file(path):
    sha = hashlib.sha256()
    with open(path,"rb") as f:
        while chunk := f.read(4096):
            sha.update(chunk)
        return sha.hexdigest()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((Host,Port))
server.listen(1)
print("Server is waiting for Client...")
conn , adds = server.accept()
print("connected by", adds)
metadata = conn.recv(1024).decode()
filename,filesize,client_hash = metadata.split("|")
filesize = int(filesize)
conn.send(b"ok")

os.makedirs("incomingFiles",exist_ok=True)
log_file_path = os.path.join("incomingFiles", "log_file.txt")
received = 0
with open(log_file_path,"wb") as f:
    while received < filesize:
        data = conn.recv(4096)
        if not data:
            break
        f.write(data)
        received += len(data)


        #verify hash
server_hash = hash_file(log_file_path)
if server_hash == client_hash:
    print("File integrity verified")
else:
    print("Warning: Hash mismatched")
#file backup
backup_file_path = os.path.join("incomingFiles", "backup_file.txt")
shutil.copy2(log_file_path,backup_file_path)

