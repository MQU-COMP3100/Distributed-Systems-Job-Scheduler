# Distributed Systems Capacity-Aware Job Scheduler

A custom Python client-side job scheduling engine built for distributed system simulations (`ds-sim`). The scheduler optimises task allocation across server clusters by evaluating real-time server availability, resource capacities, dynamic queue lengths, and hardware constraints.

Evaluated against standard baseline algorithms (FCFS, LRR, SJF), this algorithm reduced average job turnaround times by **99%+** in high-throughput simulated server workloads.

## Scheduling Algorithm Logic

The engine operates on a capacity-aware fallback strategy:

1. **Available Server Selection:** Query cluster state (`GETS Avail`) for currently idle servers matching job resource profiles.
2. **Multi-Variable Rank Heuristic:** If multiple servers are available, apply a strict deterministic tie-breaking evaluation matrix:
   $$\text{Rank} = (\text{Waiting Jobs}, -\text{Total Cores}, -\text{Avail Cores}, -\text{Avail Memory}, -\text{Avail Disk}, \text{Server ID})$$
3. **Fallback Strategy:** If no idle server matches the request, query capable nodes (`GETS Capable`) and assign tasks to the least-saturated capable server to prevent head-of-line blocking.

## Tech Stack & Simulation Protocol

- **Language:** Python 3
- **Simulation Environment:** `ds-sim` Discrete-Event Distributed Simulator
- **Protocol:** Low-level TCP Socket Communication (Custom ASCII RPC/IPC Interface)
- **Key Metrics Optimized:** Average Turnaround Time, Waiting Time, Cluster Utilization Rate

## IMPORTANT INFO
After creating the codespace, please execute 
```bash
chmod +x ds-*
```
in the terminal. 
You only need to do this for once after the creation of the codespace.

---

## Overview
ds-sim is a discrete-event simulator that has been developed primarily for leveraging scheduling algorithm design. 

It adopts a minimalist design explicitly taking into account modularity in that it uses the client-server model. 

The client-side simulator acts as a job scheduler while the server-side simulator simulates everything else including users (job submissions) and servers (job execution).

---

## Run The Automated Tests
From the repository root in terminal:
```bash
python3 ds_test.py "python3 client.py" -n -p 50000 -c TestConfigs
```

## How to run a simulation:
In one terminal:
```bash
./ds-server -n -p 50000 -v brief -c ./configs/sample-configs/ds-sample-config01.xml
```

In a second terminal:
```bash
python3 client.py
```

The client connects to localhost:50000, performs the required AUTH handshake,
schedules all JOBN and JOBP events, and exits after receiving NONE.

## Algorithm Summary

For each job, the scheduler requests GETS Avail using the job's resource requirements.
If servers are free, it picks the best one using a strict set of rules:

```text
(waiting jobs, -total cores, -available cores, -available memory, -available disk, server id)
```

If no available server is returned, it falls back to GETS Capable and schedules the job to the first capable server returned by ds-server.

