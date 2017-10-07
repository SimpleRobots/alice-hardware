from drive import Driver
from time import sleep
import socket
import threading
from ultrasonic import Sensor
import sys
import base64

HAS_CV = False
try:
    import cv2
    HAS_CV = True
except:
    print("HINT: You may want to install opencv to have camera support.")

IMAGE_RESOLUTION = (800, 600)
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
                elif cmd == "ai":
                    print("AI registered")
                    self.is_ai = True
                elif cmd == "drive" and self.is_human:
                    if self.parent.ai_mode:
                        print("Human stealing control")
                    self.parent.ai_mode = False
                    self.parent.d.stop_timeout = POLL_RATE_HZ / 2
                    self.parent.d.set_speed(int(parts[1]), int(parts[2]))
                    self.parent.send_all_ais(raw_cmd)
                elif cmd == "drive" and self.is_ai and self.parent.ai_mode:
                    self.parent.d.stop_timeout = POLL_RATE_HZ / 2
                    self.parent.d.set_speed(int(parts[1]), int(parts[2]))
                    self.parent.send_all_ais(raw_cmd)
                elif cmd == "reward":
                    print(raw_cmd)
                    self.parent.send_all_ais(raw_cmd)
                elif cmd == "ai_mode" and self.is_human:
                    print("Handing over to ai")
                    self.parent.ai_mode = True
                elif len(parts) == 6 and not self.is_ai and not self.is_human:
                    self.parent.send_all_ais("gps " + raw_cmd)

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
        self.stop_timeout = POLL_RATE_HZ / 2
        self.connections = []
        self.mark_for_removal = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))
        self.sock.listen(10)
        self.cap = None
        if HAS_CV:
            try:
                self.cap = cv2.VideoCapture(0)
            except:
                self.cap = None
                print("WARNING: Cannot open camera. Is one connected?")
        t = threading.Thread(target=self.accept_connection)
        t.daemon = True
        t.start()

    def sensor_loop(self):
        while True:
            # If no message for some time, stop.
            self.stop_timeout -= 1
            if self.stop_timeout < 0:
                self.d.set_speed(0, 0)
            
            # Measure ultrasonic
            measurement = self.sensor.poll()
            self.send_all("sense " + " ".join(('%.2f' % x) for x in measurement))

            # Send local position (odometry)
            local_pos = self.d.get_local_position(1.0 / POLL_RATE_HZ)
            self.send_all("pos %.3f %.3f %.3f %.3f" % local_pos)

            # Capture image from camera if availible
            if self.cap is not None:
                retval, img = cv2.read()
                img = cv2.resize(img, IMAGE_RESOLUTION)
                if retval:
                    _, img_encoded = cv2.imencode('.jpg', img)
                    jpg_as_text = base64.b64encode(img_encoded)
                    self.send_all("img " + jpg_as_text)
                else:
                    self.cap.release()
                    self.cap = None
                    print("WARNING: Connection to video capture lost.")

            # Wait for next cycle
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

    def kill(self):
        self.d.kill()
        if self.cap is not None:
            self.cap.release()


def main():
    api = HardwareNetworkAPI()
    try:
        api.sensor_loop()
    except:
        print("Stopping...")
    api.kill()

if __name__ == "__main__":
    main()
