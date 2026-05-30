# COMP3100 Assignment 2 Scheduler

This repository contains the Python client-side scheduler for COMP3100 Assignment 2.
The implemented algorithm is AQLCF, an available-first lightweight capacity heuristic.

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

