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

send("AUTH chicken")  # Replace myName with your name/team name
receive()

send("QUIT")
receive()


sock.close()
