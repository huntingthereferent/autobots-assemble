# Embedded Systems Lab — AVR Firmware Evidence

## Referent

Build the first non-application software witness in the ability stack:

**firmware logic → target microcontroller build → deterministic simulation → inspectable output**

Target:
- ATmega328P
- AVR-GCC toolchain

## First behavior

A debounced pushbutton toggles an LED.

Hardware mapping:
- button input: PD2
- LED output: PB5
- timer tick: 1 ms

The core controller logic is isolated from hardware register access so the exact same state machine can be exercised deterministically in a host simulation while the hardware adapter is compiled with the real AVR target toolchain.

## Acceptance

- AVR firmware compiles for `atmega328p`;
- Intel HEX image is produced;
- firmware size is inspectable;
- 1 ms timer ISR drives the controller;
- simulated switch bounce does not produce multiple toggles;
- one stable press toggles LED once;
- release + second press toggles it back;
- CI builds both AVR target and simulator;
- simulator assertions pass.

## Evidence boundary

Passing this establishes a firmware/toolchain/simulation witness.

It does **not** claim:
- physical board operation;
- oscilloscope/logic-analyzer measurement;
- electrical design;
- PCB design;
- hardware debugging.

Those require physical evidence later.
