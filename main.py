from drive import Driver
from time import sleep
import socket
import threading
from ultrasonic import Sensor
import sys

HOST = "0.0.0.0"
PORT = 2323
POLL_RATE_HZ = 10

class Connection(object):
    def __init__(self, socket, parent):
        self.is_ai = False
        self.is_human = False
        self.sock = socket
        self.fsock = socket.makefile()
        self.parent = parent
        t = threading.Thread(target=self.receive)
        t.daemon = True
        t.start()

    def receive(self):
        while True:
            try:
                raw_cmd = self.fsock.readline().replace("\n", "")
                parts = raw_cmd.split(" ")
                cmd = parts[0]
                if cmd == "human":
                    print("Human registered")
                    self.is_human = True
                if cmd == "ai":
                    print("AI registered")
                    self.is_ai = True
                if cmd == "drive" and self.is_human:
                    if self.parent.ai_mode:
                        print("Human stealing control")
                    self.parent.ai_mode = False
                    self.parent.d.set_speed(int(parts[1]), int(parts[2]))
                    self.parent.send_all_ais(raw_cmd)
                if cmd == "drive" and self.is_ai and self.parent.ai_mode:
                    self.parent.d.set_speed(int(parts[1]), int(parts[2]))
                    self.parent.send_all_ais(raw_cmd)
                if cmd == "reward":
                    print(raw_cmd)
                    self.parent.send_all_ais(raw_cmd)
                if cmd == "ai_mode" and self.is_human:
                    print("Handing over to ai")
                    self.parent.ai_mode = True
            except:
                break

    def send(self, msg):
        try:
            self.sock.send(msg + "\n")
        except:
            print("Human disconnected")
            self.parent.disconnected(self)
    
    def send_to_human(self, msg):
        if self.is_human:
            try:
                self.sock.send(msg + "\n")
            except:
                print("Human disconnected")
                self.parent.disconnected(self)
    
    def send_to_ai(self, msg):
        if self.is_ai:
            try:
                self.sock.send(msg + "\n")
            except:
                print("AI disconnected")
                self.parent.disconnected(self)


class HardwareNetworkAPI(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.d = Driver()
        self.sensor = Sensor()
        self.ai_mode = True
        self.connections = []
        self.mark_for_removal = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))
        self.sock.listen(10)
        t = threading.Thread(target=self.accept_connection)
        t.daemon = True
        t.start()

    def sensor_loop(self):
        while True:
            measurement = self.sensor.poll()
            self.send_all("sense " + " ".join(('%.2f' % x) for x in measurement))
            sleep( 1.0 / POLL_RATE_HZ )

    def accept_connection(self):
        while True:
            (clientsocket, address) = self.sock.accept()
            self.connections.append(Connection(clientsocket, self))
            print("Client connected")
            sys.stdout.flush()

    def disconnected(self, conn):
        self.mark_for_removal.append(conn)

    def send_all(self, msg):
        self.lock.acquire()
        for x in self.connections:
            x.send(msg)
        for x in self.mark_for_removal:
            self.connections.remove(x)
        self.mark_for_removal = []
        self.lock.release()

    def send_all_ais(self, msg):
        self.lock.acquire()
        for x in self.connections:
            x.send_to_ai(msg)
        for x in self.mark_for_removal:
            self.connections.remove(x)
        self.mark_for_removal = []
        self.lock.release()

    def send_all_humans(self, msg):
        self.lock.acquire()
        for x in self.connections:
            x.send_to_human(msg)
        for x in self.mark_for_removal:
            self.connections.remove(x)
        self.mark_for_removal = []
        self.lock.release()


def main():
    api = HardwareNetworkAPI()
    try:
        api.sensor_loop()
    except:
        print("Stopping...")
    api.d.kill()

if __name__ == "__main__":
    main()
