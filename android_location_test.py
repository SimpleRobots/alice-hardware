import socket

HOST = "0.0.0.0"
PORT = 2323


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
print("Listening")
try:
    while True:
        conn, addr = s.accept()
        print("Connected by", addr)
        fconn = conn.makefile()
        while True:
            line = fconn.readline().rstrip()
            if line is "": break
            print(line)
            tokens = line.split(" ")
            print("Lat: " + tokens[0])
            print("Lon: " + tokens[1])
            print("Alt: " + tokens[2])
            print("Acc: " + tokens[5])
        fconn.close()
        conn.close()
        print("Connection lost")
except KeyboardInterrupt:
    print("User stopped server.")
    s.close()