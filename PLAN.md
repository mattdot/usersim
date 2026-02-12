# UserSim Implementation Plan

## Overview

This plan defines the implementation priorities and build order for UserSim. It is derived from the [SPEC.md](SPEC.md) and organizes the spec's functionality into tiers based on what is core versus incremental versus aspirational.

---

## Tier 1 — Core (UserSim doesn't exist without these)

These are the irreducible components. Without any one of them, UserSim cannot perform its basic function of testing an agent.

### Step 1: Conversation Loop

**Goal**: UserSim can connect to a target agent, exchange messages, and terminate.

- [ ] Connect to a target agent via the A2A (Agent-to-Agent) protocol
- [ ] Discover the target agent's capabilities via its A2A Agent Card
- [ ] Send a message to the target agent and receive a response over A2A
- [ ] Maintain conversation history across turns
- [ ] Enforce a max turn limit so every conversation terminates
- [ ] Handle errors from the target agent gracefully (timeout, connection failure, malformed response)

**Done when**: UserSim can have a multi-turn A2A conversation with a target agent and stop after N turns.

### Step 2: Objective-Driven Message Generation

**Goal**: Each message UserSim sends is a purposeful step toward a defined goal, not random chatter.

- [ ] Define the system configuration schema (model provider, model name, hyperparameters: temperature, top_p, max_tokens, etc.)
- [ ] Load system config at startup — these settings apply to all tests uniformly
- [ ] Accept a goal statement and success criteria as input
- [ ] Construct a system prompt that instructs the LLM to pursue the objective
- [ ] Use an LLM to generate each user message, guided by the objective and conversation history
- [ ] Include conversation history in LLM context so messages are coherent across turns

**Done when**: Given an objective like "book a flight from Seattle to New York", UserSim generates realistic, goal-directed messages using settings from system config.

### Step 3: Objective Evaluation & Termination

**Goal**: UserSim knows when to stop and whether the objective was achieved.

- [ ] After each agent response, evaluate progress against each success criterion
- [ ] Implement termination conditions:
  - Success — all criteria met
  - Failure — max turns reached
  - Abandonment — no progress after repeated attempts
  - Error — critical failure
- [ ] Produce a final verdict: Success, Partial Success, Failure, or Abandoned
- [ ] Record which specific criteria were met and which were not

**Done when**: UserSim stops at the right time and correctly reports whether the test passed.

### Step 4: Test Result Output

**Goal**: Every test run produces a visible, useful result.

- [ ] Output the full conversation transcript (all messages, both sides)
- [ ] Output the final verdict (pass/fail/partial/abandoned)
- [ ] Output the termination reason
- [ ] Output per-criterion status (met / not met)
- [ ] Output as structured data (JSON) so it can be consumed programmatically
- [ ] Expose a Python library API: `UserSim.run()` returns a result object with outcome, transcript, turn count, and per-criterion status
- [ ] Build a CLI entry point (`usersim run`) that wraps the library, loads config, and prints results to stdout
- [ ] CLI exit codes: 0 = success, 1 = test failure, 2 = error

**Done when**: A developer can run `usersim run test.yaml` from the command line OR call `UserSim.run()` from Python and get the same result.

---

## Tier 2 — Essential Enhancements (Makes UserSim genuinely useful)

These can be added incrementally on top of the core. Each one independently improves UserSim's value.

### Step 5: Persona Support

**Goal**: UserSim can impersonate different types of users to test how the agent handles them.

- [ ] Accept a persona definition as input (start with a free-text description)
- [ ] Inject the persona description into the system prompt so the LLM adopts that identity
- [ ] Persona drives conversation behavior: how the user adapts (or doesn't) when stuck, whether they escalate, rephrase, get frustrated, or give up
- [ ] Validate that generated messages reflect the persona's tone, knowledge level, and adaptability
- [ ] Default to a neutral, cooperative, moderately adaptive user when no persona is specified

**Done when**: The same objective tested with different personas produces noticeably different conversation styles — including different reactions when the agent isn't helping.

### Step 6: Test Configuration Schema

**Goal**: Tests are defined declaratively in YAML so they are repeatable and shareable.

- [ ] Define the YAML schema for a test configuration (target, objective, persona, constraints)
- [ ] Test configs do NOT include hyperparameters — those live in system config
- [ ] Parse and validate test configuration files
- [ ] Drive test execution from configuration (no code changes needed to add a new test)
- [ ] Support referencing persona definitions inline or by name

**Done when**: A developer can write a YAML file and run it as a test without writing any code. No LLM knowledge required.

---

## Tier 3 — Production-Grade (Makes UserSim reliable and debuggable at scale)

These are important for production use but require the core and essential layers to be solid first.

### Step 7: Observability

**Goal**: When a test fails or behaves unexpectedly, a developer can understand why.

- [ ] Turn-level decision log: what strategy UserSim chose at each turn and why
- [ ] Objective evaluation trace: per-turn progress on each success criterion
- [ ] Persona adherence scoring: per-turn assessment of persona consistency
- [ ] Persona drift detection: flag when UserSim breaks character
- [ ] Termination reasoning: structured record of why the conversation ended
- [ ] Cost attribution: token usage and estimated dollar cost per conversation

**Done when**: A developer can diagnose a failed test from the observability output alone, without re-running it.

### Step 8: Structured Persona Schema & Libraries

**Goal**: Personas are well-defined, reusable, and produce consistent behavior.

- [ ] Define the structured persona schema (name, description, tone, expertise, patience, adaptability, language style, behavioral traits)
- [ ] Map persona attributes to specific system prompt instructions — including how the persona reacts when stuck (rephrase, escalate, get frustrated, give up)
- [ ] Implement persona libraries: YAML files of reusable persona definitions
- [ ] Support referencing library personas by name in test configurations
- [ ] Trait activation tracking: which persona traits were actually exhibited

**Done when**: A team can maintain a shared persona library and reference personas by name across test suites.

### Step 9: Metrics, Reporting & Regression Detection

**Goal**: Test results produce actionable intelligence, not just pass/fail.

- [ ] Aggregate metrics: success rate, average turns, common failures — overall and by persona/objective
- [ ] Regression detection: compare results across test suite runs, flag changed outcomes
- [ ] Flakiness detection: flag objective+persona combinations that produce inconsistent results
- [ ] Reports: conversation transcripts with annotations, objective analysis, persona impact analysis
- [ ] Cost reporting: token usage and dollar cost breakdown by objective, persona, and model

**Done when**: A team can run a test suite nightly and immediately see what regressed.

---

## Tier 4 — Future Enhancements

These are captured in the spec but are not planned for initial implementation. They become relevant once Tiers 1–3 are solid.

| Enhancement | Description |
|---|---|
| Test suites & batch execution | Run multiple tests together with shared configuration |
| Parallel execution | Run multiple conversations simultaneously |
| CI/CD integration | Run test suites as part of a build pipeline |
| Custom evaluation logic | Domain-specific success criteria beyond text analysis |
| Persona generators | Programmatic creation of persona variants for combinatorial testing |
| Automated persona generation | Use LLMs to generate diverse personas from parameters |
| Automated test generation | Create objectives from agent capabilities |
| Multi-agent testing | Test agent teams and orchestrations |
| Persona A/B testing | Compare agent performance across persona pairs for bias detection |
| Emotional arc simulation | Personas that evolve emotional state during conversation |
| Human-in-the-loop | Manual intervention during test runs |
| Visual testing | Support for agents with UI components |
| Voice testing | Support for voice-based agents |
| Load testing | Simulate many concurrent users with diverse personas |
| Learning from failures | Improve strategy based on past test outcomes |

---

## Build Order Summary

```
Step 1: Conversation loop + turn limit ──────────┐
Step 2: Objective-driven message generation ──────┤ Tier 1: Core
Step 3: Objective evaluation + termination ───────┤ (MVP)
Step 4: Result output + CLI + library API ───────┘

Step 5: Persona support (text-based) ────────────┐ Tier 2: Essential
Step 6: Test configuration schema (YAML) ────────┘

Step 7: Observability (decision logs, traces) ───┐
Step 8: Structured personas + libraries ─────────┤ Tier 3: Production
Step 9: Metrics, reporting, regression ──────────┘

Tier 4: Future enhancements ─────────────────────  (backlog)
```

---

## Key Principles

1. **Each step is independently shippable** — you can stop after any step and have a working (if limited) system.
2. **Tier 1 is non-negotiable** — skip any step in Tier 1 and UserSim cannot perform its basic function.
3. **Tier 2 items are independent** — steps 5 and 6 can be built in any order.
4. **Adaptive behavior is persona-driven** — how UserSim reacts when stuck (rephrase, escalate, abandon) is determined by the persona, not a separate strategy engine.
5. **Observability before scale** — invest in debuggability (Tier 3) before parallelism and CI/CD (Tier 4).
7. **CLI wraps library** — the core logic is a Python package; the CLI is a thin shell that parses YAML and calls the library.
