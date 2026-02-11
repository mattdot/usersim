# UserSim Specification

## Overview

UserSim is an intelligent agent testing system built on the Microsoft Agent Framework that simulates realistic user interactions with conversational agents. It enables automated, objective-driven testing of agent capabilities through multi-turn conversations that mimic real user behavior.

## Purpose

UserSim serves as a quality assurance tool for validating conversational AI agents by:
- Simulating realistic user conversations with target agents
- Validating agent responses against predefined objectives
- Testing agent behavior across diverse scenarios
- Identifying gaps in agent capabilities
- Providing reproducible test results

## Architecture

### Core Components

#### 1. UserSim Agent
The primary agent component built using Microsoft Agent Framework that:
- Initiates conversations with target agents
- Maintains conversation context and state
- Evaluates progress toward objectives
- Determines when to continue, pivot, or terminate conversations

#### 2. Objective Engine
Manages the goals for each testing session:
- Defines success criteria for conversations
- Tracks progress toward objectives
- Provides objective-aware prompting to the UserSim agent
- Validates completion status

#### 3. Conversation Manager
Handles the lifecycle of test conversations:
- Initializes sessions with clear objectives
- Routes messages between UserSim and target agents
- Maintains conversation history
- Implements turn limits and timeout policies

#### 4. Evaluation Module
Assesses conversation outcomes:
- Analyzes agent responses for objective fulfillment
- Tracks conversation quality metrics
- Identifies successful vs. failed interactions
- Generates test reports

### Integration Points

UserSim integrates with:
- **Microsoft Agent Framework**: Core runtime and agent orchestration
- **Target Agents**: The agents being tested (via A2A protocol or direct integration)
- **LLM Providers**: For UserSim's reasoning (Azure OpenAI, OpenAI, etc.)
- **Logging/Observability**: OpenTelemetry for tracing and monitoring
- **Test Frameworks**: Can be integrated into CI/CD pipelines

## Conversation Lifecycle

### 1. Initialization Phase
```
UserSim receives:
- Target agent connection details
- Test objective description
- Success criteria
- Constraints (max turns, timeout, etc.)
```

### 2. Engagement Phase
```
UserSim:
1. Formulates initial message based on objective
2. Sends message to target agent
3. Receives and analyzes response
4. Evaluates progress toward objective
5. Determines next action (continue, pivot, or conclude)
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

## Objective-Driven Behavior

### Objective Definition

Each test session includes:
- **Goal Statement**: Clear description of what UserSim should accomplish
- **Success Criteria**: Measurable conditions for completion
- **Context**: Background information and constraints
- **Persona** (optional): User role or behavior pattern to simulate

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
- **Alternative Paths**: Different approaches to achieve the same goal
- **Completion Status**: Whether objective is fully or partially met

### Adaptive Strategy

UserSim adjusts its approach based on:
- Target agent's capabilities and limitations
- Response quality and relevance
- Time/turn constraints
- Progress toward the objective

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

UserSim agent is configured with:
- **Model**: LLM for reasoning and response generation
- **Instructions**: System prompts for user simulation
- **Tools**: Capabilities for analysis and decision-making
- **Memory**: State management for conversation context

### Communication Protocols

UserSim uses:
- **Agent-to-Agent (A2A)**: For communicating with remote agents
- **Direct Integration**: For in-process agent testing
- **Message Formats**: Standardized formats for interoperability

### Observability

Integration with OpenTelemetry provides:
- **Tracing**: End-to-end conversation flow
- **Metrics**: Success rates, turn counts, duration
- **Logging**: Detailed conversation logs
- **Debugging**: Time-travel debugging for test analysis

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

## Configuration Schema

### Test Configuration

```yaml
usersim_test:
  name: "Test Name"
  description: "What this test validates"
  
  target:
    agent_id: "agent-under-test"
    connection:
      type: "a2a" # or "direct"
      endpoint: "https://agent-endpoint"
      
  objective:
    goal: "What UserSim should accomplish"
    success_criteria:
      - "Criterion 1"
      - "Criterion 2"
    context: "Background information"
    persona: "User role to simulate"
    
  constraints:
    max_turns: 20
    timeout_seconds: 300
    min_progress_turns: 5
    
  usersim:
    model: "gpt-4"
    temperature: 0.7
    instructions: "Additional behavioral guidelines"
```

## Metrics and Reporting

### Per-Conversation Metrics

- **Outcome**: Success, Partial Success, Failure, Abandoned
- **Turn Count**: Number of exchanges
- **Duration**: Time elapsed
- **Progress Score**: Estimated completion percentage
- **Quality Score**: Conversation naturalness rating

### Aggregate Metrics

- **Success Rate**: Percentage of objectives achieved
- **Average Turns**: Mean number of turns to success
- **Common Failures**: Most frequent failure reasons
- **Agent Capability Map**: What the agent can/cannot do

### Reports

Generated reports include:
- **Conversation Transcripts**: Full message history
- **Objective Analysis**: How criteria were/weren't met
- **Agent Performance**: Strengths and weaknesses identified
- **Recommendations**: Suggested improvements

## Implementation Considerations

### Testing Best Practices

1. **Objective Clarity**: Define clear, measurable objectives
2. **Persona Consistency**: Maintain coherent user behavior
3. **Reasonable Constraints**: Set appropriate turn limits
4. **Error Handling**: Gracefully handle unexpected responses
5. **Reproducibility**: Ensure tests can be reliably repeated

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
- **Persona Libraries**: Reusable user behavior patterns
- **Integration Adapters**: Support for various agent platforms
- **Reporting Formats**: Multiple output formats for results

## Future Enhancements

Potential additions:
- **Learning from Failures**: Improve strategy based on past tests
- **Automated Test Generation**: Create objectives from agent capabilities
- **Multi-Agent Testing**: Test agent teams/orchestrations
- **Human-in-the-Loop**: Allow manual intervention in tests
- **Visual Testing**: Support for agents with UI components
- **Voice Testing**: Support for voice-based agents
- **Load Testing**: Simulate many concurrent users

## Conclusion

UserSim provides a comprehensive solution for automated testing of conversational agents. By combining objective-driven behavior with the power of the Microsoft Agent Framework, it enables thorough validation of agent capabilities through realistic, multi-turn conversations. This specification serves as the foundation for building a robust, scalable agent testing platform.
