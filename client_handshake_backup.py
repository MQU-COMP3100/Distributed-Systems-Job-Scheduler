#!/usr/bin/env python3
import socket

HOST = "localhost"
PORT = 50000
AUTH_NAME = "chicken"

BUF_SIZE = 8192
VERBOSE = False


class DSClient:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))
        self.reader = self.sock.makefile("r", encoding="utf-8", newline="\n")

    def send(self, message: str):
        if VERBOSE:
            print("Sent:", message)
        self.sock.sendall((message + "\n").encode("utf-8"))

    def receive(self) -> str:
        message = self.reader.readline()
        if not message:
            return ""
        message = message.strip()
        if VERBOSE:
            print("Received:", message)
        return message

    def close(self):
        self.reader.close()
        self.sock.close()


def choose_server(servers):
    """
    Basic working scheduler:
    choose the capable server with the smallest number of waiting/running jobs.
    Tie-break by smaller server size to avoid wasting huge servers.
    """
    return min(
        servers,
        key=lambda s: (
            s["waiting_jobs"] + s["running_jobs"],
            s["cores"],
            s["memory"],
            s["disk"],
        ),
    )


def main():
    client = DSClient()

    client.send("HELO")
    client.receive()

    client.send(f"AUTH {AUTH_NAME}")
    client.receive()

    while True:
        client.send("REDY")
        message = client.receive()

        if message == "NONE":
            break

        parts = message.split()
        command = parts[0]

        if command == "JOBN":
            job_id = int(parts[2])
            cores = int(parts[4])
            memory = int(parts[5])
            disk = int(parts[6])

            client.send(f"GETS Capable {cores} {memory} {disk}")
            data_message = client.receive()

            data_parts = data_message.split()
            server_count = int(data_parts[1])

            client.send("OK")

            servers = []
            for _ in range(server_count):
                server_line = client.receive()
                server_parts = server_line.split()

                servers.append({
                    "type": server_parts[0],
                    "id": int(server_parts[1]),
                    "state": server_parts[2],
                    "start_time": int(server_parts[3]),
                    "cores": int(server_parts[4]),
                    "memory": int(server_parts[5]),
                    "disk": int(server_parts[6]),
                    "waiting_jobs": int(server_parts[7]),
                    "running_jobs": int(server_parts[8]),
                })

            client.send("OK")
            client.receive()  # receives "."

            chosen = choose_server(servers)
            client.send(f"SCHD {job_id} {chosen['type']} {chosen['id']}")
            client.receive()

        elif command == "JCPL":
            continue

        else:
            continue

    client.send("QUIT")
    client.receive()
    client.close()


if __name__ == "__main__":
    main()
