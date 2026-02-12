# UserSim Specification

## Overview

UserSim is an intelligent agent testing tool built on the Microsoft Agent Framework that simulates realistic user interactions with conversational agents. It is distributed as a **Python package** that can be used both as a **CLI** and as a **library**, enabling automated, objective-driven testing of agent capabilities through multi-turn conversations that mimic real user behavior.

## Purpose

UserSim serves as a quality assurance tool for validating conversational AI agents by:
- Simulating realistic user conversations with target agents
- Impersonating diverse user personas to test how agents handle different user types
- Validating agent responses against predefined objectives
- Testing agent behavior across diverse scenarios and user demographics
- Identifying gaps in agent capabilities across persona-driven interactions
- Providing reproducible test results

## Architecture

### Core Components

#### 1. UserSim Agent
The primary agent component built using Microsoft Agent Framework that:
- Initiates conversations with target agents
- Maintains conversation context and state
- Evaluates progress toward objectives
- Determines when to continue, pivot, or terminate conversations

#### 2. Persona Engine
Manages the simulated user identity for each testing session:
- Defines the persona characteristics that UserSim will adopt
- Shapes tone, vocabulary, patience level, and domain knowledge
- Ensures consistent persona behavior across the entire conversation
- Enables testing how agents handle different types of users

See [Persona System](#persona-system) for full details.

#### 3. Objective Engine
Manages the goals for each testing session:
- Defines success criteria for conversations
- Tracks progress toward objectives
- Provides objective-aware prompting to the UserSim agent
- Validates completion status

#### 4. Conversation Manager
Handles the lifecycle of test conversations:
- Initializes sessions with clear objectives
- Routes messages between UserSim and target agents
- Maintains conversation history
- Implements turn limits and timeout policies

#### 5. Evaluation Module
Assesses conversation outcomes:
- Analyzes agent responses for objective fulfillment
- Tracks conversation quality metrics
- Identifies successful vs. failed interactions
- Generates test reports

### Integration Points

UserSim integrates with:
- **Microsoft Agent Framework**: Core runtime and agent orchestration
- **Target Agents**: The agents being tested (via the A2A protocol)
- **LLM Providers**: For UserSim's reasoning (Azure OpenAI, OpenAI, etc.)
- **Logging/Observability**: OpenTelemetry for tracing and monitoring
- **Test Frameworks**: Importable as a Python library for use with pytest, unittest, etc.
- **CI/CD Pipelines**: CLI can be invoked directly in pipeline steps

## Interfaces

UserSim is a **Python package** (`usersim`) that exposes two interfaces: a CLI for direct use and a library for programmatic integration. The core logic lives in the library; the CLI is a thin wrapper.

### CLI

The primary user-facing interface. Test authors run tests from the command line:

```bash
# Run a single test from a YAML config
usersim run test.yaml

# Run a test suite
usersim run suite.yaml

# Run with explicit system config
usersim run test.yaml --config usersim.yaml

# List personas in a library
usersim personas list --library standard_personas.yaml

# Validate a test config without running it
usersim validate test.yaml
```

Output is printed to stdout as structured text (human-readable by default, `--format json` for machine consumption). Exit codes indicate pass/fail for CI/CD integration.

### Library

UserSim is also importable as a Python package for embedding in existing test frameworks:

```python
from usersim import UserSim

result = UserSim.run(
    target="https://agent-endpoint/.well-known/agent.json",
    objective="Book a flight from Seattle to New York",
    success_criteria=["Booking confirmation received"],
    persona="Confused Elderly User"
)

assert result.outcome == "success"
assert result.turns <= 15
```

This enables:
- Integration with **pytest**, **unittest**, or any Python test framework
- Programmatic test generation (e.g., loop over personas × objectives)
- Custom result processing and aggregation
- Embedding UserSim in larger automation workflows

## Conversation Lifecycle

### 1. Initialization Phase
```
UserSim receives:
- Target agent connection details
- Persona definition (who to impersonate)
- Test objective description
- Success criteria
- Constraints (max turns, timeout, etc.)
```

### 2. Engagement Phase
```
UserSim:
1. Assumes the assigned persona identity
2. Formulates initial message based on objective and persona voice
3. Sends message to target agent
4. Receives and analyzes response
5. Evaluates progress toward objective
6. Determines next action (continue, pivot, or conclude) consistent with persona behavior
```

### 3. Multi-Turn Interaction
UserSim continues the conversation by:
- Adapting its approach based on agent responses
- Maintaining coherent context across turns
- Pursuing the objective through natural dialogue
- Handling edge cases (unclear responses, errors, etc.)

### 4. Termination Phase
The conversation ends when:
- **Success**: Objective is achieved
- **Failure**: Maximum turns reached without success
- **Abandonment**: UserSim determines the objective is unachievable
- **Error**: Critical failure in the conversation

## Persona System

In addition to objectives, UserSim supports **personas** — predefined user identities that UserSim impersonates when communicating with the target agent. This allows testing how different types of users might interact with the agent being tested.

### Why Personas Matter

Real-world agents encounter a wide range of users: tech-savvy experts, confused beginners, impatient customers, non-native speakers, accessibility-dependent users, and more. An agent that works well for one user type may completely fail another. Personas let you systematically surface these gaps.

### Persona Definition

A persona describes **who** UserSim pretends to be during a conversation. It includes:

| Attribute | Description | Example |
|---|---|---|
| **Name** | A human-readable label for the persona | `"Frustrated Customer"` |
| **Description** | Narrative summary of the persona's background | `"A long-time customer who has been on hold for 30 minutes and is losing patience."` |
| **Tone** | Communication style | `angry`, `polite`, `terse`, `verbose`, `confused` |
| **Expertise Level** | Domain knowledge | `novice`, `intermediate`, `expert` |
| **Patience** | How many unhelpful turns before frustration/abandonment | `low`, `medium`, `high` |
| **Adaptability** | How the persona reacts when stuck — rephrase, escalate, get frustrated, or give up | `rigid`, `moderate`, `flexible` |
| **Language Style** | Vocabulary, formality, typos, slang, ESL patterns | `formal`, `casual`, `broken-english`, `typo-prone` |
| **Accessibility Needs** | Special requirements the persona may express | `screen-reader user`, `voice-only`, `low-vision` |
| **Behavioral Traits** | Additional personality quirks | `goes off-topic`, `asks rapid follow-ups`, `provides minimal info` |

### Example Personas

```yaml
persona:
  name: "Confused Elderly User"
  description: "A 75-year-old retiree who is not comfortable with technology and needs step-by-step guidance."
  tone: "polite"
  expertise_level: "novice"
  patience: "high"
  adaptability: "rigid"
  language_style: "casual"
  behavioral_traits:
    - "Asks for clarification frequently"
    - "Misunderstands technical jargon"
    - "Provides more personal context than needed"
    - "Repeats the same question in slightly different words when stuck"
```

```yaml
persona:
  name: "Impatient Power User"
  description: "A software engineer who expects fast, precise answers and has no tolerance for generic responses."
  tone: "terse"
  expertise_level: "expert"
  patience: "low"
  adaptability: "flexible"
  language_style: "formal"
  behavioral_traits:
    - "Uses technical terminology without explanation"
    - "Skips pleasantries"
    - "Challenges vague answers"
    - "Quickly tries alternative phrasing or asks to escalate"
```

```yaml
persona:
  name: "Non-Native English Speaker"
  description: "A user who speaks English as a second language. Grammar may be imperfect and they may ask for simpler explanations."
  tone: "polite"
  expertise_level: "intermediate"
  patience: "medium"
  adaptability: "moderate"
  language_style: "broken-english"
  behavioral_traits:
    - "Occasionally uses wrong prepositions or verb tenses"
    - "Asks 'what does X mean?' for uncommon words"
    - "Prefers short, simple sentences"
    - "May restate their question more simply when not understood"
```

### Persona Behavior at Runtime

When a persona is assigned, UserSim:
1. **Adopts the persona's voice** in all generated messages — tone, vocabulary, sentence structure, and formality all reflect the persona definition.
2. **Simulates the persona's knowledge level** — a novice persona will not use domain jargon; an expert persona will not ask basic questions.
3. **Follows the persona's patience model** — a low-patience persona may express frustration or threaten to leave after a few unhelpful turns, while a high-patience persona will keep trying.
4. **Adapts according to the persona's adaptability** — a rigid persona repeats essentially the same request; a flexible persona rephrases, tries different angles, or escalates. This replaces the need for a separate "strategy engine" — adaptation is a character trait, not a system behavior.
5. **Exhibits behavioral traits** consistently — if the persona goes off-topic, this happens naturally throughout the conversation, not just once.
6. **Maintains persona consistency** across all turns — the persona does not break character.

### Personas vs. Objectives

Personas and objectives are complementary but independent:

- An **objective** defines *what* UserSim is trying to accomplish (the goal).
- A **persona** defines *who* UserSim is pretending to be (the identity).

The same objective can be tested with multiple personas to see how the agent handles different user types:

```yaml
# Same goal, different personas
objective: "Get a refund for a defective product"

persona_variants:
  - name: "Polite First-Timer"
  - name: "Angry Repeat Caller"
  - name: "Non-Native Speaker"
  - name: "Accessibility-Dependent User"
```

This produces four separate test conversations, each pursuing the same goal but through a different user lens.

### Persona Libraries

UserSim supports reusable persona libraries — collections of predefined personas that can be referenced by name across test configurations:

```yaml
persona_library: "standard_personas.yaml"

tests:
  - objective: "Book a flight"
    persona: "Confused Elderly User"      # references library
  - objective: "Book a flight"
    persona: "Impatient Power User"        # references library
  - objective: "Cancel a subscription"
    persona: "Non-Native English Speaker"  # references library
```

## Objective-Driven Behavior

### Objective Definition

Each test session includes:
- **Goal Statement**: Clear description of what UserSim should accomplish
- **Success Criteria**: Measurable conditions for completion
- **Context**: Background information and constraints
- **Persona**: The user identity to impersonate during the conversation (optional — defaults to a neutral, cooperative user)

Example Objective:
```yaml
goal: "Book a flight from Seattle to New York for next Tuesday"
success_criteria:
  - Flight is scheduled for correct date
  - Departure city is Seattle
  - Destination city is New York
  - Booking confirmation received
context: "Budget-conscious traveler, flexible on time"
persona: "First-time flyer, needs extra guidance"
max_turns: 15
```

### Objective Tracking

UserSim continuously evaluates:
- **Progress Indicators**: Signals that indicate movement toward the goal
- **Blockers**: Issues preventing objective completion
- **Completion Status**: Whether objective is fully or partially met

How UserSim responds to blockers and lack of progress is determined by the persona — see [Persona Behavior at Runtime](#persona-behavior-at-runtime).

## Multi-Turn Conversation Handling

### Context Maintenance

UserSim maintains:
- **Conversation History**: All messages exchanged
- **State Tracking**: Current position in the objective pursuit
- **Agent Capabilities**: Discovered features of the target agent
- **User Persona State**: Consistency in simulated user behavior

### Turn Strategy

Each turn involves:
1. **Analysis**: Evaluate previous response
2. **Planning**: Determine next step toward objective
3. **Generation**: Create appropriate user message
4. **Validation**: Ensure message aligns with persona and context

### Conversation Patterns

UserSim can handle:
- **Linear Flows**: Direct path to objective
- **Branching Dialogs**: Multiple paths to explore
- **Clarification Loops**: Handle ambiguous responses
- **Error Recovery**: Navigate through misunderstandings
- **Escalation**: Request help or alternative approaches

## Success and Failure Conditions

### Success Scenarios

Conversation succeeds when:
- All success criteria are met
- Target agent provides required information/action
- Objective is fully achieved
- Confirmation is received

### Partial Success

Conversation may partially succeed when:
- Some but not all criteria are met
- Alternative acceptable outcome is achieved
- Workaround solution is found

### Failure Scenarios

Conversation fails when:
- Maximum turn limit reached without success
- Target agent is unable to help
- Critical error occurs
- Objective is determined to be impossible

### Abandonment Logic

UserSim abandons when:
- No progress after multiple attempts
- Target agent repeatedly fails to understand
- Clear indication that objective is unachievable
- Conversation enters an unproductive loop

## Microsoft Agent Framework Integration

### Agent Configuration

UserSim agent is configured via [System Configuration](#system-configuration):
- **Model**: LLM provider and model for reasoning and response generation
- **Hyperparameters**: Temperature, top_p, and other LLM settings — set system-wide, not per test
- **Instructions**: System prompts for user simulation (derived from persona + objective at runtime)
- **Memory**: State management for conversation context

### Communication Protocol

UserSim connects to target agents exclusively via the **Agent-to-Agent (A2A) protocol**:
- **A2A over HTTP(S)**: JSON-RPC 2.0 messages over HTTP(S), supporting synchronous request/response and streaming (SSE)
- **Agent Discovery**: UserSim reads the target agent's Agent Card to discover capabilities and connection details before starting a conversation
- **Multi-Turn Tasks**: A2A's task lifecycle maps directly to UserSim's conversation lifecycle — each test is an A2A task
- **Opaque Testing**: A2A's opacity model means UserSim treats the target agent as a black box, which is exactly the right testing posture
- **Framework-Agnostic**: Any agent that exposes an A2A endpoint can be tested, regardless of the framework it was built with (LangGraph, CrewAI, Semantic Kernel, ADK, custom, etc.)

### Observability

The target agent and the underlying Agent Framework provide their own observability (tracing, metrics, logging). UserSim's observability focuses on **test-specific concerns** — the information that only UserSim has visibility into and that is invisible to the agent being tested.

#### Test Outcome Observability
The target agent has no concept of objectives or success criteria — only UserSim knows whether a test passed or failed, and why:
- **Objective evaluation trace**: Per-turn evaluation of each success criterion (not yet met → partially met → met), capturing the exact turn where each criterion was satisfied or where progress stalled.
- **Termination reasoning**: Why UserSim ended the conversation — which termination condition was triggered (success, max turns, abandonment, error) and the reasoning behind the decision.
- **Partial success decomposition**: When a test partially succeeds, which specific criteria were met and which were not, with the last relevant turn cited.

#### Persona Adherence Observability
The target agent doesn't know a persona is being simulated — only UserSim can monitor whether it is staying in character:
- **Persona consistency scoring**: Per-turn assessment of whether the generated message matches the persona's defined tone, expertise level, vocabulary, and behavioral traits.
- **Persona drift detection**: Flagging when UserSim's messages start deviating from the persona definition (e.g., a "novice" persona suddenly using expert jargon, or a "terse" persona writing long paragraphs).
- **Trait activation tracking**: Which behavioral traits from the persona definition were actually exhibited during the conversation, and which were never triggered.

#### Strategy & Decision Observability
UserSim makes internal decisions each turn that are not visible in the conversation transcript:
- **Turn-level decision log**: At each turn, what strategy UserSim chose (continue on current path, pivot approach, escalate, ask clarification, express frustration, abandon) and the reasoning.
- **Progress assessment log**: UserSim's internal assessment of how much progress has been made toward the objective, captured as a structured signal (not just the final score).
- **Alternative path tracking**: When UserSim pivots to a different approach, logging the previous strategy, why it was abandoned, and what the new strategy is.

#### Test Execution Observability
Concerns related to running tests reliably at scale:
- **Test suite progress**: Which tests have run, which are pending, which are in flight — especially important for parallel and batch execution.
- **Flakiness detection**: When the same objective + persona combination produces different outcomes across runs, flagging it as non-deterministic and capturing the divergence point.
- **Regression detection**: Comparing test results across suite runs to surface objectives or personas whose outcomes have changed.
- **Cost attribution**: Token usage and estimated cost per conversation, per test suite, and per persona — critical because UserSim's own LLM calls (for reasoning, message generation, and evaluation) are a cost center separate from the target agent.

#### Conversation Replay
For debugging failed or unexpected tests:
- **State snapshots**: Full conversation state (history, objective progress, persona state, strategy) captured at each turn, enabling step-by-step replay of a test without re-running it.
- **Diff between runs**: Side-by-side comparison of two runs of the same test to identify where behavior diverged.

#### What UserSim Does NOT Need to Observe
The following are the target agent's responsibility and should not be duplicated by UserSim:
- Internal agent reasoning and tool calls
- Agent-side LLM token usage and latency
- Agent infrastructure health (uptime, memory, CPU)
- Agent-side error details beyond what is returned in responses

UserSim treats the target agent as a black box and observes only what it can see from the outside (response content, latency, errors) plus its own internal test orchestration state.

## Example Use Cases

### 1. Customer Service Bot Testing
```yaml
objective: "Get refund for a damaged product"
target_agent: "customer_service_bot"
success_criteria:
  - Refund request is initiated
  - Case number is provided
  - Expected timeline is communicated
```

### 2. Technical Support Agent Testing
```yaml
objective: "Troubleshoot internet connectivity issue"
target_agent: "tech_support_agent"
success_criteria:
  - Problem is diagnosed
  - Solution steps are provided
  - Issue is resolved or escalated
```

### 3. Booking Assistant Testing
```yaml
objective: "Reserve a hotel room with specific requirements"
target_agent: "hotel_booking_agent"
success_criteria:
  - Available rooms are shown
  - Room meets requirements (king bed, non-smoking)
  - Reservation is confirmed
```

### 4. Information Retrieval Testing
```yaml
objective: "Find company policy on remote work"
target_agent: "knowledge_bot"
success_criteria:
  - Correct policy document is found
  - Relevant sections are cited
  - Follow-up questions are answered
```

### 5. Persona-Driven Regression Testing
```yaml
objective: "Request account password reset"
target_agent: "account_support_bot"
persona:
  name: "Frustrated Locked-Out User"
  tone: "angry"
  expertise_level: "novice"
  patience: "low"
  behavioral_traits:
    - "Expresses urgency and frustration"
    - "Threatens to switch to a competitor"
    - "Provides information reluctantly"
success_criteria:
  - Identity verification is completed
  - Password reset link is sent
  - Agent maintains professional tone despite user frustration
```

## Configuration

### System Configuration

System configuration controls **how UserSim operates** — the LLM, hyperparameters, and runtime settings. These are set once per deployment, not per test. Test authors should not need to understand or set these values.

```yaml
usersim_system:
  model:
    provider: "azure-openai"       # azure-openai, openai, etc.
    model_name: "gpt-4"            # model to use for message generation and evaluation
    api_version: "2025-01-01"      # provider-specific API version
    endpoint: "https://my-instance.openai.azure.com/"
    
  hyperparameters:
    temperature: 0.7               # controls randomness in LLM output (0.0 = deterministic, 1.0 = creative)
    top_p: 0.95                    # nucleus sampling threshold
    max_tokens: 1024               # max tokens per generated message
    frequency_penalty: 0.0         # penalize repeated tokens
    presence_penalty: 0.0          # penalize tokens already present in the conversation
    
  defaults:
    max_turns: 20                  # default max turns if not specified in test
    timeout_seconds: 300           # default timeout if not specified in test
    
  logging:
    level: "info"                  # debug, info, warn, error
    output: "stdout"               # stdout, file, etc.
```

**Design principle**: Hyperparameters belong here because they affect *all* tests uniformly. Persona definitions control voice and behavior — temperature does not. If every test set its own temperature, results would be inconsistent and hard to compare across the suite.

### Test Configuration

Test configuration defines **what to test** — the objective, persona, target agent, and constraints. This is what test authors write.

```yaml
usersim_test:
  name: "Test Name"
  description: "What this test validates"
  
  target:
    agent_id: "agent-under-test"
    connection:
      endpoint: "https://agent-endpoint/.well-known/agent.json"
      
  objective:
    goal: "What UserSim should accomplish"
    success_criteria:
      - "Criterion 1"
      - "Criterion 2"
    context: "Background information"
    
  persona:
    name: "Persona Name"
    description: "Narrative background for the persona"
    tone: "polite"           # angry, polite, terse, verbose, confused
    expertise_level: "novice" # novice, intermediate, expert
    patience: "medium"        # low, medium, high
    adaptability: "moderate"   # rigid, moderate, flexible
    language_style: "casual"  # formal, casual, broken-english, typo-prone
    behavioral_traits:
      - "Trait 1"
      - "Trait 2"
    
  constraints:
    max_turns: 20                  # overrides system default
    timeout_seconds: 300           # overrides system default
```

## Metrics and Reporting

Metrics and reports are UserSim's primary output — they represent the test results. The target agent's own metrics (internal latency, tool call success, etc.) are the agent's concern; UserSim captures only what it can observe from the outside combined with its own test-level data.

### Per-Conversation Metrics

- **Outcome**: Success, Partial Success, Failure, Abandoned
- **Termination Reason**: Why the conversation ended (objective met, max turns, abandonment decision, error)
- **Turn Count**: Number of exchanges
- **Duration**: Wall-clock time elapsed
- **Progress Score**: Estimated completion percentage at termination
- **Per-Criterion Status**: Individual pass/fail for each success criterion
- **Persona Consistency Score**: How well UserSim maintained the persona throughout
- **Strategy Pivots**: Number of times UserSim changed approach during the conversation (driven by persona adaptability)
- **Token Usage**: UserSim's own LLM token consumption (prompt + completion) for the conversation
- **Estimated Cost**: Dollar cost of UserSim's LLM usage for this conversation

### Aggregate Metrics

- **Success Rate**: Percentage of objectives achieved
- **Success Rate by Persona**: Breakdown of success rate per persona type
- **Success Rate by Objective**: Which objectives are reliably achieved vs. problematic
- **Average Turns**: Mean number of turns to success
- **Average Turns by Persona**: How different personas affect conversation length
- **Common Failures**: Most frequent failure reasons
- **Persona-Correlated Failures**: Failures that disproportionately affect specific personas
- **Flakiness Rate**: Percentage of tests producing inconsistent outcomes across runs
- **Regression Indicators**: Objectives or personas whose outcomes changed since the last run
- **Total Token Usage / Cost**: Aggregate cost of the test suite
- **Agent Capability Map**: What the target agent can/cannot do (inferred from test outcomes)
- **Agent Adaptability Score**: How well the target agent adjusts to different user types

### Reports

Generated reports include:
- **Conversation Transcripts**: Full message history with persona annotations and turn-level strategy/evaluation metadata
- **Objective Analysis**: How each criterion was/wasn't met, with the specific turn cited
- **Persona Impact Analysis**: How different personas affected outcomes for the same objective
- **Regression Report**: What changed since the previous test suite run
- **Flakiness Report**: Non-deterministic tests with divergence details
- **Cost Report**: Token usage and dollar cost breakdown by objective, persona, and model
- **Agent Performance**: Strengths and weaknesses of the target agent, segmented by persona
- **Recommendations**: Suggested improvements, including persona-specific gaps

## Implementation Considerations

### Testing Best Practices

1. **Objective Clarity**: Define clear, measurable objectives
2. **Persona Diversity**: Test each objective with multiple personas to uncover user-type-specific failures
3. **Persona Consistency**: Maintain coherent user behavior throughout the entire conversation
4. **Reasonable Constraints**: Set appropriate turn limits (note: some personas may naturally require more turns)
5. **Error Handling**: Gracefully handle unexpected responses
6. **Reproducibility**: Ensure tests can be reliably repeated

### Scalability

UserSim should support:
- **Parallel Testing**: Multiple conversations simultaneously
- **Test Suites**: Collections of related objectives
- **Batch Execution**: Running many tests in sequence
- **Cloud Deployment**: Scaling to handle large test loads

### Security and Privacy

Considerations:
- **Credential Management**: Secure handling of API keys
- **Data Privacy**: Protect sensitive information in conversations
- **Access Control**: Restrict test execution to authorized users
- **Audit Logging**: Track all test activities

### Extensibility

UserSim should be extensible for:
- **Custom Evaluation Logic**: Domain-specific success criteria
- **Persona Libraries**: Reusable, shareable persona definitions for common user archetypes
- **Custom Persona Attributes**: Domain-specific persona fields (e.g., subscription tier, account age)
- **Persona Generators**: Programmatic creation of persona variants for combinatorial testing
- **Integration Adapters**: Support for various agent platforms
- **Reporting Formats**: Multiple output formats for results

## Future Enhancements

Potential additions:
- **Learning from Failures**: Improve strategy based on past tests
- **Automated Test Generation**: Create objectives from agent capabilities
- **Automated Persona Generation**: Use LLMs to generate diverse personas from demographic and behavioral parameters
- **Multi-Agent Testing**: Test agent teams/orchestrations
- **Human-in-the-Loop**: Allow manual intervention in tests
- **Persona A/B Testing**: Compare agent performance across persona pairs to measure bias or inconsistency
- **Visual Testing**: Support for agents with UI components
- **Voice Testing**: Support for voice-based agents
- **Emotional Arc Simulation**: Personas that evolve their emotional state throughout the conversation (e.g., start calm, become frustrated)
- **Load Testing**: Simulate many concurrent users with diverse personas

## Conclusion

UserSim provides a comprehensive solution for automated testing of conversational agents. By combining objective-driven behavior with the power of the Microsoft Agent Framework, it enables thorough validation of agent capabilities through realistic, multi-turn conversations. This specification serves as the foundation for building a robust, scalable agent testing platform.
