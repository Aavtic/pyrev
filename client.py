import socket
import ssl
import argparse
import sys
import json
import threading
from math import ceil
from datetime import datetime


parser = argparse.ArgumentParser(description="Reverse Shell Client")
parser.add_argument("--ip", required=True,
                    help="IP Address of the server to connect to")
parser.add_argument("--port", required=False, default=8081,
                    help="PORT to listen on. if not specified port 8081 will be used")
parser.add_argument("--cafile", required=False, default="./cert.pem",
                    help="The Certificate file of the server.\
                            If not specified ./cert.pem will be used\
                            assuming it exists.")
parser.add_argument("--nocolors", action=argparse.BooleanOptionalAction)

class Buffer:
    def __init__(self, buff_size: int):
        self.buffer_size = buff_size

    def to_buffers(self, data: str) -> [[str]]:
        buffer = ['\0']*self.buffer_size
        res = []

        if len(data) < len(buffer):
            for i in range(len(data)):
                buffer[i] = data[i]

            res.append(buffer)
            return res
        else:
            n = ceil(len(data) / self.buffer_size)
            idx = 0
            for i in range(n):
                buffer = ['\0']*self.buffer_size
                idx = i * self.buffer_size
                for (i, e) in enumerate(data[idx:idx+self.buffer_size]):
                    buffer[i] = e
                res.append(buffer)
            return res


class Client:
    def __init__(self, ip: str, port: int, cert_file: str, colorable: None | bool):

        self.colorable = colorable
        self.bufferRW = Buffer(64)
        self.std_msg = {
                "data": "",
                "time": "",
        }
        self.time_color = "\033[92;49m"
        self.reset_color = "\033[0m"

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=cert_file)

        with socket.create_connection((ip, port)) as self.s:
            with context.wrap_socket(self.s, server_hostname="localhost") as self.ss:
                print("[+] Connected")
                self.session(self.ss)

    def close_all_connections(self):
        try:
            self.s.close()
            self.ss.close()
        except:
            return

    def active_receiver(self, conn):
        buff = ""

        while msg := conn.recv(64):
            try:
                msg_d = msg.decode('utf-8')
                msg_d = msg_d.split("\0")[0]
                msg_d = buff + msg_d
                json_msg = json.loads(msg_d)
            except:
                msg_d = msg.decode('utf-8')
                buff += msg_d
                continue

            message = json_msg["data"]
            time = json_msg["time"]
            if message != "\n":
                if time:
                    message = (self.time_color if not self.colorable else "") + time + (self.reset_color if not self.colorable else "") + " :" + message
                sys.stdout.write(message)
                sys.stdout.flush()
            buff = ""

        self.close_all_connections()
        print("connection closed")

    def send_msg(self, conn, msg):
        whole_msg = self.std_msg.copy()
        current_time = datetime.now()
        ctime = datetime.strftime(current_time, "%H:%M:%S")
        whole_msg["data"] = msg
        whole_msg["time"] = ctime
        json_msg = json.dumps(whole_msg)
        buffers = self.bufferRW.to_buffers(json_msg)

        for buff in buffers:
            buff_str = ''.join(buff)
            conn.send(buff_str.encode('utf-8'))

    def session(self, ss):
        thread = threading.Thread(target=self.active_receiver, args=(ss,))
        thread.daemon = True
        thread.start()

        while True:
            try:
                user_input = input()
            except KeyboardInterrupt:
                print("[-] Closing connection...")
                try:
                    self.close_all_connections()
                except:
                    pass
                print("[-] Closed")
                sys.exit(0)

            self.send_msg(ss, user_input + "\n")


if __name__ == "__main__":
    args = parser.parse_args()
    ip = args.ip
    port = int(args.port)
    cafile = args.cafile
    colorable = args.nocolors

    Client(ip, port, cafile, colorable)
