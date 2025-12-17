import socket
import re
import hashlib
import shutil
import os
Host = "192.168.1.1"
Port = 5000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(Host,Port)
server.listen(1)
print("Server is waiting for Client...")
conn , adds = server.accept()
print("connected by", adds)