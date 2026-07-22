from app.services.llm.router import LLMRouter
from app.agents.base_agent import BaseAgent
from app.models.task import Task
from app.core.logger import logger


class PlannerAgent(BaseAgent):

    async def run(
        self,
        task: str,
        history: list | None = None,
    ) -> Task:

        llm = LLMRouter.get_llm()

        history_text = ""

        if history:

            history_text = "\n".join(
                f"{msg['role']}: {msg['content']}"
                for msg in history
            )

        prompt = f"""
You are a Senior Software Architect and Technical Lead.

Your responsibility is to analyze the user's request and produce a complete implementation plan before any code is written.

Conversation History:

{history_text}

Current User Request:

{task}

Think carefully about:

• Project objective
• Core features
• Required technologies
• Backend architecture
• Frontend architecture
• Database requirements
• APIs
• Authentication
• Deployment considerations
• Testing strategy
• Folder structure
• Implementation order

Return ONLY valid JSON.

Required format:

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

        "Testing",

        "Deployment"

    ]
}}

Rules:

- Do not explain anything.
- Do not use markdown.
- Do not wrap inside ```json.
- Return ONLY valid JSON.
"""

        logger.info("Generating implementation plan...")

        response = await llm.generate_structured(
            prompt=prompt,
            schema=Task,
        )

        logger.info("Planner completed successfully.")

        return response