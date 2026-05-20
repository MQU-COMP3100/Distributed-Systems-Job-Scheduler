#!/usr/bin/env python3
import os
import socket
import time
import xml.etree.ElementTree as ET

HOST = "localhost"
PORT = 50000
AUTH_NAME = "chicken"


class DSClient:
    def __init__(self):
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))
        self.reader = self.sock.makefile("r", encoding="utf-8", newline="\n")

    def send(self, message):
        self.sock.sendall((message + "\n").encode("utf-8"))

    def receive(self):
        msg = self.reader.readline()
        if not msg:
            raise RuntimeError("Server closed connection")
        return msg.strip()

    def close(self):
        self.reader.close()
        self.sock.close()


def load_specs():
    for _ in range(20):
        if os.path.exists("ds-system.xml"):
            root = ET.parse("ds-system.xml").getroot()
            specs = {}
            for s in root.findall(".//server"):
                specs[s.attrib["type"]] = {
                    "limit": int(s.attrib.get("limit", 1)),
                    "boot": int(s.attrib.get("bootupTime", 60)),
                    "rate": float(s.attrib.get("hourlyRate", 1.0)),
                    "cores": int(s.attrib.get("cores", 1)),
                    "memory": int(s.attrib.get("memory", 1)),
                    "disk": int(s.attrib.get("disk", 1)),
                }
            return specs
        time.sleep(0.1)
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
    resp = client.receive()
    data = resp.split()

    if data[0] == "NONE" or int(data[1]) == 0:
        client.send("OK")
        client.receive()
        return []

    count = int(data[1])
    client.send("OK")
    servers = [parse_server(client.receive()) for _ in range(count)]
    client.send("OK")
    client.receive()
    return servers


def choose_server(servers, specs):
    def spec(s, key, fb): return specs.get(s["type"], {}).get(key, fb)
    def full_cores(s): return spec(s, "cores", s["avail_cores"])

    # No queue first, then biggest cores, then lowest id
    return min(servers, key=lambda s: (s["waiting"], -full_cores(s), s["id"]))


def main():
    client = DSClient()

    client.send("HELO")
    client.receive()

    client.send(f"AUTH {AUTH_NAME}")
    client.receive()

    specs = load_specs()

    while True:
        client.send("REDY")
        msg = client.receive()

        if msg == "NONE":
            break

        parts = msg.split()

        if parts[0] in ("JOBN", "JOBP"):
            job = {
                "id": int(parts[1]),
                "submit": int(parts[2]),
                "cores": int(parts[3]),
                "memory": int(parts[4]),
                "disk": int(parts[5]),
                "runtime": int(parts[6]),
            }

            servers = get_servers(client, "Avail", job["cores"], job["memory"], job["disk"])

            if not servers:
                servers = get_servers(client, "Capable", job["cores"], job["memory"], job["disk"])
                server = servers[0]
            else:
                server = choose_server(servers, specs)

            client.send(f"SCHD {job['id']} {server['type']} {server['id']}")
            client.receive()

    client.send("QUIT")
    client.receive()
    client.close()


if __name__ == "__main__":
    main()
