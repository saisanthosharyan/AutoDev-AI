from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.models.task import Task
from app.core.logger import logger


class PlannerAgent(BaseAgent):

    async def run(self, task: str, history: list = None) -> Task:

        llm = LLMRouter.get_llm()

        history_text = ""

        if history:
            history_text = "\n".join(
                [
                    f"{msg['role']}: {msg['content']}"
                    for msg in history
                ]
            )

        prompt = f"""
You are an Expert Software Architect.

Conversation History:

{history_text}

Current User Request:

{task}

Create a structured implementation plan.

Return ONLY JSON in this format:

{{
    "title": "...",
    "description": "...",
    "steps": [
        "...",
        "...",
        "..."
    ]
}}
"""

        logger.info("Generating implementation plan...")

        response = await llm.generate_structured(
            prompt=prompt,
            schema=Task
        )

        logger.info("Planner completed successfully.")

        return response