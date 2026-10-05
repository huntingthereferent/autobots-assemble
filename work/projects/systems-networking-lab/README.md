# Systems / Networking Lab — Evidence Build

## Referent

Build one direct networking witness over owned/local interfaces.

This project proves socket-level behavior without using HTTP frameworks, cloud services, or third-party hosts as substitutes for networking evidence.

## First slice

A local TCP service and client using an explicit length-prefixed binary frame:

```text
4-byte big-endian payload length
→ payload bytes
```

The server returns the same payload as an echo response. The client records timing and failure state.

## Ability witness

The project must prove:

- TCP server bind/listen/accept behavior;
- TCP client connect/send/receive behavior;
- explicit message framing over a byte stream;
- partial-read-safe receive logic;
- multiple sequential requests over one connection;
- measurable round-trip latency;
- measurable payload throughput;
- connection-refused classification;
- read-timeout classification;
- automated clean-environment tests.

## Boundary

All targets are loopback/local test servers created by this project.

Passing this closes a first **Systems / Networking** witness. It does not claim enterprise network administration, third-party network operations, packet-routing design, or offensive network testing.
