1. Teams & Direction
Team

Starting point

Goal

A-team

genesis protocol → full runtime / civic systems / foundations

Build everything behind the curtain: runtime, civic systems, registries, Public Works, Platform SDK. Make the “plumbing” work deterministically.

B-team

MVP experience → intent → capabilities

Build capabilities and experiences: implement intents, journeys, solutions using the Platform SDK, then expose them via the Experience SDK.

2. Intercept / Meeting point


The meeting point is the SDKs, not the intents themselves.



Platform SDK

Defines intent contracts (inputs, outputs, guarantees) so both teams can align.

Exposes runtime/civic systems to B-team in a controlled way.

Enforces hard invariants: B-team can’t access civic systems directly.



Experience SDK

Exposes capabilities implemented by B-team as experiences.

Enforces the invariant: consumers (experiences, dashboards, external apps) cannot see runtime internals.



Key idea: The intercept is the SDK boundary. Both teams build towards the same contracts, which allows them to work independently.

3. Intent Contracts
The Platform SDK owns and defines the intent contracts (what inputs, outputs, side-effects are allowed).

B-team implements the intents strictly according to these contracts.

Experience SDK wraps those intents for user-facing interaction.



Example MVP flow:

User triggers a capability in the Experience (e.g., ingest file).

Experience SDK calls the corresponding intent implementation.

Intent implementation (B-team code) uses Platform SDK to access runtime/civic systems.

Platform SDK enforces proper use and logging.

4. Visual Summary
         EXPERIENCE
         (User-facing UI, dashboards)
                |
                v
        +-----------------+
        | Experience SDK  |  <- governed, stable API for consumers
        +-----------------+
                |
                v
         INTENT CONTRACTS  <- defined by Platform SDK
                |
                v
        +-----------------+
        | Platform SDK    |  <- exposes runtime & civic systems
        +-----------------+
                |
                v
      RUNTIME / CIVIC SYSTEMS / FOUNDATIONS
      (Public Works, Curator, State, WAL, Identity)
Team A: Owns runtime/civic systems + Platform SDK.

Team B: Owns B-team intent implementations + wiring to Experience SDK.

Intercept: Intent contracts defined in Platform SDK, enforced in Experience SDK.

✅ Key Takeaways
Intent implementations are not the intercept. The intercept is the contract / SDK boundary.

Platform defines the contract, ensures consistency, provides SDK for B-team.

Experience SDK wraps B-team capabilities into user-facing experiences.

Teams work independently: A-team forward from runtime; B-team backward from MVP experience.