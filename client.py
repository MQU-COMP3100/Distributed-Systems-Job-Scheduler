#!/usr/bin/env python3
import os
import socket
import time
import xml.etree.ElementTree as ET

HOST = "localhost"
PORT = 50000
AUTH_NAME = "chicken"
SPEC_LOAD_RETRIES = 20
SPEC_LOAD_DELAY = 0.1
DEFAULT_SERVER_LIMIT = 1
DEFAULT_BOOT_TIME = 60
DEFAULT_HOURLY_RATE = 1.0
DEFAULT_RESOURCE = 1


class DSClient:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))
        self.reader = self.sock.makefile("r", encoding="utf-8", newline="\n")

    def send(self, message):
        self.sock.sendall((message + "\n").encode("utf-8"))

    def receive(self):
        message = self.reader.readline()
        if not message:
            raise RuntimeError("Server closed connection")
        return message.strip()

    def close(self):
        self.reader.close()
        self.sock.close()


def load_server_specs():
    for _ in range(SPEC_LOAD_RETRIES):
        if os.path.exists("ds-system.xml"):
            root = ET.parse("ds-system.xml").getroot()
            specs = {}
            for selected_server in root.findall(".//server"):
                specs[selected_server.attrib["type"]] = {
                    "limit": int(selected_server.attrib.get("limit", DEFAULT_SERVER_LIMIT)),
                    "boot": int(selected_server.attrib.get("bootupTime", DEFAULT_BOOT_TIME)),
                    "rate": float(selected_server.attrib.get("hourlyRate", DEFAULT_HOURLY_RATE)),
                    "cores": int(selected_server.attrib.get("cores", DEFAULT_RESOURCE)),
                    "memory": int(selected_server.attrib.get("memory", DEFAULT_RESOURCE)),
                    "disk": int(selected_server.attrib.get("disk", DEFAULT_RESOURCE)),
                }
            return specs
        time.sleep(SPEC_LOAD_DELAY)
    return {}


def parse_server(line):
    p = line.split()
    return {
        "type": p[0],
        "id": int(p[1]),
        "state": p[2],
        "avail_cores": int(p[4]),
        "avail_memory": int(p[5]),
        "avail_disk": int(p[6]),
        "waiting": int(p[7]),
        "running": int(p[8]),
    }


def get_servers(client, query, cores, memory, disk):
    client.send(f"GETS {query} {cores} {memory} {disk}")
    response = client.receive()
    data = response.split()

    if data[0] == "NONE" or int(data[1]) == 0:
        client.send("OK")
        client.receive()
        return []

    server_count = int(data[1])
    client.send("OK")
    servers = [parse_server(client.receive()) for _ in range(server_count)]
    client.send("OK")
    client.receive()
    return servers


def choose_best_server(servers, specs):
    def server_specs(server, key, fallback_value):
        return specs.get(server["type"], {}).get(key, fallback_value)

    def total_server_cores(server):
        return server_specs(server, "cores", server["avail_cores"])

    return min(
        servers,
        key=lambda server: (
            server["waiting"],
            -total_server_cores(server),
            -server["avail_cores"],
            -server["avail_memory"],
            -server["avail_disk"],
            server["id"],
        ),
    )


def main():
    client = DSClient()

    client.send("HELO")
    client.receive()

    client.send(f"AUTH {AUTH_NAME}")
    client.receive()

    specs = load_server_specs()

    while True:
        client.send("REDY")
        message = client.receive()

        if message == "NONE":
            break

        message_fields = message.split()

        if message_fields[0] in ("JOBN", "JOBP"):
            job = {
                "id": int(message_fields[1]),
                "submit": int(message_fields[2]),
                "cores": int(message_fields[3]),
                "memory": int(message_fields[4]),
                "disk": int(message_fields[5]),
                "runtime": int(message_fields[6]),
            }

            servers = get_servers(
                client, "Avail", job["cores"], job["memory"], job["disk"]
                )

            if not servers:
                servers = get_servers(
                    client, "Capable", job["cores"], job["memory"], job["disk"]
                    )
                selected_server = servers[0]
            else:
                selected_server = choose_best_server(servers, specs)

            client.send(
                f"SCHD {job['id']} {selected_server['type']} {selected_server['id']}"
                )
            client.receive()

    client.send("QUIT")
    client.receive()
    client.close()

if __name__ == "__main__":
    main()