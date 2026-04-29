import socket

PORT = 50000
VERBOSE = True
BUF_SIZE = 8192

sock = socket.socket()
sock.settimeout(10)
sock.connect(("localhost", PORT))

def receive() -> str:
    data = b""
    
    while True:
        try:
            part = sock.recv(BUF_SIZE)
        except (TimeoutError, socket.timeout):
            break
            data += part
            if len(part) < BUF_SIZE: # Check if reached end of message
                break
            
    message = data.decode().strip()
    if VERBOSE:
        print("Received:", message)
    return message

def send(message: str):
    if VERBOSE:
        print("Sent:", message)
    sock.sendall(bytes(f"{message}\n", encoding="utf-8"))

send("HELO")
receive()

<<<<<<< HEAD
send("AUTH chicken")  # Replace myName with your name/team name
receive()

send("QUIT")
receive()


sock.close()
=======
send("AUTH chicken")
receive()

send("READY")
message = receive()

if message == "NONE":
        send("QUIT")
        receive()

sock.close()
>>>>>>> 95d7fb5 (Co-authored-by: Tanvir <TanvirS-07@users.noreply.github.com>)
