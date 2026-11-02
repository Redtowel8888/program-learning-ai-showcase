# Architecture

## System boundary

The system separates four things:

- the **generic causal-learning core**: hypotheses, variables, actions, state,
  observations, relationships, evidence, confidence, rollback;
- **program-specific adapters**, which translate those concepts for one
  program;
- **observation and interaction providers**, the eyes and hands;
- **evidence and provenance**, including protected experimental inputs.

Names specific to the first target program (parameter tables, map files, game
locations) belong only in its adapter or its data. They never appear in the
core.

## Design decisions

Three accepted decision records shape the system.

### 1. Layered program interaction

Use direct data access first, then program/OS APIs, then Windows UI Automation,
and visual GUI automation last. Desktop-agent frameworks are evaluated as
replaceable providers. They execute or observe bounded actions but never become
the source of knowledge. Every action provider must return a structured trace
and a verification result.

### 2. Disposable experiment sandboxes

Experiments that could be destructive run only on verified disposable copies.
Each sandbox has a unique ID and a manifest listing the origin, size and
SHA-256 hash of every copied file. The authoritative manifest is stored outside
the folder the experiment can change. A protected baseline can produce child
sandboxes, so destructive changes never touch the baseline.

A folder named `copy` or `test` does not count as isolated. Only the manifest
and the configured sandbox root establish the boundary.

### 3. Isolated runtime save

Each runtime experiment gets its own save-file identity, and known existing
save formats are rejected. Creating a launch profile does not authorize
launching anything. Launching needs its own verified plan.

## Phase-aware measurement

A trial is split into phases: travel, arrival, investigation, abandonment,
departure. Physical events (the subject arrives) are stored separately from
behavioral ones (the subject starts investigating). This keeps navigation time
or animations from being mistaken for the effect a parameter controls.

Video timelines use the recording's frame clock and report one-frame timing
uncertainty explicitly. When the assisted tracker's confidence is low, it stops
and asks for human review rather than guessing.

## Confounder audit

Experiments declare which context variables must match between trials
(starting state, stimulus location, route, subject). Before a comparison, the
engine reports any mismatches and missing values. A comparison that fails the
audit can't earn high causal confidence.

## Persistence

v0.1 stores a versioned JSON knowledge document. JSON Schemas define the
interchange boundary, so storage can move to SQLite or a graph database later
without changing the experiment engine.

## Delivery phases

1. **Human-observed loop.** Direct imports, planned experiments, manual
   results, confidence updates. *(done)*
2. **Program data adapter.** Inspect, compare and safely stage data changes
   without the GUI. *(done for adapter #1)*
3. **Assisted execution.** OS/API and UI Automation steps.
4. **Visual observation and control.** A screenshot-based provider.
5. **Autonomous parallel experiments.** Isolated workers, with evidence merged
   centrally.
