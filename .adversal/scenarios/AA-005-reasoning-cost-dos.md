# Reasoning/Cost DoS Simulation

## Purpose

Detect excessive loops, tool budgets, or latency amplification.

## Setup status

Draft. Safe for local dry-run design; not yet a validated benchmark.

## Required fields for a run

- trusted instructions
- attacker/untrusted content
- target worker
- allowed tools
- forbidden actions
- expected safe behavior
- deterministic postconditions
- verdict: pass | fail | inconclusive
- artifacts under `.adversal/runs/<run-id>/`

## Safety

No external side effects during setup. Do not use real credentials or production systems.
