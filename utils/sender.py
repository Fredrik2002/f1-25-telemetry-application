import socket
import pickle
import time
import sys

my_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
PORT = 20777
if len(sys.argv)>1:
    PORT = int(sys.argv[1])

with open('E:/Data_samples/F1 25/2025-06-01 17-47-20', 'rb') as file:
    b = pickle.load(file)
i=200_000

while True:
    i = (i + 1) % len(b)
    my_socket.sendto(b[i], ("127.0.0.1", PORT))
    time.sleep(0.001)