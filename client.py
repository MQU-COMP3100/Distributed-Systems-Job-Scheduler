import socket

PORT = 50000
VERBOSE = True
BUF_SIZE = 8192

sock = socket.socket()
sock.settimeout(10)
sock.connect(("localhost", PORT))

def receive() -> str:
    data = sock.recv(BUF_SIZE)
    message = data.decode("utf-8").strip()

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
