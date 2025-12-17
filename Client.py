import socket
import os

Host = "192.168.1.1"
Port = 5000
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(Host,Port)