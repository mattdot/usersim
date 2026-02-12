"""LLM client for message generation and evaluation."""

import logging
from typing import List, Optional

from openai import AsyncOpenAI

from usersim.models import Message, SystemConfig

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLM providers."""

    def __init__(self, config: SystemConfig):
        """Initialize the LLM client.

        Args:
            config: System configuration with LLM settings
        """
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
        )

    async def generate_user_message(
        self,
        goal: str,
        success_criteria: List[str],
        conversation_history: List[Message],
        context: Optional[str] = None,
    ) -> str:
        """Generate the next user message based on objective.

        Args:
            goal: The test objective
            success_criteria: List of success criteria
            conversation_history: Previous conversation messages
            context: Optional context information

        Returns:
            Generated user message
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(goal, success_criteria, context)

        # Build message history for LLM
        messages = [{"role": "system", "content": system_prompt}]

        for msg in conversation_history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add instruction for next message if this isn't the first turn
        if conversation_history:
            messages.append({
                "role": "system",
                "content": "Generate the next user message to continue pursuing the objective."
            })

        logger.debug(f"Generating user message with {len(messages)} context messages")

        try:
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_tokens,
            )

            generated_message = response.choices[0].message.content
            logger.debug(f"Generated message: {generated_message[:100]}...")
            return generated_message

        except Exception as e:
            logger.error(f"Failed to generate message: {e}")
            raise

    async def evaluate_progress(
        self,
        goal: str,
        success_criteria: List[str],
        conversation_history: List[Message],
    ) -> tuple[float, List[tuple[str, bool, str]]]:
        """Evaluate progress toward objective.

        Args:
            goal: The test objective
            success_criteria: List of success criteria
            conversation_history: Conversation messages

        Returns:
            Tuple of (progress_score, criteria_evaluations)
            where criteria_evaluations is List[(criterion, met, evaluation)]
        """
        evaluation_prompt = f"""Evaluate the progress toward the following objective:

Goal: {goal}

Success Criteria:
{chr(10).join(f"- {c}" for c in success_criteria)}

Conversation so far:
{self._format_conversation(conversation_history)}

For each success criterion, determine if it has been met (true/false) and provide a brief evaluation.
Also provide an overall progress score from 0.0 to 1.0.

Respond in the following format:
CRITERION: <criterion text>
MET: <true/false>
EVALUATION: <brief explanation>

[Repeat for each criterion]

OVERALL_PROGRESS: <score from 0.0 to 1.0>
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": evaluation_prompt}],
                temperature=0.0,  # Use low temperature for evaluation
                max_tokens=1024,
            )

            evaluation_text = response.choices[0].message.content
            logger.debug(f"Evaluation response: {evaluation_text[:200]}...")

            # Parse evaluation
            criteria_evals = []
            progress_score = 0.0

            lines = evaluation_text.split("\n")
            current_criterion = None
            current_met = False
            current_eval = ""

            for line in lines:
                line = line.strip()
                if line.startswith("CRITERION:"):
                    if current_criterion:
                        criteria_evals.append((current_criterion, current_met, current_eval))
                    current_criterion = line[10:].strip()
                    current_met = False
                    current_eval = ""
                elif line.startswith("MET:"):
                    current_met = line[4:].strip().lower() == "true"
                elif line.startswith("EVALUATION:"):
                    current_eval = line[11:].strip()
                elif line.startswith("OVERALL_PROGRESS:"):
                    try:
                        progress_score = float(line[17:].strip())
                    except ValueError:
                        progress_score = 0.5  # Default if parsing fails

            # Add last criterion
            if current_criterion:
                criteria_evals.append((current_criterion, current_met, current_eval))

            logger.info(f"Progress: {progress_score:.2f}, Criteria met: "
                       f"{sum(1 for _, met, _ in criteria_evals if met)}/{len(criteria_evals)}")

            return progress_score, criteria_evals

        except Exception as e:
            logger.error(f"Failed to evaluate progress: {e}")
            # Return default values on error
            return 0.0, [(c, False, "Evaluation failed") for c in success_criteria]

    def _build_system_prompt(
        self,
        goal: str,
        success_criteria: List[str],
        context: Optional[str] = None
    ) -> str:
        """Build system prompt for user message generation."""
        criteria_text = "\n".join(f"- {c}" for c in success_criteria)

        prompt = f"""You are simulating a user testing a conversational agent. Your objective is:

Goal: {goal}

Success Criteria:
{criteria_text}
"""

        if context:
            prompt += f"\nContext: {context}\n"

        prompt += """
Your task is to engage with the agent to achieve this objective. Be natural and realistic in your communication. 
Ask questions, provide information, and respond appropriately to the agent's messages. 
Stay focused on achieving the objective but communicate like a real user would.

Generate only the user's message - do not include any system text, explanations, or meta-commentary.
"""

        return prompt

    def _format_conversation(self, history: List[Message]) -> str:
        """Format conversation history for display."""
        if not history:
            return "[No conversation yet]"

        formatted = []
        for msg in history:
            role_label = "User" if msg.role == "user" else "Agent"
            formatted.append(f"{role_label}: {msg.content}")

        return "\n\n".join(formatted)
