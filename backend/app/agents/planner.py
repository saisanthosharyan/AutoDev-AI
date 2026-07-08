from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.models.task import Task


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

Create a detailed software implementation plan.

The steps should be sequential.

Include every major component.

Database

Authentication

Models

Routes

Business Logic

Testing

Deployment

Documentation

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

        response = await llm.generate_structured(
            prompt=prompt,
            schema=Task
        )
        print("=" * 80)
        print("PLANNER RESPONSE")
        print(response)
        print("=" * 80)

        return response
    