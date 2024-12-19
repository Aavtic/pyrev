# Python Cross platform Reverse shell server and client with TLS/SSL security. 



## Setup

To setup the enviornment for the server/client. we need to generate the CA certificate (for both client and server) and private keys (for the server).
These files are used for TLS/SSL session. Which ensures data security and integrity.
Let's set them up!

### CA certificate and private key generateion

#### Recommended way

You can generate the CA Certificate and the private key using the `ssl_cert_key_gen.py` file.
Run the file using python.

```shell
    python3 ssl_cert_key_gen.py
```
It will ask you some questions to generate the certificate. After answering all the questions your certificate and keys will be generated!

The CA Certificate is **Self-Signed** and will be `./cert.pem` and the private key will be `./private.key`.

#### Note
You can create the certificate and keys by using [`openssl`](https://snyk.io/blog/implementing-tls-ssl-python/).

### Running the server & client.

#### Server
To run the server you can run the following command.

```shell
    python3 server.py
```
Now the server will be listening on all interfaces **`(0.0.0.0)`*** and on default port `8081`
** CAUTION ***
The server can accept connections from any interfaces.

To run the server with separate address and port you can specify `--ip` and `--port`.
```shell
    python3 server.py --ip <ip> --port <port>
```

#### Client

To run the client you can run the following command

```shell
    python3 client.py --ip <ip> <port>
```

Here `<ip>` should be the ip-address of the server and `<port>` should be the port the server is listening.

### Additional parameters

#### Custom CA file and private key file (server)

You can use the `--cafile` tag to specify the custom CA file using it's location and similarly the `--private-key` argument for the private key.

#### Switch off colored output

By default in the `chatting` mode the time-stamps will be colored (light-green).
If you want to disable this you can use the `--nocolors` tag to only print in the default color of your terminal.

# Features

* TLS/SSL Encrypted traffic
* Multi Language chat support
* Cross Platform Support

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

