from app.agents.base_agent import BaseAgent
from app.core.logger import logger
from app.models.task import Task
from app.services.llm.router import LLMRouter


class PlannerAgent(BaseAgent):
    """
    Generates a structured implementation plan before code generation.
    """

    async def run(
        self,
        task: str,
        history: list | None = None,
    ) -> Task:

        logger.info("=" * 60)
        logger.info("Planner Agent Started")
        logger.info("=" * 60)

        llm = LLMRouter.get_llm()

        history_text = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in (history or [])
        )

        prompt = f"""
You are a Principal Software Architect and Technical Lead.

Your responsibility is to analyze the user's request and create a complete implementation plan BEFORE any code is written.

==================================================
CONVERSATION HISTORY
==================================================

{history_text}

==================================================
CURRENT USER REQUEST
==================================================

{task}

==================================================
YOUR RESPONSIBILITIES
==================================================

Analyze the request and determine:

• Project title
• Project objective
• Core features
• Recommended programming language
• Recommended framework(s)
• Database requirements
• Authentication requirements
• API requirements
• Folder structure
• Testing strategy
• Deployment strategy
• Implementation order

Choose the most appropriate technologies automatically.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

{{
    "title": "Project Name",
    "description": "Short project description",
    "steps": [
        "Analyze requirements",
        "Create folder structure",
        "Initialize project",
        "Implement backend",
        "Implement frontend",
        "Configure database",
        "Add authentication",
        "Implement APIs",
        "Implement UI",
        "Write automated tests",
        "Deployment"
    ]
}}

==================================================
RULES
==================================================

- Return ONLY JSON.
- No markdown.
- No explanations.
- No comments.
- No ```json.
- Ensure the JSON matches the required schema exactly.
"""

        logger.info("Generating implementation plan...")

        plan = await llm.generate_structured(
            prompt=prompt,
            schema=Task,
        )

        logger.info("Planner completed successfully.")

        logger.info("=" * 60)
        logger.info("Planner Agent Finished")
        logger.info("=" * 60)

        return plan