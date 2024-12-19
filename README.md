# Python Cross platform Reverse shell server and client with TLS/SSL security. 



## Usage

usage: server.py [-h] [--ip IP] [--port PORT] [--cafile CAFILE]
                 [--private-key PRIVATE_KEY]

Reverse Shell Server

options:
  -h, --help            show this help message and exit
  --ip IP               IP address to host the reverse shell server. If not
                        specified will use address 0.0.0.0.
  --port PORT           PORT to listen on.
  --cafile CAFILE       The CA Certificate file for the server Caution: If not
                        given ./cert.pem will be used as default assuming it
                        exists
  --private-key PRIVATE_KEY
                        The Private Key for the server. If not mentioned
                        ./private.key file will be used assuming it exists.


usage: client.py [-h] --ip IP [--port PORT] [--cafile CAFILE]

Reverse Shell Client

options:
  -h, --help       show this help message and exit
  --ip IP          IP Address of the server to connect to
  --port PORT      PORT to listen on. if not specified port 8081 will be used
  --cafile CAFILE  The Certificate file of the server. If not specified
                   ./cert.pem will be used assuming it exists.
